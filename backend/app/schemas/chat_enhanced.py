from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None
    file_id: Optional[str] = Field(None, description="Associated file ID")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous messages")
    file_id: Optional[str] = Field(None, description="Uploaded file ID for analysis")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    file_analyzed: Optional[bool] = Field(False, description="Whether a file was analyzed")

class ConversationHistory(BaseModel):
    conversation_id: str
    title: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime

class ConversationList(BaseModel):
    conversations: List[dict]
