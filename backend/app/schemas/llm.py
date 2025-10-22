"""
LLM schemas for Loglytics AI
Pydantic models for LLM requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class LLMTask(str, Enum):
    """LLM task types"""
    CHAT = "chat"
    LOG_ANALYSIS = "log_analysis"
    ERROR_DETECTION = "error_detection"
    ROOT_CAUSE = "root_cause"
    ANOMALY_DETECTION = "anomaly_detection"
    NATURAL_QUERY = "natural_query"
    SUMMARIZATION = "summarization"

class AnalysisType(str, Enum):
    """Analysis type enumeration"""
    GENERAL = "general"
    ERROR_DETECTION = "error_detection"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ANOMALY = "anomaly"

class LogEntry(BaseModel):
    """Log entry schema"""
    level: str = Field(..., description="Log level (DEBUG, INFO, WARN, ERROR, CRITICAL)")
    message: str = Field(..., description="Log message")
    timestamp: str = Field(..., description="Log timestamp")
    source: Optional[str] = Field(None, description="Log source")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Conversation history")
    max_tokens: Optional[int] = Field(None, ge=1, le=4000, description="Maximum tokens to generate")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    structured_output: bool = Field(False, description="Whether to request structured output")

class ChatResponse(BaseModel):
    """Chat response schema"""
    message: str = Field(..., description="AI response message")
    model_used: str = Field(..., description="Model used for generation")
    tokens_used: int = Field(..., description="Number of tokens used")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured response data")

class AnalysisRequest(BaseModel):
    """Analysis request schema"""
    log_entries: List[LogEntry] = Field(..., min_items=1, description="Log entries to analyze")
    prompt: Optional[str] = Field(None, description="Custom analysis prompt")
    analysis_type: AnalysisType = Field(AnalysisType.GENERAL, description="Type of analysis")
    max_tokens: Optional[int] = Field(None, ge=1, le=4000, description="Maximum tokens to generate")
    temperature: float = Field(0.3, ge=0.0, le=2.0, description="Sampling temperature")
    structured_output: bool = Field(True, description="Whether to request structured output")
    
    # Additional context fields
    error_patterns: Optional[List[str]] = Field(None, description="Error patterns for root cause analysis")
    system_context: Optional[Dict[str, Any]] = Field(None, description="System context information")
    baseline_metrics: Optional[Dict[str, Any]] = Field(None, description="Baseline metrics for anomaly detection")
    query: Optional[str] = Field(None, description="Natural language query")
    timeframe: Optional[str] = Field(None, description="Timeframe for analysis")

class AnalysisResponse(BaseModel):
    """Analysis response schema"""
    analysis: str = Field(..., description="Analysis result")
    model_used: str = Field(..., description="Model used for analysis")
    tokens_used: int = Field(..., description="Number of tokens used")
    latency_ms: float = Field(..., description="Analysis latency in milliseconds")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured analysis data")

class LLMRequest(BaseModel):
    """Generic LLM request schema"""
    task: LLMTask = Field(..., description="LLM task type")
    prompt: str = Field(..., min_length=1, max_length=4000, description="Input prompt")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Conversation history")
    max_tokens: Optional[int] = Field(None, ge=1, le=4000, description="Maximum tokens to generate")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    stream: bool = Field(False, description="Whether to stream the response")
    structured_output: bool = Field(False, description="Whether to request structured output")

class LLMResponse(BaseModel):
    """Generic LLM response schema"""
    content: str = Field(..., description="Generated content")
    model_used: str = Field(..., description="Model used for generation")
    tokens_used: int = Field(..., description="Number of tokens used")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured response data")

class LLMStreamResponse(BaseModel):
    """Streaming LLM response schema"""
    content: str = Field(..., description="Generated content chunk")
    model_used: str = Field(..., description="Model used for generation")
    tokens_used: int = Field(..., description="Number of tokens in this chunk")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured response data")

class ModelInfo(BaseModel):
    """Model information schema"""
    name: str = Field(..., description="Model name")
    provider: str = Field(..., description="Model provider (ollama, maverick)")
    type: str = Field(..., description="Model type (local, cloud)")
    available: bool = Field(..., description="Whether model is available")
    size: Optional[str] = Field(None, description="Model size")
    device: Optional[str] = Field(None, description="Device (cpu, cuda)")
    quantized: Optional[bool] = Field(None, description="Whether model is quantized")

class LLMUsage(BaseModel):
    """LLM usage tracking schema"""
    user_id: str = Field(..., description="User ID")
    model: str = Field(..., description="Model used")
    tokens_used: int = Field(..., description="Tokens used")
    task: str = Field(..., description="Task performed")
    cost: float = Field(0.0, description="Cost in credits")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Usage timestamp")

class LLMHealth(BaseModel):
    """LLM health status schema"""
    ollama: Dict[str, Any] = Field(..., description="Ollama service status")
    maverick: Dict[str, Any] = Field(..., description="Maverick service status")
    overall_healthy: bool = Field(..., description="Overall health status")

class PromptTemplate(BaseModel):
    """Prompt template schema"""
    name: str = Field(..., description="Template name")
    task: LLMTask = Field(..., description="Associated task")
    system_prompt: str = Field(..., description="System prompt")
    few_shot_examples: Optional[str] = Field(None, description="Few-shot examples")
    structured_output_prompt: Optional[str] = Field(None, description="Structured output prompt")

class BatchAnalysisRequest(BaseModel):
    """Batch analysis request schema"""
    analyses: List[AnalysisRequest] = Field(..., min_items=1, max_items=10, description="List of analysis requests")
    parallel: bool = Field(True, description="Whether to process in parallel")

class BatchAnalysisResponse(BaseModel):
    """Batch analysis response schema"""
    results: List[AnalysisResponse] = Field(..., description="Analysis results")
    total_tokens_used: int = Field(..., description="Total tokens used")
    total_latency_ms: float = Field(..., description="Total latency in milliseconds")
    models_used: List[str] = Field(..., description="Models used")

class LLMConfig(BaseModel):
    """LLM configuration schema"""
    default_model: str = Field(..., description="Default model to use")
    max_tokens: int = Field(1000, description="Default maximum tokens")
    temperature: float = Field(0.7, description="Default temperature")
    timeout: int = Field(60, description="Request timeout in seconds")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    enable_streaming: bool = Field(True, description="Whether streaming is enabled")

class ErrorAnalysis(BaseModel):
    """Error analysis schema"""
    errors: List[Dict[str, Any]] = Field(..., description="List of errors found")
    summary: Dict[str, Any] = Field(..., description="Error summary")
    recommendations: List[str] = Field(..., description="Recommendations")

class AnomalyAnalysis(BaseModel):
    """Anomaly analysis schema"""
    anomalies: List[Dict[str, Any]] = Field(..., description="List of anomalies found")
    summary: Dict[str, Any] = Field(..., description="Anomaly summary")
    risk_level: str = Field(..., description="Overall risk level")

class RootCauseAnalysis(BaseModel):
    """Root cause analysis schema"""
    root_cause: str = Field(..., description="Identified root cause")
    evidence: List[str] = Field(..., description="Supporting evidence")
    contributing_factors: List[str] = Field(..., description="Contributing factors")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    recommendations: List[str] = Field(..., description="Recommendations")

class LogSummary(BaseModel):
    """Log summary schema"""
    summary: str = Field(..., description="Summary text")
    key_metrics: Dict[str, Any] = Field(..., description="Key metrics")
    highlights: List[str] = Field(..., description="Key highlights")
    recommendations: List[str] = Field(..., description="Recommendations")
    timeframe: str = Field(..., description="Analysis timeframe")

class QueryResult(BaseModel):
    """Query result schema"""
    query: str = Field(..., description="Original query")
    interpretation: str = Field(..., description="Query interpretation")
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    summary: str = Field(..., description="Result summary")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
