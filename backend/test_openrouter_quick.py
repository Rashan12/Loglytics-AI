#!/usr/bin/env python3
"""
Quick OpenRouter API Test
Tests if OpenRouter API key is configured and working
"""

import os
import asyncio
from openai import OpenAI

async def test_openrouter():
    """Test OpenRouter API connection"""
    print("🔍 Testing OpenRouter API Configuration...")
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your-openrouter-api-key-here":
        print("❌ OPENROUTER_API_KEY not configured!")
        print("Please set your OpenRouter API key in the environment.")
        print("You can do this by:")
        print("1. Creating a .env file in the backend directory")
        print("2. Adding: OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here")
        print("3. Or setting the environment variable directly")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    # Test API connection
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        print("🧪 Testing API connection...")
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-8b-instruct",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10,
            extra_headers={
                "HTTP-Referer": "https://loglytics-ai.com",
                "X-Title": "Loglytics AI"
            }
        )
        
        print("✅ OpenRouter API is working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter API test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openrouter())
