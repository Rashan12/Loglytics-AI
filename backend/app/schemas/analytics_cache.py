from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class AnalyticsCacheBase(BaseModel):
    analytics_type: str = Field(..., min_length=1, max_length=100)
    analytics_data: Dict[str, Any]


class AnalyticsCacheCreate(AnalyticsCacheBase):
    project_id: UUID
    log_file_id: UUID


class AnalyticsCacheUpdate(BaseModel):
    analytics_type: Optional[str] = Field(None, min_length=1, max_length=100)
    analytics_data: Optional[Dict[str, Any]] = None


class AnalyticsCacheInDB(AnalyticsCacheBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    log_file_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalyticsCache(AnalyticsCacheInDB):
    pass


class AnalyticsCacheResponse(BaseModel):
    id: UUID
    analytics_type: str
    analytics_data: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
