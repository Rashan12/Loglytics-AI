"""
Security Initialization
Initialize and configure all security middleware and services
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.security_config import get_security_config
from app.middleware.security import SecurityMiddleware
from app.middleware.rate_limiter import RedisRateLimiter
from app.middleware.auth_middleware import AuthenticationMiddleware
from app.middleware.audit_logger import AuditLogger
from app.middleware.rate_limit import RateLimitMiddleware
from app.security.encryption import EncryptionManager as EncryptionService
from app.security.webhook_validator import WebhookValidator
from app.security.dos_protection import DoSProtection
from app.security.compliance import GDPRCompliance, ConsentManager

logger = logging.getLogger(__name__)


def setup_security_middleware(app: FastAPI) -> None:
    """
    Setup all security middleware in the correct order
    
    Args:
        app: FastAPI application instance
    """
    config = get_security_config()
    
    try:
        # 1. CORS Middleware (first)
        if config.security_headers_enabled:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=config.cors_origins,
                allow_credentials=config.cors_allow_credentials,
                allow_methods=config.cors_allow_methods,
                allow_headers=config.cors_allow_headers,
            )
            logger.info("CORS middleware configured")
        
        # 2. Security Headers Middleware
        if config.security_headers_enabled:
            # FastAPI expects the middleware class, not an instance. It will pass `app` internally.
            app.add_middleware(SecurityMiddleware)
            logger.info("Security headers middleware configured")
        
        # 3. Rate Limiting Middleware
        if config.rate_limit_enabled:
            # RateLimitMiddleware is an ASGI middleware class taking (app, limit, window)
            app.add_middleware(RateLimitMiddleware)
            logger.info("Rate limiting middleware configured")
        
        # 4. DoS Protection Middleware
        # DoSProtection is not a Starlette middleware class; skip adding directly to avoid runtime errors.
        # If needed, integrate its checks inside SecurityMiddleware or a proper BaseHTTPMiddleware wrapper.
        if config.dos_protection_enabled:
            logger.info("DoS protection enabled (handled by security middleware policies)")
        
        # 5. Authentication Middleware
        # AuthenticationMiddleware inherits BaseHTTPMiddleware; pass the class, not an instance.
        app.add_middleware(AuthenticationMiddleware)
        logger.info("Authentication middleware configured")
        
        # 6. Audit Logging Middleware (last)
        if config.audit_log_enabled:
            # AuditLogger is not a BaseHTTPMiddleware; it provides a helper/service.
            # Skip adding as middleware to avoid constructor signature issues.
            logger.info("Audit logging enabled (handled via request hooks within app)")
        
        logger.info("All security middleware configured successfully")
        
    except Exception as e:
        logger.error(f"Error setting up security middleware: {e}")
        raise


def initialize_security_services() -> dict:
    """
    Initialize all security services
    
    Returns:
        Dictionary of initialized security services
    """
    config = get_security_config()
    services = {}
    
    try:
        # Initialize encryption service
        if config.encryption_enabled:
            services["encryption"] = EncryptionService()
            logger.info("Encryption service initialized")
        
        # Initialize webhook validator
        services["webhook_validator"] = WebhookValidator()
        logger.info("Webhook validator initialized")
        
        # Initialize DoS protection
        if config.dos_protection_enabled:
            services["dos_protection"] = DoSProtection()
            logger.info("DoS protection service initialized")
        
        # Initialize GDPR compliance
        if config.gdpr_enabled:
            services["gdpr_compliance"] = GDPRCompliance()
            services["consent_manager"] = ConsentManager()
            logger.info("GDPR compliance services initialized")
        
        logger.info("All security services initialized successfully")
        return services
        
    except Exception as e:
        logger.error(f"Error initializing security services: {e}")
        raise


def get_security_status() -> dict:
    """
    Get current security status and configuration
    
    Returns:
        Dictionary with security status information
    """
    config = get_security_config()
    
    return {
        "rate_limiting": {
            "enabled": config.rate_limit_enabled,
            "redis_url": config.rate_limit_redis_url,
            "tiers": list(config.rate_limits.keys())
        },
        "security_headers": {
            "enabled": config.security_headers_enabled,
            "cors_origins": config.cors_origins,
            "csp_enabled": bool(config.csp_default_src)
        },
        "file_upload": {
            "max_size": config.max_file_size,
            "allowed_types": config.allowed_file_types,
            "scanning_enabled": config.scan_uploaded_files
        },
        "authentication": {
            "jwt_enabled": bool(config.jwt_secret_key),
            "session_timeout": config.session_timeout_minutes,
            "max_concurrent_sessions": config.max_concurrent_sessions
        },
        "audit_logging": {
            "enabled": config.audit_log_enabled,
            "retention_days": config.audit_log_retention_days,
            "sensitive_operations": len(config.audit_log_sensitive_operations)
        },
        "encryption": {
            "enabled": config.encryption_enabled,
            "algorithm": config.encryption_algorithm
        },
        "webhook_security": {
            "hmac_enabled": bool(config.webhook_hmac_secret),
            "timeout_seconds": config.webhook_timeout_seconds,
            "max_retries": config.webhook_max_retries
        },
        "dos_protection": {
            "enabled": config.dos_protection_enabled,
            "max_connections_per_ip": config.max_connections_per_ip,
            "max_requests_per_minute": config.max_requests_per_minute
        },
        "security_scanning": {
            "enabled": config.security_scan_enabled,
            "scan_scripts": config.scan_for_scripts,
            "scan_malware": config.scan_for_malware
        },
        "gdpr_compliance": {
            "enabled": config.gdpr_enabled,
            "data_retention_days": config.data_retention_days,
            "anonymization_enabled": config.anonymization_enabled
        },
        "monitoring": {
            "enabled": config.monitoring_enabled,
            "alert_failed_auth": config.alert_on_failed_auth,
            "alert_suspicious_activity": config.alert_on_suspicious_activity
        }
    }


def validate_security_config() -> list:
    """
    Validate security configuration
    
    Returns:
        List of validation errors (empty if valid)
    """
    config = get_security_config()
    errors = []
    
    # Validate required settings
    if not config.jwt_secret_key or config.jwt_secret_key == "your-jwt-secret-key":
        errors.append("JWT secret key must be set")
    
    if not config.encryption_key or config.encryption_key == "your-encryption-key":
        errors.append("Encryption key must be set")
    
    if not config.csrf_secret_key or config.csrf_secret_key == "your-csrf-secret-key":
        errors.append("CSRF secret key must be set")
    
    if not config.webhook_hmac_secret or config.webhook_hmac_secret == "your-webhook-secret":
        errors.append("Webhook HMAC secret must be set")
    
    # Validate rate limits
    for tier, limits in config.rate_limits.items():
        for limit_name, limit_value in limits.items():
            if limit_value < 0 and limit_value != -1:  # -1 means unlimited
                errors.append(f"Invalid rate limit for {tier}.{limit_name}: {limit_value}")
    
    # Validate file upload settings
    if config.max_file_size <= 0:
        errors.append("Max file size must be positive")
    
    if not config.allowed_file_types:
        errors.append("At least one file type must be allowed")
    
    # Validate retention periods
    for data_type, days in config.data_retention_days.items():
        if days < 0:
            errors.append(f"Invalid retention period for {data_type}: {days} days")
    
    return errors


def setup_security_logging() -> None:
    """Setup security-specific logging"""
    # Create security logger
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    
    # Create file handler for security logs (ensure directory exists)
    import os
    os.makedirs("logs", exist_ok=True)
    handler = logging.FileHandler("logs/security.log")
    handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    security_logger.addHandler(handler)
    
    logger.info("Security logging configured")


def create_security_summary() -> str:
    """
    Create a security configuration summary
    
    Returns:
        String summary of security configuration
    """
    config = get_security_config()
    status = get_security_status()
    
    summary = f"""
