#!/usr/bin/env python3
"""
Test script for OpenRouter API connection
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_connection():
    """Test OpenRouter API connection"""
    print("Testing OpenRouter API Connection")
    print("=" * 50)
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-90b-vision-instruct")
    
    if not api_key or api_key == "your-openrouter-api-key-here":
        print("ERROR: OPENROUTER_API_KEY not set or still using placeholder")
        print("Please set your actual OpenRouter API key in the .env file")
        print("Get your API key from: https://openrouter.ai/")
        return False
    
    print(f"API Key found: {api_key[:20]}...")
    print(f"Model: {model}")
    
    # Initialize OpenAI client
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Test headers for cost tracking
    extra_headers = {
        "HTTP-Referer": "https://loglytics-ai.com",
        "X-Title": "Loglytics AI"
    }
    
    try:
        print("\nTesting API call...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say hello and confirm you're working! Keep it brief."}
            ],
            temperature=0.7,
            max_tokens=100,
            extra_headers=extra_headers
        )
        
        print("SUCCESS! OpenRouter is working!")
        print(f"Response: {response.choices[0].message.content}")
        print(f"Model used: {response.model}")
        
        # Show usage information
        if hasattr(response, 'usage'):
            usage = response.usage
            print(f"\nUsage Information:")
            print(f"Input tokens: {usage.prompt_tokens}")
            print(f"Output tokens: {usage.completion_tokens}")
            print(f"Total tokens: {usage.total_tokens}")
            
            # Estimate cost (approximate)
            input_cost = (usage.prompt_tokens / 1000000) * 0.54  # $0.54 per million input tokens
            output_cost = (usage.completion_tokens / 1000000) * 0.81  # $0.81 per million output tokens
            total_cost = input_cost + output_cost
            
            print(f"Estimated cost: ${total_cost:.6f}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Check if your API key is correct")
        print("2. Verify you have credits in your OpenRouter account")
        print("3. Check if the model name is correct")
        print("4. Ensure you have internet connection")
        return False

def test_environment_setup():
    """Test environment configuration"""
    print("\nTesting Environment Setup")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "OPENROUTER_MODEL"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your-{var.lower().replace('_', '-')}-here":
            missing_vars.append(var)
        else:
            print(f"{var}: {value[:20]}..." if len(str(value)) > 20 else f"{var}: {value}")
    
    if missing_vars:
        print(f"\nMissing or invalid environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the correct values")
        return False
    
    print("All environment variables are set correctly")
    return True

def main():
    """Main test function"""
    print("OpenRouter API Test Suite")
    print("=" * 50)
    
    # Test environment setup
    env_ok = test_environment_setup()
    
    if not env_ok:
        print("\nEnvironment setup failed. Please fix the issues above.")
        return 1
    
    # Test API connection
    api_ok = test_openrouter_connection()
    
    if api_ok:
        print("\nAll tests passed! OpenRouter is ready to use.")
        print("\nNext steps:")
        print("1. Start your backend server: uvicorn app.main:app --reload")
        print("2. Test the chat endpoint: POST /api/v1/chat")
        print("3. Monitor usage and costs in your OpenRouter dashboard")
        return 0
    else:
        print("\nAPI connection failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
