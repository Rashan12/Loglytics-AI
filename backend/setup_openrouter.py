#!/usr/bin/env python3
"""
OpenRouter Setup Script
Helps configure OpenRouter API key and environment
"""

import os
import sys

def create_env_file():
    """Create .env file with OpenRouter configuration"""
    env_content = """# OpenRouter API Configuration
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_MODEL=meta-llama/llama-3.2-90b-vision-instruct

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/loglytics_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
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
"""
    
    env_file_path = ".env"
    
    if os.path.exists(env_file_path):
        print(f"Environment file {env_file_path} already exists.")
        print("Please manually update the OPENROUTER_API_KEY in the existing .env file.")
        return True
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"Created {env_file_path} file successfully!")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False

def show_setup_instructions():
    """Show setup instructions"""
    print("\n" + "="*60)
    print("OPENROUTER API SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. GET YOUR API KEY:")
    print("   - Go to https://openrouter.ai/")
    print("   - Sign up or log in")
    print("   - Go to your profile > Keys")
    print("   - Create a new API key")
    print("   - Copy the key (starts with 'sk-or-v1-...')")
    
    print("\n2. UPDATE YOUR .env FILE:")
    print("   - Open the .env file in this directory")
    print("   - Replace 'your-openrouter-api-key-here' with your actual API key")
    print("   - Save the file")
    
    print("\n3. TEST THE CONNECTION:")
    print("   - Run: python test_openrouter.py")
    print("   - You should see 'SUCCESS! OpenRouter is working!'")
    
    print("\n4. START THE BACKEND:")
    print("   - Run: uvicorn app.main:app --reload")
    print("   - Your API will be available at http://localhost:8000")
    
    print("\n" + "="*60)
    print("IMPORTANT NOTES:")
    print("- New accounts get $1 free credit to test")
    print("- Monitor your usage and costs in OpenRouter dashboard")
    print("- Never commit your .env file to git")
    print("- The model costs approximately $0.54/million input tokens")
    print("="*60)

def main():
    """Main setup function"""
    print("OpenRouter Setup for Loglytics AI")
    print("="*40)
    
    # Create .env file
    if create_env_file():
        show_setup_instructions()
        print("\nSetup complete! Follow the instructions above to configure your API key.")
    else:
        print("Setup failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
