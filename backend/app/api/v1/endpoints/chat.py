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
from app.models.log_file import LogFile
from app.schemas.chat import (
    Chat as ChatSchema,
    ChatCreate,
    ChatUpdate,
    ChatResponse
)
from app.schemas.user import UserResponse
from app.services.auth.jwt_handler import get_current_user

router = APIRouter()


async def _get_or_create_debug_user(db: AsyncSession) -> User:
    """Get or create a debug user for general chat (when auth is bypassed)"""
    debug_email = "debug@example.com"
    debug_id = "debug-user-id"
    
    # Try to find existing debug user
    result = await db.execute(
        select(User).where(User.id == debug_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        return user
    
    # Create debug user if not found
    from app.models.user import SubscriptionTier, LLMModel
    from app.services.auth.password_handler import PasswordHandler
    
    new_user = User(
        id=debug_id,
        email=debug_email,
        password_hash=PasswordHandler.hash_password("debug-password"),
        full_name="Debug User",
        subscription_tier=SubscriptionTier.FREE,
        selected_llm_model=LLMModel.MAVERICK,
        is_active=True
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        print(f"✅ Created debug user: {debug_email}")
        return new_user
    except Exception as e:
        await db.rollback()
        print(f"⚠️ Error creating debug user (may already exist): {e}")
        # Try to get it again by ID or email
        result = await db.execute(
            select(User).where(
                (User.id == debug_id) | (User.email == debug_email)
            )
        )
        user = result.scalar_one_or_none()
        if user:
            print(f"✅ Found existing debug user: {user.email}")
            return user
        # If still not found, raise the original error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create or retrieve debug user: {str(e)}"
        )


@router.post("")
async def general_chat(
    message: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    General AI chat endpoint with file upload support
    """
    print(f"\n{'='*60}")
    print(f"📨 GENERAL CHAT REQUEST")
    print(f"{'='*60}")
    print(f"User: DEBUG_MODE (auth bypassed)")
    print(f"Message: '{message}' (type: {type(message)}, len: {len(message) if message else 'None'})")
    print(f"File: {file.filename if file else 'None'}")
    print(f"{'='*60}\n")
    
    # Validate message
    if not message or not message.strip():
        print("❌ ERROR: Empty message received")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message cannot be empty"
        )
    
    # Get or create debug user in database
    try:
        current_user = await _get_or_create_debug_user(db)
        print(f"✅ Using user: {current_user.email} (ID: {current_user.id})")
    except Exception as e:
        print(f"❌ Error getting debug user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize debug user: {str(e)}"
        )
    
    try:
        # Initialize services
        from app.services.chat_unified_service import unified_chat_service
        
        # Get or create default project for general chat
        async def _get_or_create_default_project(db: AsyncSession, user_id: str):
            """Get or create a default project for general chat"""
            from app.models.project import Project
            
            # Try to find existing default project
            result = await db.execute(
                select(Project).where(
                    Project.user_id == user_id,
                    Project.name == "General Chat"
                )
            )
            default_project = result.scalar_one_or_none()
            
            if not default_project:
                # Create default project
                default_project = Project(
                    user_id=user_id,
                    name="General Chat",
                    description="Default project for general AI assistant chat"
                )
                db.add(default_project)
                await db.commit()
                await db.refresh(default_project)
                print(f"✅ Created default project for general chat: {default_project.id}")
            
            return default_project
        
        # Get or create default project
        default_project = await _get_or_create_default_project(db, current_user.id)
        project_id = str(default_project.id)
        
        # Process file if uploaded
        file_info = None
        file_path = None
        file_content_context = ""
        
        if file:
            print(f"📎 Processing file: {file.filename}")
            
            # Validate file
            if file.size and file.size > 100 * 1024 * 1024:  # 100MB limit
                print(f"❌ File too large: {file.size} bytes")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size exceeds 100MB limit"
                )
            
            allowed_extensions = ['.log', '.txt', '.csv']
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                print(f"❌ Invalid file type: {file_extension}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Only .log, .txt, and .csv files are allowed"
                )
            
            # Save file with UUID-based filename
            file_uuid = str(uuid.uuid4())
            unique_filename = f"{file_uuid}{file_extension}"
            upload_dir = f"uploads/{project_id}"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Read and save
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            print(f"💾 File saved: {file_path} ({len(content)} bytes)")
            
            # Create LogFile record with correct filename for parser
            log_file = LogFile(
                filename=unique_filename,  # Use UUID filename so parser can find it
                file_size=len(content),
                file_type=file_extension,
                user_id=current_user.id,
                project_id=project_id,  # Set project_id for proper foreign key
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
            
            # Process log file with parser - skip if fails (not critical)
            try:
                from app.services.log_parser.log_parser_service import LogParserService
                log_parser = LogParserService(db)
                await log_parser.process_log_file(log_file.id)
                print(f"✅ Processed log file: {file.filename}")
            except Exception as e:
                print(f"⚠️ Error processing log file (non-critical): {e}")
                logging.error(f"Error processing log file: {e}")
            
            # Read file content for prompt (skip RAG indexing to avoid greenlet errors)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                
                # Prepare file content for prompt (truncate if too long)
                if len(file_content) > 50000:
                    file_content_context = f"\n\n📄 Log File Content ({file.filename} - first 50KB):\n{file_content[:50000]}\n\n[File truncated - showing first 50KB]"
                else:
                    file_content_context = f"\n\n📄 Log File Content ({file.filename}):\n{file_content}"
                
                print(f"📄 File content loaded: {len(file_content)} characters")
                
            except Exception as read_error:
                print(f"⚠️ Error reading file content: {read_error}")
                logging.error(f"Error reading file content: {read_error}")
        
        # Build enhanced message with file content
        if file_content_context:
            enhanced_message = f"""{file_content_context}

User Question: {message}

Please analyze the log file content and answer the user's question based on the information provided in the log file."""
        else:
            # No file, just use the message
            enhanced_message = message
        
        # Generate AI response using unified chat service (same as project chats)
        try:
            print(f"🤖 Generating AI response via UnifiedChatService (OpenRouter Maverick)...")
            
            # Convert user to UserResponse format
            user_response = UserResponse(
                id=current_user.id,
                email=current_user.email,
                subscription_tier=current_user.subscription_tier,
                selected_llm_model="maverick",
                is_active=current_user.is_active,
                created_at=current_user.created_at,
                updated_at=current_user.updated_at
            )
            
            # Use unified chat service (same as project chats)
            response_text = await unified_chat_service.chat(
                message=enhanced_message,
                conversation_history=[],  # No conversation history for general chat
                user=user_response,
                db=db
            )
            
            print(f"✅ UnifiedChatService response: {response_text[:180]}...")
            
        except Exception as e:
            print(f"❌ Error generating AI response: {e}")
            logging.error(f"Error generating AI response: {e}")
            # Fallback response
            if file:
                response_text = f"I've received your log file '{file.filename}' and your question: '{message}'. However, I encountered an error processing your request. Please try again."
            else:
                response_text = f"I received your message: '{message}'. I'm here to help with log analysis. Please upload a log file if you'd like me to analyze it."
        
        result = {
            "response": response_text,
            "file_processed": file is not None,
            "file_info": file_info,
            "success": True
        }
        
        print(f"✅ Sending successful response")
        print(f"{'='*60}\n")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ ERROR in general_chat: {str(e)}")
        logging.error(f"ERROR in general_chat: {str(e)}", exc_info=True)
        print(f"{'='*60}\n")
        
        return {
            "response": "I'm here to help with log analysis. How can I assist you?",
            "file_processed": False,
            "success": False,
            "error": str(e)
        }


# Keep all other endpoints unchanged
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
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).offset(skip).limit(limit)
    )
    sessions = result.scalars().all()
    
    return sessions

