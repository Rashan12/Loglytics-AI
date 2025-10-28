#!/usr/bin/env python3
"""
Test a simplified chat endpoint to isolate the 500 error
"""
import requests

# Get token
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "rashandissanayaka@gmail.com", "password": "Rashan@12"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"Token: {token[:50]}...")
    
    # Test with a simple message
    headers = {"Authorization": f"Bearer {token}"}
    form_data = {"message": "Hello, this is a test message"}
    
    print("Testing chat endpoint with simple message...")
    response = requests.post(
        "http://localhost:8000/api/v1/projects/d90e0b24-bb39-4c6d-9bec-19c7a3bf76a1/chat",
        data=form_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test with JSON instead of form data
    print("\nTesting with JSON data...")
    json_data = {"message": "Hello, this is a test message"}
    response2 = requests.post(
        "http://localhost:8000/api/v1/projects/d90e0b24-bb39-4c6d-9bec-19c7a3bf76a1/chat",
        json=json_data,
        headers=headers
    )
    
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text}")
    
else:
    print(f"Login failed: {login_response.status_code} - {login_response.text}")
