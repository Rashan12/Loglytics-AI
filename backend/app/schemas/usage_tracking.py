from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class UsageTrackingBase(BaseModel):
    date: date
    llm_tokens_used: int = Field(0, ge=0)
    api_calls_count: int = Field(0, ge=0)
    storage_used_bytes: int = Field(0, ge=0)


class UsageTrackingCreate(UsageTrackingBase):
    pass


class UsageTrackingUpdate(BaseModel):
    llm_tokens_used: Optional[int] = Field(None, ge=0)
    api_calls_count: Optional[int] = Field(None, ge=0)
    storage_used_bytes: Optional[int] = Field(None, ge=0)


class UsageTrackingInDB(UsageTrackingBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsageTracking(UsageTrackingInDB):
    pass


class UsageTrackingResponse(BaseModel):
    id: UUID
    date: date
    llm_tokens_used: int
    api_calls_count: int
    storage_used_bytes: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
