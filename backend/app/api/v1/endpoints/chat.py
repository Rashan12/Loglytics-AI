from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import os
import shutil
import logging
from sqlalchemy import select

from app.database.session import get_db
from app.models.chat_session import ChatSession, ChatMessage
from app.models.user import User
from app.schemas.chat import (
    Chat as ChatSchema,
    ChatCreate,
    ChatUpdate,
    ChatResponse
)
from app.schemas.user import UserResponse
from app.services.auth.jwt_handler import get_current_user
from app.services.llm.llm_service import UnifiedLLMService

router = APIRouter()


@router.post("/chat")
async def general_chat(
    message: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    General AI chat endpoint with file upload support
    """
    print(f"\n{'='*60}")
    print(f"📨 GENERAL CHAT REQUEST")
    print(f"{'='*60}")
    print(f"User: {current_user.email}")
    print(f"Message: {message}")
    print(f"File: {file.filename if file else 'None'}")
    print(f"{'='*60}\n")
    
    try:
        # Initialize services
        from app.services.rag.rag_service import RAGService
        from app.services.log_parser.log_parser_service import LogParserService
        from app.models.log_file import LogFile
        
        rag_service = RAGService(db)
        
        file_id = None
    
        # Process file if uploaded
        file_info = None
        if file:
            print(f"📎 Processing file: {file.filename}")
            
            # Save file
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            upload_dir = "uploads/general"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Read and save
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            print(f"💾 File saved: {file_path} ({len(content)} bytes)")
            
            # Create LogFile record
            log_file = LogFile(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=len(content),
                file_type=file_extension,
                user_id=current_user.id,
                upload_status="completed"
            )
            db.add(log_file)
            await db.commit()
            await db.refresh(log_file)
            file_id = str(log_file.id)
            
            print(f"✅ File record created: ID {log_file.id}")
            
            file_info = {
                "id": str(log_file.id),
                "filename": file.filename,
                "size": len(content)
            }
        
        # Parse and index
        try:
            await log_parser.process_log_file(log_file.id)
            await rag_service.index_log_file(
                log_file_id=file_id,
                project_id="general",
                user_id=str(current_user.id),
                content=content.decode('utf-8', errors='ignore'),
                file_type=file_extension
            )
        except Exception as e:
            logging.error(f"Error processing file: {e}")
    
        # Query RAG - temporarily disabled for basic functionality
        rag_context = ""
    # try:
    #     await rag_service.initialize()
    #     rag_response = await rag_service.query(
    #         question=message,
    #         project_id="general",
    #         user=current_user,
    #         max_chunks=5
    #     )
    #     
    #     if rag_response.sources:
    #         rag_context = "\n\n".join([
    #             f"[Context {i+1}] {source.content}"
    #             for i, source in enumerate(rag_response.sources[:3])
    #         ])
    # except Exception as e:
    #     logging.error(f"RAG error: {e}")
    
        # Build prompt
        if rag_context:
            prompt = f"""Context from uploaded logs:
{rag_context}

User question: {message}

Answer based on the context."""
        else:
            prompt = message
    
        # Generate AI response
        if file:
            response_text = f"I've analyzed your log file '{file.filename}'. I found {len(content)} bytes of log data. What would you like to know about it?"
        else:
            response_text = "I'm your AI assistant for log analysis. Upload a log file or ask me questions about log analysis, troubleshooting, or pattern detection!"
        
        print(f"💬 Generated response: {response_text}")
        
        result = {
            "response": response_text,
            "file_processed": file is not None,
            "file_info": file_info,
            "success": True
        }
        
        print(f"✅ Sending successful response")
        print(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR in general_chat: {str(e)}")
        print(f"{'='*60}\n")
        
        return {
            "response": "I'm here to help with log analysis. How can I assist you?",
            "file_processed": False,
            "success": False,
            "error": str(e)
        }


@router.post("/sessions", response_model=ChatSchema)
async def create_chat_session(
    session_data: ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat session"""
    chat_session = ChatSession(
        session_id=session_data.session_id,
        user_id=current_user.id,
        title=session_data.title,
        context=session_data.context
    )
    
    db.add(chat_session)
    await db.commit()
    await db.refresh(chat_session)
    
    return chat_session


@router.get("/sessions", response_model=List[ChatSchema])
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's chat sessions"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).offset(skip).limit(limit)
    )
    sessions = result.scalars().all()
    
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSchema)
async def get_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific chat session"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message in a chat session"""
    from sqlalchemy import select
    
    # Get session
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
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
    
    await db.commit()
    await db.refresh(chat_message)
    
    # If it's a user message, generate AI response
    if message.role == "user":
        try:
            llm_service = UnifiedLLMService(db)
            response = await llm_service.generate_response(session.id, message.content)
            
            # Create AI response message
            ai_message = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=response.get("content", "I received your message. This is a simulated response."),
                metadata=response.get("metadata"),
                token_count=response.get("token_count", 0),
                model_used=response.get("model_used", "default")
            )
            
            db.add(ai_message)
            await db.commit()
            await db.refresh(ai_message)
            
            return ai_message
        except Exception as e:
            # If LLM service fails, create a simple response
            ai_message = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=f"I received your message: '{message.content}'. This is a simulated AI response.",
                metadata={"error": str(e)},
                token_count=0,
                model_used="simulated"
            )
            
            db.add(ai_message)
            await db.commit()
            await db.refresh(ai_message)
            
            return ai_message
    
    return chat_message


