"""
Encryption System for Sensitive Data
Provides encryption/decryption for data at rest
"""

import base64
import secrets
import hashlib
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Main encryption manager for sensitive data"""
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.key_cache: Dict[str, bytes] = {}
        self.key_rotation_interval = timedelta(days=30)
        
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        master_key = settings.ENCRYPTION_MASTER_KEY
        
        if not master_key:
            # Generate new master key
            master_key = Fernet.generate_key()
            logger.warning("No master key found, generated new one. Store this securely!")
            logger.warning(f"Master key: {base64.urlsafe_b64encode(master_key).decode()}")
        
        elif isinstance(master_key, str):
            # Convert string key to bytes
            master_key = base64.urlsafe_b64decode(master_key.encode())
        
        return master_key
    
    def _derive_key(self, purpose: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key for specific purpose"""
        if purpose in self.key_cache:
            return self.key_cache[purpose]
        
        if salt is None:
            salt = f"loglytics_{purpose}".encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        self.key_cache[purpose] = key
        
        return key
    
    def encrypt_credentials(self, credentials: str, purpose: str = "credentials") -> str:
        """
        Encrypt credentials for storage
        
        Args:
            credentials: Plain text credentials
            purpose: Purpose of encryption (for key derivation)
            
        Returns:
            Encrypted credentials as base64 string
        """
        try:
            key = self._derive_key(purpose)
            fernet = Fernet(key)
            encrypted = fernet.encrypt(credentials.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
            
        except Exception as e:
            logger.error(f"Error encrypting credentials: {e}")
            raise ValueError("Failed to encrypt credentials")
    
    def decrypt_credentials(self, encrypted_credentials: str, purpose: str = "credentials") -> str:
        """
        Decrypt credentials
        
        Args:
            encrypted_credentials: Encrypted credentials as base64 string
            purpose: Purpose of encryption (for key derivation)
            
        Returns:
            Decrypted credentials
        """
        try:
            key = self._derive_key(purpose)
            fernet = Fernet(key)
            encrypted_data = base64.urlsafe_b64decode(encrypted_credentials.encode())
            decrypted = fernet.decrypt(encrypted_data)
            return decrypted.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting credentials: {e}")
            raise ValueError("Failed to decrypt credentials")
    
    def encrypt_webhook_secret(self, secret: str) -> str:
        """Encrypt webhook secret"""
        return self.encrypt_credentials(secret, "webhook_secrets")
    
    def decrypt_webhook_secret(self, encrypted_secret: str) -> str:
        """Decrypt webhook secret"""
        return self.decrypt_credentials(encrypted_secret, "webhook_secrets")
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key (for storage)"""
        return self.encrypt_credentials(api_key, "api_keys")
    
    def decrypt_api_key(self, encrypted_api_key: str) -> str:
        """Decrypt API key"""
        return self.decrypt_credentials(encrypted_api_key, "api_keys")
    
    def encrypt_user_data(self, data: str, user_id: str) -> str:
        """Encrypt user-specific data"""
        purpose = f"user_data_{user_id}"
        return self.encrypt_credentials(data, purpose)
    
    def decrypt_user_data(self, encrypted_data: str, user_id: str) -> str:
        """Decrypt user-specific data"""
        purpose = f"user_data_{user_id}"
        return self.decrypt_credentials(encrypted_data, purpose)
    
    def encrypt_system_config(self, config: str) -> str:
        """Encrypt system configuration"""
        return self.encrypt_credentials(config, "system_config")
    
    def decrypt_system_config(self, encrypted_config: str) -> str:
        """Decrypt system configuration"""
        return self.decrypt_credentials(encrypted_config, "system_config")


class FieldEncryption:
    """Field-level encryption for database models"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def encrypt_field(self, value: str, field_type: str) -> str:
        """Encrypt a field value"""
        if not value:
            return value
        
        return self.encryption_manager.encrypt_credentials(value, f"field_{field_type}")
    
    def decrypt_field(self, encrypted_value: str, field_type: str) -> str:
        """Decrypt a field value"""
        if not encrypted_value:
            return encrypted_value
        
        return self.encryption_manager.decrypt_credentials(encrypted_value, f"field_{field_type}")


class KeyRotation:
    """Key rotation management"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.rotation_log: Dict[str, datetime] = {}
    
    def should_rotate_key(self, purpose: str) -> bool:
        """Check if key should be rotated"""
        if purpose not in self.rotation_log:
            return True
        
        last_rotation = self.rotation_log[purpose]
        return datetime.utcnow() - last_rotation > self.encryption_manager.key_rotation_interval
    
    def rotate_key(self, purpose: str) -> bool:
        """Rotate encryption key for purpose"""
        try:
            # Clear cached key to force regeneration
            if purpose in self.encryption_manager.key_cache:
                del self.encryption_manager.key_cache[purpose]
            
            # Update rotation log
            self.rotation_log[purpose] = datetime.utcnow()
            
            logger.info(f"Rotated encryption key for purpose: {purpose}")
            return True
            
        except Exception as e:
            logger.error(f"Error rotating key for {purpose}: {e}")
            return False
    
    def rotate_all_keys(self) -> Dict[str, bool]:
        """Rotate all encryption keys"""
        results = {}
        
        for purpose in self.encryption_manager.key_cache.keys():
            results[purpose] = self.rotate_key(purpose)
        
        return results


class DataAnonymization:
    """Data anonymization for GDPR compliance"""
    
    def __init__(self):
        self.anonymization_salt = secrets.token_hex(32)
    
    def anonymize_email(self, email: str) -> str:
        """Anonymize email address"""
        if not email or "@" not in email:
            return "anonymous@example.com"
        
        local, domain = email.split("@", 1)
        
        # Hash local part
        hashed_local = hashlib.sha256(f"{local}{self.anonymization_salt}".encode()).hexdigest()[:8]
        
        return f"{hashed_local}@example.com"
    
    def anonymize_ip(self, ip: str) -> str:
        """Anonymize IP address"""
        if not ip:
            return "0.0.0.0"
        
        # Remove last octet for IPv4
        if "." in ip:
            parts = ip.split(".")
            if len(parts) == 4:
                return ".".join(parts[:3]) + ".0"
        
        # Remove last 4 groups for IPv6
        if ":" in ip:
            parts = ip.split(":")
            if len(parts) >= 4:
                return ":".join(parts[:4]) + "::"
        
        return "0.0.0.0"
    
    def anonymize_user_agent(self, user_agent: str) -> str:
        """Anonymize user agent string"""
        if not user_agent:
            return "Unknown"
        
        # Keep only browser type and major version
        if "Chrome" in user_agent:
            return "Chrome Browser"
        elif "Firefox" in user_agent:
            return "Firefox Browser"
        elif "Safari" in user_agent:
            return "Safari Browser"
        elif "Edge" in user_agent:
            return "Edge Browser"
        else:
            return "Other Browser"
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive data in dictionary"""
        anonymized = data.copy()
        
        # Anonymize common sensitive fields
        sensitive_fields = {
            "email", "ip_address", "user_agent", "phone", "address",
            "credit_card", "ssn", "passport", "driver_license"
        }
        
        for field in sensitive_fields:
            if field in anonymized:
                if field == "email":
                    anonymized[field] = self.anonymize_email(anonymized[field])
                elif field == "ip_address":
                    anonymized[field] = self.anonymize_ip(anonymized[field])
                elif field == "user_agent":
                    anonymized[field] = self.anonymize_user_agent(anonymized[field])
                else:
                    anonymized[field] = "[ANONYMIZED]"
        
        return anonymized


class SecureHashing:
    """Secure hashing utilities"""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: bytes) -> bool:
        """Verify password against hash"""
        try:
            key, _ = SecureHashing.hash_password(password, salt)
            return secrets.compare_digest(key, hashed_password)
        except Exception:
            return False
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)