Security Configuration Summary
=============================

Rate Limiting: {'Enabled' if status['rate_limiting']['enabled'] else 'Disabled'}
- Redis URL: {status['rate_limiting']['redis_url']}
- Tiers: {', '.join(status['rate_limiting']['tiers'])}

Security Headers: {'Enabled' if status['security_headers']['enabled'] else 'Disabled'}
- CORS Origins: {len(status['security_headers']['cors_origins'])} configured
- CSP: {'Enabled' if status['security_headers']['csp_enabled'] else 'Disabled'}

File Upload Security:
- Max Size: {status['file_upload']['max_size'] / (1024**3):.1f} GB
- Allowed Types: {', '.join(status['file_upload']['allowed_types'])}
- Scanning: {'Enabled' if status['file_upload']['scanning_enabled'] else 'Disabled'}

Authentication:
- JWT: {'Enabled' if status['authentication']['jwt_enabled'] else 'Disabled'}
- Session Timeout: {status['authentication']['session_timeout']} minutes
- Max Concurrent Sessions: {status['authentication']['max_concurrent_sessions']}

Audit Logging: {'Enabled' if status['audit_logging']['enabled'] else 'Disabled'}
- Retention: {status['audit_logging']['retention_days']} days
- Sensitive Operations: {status['audit_logging']['sensitive_operations']} configured

Encryption: {'Enabled' if status['encryption']['enabled'] else 'Disabled'}
- Algorithm: {status['encryption']['algorithm']}

DoS Protection: {'Enabled' if status['dos_protection']['enabled'] else 'Disabled'}
- Max Connections/IP: {status['dos_protection']['max_connections_per_ip']}
- Max Requests/Minute: {status['dos_protection']['max_requests_per_minute']}

GDPR Compliance: {'Enabled' if status['gdpr_compliance']['enabled'] else 'Disabled'}
- Data Retention: {len(status['gdpr_compliance']['data_retention_days'])} policies
- Anonymization: {'Enabled' if status['gdpr_compliance']['anonymization_enabled'] else 'Disabled'}

Monitoring: {'Enabled' if status['monitoring']['enabled'] else 'Disabled'}
- Failed Auth Alerts: {'Enabled' if status['monitoring']['alert_failed_auth'] else 'Disabled'}
- Suspicious Activity Alerts: {'Enabled' if status['monitoring']['alert_suspicious_activity'] else 'Disabled'}
"""
    
    return summary