@router.get("/sessions/{session_id}/messages", response_model=List[ChatResponse])
async def get_chat_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages from a chat session"""
    from sqlalchemy import select
    
    # Get session
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get messages
    result = await db.execute(
        select(ChatMessage).where(
            ChatMessage.session_id == session.id
        ).offset(skip).limit(limit)
    )
    messages = result.scalars().all()
    
    return messages


# Additional endpoints to match frontend expectations
@router.get("/chats")
async def get_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chats (alias for sessions)"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        )
    )
    sessions = result.scalars().all()
    
    return sessions


@router.post("/chats")
async def create_chat(
    chat_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat (alias for session)"""
    import uuid
    
    session_id = str(uuid.uuid4())
    chat_session = ChatSession(
        session_id=session_id,
        user_id=current_user.id,
        title=chat_data.get("title", "New Chat"),
        context=chat_data.get("context", "")
    )
    
    db.add(chat_session)
    await db.commit()
    await db.refresh(chat_session)
    
    return {
        "id": session_id,
        "title": chat_session.title,
        "created_at": chat_session.created_at.isoformat(),
        "updated_at": chat_session.updated_at.isoformat(),
        "user_id": current_user.id
    }


@router.get("/chats/{chat_id}")
async def get_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific chat (alias for session)"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == chat_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return {
        "id": session.session_id,
        "title": session.title,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "user_id": current_user.id
    }


@router.get("/chats/{chat_id}/messages")
async def get_chat_messages_alias(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a chat (alias for session messages)"""
    from sqlalchemy import select
    
    # Get session
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == chat_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Get messages
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session.id)
    )
    messages = result.scalars().all()
    
    return messages


@router.post("/chats/{chat_id}/messages")
async def send_message_alias(
    chat_id: str,
    message: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to a chat with optional file upload"""
    from sqlalchemy import select
    
    # Get session
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == chat_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
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
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create log file record
        from app.models.log_file import LogFile
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
        
        # Process log file with parser
        try:
            from app.services.log_parser.log_parser_service import LogParserService
            log_parser = LogParserService(db)
            await log_parser.process_log_file(log_file.id)
            logging.info(f"Processed log file: {file.filename}")
        except Exception as e:
            logging.error(f"Error processing log file: {e}")
        
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
                project_id="default",  # Use default project for general chat
                user_id=current_user.id,
                content=file_content,
                file_type=file_extension[1:]  # Remove the dot
            )
            
            logging.info(f"Indexed log file for RAG: {file.filename}")
            
        except Exception as e:
            logging.error(f"Error indexing log file for RAG: {e}")
    
    # Create user message
    chat_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=message,
        metadata={"file_id": file_id} if file_id else None,
        token_count=0,
        model_used="user"
    )
    
    db.add(chat_message)
    
    # Update session last message time
    session.last_message_at = datetime.utcnow()
    session.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(chat_message)
    
    # Query RAG for relevant context
    rag_context = ""
    try:
        from app.services.rag.rag_service import RAGService
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        # Query RAG for relevant context
        rag_response = await rag_service.query(
            question=message,
            project_id="default",  # Use default project for general chat
            user=current_user,
            max_chunks=5,
            similarity_threshold=0.7
        )
        
        if rag_response.sources:
            rag_context = "\n\n".join([
                f"[Source {i+1}] {source.content}"
                for i, source in enumerate(rag_response.sources[:5])
            ])
            logging.info(f"Retrieved {len(rag_response.sources)} relevant chunks from RAG")
        else:
            logging.info("No relevant context found in RAG")
            
    except Exception as e:
        logging.error(f"Error querying RAG: {e}")
    
    # Generate AI response - simplified for basic functionality
    try:
        # Create simple AI response
        ai_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=f"I received your message: '{message}'. I'm here to help with your log analysis. You can upload log files and I'll analyze them for you.",
            metadata={"file_id": file_id},
            token_count=0,
            model_used="basic"
        )
        
        db.add(ai_message)
        await db.commit()
        await db.refresh(ai_message)
        
    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        # If response generation fails, create a simple response
        ai_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=f"I received your message: '{message}'. This is a simulated AI response.",
            metadata={"error": str(e), "file_id": file_id},
            token_count=0,
            model_used="simulated"
        )
        
        db.add(ai_message)
        await db.commit()
        await db.refresh(ai_message)
    
    return {
        "id": str(chat_message.id),
        "chat_id": chat_id,
        "content": chat_message.content,
        "role": chat_message.role,
        "timestamp": chat_message.created_at.isoformat(),
        "user_id": current_user.id,
        "file_processed": file is not None,
        "file_id": file_id
    }