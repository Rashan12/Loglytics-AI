#!/usr/bin/env python3
"""
Test script for chat endpoints with OpenRouter integration
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_chat_endpoint():
    """Test the chat endpoint with OpenRouter"""
    print("Testing Chat Endpoint with OpenRouter")
    print("=" * 50)
    
    # Test data
    test_message = "Hello! Can you help me analyze some log files? Please keep your response brief."
    
    # Headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Data for the request
    data = {
        "message": test_message,
        "conversation_history": "[]"
    }
    
    try:
        print("Sending request to chat endpoint...")
        print(f"Message: {test_message}")
        
        # Make request to the enhanced chat endpoint
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            headers=headers,
            data=data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Chat endpoint is working!")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Conversation ID: {result.get('conversation_id', 'No ID')}")
            print(f"File Analyzed: {result.get('file_analyzed', False)}")
            return True
        else:
            print(f"ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend server")
        print("Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_chat_with_file():
    """Test chat endpoint with file upload"""
    print("\nTesting Chat Endpoint with File Upload")
    print("=" * 50)
    
    # Create a test log file
    test_log_content = """2024-01-15 10:30:15 INFO Application started
2024-01-15 10:30:16 INFO Database connection established
2024-01-15 10:30:17 ERROR Failed to load configuration
2024-01-15 10:30:18 WARN Using default configuration
2024-01-15 10:30:19 INFO Server listening on port 8080"""
    
    # Create test file
    test_file_path = "test_log.txt"
    with open(test_file_path, "w") as f:
        f.write(test_log_content)
    
    try:
        # Prepare file upload
        files = {
            "file": ("test_log.txt", open(test_file_path, "rb"), "text/plain")
        }
        
        data = {
            "message": "Analyze this log file and tell me about any errors you find.",
            "conversation_history": "[]"
        }
        
        print("Sending request with file upload...")
        print(f"File: {test_file_path}")
        print(f"Message: {data['message']}")
        
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! File upload chat is working!")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"File Analyzed: {result.get('file_analyzed', False)}")
            return True
        else:
            print(f"ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        if 'files' in locals():
            files['file'][1].close()

def test_server_health():
    """Test if the server is running"""
    print("Testing Server Health")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"Server Status: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Server is not running or not accessible")
        return False
    except Exception as e:
        print(f"Error checking server: {e}")
        return False

def main():
    """Main test function"""
    print("OpenRouter Chat Integration Test")
    print("=" * 50)
    
    # Test server health
    if not test_server_health():
        print("\nPlease start the backend server first:")
        print("cd backend")
        print("uvicorn app.main:app --reload")
        return 1
    
    # Test basic chat
    chat_ok = test_chat_endpoint()
    
    # Test chat with file upload
    file_ok = test_chat_with_file()
    
    # Summary
    print("\n" + "=" * 50)
    if chat_ok and file_ok:
        print("All tests passed! OpenRouter chat integration is working!")
        print("\nYou can now test from the frontend:")
        print("1. Go to http://localhost:3000")
        print("2. Navigate to AI Assistant page")
        print("3. Try sending a message or uploading a file")
        return 0
    else:
        print("Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
