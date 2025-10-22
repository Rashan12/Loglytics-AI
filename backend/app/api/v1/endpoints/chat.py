from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.chat_session import ChatSession, ChatMessage
from app.schemas.chat import (
    Chat as ChatSchema,
    ChatCreate,
    ChatUpdate,
    ChatResponse
)
from app.services.auth.auth_service import AuthService
from app.services.llm.llm_service import UnifiedLLMService

router = APIRouter()


@router.post("/sessions", response_model=ChatSchema)
async def create_chat_session(
    session_data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Create a new chat session"""
    chat_session = ChatSession(
        session_id=session_data.session_id,
        user_id=current_user.id,
        title=session_data.title,
        context=session_data.context
    )
    
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    
    return chat_session


@router.get("/sessions", response_model=List[ChatSchema])
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get user's chat sessions"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.is_active == True
    ).offset(skip).limit(limit).all()
    
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSchema)
async def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get specific chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: str,
    message: ChatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Send a message in a chat session"""
    # Get session
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Create message
    chat_message = ChatMessage(
        session_id=session.id,
        role=message.role,
        content=message.content,
        metadata=message.metadata,
        token_count=message.token_count,
        model_used=message.model_used
    )
    
    db.add(chat_message)
    
    # Update session last message time
    session.last_message_at = datetime.utcnow()
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(chat_message)
    
    # If it's a user message, generate AI response
    if message.role == "user":
        llm_service = LLMService(db)
        response = await llm_service.generate_response(session.id, message.content)
        
        # Create AI response message
        ai_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=response["content"],
            metadata=response.get("metadata"),
            token_count=response.get("token_count"),
            model_used=response.get("model_used")
        )
        
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        return ai_message
    
    return chat_message


@router.get("/sessions/{session_id}/messages", response_model=List[ChatResponse])
async def get_chat_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get messages from a chat session"""
    # Get session
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).offset(skip).limit(limit).all()
    
    return messages
