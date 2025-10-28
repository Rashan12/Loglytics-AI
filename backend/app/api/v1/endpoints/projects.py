from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, desc, func
import uuid
import os
import shutil
from datetime import datetime
import logging

from app.database.session import get_db
from app.models.project import Project
from app.models.user import User
from app.models.chat_session import ChatSession, ChatMessage
from app.models.log_file import LogFile
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse
from app.schemas.user import UserResponse
from app.schemas.chat_enhanced import ChatMessage as ChatMessageSchema
from app.services.auth.jwt_handler import get_current_user
from app.services.chat_enhanced_service import enhanced_chat_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=ProjectListResponse)
async def get_user_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all projects for the current user"""
    try:
        result = await db.execute(
            select(Project).where(Project.user_id == current_user.id)
        )
        projects = result.scalars().all()
        
        # 🔧 FIX: Convert to response format for Pydantic v2
        project_responses = []
        for p in projects:
            try:
                project_responses.append(
                    ProjectResponse(
                        id=str(p.id),
                        name=p.name,
                        description=p.description or "",
                        user_id=str(p.user_id),
                        created_at=p.created_at,
                        updated_at=p.updated_at
                    )
                )
            except Exception as e:
                logger.error(f"❌ Error converting project {p.id}: {e}")
                continue

        logger.info(f"✅ Converted {len(project_responses)} projects")

        return ProjectListResponse(
            projects=project_responses,
            total=len(project_responses)
        )
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(500, str(e))

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    logger.info(f"📝 Creating project for user {current_user.id}: {project_data.name}")
    
    try:
        # Create project with minimal fields first
        new_project = Project(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            name=project_data.name,
            description=project_data.description
        )
        
        logger.info(f"📝 Project object created: {new_project.id}")
        
        db.add(new_project)
        logger.info("📝 Project added to session")
        
        await db.commit()
        logger.info("📝 Project committed to database")
        
        await db.refresh(new_project)
        logger.info("📝 Project refreshed from database")
        
        logger.info(f"✅ Project created: {new_project.id}")
        
        return {
            "id": new_project.id,
            "user_id": new_project.user_id,
            "name": new_project.name,
            "description": new_project.description,
            "created_at": new_project.created_at.isoformat(),
            "updated_at": new_project.updated_at.isoformat() if new_project.updated_at else None
        }
        
    except Exception as e:
        logger.error(f"❌ Project creation error: {e}", exc_info=True)
        try:
            await db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a project"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project_data.name:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    
    await db.commit()
    await db.refresh(project)
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await db.delete(project)
    await db.commit()

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
            
            allowed_extensions = ['.log', '.txt', '.csv']
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                print(f"❌ Invalid file type: {file_extension}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Only .log, .txt, and .csv files are allowed"
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
                # Don't set file_path for now - database doesn't have this column yet
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
            
            # Process log file with parser
            try:
                from app.services.log_parser.log_parser_service import LogParserService
                log_parser = LogParserService(db)
                await log_parser.process_log_file(log_file.id)
                print(f"✅ Processed log file: {file.filename}")
            except Exception as e:
                print(f"⚠️ Error processing log file: {e}")
            
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
                    log_file_id=str(log_file.id),
                    project_id=project_id,
                    user_id=current_user.id,
                    content=file_content,
                    file_type=file_extension[1:]  # Remove the dot
                )
                
                print(f"✅ Indexed log file for RAG: {file.filename}")
                
            except Exception as e:
                print(f"⚠️ Error indexing log file for RAG: {e}")
            
            # Process analytics for the uploaded log file (commented out to avoid greenlet errors)
            # Analytics will be processed asynchronously in the background
            try:
                # Just create the analysis record without processing for now
                from app.models.analysis import Analysis
                
                analysis = Analysis(
                    name=f"Auto-analysis for {file.filename}",
                    description=f"Automatic analysis of uploaded log file {file.filename}",
                    analysis_type="general",
                    log_file_id=int(log_file.id) if log_file.id.isdigit() else 0,
                    user_id=int(current_user.id),
                    results='{}',
                    status="pending"
                )
                db.add(analysis)
                await db.commit()
                print(f"✅ Created analytics analysis: {analysis.id}")
                
            except Exception as e:
                print(f"⚠️ Error creating analytics analysis: {e}")
        
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
        import json
        
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
    
    # Add user message to RAG system for context - temporarily disabled
    # try:
    #     from app.services.rag.rag_service import RAGService
    #     rag_service = RAGService(db)
    #     await rag_service.initialize()
    #     
    #     # Index the user message for future context
    #     await rag_service.index_conversation_message(
    #         message_id=str(user_message.id),
    #         conversation_id=conversation.session_id,
    #         user_id=current_user.id,
    #         content=message,
    #         role="user",
    #         project_id=project_id
    #     )
    #     
    #     logging.info(f"Indexed user message for RAG: {user_message.id}")
    #     
    # except Exception as e:
    #     logging.error(f"Error indexing user message for RAG: {e}")
    #     # Continue without RAG indexing if there's an error
    
        # Get conversation history for this project
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == conversation.id)
            .order_by(ChatMessage.created_at)
            .limit(10)
        )
        messages = result.scalars().all()
        
        history = [
            ChatMessageSchema(role=msg.role, content=msg.content, timestamp=msg.created_at)
            for msg in messages[-5:]  # Last 5 messages
        ]
        
        # Query RAG for relevant context
        rag_context = ""
        try:
            from app.services.rag.rag_service import RAGService
            rag_service = RAGService(db)
            await rag_service.initialize()
            
            # Query RAG for relevant context
            rag_response = await rag_service.query(
                question=message,
                project_id=project_id,
                user=current_user,
                max_chunks=5,
                similarity_threshold=0.7
            )
            
            if rag_response.sources:
                rag_context = "\n\n".join([
                    f"[Source {i+1}] {source.content}"
                    for i, source in enumerate(rag_response.sources[:5])
                ])
                print(f"✅ Retrieved {len(rag_response.sources)} relevant chunks from RAG")
            else:
                print("ℹ️ No relevant context found in RAG")
                
        except Exception as e:
            print(f"⚠️ Error querying RAG: {e}")
            # Continue without RAG context if there's an error
    
    # Get AI response with project context and RAG context using unified service
        project_context = f"Working on project: {project.name}\nDescription: {project.description or 'N/A'}"
        
        # Build enhanced message with context from uploaded files
        session_context = json.loads(conversation.context or "{}")
        uploaded_files_context = ""
        
        if "uploaded_files" in session_context and session_context["uploaded_files"]:
            uploaded_files_context = "\n\n📁 Previously uploaded files in this chat:\n"
            for file_info in session_context["uploaded_files"]:
                uploaded_files_context += f"• {file_info['filename']} ({file_info['size']} bytes) - uploaded {file_info['uploaded_at']}\n"
        
        # Build enhanced message with file content (RAG disabled)
        enhanced_message = f"""Project: {project.name}
