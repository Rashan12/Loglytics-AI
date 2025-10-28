#!/usr/bin/env python3
"""
Test OpenRouter API Configuration
This script tests if the OpenRouter API is properly configured and working
"""

import os
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

async def test_openrouter_config():
    """Test OpenRouter configuration"""
    print("🔍 Testing OpenRouter API Configuration...")
    
    # Check environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-4-maverick-8b-instruct")
    
    print(f"API Key: {'✅ Configured' if api_key and api_key != 'your-openrouter-api-key-here' else '❌ Not configured'}")
    print(f"Model: {model}")
    
    if not api_key or api_key == "your-openrouter-api-key-here":
        print("❌ OPENROUTER_API_KEY not properly configured!")
        return False
    
    # Test OpenRouter client
    try:
        from app.services.llm.openrouter_client import OpenRouterClient
        
        client = OpenRouterClient()
        print("🧪 Testing OpenRouter client health check...")
        
        is_healthy = await client.health_check()
        print(f"Health check: {'✅ Passed' if is_healthy else '❌ Failed'}")
        
        if is_healthy:
            print("🧪 Testing actual API call...")
            response = await client.generate_response(
                prompt="Hello, this is a test message. Please respond with 'Test successful'.",
                max_tokens=50,
                temperature=0.7
            )
            print(f"✅ API Response: {response[:100]}...")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error testing OpenRouter: {e}")
        return False

async def test_llm_service():
    """Test the unified LLM service"""
    print("\n🔍 Testing Unified LLM Service...")
    
    try:
        from app.services.llm.llm_service import UnifiedLLMService, LLMRequest, LLMTask
        from app.schemas.user import UserResponse
        from sqlalchemy.ext.asyncio import AsyncSession
        
        # Create a mock database session
        class MockDB:
            pass
        
        mock_db = MockDB()
        
        # Create LLM service
        llm_service = UnifiedLLMService(mock_db)
        
        # Ensure initialization
        await llm_service.ensure_initialized()
        
        # Check model availability
        print(f"OpenRouter available: {'✅ Yes' if llm_service._model_availability['openrouter'] else '❌ No'}")
        print(f"Ollama available: {'✅ Yes' if llm_service._model_availability['ollama'] else '❌ No'}")
        
        # Test model selection
        user = UserResponse(
            id="test-user",
            email="test@example.com",
            subscription_tier="free",
            selected_llm_model="local",
            is_active=True,
            created_at=datetime.now()
        )
        
        selected_model = await llm_service._select_model(user, LLMTask.CHAT)
        print(f"Selected model: {selected_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLM service: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Starting OpenRouter Configuration Test")
    print("=" * 50)
    
    # Test OpenRouter API
    openrouter_ok = await test_openrouter_config()
    
    # Test LLM Service
    llm_service_ok = await test_llm_service()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"OpenRouter API: {'✅ Working' if openrouter_ok else '❌ Failed'}")
    print(f"LLM Service: {'✅ Working' if llm_service_ok else '❌ Failed'}")
    
    if openrouter_ok and llm_service_ok:
        print("\n🎉 All tests passed! Your OpenRouter configuration is working.")
        print("You can now restart your backend server and test the chat functionality.")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        print("Make sure your OPENROUTER_API_KEY is set correctly in your .env file.")

if __name__ == "__main__":
    asyncio.run(main())
