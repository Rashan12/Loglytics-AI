from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.log_entry import LogLevel


class LogEntryBase(BaseModel):
    timestamp: datetime
    log_level: Optional[LogLevel] = None
    message: str = Field(..., min_length=1)
    source: Optional[str] = Field(None, max_length=255)
    metadata: Optional[Dict[str, Any]] = None
    raw_content: Optional[str] = None


class LogEntryCreate(LogEntryBase):
    log_file_id: UUID
    project_id: UUID


class LogEntryUpdate(BaseModel):
    log_level: Optional[LogLevel] = None
    message: Optional[str] = Field(None, min_length=1)
    source: Optional[str] = Field(None, max_length=255)
    metadata: Optional[Dict[str, Any]] = None
    raw_content: Optional[str] = None


class LogEntryInDB(LogEntryBase):
    id: UUID
    log_file_id: UUID
    project_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LogEntry(LogEntryInDB):
    pass


class LogEntryResponse(BaseModel):
    id: UUID
    timestamp: datetime
    log_level: Optional[LogLevel] = None
    message: str
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_content: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True