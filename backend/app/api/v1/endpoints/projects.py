from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime
import uuid
import os
import logging
import json

from app.database.session import get_db
from app.models.project import Project
from app.models.chat_session import ChatSession, ChatMessage
from app.models.user import User
from app.models.log_file import LogFile
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.user import UserResponse
from app.services.auth.jwt_handler import get_current_user
from app.services.chat_unified_service import unified_chat_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Project CRUD Endpoints
@router.get("", response_model=List[ProjectResponse])
async def get_user_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all projects for the current user"""
    try:
        result = await db.execute(
            select(Project).where(Project.user_id == current_user.id).order_by(desc(Project.created_at))
        )
        projects = result.scalars().all()
        return projects
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to get projects")

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    try:
        new_project = Project(
            id=str(uuid.uuid4()),
            name=project_data.name,
            description=project_data.description,
            user_id=current_user.id
        )
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        return new_project
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project"""
    try:
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(status_code=500, detail="Failed to get project")

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a project"""
    try:
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if project_data.name is not None:
            project.name = project_data.name
        if project_data.description is not None:
            project.description = project_data.description
        
        await db.commit()
        await db.refresh(project)
        return project
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating project: {e}")
        raise HTTPException(status_code=500, detail="Failed to update project")

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    try:
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        await db.delete(project)
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete project")

# Project Chat Endpoints
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{project_id}/chat")
async def chat_in_project(
    project_id: str,
    message: str = Form(...),
    file: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Project chat endpoint with file upload support
    """
    print(f"\n{'='*60}")
    print(f"📨 PROJECT CHAT REQUEST")
    print(f"{'='*60}")
    print(f"Project ID: {project_id}")
    print(f"User: {current_user.email}")
    print(f"Message: {message}")
    print(f"File: {file.filename if file else 'None'}")
    print(f"{'='*60}\n")
    
    try:
        # Verify project exists and user has access
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            print(f"❌ Project {project_id} not found for user {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        print(f"✅ Project verified: {project.name}")
        
        # Process file if uploaded
        file_info = None
        file_path = None
        content = b""
        
        # Initialize file_info to empty dict if no file
        if not file:
            file_info = {}
        
        if file:
            print(f"📎 Processing file: {file.filename}")
            
            # Validate file
            if file.size > 100 * 1024 * 1024:  # 100MB limit
                print(f"❌ File too large: {file.size} bytes")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size exceeds 100MB limit"
                )
            
            # FIX: Allow .json files in addition to .log, .txt, .csv
            allowed_extensions = ['.log', '.txt', '.csv', '.json']
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                print(f"❌ Invalid file type: {file_extension}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Only .log, .txt, .csv, and .json files are allowed"
                )
            
            # Save file
            file_id = str(uuid.uuid4())
            upload_dir = f"uploads/{project_id}"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
            
            # Read and save
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            print(f"💾 File saved: {file_path} ({len(content)} bytes)")
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create database record
            log_file = LogFile(
                filename=f"{file_id}_{file.filename}",
                file_size=len(content),
                file_type=file_extension,
                project_id=project_id,
                user_id=current_user.id,
                upload_status="completed"
            )
            db.add(log_file)
            await db.commit()
            await db.refresh(log_file)
            
            print(f"✅ File record created: ID {log_file.id}")
            
            file_info = {
                "id": str(log_file.id),
                "filename": file.filename,
                "size": len(content)
            }
            
            # Process file in background (non-blocking) - don't wait for completion
            # This allows the chat to respond immediately while processing happens async
            import asyncio
            
            async def process_file_background():
                try:
                    # Create a new database session for background task
                    from app.database.session import AsyncSessionLocal
                    async with AsyncSessionLocal() as async_db:
                        # Process log file with parser
                        try:
                            from app.services.log_parser.log_parser_service import LogParserService
                            log_parser = LogParserService(async_db)
                            await log_parser.process_log_file(log_file.id)
                            print(f"✅ Processed log file: {file.filename}")
                        except Exception as e:
                            print(f"⚠️ Error processing log file: {e}")
                        
                        # Index log file for RAG
                        try:
                            from app.services.rag.rag_service import RAGService
                            rag_service = RAGService(async_db)
                            await rag_service.initialize()
                            
                            # Read file content for indexing (handle both text and JSON files)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    file_content = f.read()
                            except Exception:
                                # If text reading fails, try binary
                                file_content = content.decode('utf-8', errors='ignore')
                            
                            # Index the log file for RAG
                            await rag_service.index_log_file(
                                log_file_id=str(log_file.id),
                                project_id=project_id,
                                user_id=current_user.id,
                                content=file_content,
                                file_type=file_extension[1:]  # Remove the dot
                            )
                            
                            print(f"✅ Indexed log file for RAG: {file.filename}")
                            
                        except Exception as e:
                            print(f"⚠️ Error indexing log file for RAG: {e}")
                        
                        # Process analytics for the uploaded log file
                        try:
                            from app.models.analysis import Analysis
                            
                            analysis = Analysis(
                                name=f"Auto-analysis for {file.filename}",
                                description=f"Automatic analysis of uploaded log file {file.filename}",
                                analysis_type="general",
                                log_file_id=str(log_file.id),
                                user_id=str(current_user.id),
                                results='{}',
                                status="pending"
                            )
                            async_db.add(analysis)
                            await async_db.commit()
                            print(f"✅ Created analytics analysis: {analysis.id}")
                            
                        except Exception as e:
                            print(f"⚠️ Error creating analytics analysis: {e}")
                except Exception as e:
                    print(f"⚠️ Error in background file processing: {e}")
            
            # Start background task (runs after response is sent)
            asyncio.create_task(process_file_background())
            print(f"🚀 Started background processing for: {file.filename}")
        
        # Get or create conversation for this project
        # If session_id is provided, get that specific conversation
        if session_id:
            result = await db.execute(
                select(ChatSession)
                .where(
                    ChatSession.session_id == session_id,
                    ChatSession.user_id == current_user.id
                )
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                print(f"❌ Chat session {session_id} not found, creating new one")
                conversation = None  # Will create new one below
        else:
            conversation = None
        
        # If no conversation found, get the most recent chat for this project
        if not conversation:
            result = await db.execute(
                select(ChatSession)
                .where(
                    ChatSession.user_id == current_user.id,
                    ChatSession.title.like(f"%{project.name}%")
                )
                .order_by(desc(ChatSession.updated_at))
                .limit(1)
            )
            conversation = result.scalar_one_or_none()
        
        # If still no conversation, create one
        if not conversation:
            new_session_id = str(uuid.uuid4())
            conversation = ChatSession(
                id=str(uuid.uuid4()),
                session_id=new_session_id,
                user_id=current_user.id,
                title=f"{project.name}",
                context="{}",  # Initialize with empty JSON context
                created_at=datetime.now()
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            print(f"✅ Created new conversation: {conversation.session_id}")
        
        # Update conversation context with uploaded file information
        try:
            session_context = json.loads(conversation.context or "{}")
            
            # Add uploaded file to context
            if file_info:
                if "uploaded_files" not in session_context:
                    session_context["uploaded_files"] = []
                
                # Check if file already exists in context
                file_exists = any(f["id"] == file_info["id"] for f in session_context["uploaded_files"])
                if not file_exists:
                    session_context["uploaded_files"].append({
                        "id": file_info["id"],
                        "filename": file_info["filename"],
                        "size": file_info["size"],
                        "uploaded_at": datetime.now().isoformat()
                    })
                
                # Update conversation context
                conversation.context = json.dumps(session_context)
                await db.commit()
                print(f"📝 Updated chat session context with file: {file_info['filename']}")
                
        except Exception as context_error:
            print(f"⚠️ Error updating session context: {context_error}")
            # Continue without context update if there's an error
        
        # Save user message
        user_message = ChatMessage(
            session_id=conversation.id,
            role="user",
            content=message,
            created_at=datetime.now()
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)
        
        # Use RAG to retrieve relevant chunks instead of sending entire file
        # This is much faster and more efficient for large files
        file_content_context = ""
        if file and file_path:
            try:
                # Try to use RAG search to get relevant chunks
                from app.services.rag.rag_service import RAGService
                rag_service = RAGService(db)
                await rag_service.initialize()
                
                # Search for relevant content using RAG
                try:
                    rag_results = await rag_service.search_similar_content(
                        content=message,
                        project_id=project_id,
                        user_id=current_user.id,
                        limit=5  # Get top 5 most relevant chunks
                    )
                    
                    if rag_results and len(rag_results) > 0:
                        # Build context from RAG results
                        file_content_context = f"\n\n📄 Relevant Log File Content from '{file.filename}':\n"
                        for i, result in enumerate(rag_results[:3], 1):  # Top 3 chunks
                            content = result.get('content', result.get('content_preview', ''))
                            if content:
                                # Limit each chunk to 2000 chars
                                chunk = content[:2000] + "..." if len(content) > 2000 else content
                                file_content_context += f"\n[Chunk {i}]:\n{chunk}\n"
                        print(f"✅ Retrieved {len(rag_results)} relevant chunks via RAG")
                    else:
                        # Fallback: read a small sample if RAG not ready yet
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                # Read first 10KB as sample
                                sample = f.read(10000)
                                if sample:
                                    file_content_context = f"\n\n📄 Log File Sample from '{file.filename}' (first 10KB):\n{sample}\n\n[Note: Full file is being indexed. More context will be available shortly.]"
                        except:
                            pass
                except Exception as rag_error:
                    print(f"⚠️ RAG search not available yet (file may still be indexing): {rag_error}")
                    # Fallback: small sample
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            sample = f.read(10000)
                            if sample:
                                file_content_context = f"\n\n📄 Log File Sample from '{file.filename}' (first 10KB):\n{sample}\n\n[Note: Full file is being indexed in the background. More context will be available in subsequent messages.]"
                    except:
                        pass
            except Exception as e:
                print(f"⚠️ Error getting file context: {e}")
                # Final fallback: small sample
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        sample = f.read(10000)
                        if sample:
                            file_content_context = f"\n\n📄 Log File Sample from '{file.filename}' (first 10KB):\n{sample}"
                except:
                    pass
        
        # Build enhanced message with RAG-retrieved context
        if file_content_context:
            enhanced_message = f"""{file_content_context}

User Question: {message}

Please analyze the relevant log file content above and answer the user's question based on the information provided."""
        else:
            enhanced_message = message
        
        # Generate AI response using unified chat service
        try:
            print(f"🤖 Generating AI response via UnifiedChatService...")
            
            # Convert user to UserResponse format
            user_response = UserResponse(
                id=current_user.id,
                email=current_user.email,
                subscription_tier=current_user.subscription_tier,
                selected_llm_model=getattr(current_user, 'selected_llm_model', 'maverick'),
                is_active=current_user.is_active,
                created_at=current_user.created_at,
                updated_at=current_user.updated_at
            )
            
            # Get conversation history
            history_result = await db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == conversation.id)
                .order_by(ChatMessage.created_at)
                .limit(10)  # Last 10 messages for context
            )
            history_messages = history_result.scalars().all()
            
            # FIX 2: Convert to ChatMessage schema objects (not dicts) for unified_chat_service
            from app.schemas.chat_enhanced import ChatMessage as ChatMessageSchema
            
            conversation_history = []
            for msg in history_messages:
                if msg.id != user_message.id:  # Don't include the message we just added
                    conversation_history.append(
                        ChatMessageSchema(
                            role=msg.role,
                            content=msg.content
                        )
                    )
            
            # Use unified chat service
            response_text = await unified_chat_service.chat(
                message=enhanced_message,
                conversation_history=conversation_history,
                user=user_response,
                db=db
            )
            
            print(f"✅ UnifiedChatService response: {response_text[:180]}...")
            
        except Exception as e:
            print(f"❌ Error generating AI response: {e}")
            logger.error(f"Error generating AI response: {e}")
            # Fallback response
            if file:
                response_text = f"I've received your log file '{file.filename}' and your question: '{message}'. However, I encountered an error processing your request. Please try again."
            else:
                response_text = f"I received your message: '{message}'. I'm here to help with log analysis. Please upload a log file if you'd like me to analyze it."
        
        # Save AI response
        ai_message = ChatMessage(
            session_id=conversation.id,
            role="assistant",
            content=response_text,
            created_at=datetime.now()
        )
        db.add(ai_message)
        await db.commit()
        
        # Update conversation updated_at
        conversation.updated_at = datetime.now()
        await db.commit()
        
        result = {
            "response": response_text,
            "file_processed": file is not None,
            "file_info": file_info,
            "session_id": conversation.session_id,
            "success": True
        }
        
        print(f"✅ Sending successful response")
        print(f"{'='*60}\n")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ ERROR in chat_in_project: {str(e)}")
        logger.error(f"ERROR in chat_in_project: {str(e)}", exc_info=True)
        print(f"{'='*60}\n")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )

