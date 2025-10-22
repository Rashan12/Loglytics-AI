"""
RAG schemas for Loglytics AI
Pydantic models for RAG requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class SearchType(str, Enum):
    """Search type enumeration"""
    SIMILAR = "similar"
    METADATA = "metadata"

class RAGQueryRequest(BaseModel):
    """RAG query request schema"""
    question: str = Field(..., min_length=1, max_length=1000, description="User question")
    project_id: str = Field(..., description="Project ID for isolation")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    max_chunks: int = Field(5, ge=1, le=10, description="Maximum number of chunks to retrieve")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity threshold")
    use_reranking: bool = Field(True, description="Whether to use reranking")

class RAGQueryResponse(BaseModel):
    """RAG query response schema"""
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(..., description="Source chunks used")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    model_used: str = Field(..., description="Model used for generation")
    tokens_used: int = Field(..., description="Number of tokens used")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class RAGStatsResponse(BaseModel):
    """RAG statistics response schema"""
    project_id: str = Field(..., description="Project ID")
    statistics: Dict[str, Any] = Field(..., description="RAG statistics")

class RAGIndexRequest(BaseModel):
    """RAG index request schema"""
    log_file_id: str = Field(..., description="Log file ID")
    project_id: str = Field(..., description="Project ID")
    content: str = Field(..., min_length=1, description="Log file content")
    file_type: Optional[str] = Field(None, description="File type (json, standard, apache, etc.)")

class RAGIndexResponse(BaseModel):
    """RAG index response schema"""
    log_file_id: str = Field(..., description="Log file ID")
    project_id: str = Field(..., description="Project ID")
    success: bool = Field(..., description="Whether indexing was successful")
    chunks_created: int = Field(..., description="Number of chunks created")
    vectors_stored: int = Field(..., description="Number of vectors stored")
    chunk_statistics: Dict[str, Any] = Field(default_factory=dict, description="Chunk statistics")
    error: Optional[str] = Field(None, description="Error message if failed")

class RAGReindexRequest(BaseModel):
    """RAG reindex request schema"""
    project_id: str = Field(..., description="Project ID")
    content: str = Field(..., min_length=1, description="Log file content")
    file_type: Optional[str] = Field(None, description="File type")

class RAGSearchRequest(BaseModel):
    """RAG search request schema"""
    query: str = Field(..., min_length=1, description="Search query")
    project_id: str = Field(..., description="Project ID for isolation")
    search_type: SearchType = Field(SearchType.SIMILAR, description="Type of search")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")
    similarity_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Minimum similarity threshold")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters for metadata search")

class RAGSearchResponse(BaseModel):
    """RAG search response schema"""
    query: str = Field(..., description="Search query")
    search_type: SearchType = Field(..., description="Type of search performed")
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")

class RAGHealthResponse(BaseModel):
    """RAG health response schema"""
    overall_healthy: bool = Field(..., description="Overall health status")
    pipeline: Dict[str, Any] = Field(default_factory=dict, description="Pipeline health")
    retrieval: Dict[str, Any] = Field(default_factory=dict, description="Retrieval service health")
    error: Optional[str] = Field(None, description="Error message if unhealthy")

class RAGVectorInfo(BaseModel):
    """RAG vector information schema"""
    vector_id: str = Field(..., description="Vector ID")
    content: str = Field(..., description="Vector content")
    similarity_score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Vector metadata")
    log_file_id: Optional[str] = Field(None, description="Associated log file ID")
    created_at: datetime = Field(..., description="Creation timestamp")

class RAGChunkInfo(BaseModel):
    """RAG chunk information schema"""
    chunk_id: int = Field(..., description="Chunk ID")
    content: str = Field(..., description="Chunk content")
    similarity_score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    log_file_id: Optional[str] = Field(None, description="Associated log file ID")
    vector_id: str = Field(..., description="Vector ID")

class RAGSourceInfo(BaseModel):
    """RAG source information schema"""
    chunk_id: int = Field(..., description="Chunk ID")
    content_preview: str = Field(..., description="Content preview")
    similarity_score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Source metadata")
    log_file_id: Optional[str] = Field(None, description="Associated log file ID")
    vector_id: str = Field(..., description="Vector ID")

class RAGBatchIndexRequest(BaseModel):
    """RAG batch index request schema"""
    log_files: List[RAGIndexRequest] = Field(..., min_items=1, max_items=10, description="List of log files to index")
    project_id: str = Field(..., description="Project ID")

class RAGBatchIndexResponse(BaseModel):
    """RAG batch index response schema"""
    total_files: int = Field(..., description="Total number of files processed")
    total_chunks: int = Field(..., description="Total number of chunks created")
    total_vectors: int = Field(..., description="Total number of vectors stored")
    results: List[Dict[str, Any]] = Field(..., description="Individual file results")

class RAGFilterRequest(BaseModel):
    """RAG filter request schema"""
    project_id: str = Field(..., description="Project ID for isolation")
    filters: Dict[str, Any] = Field(..., description="Metadata filters")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")

class RAGFilterResponse(BaseModel):
    """RAG filter response schema"""
    project_id: str = Field(..., description="Project ID")
    filters: Dict[str, Any] = Field(..., description="Applied filters")
    results: List[RAGVectorInfo] = Field(..., description="Filtered results")
    total_results: int = Field(..., description="Total number of results")

class RAGSimilarityRequest(BaseModel):
    """RAG similarity request schema"""
    content: str = Field(..., min_length=1, description="Reference content")
    project_id: str = Field(..., description="Project ID for isolation")
    limit: int = Field(5, ge=1, le=20, description="Maximum number of results")
    similarity_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Minimum similarity threshold")

class RAGSimilarityResponse(BaseModel):
    """RAG similarity response schema"""
    content: str = Field(..., description="Reference content")
    project_id: str = Field(..., description="Project ID")
    similar_content: List[RAGVectorInfo] = Field(..., description="Similar content")
    total_results: int = Field(..., description="Total number of results")

class RAGMetadataFilter(BaseModel):
    """RAG metadata filter schema"""
    log_level: Optional[str] = Field(None, description="Filter by log level")
    source: Optional[str] = Field(None, description="Filter by source")
    date_range: Optional[Dict[str, str]] = Field(None, description="Filter by date range")
    file_type: Optional[str] = Field(None, description="Filter by file type")

class RAGChunkStatistics(BaseModel):
    """RAG chunk statistics schema"""
    total_chunks: int = Field(..., description="Total number of chunks")
    total_size: int = Field(..., description="Total size in bytes")
    average_size: float = Field(..., description="Average chunk size")
    min_size: int = Field(..., description="Minimum chunk size")
    max_size: int = Field(..., description="Maximum chunk size")
    total_entries: int = Field(..., description="Total log entries")
    average_entries_per_chunk: float = Field(..., description="Average entries per chunk")

class RAGVectorStatistics(BaseModel):
    """RAG vector statistics schema"""
    total_vectors: int = Field(..., description="Total number of vectors")
    total_size_bytes: int = Field(..., description="Total size in bytes")
    log_files: int = Field(..., description="Number of log files")
    vectors_by_log_file: List[Dict[str, Any]] = Field(..., description="Vectors by log file")
    embedding_dimension: int = Field(..., description="Embedding dimension")
    model_info: Dict[str, Any] = Field(..., description="Model information")

class RAGPipelineStatistics(BaseModel):
    """RAG pipeline statistics schema"""
    retrieval: RAGVectorStatistics = Field(..., description="Retrieval statistics")
    llm_health: Dict[str, Any] = Field(..., description="LLM health status")
    pipeline_status: str = Field(..., description="Pipeline status")

class RAGQueryMetadata(BaseModel):
    """RAG query metadata schema"""
    chunks_retrieved: int = Field(..., description="Number of chunks retrieved")
    similarity_scores: List[float] = Field(..., description="Similarity scores")
    reranking_used: bool = Field(..., description="Whether reranking was used")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filters applied")
    query_embedding_dim: int = Field(384, description="Query embedding dimension")

class RAGErrorResponse(BaseModel):
    """RAG error response schema"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
