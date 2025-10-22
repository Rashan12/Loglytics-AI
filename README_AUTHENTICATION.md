# JWT-Based Authentication System for Loglytics AI

This document describes the comprehensive JWT-based authentication system implemented for the Loglytics AI FastAPI backend.

## 🔐 Overview

The authentication system provides:
- **User Registration & Login** with email validation
- **JWT Token Management** (access + refresh tokens)
- **Password Security** with bcrypt hashing
- **API Key Authentication** for integrations
- **Role-Based Access Control** (free vs pro tier)
- **Rate Limiting** for security
- **Password Reset Flow** with secure tokens

## 🏗️ Architecture

### Core Components

```
backend/app/services/auth/
├── auth_service.py          # Main authentication logic
├── jwt_handler.py           # JWT token operations
├── password_handler.py      # Password hashing & validation
└── dependencies.py          # FastAPI dependency functions

backend/app/api/v1/endpoints/
└── auth.py                  # Authentication API endpoints

backend/app/schemas/
├── auth.py                  # Authentication schemas
└── user.py                  # User schemas

backend/app/middleware/
└── rate_limit.py            # Rate limiting middleware
```

## 🚀 Quick Start

### 1. Start the Application
```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Authentication
```bash
# Run authentication tests
python backend/scripts/test_auth.py

# Or on Windows
backend\scripts\test_auth.bat
```

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | User login | No |
| POST | `/api/v1/auth/refresh` | Refresh access token | No |
| POST | `/api/v1/auth/logout` | User logout | Yes |
| POST | `/api/v1/auth/password-reset-request` | Request password reset | No |
| POST | `/api/v1/auth/password-reset-confirm` | Confirm password reset | No |
| GET | `/api/v1/auth/me` | Get current user | Yes |
| PUT | `/api/v1/auth/me` | Update current user | Yes |
| POST | `/api/v1/auth/api-keys` | Create API key | Yes |
| GET | `/api/v1/auth/api-keys` | List API keys | Yes |
| DELETE | `/api/v1/auth/api-keys/{key_id}` | Delete API key | Yes |

## 🔑 Authentication Methods

### 1. JWT Token Authentication

**Access Token** (15 minutes expiry):
```http
Authorization: Bearer <access_token>
```

**Refresh Token** (7 days expiry):
```json
{
  "refresh_token": "<refresh_token>"
}
```

### 2. API Key Authentication

**API Key Header**:
```http
X-API-Key: <api_key>
```

## 📝 Usage Examples

### User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "subscription_tier": "free",
    "selected_llm_model": "local"
  }'
```

### User Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123!"
```

### Get Current User

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

### Create API Key

```bash
curl -X POST "http://localhost:8000/api/v1/auth/api-keys" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My API Key"}'
```

## 🔒 Security Features

### Password Security
- **bcrypt hashing** with cost factor 12
- **Strong password validation**:
  - Minimum 8 characters
  - Uppercase and lowercase letters
  - Numbers required
  - Special characters recommended
- **Breach detection** for common passwords
- **Password strength scoring**

### JWT Security
- **HS256 algorithm** for token signing
- **Short-lived access tokens** (15 minutes)
- **Refresh token rotation** for security
- **Token type validation** (access/refresh)
- **JWT ID tracking** for token management

### Rate Limiting
- **Login attempts**: 5 per 5 minutes
- **Registration**: 3 per hour
- **Password reset**: 3 per hour
- **API calls**: 1000 per hour (default)
- **Burst protection**: 10 requests per minute

### Input Validation
- **Email format validation** using email-validator
- **Username format validation** (alphanumeric only)
- **Input sanitization** to prevent injection attacks
- **CSRF protection** with secure tokens

## 🛡️ Role-Based Access Control

### Subscription Tiers

#### Free Tier
- 3 projects maximum
- 100 log files maximum
- 10,000 log entries maximum
- 1GB storage maximum
- 1,000 API calls per day
- 100,000 LLM tokens per month

#### Pro Tier
- 50 projects maximum
- 1,000 log files maximum
- 1,000,000 log entries maximum
- 10GB storage maximum
- 10,000 API calls per day
- 1,000,000 LLM tokens per month

### Permission Checks

```python
from app.services.auth.dependencies import require_pro_subscription

