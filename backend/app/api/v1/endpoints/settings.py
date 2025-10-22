"""
Settings API endpoints for Loglytics AI
Handles user settings, preferences, and account management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserPreferences
from app.services.auth.auth_service import AuthService
from app.services.auth.dependencies import get_current_user

router = APIRouter()

# User Profile Endpoints

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    try:
        auth_service = AuthService(db)
        updated_user = await auth_service.update_user(current_user.id, user_update)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/me/avatar")
async def upload_user_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload user avatar"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (5MB limit)
        if file.size and file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")
        
        # In a real implementation, you would:
        # 1. Save the file to cloud storage (S3, etc.)
        # 2. Update the user's avatar_url in the database
        # 3. Return the new avatar URL
        
        # For now, return a mock response
        avatar_url = f"https://example.com/avatars/{current_user.id}/{uuid.uuid4()}.jpg"
        
        return {
            "avatar_url": avatar_url,
            "message": "Avatar uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Password Management

@router.put("/me/password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    try:
        auth_service = AuthService(db)
        success = await auth_service.change_password(
            current_user.id, 
            current_password, 
            new_password
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Two-Factor Authentication

@router.post("/me/2fa/enable")
async def enable_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enable two-factor authentication"""
    try:
        # In a real implementation, you would:
        # 1. Generate a secret key
        # 2. Create a QR code
        # 3. Generate backup codes
        # 4. Store the secret in the database
        
        # Mock response
        return {
            "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "backup_codes": [
                "12345678",
                "87654321",
                "11223344",
                "44332211",
                "55667788"
            ],
            "secret": "JBSWY3DPEHPK3PXP"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/me/2fa/disable")
async def disable_2fa(
    code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disable two-factor authentication"""
    try:
        # In a real implementation, you would:
        # 1. Verify the 2FA code
        # 2. Disable 2FA for the user
        # 3. Clear the secret from the database
        
        return {"message": "Two-factor authentication disabled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Subscription Management

@router.get("/subscription/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current subscription details"""
    try:
        # Mock subscription data
        subscription = {
            "tier": current_user.subscription_tier,
            "status": "active",
            "current_period_start": (datetime.utcnow() - timedelta(days=15)).isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=15)).isoformat(),
            "cancel_at_period_end": False,
            "features": {
                "local_llm": True,
                "cloud_llm": current_user.subscription_tier == "pro",
                "max_projects": 5 if current_user.subscription_tier == "free" else -1,
                "storage_gb": 10 if current_user.subscription_tier == "free" else 100,
                "advanced_analytics": current_user.subscription_tier == "pro",
                "priority_support": current_user.subscription_tier == "pro"
            },
            "usage": {
                "llm_tokens_used": 15000,
                "storage_used_gb": 2.5,
                "api_calls": 1250
            }
        }
        
        return subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/subscription/upgrade")
