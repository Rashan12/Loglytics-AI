"""
Rate limiting middleware for Loglytics AI
Provides rate limiting functionality for API endpoints
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Optional
import time
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter implementation using sliding window algorithm"""
    
    def __init__(self):
        # Store request timestamps for each IP
        self.requests: Dict[str, deque] = defaultdict(deque)
        # Store request counts for each IP
        self.counts: Dict[str, int] = defaultdict(int)
        # Cleanup interval (in seconds)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def is_allowed(
        self, 
        ip: str, 
        limit: int = 100, 
        window: int = 3600,
        burst_limit: int = 10,
        burst_window: int = 60
    ) -> tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed based on rate limits
        
        Args:
            ip: Client IP address
            limit: Maximum requests per window (default: 100/hour)
            window: Time window in seconds (default: 3600 = 1 hour)
            burst_limit: Maximum requests per burst window (default: 10/minute)
            burst_window: Burst window in seconds (default: 60 = 1 minute)
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = time.time()
        
        # Cleanup old entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(now)
            self.last_cleanup = now
        
        # Get request history for this IP
        request_times = self.requests[ip]
        
        # Remove requests outside the main window
        cutoff_time = now - window
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Remove requests outside the burst window
        burst_cutoff_time = now - burst_window
        burst_requests = [t for t in request_times if t >= burst_cutoff_time]
        
        # Check burst limit
        if len(burst_requests) >= burst_limit:
            return False, {
                "limit": burst_limit,
                "remaining": 0,
                "reset_time": int(burst_cutoff_time + burst_window),
                "retry_after": int(burst_window - (now - burst_cutoff_time))
            }
        
        # Check main limit
        if len(request_times) >= limit:
            return False, {
                "limit": limit,
                "remaining": 0,
                "reset_time": int(cutoff_time + window),
                "retry_after": int(window - (now - cutoff_time))
            }
        
        # Add current request
        request_times.append(now)
        self.counts[ip] = len(request_times)
        
        return True, {
            "limit": limit,
            "remaining": limit - len(request_times),
            "reset_time": int(now + window),
            "retry_after": None
        }
    
    def _cleanup_old_entries(self, now: float):
        """Clean up old entries to prevent memory leaks"""
        cutoff_time = now - 3600  # Remove entries older than 1 hour
        
        for ip in list(self.requests.keys()):
            request_times = self.requests[ip]
            
            # Remove old requests
            while request_times and request_times[0] < cutoff_time:
                request_times.popleft()
            
            # Remove IP if no recent requests
            if not request_times:
                del self.requests[ip]
                del self.counts[ip]
    
    def get_rate_limit_info(self, ip: str) -> Dict[str, int]:
        """Get current rate limit information for an IP"""
        now = time.time()
        request_times = self.requests[ip]
        
        # Count requests in last hour
        cutoff_time = now - 3600
        recent_requests = [t for t in request_times if t >= cutoff_time]
        
        return {
            "limit": 100,
            "remaining": max(0, 100 - len(recent_requests)),
            "reset_time": int(cutoff_time + 3600),
            "retry_after": None
        }

# Global rate limiter instance
rate_limiter = RateLimiter()

class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, limit: int = 100, window: int = 3600):
        self.app = app
        self.limit = limit
        self.window = window
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        is_allowed, rate_info = rate_limiter.is_allowed(
            client_ip, 
            limit=self.limit, 
            window=self.window
        )
        
        if not is_allowed:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "rate_limit": rate_info
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

def create_rate_limit_middleware(limit: int = 100, window: int = 3600):
    """Create rate limit middleware with custom settings"""
    return lambda app: RateLimitMiddleware(app, limit, window)

# Specific rate limits for different endpoint types
AUTH_RATE_LIMITS = {
    "login": {"limit": 5, "window": 300},  # 5 requests per 5 minutes
    "register": {"limit": 3, "window": 3600},  # 3 requests per hour
    "password_reset": {"limit": 3, "window": 3600},  # 3 requests per hour
    "refresh": {"limit": 10, "window": 300},  # 10 requests per 5 minutes
}

API_RATE_LIMITS = {
    "default": {"limit": 1000, "window": 3600},  # 1000 requests per hour
    "upload": {"limit": 50, "window": 3600},  # 50 uploads per hour
    "analysis": {"limit": 200, "window": 3600},  # 200 analyses per hour
    "chat": {"limit": 100, "window": 3600},  # 100 chat requests per hour
}

def get_rate_limit_for_endpoint(endpoint: str) -> Dict[str, int]:
    """Get rate limit settings for specific endpoint"""
    if endpoint.startswith("/api/v1/auth/login"):
        return AUTH_RATE_LIMITS["login"]
    elif endpoint.startswith("/api/v1/auth/register"):
        return AUTH_RATE_LIMITS["register"]
    elif endpoint.startswith("/api/v1/auth/password-reset"):
        return AUTH_RATE_LIMITS["password_reset"]
    elif endpoint.startswith("/api/v1/auth/refresh"):
        return AUTH_RATE_LIMITS["refresh"]
    elif endpoint.startswith("/api/v1/upload"):
        return API_RATE_LIMITS["upload"]
    elif endpoint.startswith("/api/v1/analysis"):
        return API_RATE_LIMITS["analysis"]
    elif endpoint.startswith("/api/v1/chat"):
        return API_RATE_LIMITS["chat"]
    else:
        return API_RATE_LIMITS["default"]
