from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class Project(ProjectResponse):
    """Alias for ProjectResponse for backward compatibility"""
    pass


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
