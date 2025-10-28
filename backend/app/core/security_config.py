"""
Security Configuration
Centralized security configuration and settings
"""

import os
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings


class SecurityConfig(BaseSettings):
    """Security configuration settings"""
    
    model_config = {
        "extra": "allow",
        "env_file": ".env",
        "case_sensitive": False
    }
    
    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_redis_url: str = "redis://localhost:6379/1"
    rate_limit_redis_password: Optional[str] = None
    
    # Rate Limit Tiers
    rate_limits: Dict[str, Dict[str, int]] = {
        "free": {
            "auth_per_minute": 5,
            "api_per_hour": 100,
            "uploads_per_day": 10,
            "chat_per_hour": 50,
            "tokens_per_day": 10000
        },
        "pro": {
            "auth_per_minute": 10,
            "api_per_hour": 1000,
            "uploads_per_day": -1,  # unlimited
            "chat_per_hour": -1,    # unlimited
            "tokens_per_day": 1000000
        }
    }
    
    # Security Headers
    security_headers_enabled: bool = True
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "*"
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    cors_allow_headers: List[str] = ["*"]
    
    # Content Security Policy
    csp_default_src: str = "'self'"
    csp_script_src: str = "'self'"
    csp_style_src: str = "'self' 'unsafe-inline'"
    csp_img_src: str = "'self' data: https:"
    csp_font_src: str = "'self'"
    csp_connect_src: str = "'self'"
    csp_frame_src: str = "'none'"
    csp_object_src: str = "'none'"
    csp_base_uri: str = "'self'"
    csp_form_action: str = "'self'"
    csp_frame_ancestors: str = "'none'"
    csp_upgrade_insecure_requests: bool = True
    
    # CSRF Protection
    csrf_enabled: bool = True
    csrf_secret_key: str = "your-csrf-secret-key"
    csrf_token_expire_minutes: int = 30
    
    # File Upload Security
    max_file_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    allowed_file_types: List[str] = [".log", ".txt", ".json", ".csv"]
    scan_uploaded_files: bool = True
    quarantine_suspicious_files: bool = True
    
    # Input Validation
    max_input_length: int = 10000
    sanitize_html: bool = True
    validate_emails: bool = True
    validate_urls: bool = True
    
    # Authentication
    jwt_secret_key: str = "your-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Session Management
    session_timeout_minutes: int = 60
    max_concurrent_sessions: int = 5
    session_cleanup_interval_minutes: int = 15
    
    # API Key Security
    api_key_length: int = 32
    api_key_prefix: str = "loglytics_"
    api_key_rate_limit_per_hour: int = 1000
    
    # Encryption
    encryption_enabled: bool = True
    encryption_key: str = "your-encryption-key"
    encryption_algorithm: str = "fernet"
    
    # Audit Logging
    audit_log_enabled: bool = True
    audit_log_retention_days: int = 2555  # 7 years
    audit_log_sensitive_operations: List[str] = [
        "user_login",
        "user_logout", 
        "password_change",
        "api_key_create",
        "api_key_revoke",
        "file_upload",
        "file_delete",
        "project_share",
        "settings_change"
    ]
    
    # Webhook Security
    webhook_hmac_secret: str = "your-webhook-secret"
    webhook_timeout_seconds: int = 5
    webhook_max_retries: int = 3
    webhook_retry_delay_seconds: int = 1
    
    # DoS Protection
    dos_protection_enabled: bool = False
    max_connections_per_ip: int = 100
    max_requests_per_minute: int = 1000
    request_timeout_seconds: int = 30
    max_websocket_connections: int = 50
    
    # Security Scanning
    security_scan_enabled: bool = True
    scan_for_scripts: bool = True
    scan_for_malware: bool = True
    quarantine_threshold: float = 0.8  # 80% confidence threshold
    
    # GDPR Compliance
    gdpr_enabled: bool = True
    data_retention_days: Dict[str, int] = {
        "user_data": 365,
        "audit_logs": 2555,
        "log_files": 90,
        "chat_sessions": 180,
        "analysis_results": 365,
        "backup_data": 30
    }
    anonymization_enabled: bool = True
    
    # Monitoring and Alerting
    monitoring_enabled: bool = True
    alert_on_failed_auth: bool = True
    alert_on_suspicious_activity: bool = True
    alert_on_rate_limit_violations: bool = True
    alert_on_file_quarantine: bool = True
    
    # Error Handling
    generic_error_messages: bool = True
    detailed_logging: bool = True
    log_sensitive_data: bool = False
    


