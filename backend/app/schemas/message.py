from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.message import MessageRole


class MessageBase(BaseModel):
    role: MessageRole
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    chat_id: UUID


class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class MessageInDB(MessageBase):
    id: UUID
    chat_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class Message(MessageInDB):
    pass


class MessageResponse(BaseModel):
    id: UUID
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
