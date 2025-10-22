from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ChatBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ChatCreate(ChatBase):
    project_id: UUID


class ChatUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)


class ChatInDB(ChatBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Chat(ChatInDB):
    pass


class ChatResponse(BaseModel):
    id: UUID
    title: str
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True