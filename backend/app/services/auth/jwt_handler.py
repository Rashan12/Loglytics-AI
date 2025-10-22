"""
JWT token handling for Loglytics AI
Provides JWT token generation, verification, and management
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class JWTHandler:
    """Handles JWT token operations"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = 7  # 7 days for refresh tokens
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Data to encode in the token
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow(),
            "jti": self._generate_jti()  # JWT ID for token tracking
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Access token created for user: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise ValueError("Failed to create access token")
    
    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token
        
        Args:
            data: Data to encode in the token
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "jti": self._generate_jti()
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Refresh token created for user: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise ValueError("Failed to create refresh token")
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token to verify
            token_type: Expected token type ("access" or "refresh")
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
                return None
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                logger.warning("Token has expired")
                return None
            
            logger.debug(f"Token verified successfully for user: {payload.get('sub', 'unknown')}")
            return payload
            
        except ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except JWTClaimsError as e:
            logger.warning(f"Token claims error: {e}")
            return None
        except JWTError as e:
            logger.warning(f"JWT error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {e}")
            return None
    
    def create_token_pair(self, user_id: str, email: str, subscription_tier: str = "free") -> Dict[str, str]:
        """
        Create both access and refresh tokens for a user
        
        Args:
            user_id: User ID
            email: User email
            subscription_tier: User subscription tier
            
        Returns:
            Dictionary containing access and refresh tokens
        """
        token_data = {
            "sub": user_id,
            "email": email,
            "subscription_tier": subscription_tier
        }
        
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Create a new access token using a refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token data or None if refresh token is invalid
        """
        payload = self.verify_token(refresh_token, "refresh")
        if not payload:
            return None
        
        # Create new access token with same user data
        token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "subscription_tier": payload.get("subscription_tier", "free")
        }
        
        access_token = self.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    def create_password_reset_token(self, user_id: str, email: str) -> str:
        """
        Create a password reset token
        
        Args:
            user_id: User ID
            email: User email
            
        Returns:
            Password reset token
        """
        data = {
            "sub": user_id,
            "email": email,
            "type": "password_reset",
            "iat": datetime.utcnow()
        }
        
        # Password reset tokens expire in 1 hour
        expire = datetime.utcnow() + timedelta(hours=1)
        data["exp"] = expire
        
        try:
            token = jwt.encode(data, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Password reset token created for user: {user_id}")
            return token
        except Exception as e:
            logger.error(f"Error creating password reset token: {e}")
            raise ValueError("Failed to create password reset token")
    
    def verify_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a password reset token
        
        Args:
            token: Password reset token
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        payload = self.verify_token(token, "password_reset")
        if payload and payload.get("type") == "password_reset":
            return payload
        return None
    
    def create_api_key_token(self, user_id: str, key_name: str) -> str:
        """
        Create a token for API key generation
        
        Args:
            user_id: User ID
            key_name: API key name
            
        Returns:
            API key token
        """
        data = {
            "sub": user_id,
            "key_name": key_name,
            "type": "api_key",
            "iat": datetime.utcnow()
        }
        
        # API key tokens expire in 5 minutes
        expire = datetime.utcnow() + timedelta(minutes=5)
        data["exp"] = expire
        
        try:
            token = jwt.encode(data, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"API key token created for user: {user_id}")
            return token
        except Exception as e:
            logger.error(f"Error creating API key token: {e}")
            raise ValueError("Failed to create API key token")
    
    def verify_api_key_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify an API key token
        
        Args:
            token: API key token
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        payload = self.verify_token(token, "api_key")
        if payload and payload.get("type") == "api_key":
            return payload
        return None
    
    def _generate_jti(self) -> str:
        """
        Generate a unique JWT ID
        
        Returns:
            Unique JWT ID string
        """
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    def extract_token_from_header(self, authorization: str) -> Optional[str]:
        """
        Extract token from Authorization header
        
        Args:
            authorization: Authorization header value
            
        Returns:
            Token string if valid format, None otherwise
        """
        if not authorization:
            return None
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """
        Get token expiry time
        
        Args:
            token: JWT token
            
        Returns:
            Expiry datetime if valid token, None otherwise
        """
        payload = self.verify_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired
        
        Args:
            token: JWT token
            
        Returns:
            True if expired, False otherwise
        """
        expiry = self.get_token_expiry(token)
        if expiry:
            return datetime.utcnow() > expiry
        return True
