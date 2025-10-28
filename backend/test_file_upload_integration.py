#!/usr/bin/env python3
"""
Test script for file upload to processing pipeline integration
Tests the complete flow: Upload → Parse → RAG Index → LLM Query → Response
"""

import asyncio
import aiohttp
import json
import os
import tempfile
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

# Sample log content for testing
SAMPLE_LOG_CONTENT = """2024-01-15 10:30:15 INFO [UserService] User login successful for user_id=12345
2024-01-15 10:30:16 ERROR [DatabaseService] Connection timeout to database server
2024-01-15 10:30:17 WARN [CacheService] Cache miss for key=user_profile_12345
2024-01-15 10:30:18 INFO [AuthService] Token validation successful
2024-01-15 10:30:19 ERROR [PaymentService] Payment processing failed for order_id=67890
2024-01-15 10:30:20 INFO [NotificationService] Email sent to user@example.com
"""

async def test_file_upload_integration():
    """Test the complete file upload to processing pipeline"""
    
    async with aiohttp.ClientSession() as session:
        print("Testing File Upload to Processing Pipeline Integration")
        print("=" * 60)
        
        # Step 1: Login to get authentication token
        print("\n1. Testing Authentication...")
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/login", json=login_data) as resp:
                if resp.status == 200:
                    auth_data = await resp.json()
                    token = auth_data.get("access_token")
                    headers = {"Authorization": f"Bearer {token}"}
                    print("SUCCESS: Authentication successful")
                else:
                    print(f"ERROR: Authentication failed: {resp.status}")
                    return
        except Exception as e:
            print(f"ERROR: Authentication error: {e}")
            return
        
        # Step 2: Create a test project
        print("\n2. Creating test project...")
        project_data = {
            "name": "File Upload Test Project",
            "description": "Testing file upload integration"
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/v1/projects", json=project_data, headers=headers) as resp:
                if resp.status in [200, 201]:
                    project = await resp.json()
                    project_id = project["id"]
                    print(f"SUCCESS: Project created: {project_id}")
                else:
                    print(f"ERROR: Project creation failed: {resp.status}")
                    return
        except Exception as e:
            print(f"ERROR: Project creation error: {e}")
            return
        
        # Step 3: Create a test log file
        print("\n3. Creating test log file...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(SAMPLE_LOG_CONTENT)
            log_file_path = f.name
        
        print(f"SUCCESS: Test log file created: {log_file_path}")
        
        # Step 4: Test project chat with file upload
        print("\n4. Testing project chat with file upload...")
        
        try:
            # Prepare form data for file upload
            data = aiohttp.FormData()
            data.add_field('message', 'What errors occurred in the logs?')
            
            # Read file content and add to form data
            with open(log_file_path, 'rb') as f:
                file_content = f.read()
                data.add_field('file', file_content, filename='test.log', content_type='text/plain')
            
            async with session.post(
                f"{BASE_URL}/api/v1/projects/{project_id}/chat",
                data=data,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    print("SUCCESS: Project chat successful!")
                    print(f"   Response: {response.get('response', 'No response')[:100]}...")
                    print(f"   File processed: {response.get('file_processed', False)}")
                    print(f"   Chunks retrieved: {response.get('chunks_retrieved', 0)}")
                    print(f"   Confidence: {response.get('confidence', 0.0)}")
                else:
                    error_text = await resp.text()
                    print(f"ERROR: Project chat failed: {resp.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"ERROR: Project chat error: {e}")
        
        # Step 5: Test general chat with file upload
        print("\n5. Testing general chat with file upload...")
        
        try:
            # Create a chat session first
            chat_data = {"title": "File Upload Test Chat"}
            async with session.post(f"{BASE_URL}/api/v1/chats", json=chat_data, headers=headers) as resp:
                if resp.status in [200, 201]:
                    chat = await resp.json()
                    chat_id = chat["id"]
                    print(f"SUCCESS: Chat session created: {chat_id}")
                else:
                    print(f"ERROR: Chat creation failed: {resp.status}")
                    return
            
            # Send message with file upload
            data = aiohttp.FormData()
            data.add_field('message', 'Analyze the log patterns and identify issues')
            
            # Read file content and add to form data
            with open(log_file_path, 'rb') as f:
                file_content = f.read()
                data.add_field('file', file_content, filename='test.log', content_type='text/plain')
            
            async with session.post(
                f"{BASE_URL}/api/v1/chats/{chat_id}/messages",
                data=data,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    print("SUCCESS: General chat successful!")
                    print(f"   Response: {response.get('content', 'No response')[:100]}...")
                    print(f"   File processed: {response.get('file_processed', False)}")
                else:
                    error_text = await resp.text()
                    print(f"ERROR: General chat failed: {resp.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"ERROR: General chat error: {e}")
        
        # Step 6: Test RAG search functionality
        print("\n6. Testing RAG search functionality...")
        
        try:
            search_data = {
                "query": "database connection timeout",
                "project_id": project_id,
                "search_type": "semantic",
                "limit": 5,
                "similarity_threshold": 0.7
            }
            
            async with session.post(f"{BASE_URL}/api/v1/rag/search", json=search_data, headers=headers) as resp:
                if resp.status == 200:
                    search_results = await resp.json()
                    print("SUCCESS: RAG search successful!")
                    print(f"   Results: {len(search_results.get('results', []))} chunks found")
                    if search_results.get('results'):
                        print(f"   First result: {search_results['results'][0].get('content', '')[:100]}...")
                else:
                    error_text = await resp.text()
                    print(f"ERROR: RAG search failed: {resp.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"ERROR: RAG search error: {e}")
        
        # Cleanup
        print("\nCleaning up...")
        try:
            os.unlink(log_file_path)
            print("SUCCESS: Test log file removed")
        except:
            pass
        
        print("\nFile Upload Integration Test Complete!")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_file_upload_integration())
