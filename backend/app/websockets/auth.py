"""
WebSocket Authentication Middleware
Handles JWT authentication for WebSocket connections with comprehensive security
"""

import logging
import asyncio
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from fastapi import WebSocket, status, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.core.security import verify_token
from app.database import get_db
from app.services.auth.auth_service import AuthService
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)


async def authenticate_websocket(websocket: WebSocket) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Authenticate WebSocket connection using JWT token with comprehensive validation

    Args:
        websocket: FastAPI WebSocket instance

    Returns:
        Tuple of (authenticated: bool, user_id: Optional[str], error: Optional[str])
    """
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")

        if not token:
            # Try to get from headers
            auth_header = websocket.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")

        if not token:
            return False, None, "No authentication token provided"

        # Verify token
        payload = verify_token(token)

        if not payload:
            return False, None, "Invalid or expired token"

        # Extract user ID from payload
        user_id = payload.get("sub")
        if not user_id:
            return False, None, "Invalid token payload"

        # Verify user exists and is active
        try:
            db = next(get_db())
            auth_service = AuthService(db)
            success, user, error = await auth_service.get_current_user(token)
            
            if not success or not user:
                return False, None, "User not found or inactive"
                
            # Check if user is banned or suspended
            if not user.is_active:
                return False, None, "User account is inactive"
                
        except Exception as e:
            logger.error(f"Error verifying user in WebSocket auth: {e}")
            return False, None, "User verification failed"

        logger.debug(f"WebSocket authenticated for user: {user_id}")
        return True, user_id, None

    except JWTError as e:
        logger.error(f"JWT error in WebSocket auth: {e}")
        return False, None, f"JWT verification failed: {str(e)}"
    except Exception as e:
        logger.error(f"Error authenticating WebSocket: {e}")
        return False, None, f"Authentication error: {str(e)}"


async def verify_resource_access(user_id: str, resource_type: str, resource_id: str) -> bool:
    """
    Verify user has access to specific resource (chat, project, etc.)
    
    Args:
        user_id: User ID
        resource_type: Type of resource (chat, project, etc.)
        resource_id: Resource identifier
        
    Returns:
        True if user has access, False otherwise
    """
    try:
        db = next(get_db())
        
        if resource_type == "chat":
            # TODO: Check if user has access to chat
            # This would query the chat_session table
            return True
            
        elif resource_type == "project":
            # TODO: Check if user has access to project
            # This would query the project_share table
            return True
            
        return True  # Default to allow for now
        
    except Exception as e:
        logger.error(f"Error verifying resource access: {e}")
        return False


async def close_websocket_with_error(websocket: WebSocket, error_message: str):
    """
    Close WebSocket connection with error message

    Args:
        websocket: FastAPI WebSocket instance
        error_message: Error message to send
    """
    try:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=error_message)
    except Exception as e:
        logger.error(f"Error closing WebSocket: {e}")


class WebSocketRateLimiter:
    """Advanced rate limiter for WebSocket connections with per-user limits"""

    def __init__(self, max_messages_per_minute: int = 60, max_connections_per_user: int = 5):
        self.max_messages = max_messages_per_minute
        self.max_connections = max_connections_per_user
        self.message_counts = {}  # {connection_id: (timestamp, count)}
        self.user_connections = {}  # {user_id: set of connection_ids}
        self.connection_users = {}  # {connection_id: user_id}

    async def check_rate_limit(self, connection_id: str, user_id: str = None) -> Tuple[bool, Optional[str]]:
        """
        Check if connection has exceeded rate limit

        Args:
            connection_id: WebSocket connection ID
            user_id: User ID for per-user limits

        Returns:
            Tuple of (allowed: bool, error_message: Optional[str])
        """
        try:
            now = datetime.utcnow()

            # Check per-connection rate limit
            if connection_id in self.message_counts:
                last_reset, count = self.message_counts[connection_id]

                # Reset counter if more than a minute has passed
                if now - last_reset > timedelta(minutes=1):
                    self.message_counts[connection_id] = (now, 1)
                else:
                    # Check if limit exceeded
                    if count >= self.max_messages:
                        return False, "Rate limit exceeded. Please slow down."

                    # Increment counter
                    self.message_counts[connection_id] = (last_reset, count + 1)
            else:
                # First message
                self.message_counts[connection_id] = (now, 1)

            # Check per-user connection limit
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                
                if connection_id not in self.user_connections[user_id]:
                    if len(self.user_connections[user_id]) >= self.max_connections:
                        return False, f"Maximum {self.max_connections} connections per user exceeded"
                    
                    self.user_connections[user_id].add(connection_id)
                    self.connection_users[connection_id] = user_id

            return True, None

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True, None  # Allow on error

    def cleanup_connection(self, connection_id: str):
        """Remove connection from rate limiter"""
        if connection_id in self.message_counts:
            del self.message_counts[connection_id]
            
        if connection_id in self.connection_users:
            user_id = self.connection_users[connection_id]
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            del self.connection_users[connection_id]


class MessageSanitizer:
    """Sanitizes WebSocket messages for security"""
    
    @staticmethod
    def sanitize_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize WebSocket message content
        
        Args:
            message: Raw message dictionary
            
        Returns:
            Sanitized message dictionary
        """
        try:
            sanitized = {}
            
            for key, value in message.items():
                if isinstance(value, str):
                    # Remove potentially dangerous characters
                    sanitized[key] = value.replace('<', '&lt;').replace('>', '&gt;')
                elif isinstance(value, dict):
                    sanitized[key] = MessageSanitizer.sanitize_message(value)
                elif isinstance(value, list):
                    sanitized[key] = [
                        MessageSanitizer.sanitize_message(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    sanitized[key] = value
                    
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing message: {e}")
            return message
    
    @staticmethod
    def validate_message_structure(message: Dict[str, Any]) -> bool:
        """
        Validate message structure and required fields
        
        Args:
            message: Message dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            if "type" not in message:
                return False
                
            message_type = message["type"]
            
            # Validate based on message type
            if message_type == "user_message":
                return "content" in message and isinstance(message["content"], str)
            elif message_type == "typing":
                return "is_typing" in message and isinstance(message["is_typing"], bool)
            elif message_type == "ping":
                return True
            elif message_type == "set_filters":
                return "filters" in message and isinstance(message["filters"], dict)
            elif message_type == "mark_read":
                return "notification_id" in message
            else:
                return True  # Allow unknown types for extensibility
                
        except Exception as e:
            logger.error(f"Error validating message structure: {e}")
            return False


class WebSocketSecurity:
    """Comprehensive security measures for WebSocket connections"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.suspicious_connections = {}  # {connection_id: count}
        
    async def check_connection_security(self, websocket: WebSocket, connection_id: str) -> bool:
        """
        Check if connection should be allowed based on security rules
        
        Args:
            websocket: WebSocket instance
            connection_id: Connection identifier
            
        Returns:
            True if connection is safe, False otherwise
        """
        try:
            # Get client IP
            client_ip = websocket.client.host if websocket.client else "unknown"
            
            # Check if IP is blocked
            if client_ip in self.blocked_ips:
                logger.warning(f"Blocked IP attempted WebSocket connection: {client_ip}")
                return False
                
            # Check for suspicious patterns
            if connection_id in self.suspicious_connections:
                if self.suspicious_connections[connection_id] > 10:
                    logger.warning(f"Suspicious connection pattern: {connection_id}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking connection security: {e}")
            return True  # Allow on error
            
    def mark_suspicious(self, connection_id: str):
        """Mark connection as suspicious"""
        if connection_id not in self.suspicious_connections:
            self.suspicious_connections[connection_id] = 0
        self.suspicious_connections[connection_id] += 1


# Global instances
rate_limiter = WebSocketRateLimiter(max_messages_per_minute=60, max_connections_per_user=5)
message_sanitizer = MessageSanitizer()
websocket_security = WebSocketSecurity()
