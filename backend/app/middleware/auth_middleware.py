"""
Enhanced Authentication Middleware
Provides JWT validation, token blacklisting, and session management
"""

import asyncio
import json
import time
from typing import Dict, Optional, Set, List
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
import logging

from app.config import settings
from app.core.security import verify_token
from app.core.redis_client import redis_client
from app.models.user import SubscriptionTier

logger = logging.getLogger(__name__)


class TokenBlacklist:
    """Token blacklist management using Redis"""
    
    def __init__(self):
        self.blacklist_key = "blacklisted_tokens"
        self.session_key_prefix = "user_session:"
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            if await redis_client.ensure_connection():
                logger.info("Token blacklist initialized successfully")
            else:
                logger.warning("Token blacklist initialized without Redis")
        except Exception as e:
            logger.warning(f"Token blacklist initialization failed: {e}. Continuing without Redis.")
    
    async def blacklist_token(self, token: str, user_id: str, expires_at: datetime):
        """Add token to blacklist"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping token blacklisting")
                return
            
            # Store token with expiration
            token_hash = self._hash_token(token)
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            
            if ttl > 0:
                await redis_client.execute_command(
                    "setex",
                    f"{self.blacklist_key}:{token_hash}",
                    ttl,
                    json.dumps({
                        "user_id": user_id,
                        "blacklisted_at": datetime.utcnow().isoformat(),
                        "expires_at": expires_at.isoformat()
                    })
                )
                logger.info(f"Token blacklisted for user {user_id}")
            
        except Exception as e:
            logger.warning(f"Error blacklisting token: {e}")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping token blacklist check")
                return False
            
            token_hash = self._hash_token(token)
            result = await redis_client.execute_command("get", f"{self.blacklist_key}:{token_hash}")
            return result is not None
            
        except Exception as e:
            logger.warning(f"Error checking token blacklist: {e}")
            return False
    
    async def cleanup_expired_tokens(self):
        """Clean up expired blacklisted tokens"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping token cleanup")
                return
            
            # Redis TTL handles expiration automatically
            # This is just for logging purposes
            pattern = f"{self.blacklist_key}:*"
            keys = await redis_client.execute_command("keys", pattern)
            if keys:
                logger.info(f"Cleaned up {len(keys)} blacklisted tokens")
            
        except Exception as e:
            logger.warning(f"Error cleaning up expired tokens: {e}")
    
    def _hash_token(self, token: str) -> str:
        """Hash token for storage"""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()


