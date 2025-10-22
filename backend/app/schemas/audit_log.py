from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from ipaddress import IPv4Address, IPv6Address
from typing import Union


class AuditLogBase(BaseModel):
    action: str = Field(..., min_length=1, max_length=100)
    resource_type: str = Field(..., min_length=1, max_length=100)
    resource_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[Union[IPv4Address, IPv6Address]] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogInDB(AuditLogBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLog(AuditLogInDB):
    pass


class AuditLogResponse(BaseModel):
    id: UUID
    action: str
    resource_type: str
    resource_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
