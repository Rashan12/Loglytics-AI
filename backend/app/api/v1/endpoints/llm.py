"""
LLM endpoints for Loglytics AI
Handles LLM requests and responses
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from app.database import get_db
from app.schemas.user import UserResponse
from app.schemas.llm import (
    LLMRequest, LLMResponse, LLMStreamResponse, 
    ChatRequest, ChatResponse, AnalysisRequest, AnalysisResponse
)
from app.services.auth.dependencies import get_current_active_user
from app.services.llm.llm_service import UnifiedLLMService, LLMTask, LLMRequest as ServiceLLMRequest

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Chat completion endpoint
    
    Args:
        request: Chat request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Chat response
    """
    try:
        llm_service = UnifiedLLMService(db)
        
        # Create service request
        service_request = ServiceLLMRequest(
            task=LLMTask.CHAT,
            prompt=request.message,
            context=request.context,
            conversation_history=request.conversation_history,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
            structured_output=request.structured_output
        )
        
        # Generate response
        response = await llm_service.generate_response(service_request, current_user, db)
        
        return ChatResponse(
            message=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            confidence_score=response.confidence_score,
            metadata=response.metadata,
            structured_data=response.structured_data
        )
        
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat completion failed"
        )

@router.post("/chat/stream")
async def chat_completion_stream(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Streaming chat completion endpoint
    
    Args:
        request: Chat request
        current_user: Current authenticated user
        db: Database session
        
    Yields:
        Streaming chat responses
    """
    try:
        llm_service = UnifiedLLMService(db)
        
        # Create service request
        service_request = ServiceLLMRequest(
            task=LLMTask.CHAT,
            prompt=request.message,
            context=request.context,
            conversation_history=request.conversation_history,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True,
            structured_output=request.structured_output
        )
        
        # Generate streaming response
        async for chunk in llm_service.generate_response(service_request, current_user, db):
            yield LLMStreamResponse(
                content=chunk.content,
                model_used=chunk.model_used,
                tokens_used=chunk.tokens_used,
                latency_ms=chunk.latency_ms,
                confidence_score=chunk.confidence_score,
                metadata=chunk.metadata,
                structured_data=chunk.structured_data
            )
        
    except Exception as e:
        logger.error(f"Error in streaming chat completion: {e}")
        yield LLMStreamResponse(
            content=f"Error: {str(e)}",
            model_used="error",
            tokens_used=0,
            latency_ms=0,
            confidence_score=0.0,
            metadata={"error": str(e)}
        )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_logs(
    request: AnalysisRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Analyze log entries
    
    Args:
        request: Analysis request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Analysis response
    """
    try:
        llm_service = UnifiedLLMService(db)
        
        # Create service request
        service_request = ServiceLLMRequest(
            task=LLMTask.LOG_ANALYSIS,
            prompt=request.prompt or "Analyze these log entries",
            context={
                "log_entries": request.log_entries,
                "analysis_type": request.analysis_type
            },
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
            structured_output=request.structured_output
        )
        
        # Generate response
        response = await llm_service.generate_response(service_request, current_user, db)
        
        return AnalysisResponse(
            analysis=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            confidence_score=response.confidence_score,
            metadata=response.metadata,
            structured_data=response.structured_data
        )
        
    except Exception as e:
        logger.error(f"Error in log analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Log analysis failed"
        )

@router.post("/detect-errors", response_model=AnalysisResponse)
async def detect_errors(
    request: AnalysisRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Detect errors in log entries
    
    Args:
        request: Analysis request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Error detection response
    """
    try:
        llm_service = UnifiedLLMService(db)
        
        # Create service request
        service_request = ServiceLLMRequest(
            task=LLMTask.ERROR_DETECTION,
            prompt=request.prompt or "Detect errors in these log entries",
            context={
                "log_entries": request.log_entries,
                "analysis_type": "error_detection"
            },
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
            structured_output=request.structured_output
        )
        
        # Generate response
        response = await llm_service.generate_response(service_request, current_user, db)
        
        return AnalysisResponse(
            analysis=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            confidence_score=response.confidence_score,
            metadata=response.metadata,
            structured_data=response.structured_data
        )
        
    except Exception as e:
        logger.error(f"Error in error detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error detection failed"
        )

@router.post("/root-cause", response_model=AnalysisResponse)
async def root_cause_analysis(
    request: AnalysisRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Perform root cause analysis
    
    Args:
        request: Analysis request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Root cause analysis response
    """
    try:
        llm_service = UnifiedLLMService(db)
        
        # Create service request
        service_request = ServiceLLMRequest(
            task=LLMTask.ROOT_CAUSE,
            prompt=request.prompt or "Perform root cause analysis",
            context={
                "log_entries": request.log_entries,
                "error_patterns": request.error_patterns or [],
                "system_context": request.system_context or {}
            },
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
            structured_output=request.structured_output
        )
        
        # Generate response
        response = await llm_service.generate_response(service_request, current_user, db)
        
        return AnalysisResponse(
            analysis=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            confidence_score=response.confidence_score,
            metadata=response.metadata,
            structured_data=response.structured_data
        )
        
    except Exception as e:
        logger.error(f"Error in root cause analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Root cause analysis failed"
        )

@router.post("/detect-anomalies", response_model=AnalysisResponse)
async def detect_anomalies(
    request: AnalysisRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Detect anomalies in log entries
    
    Args:
        request: Analysis request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Anomaly detection response
    """
    try:
        llm_service = UnifiedLLMService(db)
        
        # Create service request
        service_request = ServiceLLMRequest(
            task=LLMTask.ANOMALY_DETECTION,
            prompt=request.prompt or "Detect anomalies in these log entries",
            context={
                "log_entries": request.log_entries,
                "baseline_metrics": request.baseline_metrics or {}
            },
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
            structured_output=request.structured_output
        )
        
        # Generate response
        response = await llm_service.generate_response(service_request, current_user, db)
        
        return AnalysisResponse(
            analysis=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            confidence_score=response.confidence_score,
            metadata=response.metadata,
            structured_data=response.structured_data
        )
        
    except Exception as e:
        logger.error(f"Error in anomaly detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Anomaly detection failed"
        )

@router.post("/query", response_model=AnalysisResponse)
async def natural_language_query(
    request: AnalysisRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Process natural language queries on log data
    
    Args:
        request: Analysis request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Query response
    """
    try:
        llm_service = UnifiedLLMService(db)
        
        # Create service request
        service_request = ServiceLLMRequest(
            task=LLMTask.NATURAL_QUERY,
            prompt=request.prompt or "Answer this question about the log data",
            context={
                "log_entries": request.log_entries,
                "query": request.query
            },
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
            structured_output=request.structured_output
        )
        
        # Generate response
        response = await llm_service.generate_response(service_request, current_user, db)
        
        return AnalysisResponse(
            analysis=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            confidence_score=response.confidence_score,
            metadata=response.metadata,
            structured_data=response.structured_data
        )
        
    except Exception as e:
        logger.error(f"Error in natural language query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query processing failed"
        )

@router.post("/summarize", response_model=AnalysisResponse)
async def summarize_logs(
    request: AnalysisRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Summarize log entries
    
    Args:
        request: Analysis request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Summary response
    """
    try:
        llm_service = UnifiedLLMService(db)
        
        # Create service request
        service_request = ServiceLLMRequest(
            task=LLMTask.SUMMARIZATION,
            prompt=request.prompt or "Summarize these log entries",
            context={
                "log_entries": request.log_entries,
                "timeframe": request.timeframe or "recent"
            },
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
            structured_output=request.structured_output
        )
        
        # Generate response
        response = await llm_service.generate_response(service_request, current_user, db)
        
        return AnalysisResponse(
            analysis=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            confidence_score=response.confidence_score,
            metadata=response.metadata,
            structured_data=response.structured_data
        )
        
    except Exception as e:
        logger.error(f"Error in log summarization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Log summarization failed"
        )

@router.get("/models")
async def get_available_models(
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get available LLM models
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of available models
    """
    try:
        llm_service = UnifiedLLMService(db)
        models = await llm_service.get_available_models()
        return models
        
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available models"
        )

@router.get("/health")
async def llm_health_check(
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Check LLM service health
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Health status
    """
    try:
        llm_service = UnifiedLLMService(db)
        health = await llm_service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"Error checking LLM health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check LLM health"
        )
