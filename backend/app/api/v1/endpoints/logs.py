from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.log_file import LogFile
from app.schemas.log_file import LogFile as LogFileSchema, LogFileCreate
from app.services.auth.auth_service import AuthService
from app.services.log_parser.log_parser_service import LogParserService

router = APIRouter()


@router.post("/upload", response_model=LogFileSchema)
async def upload_log_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Upload a log file for processing"""
    # Validate file type
    if not file.filename.endswith(('.log', '.txt', '.json', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("uploads", unique_filename)
    
    # Ensure upload directory exists
    os.makedirs("uploads", exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create database record
    log_file_data = LogFileCreate(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        file_type=file_extension,
        user_id=current_user.id
    )
    
    log_file = LogFile(**log_file_data.dict())
    db.add(log_file)
    db.commit()
    db.refresh(log_file)
    
    # Process file asynchronously
    log_parser = LogParserService(db)
    await log_parser.process_log_file(log_file.id)
    
    return log_file


@router.get("/", response_model=List[LogFileSchema])
async def get_log_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get user's log files"""
    log_files = db.query(LogFile).filter(
        LogFile.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return log_files


@router.get("/{log_file_id}", response_model=LogFileSchema)
async def get_log_file(
    log_file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get specific log file"""
    log_file = db.query(LogFile).filter(
        LogFile.id == log_file_id,
        LogFile.user_id == current_user.id
    ).first()
    
    if not log_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log file not found"
        )
    
    return log_file


@router.delete("/{log_file_id}")
async def delete_log_file(
    log_file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Delete log file"""
    log_file = db.query(LogFile).filter(
        LogFile.id == log_file_id,
        LogFile.user_id == current_user.id
    ).first()
    
    if not log_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log file not found"
        )
    
    # Delete physical file
    if os.path.exists(log_file.file_path):
        os.remove(log_file.file_path)
    
    # Delete database record
    db.delete(log_file)
    db.commit()
    
    return {"message": "Log file deleted successfully"}
