"""
Webhook Security and Validation
Provides HMAC signature validation and webhook security
"""

import hmac
import hashlib
import time
import secrets
import asyncio
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
import requests
import logging

from app.config import settings
from app.security.encryption import encryption_manager

logger = logging.getLogger(__name__)


class WebhookValidator:
    """Webhook security and validation"""
    
    def __init__(self):
        self.timeout = 5  # 5 seconds
        self.max_retries = 3
        self.retry_delay = 1  # 1 second
        self.allowed_schemes = {"http", "https"}
        self.blocked_domains = {
            "localhost", "127.0.0.1", "0.0.0.0", "::1",
            "example.com", "test.com", "invalid.com"
        }
    
    def generate_webhook_secret(self) -> str:
        """Generate secure webhook secret"""
        return secrets.token_urlsafe(32)
    
    def encrypt_webhook_secret(self, secret: str) -> str:
        """Encrypt webhook secret for storage"""
        return encryption_manager.encrypt_webhook_secret(secret)
    
    def decrypt_webhook_secret(self, encrypted_secret: str) -> str:
        """Decrypt webhook secret"""
        return encryption_manager.decrypt_webhook_secret(encrypted_secret)
    
    def generate_hmac_signature(self, payload: str, secret: str, algorithm: str = "sha256") -> str:
        """
        Generate HMAC signature for webhook payload
        
        Args:
            payload: Webhook payload as string
            secret: Webhook secret
            algorithm: Hash algorithm (sha1, sha256, sha512)
            
        Returns:
            HMAC signature as hex string
        """
        try:
            if algorithm == "sha1":
                hash_func = hashlib.sha1
            elif algorithm == "sha256":
                hash_func = hashlib.sha256
            elif algorithm == "sha512":
                hash_func = hashlib.sha512
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hash_func
            ).hexdigest()
            
            return signature
            
        except Exception as e:
            logger.error(f"Error generating HMAC signature: {e}")
            raise ValueError("Failed to generate HMAC signature")
    
    def verify_hmac_signature(
        self,
        payload: str,
        signature: str,
        secret: str,
        algorithm: str = "sha256"
    ) -> bool:
        """
        Verify HMAC signature
        
        Args:
            payload: Webhook payload as string
            signature: Received signature
            secret: Webhook secret
            algorithm: Hash algorithm
            
        Returns:
            True if signature is valid
        """
        try:
            expected_signature = self.generate_hmac_signature(payload, secret, algorithm)
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying HMAC signature: {e}")
            return False
    
    def validate_webhook_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate webhook URL
        
        Args:
            url: Webhook URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not url:
                return False, "URL is required"
            
            # Parse URL
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in self.allowed_schemes:
                return False, f"Scheme not allowed: {parsed.scheme}"
            
            # Check domain
            if not parsed.netloc:
                return False, "Invalid domain"
            
            # Check for blocked domains
            domain = parsed.netloc.lower()
            if domain in self.blocked_domains:
                return False, f"Domain not allowed: {domain}"
            
            # Check for suspicious patterns
            if self._is_suspicious_url(url):
                return False, "Suspicious URL detected"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating webhook URL: {e}")
            return False, "Invalid URL format"
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check for suspicious URL patterns"""
        suspicious_patterns = [
            "javascript:",
            "vbscript:",
            "data:",
            "file:",
            "ftp:",
            "gopher:",
            "mailto:",
            "tel:",
            "<script",
            "</script>",
            "onload=",
            "onerror=",
            "eval(",
            "expression(",
        ]
        
        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                return True
        
        return False
    
    async def test_webhook_url(self, url: str, secret: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Test webhook URL with a test payload
        
        Args:
            url: Webhook URL to test
            secret: Webhook secret
            
        Returns:
            Tuple of (success, error_message, response_info)
        """
        try:
            # Validate URL first
            is_valid, error = self.validate_webhook_url(url)
            if not is_valid:
                return False, error, {}
            
            # Create test payload
            test_payload = {
                "event": "webhook_test",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "message": "This is a test webhook from Loglytics AI",
                    "test_id": secrets.token_hex(8)
                }
            }
            
            # Convert to JSON string
            import json
            payload_str = json.dumps(test_payload)
            
            # Generate signature
            signature = self.generate_hmac_signature(payload_str, secret)
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": f"sha256={signature}",
                "X-Webhook-Timestamp": str(int(time.time())),
                "User-Agent": "Loglytics-AI-Webhook/1.0"
            }
            
            # Send test request
            response = requests.post(
                url,
                data=payload_str,
                headers=headers,
                timeout=self.timeout,
                verify=True  # Verify SSL certificates
            )
            
            response_info = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "response_time": response.elapsed.total_seconds(),
                "success": 200 <= response.status_code < 300
            }
            
            if response_info["success"]:
                return True, "Webhook test successful", response_info
            else:
                return False, f"Webhook test failed with status {response.status_code}", response_info
            
        except requests.exceptions.Timeout:
            return False, "Webhook test timed out", {}
        except requests.exceptions.ConnectionError:
            return False, "Webhook test connection failed", {}
        except requests.exceptions.SSLError:
            return False, "Webhook test SSL error", {}
        except Exception as e:
            logger.error(f"Error testing webhook URL: {e}")
            return False, f"Webhook test error: {str(e)}", {}
    
    async def send_webhook(
        self,
        url: str,
        payload: Dict[str, Any],
        secret: str,
        event_type: str,
        retry_count: int = 0
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Send webhook with retry logic
        
        Args:
            url: Webhook URL
            payload: Webhook payload
            secret: Webhook secret
            event_type: Type of webhook event
            retry_count: Current retry count
            
        Returns:
            Tuple of (success, error_message, response_info)
        """
        try:
            # Add webhook metadata
            webhook_payload = {
                "event": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": payload
            }
            
            # Convert to JSON string
            import json
            payload_str = json.dumps(webhook_payload)
            
            # Generate signature
            signature = self.generate_hmac_signature(payload_str, secret)
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": f"sha256={signature}",
                "X-Webhook-Timestamp": str(int(time.time())),
                "X-Webhook-Event": event_type,
                "User-Agent": "Loglytics-AI-Webhook/1.0"
            }
            
            # Send webhook
            response = requests.post(
                url,
                data=payload_str,
                headers=headers,
                timeout=self.timeout,
                verify=True
            )
            
            response_info = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "response_time": response.elapsed.total_seconds(),
                "retry_count": retry_count,
                "success": 200 <= response.status_code < 300
            }
            
            if response_info["success"]:
                logger.info(f"Webhook sent successfully to {url}")
                return True, "Webhook sent successfully", response_info
            else:
                # Retry logic
                if retry_count < self.max_retries:
                    logger.warning(f"Webhook failed, retrying... (attempt {retry_count + 1})")
                    await asyncio.sleep(self.retry_delay * (retry_count + 1))
                    return await self.send_webhook(url, payload, secret, event_type, retry_count + 1)
                else:
                    error_msg = f"Webhook failed after {self.max_retries} retries with status {response.status_code}"
                    logger.error(error_msg)
                    return False, error_msg, response_info
            
        except requests.exceptions.Timeout:
            if retry_count < self.max_retries:
                logger.warning(f"Webhook timeout, retrying... (attempt {retry_count + 1})")
                await asyncio.sleep(self.retry_delay * (retry_count + 1))
                return await self.send_webhook(url, payload, secret, event_type, retry_count + 1)
            else:
                error_msg = f"Webhook timeout after {self.max_retries} retries"
                logger.error(error_msg)
                return False, error_msg, {}
        
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
            return False, f"Webhook error: {str(e)}", {}
    
    def validate_webhook_request(
        self,
        payload: str,
        signature: str,
        timestamp: str,
        secret: str,
        tolerance: int = 300
    ) -> Tuple[bool, str]:
        """
        Validate incoming webhook request
        
        Args:
            payload: Webhook payload
            signature: HMAC signature
            timestamp: Request timestamp
            secret: Webhook secret
            tolerance: Time tolerance in seconds (default 5 minutes)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check timestamp to prevent replay attacks
            try:
                request_time = int(timestamp)
                current_time = int(time.time())
                
                if abs(current_time - request_time) > tolerance:
                    return False, "Request timestamp too old"
            except ValueError:
                return False, "Invalid timestamp format"
            
            # Verify signature
            if not self.verify_hmac_signature(payload, signature, secret):
                return False, "Invalid signature"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating webhook request: {e}")
            return False, "Validation error"
    
    def rate_limit_webhook(self, webhook_id: str, max_requests: int = 100, window: int = 3600) -> bool:
        """
        Check webhook rate limit
        
        Args:
            webhook_id: Webhook identifier
            max_requests: Maximum requests per window
            window: Time window in seconds
            
        Returns:
            True if within rate limit
        """
        # This would integrate with Redis rate limiting
        # For now, return True (no rate limiting)
        return True


class WebhookSecurityMiddleware:
    """Middleware for webhook security"""
    
    def __init__(self):
        self.validator = WebhookValidator()
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
    
    async def validate_incoming_webhook(
        self,
        request_data: str,
        headers: Dict[str, str],
        webhook_secret: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate incoming webhook request
        
        Args:
            request_data: Request body
            headers: Request headers
            webhook_secret: Webhook secret
            
        Returns:
            Tuple of (is_valid, error_message, webhook_info)
        """
        try:
            # Extract signature and timestamp
            signature = headers.get("X-Webhook-Signature", "")
            timestamp = headers.get("X-Webhook-Timestamp", "")
            event_type = headers.get("X-Webhook-Event", "unknown")
            
            if not signature:
                return False, "Missing signature", {}
            
            if not timestamp:
                return False, "Missing timestamp", {}
            
            # Validate request
            is_valid, error = self.validator.validate_webhook_request(
                request_data, signature, timestamp, webhook_secret
            )
            
            if not is_valid:
                return False, error, {}
            
            webhook_info = {
                "event_type": event_type,
                "timestamp": timestamp,
                "signature": signature,
                "validated": True
            }
            
            return True, "", webhook_info
            
        except Exception as e:
            logger.error(f"Error validating incoming webhook: {e}")
            return False, "Validation error", {}
    
    async def send_webhook_notification(
        self,
        webhook_url: str,
        webhook_secret: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Send webhook notification
        
        Args:
            webhook_url: Webhook URL
            webhook_secret: Webhook secret
            event_type: Event type
            data: Event data
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate URL first
            is_valid, error = self.validator.validate_webhook_url(webhook_url)
            if not is_valid:
                return False, error
            
            # Send webhook
            success, message, response_info = await self.validator.send_webhook(
                webhook_url, data, webhook_secret, event_type
            )
            
            return success, message
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
            return False, str(e)


# Global webhook validator instance
webhook_validator = WebhookValidator()
webhook_security_middleware = WebhookSecurityMiddleware()
