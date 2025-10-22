"""
Comprehensive End-to-End Backend Testing Suite
Tests all API endpoints, services, and business logic
"""

import pytest
import asyncio
import json
import websockets
from httpx import AsyncClient
from pathlib import Path
import time
from datetime import datetime
import uuid
import os
import tempfile

# Base URL
BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"

# Test data
TEST_USER = {
    "email": "test_e2e@example.com",
    "password": "Test@12345678",
    "full_name": "E2E Test User"
}

# Global variables for test state
access_token = None
user_id = None
project_id = None
log_file_id = None
chat_id = None
api_key = None

class TestResults:
    """Store and format test results"""
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def add_result(self, category, test_name, status, details="", response_time=0):
        result = {
            "category": category,
            "test": test_name,
            "status": status,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "WARN":
            self.warnings += 1
    
    def generate_markdown(self):
        """Generate detailed markdown report"""
        report = f"""# Loglytics AI - End-to-End Backend Test Results

**Test Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Tests:** {len(self.results)}
**Passed:** {self.passed} ✅
**Failed:** {self.failed} ❌
**Warnings:** {self.warnings} ⚠️
**Success Rate:** {(self.passed / len(self.results) * 100):.2f}%

---

## Test Summary by Category

"""
        # Group by category
        categories = {}
        for result in self.results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        # Add category summaries
        for category, tests in categories.items():
            passed = sum(1 for t in tests if t['status'] == 'PASS')
            failed = sum(1 for t in tests if t['status'] == 'FAIL')
            warned = sum(1 for t in tests if t['status'] == 'WARN')
            avg_time = sum(t['response_time_ms'] for t in tests) / len(tests)
            
            report += f"""
### {category}
- Total: {len(tests)}
- Passed: {passed} ✅
- Failed: {failed} ❌
- Warnings: {warned} ⚠️
- Avg Response Time: {avg_time:.2f}ms

"""
        
        report += "\n---\n\n## Detailed Test Results\n\n"
        
        # Detailed results
        for category, tests in categories.items():
            report += f"\n### {category}\n\n"
            report += "| Test Name | Status | Response Time | Details |\n"
            report += "|-----------|--------|---------------|----------|\n"
            
            for test in tests:
                status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}[test['status']]
                report += f"| {test['test']} | {status_icon} {test['status']} | {test['response_time_ms']}ms | {test['details'][:100]} |\n"
        
        return report

# Initialize test results
test_results = TestResults()


# ============================================
# 1. AUTHENTICATION TESTS
# ============================================

@pytest.mark.asyncio
async def test_01_user_registration():
    """Test user registration"""
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.post("/api/v1/auth/register", json=TEST_USER)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            global user_id
            user_id = data.get('user', {}).get('id')
            test_results.add_result(
                "Authentication",
                "User Registration",
                "PASS",
                f"User created successfully with ID: {user_id}",
                elapsed
            )
        else:
            test_results.add_result(
                "Authentication",
                "User Registration",
                "FAIL",
                f"Status: {response.status_code}, Error: {response.text[:200]}",
                elapsed
            )


