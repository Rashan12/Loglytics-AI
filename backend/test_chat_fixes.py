#!/usr/bin/env python3
"""
Test script for chat functionality fixes
Tests the endpoints and basic functionality
"""

import asyncio
import aiohttp
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

async def test_chat_endpoints():
    """Test the chat endpoints"""
    
    async with aiohttp.ClientSession() as session:
        print("Testing Chat Functionality Fixes")
        print("=" * 50)
        
        # Step 1: Login
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
        
        # Step 2: Test general chat endpoint
        print("\n2. Testing general chat endpoint...")
        try:
            data = aiohttp.FormData()
            data.add_field('message', 'Hello, this is a test message')
            
            async with session.post(f"{BASE_URL}/api/v1/chat/chat", data=data, headers=headers) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    print("SUCCESS: General chat endpoint working!")
                    print(f"   Response: {response.get('response', 'No response')[:100]}...")
                else:
                    error_text = await resp.text()
                    print(f"ERROR: General chat failed: {resp.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"ERROR: General chat error: {e}")
        
        # Step 3: Create a test project
        print("\n3. Creating test project...")
        project_data = {
            "name": "Chat Test Project",
            "description": "Testing chat functionality"
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
        
        # Step 4: Test project chat endpoint
        print("\n4. Testing project chat endpoint...")
        try:
            data = aiohttp.FormData()
            data.add_field('message', 'Hello from project chat')
            
            async with session.post(f"{BASE_URL}/api/v1/projects/{project_id}/chat", data=data, headers=headers) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    print("SUCCESS: Project chat endpoint working!")
                    print(f"   Response: {response.get('response', 'No response')[:100]}...")
                else:
                    error_text = await resp.text()
                    print(f"ERROR: Project chat failed: {resp.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"ERROR: Project chat error: {e}")
        
        print("\nChat Functionality Test Complete!")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_chat_endpoints())
