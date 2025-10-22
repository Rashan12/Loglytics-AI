# RAG (Retrieval-Augmented Generation) System for Loglytics AI

This document describes the comprehensive RAG system that provides intelligent log analysis through semantic search and context-aware AI responses.

## 🧠 Overview

The RAG system provides:
- **Semantic Search**: Find relevant log entries using natural language queries
- **Project Isolation**: Complete data isolation using project-level filtering
- **Smart Chunking**: Intelligent text chunking that preserves log entry boundaries
- **Vector Embeddings**: all-MiniLM-L6-v2 model for high-quality embeddings
- **Hybrid Search**: Combines vector similarity with metadata filtering
- **Context-Aware Responses**: AI answers based on retrieved log context

## 🏗️ Architecture

### Core Components

```
backend/app/services/rag/
├── rag_service.py          # Main RAG orchestration
├── embedding_service.py    # all-MiniLM-L6-v2 embeddings
├── vector_store.py         # pgvector operations
├── chunking_service.py     # Smart text chunking
├── retrieval_service.py    # Semantic search and ranking
└── rag_pipeline.py         # End-to-end RAG pipeline

backend/app/api/v1/endpoints/
└── rag.py                  # RAG API endpoints

backend/app/schemas/
└── rag.py                  # RAG request/response schemas
```

## 🚀 Quick Start

### 1. Start the Application
```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test RAG System
```bash
# Run comprehensive RAG tests
python backend/scripts/test_rag.py

# Or on Windows
backend\scripts\test_rag.bat
```

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### RAG Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/rag/query` | Ask question using RAG | Yes |
| GET | `/api/v1/rag/stats/{project_id}` | Get RAG statistics | Yes |
| DELETE | `/api/v1/rag/clear/{project_id}` | Clear project vectors | Yes |
| POST | `/api/v1/rag/index` | Index log file for RAG | Yes |
| POST | `/api/v1/rag/reindex/{log_file_id}` | Reindex specific log file | Yes |
| POST | `/api/v1/rag/search` | Search similar content | Yes |
| GET | `/api/v1/rag/health` | RAG service health | Yes |
| POST | `/api/v1/rag/batch-index` | Batch index multiple files | Yes |

## 🔧 Core Services

### 1. Embedding Service (`embedding_service.py`)
- **Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Features**: Batch processing, similarity calculation
- **Memory**: Optimized for 16GB RAM constraint
- **Caching**: Model loaded once at startup

### 2. Chunking Service (`chunking_service.py`)
- **Strategy**: Semantic chunking with log entry boundaries
- **Size**: 500-1000 characters with 100 char overlap
- **Formats**: Standard, JSON, Apache, Nginx, Syslog
- **Metadata**: Timestamp, log level, source preservation

### 3. Vector Store (`vector_store.py`)
- **Database**: PostgreSQL with pgvector extension
- **Index**: IVFFlat index for cosine similarity
- **Isolation**: Project-level and user-level filtering
- **Operations**: CRUD, search, statistics

### 4. Retrieval Service (`retrieval_service.py`)
- **Search**: Vector similarity + metadata filtering
- **Reranking**: Content quality scoring
- **Hybrid**: Combines vector and text search
- **Filtering**: Date range, log level, source

### 5. RAG Pipeline (`rag_pipeline.py`)
- **Flow**: Query → Embedding → Retrieval → LLM → Response
- **Context**: Constructs rich context from retrieved chunks
- **Citations**: Tracks which chunks were used
- **Confidence**: Calculates overall confidence score

## 📝 Usage Examples

### RAG Query

```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What errors are occurring in my system?",
    "project_id": "project-123",
    "max_chunks": 5,
    "similarity_threshold": 0.7
  }'
```

### Index Log File

```bash
curl -X POST "http://localhost:8000/api/v1/rag/index" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "log_file_id": "log-001",
    "project_id": "project-123",
    "content": "2024-01-15T10:30:45Z ERROR Database connection failed",
    "file_type": "standard"
  }'
```

### Search Similar Content

```bash
curl -X POST "http://localhost:8000/api/v1/rag/search" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "database timeout",
    "project_id": "project-123",
    "search_type": "similar",
    "limit": 5
  }'
```