class EncryptionMiddleware:
    """Middleware for automatic field encryption/decryption"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.encrypted_fields = {
            "cloud_credentials": "credentials",
            "webhook_secret": "webhook_secrets",
            "api_key": "api_keys",
            "user_data": "user_data",
            "system_config": "system_config"
        }
    
    def encrypt_model_fields(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in model data"""
        encrypted_data = model_data.copy()
        
        for field, purpose in self.encrypted_fields.items():
            if field in encrypted_data and encrypted_data[field]:
                try:
                    encrypted_data[field] = self.encryption_manager.encrypt_credentials(
                        encrypted_data[field], purpose
                    )
                except Exception as e:
                    logger.error(f"Error encrypting field {field}: {e}")
        
        return encrypted_data
    
    def decrypt_model_fields(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in model data"""
        decrypted_data = model_data.copy()
        
        for field, purpose in self.encrypted_fields.items():
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.encryption_manager.decrypt_credentials(
                        decrypted_data[field], purpose
                    )
                except Exception as e:
                    logger.error(f"Error decrypting field {field}: {e}")
        
        return decrypted_data


# Global instances
encryption_manager = EncryptionManager()
field_encryption = FieldEncryption(encryption_manager)
key_rotation = KeyRotation(encryption_manager)
data_anonymization = DataAnonymization()
secure_hashing = SecureHashing()
encryption_middleware = EncryptionMiddleware(encryption_manager)
