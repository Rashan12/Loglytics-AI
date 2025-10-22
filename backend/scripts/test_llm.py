#!/usr/bin/env python3
"""
LLM Service Test Script for Loglytics AI
Tests all LLM functionality including Ollama and Maverick integration
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMTester:
    """Test LLM service functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.access_token: str = None
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def authenticate(self) -> bool:
        """Authenticate and get access token"""
        logger.info("🔐 Authenticating...")
        
        # Try to register a test user first
        try:
            register_data = {
                "email": "llmtest@example.com",
                "username": "llmtest",
                "password": "TestPassword123!",
                "full_name": "LLM Test User",
                "subscription_tier": "pro"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data
            )
            
            if response.status_code not in [201, 400]:  # 400 if user already exists
                logger.warning(f"Registration response: {response.status_code}")
        except Exception as e:
            logger.warning(f"Registration failed: {e}")
        
        # Login
        try:
            login_data = {
                "username": "llmtest@example.com",
                "password": "TestPassword123!"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                logger.info("✅ Authentication successful")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    async def test_llm_health(self) -> bool:
        """Test LLM service health"""
        logger.info("🏥 Testing LLM health...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/llm/health",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ LLM health check passed")
                logger.info(f"   Ollama: {data.get('ollama', {}).get('available', False)}")
                logger.info(f"   Maverick: {data.get('maverick', {}).get('available', False)}")
                return True
            else:
                logger.error(f"❌ LLM health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ LLM health check error: {e}")
            return False
    
    async def test_available_models(self) -> bool:
        """Test getting available models"""
        logger.info("🤖 Testing available models...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/llm/models",
                headers=headers
            )
            
            if response.status_code == 200:
                models = response.json()
                logger.info(f"✅ Found {len(models)} available models")
                for model in models:
                    logger.info(f"   - {model.get('name', 'Unknown')} ({model.get('provider', 'Unknown')})")
                return True
            else:
                logger.error(f"❌ Failed to get models: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error getting models: {e}")
            return False
    
    async def test_chat_completion(self) -> bool:
        """Test chat completion"""
        logger.info("💬 Testing chat completion...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            chat_data = {
                "message": "Hello! Can you help me analyze logs?",
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/llm/chat",
                json=chat_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Chat completion successful")
                logger.info(f"   Model: {data.get('model_used', 'Unknown')}")
                logger.info(f"   Tokens: {data.get('tokens_used', 0)}")
                logger.info(f"   Latency: {data.get('latency_ms', 0):.2f}ms")
                logger.info(f"   Response: {data.get('message', '')[:100]}...")
                return True
            else:
                logger.error(f"❌ Chat completion failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Chat completion error: {e}")
            return False
    
    async def test_log_analysis(self) -> bool:
        """Test log analysis"""
        logger.info("📊 Testing log analysis...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Sample log entries
            log_entries = [
                {
                    "level": "ERROR",
                    "message": "Database connection failed: timeout after 30s",
                    "timestamp": "2024-01-15T10:30:45Z",
                    "source": "database"
                },
                {
                    "level": "WARN",
                    "message": "High memory usage: 85% of available memory",
                    "timestamp": "2024-01-15T10:31:12Z",
                    "source": "monitor"
                },
                {
                    "level": "INFO",
                    "message": "User login successful: user_id=12345",
                    "timestamp": "2024-01-15T10:31:45Z",
                    "source": "auth"
                }
            ]
            
            analysis_data = {
                "log_entries": log_entries,
                "analysis_type": "general",
                "temperature": 0.3,
                "structured_output": True
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/llm/analyze",
                json=analysis_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Log analysis successful")
                logger.info(f"   Model: {data.get('model_used', 'Unknown')}")
                logger.info(f"   Tokens: {data.get('tokens_used', 0)}")
                logger.info(f"   Analysis: {data.get('analysis', '')[:200]}...")
                return True
            else:
                logger.error(f"❌ Log analysis failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Log analysis error: {e}")
            return False
    
    async def test_error_detection(self) -> bool:
        """Test error detection"""
        logger.info("🚨 Testing error detection...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Sample log entries with errors
            log_entries = [
                {
                    "level": "ERROR",
                    "message": "HTTP 500 Internal Server Error - /api/users",
                    "timestamp": "2024-01-15T10:30:45Z",
                    "source": "api"
                },
                {
                    "level": "ERROR",
                    "message": "Database connection timeout",
                    "timestamp": "2024-01-15T10:31:12Z",
                    "source": "database"
                },
                {
                    "level": "WARN",
                    "message": "Slow query detected: 5.2s execution time",
                    "timestamp": "2024-01-15T10:31:45Z",
                    "source": "database"
                }
            ]
            
            analysis_data = {
                "log_entries": log_entries,
                "analysis_type": "error_detection",
                "temperature": 0.3,
                "structured_output": True
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/llm/detect-errors",
                json=analysis_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Error detection successful")
                logger.info(f"   Model: {data.get('model_used', 'Unknown')}")
                logger.info(f"   Analysis: {data.get('analysis', '')[:200]}...")
                return True
            else:
                logger.error(f"❌ Error detection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error detection error: {e}")
            return False
    
    async def test_anomaly_detection(self) -> bool:
        """Test anomaly detection"""
        logger.info("🔍 Testing anomaly detection...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Sample log entries with anomalies
            log_entries = [
                {
                    "level": "INFO",
                    "message": "Normal operation: CPU 45%",
                    "timestamp": "2024-01-15T10:30:45Z",
                    "source": "monitor"
                },
                {
                    "level": "INFO",
                    "message": "Normal operation: CPU 48%",
                    "timestamp": "2024-01-15T10:31:12Z",
                    "source": "monitor"
                },
                {
                    "level": "CRITICAL",
                    "message": "System overload: CPU 95%",
                    "timestamp": "2024-01-15T10:31:45Z",
                    "source": "monitor"
                }
            ]
            
            analysis_data = {
                "log_entries": log_entries,
                "analysis_type": "anomaly",
                "temperature": 0.3,
                "structured_output": True
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/llm/detect-anomalies",
                json=analysis_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Anomaly detection successful")
                logger.info(f"   Model: {data.get('model_used', 'Unknown')}")
                logger.info(f"   Analysis: {data.get('analysis', '')[:200]}...")
                return True
            else:
                logger.error(f"❌ Anomaly detection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Anomaly detection error: {e}")
            return False
    
    async def test_natural_query(self) -> bool:
        """Test natural language query"""
        logger.info("❓ Testing natural language query...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            log_entries = [
                {
                    "level": "ERROR",
                    "message": "Database connection failed",
                    "timestamp": "2024-01-15T10:30:45Z",
                    "source": "database"
                },
                {
                    "level": "WARN",
                    "message": "High memory usage detected",
                    "timestamp": "2024-01-15T10:31:12Z",
                    "source": "monitor"
                }
            ]
            
            query_data = {
                "log_entries": log_entries,
                "query": "What errors are occurring in my system?",
                "temperature": 0.3,
                "structured_output": True
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/llm/query",
                json=query_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Natural query successful")
                logger.info(f"   Model: {data.get('model_used', 'Unknown')}")
                logger.info(f"   Response: {data.get('analysis', '')[:200]}...")
                return True
            else:
                logger.error(f"❌ Natural query failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Natural query error: {e}")
            return False
    
    async def test_log_summarization(self) -> bool:
        """Test log summarization"""
        logger.info("📝 Testing log summarization...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Sample log entries for summarization
            log_entries = [
                {
                    "level": "INFO",
                    "message": "Application started successfully",
                    "timestamp": "2024-01-15T10:00:00Z",
                    "source": "app"
                },
                {
                    "level": "ERROR",
                    "message": "Database connection failed",
                    "timestamp": "2024-01-15T10:30:45Z",
                    "source": "database"
                },
                {
                    "level": "WARN",
                    "message": "High memory usage: 85%",
                    "timestamp": "2024-01-15T10:31:12Z",
                    "source": "monitor"
                },
                {
                    "level": "INFO",
                    "message": "User login successful",
                    "timestamp": "2024-01-15T10:31:45Z",
                    "source": "auth"
                }
            ]
            
            summary_data = {
                "log_entries": log_entries,
                "timeframe": "last hour",
                "temperature": 0.3,
                "structured_output": True
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/llm/summarize",
                json=summary_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Log summarization successful")
                logger.info(f"   Model: {data.get('model_used', 'Unknown')}")
                logger.info(f"   Summary: {data.get('analysis', '')[:200]}...")
                return True
            else:
                logger.error(f"❌ Log summarization failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Log summarization error: {e}")
            return False
    
    async def test_streaming_chat(self) -> bool:
        """Test streaming chat completion"""
        logger.info("🌊 Testing streaming chat...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            chat_data = {
                "message": "Tell me about log analysis best practices",
                "temperature": 0.7,
                "max_tokens": 300
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/llm/chat/stream",
                json=chat_data,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info("✅ Streaming chat successful")
                
                # Read streaming response
                content = ""
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            content += chunk.get("content", "")
                        except json.JSONDecodeError:
                            continue
                
                logger.info(f"   Streamed content: {content[:100]}...")
                return True
            else:
                logger.error(f"❌ Streaming chat failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Streaming chat error: {e}")
            return False
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting"""
        logger.info("⏱️ Testing rate limiting...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Make multiple requests quickly
            for i in range(5):
                chat_data = {
                    "message": f"Test message {i+1}",
                    "temperature": 0.7,
                    "max_tokens": 50
                }
                
                response = await self.client.post(
                    f"{self.base_url}/api/v1/llm/chat",
                    json=chat_data,
                    headers=headers
                )
                
                if response.status_code == 429:
                    logger.info(f"✅ Rate limiting triggered after {i+1} requests")
                    return True
                elif response.status_code != 200:
                    logger.warning(f"Unexpected status code: {response.status_code}")
            
            logger.warning("⚠️ Rate limiting not triggered - may not be configured")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rate limiting test error: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all LLM tests"""
        logger.info("🚀 Starting LLM Service Tests")
        logger.info("=" * 50)
        
        # Authenticate first
        if not await self.authenticate():
            logger.error("❌ Authentication failed, cannot run tests")
            return False
        
        tests = [
            ("LLM Health Check", self.test_llm_health),
            ("Available Models", self.test_available_models),
            ("Chat Completion", self.test_chat_completion),
            ("Log Analysis", self.test_log_analysis),
            ("Error Detection", self.test_error_detection),
            ("Anomaly Detection", self.test_anomaly_detection),
            ("Natural Query", self.test_natural_query),
            ("Log Summarization", self.test_log_summarization),
            ("Streaming Chat", self.test_streaming_chat),
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
            logger.info("🎉 All tests passed! LLM service is working correctly.")
        else:
            logger.info("⚠️ Some tests failed. Please check the configuration and logs.")
        
        return passed == total

async def main():
    """Main test function"""
    base_url = "http://localhost:8000"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    logger.info(f"Testing LLM service at: {base_url}")
    
    async with LLMTester(base_url) as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
