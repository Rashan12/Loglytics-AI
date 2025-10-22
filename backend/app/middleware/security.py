"""
Comprehensive Security Middleware
Provides CORS, CSRF, XSS protection, and other security measures
"""

import re
import hashlib
import hmac
import secrets
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.allowed_origins = self._get_allowed_origins()
        self.csp_policy = self._get_csp_policy()
        self.blocked_ips: Set[str] = set()
        self.suspicious_ips: Dict[str, int] = {}
        self.max_request_size = 10 * 1024 * 1024 * 1024  # 10GB
        self.request_timeout = 300  # 5 minutes
        
    def _get_allowed_origins(self) -> List[str]:
        """Get allowed CORS origins"""
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "https://app.loglytics.ai",
            "https://staging.loglytics.ai",
            "https://loglytics.ai",
        ] + (settings.ALLOWED_ORIGINS or [])
    
    def _get_csp_policy(self) -> str:
        """Get Content Security Policy"""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: ws:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware"""
        try:
            # Check request size
            if request.headers.get("content-length"):
                content_length = int(request.headers["content-length"])
                if content_length > self.max_request_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"error": "Request too large"}
                    )
            
            # Check for blocked IPs
            client_ip = self._get_client_ip(request)
            if client_ip in self.blocked_ips:
                logger.warning(f"Blocked IP attempted access: {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "Access denied"}
                )
            
            # Check for suspicious activity
            if self._is_suspicious_request(request, client_ip):
                self._handle_suspicious_activity(client_ip)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"error": "Suspicious activity detected"}
                )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response)
            
            # Add CORS headers
            self._add_cors_headers(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in security middleware: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_suspicious_request(self, request: Request, client_ip: str) -> bool:
        """Check for suspicious request patterns"""
        # Check for SQL injection patterns
        if self._contains_sql_injection(request):
            return True
        
        # Check for XSS patterns
        if self._contains_xss_patterns(request):
            return True
        
        # Check for path traversal
        if self._contains_path_traversal(request):
            return True
        
        # Check for suspicious user agent
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan", "zap"]
        if any(agent in user_agent for agent in suspicious_agents):
            return True
        
        # Check for too many requests from same IP
        if client_ip in self.suspicious_ips:
            self.suspicious_ips[client_ip] += 1
            if self.suspicious_ips[client_ip] > 100:  # 100 requests threshold
                return True
        else:
            self.suspicious_ips[client_ip] = 1
        
        return False
    
    def _contains_sql_injection(self, request: Request) -> bool:
        """Check for SQL injection patterns"""
        sql_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"delete\s+from",
            r"insert\s+into",
            r"update\s+set",
            r"exec\s*\(",
            r"execute\s*\(",
            r"sp_executesql",
            r"xp_cmdshell",
            r"';.*--",
            r"'.*or.*1=1",
            r"'.*or.*'1'='1",
            r"'.*and.*1=1",
            r"'.*and.*'1'='1",
        ]
        
        # Check URL parameters
        for param in request.query_params.values():
            if self._check_patterns(param, sql_patterns):
                return True
        
        # Check form data (if available)
        if hasattr(request, "_form") and request._form:
            for value in request._form.values():
                if self._check_patterns(str(value), sql_patterns):
                    return True
        
        return False
    
    def _contains_xss_patterns(self, request: Request) -> bool:
        """Check for XSS patterns"""
        xss_patterns = [
            r"<script[^>]*>.*</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"<style[^>]*>",
            r"expression\s*\(",
            r"vbscript:",
            r"data:text/html",
        ]
        
        # Check URL parameters
        for param in request.query_params.values():
            if self._check_patterns(param, xss_patterns):
                return True
        
        return False
    
    def _contains_path_traversal(self, request: Request) -> bool:
        """Check for path traversal patterns"""
        path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"\.\.%2f",
            r"\.\.%5c",
        ]
        
        path = request.url.path
        if self._check_patterns(path, path_traversal_patterns):
            return True
        
        return False
    
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the patterns"""
        try:
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        except Exception as e:
            logger.error(f"Error checking patterns: {e}")
        return False
    
    def _handle_suspicious_activity(self, client_ip: str):
        """Handle suspicious activity"""
        logger.warning(f"Suspicious activity detected from IP: {client_ip}")
        
        # Increment suspicious count
        if client_ip in self.suspicious_ips:
            self.suspicious_ips[client_ip] += 1
        else:
            self.suspicious_ips[client_ip] = 1
        
        # Block IP if too many suspicious activities
        if self.suspicious_ips[client_ip] > 50:
            self.blocked_ips.add(client_ip)
            logger.warning(f"IP {client_ip} has been blocked due to suspicious activity")
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = self.csp_policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    
    def _add_cors_headers(self, request: Request, response: Response):
        """Add CORS headers to response"""
        origin = request.headers.get("origin")
        
        if origin and origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Max-Age"] = "86400"


