from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class APIKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    expires_at: Optional[datetime] = None
    is_active: bool = True


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class APIKeyInDB(APIKeyBase):
    id: UUID
    user_id: UUID
    key_hash: str
    last_used_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class APIKey(APIKeyInDB):
    pass


class APIKeyResponse(BaseModel):
    id: UUID
    name: str
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyCreateResponse(BaseModel):
    id: UUID
    name: str
    key: str  # Only returned on creation
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
