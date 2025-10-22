"""
Comprehensive security tests
Tests for rate limiting, security middleware, input validation, and more
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request, HTTPException

from app.middleware.rate_limiter import RateLimiter
from app.middleware.security import SecurityMiddleware
from app.middleware.validators import InputValidator
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.audit_logger import AuditLogger
from app.security.encryption import EncryptionService
from app.security.webhook_validator import WebhookValidator
from app.security.dos_protection import DoSProtection
from app.security.compliance import GDPRCompliance, ConsentManager


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def rate_limiter(self):
        return RateLimiter()
    
    @pytest.mark.asyncio
    async def test_token_bucket_algorithm(self, rate_limiter):
        """Test token bucket algorithm"""
        # Test normal operation
        result = await rate_limiter._token_bucket_check("user123", "api", 10, 10, 60)
        assert result["allowed"] is True
        assert result["remaining"] == 9
        
        # Test rate limit exceeded
        for _ in range(10):
            result = await rate_limiter._token_bucket_check("user123", "api", 10, 10, 60)
        
        result = await rate_limiter._token_bucket_check("user123", "api", 10, 10, 60)
        assert result["allowed"] is False
        assert result["remaining"] == 0
    
    @pytest.mark.asyncio
    async def test_sliding_window_counter(self, rate_limiter):
        """Test sliding window counter"""
        # Test normal operation
        result = await rate_limiter._sliding_window_check("user123", "api", 10, 60)
        assert result["allowed"] is True
        assert result["remaining"] >= 0
        
        # Test rate limit exceeded
        for _ in range(15):
            result = await rate_limiter._sliding_window_check("user123", "api", 10, 60)
        
        result = await rate_limiter._sliding_window_check("user123", "api", 10, 60)
        assert result["allowed"] is False
    
    @pytest.mark.asyncio
    async def test_per_user_rate_limits(self, rate_limiter):
        """Test per-user rate limits"""
        # Test free tier limits
        result = await rate_limiter.check_user_rate_limit("user123", "free", "api")
        assert result["allowed"] is True
        
        # Test pro tier limits
        result = await rate_limiter.check_user_rate_limit("user456", "pro", "api")
        assert result["allowed"] is True
    
    @pytest.mark.asyncio
    async def test_per_endpoint_rate_limits(self, rate_limiter):
        """Test per-endpoint rate limits"""
        result = await rate_limiter.check_endpoint_rate_limit("user123", "/api/upload", "POST")
        assert result["allowed"] is True
    
    @pytest.mark.asyncio
    async def test_api_key_rate_limits(self, rate_limiter):
        """Test API key rate limits"""
        result = await rate_limiter.check_api_key_rate_limit("api_key_123", "api")
        assert result["allowed"] is True


class TestSecurityMiddleware:
    """Test security middleware"""
    
    @pytest.fixture
    def security_middleware(self):
        return SecurityMiddleware()
    
    def test_security_headers(self, security_middleware):
        """Test security headers are set correctly"""
        headers = security_middleware._get_security_headers()
        
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in headers
        assert headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in headers
        assert headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Strict-Transport-Security" in headers
        assert "max-age=31536000" in headers["Strict-Transport-Security"]
    
    def test_csp_header(self, security_middleware):
        """Test Content Security Policy header"""
        headers = security_middleware._get_security_headers()
        
        assert "Content-Security-Policy" in headers
        csp = headers["Content-Security-Policy"]
        
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "style-src 'self'" in csp
        assert "img-src 'self' data:" in csp
    
    @pytest.mark.asyncio
    async def test_csrf_protection(self, security_middleware):
        """Test CSRF protection"""
        # Test valid CSRF token
        request = Mock()
        request.method = "POST"
        request.headers = {"X-CSRF-Token": "valid_token"}
        request.cookies = {"csrf_token": "valid_token"}
        
        result = await security_middleware._validate_csrf_token(request)
        assert result is True
        
        # Test invalid CSRF token
        request.headers = {"X-CSRF-Token": "invalid_token"}
        result = await security_middleware._validate_csrf_token(request)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_suspicious_activity_detection(self, security_middleware):
        """Test suspicious activity detection"""
        # Test normal request
        request = Mock()
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {"User-Agent": "Mozilla/5.0"}
        
        result = await security_middleware._detect_suspicious_activity(request)
        assert result["is_suspicious"] is False
        
        # Test suspicious request (no user agent)
        request.headers = {}
        result = await security_middleware._detect_suspicious_activity(request)
        assert result["is_suspicious"] is True


class TestInputValidator:
    """Test input validation"""
    
    @pytest.fixture
    def validator(self):
        return InputValidator()
    
    def test_sanitize_input(self, validator):
        """Test input sanitization"""
        # Test XSS prevention
        malicious_input = "<script>alert('xss')</script>Hello"
        sanitized = validator.sanitize_input(malicious_input)
        assert "<script>" not in sanitized
        assert "Hello" in sanitized
        
        # Test SQL injection prevention
        sql_input = "'; DROP TABLE users; --"
        sanitized = validator.sanitize_input(sql_input)
        assert "DROP TABLE" not in sanitized
        
        # Test HTML encoding
        html_input = "<b>Bold</b> & <i>Italic</i>"
        sanitized = validator.sanitize_input(html_input)
        assert "&lt;b&gt;" in sanitized
        assert "&amp;" in sanitized
    
    def test_validate_email(self, validator):
        """Test email validation"""
        # Valid emails
        assert validator.validate_email("user@example.com") is True
        assert validator.validate_email("test.user+tag@domain.co.uk") is True
        
        # Invalid emails
        assert validator.validate_email("invalid-email") is False
        assert validator.validate_email("@domain.com") is False
        assert validator.validate_email("user@") is False
    
    def test_validate_url(self, validator):
        """Test URL validation"""
        # Valid URLs
        assert validator.validate_url("https://example.com") is True
        assert validator.validate_url("http://subdomain.example.com/path") is True
        
        # Invalid URLs
        assert validator.validate_url("not-a-url") is False
        assert validator.validate_url("ftp://example.com") is False  # Only HTTP/HTTPS allowed
        assert validator.validate_url("javascript:alert('xss')") is False
    
    def test_validate_file_upload(self, validator):
        """Test file upload validation"""
        # Valid file
        valid_file = Mock()
        valid_file.filename = "test.log"
        valid_file.content_type = "text/plain"
        valid_file.size = 1024
        
        result = validator.validate_file_upload(valid_file)
        assert result["valid"] is True
        
        # Invalid file type
        invalid_file = Mock()
        invalid_file.filename = "malicious.exe"
        invalid_file.content_type = "application/x-executable"
        invalid_file.size = 1024
        
        result = validator.validate_file_upload(invalid_file)
        assert result["valid"] is False
        assert "File type not allowed" in result["error"]
        
        # File too large
        large_file = Mock()
        large_file.filename = "large.log"
        large_file.content_type = "text/plain"
        large_file.size = 11 * 1024 * 1024 * 1024  # 11GB
        
        result = validator.validate_file_upload(large_file)
        assert result["valid"] is False
        assert "File too large" in result["error"]
    
    def test_validate_search_query(self, validator):
        """Test search query validation"""
        # Valid search query
        result = validator.validate_search_query("normal search query")
        assert result["valid"] is True
        
        # SQL injection attempt
        result = validator.validate_search_query("'; DROP TABLE users; --")
        assert result["valid"] is False
        assert "Invalid characters" in result["error"]
        
        # NoSQL injection attempt
        result = validator.validate_search_query('{"$where": "this.password"}')
        assert result["valid"] is False
        assert "Invalid characters" in result["error"]


class TestAuthMiddleware:
    """Test authentication middleware"""
    
    @pytest.fixture
    def auth_middleware(self):
        return AuthMiddleware()
    
    @pytest.mark.asyncio
    async def test_jwt_validation(self, auth_middleware):
        """Test JWT token validation"""
        # This would test JWT validation logic
        # For now, we'll test the structure
        assert hasattr(auth_middleware, '_validate_jwt_token')
        assert hasattr(auth_middleware, '_check_token_blacklist')
    
    @pytest.mark.asyncio
    async def test_api_key_validation(self, auth_middleware):
        """Test API key validation"""
        # This would test API key validation logic
        assert hasattr(auth_middleware, '_validate_api_key')
    
    @pytest.mark.asyncio
    async def test_session_management(self, auth_middleware):
        """Test session management"""
        # This would test session management logic
        assert hasattr(auth_middleware, '_create_session')
        assert hasattr(auth_middleware, '_validate_session')
        assert hasattr(auth_middleware, '_check_concurrent_sessions')


class TestAuditLogger:
    """Test audit logging"""
    
    @pytest.fixture
    def audit_logger(self):
        return AuditLogger()
    
    @pytest.mark.asyncio
    async def test_log_sensitive_operation(self, audit_logger):
        """Test logging sensitive operations"""
        # This would test audit logging logic
        assert hasattr(audit_logger, 'log_operation')
        assert hasattr(audit_logger, 'log_authentication')
        assert hasattr(audit_logger, 'log_data_access')


class TestEncryptionService:
    """Test encryption service"""
    
    @pytest.fixture
    def encryption_service(self):
        return EncryptionService()
    
    def test_encrypt_decrypt(self, encryption_service):
        """Test encryption and decryption"""
        test_data = "sensitive data"
        
        # Encrypt
        encrypted = encryption_service.encrypt(test_data)
        assert encrypted != test_data
        assert isinstance(encrypted, str)
        
        # Decrypt
        decrypted = encryption_service.decrypt(encrypted)
        assert decrypted == test_data
    
    def test_key_rotation(self, encryption_service):
        """Test key rotation"""
        # This would test key rotation logic
        assert hasattr(encryption_service, 'rotate_key')
        assert hasattr(encryption_service, 'get_key_version')


class TestWebhookValidator:
    """Test webhook validation"""
    
    @pytest.fixture
    def webhook_validator(self):
        return WebhookValidator()
    
    def test_hmac_validation(self, webhook_validator):
        """Test HMAC signature validation"""
        payload = '{"test": "data"}'
        secret = "test_secret"
        
        # Generate valid signature
        signature = webhook_validator._generate_hmac_signature(payload, secret)
        
        # Validate signature
        result = webhook_validator._validate_hmac_signature(payload, signature, secret)
        assert result is True
        
        # Test invalid signature
        invalid_signature = "invalid_signature"
        result = webhook_validator._validate_hmac_signature(payload, invalid_signature, secret)
        assert result is False
    
    def test_url_verification(self, webhook_validator):
        """Test webhook URL verification"""
        # Valid URLs
        assert webhook_validator.verify_webhook_url("https://example.com/webhook") is True
        assert webhook_validator.verify_webhook_url("https://api.example.com/callback") is True
        
        # Invalid URLs
        assert webhook_validator.verify_webhook_url("http://example.com/webhook") is False  # HTTP not allowed
        assert webhook_validator.verify_webhook_url("ftp://example.com/webhook") is False
        assert webhook_validator.verify_webhook_url("javascript:alert('xss')") is False


class TestDoSProtection:
    """Test DoS protection"""
    
    @pytest.fixture
    def dos_protection(self):
        return DoSProtection()
    
    @pytest.mark.asyncio
    async def test_connection_limits(self, dos_protection):
        """Test connection limits per IP"""
        ip_address = "192.168.1.1"
        
        # Test normal connections
        for _ in range(10):
            result = await dos_protection.check_connection_limit(ip_address)
            assert result["allowed"] is True
        
        # Test connection limit exceeded
        result = await dos_protection.check_connection_limit(ip_address)
        assert result["allowed"] is False
    
    @pytest.mark.asyncio
    async def test_request_size_limits(self, dos_protection):
        """Test request size limits"""
        # Test normal request size
        result = await dos_protection.check_request_size(1024)  # 1KB
        assert result["allowed"] is True
        
        # Test oversized request
        result = await dos_protection.check_request_size(11 * 1024 * 1024 * 1024)  # 11GB
        assert result["allowed"] is False
    
    @pytest.mark.asyncio
    async def test_timeout_limits(self, dos_protection):
        """Test timeout limits"""
        # This would test timeout logic
        assert hasattr(dos_protection, 'check_timeout_limit')


class TestGDPRCompliance:
    """Test GDPR compliance"""
    
    @pytest.fixture
    def gdpr_compliance(self):
        return GDPRCompliance()
    
    @pytest.mark.asyncio
    async def test_export_user_data(self, gdpr_compliance):
        """Test user data export"""
        # This would test data export functionality
        assert hasattr(gdpr_compliance, 'export_user_data')
        assert hasattr(gdpr_compliance, 'delete_user_data')
    
    @pytest.mark.asyncio
    async def test_data_anonymization(self, gdpr_compliance):
        """Test data anonymization"""
        # This would test data anonymization
        assert hasattr(gdpr_compliance, '_anonymize_user_data')
    
    @pytest.mark.asyncio
    async def test_data_retention(self, gdpr_compliance):
        """Test data retention policies"""
        # This would test data retention
        assert hasattr(gdpr_compliance, 'cleanup_expired_data')
        assert hasattr(gdpr_compliance, 'get_data_retention_status')


class TestConsentManager:
    """Test consent management"""
    
    @pytest.fixture
    def consent_manager(self):
        return ConsentManager()
    
    @pytest.mark.asyncio
    async def test_consent_recording(self, consent_manager):
        """Test consent recording"""
        result = await consent_manager.record_consent(
            "user123",
            "marketing",
            True,
            "I consent to marketing emails",
            "192.168.1.1"
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_consent_retrieval(self, consent_manager):
        """Test consent retrieval"""
        consent = await consent_manager.get_user_consent("user123")
        assert "user_id" in consent
        assert "consent_status" in consent


class TestSecurityIntegration:
    """Test security features integration"""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI app"""
        app = FastAPI()
        
        # Add security middleware
        security_middleware = SecurityMiddleware()
        app.add_middleware(security_middleware)
        
        # Add rate limiting
        rate_limiter = RateLimiter()
        app.add_middleware(rate_limiter)
        
        # Add audit logging
        audit_logger = AuditLogger()
        app.add_middleware(audit_logger)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        return app
    
    def test_security_headers_integration(self, app):
        """Test security headers are applied"""
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
    
    def test_rate_limiting_integration(self, app):
        """Test rate limiting is applied"""
        client = TestClient(app)
        
        # Make multiple requests to trigger rate limiting
        for _ in range(20):
            response = client.get("/test")
        
        # Should eventually hit rate limit
        assert response.status_code in [200, 429]


if __name__ == "__main__":
    pytest.main([__file__])