class CSRFProtection:
    """CSRF protection middleware"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY.encode()
        self.token_cache: Dict[str, str] = {}
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        token = secrets.token_urlsafe(32)
        self.token_cache[session_id] = token
        return token
    
    def verify_csrf_token(self, session_id: str, token: str) -> bool:
        """Verify CSRF token"""
        if session_id not in self.token_cache:
            return False
        
        expected_token = self.token_cache[session_id]
        return secrets.compare_digest(token, expected_token)
    
    def invalidate_csrf_token(self, session_id: str):
        """Invalidate CSRF token"""
        if session_id in self.token_cache:
            del self.token_cache[session_id]


class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not input_str:
            return ""
        
        # Remove null bytes
        sanitized = input_str.replace("\x00", "")
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)
        
        # Limit length
        sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename"""
        if not filename:
            return "unnamed"
        
        # Remove path components
        filename = filename.split("/")[-1].split("\\")[-1]
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
        
        # Remove leading dots and spaces
        filename = filename.lstrip(". ")
        
        # Limit length
        filename = filename[:255]
        
        return filename or "unnamed"
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """Sanitize URL"""
        if not url:
            return ""
        
        # Basic URL validation
        if not re.match(r"^https?://", url):
            return ""
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>"\'`]', "", url)
        
        return sanitized[:2048]  # Limit length
    
    @staticmethod
    def sanitize_json(data: dict) -> dict:
        """Sanitize JSON data recursively"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            clean_key = InputSanitizer.sanitize_string(str(key), 100)
            
            # Sanitize value
            if isinstance(value, str):
                clean_value = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                clean_value = InputSanitizer.sanitize_json(value)
            elif isinstance(value, list):
                clean_value = [
                    InputSanitizer.sanitize_string(str(item)) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                clean_value = value
            
            sanitized[clean_key] = clean_value
        
        return sanitized


class RequestValidator:
    """Request validation utilities"""
    
    @staticmethod
    def validate_file_upload(file_info: dict) -> tuple[bool, str]:
        """Validate file upload"""
        # Check file size
        max_size = 100 * 1024 * 1024  # 100MB
        if file_info.get("size", 0) > max_size:
            return False, "File too large"
        
        # Check file type
        allowed_types = {
            ".log", ".txt", ".json", ".csv", ".xml", ".yaml", ".yml",
            ".gz", ".zip", ".tar", ".tar.gz"
        }
        
        filename = file_info.get("filename", "").lower()
        if not any(filename.endswith(ext) for ext in allowed_types):
            return False, "File type not allowed"
        
        # Check filename
        if len(filename) > 255:
            return False, "Filename too long"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        
        return True, ""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format"""
        if not api_key:
            return False
        
        # Check length and format
        if len(api_key) < 32 or len(api_key) > 64:
            return False
        
        # Check if it contains only valid characters
        if not re.match(r"^[a-zA-Z0-9_-]+$", api_key):
            return False
        
        return True


# Global instances
csrf_protection = CSRFProtection()
input_sanitizer = InputSanitizer()
request_validator = RequestValidator()


def create_security_middleware():
    """Create security middleware"""
    return SecurityMiddleware