@router.get("/pro-feature")
async def pro_feature(
    current_user: UserResponse = Depends(require_pro_subscription)
):
    # Only Pro users can access this endpoint
    pass
```

## 🔧 Configuration

### Environment Variables

```bash
# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/loglytics_db

# Redis
REDIS_URL=redis://localhost:6379/0
```

### JWT Configuration

```python
# In app/config.py
class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
```

## 🧪 Testing

### Run Authentication Tests

```bash
# Test all authentication functionality
python backend/scripts/test_auth.py

# Test with custom base URL
python backend/scripts/test_auth.py http://localhost:8000
```

### Test Coverage

The test suite covers:
- ✅ User registration
- ✅ User login
- ✅ Token refresh
- ✅ Password reset flow
- ✅ API key management
- ✅ Rate limiting
- ✅ Invalid credentials handling
- ✅ JWT token validation

## 📊 Monitoring & Logging

### Security Events

The system logs:
- **Login attempts** (successful and failed)
- **Password reset requests**
- **API key creation/deletion**
- **Rate limit violations**
- **Suspicious activities**

### Log Format

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "event": "user_login",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "success": true
}
```

## 🚨 Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "error": {
    "code": 401,
    "message": "Could not validate credentials",
    "request_id": "abc123"
  }
}
```

#### 429 Too Many Requests
```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded",
    "rate_limit": {
      "limit": 5,
      "remaining": 0,
      "reset_time": 1642248000,
      "retry_after": 300
    }
  }
}
```

#### 422 Validation Error
```json
{
  "error": {
    "code": 422,
    "message": "Validation error",
    "details": [
      {
        "loc": ["body", "password"],
        "msg": "Password must contain at least one uppercase letter",
        "type": "value_error"
      }
    ]
  }
}
```

## 🔄 Token Management

### Access Token Structure

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "subscription_tier": "free",
  "exp": 1642248000,
  "iat": 1642247100,
  "type": "access",
  "jti": "unique_token_id"
}
```

### Refresh Token Structure

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "subscription_tier": "free",
  "exp": 1642852800,
  "iat": 1642248000,
  "type": "refresh",
  "jti": "unique_token_id"
}
```

## 🛠️ Development

### Adding New Endpoints

```python
from app.services.auth.dependencies import get_current_active_user

@router.get("/protected-endpoint")
async def protected_endpoint(
    current_user: UserResponse = Depends(get_current_active_user)
):
    return {"message": f"Hello {current_user.email}!"}
```

### Custom Permission Checks

```python
from app.services.auth.dependencies import require_pro_subscription

@router.get("/pro-only")
async def pro_only_endpoint(
    current_user: UserResponse = Depends(require_pro_subscription)
):
    return {"message": "Pro feature accessed!"}
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### OpenAPI Schema
The API follows OpenAPI 3.0 specification with:
- Complete request/response schemas
- Authentication requirements
- Error response definitions
- Example requests and responses

## 🔍 Troubleshooting

### Common Issues

#### 1. Token Expired
```bash
# Refresh the token
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

#### 2. Rate Limited
```bash
# Wait for rate limit to reset or use exponential backoff
# Check rate limit headers in response
```

#### 3. Invalid Credentials
```bash
# Check username/password format
# Ensure user exists and is active
```

#### 4. Database Connection Issues
```bash
# Check DATABASE_URL configuration
# Ensure PostgreSQL is running
# Verify database permissions
```

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload
```

## 🚀 Production Deployment

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Set up database SSL
- [ ] Enable rate limiting
- [ ] Configure proper logging
- [ ] Set up monitoring
- [ ] Use environment variables for secrets

### Performance Optimization

- [ ] Use Redis for session storage
- [ ] Implement token blacklisting
- [ ] Add database connection pooling
- [ ] Enable response caching
- [ ] Use CDN for static assets

## 📞 Support

For issues with the authentication system:
1. Check the logs for error messages
2. Verify configuration settings
3. Run the test suite
4. Check API documentation
5. Contact the development team

---

**Ready to get started?** Run the test script to verify your authentication system is working correctly!
