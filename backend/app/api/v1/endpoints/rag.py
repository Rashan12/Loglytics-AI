"""
RAG endpoints for Loglytics AI
Handles RAG queries and vector management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from app.database import get_db
from app.schemas.user import UserResponse
from app.schemas.rag import (
    RAGQueryRequest, RAGQueryResponse, RAGStatsResponse,
    RAGIndexRequest, RAGIndexResponse, RAGReindexRequest,
    RAGSearchRequest, RAGSearchResponse, RAGHealthResponse
)
from app.services.auth.dependencies import get_current_active_user
from app.services.rag.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(
    request: RAGQueryRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> RAGQueryResponse:
    """
    Query the RAG system with a question
    
    Args:
        request: RAG query request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        RAG query response
    """
    try:
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        # Process RAG query
        response = await rag_service.query(
            question=request.question,
            project_id=request.project_id,
            user=current_user,
            context=request.context,
            filters=request.filters,
            max_chunks=request.max_chunks,
            similarity_threshold=request.similarity_threshold,
            use_reranking=request.use_reranking
        )
        
        return RAGQueryResponse(
            answer=response.answer,
            sources=response.sources,
            confidence_score=response.confidence_score,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RAG query failed"
        )

@router.get("/stats/{project_id}", response_model=RAGStatsResponse)
async def get_rag_stats(
    project_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> RAGStatsResponse:
    """
    Get RAG statistics for a project
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        RAG statistics
    """
    try:
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        stats = await rag_service.get_project_statistics(
            project_id=project_id,
            user_id=str(current_user.id)
        )
        
        return RAGStatsResponse(
            project_id=project_id,
            statistics=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting RAG stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get RAG statistics"
        )

@router.delete("/clear/{project_id}")
async def clear_project_vectors(
    project_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Clear all vectors for a project
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Clear result
    """
    try:
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        result = await rag_service.clear_project_vectors(
            project_id=project_id,
            user_id=str(current_user.id)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error clearing project vectors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear project vectors"
        )

@router.post("/index", response_model=RAGIndexResponse)
async def index_log_file(
    request: RAGIndexRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> RAGIndexResponse:
    """
    Index a log file for RAG
    
    Args:
        request: Index request
        background_tasks: Background tasks
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Index result
    """
    try:
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        # Process indexing
        result = await rag_service.index_log_file(
            log_file_id=request.log_file_id,
            project_id=request.project_id,
            user_id=str(current_user.id),
            content=request.content,
            file_type=request.file_type
        )
        
        return RAGIndexResponse(
            log_file_id=request.log_file_id,
            project_id=request.project_id,
            success=result.get("success", False),
            chunks_created=result.get("chunks_created", 0),
            vectors_stored=result.get("vectors_stored", 0),
            chunk_statistics=result.get("chunk_statistics", {}),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error indexing log file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to index log file"
        )

@router.post("/reindex/{log_file_id}")
async def reindex_log_file(
    log_file_id: str,
    request: RAGReindexRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reindex a specific log file
    
    Args:
        log_file_id: Log file ID
        request: Reindex request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Reindex result
    """
    try:
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        result = await rag_service.reindex_log_file(
            log_file_id=log_file_id,
            project_id=request.project_id,
            user_id=str(current_user.id),
            content=request.content,
            file_type=request.file_type
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error reindexing log file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reindex log file"
        )

@router.post("/search", response_model=RAGSearchResponse)
async def search_similar_content(
    request: RAGSearchRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> RAGSearchResponse:
    """
    Search for similar content
    
    Args:
        request: Search request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Search results
    """
    try:
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        if request.search_type == "similar":
            results = await rag_service.search_similar_content(
                content=request.query,
                project_id=request.project_id,
                user_id=str(current_user.id),
                limit=request.limit,
                similarity_threshold=request.similarity_threshold
            )
        elif request.search_type == "metadata":
            results = await rag_service.search_by_metadata(
                project_id=request.project_id,
                user_id=str(current_user.id),
                filters=request.filters or {},
                limit=request.limit
            )
        else:
            raise ValueError(f"Invalid search type: {request.search_type}")
        
        return RAGSearchResponse(
            query=request.query,
            search_type=request.search_type,
            results=results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )

@router.get("/health", response_model=RAGHealthResponse)
async def rag_health_check(
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> RAGHealthResponse:
    """
    Check RAG service health
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Health status
    """
    try:
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        health = await rag_service.health_check()
        
        return RAGHealthResponse(
            overall_healthy=health.get("overall_healthy", False),
            pipeline=health.get("pipeline", {}),
            retrieval=health.get("retrieval", {}),
            error=health.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error checking RAG health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check RAG health"
        )

@router.post("/batch-index")
async def batch_index_log_files(
    requests: List[RAGIndexRequest],
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Batch index multiple log files
    
    Args:
        requests: List of index requests
        background_tasks: Background tasks
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Batch index result
    """
    try:
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        results = []
        total_chunks = 0
        total_vectors = 0
        
        for request in requests:
            result = await rag_service.index_log_file(
                log_file_id=request.log_file_id,
                project_id=request.project_id,
                user_id=str(current_user.id),
                content=request.content,
                file_type=request.file_type
            )
            
            results.append({
                "log_file_id": request.log_file_id,
                "success": result.get("success", False),
                "chunks_created": result.get("chunks_created", 0),
                "vectors_stored": result.get("vectors_stored", 0),
                "error": result.get("error")
            })
            
            total_chunks += result.get("chunks_created", 0)
            total_vectors += result.get("vectors_stored", 0)
        
        return {
            "total_files": len(requests),
            "total_chunks": total_chunks,
            "total_vectors": total_vectors,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch indexing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch indexing failed"
        )
