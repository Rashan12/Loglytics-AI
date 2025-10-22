"""
Password handling utilities for Loglytics AI
Provides secure password hashing and verification using bcrypt
"""

import re
from typing import Optional
from passlib.context import CryptContext
from passlib.exc import InvalidHashError
import logging

logger = logging.getLogger(__name__)

# Configure bcrypt with cost factor 12 for security
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

class PasswordHandler:
    """Handles password operations with bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
            
        Raises:
            ValueError: If password is empty or None
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        try:
            hashed = pwd_context.hash(password)
            logger.debug("Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise ValueError("Failed to hash password")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hash to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        if not plain_password or not hashed_password:
            return False
        
        try:
            is_valid = pwd_context.verify(plain_password, hashed_password)
            logger.debug(f"Password verification: {'success' if is_valid else 'failed'}")
            return is_valid
        except InvalidHashError:
            logger.warning("Invalid hash format during password verification")
            return False
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list[str]]:
        """
        Validate password strength according to security requirements
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not password:
            errors.append("Password is required")
            return False, errors
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        # Optional: Check for special characters
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password should contain at least one special character")
        
        # Check for common weak patterns
        if re.search(r'(.)\1{2,}', password):
            errors.append("Password should not contain repeated characters")
        
        if re.search(r'(123|abc|qwe|asd)', password.lower()):
            errors.append("Password should not contain common sequences")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def needs_update(hashed_password: str) -> bool:
        """
        Check if a password hash needs to be updated (e.g., due to algorithm changes)
        
        Args:
            hashed_password: Current password hash
            
        Returns:
            True if password needs update, False otherwise
        """
        try:
            return pwd_context.needs_update(hashed_password)
        except Exception as e:
            logger.error(f"Error checking if password needs update: {e}")
            return False
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """
        Generate a secure random password
        
        Args:
            length: Length of password to generate
            
        Returns:
            Secure random password
        """
        import secrets
        import string
        
        if length < 8:
            length = 8
        
        # Character sets
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each required set
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill the rest with random characters
        all_chars = uppercase + lowercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    @staticmethod
    def check_password_breach(password: str) -> bool:
        """
        Check if password appears in common breach databases
        This is a placeholder - in production, you'd integrate with HaveIBeenPwned API
        
        Args:
            password: Password to check
            
        Returns:
            True if password appears in breaches, False otherwise
        """
        # Common weak passwords that should be rejected
        common_passwords = {
            "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey",
            "1234567890", "password1", "qwerty123", "dragon", "master"
        }
        
        return password.lower() in common_passwords
