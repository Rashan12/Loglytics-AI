from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AnalysisBase(BaseModel):
    name: str
    description: Optional[str] = None
    analysis_type: str
    query: Optional[str] = None


class AnalysisCreate(AnalysisBase):
    log_file_id: Optional[int] = None
    user_id: int
    results: Dict[str, Any]


class AnalysisUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    query: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    is_public: Optional[bool] = None


class AnalysisInDB(AnalysisBase):
    id: int
    log_file_id: Optional[int] = None
    user_id: int
    results: str  # JSON string
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    is_public: bool

    class Config:
        from_attributes = True


class Analysis(AnalysisInDB):
    pass
