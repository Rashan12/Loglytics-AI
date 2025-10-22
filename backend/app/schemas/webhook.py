from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class WebhookBase(BaseModel):
    url: str = Field(..., min_length=1)
    events: List[str] = Field(..., min_items=1)
    is_active: bool = True
    secret_key: Optional[str] = Field(None, max_length=255)


class WebhookCreate(WebhookBase):
    project_id: UUID


class WebhookUpdate(BaseModel):
    url: Optional[str] = Field(None, min_length=1)
    events: Optional[List[str]] = Field(None, min_items=1)
    is_active: Optional[bool] = None
    secret_key: Optional[str] = Field(None, max_length=255)


class WebhookInDB(WebhookBase):
    id: UUID
    user_id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Webhook(WebhookInDB):
    pass


class WebhookResponse(BaseModel):
    id: UUID
    url: str
    events: List[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
