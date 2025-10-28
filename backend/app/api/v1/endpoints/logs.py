from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
import os
import uuid
from datetime import datetime
import logging

from app.database.session import get_db
from app.models.user import User
from app.models.log_file import LogFile
from app.models.log_entry import LogEntry
from app.services.auth.jwt_handler import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Directory to store uploaded log files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/files")
async def get_user_log_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all log files for the current user"""
    try:
        # Get all log files for this user, ordered by most recent first
        log_files_result = await db.execute(
            select(LogFile)
            .where(LogFile.user_id == current_user.id)
            .order_by(desc(LogFile.created_at))
        )
        log_files = log_files_result.scalars().all()
        
        # Process log files data and deduplicate
        files_data = []
        seen_filenames = {}  # Track filenames we've seen for deduplication
        
        for log_file in log_files:
            # Extract actual filename without UUID prefix
            actual_filename = log_file.filename
            if '_' in actual_filename:
                # Remove the UUID prefix (everything before the last underscore)
                parts = actual_filename.rsplit('_', 1)
                if len(parts) == 2 and len(parts[0]) > 10:
                    # Likely has UUID prefix, use the second part
                    actual_filename = parts[1]
                else:
                    # Just use the original
                    actual_filename = log_file.filename
            
            # Check for duplicates by actual filename
            if actual_filename in seen_filenames:
                # This is a duplicate, skip it
                logger.debug(f"Skipping duplicate file: {actual_filename}")
                continue
            
            # Get log entry count for this file
            try:
                entry_count_result = await db.execute(
                    select(func.count(LogEntry.id)).where(LogEntry.log_file_id == log_file.id)
                )
                entry_count = entry_count_result.scalar() or 0
            except:
                entry_count = 0
            
            files_data.append({
                "id": str(log_file.id),
                "filename": actual_filename,  # Use cleaned filename
                "original_filename": log_file.filename,  # Keep original for reference
                "size": log_file.file_size or 0,
                "uploadedAt": log_file.created_at.isoformat() if log_file.created_at else None,
                "status": log_file.upload_status.value if hasattr(log_file.upload_status, 'value') else log_file.upload_status,
                "logCount": entry_count
            })
            
            seen_filenames[actual_filename] = log_file
        
        logger.info(f"📄 Retrieved {len(files_data)} log files for user {current_user.id}")
        
        return {
            "files": files_data,
            "total": len(files_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Get log files error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get log files: {str(e)}")

@router.post("/upload")
async def upload_log_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a log file for processing"""
    try:
        # Validate file type
        allowed_extensions = ['.log', '.txt', '.csv']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .log, .txt, and .csv files are allowed"
            )
        
        # Validate file size
        if file.size and file.size > 100 * 1024 * 1024:  # 100MB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 100MB limit"
            )
        
        # Read file content
        content = await file.read()
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        unique_filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        file_size = len(content)
        
        # Create database record (direct uploads don't require project_id)
        # Note: project_id can be null for direct uploads
        log_file = LogFile(
            filename=unique_filename,
            file_size=file_size,
            file_type=file_extension,
            upload_status="completed",
            user_id=current_user.id,
            project_id=None,  # Direct upload, no project
            chat_id=None  # Direct upload, no chat
        )
        db.add(log_file)
        await db.commit()
        await db.refresh(log_file)
        
        # Process file with parser
        try:
            from app.services.log_parser.log_parser_service import LogParserService
            parser = LogParserService(db)
            await parser.process_log_file(str(log_file.id))
            logger.info(f"✅ Processed log file: {file.filename}")
        except Exception as e:
            logger.warning(f"Could not process log file: {e}")
        
        # Index file for RAG
        try:
            from app.services.rag.rag_service import RAGService
            rag_service = RAGService(db)
            await rag_service.initialize()
            
            # Decode content for indexing
            file_content = content.decode('utf-8', errors='ignore')
            
            # Index the log file for RAG
            await rag_service.index_log_file(
                log_file_id=str(log_file.id),
                project_id="default",  # Use "default" for direct uploads
                user_id=current_user.id,
                content=file_content,
                file_type=file_extension[1:]  # Remove the dot
            )
            logger.info(f"✅ Indexed log file for RAG: {file.filename}")
        except Exception as e:
            logger.warning(f"Could not index log file for RAG: {e}")
        
        logger.info(f"📤 Uploaded log file: {file.filename} ({file_size} bytes)")
        
        return {
            "id": str(log_file.id),
            "filename": file.filename,
            "size": file_size,
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to upload file: {str(e)}")

@router.delete("/files/{file_id}")
async def delete_log_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a log file"""
    try:
        # Get log file
        result = await db.execute(
            select(LogFile).where(
                LogFile.id == file_id,
                LogFile.user_id == current_user.id
            )
        )
        log_file = result.scalar_one_or_none()
        
        if not log_file:
            raise HTTPException(404, "Log file not found")
        
        # Delete file if exists
        file_path = os.path.join(UPLOAD_DIR, log_file.filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not delete physical file: {e}")
        
        # Delete database record
        await db.delete(log_file)
        await db.commit()
        
        logger.info(f"🗑️ Deleted log file: {file_id}")
        
        return {"message": "Log file deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to delete file: {str(e)}")

@router.get("/files/{file_id}/download")
async def download_log_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download a log file"""
    try:
        # Get log file
        result = await db.execute(
            select(LogFile).where(
                LogFile.id == file_id,
                LogFile.user_id == current_user.id
            )
        )
        log_file = result.scalar_one_or_none()
        
        if not log_file:
            raise HTTPException(404, "Log file not found")
        
        # Try multiple possible file locations
        possible_paths = []
        
        # For direct uploads (project_id is None)
        if not log_file.project_id:
            possible_paths.append(os.path.join(UPLOAD_DIR, log_file.filename))
        # For project-based uploads
        else:
            possible_paths.append(os.path.join(UPLOAD_DIR, str(log_file.project_id), log_file.filename))
        
        # Also try just the filename in base directory (for backward compatibility)
        possible_paths.append(os.path.join(UPLOAD_DIR, log_file.filename))
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path or not os.path.exists(file_path):
            logger.error(f"❌ Physical file not found. Tried: {possible_paths}")
            raise HTTPException(404, "Physical file not found")
        
        # Return file content
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=log_file.filename.split('_', 1)[-1] if '_' in log_file.filename else log_file.filename,  # Return original filename
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Download error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to download file: {str(e)}")