@router.post("/{project_id}/chat/new")
async def create_new_chat(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session for a project"""
    try:
        # Verify project exists
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create new chat session
        new_session_id = str(uuid.uuid4())
        conversation = ChatSession(
            id=str(uuid.uuid4()),
            session_id=new_session_id,
            user_id=current_user.id,
            title=f"{project.name}",
            context="{}",
            created_at=datetime.now()
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
        return {"session_id": conversation.session_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating new chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@router.get("/{project_id}/chat/history")
async def get_chat_history(
    project_id: str,
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a project"""
    try:
        # Verify project exists
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get chat session
        if session_id:
            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.session_id == session_id,
                    ChatSession.user_id == current_user.id
                )
            )
            conversation = result.scalar_one_or_none()
        else:
            # Get most recent chat for this project
            result = await db.execute(
                select(ChatSession)
                .where(
                    ChatSession.user_id == current_user.id,
                    ChatSession.title.like(f"%{project.name}%")
                )
                .order_by(desc(ChatSession.updated_at))
                .limit(1)
            )
            conversation = result.scalar_one_or_none()
        
        if not conversation:
            return {"session_id": None, "messages": []}
        
        # Get messages
        messages_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == conversation.id)
            .order_by(ChatMessage.created_at)
        )
        messages = messages_result.scalars().all()
        
        return {
            "session_id": conversation.session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")

