#!/usr/bin/env python3
"""
Simple chat test to isolate the 500 error
"""
import requests

# Get token first
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "rashandissanayaka@gmail.com", "password": "Rashan@12"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"Token: {token[:50]}...")
    
    # Test with minimal data
    headers = {"Authorization": f"Bearer {token}"}
    form_data = {"message": "test"}
    
    print("Testing chat endpoint...")
    response = requests.post(
        "http://localhost:8000/api/v1/projects/d90e0b24-bb39-4c6d-9bec-19c7a3bf76a1/chat",
        data=form_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
else:
    print(f"Login failed: {login_response.status_code} - {login_response.text}")

