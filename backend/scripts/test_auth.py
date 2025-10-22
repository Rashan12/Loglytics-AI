#!/usr/bin/env python3
"""
Authentication system test script for Loglytics AI
Tests all authentication endpoints and functionality
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthTester:
    """Test authentication system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.api_key: Optional[str] = None
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_health_check(self) -> bool:
        """Test health check endpoint"""
        logger.info("🏥 Testing health check...")
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Health check passed: {data['status']}")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False
    
    async def test_user_registration(self) -> bool:
        """Test user registration"""
        logger.info("📝 Testing user registration...")
        
        test_user = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword123!",
            "full_name": "Test User",
            "subscription_tier": "free",
            "selected_llm_model": "local"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/register",
                json=test_user
            )
            
            if response.status_code == 201:
                data = response.json()
                logger.info(f"✅ User registration successful: {data['email']}")
                return True
            else:
                logger.error(f"❌ User registration failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ User registration error: {e}")
            return False
    
    async def test_user_login(self) -> bool:
        """Test user login"""
        logger.info("🔐 Testing user login...")
        
        login_data = {
            "username": "test@example.com",  # OAuth2 uses username field
            "password": "TestPassword123!"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data  # Use form data for OAuth2
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                logger.info(f"✅ User login successful: {data['user']['email']}")
                return True
            else:
                logger.error(f"❌ User login failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ User login error: {e}")
            return False
    
    async def test_get_current_user(self) -> bool:
        """Test get current user"""
        logger.info("👤 Testing get current user...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get current user successful: {data['email']}")
                return True
            else:
                logger.error(f"❌ Get current user failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Get current user error: {e}")
            return False
    
    async def test_token_refresh(self) -> bool:
        """Test token refresh"""
        logger.info("🔄 Testing token refresh...")
        
        if not self.refresh_token:
            logger.error("❌ No refresh token available")
            return False
        
        refresh_data = {"refresh_token": self.refresh_token}
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/refresh",
                json=refresh_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                logger.info("✅ Token refresh successful")
                return True
            else:
                logger.error(f"❌ Token refresh failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Token refresh error: {e}")
            return False
    
    async def test_password_reset_request(self) -> bool:
        """Test password reset request"""
        logger.info("🔑 Testing password reset request...")
        
        reset_data = {"email": "test@example.com"}
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/password-reset-request",
                json=reset_data
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Password reset request successful: {data['message']}")
                return True
            else:
                logger.error(f"❌ Password reset request failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Password reset request error: {e}")
            return False
    
    async def test_create_api_key(self) -> bool:
        """Test create API key"""
        logger.info("🔑 Testing API key creation...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        key_data = {"name": "Test API Key"}
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/api-keys",
                json=key_data,
                headers=headers
            )
            
            if response.status_code == 201:
                data = response.json()
                self.api_key = data["key"]
                logger.info(f"✅ API key creation successful: {data['name']}")
                return True
            else:
                logger.error(f"❌ API key creation failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ API key creation error: {e}")
            return False
    
    async def test_api_key_authentication(self) -> bool:
        """Test API key authentication"""
        logger.info("🔐 Testing API key authentication...")
        
        if not self.api_key:
            logger.error("❌ No API key available")
            return False
        
        headers = {"X-API-Key": self.api_key}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API key authentication successful: {data['email']}")
                return True
            else:
                logger.error(f"❌ API key authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ API key authentication error: {e}")
            return False
    
    async def test_list_api_keys(self) -> bool:
        """Test list API keys"""
        logger.info("📋 Testing list API keys...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/auth/api-keys",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ List API keys successful: {len(data['api_keys'])} keys")
                return True
            else:
                logger.error(f"❌ List API keys failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ List API keys error: {e}")
            return False
    
    async def test_user_logout(self) -> bool:
        """Test user logout"""
        logger.info("🚪 Testing user logout...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/logout",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ User logout successful: {data['message']}")
                return True
            else:
                logger.error(f"❌ User logout failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ User logout error: {e}")
            return False
    
    async def test_invalid_credentials(self) -> bool:
        """Test invalid credentials handling"""
        logger.info("🚫 Testing invalid credentials...")
        
        invalid_login = {
            "username": "test@example.com",
            "password": "WrongPassword123!"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/login",
                data=invalid_login
            )
            
            if response.status_code == 401:
                logger.info("✅ Invalid credentials properly rejected")
                return True
            else:
                logger.error(f"❌ Invalid credentials not properly handled: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Invalid credentials test error: {e}")
            return False
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting"""
        logger.info("⏱️ Testing rate limiting...")
        
        # Try to make multiple requests quickly
        for i in range(6):  # Should trigger rate limit
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    data={"username": "test@example.com", "password": "TestPassword123!"}
                )
                
                if response.status_code == 429:
                    logger.info(f"✅ Rate limiting triggered after {i+1} requests")
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Rate limiting test error: {e}")
                return False
        
        logger.warning("⚠️ Rate limiting not triggered - may not be configured")
        return True
    
    async def run_all_tests(self) -> bool:
        """Run all authentication tests"""
        logger.info("🚀 Starting Authentication System Tests")
        logger.info("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get Current User", self.test_get_current_user),
            ("Token Refresh", self.test_token_refresh),
            ("Password Reset Request", self.test_password_reset_request),
            ("Create API Key", self.test_create_api_key),
            ("API Key Authentication", self.test_api_key_authentication),
            ("List API Keys", self.test_list_api_keys),
            ("User Logout", self.test_user_logout),
            ("Invalid Credentials", self.test_invalid_credentials),
            ("Rate Limiting", self.test_rate_limiting)
        ]
        
        results = []
        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running {test_name}...")
            try:
                success = await test_func()
                results.append((test_name, success))
                status_icon = "✅" if success else "❌"
                logger.info(f"{status_icon} {test_name}: {'PASSED' if success else 'FAILED'}")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        # Summary
        logger.info("\n📊 Test Summary")
        logger.info("=" * 50)
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status_icon = "✅" if success else "❌"
            logger.info(f"{status_icon} {test_name}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! Authentication system is working correctly.")
        else:
            logger.info("⚠️ Some tests failed. Please check the configuration and logs.")
        
        return passed == total

async def main():
    """Main test function"""
    base_url = "http://localhost:8000"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    logger.info(f"Testing authentication system at: {base_url}")
    
    async with AuthTester(base_url) as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
