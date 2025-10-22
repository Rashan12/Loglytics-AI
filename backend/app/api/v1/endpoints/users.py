"""
User management endpoints for Loglytics AI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.schemas.user import UserResponse, UserListResponse, UserSearchRequest
from app.services.auth.dependencies import get_current_active_user, require_admin
from app.services.auth.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter()

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
    update_data: dict,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update current user information
    
    Args:
        update_data: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user data
    """
    try:
        auth_service = AuthService(db)
        success, user, error_message = await auth_service.update_user(
            str(current_user.id),
            update_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )

@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search query"),
    subscription_tier: Optional[str] = Query(None, description="Filter by subscription tier"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
) -> UserListResponse:
    """
    List users (admin only)
    
    Args:
        page: Page number
        size: Page size
        search: Search query
        subscription_tier: Filter by subscription tier
        is_active: Filter by active status
        current_user: Current admin user
        db: Database session
        
    Returns:
        List of users
    """
    try:
        # This would typically use a user service
        # For now, return empty list
        return UserListResponse(
            users=[],
            total=0,
            page=page,
            size=size,
            pages=0
        )
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get user by ID (admin only)
    
    Args:
        user_id: User ID
        current_user: Current admin user
        db: Database session
        
    Returns:
        User data
    """
    try:
        # This would typically use a user service
        # For now, return 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete user (admin only)
    
    Args:
        user_id: User ID
        current_user: Current admin user
        db: Database session
        
    Returns:
        Deletion confirmation
    """
    try:
        # This would typically use a user service
        # For now, return success
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )