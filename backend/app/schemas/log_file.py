from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.log_file import UploadStatus


class LogFileBase(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    file_size: Optional[int] = None
    file_type: Optional[str] = Field(None, max_length=50)
    s3_key: Optional[str] = None
    upload_status: UploadStatus = UploadStatus.UPLOADING
    processing_metadata: Optional[Dict[str, Any]] = None


class LogFileCreate(LogFileBase):
    project_id: UUID
    chat_id: Optional[UUID] = None


class LogFileUpdate(BaseModel):
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    upload_status: Optional[UploadStatus] = None
    processing_metadata: Optional[Dict[str, Any]] = None


class LogFileInDB(LogFileBase):
    id: UUID
    chat_id: Optional[UUID] = None
    project_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LogFile(LogFileInDB):
    pass


class LogFileResponse(BaseModel):
    id: UUID
    filename: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    upload_status: UploadStatus
    processing_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True