class SessionManager:
    """Session management with concurrent session limits"""
    
    def __init__(self):
        self.session_key_prefix = "user_session:"
        self.max_concurrent_sessions = {
            SubscriptionTier.FREE: 2,
            SubscriptionTier.PRO: 5,
            SubscriptionTier.ENTERPRISE: 10
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            if await redis_client.ensure_connection():
                logger.info("Session manager initialized successfully")
            else:
                logger.warning("Session manager initialized without Redis")
        except Exception as e:
            logger.warning(f"Session manager initialization failed: {e}. Continuing without Redis.")
    
    async def create_session(
        self, 
        user_id: str, 
        token: str, 
        user_tier: SubscriptionTier,
        ip_address: str,
        user_agent: str
    ) -> bool:
        """Create new session"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping session creation")
                return True  # Allow session creation without Redis
            
            # Check concurrent session limit
            max_sessions = self.max_concurrent_sessions.get(user_tier, 2)
            current_sessions = await self.get_user_sessions(user_id)
            
            if len(current_sessions) >= max_sessions:
                # Remove oldest session
                await self.remove_oldest_session(user_id)
            
            # Create new session
            session_id = f"{user_id}_{int(time.time())}"
            session_data = {
                "user_id": user_id,
                "token": token,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
            
            # Store session with 24 hour expiration
            await redis_client.execute_command(
                "setex",
                f"{self.session_key_prefix}{session_id}",
                86400,  # 24 hours
                json.dumps(session_data)
            )
            
            # Add to user's session list
            await redis_client.execute_command("sadd", f"user_sessions:{user_id}", session_id)
            await redis_client.execute_command("expire", f"user_sessions:{user_id}", 86400)
            
            logger.info(f"Session created for user {user_id}")
            return True
            
        except Exception as e:
            logger.warning(f"Error creating session: {e}")
            return True  # Allow session creation on error
    
    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for user"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, returning empty sessions")
                return []
            
            session_ids = await redis_client.execute_command("smembers", f"user_sessions:{user_id}")
            sessions = []
            
            if session_ids:
                for session_id in session_ids:
                    session_data = await redis_client.execute_command("get", f"{self.session_key_prefix}{session_id}")
                    if session_data:
                        sessions.append(json.loads(session_data))
            
            return sessions
            
        except Exception as e:
            logger.warning(f"Error getting user sessions: {e}")
            return []
    
    async def update_session_activity(self, user_id: str, token: str):
        """Update session last activity"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping session activity update")
                return
            
            session_ids = await redis_client.execute_command("smembers", f"user_sessions:{user_id}")
            
            if session_ids:
                for session_id in session_ids:
                    session_data = await redis_client.execute_command("get", f"{self.session_key_prefix}{session_id}")
                    if session_data:
                        session = json.loads(session_data)
                        if session.get("token") == token:
                            session["last_activity"] = datetime.utcnow().isoformat()
                            await redis_client.execute_command(
                                "setex",
                                f"{self.session_key_prefix}{session_id}",
                                86400,
                                json.dumps(session)
                            )
                            break
            
        except Exception as e:
            logger.warning(f"Error updating session activity: {e}")
    
    async def remove_session(self, user_id: str, token: str):
        """Remove specific session"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping session removal")
                return
            
            session_ids = await redis_client.execute_command("smembers", f"user_sessions:{user_id}")
            
            if session_ids:
                for session_id in session_ids:
                    session_data = await redis_client.execute_command("get", f"{self.session_key_prefix}{session_id}")
                    if session_data:
                        session = json.loads(session_data)
                        if session.get("token") == token:
                            await redis_client.execute_command("delete", f"{self.session_key_prefix}{session_id}")
                            await redis_client.execute_command("srem", f"user_sessions:{user_id}", session_id)
                            logger.info(f"Session removed for user {user_id}")
                            break
            
        except Exception as e:
            logger.warning(f"Error removing session: {e}")
    
    async def remove_oldest_session(self, user_id: str):
        """Remove oldest session for user"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping oldest session removal")
                return
            
            sessions = await self.get_user_sessions(user_id)
            if not sessions:
                return
            
            # Sort by creation time and remove oldest
            sessions.sort(key=lambda x: x.get("created_at", ""))
            oldest_session = sessions[0]
            
            # Find session ID
            session_ids = await redis_client.execute_command("smembers", f"user_sessions:{user_id}")
            if session_ids:
                for session_id in session_ids:
                    session_data = await redis_client.execute_command("get", f"{self.session_key_prefix}{session_id}")
                    if session_data:
                        session = json.loads(session_data)
                        if session.get("created_at") == oldest_session.get("created_at"):
                            await redis_client.execute_command("delete", f"{self.session_key_prefix}{session_id}")
                            await redis_client.execute_command("srem", f"user_sessions:{user_id}", session_id)
                            logger.info(f"Oldest session removed for user {user_id}")
                            break
            
        except Exception as e:
            logger.warning(f"Error removing oldest session: {e}")
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping session cleanup")
                return
            
            # Redis TTL handles expiration automatically
            pattern = f"{self.session_key_prefix}*"
            keys = await redis_client.execute_command("keys", pattern)
            if keys:
                logger.info(f"Cleaned up {len(keys)} expired sessions")
            
        except Exception as e:
            logger.warning(f"Error cleaning up expired sessions: {e}")


