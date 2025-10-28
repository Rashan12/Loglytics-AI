#!/usr/bin/env python3
"""
Test chat endpoint with authentication
"""
import requests
import json

# Test login first
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "rashandissanayaka@gmail.com", "password": "Rashan@12"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"SUCCESS: Login successful, token: {token[:50]}...")
    
    # Test project chat
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    chat_response = requests.post(
        "http://localhost:8000/api/v1/projects/d90e0b24-bb39-4c6d-9bec-19c7a3bf76a1/chat",
        json={"message": "Hello, test message"},
        headers=headers
    )
    
    print(f"Chat response status: {chat_response.status_code}")
    print(f"Chat response: {chat_response.text}")
    
else:
    print(f"ERROR: Login failed: {login_response.status_code} - {login_response.text}")