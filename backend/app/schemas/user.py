"""
User schemas for Loglytics AI
Pydantic models for user-related requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SubscriptionTier(str, Enum):
    """User subscription tier enumeration"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class LLMModel(str, Enum):
    """LLM model enumeration"""
    LOCAL = "local"
    MAVERICK = "maverick"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name")
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.FREE, description="Subscription tier")
    selected_llm_model: LLMModel = Field(default=LLMModel.LOCAL, description="Selected LLM model")

class UserCreate(BaseModel):
    """User creation schema - FIXED: made username optional, removed from base"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name")
    subscription_tier: Optional[SubscriptionTier] = Field(default=SubscriptionTier.FREE, description="Subscription tier")
    selected_llm_model: Optional[LLMModel] = Field(default=LLMModel.LOCAL, description="Selected LLM model")
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        
        return v

class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name")
    password: Optional[str] = Field(None, min_length=8, description="New password")
    subscription_tier: Optional[SubscriptionTier] = Field(None, description="Subscription tier")
    selected_llm_model: Optional[LLMModel] = Field(None, description="Selected LLM model")
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength if provided"""
        if v is None:
            return v
            
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        
        return v

class UserResponse(BaseModel):
    """User response schema"""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="Full name")
    subscription_tier: SubscriptionTier = Field(..., description="Subscription tier")
    selected_llm_model: LLMModel = Field(..., description="Selected LLM model")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True

# Alias for backward compatibility
User = UserResponse

class UserProfile(BaseModel):
    """User profile schema for detailed user information"""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="Full name")
    subscription_tier: SubscriptionTier = Field(..., description="Subscription tier")
    selected_llm_model: LLMModel = Field(..., description="Selected LLM model")
    is_active: bool = Field(..., description="Whether user is active")
    is_superuser: bool = Field(default=False, description="Whether user is superuser")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        from_attributes = True

class UserStats(BaseModel):
    """User statistics schema"""
    total_projects: int = Field(default=0, description="Total number of projects")
    total_log_files: int = Field(default=0, description="Total number of log files")
    total_log_entries: int = Field(default=0, description="Total number of log entries")
    total_chats: int = Field(default=0, description="Total number of chat sessions")
    storage_used_bytes: int = Field(default=0, description="Storage used in bytes")
    api_calls_count: int = Field(default=0, description="Total API calls made")
    llm_tokens_used: int = Field(default=0, description="Total LLM tokens used")

class UserPreferences(BaseModel):
    """User preferences schema"""
    theme: str = Field(default="system", description="UI theme preference")
    language: str = Field(default="en", description="Language preference")
    timezone: str = Field(default="UTC", description="Timezone preference")
    notifications_enabled: bool = Field(default=True, description="Whether notifications are enabled")
    email_notifications: bool = Field(default=True, description="Whether email notifications are enabled")
    push_notifications: bool = Field(default=False, description="Whether push notifications are enabled")
    auto_refresh_interval: int = Field(default=30, description="Auto refresh interval in seconds")
    default_project_id: Optional[str] = Field(None, description="Default project ID")

class UserActivity(BaseModel):
    """User activity schema"""
    id: str = Field(..., description="Activity ID")
    user_id: str = Field(..., description="User ID")
    activity_type: str = Field(..., description="Type of activity")
    description: str = Field(..., description="Activity description")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Activity timestamp")

class UserListResponse(BaseModel):
    """User list response schema"""
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")

class UserSearchRequest(BaseModel):
    """User search request schema"""
    query: Optional[str] = Field(None, description="Search query")
    subscription_tier: Optional[SubscriptionTier] = Field(None, description="Filter by subscription tier")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order (asc/desc)")

class UserBulkUpdate(BaseModel):
    """User bulk update schema"""
    user_ids: List[str] = Field(..., min_items=1, description="List of user IDs to update")
    updates: UserUpdate = Field(..., description="Updates to apply")
    reason: Optional[str] = Field(None, description="Reason for bulk update")

class UserExportRequest(BaseModel):
    """User export request schema"""
    format: str = Field(default="json", description="Export format (json/csv)")
    fields: List[str] = Field(default_factory=lambda: ["id", "email", "full_name", "subscription_tier", "created_at"], description="Fields to export")
    filters: Optional[dict] = Field(None, description="Export filters")

class UserImportRequest(BaseModel):
    """User import request schema"""
    data: List[dict] = Field(..., min_items=1, description="User data to import")
    update_existing: bool = Field(default=False, description="Whether to update existing users")
    send_welcome_email: bool = Field(default=True, description="Whether to send welcome emails")