# Global security configuration instance
security_config = SecurityConfig()


def get_security_config() -> SecurityConfig:
    """Get security configuration instance"""
    return security_config


def update_security_config(**kwargs) -> None:
    """Update security configuration"""
    global security_config
    for key, value in kwargs.items():
        if hasattr(security_config, key):
            setattr(security_config, key, value)


def get_rate_limits_for_tier(tier: str) -> Dict[str, int]:
    """Get rate limits for a specific subscription tier"""
    return security_config.rate_limits.get(tier, security_config.rate_limits["free"])


def is_security_feature_enabled(feature: str) -> bool:
    """Check if a security feature is enabled"""
    feature_map = {
        "rate_limiting": security_config.rate_limit_enabled,
        "security_headers": security_config.security_headers_enabled,
        "csrf_protection": security_config.csrf_enabled,
        "file_scanning": security_config.scan_uploaded_files,
        "input_validation": security_config.sanitize_html,
        "audit_logging": security_config.audit_log_enabled,
        "encryption": security_config.encryption_enabled,
        "dos_protection": security_config.dos_protection_enabled,
        "security_scanning": security_config.security_scan_enabled,
        "gdpr_compliance": security_config.gdpr_enabled,
        "monitoring": security_config.monitoring_enabled
    }
    
    return feature_map.get(feature, False)


def get_csp_header() -> str:
    """Get Content Security Policy header"""
    directives = []
    
    if security_config.csp_default_src:
        directives.append(f"default-src {security_config.csp_default_src}")
    
    if security_config.csp_script_src:
        directives.append(f"script-src {security_config.csp_script_src}")
    
    if security_config.csp_style_src:
        directives.append(f"style-src {security_config.csp_style_src}")
    
    if security_config.csp_img_src:
        directives.append(f"img-src {security_config.csp_img_src}")
    
    if security_config.csp_font_src:
        directives.append(f"font-src {security_config.csp_font_src}")
    
    if security_config.csp_connect_src:
        directives.append(f"connect-src {security_config.csp_connect_src}")
    
    if security_config.csp_frame_src:
        directives.append(f"frame-src {security_config.csp_frame_src}")
    
    if security_config.csp_object_src:
        directives.append(f"object-src {security_config.csp_object_src}")
    
    if security_config.csp_base_uri:
        directives.append(f"base-uri {security_config.csp_base_uri}")
    
    if security_config.csp_form_action:
        directives.append(f"form-action {security_config.csp_form_action}")
    
    if security_config.csp_frame_ancestors:
        directives.append(f"frame-ancestors {security_config.csp_frame_ancestors}")
    
    if security_config.csp_upgrade_insecure_requests:
        directives.append("upgrade-insecure-requests")
    
    return "; ".join(directives)


def get_allowed_file_types() -> List[str]:
    """Get list of allowed file types"""
    return security_config.allowed_file_types


def get_max_file_size() -> int:
    """Get maximum file size in bytes"""
    return security_config.max_file_size


def get_audit_sensitive_operations() -> List[str]:
    """Get list of sensitive operations to audit"""
    return security_config.audit_log_sensitive_operations


def get_data_retention_days() -> Dict[str, int]:
    """Get data retention periods in days"""
    return security_config.data_retention_days
