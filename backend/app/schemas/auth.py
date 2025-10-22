"""
Authentication schemas for Loglytics AI
Pydantic models for authentication requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")

class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="JWT refresh token")

class RefreshTokenResponse(BaseModel):
    """Refresh token response schema"""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email address")

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
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

class UserUpdateRequest(BaseModel):
    """User update request schema"""
    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name")
    password: Optional[str] = Field(None, min_length=8, description="New password")
    
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

class APIKeyCreate(BaseModel):
    """API key creation schema"""
    name: str = Field(..., min_length=1, max_length=100, description="API key name")

class APIKeyResponse(BaseModel):
    """API key response schema"""
    id: str = Field(..., description="API key ID")
    name: str = Field(..., description="API key name")
    key: str = Field(..., description="API key value")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")

class APIKeyInfo(BaseModel):
    """API key information schema (without the actual key)"""
    id: str = Field(..., description="API key ID")
    name: str = Field(..., description="API key name")
    is_active: bool = Field(..., description="Whether the key is active")
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")

class APIKeyListResponse(BaseModel):
    """API key list response schema"""
    api_keys: List[APIKeyInfo] = Field(..., description="List of API keys")

class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    subscription_tier: Optional[str] = None

class AuthResponse(BaseModel):
    """Generic authentication response schema"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Additional response data")

class PasswordStrengthResponse(BaseModel):
    """Password strength validation response schema"""
    is_valid: bool = Field(..., description="Whether the password is valid")
    score: int = Field(..., ge=0, le=10, description="Password strength score (0-10)")
    errors: List[str] = Field(..., description="List of validation errors")
    suggestions: List[str] = Field(..., description="List of improvement suggestions")

class SecuritySettings(BaseModel):
    """Security settings schema"""
    password_min_length: int = Field(default=8, description="Minimum password length")
    password_require_uppercase: bool = Field(default=True, description="Require uppercase letters")
    password_require_lowercase: bool = Field(default=True, description="Require lowercase letters")
    password_require_numbers: bool = Field(default=True, description="Require numbers")
    password_require_special_chars: bool = Field(default=False, description="Require special characters")
    session_timeout_minutes: int = Field(default=15, description="Session timeout in minutes")
    max_login_attempts: int = Field(default=5, description="Maximum login attempts")
    lockout_duration_minutes: int = Field(default=30, description="Account lockout duration")

class LoginAttempt(BaseModel):
    """Login attempt schema"""
    email: EmailStr = Field(..., description="User email")
    ip_address: str = Field(..., description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    success: bool = Field(..., description="Whether login was successful")
    timestamp: datetime = Field(..., description="Attempt timestamp")

class SecurityEvent(BaseModel):
    """Security event schema"""
    event_type: str = Field(..., description="Type of security event")
    user_id: Optional[str] = Field(None, description="User ID if applicable")
    ip_address: str = Field(..., description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    details: Optional[dict] = Field(None, description="Event details")
    timestamp: datetime = Field(..., description="Event timestamp")
    severity: str = Field(default="medium", description="Event severity level")

class RateLimitInfo(BaseModel):
    """Rate limit information schema"""
    limit: int = Field(..., description="Rate limit")
    remaining: int = Field(..., description="Remaining requests")
    reset_time: datetime = Field(..., description="Reset time")
    retry_after: Optional[int] = Field(None, description="Retry after seconds")

class AuthStatus(BaseModel):
    """Authentication status schema"""
    is_authenticated: bool = Field(..., description="Whether user is authenticated")
    user: Optional[UserResponse] = Field(None, description="User information if authenticated")
    token_type: Optional[str] = Field(None, description="Token type if authenticated")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
