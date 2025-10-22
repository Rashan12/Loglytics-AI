# Unified LLM Service for Loglytics AI

This document describes the comprehensive unified LLM service that handles both local Ollama models and cloud-based Llama 4 Maverick model for the Loglytics AI platform.

## 🧠 Overview

The unified LLM service provides:
- **Multi-Provider Support**: Ollama (local) + Maverick (cloud) models
- **Task-Specific Processing**: Chat, log analysis, error detection, anomaly detection
- **Intelligent Model Selection**: Based on user tier and availability
- **Streaming Support**: Real-time response streaming
- **Usage Tracking**: Token counting and billing integration
- **Rate Limiting**: Tier-based request limits

## 🏗️ Architecture

### Core Components

```
backend/app/services/llm/
├── llm_service.py          # Main unified LLM service
├── ollama_client.py        # Local Ollama integration
├── maverick_client.py      # Llama 4 Maverick integration
├── prompt_templates.py     # System prompts and templates
└── response_parser.py      # Response parsing and structuring

backend/app/api/v1/endpoints/
└── llm.py                  # LLM API endpoints

backend/app/schemas/
└── llm.py                  # LLM request/response schemas
```

## 🚀 Quick Start

### 1. Start the Application
```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test LLM Service
```bash
# Run comprehensive LLM tests
python backend/scripts/test_llm.py

# Or on Windows
backend\scripts\test_llm.bat
```

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### LLM Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/llm/chat` | Chat completion | Yes |
| POST | `/api/v1/llm/chat/stream` | Streaming chat | Yes |
| POST | `/api/v1/llm/analyze` | Log analysis | Yes |
| POST | `/api/v1/llm/detect-errors` | Error detection | Yes |
| POST | `/api/v1/llm/root-cause` | Root cause analysis | Yes |
| POST | `/api/v1/llm/detect-anomalies` | Anomaly detection | Yes |
| POST | `/api/v1/llm/query` | Natural language query | Yes |
| POST | `/api/v1/llm/summarize` | Log summarization | Yes |
| GET | `/api/v1/llm/models` | Available models | Yes |
| GET | `/api/v1/llm/health` | Service health | Yes |

## 🔧 Model Providers

### 1. Ollama (Local Models)
- **Provider**: Local Ollama service
- **Models**: llama3.2:3b, phi3:3.8b, qwen2.5:3b
- **Use Case**: Free tier users, offline operation
- **Requirements**: 8GB+ RAM, Ollama installed

### 2. Maverick (Cloud Models)
- **Provider**: Llama 4 Maverick via transformers
- **Models**: meta-llama/Llama-4-Maverick-8B-Instruct
- **Use Case**: Pro tier users, high-quality analysis
- **Requirements**: 16GB+ RAM, GPU recommended

## 📝 Usage Examples

### Chat Completion

```bash
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me analyze these logs for errors",
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Log Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/llm/analyze" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "log_entries": [
      {
        "level": "ERROR",
        "message": "Database connection failed",
        "timestamp": "2024-01-15T10:30:45Z",
        "source": "database"
      }
    ],
    "analysis_type": "general",
    "structured_output": true
  }'
```

### Error Detection

```bash
curl -X POST "http://localhost:8000/api/v1/llm/detect-errors" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "log_entries": [...],
    "analysis_type": "error_detection",
    "structured_output": true
  }'
```

### Streaming Chat

```bash
curl -X POST "http://localhost:8000/api/v1/llm/chat/stream" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain log analysis best practices",
    "temperature": 0.7
  }'
```

## 🎯 LLM Tasks

### 1. Chat Completion
- **Purpose**: Conversational AI assistance
- **Use Case**: General questions about logs and systems
- **Output**: Natural language responses

### 2. Log Analysis
- **Purpose**: Comprehensive log analysis
- **Use Case**: Understanding log patterns and issues
- **Output**: Structured analysis with recommendations

### 3. Error Detection
- **Purpose**: Identify and categorize errors
- **Use Case**: Error monitoring and alerting
- **Output**: Error counts, categories, and severity

### 4. Root Cause Analysis
- **Purpose**: Find underlying causes of issues
- **Use Case**: Troubleshooting and debugging
- **Output**: Root cause with supporting evidence

### 5. Anomaly Detection
- **Purpose**: Detect unusual patterns and outliers
- **Use Case**: Security monitoring and performance analysis
- **Output**: Anomalies with confidence scores

