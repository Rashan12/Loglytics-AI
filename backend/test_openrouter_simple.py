#!/usr/bin/env python3
"""
Simple test for OpenRouter integration
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openrouter_direct():
    """Test OpenRouter API directly"""
    print("Testing OpenRouter API Directly")
    print("=" * 40)
    
    try:
        from app.services.chat_enhanced_service import enhanced_chat_service
        from app.schemas.chat_enhanced import ChatMessage
        
        print("Testing OpenRouter service...")
        
        # Test message
        test_message = "Hello! Can you help me analyze some log files? Please keep your response brief."
        test_history = [
            ChatMessage(role="user", content="Hi there"),
            ChatMessage(role="assistant", content="Hello! I'm here to help with log analysis.")
        ]
        
        # Test the service
        response = await enhanced_chat_service.chat(
            message=test_message,
            conversation_history=test_history
        )
        
        print("SUCCESS! OpenRouter service is working!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("Testing Environment Configuration")
    print("=" * 40)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-90b-vision-instruct")
    
    if not api_key or api_key == "your-openrouter-api-key-here":
        print("ERROR: OPENROUTER_API_KEY not set")
        return False
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Model: {model}")
    print("Environment configuration OK")
    return True

async def main():
    """Main test function"""
    print("OpenRouter Simple Test")
    print("=" * 30)
    
    # Test environment
    env_ok = test_environment()
    if not env_ok:
        print("Environment test failed")
        return 1
    
    # Test OpenRouter
    api_ok = await test_openrouter_direct()
    
    if api_ok:
        print("\nSUCCESS! OpenRouter integration is working!")
        print("\nNext steps:")
        print("1. Start the backend server")
        print("2. Test from frontend at http://localhost:3000")
        print("3. Navigate to AI Assistant page")
        return 0
    else:
        print("\nERROR: OpenRouter integration failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
