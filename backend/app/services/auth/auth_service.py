"""
Authentication service for Loglytics AI
Handles user registration, login, password management, and API keys
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession  # CHANGED: AsyncSession instead of Session
from sqlalchemy import select, and_, or_  # ADDED: select for async queries
from email_validator import validate_email, EmailNotValidError
import logging

from app.models.user import User, SubscriptionTier, LLMModel
from app.models.api_key import APIKey
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.auth.password_handler import PasswordHandler
from app.services.auth.jwt_handler import JWTHandler
# REMOVED: from app.core.security import create_access_token (not needed)

logger = logging.getLogger(__name__)

class AuthService:
    """Main authentication service"""
    
    def __init__(self, db: AsyncSession):  # CHANGED: AsyncSession
        self.db = db
        self.password_handler = PasswordHandler()
        self.jwt_handler = JWTHandler()
    
    async def register_user(self, user_data: UserCreate) -> Tuple[bool, Optional[UserResponse], str]:
        """
        Register a new user
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of (success, user_data, error_message)
        """
        try:
            # Validate email format
            try:
                valid_email = validate_email(user_data.email)
                email = valid_email.email
            except EmailNotValidError:
                return False, None, "Invalid email format"
            
            # Check if user already exists - CHANGED to async
            result = await self.db.execute(
                select(User).filter(
                    or_(User.email == email)
                )
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                return False, None, "Email already registered"
            
            # Validate password strength
            is_valid, password_errors = self.password_handler.validate_password_strength(user_data.password)
            if not is_valid:
                return False, None, f"Password validation failed: {', '.join(password_errors)}"
            
            # Check for password breach
            if self.password_handler.check_password_breach(user_data.password):
                return False, None, "Password appears in breach databases. Please choose a stronger password."
            
            # Hash password
            hashed_password = self.password_handler.hash_password(user_data.password)

            # Create new user
            db_user = User(
                email=email,
                password_hash=hashed_password,
                full_name=user_data.full_name,
                subscription_tier=user_data.subscription_tier if hasattr(user_data, 'subscription_tier') else SubscriptionTier.FREE,
                selected_llm_model=user_data.selected_llm_model if hasattr(user_data, 'selected_llm_model') else LLMModel.LOCAL,
                is_active=True
            )

            # Add to database
            self.db.add(db_user)
            await self.db.commit()  # CHANGED: await
            await self.db.refresh(db_user)  # CHANGED: await
            
            logger.info(f"User registered successfully: {email}")
            
            # Return user data without password
            user_response = UserResponse(
                id=db_user.id,
                email=db_user.email,
                full_name=db_user.full_name,
                subscription_tier=db_user.subscription_tier,
                selected_llm_model=db_user.selected_llm_model,
                is_active=db_user.is_active,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at or db_user.created_at  # Fallback to created_at if None
            )
            
            return True, user_response, "User registered successfully"
            
        except Exception as e:
            logger.error(f"Error registering user: {e}", exc_info=True)
            await self.db.rollback()  # CHANGED: await
            return False, None, "Registration failed. Please try again."
    
    async def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[UserResponse], str]:
        """
        Authenticate a user with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, user_data, error_message)
        """
        try:
            # Find user by email - CHANGED to async
            result = await self.db.execute(
                select(User).filter(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"Login attempt with non-existent email: {email}")
                return False, None, "Invalid credentials"
            
            if not user.is_active:
                logger.warning(f"Login attempt with inactive account: {email}")
                return False, None, "Account is deactivated"
            
            # Verify password
            if not self.password_handler.verify_password(password, user.password_hash):
                logger.warning(f"Failed login attempt for: {email}")
                return False, None, "Invalid credentials"
            
            # Check if password needs update
            if self.password_handler.needs_update(user.password_hash):
                logger.info(f"Password needs update for user: {email}")
                # In production, you might want to force password update
            
            logger.info(f"User authenticated successfully: {email}")
            
            # Return user data
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                subscription_tier=user.subscription_tier,
                selected_llm_model=user.selected_llm_model,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at or user.created_at  # Fallback to created_at if None
            )
            
            return True, user_response, "Authentication successful"
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}", exc_info=True)
            return False, None, "Authentication failed"
    
    def create_tokens(self, user: UserResponse) -> Dict[str, str]:  # REMOVED async - this is sync
        """
        Create JWT tokens for authenticated user
        
        Args:
            user: User data
            
        Returns:
            Dictionary containing tokens
        """
        return self.jwt_handler.create_token_pair(
            user_id=str(user.id),
            email=user.email,
            subscription_tier=user.subscription_tier.value if hasattr(user.subscription_tier, 'value') else str(user.subscription_tier)
        )
    
    def refresh_tokens(self, refresh_token: str) -> Tuple[bool, Optional[Dict[str, str]], str]:  # REMOVED async
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Tuple of (success, tokens, error_message)
        """
        try:
            tokens = self.jwt_handler.refresh_access_token(refresh_token)
            if tokens:
                return True, tokens, "Tokens refreshed successfully"
            else:
                return False, None, "Invalid or expired refresh token"
        except Exception as e:
            logger.error(f"Error refreshing tokens: {e}", exc_info=True)
            return False, None, "Token refresh failed"
    
    async def get_current_user(self, token: str) -> Tuple[bool, Optional[UserResponse], str]:
        """
        Get current user from JWT token
        
        Args:
            token: JWT access token
            
        Returns:
            Tuple of (success, user_data, error_message)
        """
        try:
            payload = self.jwt_handler.verify_token(token, "access")
            if not payload:
                return False, None, "Invalid or expired token"
            
            user_id = payload.get("sub")
            if not user_id:
                return False, None, "Invalid token payload"
            
            # Get user from database - CHANGED to async
            result = await self.db.execute(
                select(User).filter(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                return False, None, "User not found or inactive"
            
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                subscription_tier=user.subscription_tier,
                selected_llm_model=user.selected_llm_model,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at or user.created_at  # Fallback to created_at if None
            )
            
            return True, user_response, "User retrieved successfully"
            
        except Exception as e:
            logger.error(f"Error getting current user: {e}", exc_info=True)
            return False, None, "Failed to get user"
    
    async def update_user(self, user_id: str, update_data: UserUpdate) -> Tuple[bool, Optional[UserResponse], str]:
        """
        Update user information
        
        Args:
            user_id: User ID
            update_data: Update data
            
        Returns:
            Tuple of (success, user_data, error_message)
        """
        try:
            # CHANGED to async
            result = await self.db.execute(
                select(User).filter(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False, None, "User not found"
            
            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            
            # Handle password update
            if "password" in update_dict and update_dict["password"]:
                password = update_dict.pop("password")
                
                # Validate password strength
                is_valid, password_errors = self.password_handler.validate_password_strength(password)
                if not is_valid:
                    return False, None, f"Password validation failed: {', '.join(password_errors)}"
                
                # Check for password breach
                if self.password_handler.check_password_breach(password):
                    return False, None, "Password appears in breach databases. Please choose a stronger password."
                
                # Hash new password
                update_dict["password_hash"] = self.password_handler.hash_password(password)
            
            # Update user
            for field, value in update_dict.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            await self.db.commit()  # CHANGED: await
            await self.db.refresh(user)  # CHANGED: await
            
            logger.info(f"User updated successfully: {user.email}")
            
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                subscription_tier=user.subscription_tier,
                selected_llm_model=user.selected_llm_model,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at or user.created_at  # Fallback to created_at if None
            )
            
            return True, user_response, "User updated successfully"
            
        except Exception as e:
            logger.error(f"Error updating user: {e}", exc_info=True)
            await self.db.rollback()  # CHANGED: await
            return False, None, "User update failed"
    
    async def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """
        Request password reset
        
        Args:
            email: User email
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # CHANGED to async
            result = await self.db.execute(
                select(User).filter(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # Don't reveal if email exists
                return True, "If the email exists, a reset link has been sent"
            
            # Create password reset token
            reset_token = self.jwt_handler.create_password_reset_token(
                str(user.id), user.email
            )
            
            # In production, you would send this token via email
            # For now, we'll just log it
            logger.info(f"Password reset token for {email}: {reset_token}")
            
            return True, "If the email exists, a reset link has been sent"
            
        except Exception as e:
            logger.error(f"Error requesting password reset: {e}", exc_info=True)
            return False, "Password reset request failed"
    
    async def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password using reset token
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Verify reset token
            payload = self.jwt_handler.verify_password_reset_token(token)
            if not payload:
                return False, "Invalid or expired reset token"
            
            user_id = payload.get("sub")
            if not user_id:
                return False, "Invalid reset token"
            
            # Get user - CHANGED to async
            result = await self.db.execute(
                select(User).filter(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False, "User not found"
            
            # Validate new password
            is_valid, password_errors = self.password_handler.validate_password_strength(new_password)
            if not is_valid:
                return False, f"Password validation failed: {', '.join(password_errors)}"
            
            # Check for password breach
            if self.password_handler.check_password_breach(new_password):
                return False, "Password appears in breach databases. Please choose a stronger password."
            
            # Update password
            user.password_hash = self.password_handler.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            await self.db.commit()  # CHANGED: await
            
            logger.info(f"Password reset successfully for user: {user.email}")
            return True, "Password reset successfully"
            
        except Exception as e:
            logger.error(f"Error resetting password: {e}", exc_info=True)
            await self.db.rollback()  # CHANGED: await
            return False, "Password reset failed"
    
    async def create_api_key(self, user_id: str, key_name: str) -> Tuple[bool, Optional[str], str]:
        """
        Create a new API key for user
        
        Args:
            user_id: User ID
            key_name: Name for the API key
            
        Returns:
            Tuple of (success, api_key, error_message)
        """
        try:
            # Generate secure API key
            api_key = self._generate_api_key()
            key_hash = self._hash_api_key(api_key)
            
            # Create API key record
            db_api_key = APIKey(
                user_id=user_id,
                key_hash=key_hash,
                name=key_name,
                is_active=True
            )
            
            self.db.add(db_api_key)
            await self.db.commit()  # CHANGED: await
            await self.db.refresh(db_api_key)  # CHANGED: await
            
            logger.info(f"API key created for user: {user_id}")
            return True, api_key, "API key created successfully"
            
        except Exception as e:
            logger.error(f"Error creating API key: {e}", exc_info=True)
            await self.db.rollback()  # CHANGED: await
            return False, None, "API key creation failed"
    
    async def get_user_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's API keys
        
        Args:
            user_id: User ID
            
        Returns:
            List of API key data
        """
        try:
            # CHANGED to async
            result = await self.db.execute(
                select(APIKey).filter(APIKey.user_id == user_id)
            )
            api_keys = result.scalars().all()
            
            return [
                {
                    "id": str(key.id),
                    "name": key.name,
                    "is_active": key.is_active,
                    "last_used_at": key.last_used_at,
                    "expires_at": key.expires_at,
                    "created_at": key.created_at
                }
                for key in api_keys
            ]
            
        except Exception as e:
            logger.error(f"Error getting API keys: {e}", exc_info=True)
            return []
    
    async def delete_api_key(self, user_id: str, key_id: str) -> Tuple[bool, str]:
        """
        Delete an API key
        
        Args:
            user_id: User ID
            key_id: API key ID
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # CHANGED to async
            result = await self.db.execute(
                select(APIKey).filter(
                    and_(APIKey.id == key_id, APIKey.user_id == user_id)
                )
            )
            api_key = result.scalar_one_or_none()
            
            if not api_key:
                return False, "API key not found"
            
            await self.db.delete(api_key)  # CHANGED: await
            await self.db.commit()  # CHANGED: await
            
            logger.info(f"API key deleted: {key_id}")
            return True, "API key deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting API key: {e}", exc_info=True)
            await self.db.rollback()  # CHANGED: await
            return False, "API key deletion failed"
    
    async def authenticate_api_key(self, api_key: str) -> Tuple[bool, Optional[UserResponse], str]:
        """
        Authenticate using API key
        
        Args:
            api_key: API key string
            
        Returns:
            Tuple of (success, user_data, error_message)
        """
        try:
            key_hash = self._hash_api_key(api_key)
            
            # Find API key - CHANGED to async
            result = await self.db.execute(
                select(APIKey).filter(
                    and_(
                        APIKey.key_hash == key_hash,
                        APIKey.is_active == True
                    )
                )
            )
            db_api_key = result.scalar_one_or_none()
            
            if not db_api_key:
                return False, None, "Invalid API key"
            
            # Check expiration
            if db_api_key.expires_at and datetime.utcnow() > db_api_key.expires_at:
                return False, None, "API key expired"
            
            # Update last used
            db_api_key.last_used_at = datetime.utcnow()
            await self.db.commit()  # CHANGED: await
            
            # Get user - CHANGED to async
            result = await self.db.execute(
                select(User).filter(User.id == db_api_key.user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                return False, None, "User not found or inactive"
            
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                subscription_tier=user.subscription_tier,
                selected_llm_model=user.selected_llm_model,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at or user.created_at  # Fallback to created_at if None
            )
            
            return True, user_response, "API key authentication successful"
            
        except Exception as e:
            logger.error(f"Error authenticating API key: {e}", exc_info=True)
            return False, None, "API key authentication failed"
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()