### 6. Natural Language Query
- **Purpose**: Answer questions about log data
- **Use Case**: Interactive log exploration
- **Output**: Direct answers to user questions

### 7. Log Summarization
- **Purpose**: Create concise summaries
- **Use Case**: Executive reports and quick insights
- **Output**: Key metrics and highlights

## 🎨 Prompt Templates

### System Prompts
Each task has specialized system prompts:

```python
# Log Analysis System Prompt
"You are Loglytics AI, an expert log analysis assistant. You help users understand their logs, identify issues, and provide actionable insights."

# Error Detection System Prompt
"You are an expert error detection specialist. Your task is to identify and categorize errors in log data."

# Root Cause Analysis System Prompt
"You are a root cause analysis expert. Analyze error patterns and system behavior to identify the underlying causes of issues."
```

### Few-Shot Examples
Templates include relevant examples:

```python
# Error Detection Examples
"Example 1: [ERROR] HTTP 500 Internal Server Error - /api/users
Detection: Server error in user API endpoint. High priority - affects user functionality."
```

### Structured Output
JSON format specifications:

```json
{
  "summary": "Brief overview of the log data",
  "issues": [
    {
      "type": "error|warning|info",
      "severity": "low|medium|high|critical",
      "message": "Description of the issue"
    }
  ],
  "recommendations": ["Actionable recommendations"]
}
```

## ⚙️ Configuration

### Environment Variables

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_LLM_MODEL=llama3.2:3b

# Maverick Configuration
MAVERICK_MODEL_NAME=meta-llama/Llama-4-Maverick-8B-Instruct

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Subscription Limits
FREE_TIER_LIMITS={"max_llm_tokens_per_month": 100000}
PRO_TIER_LIMITS={"max_llm_tokens_per_month": 1000000}
```

### Model Selection Logic

```python
# Pro users get Maverick if available
if user.subscription_tier == SubscriptionTier.PRO and maverick_available:
    return "maverick"

# Free users and fallback to Ollama
if ollama_available:
    return "ollama"

# Last resort: Maverick for all
if maverick_available:
    return "maverick"
```

## 🔒 Security & Rate Limiting

### Rate Limits by Tier

#### Free Tier
- **LLM Tokens**: 100,000 per month
- **API Calls**: 1,000 per day
- **Models**: Ollama only

#### Pro Tier
- **LLM Tokens**: 1,000,000 per month
- **API Calls**: 10,000 per day
- **Models**: Ollama + Maverick

### Rate Limiting Implementation

```python
# Check user's current usage
usage = db.query(UsageTracking).filter(
    UsageTracking.user_id == user.id,
    UsageTracking.date == today
).first()

# Enforce limits
if usage.llm_tokens_used >= max_tokens:
    raise ValueError("Token limit exceeded")
```

## 📊 Usage Tracking

### Token Counting
- **Input Tokens**: Prompt length
- **Output Tokens**: Generated content length
- **Total Tokens**: Input + Output

### Usage Storage
```python
# Track in usage_tracking table
usage = UsageTracking(
    user_id=user_id,
    date=today,
    llm_tokens_used=tokens_used,
    api_calls_count=1
)
```

### Billing Integration
- **Free Tier**: Token counting for limits
- **Pro Tier**: Token counting for billing
- **Overage**: Track excess usage

## 🧪 Testing

### Test Coverage

The test suite covers:
- ✅ Model availability and health checks
- ✅ Chat completion (single and streaming)
- ✅ Log analysis with structured output
- ✅ Error detection and categorization
- ✅ Anomaly detection
- ✅ Natural language queries
- ✅ Log summarization
- ✅ Rate limiting enforcement
- ✅ Usage tracking

### Running Tests

```bash
# Run all LLM tests
python backend/scripts/test_llm.py

# Test with custom base URL
python backend/scripts/test_llm.py http://localhost:8000

# Run specific test
python -c "
import asyncio
from backend.scripts.test_llm import LLMTester

async def test():
    async with LLMTester() as tester:
        await tester.authenticate()
        await tester.test_chat_completion()

asyncio.run(test())
"
```

## 🔧 Development

### Adding New Tasks

```python
# 1. Add task to enum
class LLMTask(str, Enum):
    NEW_TASK = "new_task"

# 2. Add prompt template
templates["new_task"] = {
    "system": "You are a new task specialist...",
    "few_shot": "Examples...",
    "structured_output": "JSON format..."
}

