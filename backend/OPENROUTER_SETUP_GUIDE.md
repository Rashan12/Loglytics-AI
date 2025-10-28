# OpenRouter API Setup Guide

## Step 1: Get OpenRouter API Key

1. Go to https://openrouter.ai/
2. Click "Sign In" or "Sign Up"
3. Sign in with Google/GitHub or create account
4. After login, click on your profile (top right)
5. Click "Keys" or "API Keys"
6. Click "Create Key" or "+ New Key"
7. Give it a name like "Loglytics AI"
8. Copy the API key (starts with "sk-or-v1-...")

## Step 2: Add API Key to Environment

Create a `.env` file in the `backend/` directory with:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
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
```

## Step 3: Test the Connection

Run the test script:
```bash
cd backend
python test_openrouter.py
```

## Step 4: Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

## Available Models

- `meta-llama/llama-3.2-90b-vision-instruct` (Best quality, recommended)
- `meta-llama/llama-3.1-70b-instruct` (Cheaper, faster)
- `anthropic/claude-3.5-sonnet` (Alternative)
- `openai/gpt-4-turbo` (Alternative)

## Cost Information

- Llama 3.2 90B: ~$0.54/million input tokens, ~$0.81/million output tokens
- New accounts get $1 free credit to test
- Free tier has rate limits, upgrade for production

## Security Notes

- NEVER commit .env file to git
- Use strong, unique API keys
- Monitor usage and costs
- Set up proper rate limiting for production
