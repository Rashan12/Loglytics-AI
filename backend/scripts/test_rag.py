#!/usr/bin/env python3
"""
RAG System Test Script for Loglytics AI
Tests all RAG functionality including embedding, chunking, and retrieval
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

class RAGTester:
    """Test RAG system functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.access_token: str = None
        self.project_id: str = None
        
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
                "email": "ragtest@example.com",
                "username": "ragtest",
                "password": "TestPassword123!",
                "full_name": "RAG Test User",
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
                "username": "ragtest@example.com",
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
    
    async def create_test_project(self) -> bool:
        """Create a test project"""
        logger.info("📁 Creating test project...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            project_data = {
                "name": "RAG Test Project",
                "description": "Project for testing RAG functionality"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/projects",
                json=project_data,
                headers=headers
            )
            
            if response.status_code == 201:
                data = response.json()
                self.project_id = data["id"]
                logger.info(f"✅ Test project created: {self.project_id}")
                return True
            else:
                logger.error(f"❌ Project creation failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Project creation error: {e}")
            return False
    
    async def test_rag_health(self) -> bool:
        """Test RAG service health"""
        logger.info("🏥 Testing RAG health...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/rag/health",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ RAG health check passed")
                logger.info(f"   Overall healthy: {data.get('overall_healthy', False)}")
                return True
            else:
                logger.error(f"❌ RAG health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ RAG health check error: {e}")
            return False
    
    async def test_index_log_file(self) -> bool:
        """Test indexing a log file"""
        logger.info("📝 Testing log file indexing...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Sample log content
            log_content = """2024-01-15T10:30:45Z ERROR Database connection failed: timeout after 30s
2024-01-15T10:31:12Z WARN High memory usage: 85% of available memory
2024-01-15T10:31:45Z INFO User login successful: user_id=12345
2024-01-15T10:32:01Z ERROR HTTP 500 Internal Server Error - /api/users
2024-01-15T10:32:15Z INFO API request processed: GET /api/health
2024-01-15T10:32:30Z WARN Slow query detected: 5.2s execution time
2024-01-15T10:32:45Z ERROR Out of memory: Cannot allocate 1GB
2024-01-15T10:33:01Z INFO System backup completed successfully"""
            
            index_data = {
                "log_file_id": "test-log-001",
                "project_id": self.project_id,
                "content": log_content,
                "file_type": "standard"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/index",
                json=index_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Log file indexing successful")
                logger.info(f"   Chunks created: {data.get('chunks_created', 0)}")
                logger.info(f"   Vectors stored: {data.get('vectors_stored', 0)}")
                return True
            else:
                logger.error(f"❌ Log file indexing failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Log file indexing error: {e}")
            return False
    
    async def test_rag_query(self) -> bool:
        """Test RAG query"""
        logger.info("❓ Testing RAG query...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            query_data = {
                "question": "What errors are occurring in my system?",
                "project_id": self.project_id,
                "max_chunks": 5,
                "similarity_threshold": 0.7
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/query",
                json=query_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ RAG query successful")
                logger.info(f"   Answer: {data.get('answer', '')[:100]}...")
                logger.info(f"   Sources: {len(data.get('sources', []))}")
                logger.info(f"   Confidence: {data.get('confidence_score', 0):.2f}")
                return True
            else:
                logger.error(f"❌ RAG query failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ RAG query error: {e}")
            return False
    
    async def test_rag_query_with_filters(self) -> bool:
        """Test RAG query with metadata filters"""
        logger.info("🔍 Testing RAG query with filters...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            query_data = {
                "question": "Show me all ERROR level logs",
                "project_id": self.project_id,
                "filters": {
                    "log_level": "ERROR"
                },
                "max_chunks": 3,
                "similarity_threshold": 0.6
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/query",
                json=query_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ RAG query with filters successful")
                logger.info(f"   Answer: {data.get('answer', '')[:100]}...")
                logger.info(f"   Sources: {len(data.get('sources', []))}")
                return True
            else:
                logger.error(f"❌ RAG query with filters failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ RAG query with filters error: {e}")
            return False
    
    async def test_similarity_search(self) -> bool:
        """Test similarity search"""
        logger.info("🔍 Testing similarity search...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            search_data = {
                "query": "database connection timeout",
                "project_id": self.project_id,
                "search_type": "similar",
                "limit": 5,
                "similarity_threshold": 0.8
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/search",
                json=search_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Similarity search successful")
                logger.info(f"   Results: {data.get('total_results', 0)}")
                return True
            else:
                logger.error(f"❌ Similarity search failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Similarity search error: {e}")
            return False
    
    async def test_metadata_search(self) -> bool:
        """Test metadata search"""
        logger.info("📊 Testing metadata search...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            search_data = {
                "query": "metadata search",
                "project_id": self.project_id,
                "search_type": "metadata",
                "filters": {
                    "log_level": "ERROR"
                },
                "limit": 5
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/search",
                json=search_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Metadata search successful")
                logger.info(f"   Results: {data.get('total_results', 0)}")
                return True
            else:
                logger.error(f"❌ Metadata search failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Metadata search error: {e}")
            return False
    
    async def test_rag_stats(self) -> bool:
        """Test RAG statistics"""
        logger.info("📈 Testing RAG statistics...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/rag/stats/{self.project_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ RAG statistics successful")
                stats = data.get('statistics', {})
                if 'retrieval' in stats:
                    retrieval = stats['retrieval']
                    logger.info(f"   Total vectors: {retrieval.get('total_vectors', 0)}")
                    logger.info(f"   Log files: {retrieval.get('log_files', 0)}")
                return True
            else:
                logger.error(f"❌ RAG statistics failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ RAG statistics error: {e}")
            return False
    
    async def test_batch_indexing(self) -> bool:
        """Test batch indexing"""
        logger.info("📦 Testing batch indexing...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Sample log files
            log_files = [
                {
                    "log_file_id": "test-log-002",
                    "project_id": self.project_id,
                    "content": "2024-01-15T11:00:00Z INFO Application started\n2024-01-15T11:01:00Z WARN Low disk space: 90% full",
                    "file_type": "standard"
                },
                {
                    "log_file_id": "test-log-003",
                    "project_id": self.project_id,
                    "content": '{"timestamp":"2024-01-15T11:02:00Z","level":"ERROR","message":"Service unavailable","service":"api"}',
                    "file_type": "json"
                }
            ]
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/batch-index",
                json=log_files,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Batch indexing successful")
                logger.info(f"   Total files: {data.get('total_files', 0)}")
                logger.info(f"   Total chunks: {data.get('total_chunks', 0)}")
                logger.info(f"   Total vectors: {data.get('total_vectors', 0)}")
                return True
            else:
                logger.error(f"❌ Batch indexing failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Batch indexing error: {e}")
            return False
    
    async def test_reindexing(self) -> bool:
        """Test log file reindexing"""
        logger.info("🔄 Testing log file reindexing...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Updated log content
            updated_content = """2024-01-15T10:30:45Z ERROR Database connection failed: timeout after 30s
2024-01-15T10:31:12Z WARN High memory usage: 85% of available memory
2024-01-15T10:31:45Z INFO User login successful: user_id=12345
2024-01-15T10:32:01Z ERROR HTTP 500 Internal Server Error - /api/users
2024-01-15T10:32:15Z INFO API request processed: GET /api/health
2024-01-15T10:32:30Z WARN Slow query detected: 5.2s execution time
2024-01-15T10:32:45Z ERROR Out of memory: Cannot allocate 1GB
2024-01-15T10:33:01Z INFO System backup completed successfully
2024-01-15T10:33:15Z INFO New log entry added for testing"""
            
            reindex_data = {
                "project_id": self.project_id,
                "content": updated_content,
                "file_type": "standard"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/reindex/test-log-001",
                json=reindex_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Reindexing successful")
                logger.info(f"   Vectors deleted: {data.get('vectors_deleted', 0)}")
                logger.info(f"   Chunks created: {data.get('chunks_created', 0)}")
                return True
            else:
                logger.error(f"❌ Reindexing failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Reindexing error: {e}")
            return False
    
    async def test_clear_vectors(self) -> bool:
        """Test clearing project vectors"""
        logger.info("🗑️ Testing vector clearing...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.delete(
                f"{self.base_url}/api/v1/rag/clear/{self.project_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Vector clearing successful")
                logger.info(f"   Vectors deleted: {data.get('vectors_deleted', 0)}")
                return True
            else:
                logger.error(f"❌ Vector clearing failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Vector clearing error: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all RAG tests"""
        logger.info("🚀 Starting RAG System Tests")
        logger.info("=" * 50)
        
        # Authenticate first
        if not await self.authenticate():
            logger.error("❌ Authentication failed, cannot run tests")
            return False
        
        # Create test project
        if not await self.create_test_project():
            logger.error("❌ Project creation failed, cannot run tests")
            return False
        
        tests = [
            ("RAG Health Check", self.test_rag_health),
            ("Log File Indexing", self.test_index_log_file),
            ("RAG Query", self.test_rag_query),
            ("RAG Query with Filters", self.test_rag_query_with_filters),
            ("Similarity Search", self.test_similarity_search),
            ("Metadata Search", self.test_metadata_search),
            ("RAG Statistics", self.test_rag_stats),
            ("Batch Indexing", self.test_batch_indexing),
            ("Reindexing", self.test_reindexing),
            ("Vector Clearing", self.test_clear_vectors)
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
            logger.info("🎉 All tests passed! RAG system is working correctly.")
        else:
            logger.info("⚠️ Some tests failed. Please check the configuration and logs.")
        
        return passed == total

async def main():
    """Main test function"""
    base_url = "http://localhost:8000"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    logger.info(f"Testing RAG system at: {base_url}")
    
    async with RAGTester(base_url) as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
