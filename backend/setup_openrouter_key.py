#!/usr/bin/env python3
"""
OpenRouter API Key Setup Helper
This script helps you configure the OpenRouter API key for Loglytics AI
"""

import os
import sys

def check_api_key():
    """Check if API key is configured"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key and api_key != "your-openrouter-api-key-here":
        print(f"✅ OpenRouter API key is configured: {api_key[:20]}...")
        return True
    else:
        print("❌ OpenRouter API key is not configured")
        return False

def show_setup_instructions():
    """Show setup instructions"""
    print("\n" + "="*60)
    print("🔧 OPENROUTER API KEY SETUP INSTRUCTIONS")
    print("="*60)
    print()
    print("1. Get your OpenRouter API key:")
    print("   • Go to https://openrouter.ai/")
    print("   • Sign in or create an account")
    print("   • Go to your profile → Keys")
    print("   • Create a new API key")
    print("   • Copy the key (starts with 'sk-or-v1-...')")
    print()
    print("2. Set the API key in your environment:")
    print("   Option A - Create .env file in backend directory:")
    print("   ```")
    print("   OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here")
    print("   OPENROUTER_MODEL=meta-llama/llama-4-maverick-8b-instruct")
    print("   ```")
    print()
    print("   Option B - Set environment variable:")
    print("   Windows: set OPENROUTER_API_KEY=sk-or-v1-your-key")
    print("   Linux/Mac: export OPENROUTER_API_KEY=sk-or-v1-your-key")
    print()
    print("3. Test the configuration:")
    print("   python test_openrouter_quick.py")
    print()
    print("4. Restart your backend server")
    print()

def create_env_template():
    """Create a template .env file"""
    env_content = """# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_MODEL=meta-llama/llama-4-maverick-8b-instruct

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:Rashan12@localhost:5432/loglytics_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Rashan12
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=loglytics_ai

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Security
SECRET_KEY=your-secret-key-change-in-production

# Application Settings
APP_NAME=Loglytics AI
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_LLM_MODEL=llama3.2:3b
"""
    
    env_file_path = ".env"
    
    if os.path.exists(env_file_path):
        print(f"⚠️  {env_file_path} already exists")
        print("Please manually update the OPENROUTER_API_KEY in the existing file")
        return False
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_file_path} template file")
        print("Please edit the file and replace 'sk-or-v1-your-actual-key-here' with your real API key")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Checking OpenRouter API configuration...")
    
    if check_api_key():
        print("✅ Configuration looks good!")
        return
    
    print("\n❌ API key not configured. Here's how to fix it:")
    show_setup_instructions()
    
    # Ask if user wants to create .env template
    try:
        response = input("\nWould you like me to create a .env template file? (y/n): ").lower()
        if response in ['y', 'yes']:
            create_env_template()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        return
    
    print("\n📝 Next steps:")
    print("1. Get your OpenRouter API key from https://openrouter.ai/")
    print("2. Update the .env file with your real API key")
    print("3. Run: python test_openrouter_quick.py")
    print("4. Restart your backend server")

if __name__ == "__main__":
    main()