### Get RAG Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/rag/stats/project-123" \
  -H "Authorization: Bearer <access_token>"
```

## 🎯 RAG Pipeline Flow

### 1. Query Processing
```python
# User asks question
question = "What errors are occurring in my system?"

# Generate query embedding
query_embedding = await embedding_service.generate_embedding(question)
```

### 2. Vector Retrieval
```python
# Search for similar vectors
similar_vectors = await vector_store.search_similar(
    query_embedding=query_embedding,
    project_id=project_id,
    user_id=user_id,
    limit=5,
    similarity_threshold=0.7
)
```

### 3. Context Construction
```python
# Build context from retrieved chunks
context = {
    "question": question,
    "relevant_logs": formatted_chunks,
    "total_chunks": len(chunks),
    "average_similarity": avg_similarity
}
```

### 4. LLM Generation
```python
# Send to LLM with context
llm_request = LLMRequest(
    task=LLMTask.NATURAL_QUERY,
    prompt=question,
    context=context,
    temperature=0.3
)

response = await llm_service.generate_response(llm_request, user, db)
```

### 5. Response Formatting
```python
# Format response with sources
rag_response = RAGResponse(
    answer=response.content,
    sources=formatted_sources,
    confidence_score=combined_confidence,
    model_used=response.model_used
)
```

## 🔍 Chunking Strategies

### Standard Log Format
```
2024-01-15T10:30:45Z ERROR Database connection failed: timeout after 30s
2024-01-15T10:31:12Z WARN High memory usage: 85% of available memory
```

**Chunking**: Preserves log entry boundaries, groups related entries

### JSON Log Format
```json
{"timestamp":"2024-01-15T10:30:45Z","level":"ERROR","message":"Database connection failed","service":"db"}
{"timestamp":"2024-01-15T10:31:12Z","level":"WARN","message":"High memory usage","service":"monitor"}
```

**Chunking**: Groups by logical units, maintains JSON structure

### Apache Log Format
```
192.168.1.1 - - [15/Jan/2024:10:30:45 +0000] "GET /api/users HTTP/1.1" 500 1234
192.168.1.2 - - [15/Jan/2024:10:31:12 +0000] "POST /api/auth HTTP/1.1" 200 5678
```

**Chunking**: Groups by request patterns, preserves IP and timestamp info

## 🎨 Embedding Model

### all-MiniLM-L6-v2 Specifications
- **Dimensions**: 384
- **Model Size**: ~80MB
- **Performance**: Fast inference, good quality
- **Use Case**: General-purpose text embeddings

### Embedding Generation
```python
# Single text embedding
embedding = await embedding_service.generate_embedding("Database connection failed")

# Batch processing
embeddings = await embedding_service.generate_embeddings_batch([
    "Error message 1",
    "Error message 2",
    "Error message 3"
])
```

### Similarity Calculation
```python
# Cosine similarity
similarity = await embedding_service.compute_similarity(
    embedding1, embedding2
)

# Find most similar
similar_items = await embedding_service.find_most_similar(
    query_embedding, candidate_embeddings
)
```

## 🔒 Project Isolation

### Database Level
```sql
-- RLS policies ensure isolation
ALTER TABLE rag_vectors ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_vectors_policy ON rag_vectors
FOR ALL
USING (user_id = current_setting('app.current_user_id')::uuid 
       AND project_id = current_setting('app.current_project_id')::uuid);
```

### Application Level
```python
# Always filter by project_id and user_id
query = db.query(RAGVector).filter(
    and_(
        RAGVector.project_id == project_id,
        RAGVector.user_id == user_id
    )
)
```

### API Level
```python
# Validate project ownership
if not await user_owns_project(user_id, project_id):
    raise HTTPException(403, "Access denied")
```

## 📊 Vector Storage

### Database Schema
```sql
CREATE TABLE rag_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID NOT NULL REFERENCES users(id),
    log_file_id UUID REFERENCES log_files(id),
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Indexes
```sql
-- Vector similarity index
CREATE INDEX ON rag_vectors USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Project isolation index
CREATE INDEX ON rag_vectors (project_id, user_id);

-- Log file index
CREATE INDEX ON rag_vectors (log_file_id);
```

