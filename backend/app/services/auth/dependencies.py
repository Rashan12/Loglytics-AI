"""
FastAPI dependencies for authentication
Provides dependency functions for protected endpoints
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from app.database import get_db
from app.services.auth.auth_service import AuthService
from app.services.auth.jwt_handler import JWTHandler
from app.schemas.user import UserResponse
from app.models.user import SubscriptionTier

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

class AuthDependencies:
    """Authentication dependency functions"""
    
    def __init__(self):
        self.jwt_handler = JWTHandler()
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> UserResponse:
        """
        Get current authenticated user from JWT token
        
        Args:
            credentials: HTTP authorization credentials
            db: Database session
            
        Returns:
            Current user data
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            token = credentials.credentials
            auth_service = AuthService(db)
            
            success, user, error_message = await auth_service.get_current_user(token)
            
            if not success or not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_message or "Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_current_user: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_current_active_user(
        self,
        current_user: UserResponse = Depends(lambda: AuthDependencies().get_current_user)
    ) -> UserResponse:
        """
        Get current active user (additional check for active status)
        
        Args:
            current_user: Current user from get_current_user
            
        Returns:
            Active user data
            
        Raises:
            HTTPException: If user is inactive
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user
    
    async def get_current_user_optional(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
        db: Session = Depends(get_db)
    ) -> Optional[UserResponse]:
        """
        Get current user if authenticated, None otherwise
        
        Args:
            credentials: Optional HTTP authorization credentials
            db: Database session
            
        Returns:
            Current user data or None
        """
        if not credentials:
            return None
        
        try:
            token = credentials.credentials
            auth_service = AuthService(db)
            
            success, user, _ = await auth_service.get_current_user(token)
            return user if success else None
            
        except Exception as e:
            logger.error(f"Error in get_current_user_optional: {e}")
            return None
    
    async def get_current_user_from_api_key(
        self,
        request: Request,
        db: Session = Depends(get_db)
    ) -> Optional[UserResponse]:
        """
        Get current user from API key (X-API-Key header)
        
        Args:
            request: FastAPI request object
            db: Database session
            
        Returns:
            Current user data or None
        """
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return None
        
        try:
            auth_service = AuthService(db)
            success, user, _ = await auth_service.authenticate_api_key(api_key)
            return user if success else None
            
        except Exception as e:
            logger.error(f"Error in get_current_user_from_api_key: {e}")
            return None
    
    async def get_current_user_jwt_or_api_key(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
        db: Session = Depends(get_db)
    ) -> Optional[UserResponse]:
        """
        Get current user from either JWT token or API key
        
        Args:
            request: FastAPI request object
            credentials: Optional HTTP authorization credentials
            db: Database session
            
        Returns:
            Current user data or None
        """
        # Try JWT first
        if credentials:
            try:
                token = credentials.credentials
                auth_service = AuthService(db)
                success, user, _ = await auth_service.get_current_user(token)
                if success and user:
                    return user
            except Exception as e:
                logger.debug(f"JWT authentication failed: {e}")
        
        # Try API key
        try:
            user = await self.get_current_user_from_api_key(request, db)
            if user:
                return user
        except Exception as e:
            logger.debug(f"API key authentication failed: {e}")
        
        return None
    
    async def require_authentication(
        self,
        current_user: Optional[UserResponse] = Depends(lambda: AuthDependencies().get_current_user_jwt_or_api_key)
    ) -> UserResponse:
        """
        Require authentication (JWT or API key)
        
        Args:
            current_user: Current user from get_current_user_jwt_or_api_key
            
        Returns:
            Authenticated user data
            
        Raises:
            HTTPException: If not authenticated
        """
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
    
    async def require_pro_subscription(
        self,
        current_user: UserResponse = Depends(lambda: AuthDependencies().get_current_active_user)
    ) -> UserResponse:
        """
        Require Pro subscription
        
        Args:
            current_user: Current active user
            
        Returns:
            Pro user data
            
        Raises:
            HTTPException: If not Pro subscriber
        """
        if current_user.subscription_tier != SubscriptionTier.PRO:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pro subscription required"
            )
        return current_user
    
    async def require_admin(
        self,
        current_user: UserResponse = Depends(lambda: AuthDependencies().get_current_active_user)
    ) -> UserResponse:
        """
        Require admin privileges
        
        Args:
            current_user: Current active user
            
        Returns:
            Admin user data
            
        Raises:
            HTTPException: If not admin
        """
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return current_user

# Create dependency instances
auth_deps = AuthDependencies()

# Export commonly used dependencies
get_current_user = auth_deps.get_current_user
get_current_active_user = auth_deps.get_current_active_user
get_current_user_optional = auth_deps.get_current_user_optional
require_authentication = auth_deps.require_authentication
require_pro_subscription = auth_deps.require_pro_subscription
require_admin = auth_deps.require_admin
