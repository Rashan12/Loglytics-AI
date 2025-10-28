from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta, datetime
from pydantic import BaseModel
import uuid
from app.database.session import get_db
from app.services.auth.jwt_handler import get_current_user, create_access_token
from app.models.user import User
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

class RegisterResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """User login"""
    print(f"\n{'='*60}")
    print(f"LOGIN REQUEST")
    print(f"{'='*60}")
    print(f"Email: {login_data.email}")
    print(f"{'='*60}\n")
    
    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("ERROR: Authentication failed - User not found")
            raise HTTPException(401, "Invalid credentials")
        
        # For now, we'll skip password verification (you should add proper password hashing)
        # In production, you should verify the password hash
        
        # Create token with 7-day expiration
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        
        print(f"SUCCESS: Login successful for: {user.email}")
        print(f"{'='*60}\n")
        
        return {
            "access_token": access_token,
            "refresh_token": access_token,  # For now, use same token as refresh
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": getattr(user, 'full_name', 'User'),
                "subscription_tier": "free",
                "selected_llm_model": "maverick",
                "is_active": getattr(user, 'is_active', True),
                "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
                "updated_at": user.updated_at.isoformat() if hasattr(user, 'updated_at') and user.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(401, "Invalid credentials")

@router.post("/register", response_model=RegisterResponse)
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """User registration"""
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == register_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(400, "User with this email already exists")
        
        # Create new user (for now, we'll skip password hashing)
        new_user = User(
            id=str(uuid.uuid4()),
            email=register_data.email,
            full_name=register_data.full_name,
            is_active=True,
            created_at=datetime.now()
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Create token with 7-day expiration
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        access_token = create_access_token(
            data={"sub": new_user.id, "email": new_user.email},
            expires_delta=access_token_expires
        )
        
        logger.info(f"✅ User registered: {new_user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": access_token,  # For now, use same token as refresh
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "subscription_tier": "free",
                "selected_llm_model": "maverick",
                "is_active": new_user.is_active,
                "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
                "updated_at": new_user.updated_at.isoformat() if new_user.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(500, "Registration failed")

@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        # Create new token
        access_token = create_access_token(
            data={"sub": current_user.id, "email": current_user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(401, "Token refresh failed")

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user info"""
    try:
        result = await db.execute(
            select(User).where(User.id == current_user["id"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(404, "User not found")
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(500, str(e))