# 3. Add API endpoint
@router.post("/new-task")
async def new_task_endpoint(request: AnalysisRequest):
    # Implementation
```

### Adding New Models

```python
# 1. Create model client
class NewModelClient:
    async def generate(self, prompt: str) -> Dict[str, Any]:
        # Implementation

# 2. Update unified service
class UnifiedLLMService:
    def __init__(self):
        self.new_model_client = NewModelClient()
    
    async def _select_model(self, user, task):
        if self.new_model_available:
            return "new_model"
```

## 📈 Performance Optimization

### Memory Management
- **Ollama**: Automatic model loading/unloading
- **Maverick**: Quantization for 16GB RAM
- **Caching**: Response caching for repeated queries

### Batch Processing
```python
# Process multiple requests together
async def batch_generate(prompts: List[str]):
    return await maverick_client.batch_generate(prompts)
```

### Streaming Optimization
- **Chunk Size**: Optimal chunk sizes for streaming
- **Buffer Management**: Efficient content buffering
- **Error Handling**: Graceful streaming error recovery

## 🚨 Error Handling

### Model Unavailability
```python
# Graceful fallback
if not ollama_available and not maverick_available:
    return error_response("No LLM models available")

# Fallback to available model
if preferred_model_unavailable:
    return fallback_model
```

### Rate Limit Exceeded
```python
# Clear error messages
if rate_limit_exceeded:
    return {
        "error": "Rate limit exceeded",
        "retry_after": 300,
        "limit": 1000
    }
```

### Token Limit Exceeded
```python
# Truncate context if too long
if context_too_long:
    context = truncate_context(context, max_length=4000)
```

## 📚 API Documentation

### Request Schemas

```python
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]]
    conversation_history: Optional[List[Dict[str, str]]]
    max_tokens: Optional[int]
    temperature: float = 0.7
    structured_output: bool = False

class AnalysisRequest(BaseModel):
    log_entries: List[LogEntry]
    prompt: Optional[str]
    analysis_type: AnalysisType
    max_tokens: Optional[int]
    temperature: float = 0.3
    structured_output: bool = True
```

### Response Schemas

```python
class ChatResponse(BaseModel):
    message: str
    model_used: str
    tokens_used: int
    latency_ms: float
    confidence_score: float
    metadata: Dict[str, Any]
    structured_data: Optional[Dict[str, Any]]

class AnalysisResponse(BaseModel):
    analysis: str
    model_used: str
    tokens_used: int
    latency_ms: float
    confidence_score: float
    metadata: Dict[str, Any]
    structured_data: Optional[Dict[str, Any]]
```

## 🔍 Troubleshooting

### Common Issues

#### 1. No Models Available
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check Maverick model
python -c "from transformers import AutoTokenizer; print('Maverick available')"
```

#### 2. Rate Limit Exceeded
```bash
# Check user usage
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/users/me
```

#### 3. Memory Issues
```bash
# Check system memory
free -h

# Check GPU memory
nvidia-smi
```

#### 4. Slow Responses
```bash
# Check model loading
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/llm/health
```

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload
```

## 🚀 Production Deployment

### Requirements

#### Minimum System Requirements
- **RAM**: 16GB (8GB for Ollama only)
- **CPU**: 4+ cores
- **Storage**: 20GB free space
- **GPU**: Optional but recommended for Maverick

#### Recommended Configuration
- **RAM**: 32GB+
- **GPU**: NVIDIA RTX 4090 or better
- **Storage**: SSD with 50GB+ free space
- **Network**: High-speed internet for model downloads

### Deployment Checklist

- [ ] Install and configure Ollama
- [ ] Download required models
- [ ] Set up Maverick model (if using)
- [ ] Configure rate limiting
- [ ] Set up usage tracking
- [ ] Enable monitoring
- [ ] Test all endpoints
- [ ] Configure load balancing
- [ ] Set up caching
- [ ] Monitor performance

## 📞 Support

### Getting Help

1. **Check Logs**: Review application logs for errors
2. **Run Tests**: Execute test suite to identify issues
3. **Check Health**: Use health check endpoints
4. **Verify Models**: Ensure models are loaded and available
5. **Contact Support**: Reach out to development team

### Resources

- **API Documentation**: http://localhost:8000/docs
- **Test Suite**: `backend/scripts/test_llm.py`
- **Health Checks**: `/api/v1/llm/health`
- **Model Status**: `/api/v1/llm/models`

---

**Ready to get started?** Run the test script to verify your LLM service is working correctly!
