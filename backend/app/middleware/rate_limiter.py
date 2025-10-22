"""
Enhanced Redis-based Rate Limiter
Provides distributed rate limiting with subscription tier support
"""

import asyncio
import json
import time
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.core.redis_client import redis_client
from app.models.user import SubscriptionTier

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    """Redis-based distributed rate limiter with subscription tier support"""
    
    def __init__(self):
        self.rate_limits = self._get_rate_limits()
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            if await redis_client.ensure_connection():
                logger.info("Redis rate limiter initialized successfully")
            else:
                logger.warning("Redis rate limiter initialized without Redis")
        except Exception as e:
            logger.warning(f"Redis rate limiter initialization failed: {e}. Continuing without Redis.")
    
    def _get_rate_limits(self) -> Dict[str, Dict[str, int]]:
        """Get rate limits by subscription tier"""
        return {
            SubscriptionTier.FREE: {
                "auth_requests_per_minute": 5,
                "api_requests_per_hour": 100,
                "file_uploads_per_day": 10,
                "chat_messages_per_hour": 50,
                "llm_tokens_per_day": 10000,
                "websocket_connections": 2,
                "burst_limit": 10,
                "burst_window": 60
            },
            SubscriptionTier.PRO: {
                "auth_requests_per_minute": 10,
                "api_requests_per_hour": 1000,
                "file_uploads_per_day": -1,  # Unlimited
                "chat_messages_per_hour": -1,  # Unlimited
                "llm_tokens_per_day": 1000000,
                "websocket_connections": 10,
                "burst_limit": 50,
                "burst_window": 60
            },
            SubscriptionTier.ENTERPRISE: {
                "auth_requests_per_minute": 50,
                "api_requests_per_hour": 10000,
                "file_uploads_per_day": -1,  # Unlimited
                "chat_messages_per_hour": -1,  # Unlimited
                "llm_tokens_per_day": -1,  # Unlimited
                "websocket_connections": 50,
                "burst_limit": 200,
                "burst_window": 60
            }
        }
    
    async def check_rate_limit(
        self,
        identifier: str,
        endpoint_type: str,
        user_tier: SubscriptionTier = SubscriptionTier.FREE,
        user_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limits
        
        Args:
            identifier: IP address or user ID
            endpoint_type: Type of endpoint (auth, api, upload, chat, llm)
            user_tier: User subscription tier
            user_id: User ID for user-specific limits
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        if not await redis_client.ensure_connection():
            logger.warning("Redis unavailable, allowing request (rate limiting disabled)")
            return True, {
                "limit": -1,
                "remaining": -1,
                "reset_time": int(time.time()) + 3600,
                "retry_after": None
            }
        
        try:
            limits = self.rate_limits.get(user_tier, self.rate_limits[SubscriptionTier.FREE])
            now = int(time.time())
            
            # Get appropriate limit based on endpoint type
            if endpoint_type == "auth":
                limit = limits["auth_requests_per_minute"]
                window = 60  # 1 minute
                key_prefix = f"rate_limit:auth:{identifier}"
            elif endpoint_type == "api":
                limit = limits["api_requests_per_hour"]
                window = 3600  # 1 hour
                key_prefix = f"rate_limit:api:{identifier}"
            elif endpoint_type == "upload":
                limit = limits["file_uploads_per_day"]
                window = 86400  # 24 hours
                key_prefix = f"rate_limit:upload:{identifier}"
            elif endpoint_type == "chat":
                limit = limits["chat_messages_per_hour"]
                window = 3600  # 1 hour
                key_prefix = f"rate_limit:chat:{identifier}"
            elif endpoint_type == "llm":
                limit = limits["llm_tokens_per_day"]
                window = 86400  # 24 hours
                key_prefix = f"rate_limit:llm:{identifier}"
            else:
                limit = limits["api_requests_per_hour"]
                window = 3600
                key_prefix = f"rate_limit:default:{identifier}"
            
            # Check if unlimited
            if limit == -1:
                return True, {
                    "limit": -1,
                    "remaining": -1,
                    "reset_time": now + window,
                    "retry_after": None
                }
            
            # Use sliding window counter
            is_allowed, rate_info = await self._sliding_window_check(
                key_prefix, limit, window, now
            )
            
            # Check burst limit
            if is_allowed:
                burst_limit = limits["burst_limit"]
                burst_window = limits["burst_window"]
                burst_key = f"{key_prefix}:burst"
                
                burst_allowed, burst_info = await self._sliding_window_check(
                    burst_key, burst_limit, burst_window, now
                )
                
                if not burst_allowed:
                    is_allowed = False
                    rate_info = burst_info
            
            return is_allowed, rate_info
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Allow request on error to prevent service disruption
            return True, {
                "limit": 1000,
                "remaining": 999,
                "reset_time": int(time.time()) + 3600,
                "retry_after": None
            }
    
    async def _sliding_window_check(
        self, key: str, limit: int, window: int, now: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using sliding window algorithm"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, allowing request")
                return True, {
                    "limit": limit,
                    "remaining": limit - 1,
                    "reset_time": now + window,
                    "retry_after": None
                }
            
            # Remove expired entries
            await redis_client.execute_command("zremrangebyscore", key, 0, now - window)
            
            # Count current requests
            current_count = await redis_client.execute_command("zcard", key)
            
            # Add current request
            await redis_client.execute_command("zadd", key, {str(now): now})
            
            # Set expiration
            await redis_client.execute_command("expire", key, window)
            
            if current_count and current_count >= limit:
                # Get oldest request time for retry calculation
                oldest_requests = await redis_client.execute_command("zrange", key, 0, 0, withscores=True)
                oldest_time = int(oldest_requests[0][1]) if oldest_requests else now
                retry_after = window - (now - oldest_time)
                
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset_time": now + window,
                    "retry_after": max(0, retry_after)
                }
            
            return True, {
                "limit": limit,
                "remaining": limit - (current_count or 0) - 1,
                "reset_time": now + window,
                "retry_after": None
            }
            
        except Exception as e:
            logger.warning(f"Error in sliding window check: {e}")
            return True, {
                "limit": limit,
                "remaining": limit - 1,
                "reset_time": now + window,
                "retry_after": None
            }
    
    async def get_rate_limit_info(
        self, identifier: str, endpoint_type: str, user_tier: SubscriptionTier
    ) -> Dict[str, Any]:
        """Get current rate limit information"""
        is_allowed, rate_info = await self.check_rate_limit(
            identifier, endpoint_type, user_tier
        )
        return rate_info
    
    async def reset_rate_limit(self, identifier: str, endpoint_type: str):
        """Reset rate limit for identifier"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping rate limit reset")
                return
            
            pattern = f"rate_limit:{endpoint_type}:{identifier}*"
            keys = await redis_client.execute_command("keys", pattern)
            if keys:
                await redis_client.execute_command("delete", *keys)
                logger.info(f"Reset rate limit for {identifier} on {endpoint_type}")
        except Exception as e:
            logger.warning(f"Error resetting rate limit: {e}")
    
    async def cleanup_expired_limits(self):
        """Clean up expired rate limit entries"""
        try:
            if not await redis_client.ensure_connection():
                logger.warning("Redis unavailable, skipping rate limit cleanup")
                return
            
            now = int(time.time())
            pattern = "rate_limit:*"
            keys = await redis_client.execute_command("keys", pattern)
            
            if keys:
                for key in keys:
                    # Check if key has expired
                    ttl = await redis_client.execute_command("ttl", key)
                    if ttl == -1:  # No expiration set
                        await redis_client.execute_command("expire", key, 3600)  # Set 1 hour expiration
                    elif ttl == -2:  # Key doesn't exist
                        continue
                    
        except Exception as e:
            logger.warning(f"Error cleaning up expired limits: {e}")


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app):
        self.app = app
        self.rate_limiter = RedisRateLimiter()
        self.endpoint_mapping = {
            "/api/v1/auth": "auth",
            "/api/v1/upload": "upload",
            "/api/v1/chat": "chat",
            "/api/v1/llm": "llm",
            "/api/v1/analytics": "api",
            "/api/v1/logs": "api",
            "/api/v1/live-logs": "api",
            "/api/v1/notifications": "api",
            "/api/v1/users": "api",
            "/api/v1/settings": "api",
            "/api/v1/rag": "api",
        }
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Determine endpoint type
            endpoint_type = self._get_endpoint_type(request.url.path)
            
            # Get user tier (default to FREE)
            user_tier = SubscriptionTier.FREE
            user_id = None
            
            # Try to get user info from request headers or JWT
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # Extract user info from JWT (simplified)
                # In production, you'd decode the JWT to get user tier
                user_id = "user_from_jwt"  # This would be extracted from JWT
            
            # Check rate limit
            is_allowed, rate_info = await self.rate_limiter.check_rate_limit(
                client_ip, endpoint_type, user_tier, user_id
            )
            
            if not is_allowed:
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": {
                            "code": 429,
                            "message": "Rate limit exceeded",
                            "details": f"Too many {endpoint_type} requests. Please try again later.",
                            "rate_limit": rate_info
                        }
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": str(rate_info["remaining"]),
                        "X-RateLimit-Reset": str(rate_info["reset_time"]),
                        "Retry-After": str(rate_info.get("retry_after", 0))
                    }
                )
                await response(scope, receive, send)
                return
            
            # Add rate limit headers to response
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    headers[b"x-ratelimit-limit"] = str(rate_info["limit"]).encode()
                    headers[b"x-ratelimit-remaining"] = str(rate_info["remaining"]).encode()
                    headers[b"x-ratelimit-reset"] = str(rate_info["reset_time"]).encode()
                    message["headers"] = list(headers.items())
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
            
        except Exception as e:
            logger.error(f"Error in rate limit middleware: {e}")
            # Allow request on error
            await self.app(scope, receive, send)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type from path"""
        for prefix, endpoint_type in self.endpoint_mapping.items():
            if path.startswith(prefix):
                return endpoint_type
        return "api"


class TokenBucketRateLimiter:
    """Token bucket rate limiter for burst handling"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from bucket"""
        now = time.time()
        
        # Refill tokens based on time passed
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
        
        # Check if enough tokens available
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


# Global rate limiter instance
redis_rate_limiter = RedisRateLimiter()


def create_rate_limit_middleware():
    """Create rate limit middleware"""
    return RateLimitMiddleware


# Rate limit decorator for specific endpoints
def rate_limit(endpoint_type: str, user_tier: SubscriptionTier = SubscriptionTier.FREE):
    """Decorator for rate limiting specific endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request and user info
            request = None
            user_id = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                return await func(*args, **kwargs)
            
            client_ip = request.client.host if request.client else "unknown"
            
            # Check rate limit
            is_allowed, rate_info = await redis_rate_limiter.check_rate_limit(
                client_ip, endpoint_type, user_tier, user_id
            )
            
            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": str(rate_info["remaining"]),
                        "X-RateLimit-Reset": str(rate_info["reset_time"]),
                        "Retry-After": str(rate_info.get("retry_after", 0))
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Alias for backward compatibility
RateLimiter = RedisRateLimiter
