"""
Chat WebSocket Endpoint
Handles real-time chat with LLM response streaming
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from app.websockets.manager import connection_manager
from app.websockets.auth import authenticate_websocket, close_websocket_with_error, rate_limiter, verify_resource_access
from app.websockets.middleware import websocket_middleware
from app.database import get_db
from app.services.llm.llm_service import UnifiedLLMService, LLMRequest, LLMTask
try:
    from app.services.chat.chat_service import ChatService  # optional, may not exist
except Exception:
    ChatService = None
from app.models.chat_session import ChatSession
from app.models.message import Message, MessageRole
from app.schemas.user import UserResponse, SubscriptionTier, LLMModel


class _InlineChatService:
    """Lightweight chat service used only if real ChatService is missing."""
    def __init__(self, db: Session):
        self.db = db

    async def create_message(self, content: str, role: str, chat_id: str, user_id: Optional[str] = None):
        # Persist minimal message using ORM models
        msg = Message(
            chat_id=chat_id,
            role=MessageRole.USER if role == "user" else MessageRole.ASSISTANT,
            content=content,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        class Obj:
            id = msg.id
            created_at = msg.created_at
        return Obj()

    async def get_chat_messages(self, chat_id: str, limit: int = 10, offset: int = 0):
        # Return recent messages
        from sqlalchemy import select
        result = self.db.execute(
            select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.desc())
        )
        rows = result.scalars().all()
        rows = list(reversed(rows))  # chronological
        rows = rows[offset:offset+limit]
        class RowObj:
            def __init__(self, r: Message):
                self.role = r.role.value if hasattr(r.role, 'value') else r.role
                self.content = r.content
                self.created_at = r.created_at
                self.user_id = None
        return [RowObj(r) for r in rows]


logger = logging.getLogger(__name__)


async def chat_websocket(websocket: WebSocket, chat_id: str):
    """
    WebSocket endpoint for real-time chat

    Endpoint: ws://api/v1/chat/ws/{chat_id}

    Message Types:
    - user_message: User sent a message
    - assistant_message_start: LLM starts responding
    - assistant_message_token: Each token streamed
    - assistant_message_end: LLM finished
    - typing: Someone is typing
    - error: Error occurred
    - system: System notification
    """
    connection_id = str(uuid.uuid4())
    user_id = None

    try:
        # Authenticate connection
        authenticated, user_id, error = await authenticate_websocket(websocket)

        if not authenticated:
            logger.warning(f"WebSocket auth failed for chat {chat_id}: {error}")
            await close_websocket_with_error(websocket, error or "Authentication failed")
            return

        # Verify user has access to this chat
        has_access = await verify_resource_access(user_id, "chat", chat_id)
        if not has_access:
            logger.warning(f"User {user_id} denied access to chat {chat_id}")
            await close_websocket_with_error(websocket, "Access denied to this chat")
            return

        # Connect to manager
        await connection_manager.connect(
            websocket,
            user_id,
            connection_id,
            metadata={
                "type": "chat",
                "chat_id": chat_id
            }
        )

        # Subscribe to chat
        await connection_manager.subscribe_to_chat(user_id, connection_id, chat_id)

        logger.info(f"Chat WebSocket connected: chat_id={chat_id}, user={user_id}")

        # Send welcome message
        await connection_manager.send_personal_message(
            user_id,
            connection_id,
            {
                "type": "system",
                "message": "Connected to chat",
                "chat_id": chat_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                
                # Process message through middleware
                message = await websocket_middleware.process_incoming_message(
                    websocket, connection_id, user_id, data
                )
                
                if not message:
                    continue

                # Handle different message types
                message_type = message.get("type")

                if message_type == "user_message":
                    await handle_user_message(chat_id, user_id, connection_id, message)

                elif message_type == "typing":
                    await handle_typing_indicator(chat_id, user_id, connection_id, message)

                elif message_type == "ping":
                    await connection_manager.send_personal_message(
                        user_id,
                        connection_id,
                        {
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )

                elif message_type == "get_chat_history":
                    await handle_get_chat_history(chat_id, user_id, connection_id, message)

                else:
                    logger.warning(f"Unknown message type: {message_type}")

            except WebSocketDisconnect:
                break

            except Exception as e:
                logger.error(f"Error in chat WebSocket loop: {e}")
                await websocket_middleware.error_handler.handle_error(
                    connection_id, e, websocket, user_id
                )

    except WebSocketDisconnect:
        logger.info(f"Chat WebSocket disconnected: chat_id={chat_id}, user={user_id}")

    except Exception as e:
        logger.error(f"Error in chat WebSocket: {e}")

    finally:
        # Cleanup
        if user_id:
            await connection_manager.unsubscribe_from_chat(user_id, chat_id)
            await connection_manager.disconnect(user_id, connection_id)
            rate_limiter.cleanup_connection(connection_id)
            websocket_middleware.cleanup_connection(connection_id)


async def handle_user_message(chat_id: str, user_id: str, connection_id: str, message: Dict[str, Any]):
    """
    Handle user message and stream LLM response

    Args:
        chat_id: Chat identifier
        user_id: User identifier
        connection_id: WebSocket connection ID
        message: Message data
    """
    try:
        content = message.get("content", "").strip()
        if not content:
            await connection_manager.send_personal_message(
                user_id,
                connection_id,
                {
                    "type": "error",
                    "message": "Message content cannot be empty",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return

        message_id = str(uuid.uuid4())

        # Save user message to database
        db = next(get_db())
        try:
            chat_service = ChatService(db) if ChatService else _InlineChatService(db)
            
            # Create message
            message_create = MessageCreate(
                content=content,
                role="user",
                chat_session_id=chat_id
            )
            
            user_message = await chat_service.create_message(message_create, user_id)
            
            # Broadcast user message to all chat participants
            await connection_manager.broadcast_to_chat(
                chat_id,
                {
                    "type": "user_message",
                    "message_id": str(user_message.id),
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "content": content,
                    "timestamp": user_message.created_at.isoformat()
                }
            )

            # Send assistant message start
            assistant_message_id = str(uuid.uuid4())
            await connection_manager.broadcast_to_chat(
                chat_id,
                {
                    "type": "assistant_message_start",
                    "message_id": assistant_message_id,
                    "chat_id": chat_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            # Stream LLM response
            await stream_llm_response(chat_id, user_id, assistant_message_id, content, db)

            # Send assistant message end
            await connection_manager.broadcast_to_chat(
                chat_id,
                {
                    "type": "assistant_message_end",
                    "message_id": assistant_message_id,
                    "chat_id": chat_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error handling user message: {e}")
        await connection_manager.send_personal_message(
            user_id,
            connection_id,
            {
                "type": "error",
                "message": f"Failed to process message: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


async def stream_llm_response(chat_id: str, user_id: str, message_id: str, user_message: str, db: Session):
    """
    Stream LLM response token by token using actual LLM service

    Args:
        chat_id: Chat identifier
        user_id: User identifier
        message_id: Message identifier
        user_message: User's message to respond to
        db: Database session
    """
    try:
        # Initialize LLM service
        llm_service = UnifiedLLMService(db)
        chat_service = ChatService(db) if ChatService else _InlineChatService(db)
        
        # Get chat history for context
        chat_history = await chat_service.get_chat_messages(chat_id, limit=10)
        
        # Prepare conversation history for LLM
        messages = []
        for msg in chat_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        # Add current user message last
        messages.append({"role": "user", "content": user_message})

        # Build LLM request
        llm_request = LLMRequest(
            task=LLMTask.CHAT,
            prompt=user_message,
            conversation_history=[
                {"role": m["role"], "content": m["content"]} for m in messages
            ],
            stream=True,
        )

        # Stream response from LLM
        full_response = ""
        response_stream = await llm_service.generate_response(llm_request, user=await _get_user_stub(user_id, db), db=db)
        if hasattr(response_stream, "__aiter__"):
            async for chunk in response_stream:
                token = chunk.content
                if token:
                    full_response += token
                    await connection_manager.broadcast_to_chat(
                        chat_id,
                        {
                            "type": "assistant_message_token",
                            "message_id": message_id,
                            "chat_id": chat_id,
                            "token": token,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    await asyncio.sleep(0.01)
        else:
            # Non-streaming fallback
            token = getattr(response_stream, "content", "")
            full_response = token or ""
            if token:
                await connection_manager.broadcast_to_chat(
                    chat_id,
                    {
                        "type": "assistant_message_token",
                        "message_id": message_id,
                        "chat_id": chat_id,
                        "token": token,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

        # Save assistant message to database
        if full_response.strip():
            message_create = MessageCreate(
                content=full_response.strip(),
                role="assistant",
                chat_session_id=chat_id
            )
            
            await chat_service.create_message(message_create, user_id)

    except Exception as e:
        logger.error(f"Error streaming LLM response: {e}")
        await connection_manager.broadcast_to_chat(
            chat_id,
            {
                "type": "error",
                "message": f"Failed to generate response: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


async def handle_typing_indicator(chat_id: str, user_id: str, connection_id: str, message: Dict[str, Any]):
    """
    Handle typing indicator broadcast

    Args:
        chat_id: Chat identifier
        user_id: User identifier
        connection_id: WebSocket connection ID
        message: Message data
    """
    try:
        is_typing = message.get("is_typing", False)

        # Broadcast typing indicator to other chat participants
        await connection_manager.broadcast_to_chat(
            chat_id,
            {
                "type": "typing",
                "chat_id": chat_id,
                "user_id": user_id,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error handling typing indicator: {e}")

async def _get_user_stub(user_id: str, db: Session) -> UserResponse:
    """Create minimal UserResponse for LLM service using DB user record."""
    try:
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return UserResponse(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                subscription_tier=user.subscription_tier,
                selected_llm_model=user.selected_llm_model,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at or user.created_at,
            )
    except Exception:
        pass
    # Fallback stub
    return UserResponse(
        id=str(user_id),
        email="unknown@example.com",
        full_name="User",
        subscription_tier=SubscriptionTier.FREE,
        selected_llm_model=LLMModel.LOCAL,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


async def handle_get_chat_history(chat_id: str, user_id: str, connection_id: str, message: Dict[str, Any]):
    """
    Handle request for chat history

    Args:
        chat_id: Chat identifier
        user_id: User identifier
        connection_id: WebSocket connection ID
        message: Message data
    """
    try:
        limit = message.get("limit", 50)
        offset = message.get("offset", 0)
        
        db = next(get_db())
        try:
            chat_service = ChatService(db) if ChatService else _InlineChatService(db)
            messages = await chat_service.get_chat_messages(chat_id, limit=limit, offset=offset)
            
            # Convert to response format
            message_list = []
            for msg in messages:
                message_list.append({
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "user_id": str(msg.user_id) if msg.user_id else None
                })
            
            # Send chat history to requesting connection
            await connection_manager.send_personal_message(
                user_id,
                connection_id,
                {
                    "type": "chat_history",
                    "chat_id": chat_id,
                    "messages": message_list,
                    "has_more": len(message_list) == limit,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error handling get chat history: {e}")
        await connection_manager.send_personal_message(
            user_id,
            connection_id,
            {
                "type": "error",
                "message": f"Failed to get chat history: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
