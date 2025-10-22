from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.project_share import ShareRole


class ProjectShareBase(BaseModel):
    role: ShareRole


class ProjectShareCreate(ProjectShareBase):
    project_id: UUID
    shared_with_user_id: UUID


class ProjectShareUpdate(BaseModel):
    role: Optional[ShareRole] = None


class ProjectShareInDB(ProjectShareBase):
    id: UUID
    project_id: UUID
    shared_by_user_id: UUID
    shared_with_user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectShare(ProjectShareInDB):
    pass


class ProjectShareResponse(BaseModel):
    id: UUID
    project_id: UUID
    shared_by_user_id: UUID
    shared_with_user_id: UUID
    role: ShareRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