### Vector Operations
```python
# Store vectors
vector_ids = await vector_store.store_vectors(
    vectors=vector_data,
    project_id=project_id,
    user_id=user_id
)

# Search similar
results = await vector_store.search_similar(
    query_embedding=query_embedding,
    project_id=project_id,
    user_id=user_id,
    limit=5
)

# Delete by project
deleted_count = await vector_store.delete_vectors_by_project(
    project_id=project_id,
    user_id=user_id
)
```

## 🔍 Search Types

### 1. Vector Similarity Search
- **Use Case**: Semantic similarity
- **Algorithm**: Cosine similarity
- **Performance**: Fast with IVFFlat index
- **Quality**: High for semantic queries

### 2. Hybrid Search
- **Use Case**: Combined vector + text search
- **Algorithm**: 70% vector + 30% text relevance
- **Performance**: Slightly slower
- **Quality**: Best overall results

### 3. Metadata Search
- **Use Case**: Filter by log level, source, date
- **Algorithm**: Exact matching on metadata
- **Performance**: Very fast
- **Quality**: Precise filtering

### 4. Reranked Search
- **Use Case**: High-quality results
- **Algorithm**: Initial retrieval + reranking
- **Performance**: Slower but better quality
- **Quality**: Highest precision

## ⚙️ Configuration

### Environment Variables

```bash
# Embedding Model
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
EMBEDDING_BATCH_SIZE=32

# Chunking
CHUNK_SIZE=800
MIN_CHUNK_SIZE=500
MAX_CHUNK_SIZE=1000
OVERLAP_SIZE=100

# Vector Search
SIMILARITY_THRESHOLD=0.7
MAX_CHUNKS=5
USE_RERANKING=true

# Database
DATABASE_URL=postgresql://user:pass@localhost/loglytics_db
```

### Model Configuration
```python
# Embedding service settings
embedding_service = EmbeddingService()
embedding_service.batch_size = 32
embedding_service.max_sequence_length = 512
embedding_service.embedding_dim = 384
```

## 🧪 Testing

### Test Coverage

The test suite covers:
- ✅ RAG service health checks
- ✅ Log file indexing and chunking
- ✅ Vector storage and retrieval
- ✅ RAG query processing
- ✅ Similarity and metadata search
- ✅ Batch operations
- ✅ Project isolation
- ✅ Error handling

### Running Tests

```bash
# Run all RAG tests
python backend/scripts/test_rag.py

# Test with custom base URL
python backend/scripts/test_rag.py http://localhost:8000

# Run specific test
python -c "
import asyncio
from backend.scripts.test_rag import RAGTester

async def test():
    async with RAGTester() as tester:
        await tester.authenticate()
        await tester.test_rag_query()

asyncio.run(test())
"
```

## 📈 Performance Optimization

### Embedding Optimization
- **Batch Processing**: Process multiple texts together
- **Model Caching**: Keep model in memory
- **GPU Acceleration**: Use CUDA when available
- **Memory Management**: Clear cache periodically

### Vector Search Optimization
- **Index Tuning**: Optimize IVFFlat parameters
- **Query Optimization**: Use prepared statements
- **Connection Pooling**: Reuse database connections
- **Caching**: Cache frequent queries

### Chunking Optimization
- **Parallel Processing**: Process multiple files
- **Streaming**: Process large files in chunks
- **Memory Efficient**: Process one file at a time
- **Format Detection**: Quick format identification

## 🔧 Development

### Adding New Chunking Strategies

```python
# 1. Add format detection
def _detect_custom_format(self, lines):
    # Custom detection logic
    return 'custom'

# 2. Add parsing method
def _parse_custom_log(self, line, line_number):
    # Custom parsing logic
    return parsed_entry

# 3. Add chunking method
def _create_custom_chunks(self, entries, metadata):
    # Custom chunking logic
    return chunks
```

### Adding New Search Types

```python
# 1. Add search method
async def search_custom(
    self,
    query: str,
    project_id: str,
    user_id: str,
    custom_params: Dict[str, Any]
) -> List[RetrievalResult]:
    # Custom search logic
    pass

# 2. Add API endpoint
@router.post("/search-custom")
async def custom_search(request: CustomSearchRequest):
    # API implementation
    pass
```