Description: {project.description or 'N/A'}{uploaded_files_context}

User Question: {message}

Please provide assistance with this project. If you need log files to analyze, please ask the user to upload them."""
    
        # Generate AI response using LLM service
        try:
            from app.services.chat_unified_service import unified_chat_service
            from app.schemas.user import UserResponse
            
            # Convert user to UserResponse format
            user_response = UserResponse(
                id=current_user.id,
                email=current_user.email,
                subscription_tier=current_user.subscription_tier,
                selected_llm_model="maverick",
                is_active=current_user.is_active,
                created_at=datetime.now()
            )
            
            # Prepare conversation history
            conversation_history = [
                ChatMessageSchema(role=msg.role, content=msg.content, timestamp=msg.created_at)
                for msg in messages[-5:]  # Last 5 messages
            ]
            
            # Include content from uploaded files (current and previous)
            file_content_context = ""
            
            try:
                # Add content from currently uploaded file
                if file and file_info:
                    try:
                        # Read the uploaded file content
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            file_content = f.read()
                        
                        # Truncate if too long (keep first 50KB for analysis)
                        if len(file_content) > 50000:
                            file_content = file_content[:50000] + "\n\n[File truncated - showing first 50KB]"
                        
                        file_content_context += f"\n\n📄 Current Log File Content ({file.filename}):\n{file_content}"
                        print(f"📄 File content loaded: {len(file_content)} characters")
                        
                    except Exception as file_error:
                        print(f"⚠️ Error reading file content: {file_error}")
                        file_content_context += f"\n\n⚠️ Note: A log file '{file.filename}' was uploaded but I couldn't read its content."
                
                # Add content from previously uploaded files in this session
                if "uploaded_files" in session_context and session_context["uploaded_files"]:
                    for file_info in session_context["uploaded_files"]:
                        try:
                            # Find the file path for previously uploaded files
                            result = await db.execute(
                                select(LogFile).where(LogFile.id == file_info["id"])
                            )
                            log_file = result.scalar_one_or_none()
                            
                            if log_file:
                                # Construct file path
                                prev_file_path = os.path.join(UPLOAD_DIR, log_file.filename)
                                
                                if os.path.exists(prev_file_path):
                                    with open(prev_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        prev_file_content = f.read()
                                    
                                    # Truncate if too long
                                    if len(prev_file_content) > 30000:
                                        prev_file_content = prev_file_content[:30000] + "\n\n[File truncated - showing first 30KB]"
                                    
                                    file_content_context += f"\n\n📄 Previous Log File Content ({file_info['filename']}):\n{prev_file_content}"
                                    print(f"📄 Previous file content loaded: {file_info['filename']} ({len(prev_file_content)} characters)")
                        
                        except Exception as prev_file_error:
                            print(f"⚠️ Error reading previous file content: {prev_file_error}")
                            continue
                            
            except Exception as content_error:
                print(f"⚠️ Error processing file content: {content_error}")
                file_content_context = ""
            
            # Enhance the message with all file content and RAG context
            if file_content_context:
                rag_context_text = f"RAG Context from previous logs:\n{rag_context}\n" if rag_context else ""
                enhanced_message = f"""User asked: {message}

