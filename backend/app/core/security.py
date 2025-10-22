"""
Security utilities for Loglytics AI
Provides JWT token creation and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import hashlib
import logging
import base64
from cryptography.fernet import Fernet

from app.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise ValueError("Failed to create access token")

def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token
    
    Args:
        length: Token length
        
    Returns:
        Secure random token
    """
    return secrets.token_urlsafe(length)

def generate_api_key() -> str:
    """
    Generate a secure API key
    
    Returns:
        Secure API key
    """
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage
    
    Args:
        api_key: API key to hash
        
    Returns:
        Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()

def generate_password_reset_token() -> str:
    """
    Generate a password reset token
    
    Returns:
        Password reset token
    """
    return secrets.token_urlsafe(32)

def generate_email_verification_token() -> str:
    """
    Generate an email verification token
    
    Returns:
        Email verification token
    """
    return secrets.token_urlsafe(32)

def create_secure_filename(original_filename: str) -> str:
    """
    Create a secure filename from original filename
    
    Args:
        original_filename: Original filename
        
    Returns:
        Secure filename
    """
    import os
    import uuid
    
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate secure filename
    secure_name = f"{uuid.uuid4().hex}{ext}"
    
    return secure_name

def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_string: Input string to sanitize
        
    Returns:
        Sanitized string
    """
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
    
    sanitized = input_string
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length
    sanitized = sanitized[:1000]
    
    return sanitized.strip()

def validate_email_domain(email: str) -> bool:
    """
    Validate email domain against allowed domains
    
    Args:
        email: Email address to validate
        
    Returns:
        True if domain is allowed, False otherwise
    """
    if not email or '@' not in email:
        return False
    
    domain = email.split('@')[1].lower()
    
    # List of allowed domains (can be configured)
    allowed_domains = [
        'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
        'company.com', 'example.com'  # Add your company domains
    ]
    
    return domain in allowed_domains

def check_password_strength(password: str) -> dict:
    """
    Check password strength
    
    Args:
        password: Password to check
        
    Returns:
        Dictionary with strength information
    """
    strength = {
        'score': 0,
        'is_strong': False,
        'errors': [],
        'suggestions': []
    }
    
    if not password:
        strength['errors'].append('Password is required')
        return strength
    
    # Length check
    if len(password) < 8:
        strength['errors'].append('Password must be at least 8 characters long')
    elif len(password) >= 12:
        strength['score'] += 2
    else:
        strength['score'] += 1
    
    # Character variety checks
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    
    if has_upper:
        strength['score'] += 1
    else:
        strength['errors'].append('Password must contain at least one uppercase letter')
    
    if has_lower:
        strength['score'] += 1
    else:
        strength['errors'].append('Password must contain at least one lowercase letter')
    
    if has_digit:
        strength['score'] += 1
    else:
        strength['errors'].append('Password must contain at least one number')
    
    if has_special:
        strength['score'] += 1
    else:
        strength['suggestions'].append('Consider adding special characters for better security')
    
    # Check for common patterns
    if password.lower() in ['password', '123456', 'qwerty', 'abc123']:
        strength['score'] = 0
        strength['errors'].append('Password is too common')
    
    # Check for repeated characters
    if len(set(password)) < len(password) * 0.6:
        strength['suggestions'].append('Avoid repeating characters')
    
    # Determine if password is strong
    strength['is_strong'] = strength['score'] >= 4 and len(strength['errors']) == 0
    
    return strength

def create_csrf_token() -> str:
    """
    Create a CSRF token
    
    Returns:
        CSRF token
    """
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, session_token: str) -> bool:
    """
    Verify a CSRF token
    
    Args:
        token: Token to verify
        session_token: Session token to compare against
        
    Returns:
        True if token is valid, False otherwise
    """
    return secrets.compare_digest(token, session_token)

def encrypt_credentials(credentials: str) -> str:
    """
    Encrypt credentials for secure storage
    
    Args:
        credentials: Plain text credentials to encrypt
        
    Returns:
        Encrypted credentials
    """
    try:
        # Use the secret key to create a Fernet key
        key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'0'))
        fernet = Fernet(key)
        encrypted = fernet.encrypt(credentials.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        logger.error(f"Error encrypting credentials: {e}")
        raise ValueError("Failed to encrypt credentials")

def decrypt_credentials(encrypted_credentials: str) -> str:
    """
    Decrypt credentials
    
    Args:
        encrypted_credentials: Encrypted credentials to decrypt
        
    Returns:
        Decrypted credentials
    """
    try:
        # Use the secret key to create a Fernet key
        key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'0'))
        fernet = Fernet(key)
        encrypted_data = base64.urlsafe_b64decode(encrypted_credentials.encode())
        decrypted = fernet.decrypt(encrypted_data)
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Error decrypting credentials: {e}")
        raise ValueError("Failed to decrypt credentials")