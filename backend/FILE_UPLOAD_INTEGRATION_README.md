# File Upload to Processing Pipeline Integration

## Overview

This document describes the complete integration of file upload functionality with the processing pipeline, enabling users to upload log files through chat interfaces and receive AI-powered responses based on the uploaded content.

## Integration Flow

```
User uploads file → Backend saves → LogParser parses → RAG indexes → 
User asks question → RAG queries context → LLM generates answer with context → User sees response
```

## Components Updated

### 1. Project Chat Endpoint (`backend/app/api/v1/endpoints/projects.py`)

**Endpoint**: `POST /api/v1/projects/{project_id}/chat`

**Features**:
- ✅ Accepts file uploads with message
- ✅ Validates file size (100MB limit) and type (.log, .txt, .csv)
- ✅ Saves file to disk and creates LogFile record
- ✅ Processes file with LogParserService
- ✅ Indexes file content in RAG system
- ✅ Queries RAG for relevant context before LLM generation
- ✅ Generates AI response with RAG context
- ✅ Returns comprehensive response with processing metadata

**Request Format**:
```python
# Form data with file upload
message: str = Form(...)
file: Optional[UploadFile] = File(None)
```

**Response Format**:
```json
{
    "response": "AI response based on uploaded logs",
    "conversation_id": "uuid",
    "timestamp": "2024-01-15T10:30:00",
    "file_processed": true,
    "file_id": "uuid",
    "chunks_retrieved": 5,
    "confidence": 0.85
}
```

### 2. General Chat Endpoint (`backend/app/api/v1/endpoints/chat.py`)

**Endpoint**: `POST /api/v1/chats/{chat_id}/messages`

**Features**:
- ✅ Accepts file uploads with message
- ✅ Same validation and processing as project chat
- ✅ Uses "default" project for RAG indexing
- ✅ Full RAG integration for context retrieval
- ✅ Enhanced error handling and logging

### 3. Unified LLM Service (`backend/app/services/llm/llm_service.py`)

**Enhanced Method**: `generate_response()`

**New Features**:
- ✅ Accepts optional `rag_context` parameter
- ✅ Prepends RAG context to prompt when provided
- ✅ Maintains backward compatibility
- ✅ Enhanced prompt construction with context

**Usage**:
```python
response = await llm_service.generate_response(
    request=llm_request,
    user=current_user,
    db=db,
    rag_context="Relevant context from uploaded logs..."
)
```

## Processing Pipeline

### 1. File Upload & Validation
- File size validation (100MB limit)
- File type validation (.log, .txt, .csv)
- Secure file storage with unique naming

### 2. Log Parsing
- **Service**: `LogParserService`
- **Method**: `process_log_file(log_file_id)`
- **Features**:
  - Extracts log entries with timestamps, levels, messages
  - Identifies patterns (IP addresses, session IDs, user IDs)
  - Stores parsed data in database
  - Error handling for parsing failures

### 3. RAG Indexing
- **Service**: `RAGService`
- **Method**: `index_log_file()`
- **Features**:
  - Chunks file content for vector storage
  - Generates embeddings using SentenceTransformer
  - Stores in ChromaDB with metadata
  - Project-level isolation for security

### 4. Context Retrieval
- **Service**: `RAGService`
- **Method**: `query()`
- **Features**:
  - Semantic search for relevant chunks
  - Configurable similarity threshold
  - Returns ranked results with confidence scores
  - Project-specific context isolation

### 5. LLM Generation
- **Service**: `UnifiedLLMService`
- **Features**:
  - Accepts RAG context for enhanced responses
  - Supports both local (Ollama) and cloud (Maverick) models
  - Subscription-based model selection
  - Context-aware prompt construction

## Error Handling

### File Processing Errors
- File size/type validation failures
- Parsing errors (non-blocking)
- RAG indexing failures (non-blocking)
- Graceful degradation when services fail

### LLM Generation Errors
- Model availability fallbacks
- Rate limiting based on user tier
- Error logging and user feedback
- Simulated responses when LLM fails

## Security Features

### File Security
- File type validation
- Size limits to prevent abuse
- Secure file storage with unique names
- Project-level access control

### RAG Security
- Project-level context isolation
- User-specific indexing
- Metadata filtering for access control
- Secure vector storage

## Performance Optimizations

### File Processing
- Streaming file uploads (no memory overload)
- Async processing for parsing and indexing
- Background processing for large files
- Efficient chunking for RAG storage

### RAG Performance
- Configurable chunk sizes
- Similarity threshold tuning
- Result limiting for performance
- Caching for repeated queries

## Testing

### Test Script
Run the integration test:
```bash
cd backend
python test_file_upload_integration.py
```

### Test Coverage
- ✅ Authentication flow
- ✅ Project creation
- ✅ File upload with validation
- ✅ Project chat with file processing
- ✅ General chat with file processing
- ✅ RAG search functionality
- ✅ Error handling scenarios

## API Endpoints Summary

| Endpoint | Method | Purpose | File Upload |
|----------|--------|---------|-------------|
| `/api/v1/projects/{id}/chat` | POST | Project chat with file | ✅ |
| `/api/v1/chats/{id}/messages` | POST | General chat with file | ✅ |
| `/api/v1/rag/search` | POST | RAG search | ❌ |
| `/api/v1/rag/stats` | GET | RAG statistics | ❌ |

## Configuration

### Environment Variables
```bash
# Required for RAG functionality
CHROMA_DB_PATH=./chroma_db
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2

# Required for LLM functionality
OPENROUTER_API_KEY=your_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

### File Storage
- Upload directory: `uploads/`
- File naming: `{uuid}_{original_filename}`
- Project isolation: `uploads/{project_id}/`

## Monitoring & Logging

### Log Levels
- **INFO**: Successful operations, file processing
- **ERROR**: Service failures, parsing errors
- **DEBUG**: Detailed processing steps

### Key Metrics
- File processing success rate
- RAG indexing performance
- LLM response quality
- User engagement metrics

## Future Enhancements

### Planned Features
- [ ] Batch file upload support
- [ ] Real-time processing status updates
- [ ] Advanced file format support
- [ ] Custom parsing rules
- [ ] Enhanced RAG reranking
- [ ] Multi-modal file support

### Performance Improvements
- [ ] Distributed processing
- [ ] Caching layer for RAG queries
- [ ] Background job queue
- [ ] Progressive file processing

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size limits
   - Verify file type restrictions
   - Ensure upload directory permissions

2. **RAG Indexing Fails**
   - Verify ChromaDB initialization
   - Check SentenceTransformer model
   - Ensure sufficient disk space

3. **LLM Generation Fails**
   - Verify model availability
   - Check API keys and quotas
   - Review rate limiting settings

### Debug Commands
```bash
# Check RAG service status
python -c "from app.services.rag.rag_service import RAGService; print('RAG OK')"

# Test LLM service
python -c "from app.services.llm.llm_service import UnifiedLLMService; print('LLM OK')"

# Verify file processing
ls -la uploads/
```

## Conclusion

The file upload to processing pipeline integration provides a complete solution for:
- ✅ Secure file upload and validation
- ✅ Intelligent log parsing and analysis
- ✅ RAG-powered context retrieval
- ✅ AI-powered responses with file context
- ✅ Project-level isolation and security
- ✅ Comprehensive error handling
- ✅ Performance optimization
- ✅ Full testing coverage

This integration enables users to upload log files and immediately ask questions about them, receiving intelligent responses based on the actual content of their logs.
