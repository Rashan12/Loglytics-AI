"""
RAG Service for Loglytics AI
Main RAG orchestration service
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.rag.rag_pipeline import RAGPipeline, RAGQuery, RAGResponse
from app.services.rag.retrieval_service import RetrievalService
from app.services.rag.vector_store import VectorStore
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)

class RAGService:
    """Main RAG orchestration service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rag_pipeline = RAGPipeline(db)
        self.retrieval_service = RetrievalService(db)
        self.vector_store = VectorStore(db)
    
    async def initialize(self):
        """Initialize the RAG service"""
        await self.rag_pipeline.initialize()
    
    async def query(
        self,
        question: str,
        project_id: str,
        user: UserResponse,
        context: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None,
        max_chunks: int = 5,
        similarity_threshold: float = 0.7,
        use_reranking: bool = True
    ) -> RAGResponse:
        """
        Process a RAG query
        
        Args:
            question: User question
            project_id: Project ID for isolation
            user: User making the query
            context: Additional context
            filters: Metadata filters
            max_chunks: Maximum number of chunks to retrieve
            similarity_threshold: Minimum similarity threshold
            use_reranking: Whether to use reranking
            
        Returns:
            RAG response
        """
        try:
            # Create RAG query
            rag_query = RAGQuery(
                question=question,
                project_id=project_id,
                user_id=str(user.id),
                context=context,
                filters=filters,
                max_chunks=max_chunks,
                similarity_threshold=similarity_threshold,
                use_reranking=use_reranking
            )
            
            # Process through pipeline
            response = await self.rag_pipeline.query(rag_query, user)
            
            logger.info(f"RAG query processed for project {project_id}: {len(response.sources)} sources")
            return response
            
        except Exception as e:
            logger.error(f"Error processing RAG query: {e}")
            return RAGResponse(
                answer=f"Error processing your question: {str(e)}",
                sources=[],
                confidence_score=0.0,
                model_used="error",
                tokens_used=0,
                latency_ms=0.0,
                metadata={"error": str(e)}
            )
    
    async def index_log_file(
        self,
        log_file_id: str,
        project_id: str,
        user_id: str,
        content: str,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Index a log file for RAG
        
        Args:
            log_file_id: Log file ID
            project_id: Project ID
            user_id: User ID
            content: Log file content
            file_type: File type
            
        Returns:
            Indexing result
        """
        try:
            result = await self.rag_pipeline.process_log_file_for_rag(
                log_file_id=log_file_id,
                project_id=project_id,
                user_id=user_id,
                content=content,
                file_type=file_type
            )
            
            logger.info(f"Indexed log file {log_file_id} for project {project_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error indexing log file: {e}")
            return {"error": str(e)}
    
    async def reindex_log_file(
        self,
        log_file_id: str,
        project_id: str,
        user_id: str,
        content: str,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reindex a log file
        
        Args:
            log_file_id: Log file ID
            project_id: Project ID
            user_id: User ID
            content: Log file content
            file_type: File type
            
        Returns:
            Reindexing result
        """
        try:
            result = await self.rag_pipeline.reindex_log_file(
                log_file_id=log_file_id,
                project_id=project_id,
                user_id=user_id,
                content=content,
                file_type=file_type
            )
            
            logger.info(f"Reindexed log file {log_file_id} for project {project_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error reindexing log file: {e}")
            return {"error": str(e)}
    
    async def clear_project_vectors(
        self,
        project_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Clear all vectors for a project
        
        Args:
            project_id: Project ID
            user_id: User ID for isolation
            
        Returns:
            Clear result
        """
        try:
            result = await self.rag_pipeline.clear_project_vectors(
                project_id=project_id,
                user_id=user_id
            )
            
            logger.info(f"Cleared vectors for project {project_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error clearing project vectors: {e}")
            return {"error": str(e)}
    
    async def get_project_statistics(
        self,
        project_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get RAG statistics for a project
        
        Args:
            project_id: Project ID
            user_id: User ID for isolation
            
        Returns:
            Statistics dictionary
        """
        try:
            stats = await self.rag_pipeline.get_pipeline_statistics(
                project_id=project_id,
                user_id=user_id
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting project statistics: {e}")
            return {"error": str(e)}
    
    async def search_similar_content(
        self,
        content: str,
        project_id: str,
        user_id: str,
        limit: int = 5,
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Find content similar to given text
        
        Args:
            content: Reference content
            project_id: Project ID for isolation
            user_id: User ID for isolation
            limit: Maximum number of results
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of similar content
        """
        try:
            results = await self.retrieval_service.get_similar_chunks(
                content=content,
                project_id=project_id,
                user_id=user_id,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            # Format results
            similar_content = []
            for result in results:
                similar_content.append({
                    "content": result.content,
                    "similarity_score": result.similarity_score,
                    "metadata": result.metadata,
                    "log_file_id": result.log_file_id,
                    "vector_id": result.vector_id
                })
            
            return similar_content
            
        except Exception as e:
            logger.error(f"Error searching similar content: {e}")
            return []
    
    async def search_by_metadata(
        self,
        project_id: str,
        user_id: str,
        filters: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search vectors by metadata filters
        
        Args:
            project_id: Project ID for isolation
            user_id: User ID for isolation
            filters: Metadata filters
            limit: Maximum number of results
            
        Returns:
            List of matching content
        """
        try:
            results = await self.retrieval_service.search_by_metadata(
                project_id=project_id,
                user_id=user_id,
                filters=filters,
                limit=limit
            )
            
            # Format results
            matching_content = []
            for result in results:
                matching_content.append({
                    "content": result.content,
                    "similarity_score": result.similarity_score,
                    "metadata": result.metadata,
                    "log_file_id": result.log_file_id,
                    "vector_id": result.vector_id
                })
            
            return matching_content
            
        except Exception as e:
            logger.error(f"Error searching by metadata: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check RAG service health"""
        try:
            # Check pipeline health
            pipeline_stats = await self.rag_pipeline.get_pipeline_statistics(
                project_id="health_check",
                user_id="health_check"
            )
            
            # Check retrieval service
            retrieval_healthy = await self.retrieval_service.retrieval_service.health_check()
            
            return {
                "pipeline": pipeline_stats,
                "retrieval": retrieval_healthy,
                "overall_healthy": retrieval_healthy
            }
            
        except Exception as e:
            logger.error(f"Error checking RAG health: {e}")
            return {
                "overall_healthy": False,
                "error": str(e)
            }