from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.alert import AlertType, AlertSeverity


class AlertBase(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity
    message: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    notified_via: Optional[Dict[str, Any]] = None


class AlertCreate(AlertBase):
    project_id: UUID
    live_connection_id: Optional[UUID] = None


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    notified_via: Optional[Dict[str, Any]] = None


class AlertInDB(AlertBase):
    id: UUID
    user_id: UUID
    project_id: UUID
    live_connection_id: Optional[UUID] = None
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class Alert(AlertInDB):
    pass


class AlertResponse(BaseModel):
    id: UUID
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    metadata: Optional[Dict[str, Any]] = None
    is_read: bool
    notified_via: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
