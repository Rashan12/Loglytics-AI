#!/usr/bin/env python3
"""
AI Models Testing Script for Loglytics AI
Tests both Ollama (local) and Maverick (cloud) models
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm.llm_service import UnifiedLLMService, LLMRequest, LLMTask
from app.services.llm.ollama_client import OllamaClient
from app.services.llm.maverick_client import MaverickClient
from app.database.database import get_db
from app.models.user import User, SubscriptionTier
from app.schemas.user import UserResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelTester:
    """Comprehensive AI model testing class"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "ollama": {"status": "not_tested", "tests": []},
            "maverick": {"status": "not_tested", "tests": []},
            "unified_service": {"status": "not_tested", "tests": []},
            "summary": {}
        }
        
        # Test prompts for different scenarios
        self.test_prompts = {
            "simple_chat": "Hello! How are you today?",
            "log_analysis": "Analyze this log entry: '2024-01-15 10:30:45 ERROR Database connection failed: timeout after 30 seconds'",
            "error_detection": "What could cause a 'Connection timeout' error in a web application?",
            "root_cause": "A user reports that their application is running slowly. What should I investigate first?",
            "technical_question": "Explain the difference between synchronous and asynchronous programming in Python.",
            "creative_task": "Write a short poem about debugging code."
        }
    
    async def test_ollama_client(self) -> Dict[str, Any]:
        """Test Ollama client functionality"""
        logger.info("🔍 Testing Ollama Client...")
        ollama_results = {"status": "testing", "tests": [], "errors": []}
        
        try:
            client = OllamaClient()
            
            # Test 1: Health Check
            logger.info("  📡 Testing health check...")
            health_ok = await client.health_check()
            ollama_results["tests"].append({
                "test": "health_check",
                "status": "passed" if health_ok else "failed",
                "result": health_ok
            })
            
            if not health_ok:
                ollama_results["errors"].append("Ollama service not available")
                ollama_results["status"] = "failed"
                return ollama_results
            
            # Test 2: List Models
            logger.info("  📋 Testing model listing...")
            models = await client.list_models()
            ollama_results["tests"].append({
                "test": "list_models",
                "status": "passed" if models else "failed",
                "result": f"Found {len(models)} models",
                "models": [m["name"] for m in models]
            })
            
            # Test 3: Simple Generation
            logger.info("  💬 Testing simple generation...")
            start_time = time.time()
            response = await client.generate(
                prompt=self.test_prompts["simple_chat"],
                temperature=0.7,
                max_tokens=100
            )
            generation_time = time.time() - start_time
            
            ollama_results["tests"].append({
                "test": "simple_generation",
                "status": "passed" if response.get("content") else "failed",
                "result": {
                    "content_length": len(response.get("content", "")),
                    "tokens_used": response.get("tokens_used", 0),
                    "generation_time": round(generation_time, 2),
                    "model": response.get("model", "unknown")
                },
                "response_preview": response.get("content", "")[:100] + "..." if len(response.get("content", "")) > 100 else response.get("content", "")
            })
            
            # Test 4: Log Analysis
            logger.info("  🔍 Testing log analysis...")
            log_response = await client.generate(
                prompt=self.test_prompts["log_analysis"],
                temperature=0.3,
                max_tokens=200
            )
            
            ollama_results["tests"].append({
                "test": "log_analysis",
                "status": "passed" if log_response.get("content") else "failed",
                "result": {
                    "content_length": len(log_response.get("content", "")),
                    "tokens_used": log_response.get("tokens_used", 0)
                },
                "response_preview": log_response.get("content", "")[:150] + "..." if len(log_response.get("content", "")) > 150 else log_response.get("content", "")
            })
            
            # Test 5: Streaming (if supported)
            logger.info("  🌊 Testing streaming generation...")
            try:
                stream_chunks = []
                async for chunk in client.generate_stream(
                    prompt=self.test_prompts["technical_question"],
                    temperature=0.7,
                    max_tokens=150
                ):
                    stream_chunks.append(chunk)
                    if len(stream_chunks) >= 5:  # Limit for testing
                        break
                
                ollama_results["tests"].append({
                    "test": "streaming_generation",
                    "status": "passed" if stream_chunks else "failed",
                    "result": {
                        "chunks_received": len(stream_chunks),
                        "total_content": "".join([chunk.get("content", "") for chunk in stream_chunks])
                    }
                })
            except Exception as e:
                ollama_results["tests"].append({
                    "test": "streaming_generation",
                    "status": "failed",
                    "error": str(e)
                })
            
            await client.close()
            ollama_results["status"] = "passed"
            
        except Exception as e:
            logger.error(f"❌ Ollama testing failed: {e}")
            ollama_results["status"] = "failed"
            ollama_results["errors"].append(str(e))
        
        return ollama_results
    
    async def test_maverick_client(self) -> Dict[str, Any]:
        """Test Maverick client functionality"""
        logger.info("🔍 Testing Maverick Client...")
        maverick_results = {"status": "testing", "tests": [], "errors": []}
        
        try:
            client = MaverickClient()
            
            # Test 1: Health Check
            logger.info("  📡 Testing health check...")
            health_ok = await client.health_check()
            maverick_results["tests"].append({
                "test": "health_check",
                "status": "passed" if health_ok else "failed",
                "result": health_ok
            })
            
            if not health_ok:
                maverick_results["errors"].append("Maverick model not available")
                maverick_results["status"] = "failed"
                return maverick_results
            
            # Test 2: Memory Usage
            logger.info("  💾 Checking memory usage...")
            memory_info = client.get_memory_usage()
            maverick_results["tests"].append({
                "test": "memory_usage",
                "status": "passed",
                "result": memory_info
            })
            
            # Test 3: Simple Generation
            logger.info("  💬 Testing simple generation...")
            start_time = time.time()
            response = await client.generate(
                prompt=self.test_prompts["simple_chat"],
                temperature=0.7,
                max_tokens=100
            )
            generation_time = time.time() - start_time
            
            maverick_results["tests"].append({
                "test": "simple_generation",
                "status": "passed" if response.get("content") else "failed",
                "result": {
                    "content_length": len(response.get("content", "")),
                    "tokens_used": response.get("tokens_used", 0),
                    "generation_time": round(generation_time, 2),
                    "device": response.get("device", "unknown")
                },
                "response_preview": response.get("content", "")[:100] + "..." if len(response.get("content", "")) > 100 else response.get("content", "")
            })
            
            # Test 4: Error Detection
            logger.info("  🚨 Testing error detection...")
            error_response = await client.generate(
                prompt=self.test_prompts["error_detection"],
                temperature=0.3,
                max_tokens=200
            )
            
            maverick_results["tests"].append({
                "test": "error_detection",
                "status": "passed" if error_response.get("content") else "failed",
                "result": {
                    "content_length": len(error_response.get("content", "")),
                    "tokens_used": error_response.get("tokens_used", 0)
                },
                "response_preview": error_response.get("content", "")[:150] + "..." if len(error_response.get("content", "")) > 150 else error_response.get("content", "")
            })
            
            # Test 5: Creative Task
            logger.info("  🎨 Testing creative task...")
            creative_response = await client.generate(
                prompt=self.test_prompts["creative_task"],
                temperature=0.9,
                max_tokens=150
            )
            
            maverick_results["tests"].append({
                "test": "creative_task",
                "status": "passed" if creative_response.get("content") else "failed",
                "result": {
                    "content_length": len(creative_response.get("content", "")),
                    "tokens_used": creative_response.get("tokens_used", 0)
                },
                "response_preview": creative_response.get("content", "")[:200] + "..." if len(creative_response.get("content", "")) > 200 else creative_response.get("content", "")
            })
            
            # Test 6: Batch Generation
            logger.info("  📦 Testing batch generation...")
            try:
                batch_prompts = [
                    "What is Python?",
                    "What is JavaScript?",
                    "What is machine learning?"
                ]
                batch_responses = await client.batch_generate(
                    prompts=batch_prompts,
                    temperature=0.7,
                    max_tokens=50
                )
                
                maverick_results["tests"].append({
                    "test": "batch_generation",
                    "status": "passed" if len(batch_responses) == len(batch_prompts) else "failed",
                    "result": {
                        "input_prompts": len(batch_prompts),
                        "output_responses": len(batch_responses),
                        "responses": [{"content": r.get("content", "")[:50] + "..." if len(r.get("content", "")) > 50 else r.get("content", "")} for r in batch_responses]
                    }
                })
            except Exception as e:
                maverick_results["tests"].append({
                    "test": "batch_generation",
                    "status": "failed",
                    "error": str(e)
                })
            
            await client.unload_model()
            maverick_results["status"] = "passed"
            
        except Exception as e:
            logger.error(f"❌ Maverick testing failed: {e}")
            maverick_results["status"] = "failed"
            maverick_results["errors"].append(str(e))
        
        return maverick_results
    
    async def test_unified_service(self) -> Dict[str, Any]:
        """Test the unified LLM service"""
        logger.info("🔍 Testing Unified LLM Service...")
        unified_results = {"status": "testing", "tests": [], "errors": []}
        
        try:
            # Create a mock database session (simplified for testing)
            db = next(get_db())
            
            # Create a mock user
            mock_user = UserResponse(
                id=1,
                email="test@example.com",
                full_name="Test User",
                subscription_tier=SubscriptionTier.PRO,
                is_active=True
            )
            
            service = UnifiedLLMService(db)
            
            # Test 1: Chat Task
            logger.info("  💬 Testing chat task...")
            chat_request = LLMRequest(
                task=LLMTask.CHAT,
                prompt=self.test_prompts["simple_chat"],
                stream=False
            )
            
            start_time = time.time()
            chat_response = await service.generate_response(chat_request, mock_user, db)
            chat_time = time.time() - start_time
            
            unified_results["tests"].append({
                "test": "chat_task",
                "status": "passed" if hasattr(chat_response, 'content') and chat_response.content else "failed",
                "result": {
                    "content_length": len(chat_response.content) if hasattr(chat_response, 'content') else 0,
                    "generation_time": round(chat_time, 2),
                    "model_used": getattr(chat_response, 'model', 'unknown')
                },
                "response_preview": chat_response.content[:100] + "..." if hasattr(chat_response, 'content') and len(chat_response.content) > 100 else getattr(chat_response, 'content', "")
            })
            
            # Test 2: Log Analysis Task
            logger.info("  🔍 Testing log analysis task...")
            log_request = LLMRequest(
                task=LLMTask.LOG_ANALYSIS,
                prompt=self.test_prompts["log_analysis"],
                stream=False
            )
            
            log_response = await service.generate_response(log_request, mock_user, db)
            
            unified_results["tests"].append({
                "test": "log_analysis_task",
                "status": "passed" if hasattr(log_response, 'content') and log_response.content else "failed",
                "result": {
                    "content_length": len(log_response.content) if hasattr(log_response, 'content') else 0,
                    "model_used": getattr(log_response, 'model', 'unknown')
                },
                "response_preview": log_response.content[:150] + "..." if hasattr(log_response, 'content') and len(log_response.content) > 150 else getattr(log_response, 'content', "")
            })
            
            # Test 3: Error Detection Task
            logger.info("  🚨 Testing error detection task...")
            error_request = LLMRequest(
                task=LLMTask.ERROR_DETECTION,
                prompt=self.test_prompts["error_detection"],
                stream=False
            )
            
            error_response = await service.generate_response(error_request, mock_user, db)
            
            unified_results["tests"].append({
                "test": "error_detection_task",
                "status": "passed" if hasattr(error_response, 'content') and error_response.content else "failed",
                "result": {
                    "content_length": len(error_response.content) if hasattr(error_response, 'content') else 0,
                    "model_used": getattr(error_response, 'model', 'unknown')
                },
                "response_preview": error_response.content[:150] + "..." if hasattr(error_response, 'content') and len(error_response.content) > 150 else getattr(error_response, 'content', "")
            })
            
            unified_results["status"] = "passed"
            
        except Exception as e:
            logger.error(f"❌ Unified service testing failed: {e}")
            unified_results["status"] = "failed"
            unified_results["errors"].append(str(e))
        
        return unified_results
    
    async def run_all_tests(self):
        """Run all AI model tests"""
        logger.info("🚀 Starting AI Models Testing...")
        logger.info("=" * 60)
        
        # Test Ollama
        self.test_results["ollama"] = await self.test_ollama_client()
        
        # Test Maverick
        self.test_results["maverick"] = await self.test_maverick_client()
        
        # Test Unified Service
        self.test_results["unified_service"] = await self.test_unified_service()
        
        # Generate summary
        self._generate_summary()
        
        # Save results
        await self._save_results()
        
        # Print summary
        self._print_summary()
    
    def _generate_summary(self):
        """Generate test summary"""
        ollama_passed = self.test_results["ollama"]["status"] == "passed"
        maverick_passed = self.test_results["maverick"]["status"] == "passed"
        unified_passed = self.test_results["unified_service"]["status"] == "passed"
        
        total_tests = 0
        passed_tests = 0
        
        for service in ["ollama", "maverick", "unified_service"]:
            service_data = self.test_results[service]
            if "tests" in service_data:
                for test in service_data["tests"]:
                    total_tests += 1
                    if test["status"] == "passed":
                        passed_tests += 1
        
        self.test_results["summary"] = {
            "total_services": 3,
            "working_services": sum([ollama_passed, maverick_passed, unified_passed]),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0,
            "ollama_working": ollama_passed,
            "maverick_working": maverick_passed,
            "unified_service_working": unified_passed,
            "overall_status": "PASS" if (ollama_passed or maverick_passed) and unified_passed else "FAIL"
        }
    
    async def _save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_models_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"📄 Test results saved to: {filename}")
    
    def _print_summary(self):
        """Print test summary"""
        summary = self.test_results["summary"]
        
        print("\n" + "=" * 60)
        print("🎯 AI MODELS TESTING SUMMARY")
        print("=" * 60)
        
        print(f"📊 Overall Status: {'✅ PASS' if summary['overall_status'] == 'PASS' else '❌ FAIL'}")
        print(f"🔧 Working Services: {summary['working_services']}/{summary['total_services']}")
        print(f"🧪 Tests Passed: {summary['passed_tests']}/{summary['total_tests']} ({summary['success_rate']}%)")
        
        print("\n📋 Service Status:")
        print(f"  🤖 Ollama (Local): {'✅ Working' if summary['ollama_working'] else '❌ Failed'}")
        print(f"  🚀 Maverick (Cloud): {'✅ Working' if summary['maverick_working'] else '❌ Failed'}")
        print(f"  🔗 Unified Service: {'✅ Working' if summary['unified_service_working'] else '❌ Failed'}")
        
        print("\n💡 Recommendations:")
        if not summary['ollama_working']:
            print("  • Check if Ollama is installed and running")
            print("  • Verify Ollama service is accessible at configured URL")
        if not summary['maverick_working']:
            print("  • Check system memory (requires 16GB+ RAM)")
            print("  • Verify CUDA/GPU availability for optimal performance")
        if not summary['unified_service_working']:
            print("  • Check database connection")
            print("  • Verify service configuration")
        
        print("\n" + "=" * 60)

async def main():
    """Main testing function"""
    tester = AIModelTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