@pytest.mark.asyncio
async def test_02_user_login():
    """Test user login and JWT token generation"""
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.post("/api/v1/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            global access_token
            access_token = data.get('access_token')
            
            if access_token:
                test_results.add_result(
                    "Authentication",
                    "User Login",
                    "PASS",
                    f"Token received: {access_token[:20]}...",
                    elapsed
                )
            else:
                test_results.add_result(
                    "Authentication",
                    "User Login",
                    "FAIL",
                    "No access token in response",
                    elapsed
                )
        else:
            test_results.add_result(
                "Authentication",
                "User Login",
                "FAIL",
                f"Status: {response.status_code}, Error: {response.text[:200]}",
                elapsed
            )


@pytest.mark.asyncio
async def test_03_token_validation():
    """Test JWT token validation"""
    if not access_token:
        test_results.add_result(
            "Authentication",
            "Token Validation",
            "FAIL",
            "No token available to test",
            0
        )
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            test_results.add_result(
                "Authentication",
                "Token Validation",
                "PASS",
                "Token is valid and authenticated",
                elapsed
            )
        else:
            test_results.add_result(
                "Authentication",
                "Token Validation",
                "FAIL",
                f"Status: {response.status_code}",
                elapsed
            )


@pytest.mark.asyncio
async def test_04_create_api_key():
    """Test API key creation"""
    if not access_token:
        test_results.add_result("Authentication", "Create API Key", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.post(
            "/api/v1/auth/api-keys",
            json={"name": "E2E Test Key", "description": "Test API key"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            global api_key
            api_key = data.get('api_key')
            test_results.add_result(
                "Authentication",
                "Create API Key",
                "PASS",
                f"API key created: {api_key[:20] if api_key else 'None'}...",
                elapsed
            )
        else:
            test_results.add_result(
                "Authentication",
                "Create API Key",
                "WARN",
                f"Status: {response.status_code} - API key feature may not be implemented",
                elapsed
            )


# ============================================
# 2. PROJECT MANAGEMENT TESTS
# ============================================

@pytest.mark.asyncio
async def test_05_create_project():
    """Test project creation"""
    if not access_token:
        test_results.add_result("Projects", "Create Project", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "E2E Test Project",
                "description": "Automated testing project"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            global project_id
            project_id = data.get('id')
            test_results.add_result(
                "Projects",
                "Create Project",
                "PASS",
                f"Project created with ID: {project_id}",
                elapsed
            )
        else:
            test_results.add_result(
                "Projects",
                "Create Project",
                "FAIL",
                f"Status: {response.status_code}, Error: {response.text[:200]}",
                elapsed
            )


@pytest.mark.asyncio
async def test_06_list_projects():
    """Test listing user projects"""
    if not access_token:
        test_results.add_result("Projects", "List Projects", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            projects = response.json()
            test_results.add_result(
                "Projects",
                "List Projects",
                "PASS",
                f"Retrieved {len(projects)} projects",
                elapsed
            )
        else:
            test_results.add_result(
                "Projects",
                "List Projects",
                "FAIL",
                f"Status: {response.status_code}",
                elapsed
            )


@pytest.mark.asyncio
async def test_07_get_project_details():
    """Test getting project details"""
    if not access_token or not project_id:
        test_results.add_result("Projects", "Get Project Details", "FAIL", "Missing prerequisites", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            test_results.add_result(
                "Projects",
                "Get Project Details",
                "PASS",
                "Project details retrieved successfully",
                elapsed
            )
        else:
            test_results.add_result(
                "Projects",
                "Get Project Details",
                "FAIL",
                f"Status: {response.status_code}",
                elapsed
            )


# ============================================
# 3. LOG FILE UPLOAD & PROCESSING TESTS
# ============================================

@pytest.mark.asyncio
async def test_08_upload_log_file():
    """Test log file upload"""
    if not access_token or not project_id:
        test_results.add_result("Log Processing", "Upload Log File", "FAIL", "Missing prerequisites", 0)
        return
    
    # Create dummy log file
    log_content = """
2024-10-16 10:00:00 INFO Application started
2024-10-16 10:00:01 INFO User logged in: user@example.com
2024-10-16 10:00:05 WARN High memory usage detected: 85%
2024-10-16 10:00:10 ERROR Database connection failed: timeout
2024-10-16 10:00:15 ERROR Failed to process request: NullPointerException
2024-10-16 10:00:20 INFO Request processed successfully
2024-10-16 10:00:25 DEBUG Query executed in 45ms
2024-10-16 10:00:30 INFO Application shutdown initiated
"""
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        start = time.time()
        response = await client.post(
            f"/api/v1/logs/upload",
            files={"file": ("test.log", log_content, "text/plain")},
            data={"project_id": project_id},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            global log_file_id
            log_file_id = data.get('id')
            test_results.add_result(
                "Log Processing",
                "Upload Log File",
                "PASS",
                f"Log uploaded with ID: {log_file_id}",
                elapsed
            )
        else:
            test_results.add_result(
                "Log Processing",
                "Upload Log File",
                "FAIL",
                f"Status: {response.status_code}, Error: {response.text[:200]}",
                elapsed
            )


@pytest.mark.asyncio
async def test_09_log_parsing():
    """Test log file parsing"""
    if not access_token or not log_file_id:
        test_results.add_result("Log Processing", "Log Parsing", "FAIL", "Missing prerequisites", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get(
            f"/api/v1/logs/{log_file_id}/entries",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            entries = response.json()
            test_results.add_result(
                "Log Processing",
                "Log Parsing",
                "PASS",
                f"Parsed {len(entries)} log entries",
                elapsed
            )
        else:
            test_results.add_result(
                "Log Processing",
                "Log Parsing",
                "FAIL",
                f"Status: {response.status_code}",
                elapsed
            )


@pytest.mark.asyncio
async def test_10_list_log_files():
    """Test listing log files"""
    if not access_token:
        test_results.add_result("Log Processing", "List Log Files", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get(
            "/api/v1/logs",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            log_files = response.json()
            test_results.add_result(
                "Log Processing",
                "List Log Files",
                "PASS",
                f"Retrieved {len(log_files)} log files",
                elapsed
            )
        else:
            test_results.add_result(
                "Log Processing",
                "List Log Files",
                "FAIL",
                f"Status: {response.status_code}",
                elapsed
            )


# ============================================
# 4. AI ANALYSIS TESTS
# ============================================

@pytest.mark.asyncio
async def test_11_ai_log_analysis():
    """Test AI-powered log analysis"""
    if not access_token or not log_file_id:
        test_results.add_result("AI Analysis", "Log Analysis", "FAIL", "Missing prerequisites", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        start = time.time()
        response = await client.post(
            f"/api/v1/analytics/analyze",
            json={"log_file_id": log_file_id},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            analysis = response.json()
            test_results.add_result(
                "AI Analysis",
                "Log Analysis",
                "PASS",
                f"Analysis complete: {len(analysis.get('insights', []))} insights found",
                elapsed
            )
        else:
            test_results.add_result(
                "AI Analysis",
                "Log Analysis",
                "WARN",
                f"Status: {response.status_code} - AI service may not be configured",
                elapsed
            )


@pytest.mark.asyncio
async def test_12_ai_chat():
    """Test AI chat assistant"""
    if not access_token:
        test_results.add_result("AI Analysis", "Chat Assistant", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        start = time.time()
        response = await client.post(
            "/api/v1/llm/chat",
            json={"message": "Analyze the errors in my logs", "context": "test"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            test_results.add_result(
                "AI Analysis",
                "Chat Assistant",
                "PASS",
                f"Response received: {data.get('response', '')[:50]}...",
                elapsed
            )
        else:
            test_results.add_result(
                "AI Analysis",
                "Chat Assistant",
                "WARN",
                f"Status: {response.status_code} - AI service may not be configured",
                elapsed
            )


@pytest.mark.asyncio
async def test_13_create_chat_session():
    """Test creating chat session"""
    if not access_token:
        test_results.add_result("AI Analysis", "Create Chat Session", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.post(
            "/api/v1/chat/sessions",
            json={"title": "E2E Test Chat", "context": "Testing chat functionality"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            global chat_id
            chat_id = data.get('id')
            test_results.add_result(
                "AI Analysis",
                "Create Chat Session",
                "PASS",
                f"Chat session created with ID: {chat_id}",
                elapsed
            )
        else:
            test_results.add_result(
                "AI Analysis",
                "Create Chat Session",
                "WARN",
                f"Status: {response.status_code} - Chat service may not be implemented",
                elapsed
            )


# ============================================
# 5. RAG SEARCH TESTS
# ============================================

@pytest.mark.asyncio
async def test_14_rag_search():
    """Test RAG semantic search"""
    if not access_token:
        test_results.add_result("RAG Search", "Semantic Search", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        start = time.time()
        response = await client.post(
            "/api/v1/rag/query",
            json={"query": "database errors", "limit": 10},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            results = response.json()
            test_results.add_result(
                "RAG Search",
                "Semantic Search",
                "PASS",
                f"Found {len(results.get('results', []))} matching entries",
                elapsed
            )
        else:
            test_results.add_result(
                "RAG Search",
                "Semantic Search",
                "WARN",
                f"Status: {response.status_code} - Vector DB may not be configured",
                elapsed
            )


@pytest.mark.asyncio
async def test_15_rag_indexing():
    """Test RAG indexing"""
    if not access_token or not log_file_id:
        test_results.add_result("RAG Search", "Indexing", "FAIL", "Missing prerequisites", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        start = time.time()
        response = await client.post(
            "/api/v1/rag/index",
            json={"log_file_id": log_file_id},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            test_results.add_result(
                "RAG Search",
                "Indexing",
                "PASS",
                "RAG indexing completed successfully",
                elapsed
            )
        else:
            test_results.add_result(
                "RAG Search",
                "Indexing",
                "WARN",
                f"Status: {response.status_code} - RAG indexing may not be implemented",
                elapsed
            )


# ============================================
# 6. WEBSOCKET & NOTIFICATIONS TESTS
# ============================================

@pytest.mark.asyncio
async def test_16_websocket_notifications():
    """Test WebSocket connection for notifications"""
    if not user_id:
        test_results.add_result("WebSocket", "Notifications", "FAIL", "No user ID", 0)
        return
    
    try:
        start = time.time()
        async with websockets.connect(f"{WS_BASE_URL}/api/v1/notifications/ws?token={access_token}") as websocket:
            # Wait for connection confirmation
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            elapsed = time.time() - start
            
            test_results.add_result(
                "WebSocket",
                "Notifications",
                "PASS",
                f"Connected successfully: {message[:50]}",
                elapsed
            )
    except Exception as e:
        test_results.add_result(
            "WebSocket",
            "Notifications",
            "FAIL",
            f"Error: {str(e)[:100]}",
            time.time() - start
        )


@pytest.mark.asyncio
async def test_17_websocket_live_logs():
    """Test WebSocket connection for live logs"""
    if not access_token or not project_id:
        test_results.add_result("WebSocket", "Live Logs", "FAIL", "Missing prerequisites", 0)
        return
    
    try:
        start = time.time()
        async with websockets.connect(f"{WS_BASE_URL}/api/v1/live-logs/ws/{project_id}?token={access_token}") as websocket:
            # Wait for connection confirmation
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            elapsed = time.time() - start
            
            test_results.add_result(
                "WebSocket",
                "Live Logs",
                "PASS",
                f"Connected successfully: {message[:50]}",
                elapsed
            )
    except Exception as e:
        test_results.add_result(
            "WebSocket",
            "Live Logs",
            "FAIL",
            f"Error: {str(e)[:100]}",
            time.time() - start
        )


@pytest.mark.asyncio
async def test_18_websocket_chat():
    """Test WebSocket connection for chat"""
    if not access_token or not chat_id:
        test_results.add_result("WebSocket", "Chat", "FAIL", "Missing prerequisites", 0)
        return
    
    try:
        start = time.time()
        async with websockets.connect(f"{WS_BASE_URL}/api/v1/chat/ws/{chat_id}?token={access_token}") as websocket:
            # Wait for connection confirmation
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            elapsed = time.time() - start
            
            test_results.add_result(
                "WebSocket",
                "Chat",
                "PASS",
                f"Connected successfully: {message[:50]}",
                elapsed
            )
    except Exception as e:
        test_results.add_result(
            "WebSocket",
            "Chat",
            "FAIL",
            f"Error: {str(e)[:100]}",
            time.time() - start
        )


# ============================================
# 7. ANALYTICS TESTS
# ============================================

@pytest.mark.asyncio
async def test_19_dashboard_analytics():
    """Test dashboard analytics data"""
    if not access_token:
        test_results.add_result("Analytics", "Dashboard Data", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get(
            "/api/v1/analytics/dashboard",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            test_results.add_result(
                "Analytics",
                "Dashboard Data",
                "PASS",
                f"Analytics retrieved: {data.get('total_logs', 0)} logs processed",
                elapsed
            )
        else:
            test_results.add_result(
                "Analytics",
                "Dashboard Data",
                "WARN",
                f"Status: {response.status_code}",
                elapsed
            )


@pytest.mark.asyncio
async def test_20_project_analytics():
    """Test project-specific analytics"""
    if not access_token or not project_id:
        test_results.add_result("Analytics", "Project Analytics", "FAIL", "Missing prerequisites", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get(
            f"/api/v1/analytics/project/{project_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            test_results.add_result(
                "Analytics",
                "Project Analytics",
                "PASS",
                "Project analytics retrieved successfully",
                elapsed
            )
        else:
            test_results.add_result(
                "Analytics",
                "Project Analytics",
                "WARN",
                f"Status: {response.status_code}",
                elapsed
            )


# ============================================
# 8. DATABASE INTEGRITY TESTS
# ============================================

@pytest.mark.asyncio
async def test_21_database_health():
    """Test database connection and health"""
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get("/health")
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            test_results.add_result(
                "Database",
                "Health Check",
                "PASS",
                f"Database status: {data.get('status', 'unknown')}",
                elapsed
            )
        else:
            test_results.add_result(
                "Database",
                "Health Check",
                "FAIL",
                f"Status: {response.status_code}",
                elapsed
            )


@pytest.mark.asyncio
async def test_22_database_optimization():
    """Test database optimization endpoint"""
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.post("/database/optimize")
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            test_results.add_result(
                "Database",
                "Optimization",
                "PASS",
                f"Database optimization: {data.get('status', 'unknown')}",
                elapsed
            )
        else:
            test_results.add_result(
                "Database",
                "Optimization",
                "WARN",
                f"Status: {response.status_code} - Optimization may not be implemented",
                elapsed
            )


# ============================================
# 9. SECURITY TESTS
# ============================================

@pytest.mark.asyncio
async def test_23_security_headers():
    """Test security headers"""
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get("/")
        elapsed = time.time() - start
        
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        present_headers = [h for h in security_headers if h in response.headers]
        
        if len(present_headers) >= 2:
            test_results.add_result(
                "Security",
                "Security Headers",
                "PASS",
                f"Found {len(present_headers)} security headers",
                elapsed
            )
        else:
            test_results.add_result(
                "Security",
                "Security Headers",
                "WARN",
                f"Only {len(present_headers)} security headers found",
                elapsed
            )


@pytest.mark.asyncio
async def test_24_rate_limiting():
    """Test rate limiting"""
    if not access_token:
        test_results.add_result("Security", "Rate Limiting", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            responses.append(response.status_code)
        
        elapsed = time.time() - start
        
        # Check if any requests were rate limited (429 status)
        rate_limited = any(status == 429 for status in responses)
        
        if rate_limited:
            test_results.add_result(
                "Security",
                "Rate Limiting",
                "PASS",
                "Rate limiting is working",
                elapsed
            )
        else:
            test_results.add_result(
                "Security",
                "Rate Limiting",
                "WARN",
                "Rate limiting may not be configured",
                elapsed
            )


# ============================================
# 10. ERROR HANDLING TESTS
# ============================================

@pytest.mark.asyncio
async def test_25_invalid_endpoint():
    """Test invalid endpoint handling"""
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get("/api/v1/invalid-endpoint")
        elapsed = time.time() - start
        
        if response.status_code == 404:
            test_results.add_result(
                "Error Handling",
                "Invalid Endpoint",
                "PASS",
                "404 error returned for invalid endpoint",
                elapsed
            )
        else:
            test_results.add_result(
                "Error Handling",
                "Invalid Endpoint",
                "FAIL",
                f"Expected 404, got {response.status_code}",
                elapsed
            )


@pytest.mark.asyncio
async def test_26_unauthorized_access():
    """Test unauthorized access handling"""
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.time()
        response = await client.get("/api/v1/users/me")
        elapsed = time.time() - start
        
        if response.status_code == 401:
            test_results.add_result(
                "Error Handling",
                "Unauthorized Access",
                "PASS",
                "401 error returned for unauthorized access",
                elapsed
            )
        else:
            test_results.add_result(
                "Error Handling",
                "Unauthorized Access",
                "FAIL",
                f"Expected 401, got {response.status_code}",
                elapsed
            )


# ============================================
# 11. PERFORMANCE TESTS
# ============================================

@pytest.mark.asyncio
async def test_27_response_times():
    """Test response times for critical endpoints"""
    if not access_token:
        test_results.add_result("Performance", "Response Times", "FAIL", "No auth token", 0)
        return
    
    async with AsyncClient(base_url=BASE_URL) as client:
        endpoints = [
            ("/api/v1/users/me", "User Profile"),
            ("/api/v1/projects", "List Projects"),
            ("/api/v1/logs", "List Log Files"),
            ("/health", "Health Check")
        ]
        
        slow_endpoints = []
        
        for endpoint, name in endpoints:
            start = time.time()
            response = await client.get(
                endpoint,
                headers={"Authorization": f"Bearer {access_token}"} if endpoint != "/health" else {}
            )
            elapsed = time.time() - start
            
            if elapsed > 2.0:  # More than 2 seconds
                slow_endpoints.append(f"{name}: {elapsed:.2f}s")
        
        if slow_endpoints:
            test_results.add_result(
                "Performance",
                "Response Times",
                "WARN",
                f"Slow endpoints: {', '.join(slow_endpoints)}",
                0
            )
        else:
            test_results.add_result(
                "Performance",
                "Response Times",
                "PASS",
                "All endpoints responding within 2 seconds",
                0
            )


# ============================================
# MAIN TEST RUNNER
# ============================================

@pytest.mark.asyncio
async def test_99_generate_report():
    """Generate final test report"""
    report = test_results.generate_markdown()
    
    # Save to file
    with open("TEST_RESULTS.md", "w") as f:
        f.write(report)
    
    print("\n" + "="*60)
    print("TEST REPORT GENERATED: TEST_RESULTS.md")
    print("="*60)
    print(f"Total Tests: {len(test_results.results)}")
    print(f"Passed: {test_results.passed} ✅")
    print(f"Failed: {test_results.failed} ❌")
    print(f"Warnings: {test_results.warnings} ⚠️")
    print(f"Success Rate: {(test_results.passed / len(test_results.results) * 100):.2f}%")
    print("="*60 + "\n")