Context: Working on project '{project.name}'{uploaded_files_context}

Log file content:
{file_content_context}

{rag_context_text}

Answer the user's question using the log content above. Be direct and helpful."""
                print(f"📝 Enhanced message with file content: {len(enhanced_message)} characters")
                print(f"📄 File content included: {len(file_content_context)} characters")
                if rag_context:
                    print(f"🔍 RAG context included: {len(rag_context)} characters")
            else:
                rag_context_text = f"RAG Context from previous logs:\n{rag_context}\n" if rag_context else ""
                enhanced_message = f"""You are Loglytics AI.

User asked: {message}

Context: Working on project '{project.name}'{uploaded_files_context}

{rag_context_text}

IMPORTANT: Answer the user's question directly. Do not ask for file uploads unless the user specifically asks about file uploads. Be direct and helpful."""
                print(f"📝 Enhanced message without file content: {len(enhanced_message)} characters")
                if rag_context:
                    print(f"🔍 RAG context included: {len(rag_context)} characters")
            
            # Generate AI response
            response_text = await unified_chat_service.chat(
                message=enhanced_message,
                conversation_history=conversation_history,
                conversation_id=conversation.session_id,
                file_id=file_info["id"] if file_info else None,
                user_id=current_user.id,
                project_id=project_id,
                db=db,
                user=user_response
            )
            
            print(f"💬 Generated AI response: {response_text[:100]}...")
            
        except Exception as e:
            print(f"⚠️ LLM service error: {e}")
            import traceback
            traceback.print_exc()
            
            # Rollback database transaction to prevent PendingRollbackError
            try:
                await db.rollback()
                print("🔄 Database transaction rolled back due to error")
            except Exception as rollback_error:
                print(f"⚠️ Error during rollback: {rollback_error}")
            
            # DON'T use fallback - let the actual error response through
            # The chat service already returns an error message
            if 'response_text' not in locals():
                response_text = "I encountered an error. Please try again."
        
        print(f"💬 Final response: {response_text}")
    
        # Save assistant message with proper transaction handling
        try:
            # Create a new message object
            assistant_message = ChatMessage(
                session_id=conversation.id,
                role="assistant",
                content=response_text,
                created_at=datetime.now()
            )
            
            # Add to session
            db.add(assistant_message)
            
            # Update conversation timestamp
            conversation.updated_at = datetime.now()
            
            # Commit both changes together
            await db.commit()
            await db.refresh(assistant_message)
            print("✅ Assistant message saved successfully")
            
        except Exception as save_error:
            print(f"⚠️ Error saving assistant message: {save_error}")
            # Rollback the transaction to clear the error state
            try:
                await db.rollback()
                print("🔄 Database rolled back after message save error")
            except Exception as rollback_error:
                print(f"⚠️ Error during rollback: {rollback_error}")
            # Don't re-raise the error - continue with the response so user still gets their answer
    
    # Add assistant message to RAG system for context - temporarily disabled
    # try:
    #     # Index the assistant message for future context
    #     await rag_service.index_conversation_message(
    #         message_id=str(assistant_message.id),
    #         conversation_id=conversation.session_id,
    #         user_id=current_user.id,
    #         content=ai_response,
    #         role="assistant",
    #         project_id=project_id
    #     )
    #     
    #     logging.info(f"Indexed assistant message for RAG: {assistant_message.id}")
    #     
    # except Exception as e:
    #     logging.error(f"Error indexing assistant message for RAG: {e}")
    #     # Continue without RAG indexing if there's an error
    
        result = {
            "response": response_text,
            "file_processed": file is not None,
            "file_info": file_info,
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"✅ Sending successful response")
        print(f"{'='*60}\n")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR in project_chat: {str(e)}")
        print(f"{'='*60}\n")
        
        # Re-raise to return proper error
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.get("/{project_id}/analytics")
async def get_project_analytics(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific project"""
    try:
        # Verify project exists and belongs to user
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(404, "Project not found")
        
        # Get log file count for this project
        log_file_result = await db.execute(
            select(func.count(LogFile.id)).where(LogFile.project_id == project_id)
        )
        log_file_count = log_file_result.scalar() or 0
        
        # Get chat count for this project (if chat table exists)
        try:
            from app.models.chat_session import ChatSession
            chat_result = await db.execute(
                select(func.count(ChatSession.id)).where(ChatSession.user_id == current_user.id)
            )
            chat_count = chat_result.scalar() or 0
        except:
            chat_count = 0
        
        # Mock analytics data for now
        analytics = {
            "project_id": project_id,
            "total_logs": log_file_count,
            "total_chats": chat_count,
            "error_rate": 2.5,
            "last_activity": project.updated_at.isoformat() if project.updated_at else project.created_at.isoformat(),
            "status": "active"
        }
        
        logger.info(f"📊 Project analytics for {project_id}: {analytics}")
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Project analytics error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get project analytics: {str(e)}")

@router.get("/{project_id}/chats")
async def get_project_chats(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chats for a project"""
    # Verify project belongs to user
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get all conversations for this project
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.user_id == current_user.id,
            ChatSession.title.like(f"%{project.name}%")
        )
        .order_by(desc(ChatSession.updated_at))
    )
    conversations = result.scalars().all()
    
    return {
        "chats": [
            {
                "id": str(conv.session_id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
            }
            for conv in conversations
        ]
    }

@router.get("/{project_id}/chat/history")
async def get_project_chat_history(
    project_id: str,
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a project and optionally a specific session"""
    # Verify project belongs to user
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
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
    else:
        # Get the most recent conversation for this project
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
        logger.info(f"No conversation found for project {project_id}")
        return {"messages": []}
    
    logger.info(f"Found conversation {conversation.id} for project {project_id}")
    
    # Get messages for this conversation
    # Note: ChatMessage.session_id refers to ChatSession.id (PK), not ChatSession.session_id
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == conversation.id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    
    logger.info(f"Found conversation {conversation.id} (session_id: {conversation.session_id})")
    logger.info(f"Found {len(messages)} messages for conversation {conversation.id}")
    
    return {
        "session_id": conversation.session_id,
        "conversation_id": str(conversation.id),
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else datetime.now().isoformat()
            }
            for msg in messages
        ]
    }

@router.post("/{project_id}/chat/new")
async def create_project_chat(
    project_id: str,
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat for a project"""
    # Verify project belongs to user
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Create new chat session
    new_session_id = str(uuid.uuid4())
    conversation = ChatSession(
        id=str(uuid.uuid4()),
        session_id=new_session_id,
        user_id=current_user.id,
        title=title or f"{project.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        context="{}",
        created_at=datetime.now()
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    logger.info(f"Created new chat {conversation.session_id} for project {project_id}")
    
    return {
        "id": conversation.session_id,
        "title": conversation.title,
        "session_id": conversation.session_id,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None
    }

@router.options("")
async def projects_options():
    """Handle OPTIONS request for CORS preflight"""
    return Response(status_code=200)
