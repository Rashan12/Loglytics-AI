import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import logging

logger = logging.getLogger(__name__)

class CredentialEncryption:
    """
    Handles encryption and decryption of cloud provider credentials
    Uses Fernet symmetric encryption with PBKDF2 key derivation
    """
    
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        try:
            # Try to get key from environment variable
            key_b64 = os.getenv("CREDENTIAL_ENCRYPTION_KEY")
            
            if key_b64:
                return base64.b64decode(key_b64)
            
            # Generate new key if not found
            key = Fernet.generate_key()
            
            # Log warning about missing key
            logger.warning("CREDENTIAL_ENCRYPTION_KEY not found in environment. Generated new key.")
            logger.warning("For production, set CREDENTIAL_ENCRYPTION_KEY environment variable.")
            
            return key
            
        except Exception as e:
            logger.error(f"Failed to get encryption key: {str(e)}")
            # Generate fallback key
            return Fernet.generate_key()
    
    def encrypt_credentials(self, credentials: dict) -> dict:
        """
        Encrypt cloud provider credentials
        
        Args:
            credentials: Dictionary containing cloud provider credentials
            
        Returns:
            Dictionary with encrypted credentials
        """
        try:
            if not credentials:
                return {}
            
            # Separate sensitive and non-sensitive fields
            sensitive_fields = self._get_sensitive_fields(credentials)
            non_sensitive = {k: v for k, v in credentials.items() if k not in sensitive_fields}
            
            # Encrypt sensitive fields
            encrypted_sensitive = {}
            for field in sensitive_fields:
                if field in credentials and credentials[field]:
                    value = str(credentials[field])
                    encrypted_value = self.cipher.encrypt(value.encode())
                    encrypted_sensitive[field] = base64.b64encode(encrypted_value).decode()
            
            return {
                **non_sensitive,
                **encrypted_sensitive,
                "_encrypted": True,
                "_encrypted_fields": list(sensitive_fields)
            }
            
        except Exception as e:
            logger.error(f"Failed to encrypt credentials: {str(e)}")
            # Return original credentials if encryption fails
            return credentials
    
    def decrypt_credentials(self, encrypted_credentials: dict) -> dict:
        """
        Decrypt cloud provider credentials
        
        Args:
            encrypted_credentials: Dictionary with encrypted credentials
            
        Returns:
            Dictionary with decrypted credentials
        """
        try:
            if not encrypted_credentials or not encrypted_credentials.get("_encrypted"):
                return encrypted_credentials
            
            # Get encrypted fields
            encrypted_fields = encrypted_credentials.get("_encrypted_fields", [])
            
            # Decrypt sensitive fields
            decrypted_credentials = {}
            for key, value in encrypted_credentials.items():
                if key in encrypted_fields and value:
                    try:
                        encrypted_bytes = base64.b64decode(value.encode())
                        decrypted_value = self.cipher.decrypt(encrypted_bytes)
                        decrypted_credentials[key] = decrypted_value.decode()
                    except Exception as e:
                        logger.error(f"Failed to decrypt field {key}: {str(e)}")
                        decrypted_credentials[key] = value  # Keep original if decryption fails
                elif not key.startswith("_"):
                    decrypted_credentials[key] = value
            
            return decrypted_credentials
            
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {str(e)}")
            # Return original credentials if decryption fails
            return encrypted_credentials
    
    def _get_sensitive_fields(self, credentials: dict) -> set:
        """
        Get list of sensitive fields that should be encrypted
        """
        # Common sensitive fields across cloud providers
        sensitive_fields = {
            # AWS
            "access_key_id", "secret_access_key", "session_token",
            # Azure
            "client_id", "client_secret", "tenant_id", "subscription_id",
            # GCP
            "private_key", "client_email", "private_key_id",
            # Generic
            "password", "token", "key", "secret", "credential"
        }
        
        # Check for fields that contain sensitive data
        found_sensitive = set()
        for field in credentials.keys():
            field_lower = field.lower()
            if any(sensitive in field_lower for sensitive in sensitive_fields):
                found_sensitive.add(field)
        
        return found_sensitive
    
    def encrypt_string(self, text: str) -> str:
        """Encrypt a single string"""
        try:
            encrypted_bytes = self.cipher.encrypt(text.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt string: {str(e)}")
            return text
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt a single string"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode())
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt string: {str(e)}")
            return encrypted_text
    
    def get_key_for_export(self) -> str:
        """Get the encryption key as base64 string for export"""
        return base64.b64encode(self.key).decode()
    
    def set_key_from_export(self, key_b64: str) -> bool:
        """Set encryption key from base64 string"""
        try:
            self.key = base64.b64decode(key_b64.encode())
            self.cipher = Fernet(self.key)
            return True
        except Exception as e:
            logger.error(f"Failed to set encryption key: {str(e)}")
            return False

# Global instance
credential_encryption = CredentialEncryption()

# Convenience functions
def encrypt_credentials(credentials: dict) -> dict:
    """Encrypt credentials using global instance"""
    return credential_encryption.encrypt_credentials(credentials)

def decrypt_credentials(encrypted_credentials: dict) -> dict:
    """Decrypt credentials using global instance"""
    return credential_encryption.decrypt_credentials(encrypted_credentials)

def encrypt_string(text: str) -> str:
    """Encrypt a string using global instance"""
    return credential_encryption.encrypt_string(text)

def decrypt_string(encrypted_text: str) -> str:
    """Decrypt a string using global instance"""
    return credential_encryption.decrypt_string(encrypted_text)
