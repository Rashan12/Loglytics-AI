#!/usr/bin/env python3
"""
Test the REAL system end-to-end
"""
import requests
import json

print("=" * 60)
print("TESTING REAL SYSTEM END-TO-END")
print("=" * 60)

# Test 1: Backend health
print("\n1. Testing backend health...")
try:
    response = requests.get("http://localhost:8000/")
    print(f"   Backend status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ERROR: Backend not responding: {e}")
    exit(1)

# Test 2: Login
print("\n2. Testing login...")
try:
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "rashandissanayaka@gmail.com", "password": "Rashan@12"}
    )
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print(f"   SUCCESS: Got token: {token[:50]}...")
        
        # Test 3: Project chat with form data
        print("\n3. Testing project chat...")
        headers = {"Authorization": f"Bearer {token}"}
        form_data = {"message": "Hello, this is a real test message"}
        
        chat_response = requests.post(
            "http://localhost:8000/api/v1/projects/d90e0b24-bb39-4c6d-9bec-19c7a3bf76a1/chat",
            data=form_data,
            headers=headers
        )
        
        print(f"   Chat status: {chat_response.status_code}")
        print(f"   Chat response: {chat_response.text}")
        
        if chat_response.status_code == 200:
            print("   SUCCESS: Chat endpoint working!")
        else:
            print("   ERROR: Chat endpoint failed")
            
    else:
        print(f"   ERROR: Login failed: {login_response.text}")
        
except Exception as e:
    print(f"   ERROR: Login test failed: {e}")

print("\n" + "=" * 60)
print("REAL SYSTEM TEST COMPLETE")
print("=" * 60)