### Adding New Metadata Filters

```python
# 1. Add filter method
def _apply_custom_filter(self, query, filter_value):
    return query.filter(
        RAGVector.metadata['custom_field'].astext == filter_value
    )

# 2. Update filter schema
class RAGMetadataFilter(BaseModel):
    custom_field: Optional[str] = Field(None, description="Custom filter")
```

## 🚨 Error Handling

### Common Issues

#### 1. Embedding Model Not Loaded
```python
# Check model health
if not await embedding_service.health_check():
    raise ValueError("Embedding model not available")
```

#### 2. No Vectors Found
```python
# Handle empty results
if not similar_vectors:
    return RAGResponse(
        answer="No relevant information found in your logs.",
        sources=[],
        confidence_score=0.0
    )
```

#### 3. Project Isolation Violation
```python
# Validate project access
if not await user_owns_project(user_id, project_id):
    raise HTTPException(403, "Access denied to project")
```

#### 4. Vector Dimension Mismatch
```python
# Validate embedding dimension
if len(embedding) != self.embedding_dim:
    raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {len(embedding)}")
```

### Error Recovery

```python
# Graceful degradation
try:
    # Try hybrid search
    results = await search_hybrid(query, project_id, user_id)
except Exception:
    # Fallback to simple search
    results = await search_simple(query, project_id, user_id)
```

## 📚 API Documentation

### Request Schemas

```python
class RAGQueryRequest(BaseModel):
    question: str
    project_id: str
    context: Optional[Dict[str, Any]]
    filters: Optional[Dict[str, Any]]
    max_chunks: int = 5
    similarity_threshold: float = 0.7
    use_reranking: bool = True

class RAGIndexRequest(BaseModel):
    log_file_id: str
    project_id: str
    content: str
    file_type: Optional[str]
```

### Response Schemas

```python
class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    model_used: str
    tokens_used: int
    latency_ms: float
    metadata: Dict[str, Any]

class RAGStatsResponse(BaseModel):
    project_id: str
    statistics: Dict[str, Any]
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Slow Embedding Generation
```bash
# Check model loading
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/rag/health

# Check GPU availability
nvidia-smi
```

#### 2. No Search Results
```bash
# Check vector count
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/rag/stats/project-123

# Check similarity threshold
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Authorization: Bearer <token>" \
  -d '{"question": "test", "project_id": "project-123", "similarity_threshold": 0.1}'
```

#### 3. Memory Issues
```bash
# Check system memory
free -h

# Check Python memory usage
ps aux | grep python
```

#### 4. Database Connection Issues
```bash
# Check database status
psql -h localhost -U user -d loglytics_db -c "SELECT 1"

# Check pgvector extension
psql -h localhost -U user -d loglytics_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
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
- **RAM**: 16GB (8GB for embedding model + 8GB for application)
- **CPU**: 4+ cores
- **Storage**: 50GB free space
- **Database**: PostgreSQL 13+ with pgvector extension

#### Recommended Configuration
- **RAM**: 32GB+
- **CPU**: 8+ cores
- **GPU**: NVIDIA RTX 4090 or better (optional)
- **Storage**: SSD with 100GB+ free space
- **Database**: PostgreSQL 15+ with optimized settings

### Deployment Checklist

- [ ] Install PostgreSQL with pgvector extension
- [ ] Configure database connection
- [ ] Download embedding model
- [ ] Set up vector indexes
- [ ] Configure chunking parameters
- [ ] Test RAG functionality
- [ ] Monitor performance
- [ ] Set up logging
- [ ] Configure backup
- [ ] Test failover

## 📞 Support

### Getting Help

1. **Check Logs**: Review application logs for errors
2. **Run Tests**: Execute test suite to identify issues
3. **Check Health**: Use health check endpoints
4. **Verify Database**: Ensure pgvector extension is installed
5. **Contact Support**: Reach out to development team

### Resources

- **API Documentation**: http://localhost:8000/docs
- **Test Suite**: `backend/scripts/test_rag.py`
- **Health Checks**: `/api/v1/rag/health`
- **Statistics**: `/api/v1/rag/stats/{project_id}`

---

**Ready to get started?** Run the test script to verify your RAG system is working correctly!
