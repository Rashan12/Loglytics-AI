from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class RAGVectorBase(BaseModel):
    content: str = Field(..., min_length=1)
    embedding: List[float] = Field(..., min_items=384, max_items=384)
    metadata: Optional[Dict[str, Any]] = None


class RAGVectorCreate(RAGVectorBase):
    project_id: UUID
    log_file_id: Optional[UUID] = None


class RAGVectorUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class RAGVectorInDB(RAGVectorBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    log_file_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RAGVector(RAGVectorInDB):
    pass


class RAGVectorResponse(BaseModel):
    id: UUID
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RAGVectorSearch(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=100)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
