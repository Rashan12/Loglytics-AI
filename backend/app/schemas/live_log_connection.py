from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.live_log_connection import CloudProvider, ConnectionStatus


class LiveLogConnectionBase(BaseModel):
    connection_name: str = Field(..., min_length=1, max_length=255)
    cloud_provider: CloudProvider
    connection_config: Dict[str, Any]
    status: ConnectionStatus = ConnectionStatus.ACTIVE


class LiveLogConnectionCreate(LiveLogConnectionBase):
    project_id: UUID


class LiveLogConnectionUpdate(BaseModel):
    connection_name: Optional[str] = Field(None, min_length=1, max_length=255)
    connection_config: Optional[Dict[str, Any]] = None
    status: Optional[ConnectionStatus] = None


class LiveLogConnectionInDB(LiveLogConnectionBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LiveLogConnection(LiveLogConnectionInDB):
    pass


class LiveLogConnectionResponse(BaseModel):
    id: UUID
    connection_name: str
    cloud_provider: CloudProvider
    status: ConnectionStatus
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LiveLogConnectionTest(BaseModel):
    """Schema for testing live log connections"""
    connection_config: Dict[str, Any]
    cloud_provider: CloudProvider
