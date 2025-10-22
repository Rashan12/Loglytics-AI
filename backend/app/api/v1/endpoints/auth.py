"""
Authentication endpoints for Loglytics AI
Handles user registration, login, password management, and API keys
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession  # CHANGED: AsyncSession instead of Session
from typing import Dict, Any, List
import logging

from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.auth.auth_service import AuthService
from app.services.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    require_authentication
)
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyListResponse,
    UserUpdateRequest
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)  # CHANGED: AsyncSession
) -> LoginResponse:
    """
    Register a new user and return authentication tokens

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        JWT tokens and created user data

    Raises:
        HTTPException: If registration fails
    """
    try:
        auth_service = AuthService(db)
        success, user, error_message = await auth_service.register_user(user_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        # FIXED: Create tokens for newly registered user so they are automatically logged in
        tokens = auth_service.create_tokens(user)

        logger.info(f"User registered successfully: {user.email}")
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=user
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in register endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)  # CHANGED: AsyncSession
) -> LoginResponse:
    """
    Authenticate user and return JWT tokens
    
    Args:
        login_data: Login request data with email and password
        db: Database session
        
    Returns:
        JWT tokens and user data
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        auth_service = AuthService(db)
        success, user, error_message = await auth_service.authenticate_user(
            login_data.email,  # Use email field directly
            login_data.password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message,
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        tokens = auth_service.create_tokens(user)  # REMOVED: await (create_tokens is sync)
        
        logger.info(f"User logged in successfully: {user.email}")
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)  # CHANGED: AsyncSession
) -> RefreshTokenResponse:
    """
    Refresh access token using refresh token
    
    Args:
        refresh_data: Refresh token data
        db: Database session
        
    Returns:
        New access token
        
    Raises:
        HTTPException: If refresh fails
    """
    try:
        auth_service = AuthService(db)
        success, tokens, error_message = auth_service.refresh_tokens(  # REMOVED: await (refresh_tokens is sync)
            refresh_data.refresh_token
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message
            )
        
        return RefreshTokenResponse(
            access_token=tokens["access_token"],
            token_type=tokens["token_type"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    current_user: UserResponse = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Logout user (client should discard tokens)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Logout confirmation
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}

@router.post("/password-reset-request")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)  # CHANGED: AsyncSession
) -> Dict[str, str]:
    """
    Request password reset
    
    Args:
        reset_data: Password reset request data
        db: Database session
        
    Returns:
        Reset request confirmation
    """
    try:
        auth_service = AuthService(db)
        success, message = await auth_service.request_password_reset(reset_data.email)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {"message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in password reset request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/password-reset-confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)  # CHANGED: AsyncSession
) -> Dict[str, str]:
    """
    Confirm password reset with token
    
    Args:
        reset_data: Password reset confirmation data
        db: Database session
        
    Returns:
        Reset confirmation
    """
    try:
        auth_service = AuthService(db)
        success, message = await auth_service.reset_password(
            reset_data.token,
            reset_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {"message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in password reset confirm: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdateRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)  # CHANGED: AsyncSession
) -> UserResponse:
    """
    Update current user information
    
    Args:
        update_data: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user data
        
    Raises:
        HTTPException: If update fails
    """
    try:
        auth_service = AuthService(db)
        
        # Convert to UserUpdate schema
        user_update = UserUpdate(
            email=update_data.email,
            username=update_data.username,
            full_name=update_data.full_name,
            password=update_data.password
        )
        
        success, user, error_message = await auth_service.update_user(
            str(current_user.id),
            user_update
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        logger.info(f"User updated successfully: {user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update user endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )

@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)  # CHANGED: AsyncSession
) -> APIKeyResponse:
    """
    Create a new API key
    
    Args:
        key_data: API key creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created API key data
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        auth_service = AuthService(db)
        success, api_key, error_message = await auth_service.create_api_key(
            str(current_user.id),
            key_data.name
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        logger.info(f"API key created for user: {current_user.email}")
        return APIKeyResponse(
            id="",  # Will be set by the response model
            name=key_data.name,
            key=api_key,
            created_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create API key endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key creation failed"
        )

@router.get("/api-keys", response_model=APIKeyListResponse)
async def list_api_keys(
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)  # CHANGED: AsyncSession
) -> APIKeyListResponse:
    """
    List user's API keys
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of API keys
    """
    try:
        auth_service = AuthService(db)
        api_keys = await auth_service.get_user_api_keys(str(current_user.id))
        
        return APIKeyListResponse(api_keys=api_keys)
        
    except Exception as e:
        logger.error(f"Error in list API keys endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API keys"
        )

@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)  # CHANGED: AsyncSession
) -> Dict[str, str]:
    """
    Delete an API key
    
    Args:
        key_id: API key ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Deletion confirmation
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        auth_service = AuthService(db)
        success, message = await auth_service.delete_api_key(
            str(current_user.id),
            key_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        logger.info(f"API key deleted by user: {current_user.email}")
        return {"message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete API key endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key deletion failed"
        )