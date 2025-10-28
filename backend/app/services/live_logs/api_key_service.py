import secrets
import hashlib
import hmac
from typing import Tuple

class APIKeyService:
    """Service for generating and validating API keys"""
    
    @staticmethod
    def generate_api_key() -> Tuple[str, str, str]:
        """
        Generate a new API key
        Returns: (full_key, hashed_key, prefix)
        """
        # Generate 32-byte random key
        key = secrets.token_urlsafe(32)
        
        # Hash for storage
        hashed = hashlib.sha256(key.encode()).hexdigest()
        
        # Prefix for display (first 8 chars)
        prefix = key[:8]
        
        return key, hashed, prefix
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(provided_key: str, stored_hash: str) -> bool:
        """Verify an API key against stored hash"""
        provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        return hmac.compare_digest(provided_hash, stored_hash)