class IPAccessControl:
    """IP-based access control"""
    
    def __init__(self):
        self.blocked_ips_key = "blocked_ips"
        self.whitelist_key = "whitelist_ips"
        self.suspicious_ips_key = "suspicious_ips"
        self.max_failed_attempts = 5
        self.block_duration = 3600  # 1 hour
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            if await redis_client.ensure_connection():
                logger.info("IP access control initialized successfully")
            else:
                logger.warning("IP access control initialized without Redis")
        except Exception as e:
            logger.warning(f"IP access control initialization failed: {e}. Continuing without Redis.")
    
    async def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping IP block check")
                return False
            
            result = await redis_client.execute_command("get", f"{self.blocked_ips_key}:{ip}")
            return result is not None
            
        except Exception as e:
            logger.warning(f"Error checking IP block: {e}")
            return False
    
    async def is_ip_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping IP whitelist check")
                return False
            
            result = await redis_client.execute_command("get", f"{self.whitelist_key}:{ip}")
            return result is not None
            
        except Exception as e:
            logger.warning(f"Error checking IP whitelist: {e}")
            return False
    
    async def record_failed_attempt(self, ip: str):
        """Record failed authentication attempt"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping failed attempt recording")
                return
            
            key = f"{self.suspicious_ips_key}:{ip}"
            attempts = await redis_client.execute_command("incr", key)
            await redis_client.execute_command("expire", key, self.block_duration)
            
            if attempts and attempts >= self.max_failed_attempts:
                await self.block_ip(ip)
                logger.warning(f"IP {ip} blocked due to {attempts} failed attempts")
            
        except Exception as e:
            logger.warning(f"Error recording failed attempt: {e}")
    
    async def block_ip(self, ip: str, duration: int = None):
        """Block IP address"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping IP blocking")
                return
            
            duration = duration or self.block_duration
            await redis_client.execute_command("setex", f"{self.blocked_ips_key}:{ip}", duration, "blocked")
            logger.info(f"IP {ip} blocked for {duration} seconds")
            
        except Exception as e:
            logger.warning(f"Error blocking IP: {e}")
    
    async def unblock_ip(self, ip: str):
        """Unblock IP address"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping IP unblocking")
                return
            
            await redis_client.execute_command("delete", f"{self.blocked_ips_key}:{ip}")
            await redis_client.execute_command("delete", f"{self.suspicious_ips_key}:{ip}")
            logger.info(f"IP {ip} unblocked")
            
        except Exception as e:
            logger.warning(f"Error unblocking IP: {e}")


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Enhanced authentication middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.token_blacklist = TokenBlacklist()
        self.session_manager = SessionManager()
        self.ip_access_control = IPAccessControl()
        self.protected_paths = {
            "/api/v1/auth/logout",
            "/api/v1/users",
            "/api/v1/logs",
            "/api/v1/analytics",
            "/api/v1/chat",
            "/api/v1/llm",
            "/api/v1/rag",
            "/api/v1/live-logs",
            "/api/v1/notifications",
            "/api/v1/settings",
            "/api/v1/upload",
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request through authentication middleware"""
        try:
            # Skip authentication for OPTIONS requests (CORS preflight)
            if request.method == "OPTIONS":
                return await call_next(request)
            
            # Skip authentication for certain paths
            if not self._requires_authentication(request.url.path):
                return await call_next(request)
            
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Check IP access control
            if await self.ip_access_control.is_ip_blocked(client_ip):
                logger.warning(f"Blocked IP attempted access: {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "Access denied"}
                )
            
            # Get authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                await self.ip_access_control.record_failed_attempt(client_ip)
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Authorization header required"}
                )
            
            # Extract token
            token = auth_header.split(" ")[1]
            
            # Check if token is blacklisted
            if await self.token_blacklist.is_token_blacklisted(token):
                await self.ip_access_control.record_failed_attempt(client_ip)
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Token has been revoked"}
                )
            
            # Verify token
            payload = verify_token(token)
            if not payload:
                await self.ip_access_control.record_failed_attempt(client_ip)
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid or expired token"}
                )
            
            # Extract user info
            user_id = payload.get("sub")
            if not user_id:
                await self.ip_access_control.record_failed_attempt(client_ip)
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid token payload"}
                )
            
            # Update session activity
            await self.session_manager.update_session_activity(user_id, token)
            
            # Add user info to request state
            request.state.user_id = user_id
            request.state.user_tier = SubscriptionTier(payload.get("tier", "FREE"))
            request.state.token = token
            
            # Process request
            response = await call_next(request)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in authentication middleware: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Authentication error"}
            )
    
    def _requires_authentication(self, path: str) -> bool:
        """Check if path requires authentication"""
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


# Global instances
token_blacklist = TokenBlacklist()
session_manager = SessionManager()
ip_access_control = IPAccessControl()


def create_auth_middleware():
    """Create authentication middleware"""
    return AuthenticationMiddleware
