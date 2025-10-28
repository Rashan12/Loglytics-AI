from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import os
import shutil
from datetime import datetime
import logging

from app.database import get_db
from app.models.user import User
from app.models.chat_session import ChatSession, ChatMessage
from app.models.log_file import LogFile
from app.schemas.chat_enhanced import ChatRequest, ChatResponse, ChatMessage as ChatMessageSchema, ConversationHistory, ConversationList
from app.services.auth.jwt_handler import get_current_user
from app.services.chat_enhanced_service import enhanced_chat_service
from app.services.chat_unified_service import unified_chat_service
from sqlalchemy import select, desc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Enhanced Chat"])

# Directory to store uploaded log files
UPLOAD_DIR = "uploaded_logs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("", response_model=ChatResponse)
async def chat_with_ai(
    message: str = Form(...),
    file: Optional[UploadFile] = File(None),
    conversation_history: str = Form("[]"),  # JSON string
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to AI assistant with optional log file upload
    """
    import json
    
    logger.info(f"🤖 Chat request received from user: {current_user.id}")
    logger.info(f"📝 Message: {message[:100]}...")
    logger.info(f"📁 File attached: {file.filename if file else 'None'}")
    
    try:
        # Parse conversation history
        try:
            history_data = json.loads(conversation_history)
            history = [ChatMessageSchema(**msg) for msg in history_data]
        except:
            history = []
        
        # Handle file upload if provided
        file_id = None
        if file:
            # Validate file
            if file.size > 100 * 1024 * 1024:  # 100MB limit
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size exceeds 100MB limit"
                )
            
            allowed_extensions = ['.log', '.txt', '.csv']
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Only .log, .txt, and .csv files are allowed"
                )
            
            # Save file
            file_id = str(uuid.uuid4())
            file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create log file record
            log_file = LogFile(
                id=file_id,
                user_id=current_user.id,
                filename=file.filename,
                file_size=file_size,
                upload_status="completed",
                created_at=datetime.now()
            )
            
            db.add(log_file)
            await db.commit()
            
            # Index log file for RAG
            try:
                from app.services.rag.rag_service import RAGService
                rag_service = RAGService(db)
                await rag_service.initialize()
                
                # Read file content for indexing
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                
                # Index the log file for RAG
                await rag_service.index_log_file(
                    log_file_id=file_id,
                    project_id="default",  # Use default project for now
                    user_id=current_user.id,
                    content=file_content,
                    file_type=file_extension[1:]  # Remove the dot
                )
                
                logger.info(f"Indexed log file for RAG: {file.filename}")
                
            except Exception as e:
                logger.error(f"Error indexing log file for RAG: {e}")
                # Continue without RAG indexing if there's an error
        
        # Get or create conversation
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == current_user.id)
            .order_by(desc(ChatSession.updated_at))
            .limit(1)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            conversation = ChatSession(
                session_id=str(uuid.uuid4()),
                user_id=current_user.id,
                title="New Conversation",
                created_at=datetime.now()
            )
            db.add(conversation)
            await db.commit()
        
        # Save user message
        user_message = ChatMessage(
            session_id=conversation.id,
            role="user",
            content=message,
            created_at=datetime.now()
        )
        db.add(user_message)
        
        # Add user message to RAG system for context
        try:
            from app.services.rag.rag_service import RAGService
            rag_service = RAGService(db)
            await rag_service.initialize()
            
            # Index the user message for future context
            await rag_service.index_conversation_message(
                message_id=str(user_message.id),
                conversation_id=conversation.session_id,
                user_id=current_user.id,
                content=message,
                role="user",
                project_id="default"
            )
            
            logger.info(f"Indexed user message for RAG: {user_message.id}")
            
        except Exception as e:
            logger.error(f"Error indexing user message for RAG: {e}")
            # Continue without RAG indexing if there's an error
        
        # Get AI response with RAG context using unified service
        ai_response = await unified_chat_service.chat(
            message=message,
            conversation_history=history,
            conversation_id=conversation.session_id,
            file_id=file_id,
            user_id=current_user.id,
            project_id="default",  # Use default project for RAG context
            db=db,
            user=current_user  # Pass user object for subscription-based model selection
        )
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=conversation.id,
            role="assistant",
            content=ai_response,
            created_at=datetime.now()
        )
        db.add(assistant_message)
        
        # Add assistant message to RAG system for context
        try:
            # Index the assistant message for future context
            await rag_service.index_conversation_message(
                message_id=str(assistant_message.id),
                conversation_id=conversation.session_id,
                user_id=current_user.id,
                content=ai_response,
                role="assistant",
                project_id="default"
            )
            
            logger.info(f"Indexed assistant message for RAG: {assistant_message.id}")
            
        except Exception as e:
            logger.error(f"Error indexing assistant message for RAG: {e}")
            # Continue without RAG indexing if there's an error
        
        # Update conversation
        conversation.updated_at = datetime.now()
        if not conversation.title or conversation.title == "New Conversation":
            # Set title from first user message
            conversation.title = message[:50] + "..." if len(message) > 50 else message
        
        await db.commit()
        
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation.session_id,
            timestamp=datetime.now(),
            file_analyzed=file_id is not None
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )

@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation history"""
    # Verify conversation belongs to user
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == conversation_id,
            ChatSession.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == conversation.id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    
    return {
        "conversation_id": conversation_id,
        "title": conversation.title,
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at
            }
            for msg in messages
        ]
    }

@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all user conversations"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(desc(ChatSession.updated_at))
    )
    conversations = result.scalars().all()
    
    return {
        "conversations": [
            {
                "id": conv.session_id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
            for conv in conversations
        ]
    }

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation"""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == conversation_id,
            ChatSession.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "Conversation deleted successfully"}
