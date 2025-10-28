#!/usr/bin/env python3
"""
Complete Fix Test - Verify all endpoints are working correctly
"""
import asyncio
import aiohttp
import json
import tempfile
import os

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

# Sample log content for testing
SAMPLE_LOG_CONTENT = """2024-01-15 10:30:15 INFO [UserService] User login successful: user_id=12345
2024-01-15 10:30:16 INFO [AuthService] Session created: session_id=abc123
2024-01-15 10:30:17 WARN [DatabaseService] Connection pool at 80% capacity
2024-01-15 10:30:18 ERROR [PaymentService] Payment processing failed: transaction_id=txn_456
2024-01-15 10:30:19 INFO [NotificationService] Email sent: user_id=12345
2024-01-15 10:30:20 ERROR [DatabaseService] Query timeout: query=SELECT * FROM users
2024-01-15 10:30:21 INFO [CacheService] Cache miss: key=user_profile_12345
2024-01-15 10:30:22 WARN [SecurityService] Multiple failed login attempts: ip=192.168.1.100
"""

async def test_complete_fix():
    """Test the complete fix for chat endpoints"""
    print("Testing Complete Fix for Chat Endpoints")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Test authentication
            print("\n1. Testing Authentication...")
            auth_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            async with session.post(f"{BASE_URL}/api/v1/auth/login", json=auth_data) as resp:
                if resp.status == 200:
                    auth_result = await resp.json()
                    token = auth_result.get("access_token")
                    headers = {"Authorization": f"Bearer {token}"}
                    print("SUCCESS: Authentication successful")
                else:
                    print(f"ERROR: Authentication failed: {resp.status}")
                    return
            
            # Step 2: Test project creation
            print("\n2. Creating test project...")
            project_data = {
                "name": "Test Project for Chat",
                "description": "Testing chat functionality"
            }
            
            async with session.post(f"{BASE_URL}/api/v1/projects", json=project_data, headers=headers) as resp:
                if resp.status in [200, 201]:
                    project_result = await resp.json()
                    project_id = project_result.get("id")
                    print(f"SUCCESS: Project created: {project_id}")
                else:
                    print(f"ERROR: Project creation failed: {resp.status}")
                    return
            
            # Step 3: Test project chat endpoint
            print("\n3. Testing project chat endpoint...")
            
            # Create a temporary log file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
                f.write(SAMPLE_LOG_CONTENT)
                temp_file_path = f.name
            
            try:
                # Test project chat with file upload
                data = aiohttp.FormData()
                data.add_field('message', 'Analyze this log file for errors')
                data.add_field('file', open(temp_file_path, 'rb'), filename='test.log', content_type='text/plain')
                
                async with session.post(f"{BASE_URL}/api/v1/projects/{project_id}/chat", data=data, headers=headers) as resp:
                    print(f"Project chat status: {resp.status}")
                    if resp.status == 200:
                        result = await resp.json()
                        print("SUCCESS: Project chat successful!")
                        print(f"   Response: {result.get('response', 'No response')}")
                        print(f"   File processed: {result.get('file_processed', False)}")
                        print(f"   Success: {result.get('success', False)}")
                    else:
                        error_text = await resp.text()
                        print(f"ERROR: Project chat failed: {resp.status}")
                        print(f"   Error: {error_text}")
                
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
            
            # Step 4: Test general chat endpoint
            print("\n4. Testing general chat endpoint...")
            
            # Create another temporary log file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
                f.write(SAMPLE_LOG_CONTENT)
                temp_file_path = f.name
            
            try:
                # Test general chat with file upload
                data = aiohttp.FormData()
                data.add_field('message', 'What errors are in this log?')
                data.add_field('file', open(temp_file_path, 'rb'), filename='test.log', content_type='text/plain')
                
                async with session.post(f"{BASE_URL}/api/v1/chat/chat", data=data, headers=headers) as resp:
                    print(f"General chat status: {resp.status}")
                    if resp.status == 200:
                        result = await resp.json()
                        print("SUCCESS: General chat successful!")
                        print(f"   Response: {result.get('response', 'No response')}")
                        print(f"   File processed: {result.get('file_processed', False)}")
                        print(f"   Success: {result.get('success', False)}")
                    else:
                        error_text = await resp.text()
                        print(f"ERROR: General chat failed: {resp.status}")
                        print(f"   Error: {error_text}")
                
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
            
            # Step 5: Test without file upload
            print("\n5. Testing chat without file upload...")
            
            # Test project chat without file
            data = aiohttp.FormData()
            data.add_field('message', 'Hello, can you help me analyze logs?')
            
            async with session.post(f"{BASE_URL}/api/v1/projects/{project_id}/chat", data=data, headers=headers) as resp:
                print(f"Project chat (no file) status: {resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    print("SUCCESS: Project chat (no file) successful!")
                    print(f"   Response: {result.get('response', 'No response')}")
                else:
                    error_text = await resp.text()
                    print(f"ERROR: Project chat (no file) failed: {resp.status}")
                    print(f"   Error: {error_text}")
            
            # Test general chat without file
            data = aiohttp.FormData()
            data.add_field('message', 'Hello, I need help with log analysis')
            
            async with session.post(f"{BASE_URL}/api/v1/chat/chat", data=data, headers=headers) as resp:
                print(f"General chat (no file) status: {resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    print("SUCCESS: General chat (no file) successful!")
                    print(f"   Response: {result.get('response', 'No response')}")
                else:
                    error_text = await resp.text()
                    print(f"ERROR: General chat (no file) failed: {resp.status}")
                    print(f"   Error: {error_text}")
            
            print("\n" + "=" * 50)
            print("Complete Fix Test Finished!")
            print("=" * 50)
            
        except Exception as e:
            print(f"ERROR: Test failed with exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_complete_fix())