async def upgrade_subscription(
    tier: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade subscription tier"""
    try:
        if tier not in ["pro", "enterprise"]:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        
        # In a real implementation, you would:
        # 1. Process payment
        # 2. Update user subscription tier
        # 3. Send confirmation email
        
        return {"message": f"Subscription upgraded to {tier} successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/subscription/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel subscription"""
    try:
        # In a real implementation, you would:
        # 1. Set cancel_at_period_end to True
        # 2. Send confirmation email
        # 3. Log the cancellation
        
        return {"message": "Subscription cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API Keys Management

@router.get("/api-keys")
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's API keys"""
    try:
        # In a real implementation, you would fetch from the database
        # Mock API keys data
        api_keys = [
            {
                "id": "key_1",
                "name": "My App Integration",
                "masked_key": "sk-...abc123",
                "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "last_used": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "permissions": ["read", "write"],
                "is_active": True
            },
            {
                "id": "key_2",
                "name": "Development Key",
                "masked_key": "sk-...def456",
                "created_at": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "last_used": None,
                "permissions": ["read"],
                "is_active": True
            }
        ]
        
        return {"api_keys": api_keys}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api-keys")
async def create_api_key(
    name: str,
    permissions: List[str],
    expires_at: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new API key"""
    try:
        # In a real implementation, you would:
        # 1. Generate a secure API key
        # 2. Store it in the database
        # 3. Return the key (only shown once)
        
        api_key = f"sk-{uuid.uuid4().hex}"
        
        return {
            "id": f"key_{uuid.uuid4().hex[:8]}",
            "name": name,
            "key": api_key,
            "masked_key": f"sk-...{api_key[-8:]}",
            "created_at": datetime.utcnow().isoformat(),
            "permissions": permissions,
            "is_active": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke API key"""
    try:
        # In a real implementation, you would:
        # 1. Find the API key
        # 2. Mark it as inactive
        # 3. Log the revocation
        
        return {"message": "API key revoked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Notification Settings

@router.get("/notifications")
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get notification settings"""
    try:
        # Mock notification settings
        settings = {
            "email_notifications": {
                "new_alerts": True,
                "daily_summary": False,
                "weekly_reports": True,
                "product_updates": True,
                "security_alerts": True
            },
            "in_app_notifications": {
                "desktop_notifications": False,
                "sound_alerts": True,
                "alert_threshold": "high+"
            },
            "slack_integration": {
                "connected": False,
                "workspace_name": None,
                "channel": None,
                "alert_types": []
            },
            "jira_integration": {
                "connected": False,
                "instance_url": None,
                "project_key": None,
                "issue_type": None,
                "auto_create_for": []
            }
        }
        
        return settings
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/notifications")
async def update_notification_settings(
    settings: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update notification settings"""
    try:
        # In a real implementation, you would:
        # 1. Validate the settings
        # 2. Store them in the database
        # 3. Apply any necessary changes
        
        return {"message": "Notification settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Security Settings

@router.get("/security/sessions")
async def get_active_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get active sessions"""
    try:
        # Mock active sessions data
        sessions = [
            {
                "id": "session_1",
                "device": "Chrome on Windows",
                "browser": "Chrome 120.0",
                "ip_address": "192.168.1.100",
                "location": "New York, US",
                "last_active": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "is_current": True
            },
            {
                "id": "session_2",
                "device": "Safari on iPhone",
                "browser": "Safari 17.0",
                "ip_address": "203.0.113.1",
                "location": "San Francisco, US",
                "last_active": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "is_current": False
            }
        ]
        
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/security/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke a specific session"""
    try:
        # In a real implementation, you would:
        # 1. Find the session
        # 2. Mark it as revoked
        # 3. Log the action
        
        return {"message": "Session revoked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/security/sessions")
async def revoke_all_other_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke all sessions except current"""
    try:
        # In a real implementation, you would:
        # 1. Find all sessions except current
        # 2. Mark them as revoked
        # 3. Log the action
        
        return {"message": "All other sessions revoked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/security/login-history")
async def get_login_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get login history"""
    try:
        # Mock login history data
        history = [
            {
                "id": "login_1",
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "ip_address": "192.168.1.100",
                "location": "New York, US",
                "device": "Chrome on Windows",
                "status": "success",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            {
                "id": "login_2",
                "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "ip_address": "203.0.113.1",
                "location": "San Francisco, US",
                "device": "Safari on iPhone",
                "status": "success",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
            },
            {
                "id": "login_3",
                "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "ip_address": "198.51.100.1",
                "location": "Unknown",
                "device": "Unknown",
                "status": "failed",
                "user_agent": "Mozilla/5.0 (compatible; bot)"
            }
        ]
        
        return {"login_history": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Billing Information

@router.get("/billing/info")
async def get_billing_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get billing information"""
    try:
        # Mock billing info
        billing_info = {
            "payment_method": {
                "type": "card",
                "last4": "4242",
                "brand": "visa",
                "expiry_month": 12,
                "expiry_year": 2025
            },
            "billing_address": {
                "name": "John Doe",
                "line1": "123 Main St",
                "line2": "Apt 4B",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States"
            },
            "invoices": [
                {
                    "id": "inv_001",
                    "date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    "amount": 29.00,
                    "status": "paid",
                    "download_url": f"/api/v1/settings/billing/invoices/inv_001/download"
                },
                {
                    "id": "inv_002",
                    "date": (datetime.utcnow() - timedelta(days=60)).isoformat(),
                    "amount": 29.00,
                    "status": "paid",
                    "download_url": f"/api/v1/settings/billing/invoices/inv_002/download"
                }
            ]
        }
        
        return billing_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/billing/usage")
async def get_billing_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current billing usage"""
    try:
        # Mock usage data
        usage = {
            "llm_tokens_used": 15000,
            "storage_used_gb": 2.5,
            "api_calls": 1250,
            "current_month_charges": 29.00
        }
        
        return usage
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Account Management

@router.delete("/me")
async def delete_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user account"""
    try:
        # In a real implementation, you would:
        # 1. Verify the password
        # 2. Schedule account deletion (GDPR compliance)
        # 3. Send confirmation email
        # 4. Log the action
        
        return {"message": "Account deletion scheduled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/me/export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export user data"""
    try:
        # In a real implementation, you would:
        # 1. Collect all user data
        # 2. Create a downloadable archive
        # 3. Send download link via email
        
        return {
            "message": "Data export initiated",
            "download_url": f"/api/v1/settings/me/export/{uuid.uuid4()}",
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
