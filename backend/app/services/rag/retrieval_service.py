"""
Retrieval Service for Loglytics AI
Semantic search and ranking for RAG system
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rag.vector_store import VectorStore
from app.services.rag.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Result from retrieval operation"""
    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    vector_id: str
    log_file_id: Optional[str] = None
    combined_score: Optional[float] = None
    text_score: Optional[float] = None

class RetrievalService:
    """Service for semantic search and retrieval"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_store = VectorStore(db)
        self.embedding_service = None
    
    async def initialize(self):
        """Initialize the retrieval service"""
        self.embedding_service = await get_embedding_service()
    
    async def retrieve_relevant_chunks(
        self,
        query: str,
        project_id: str,
        user_id: str,
        limit: int = 5,
        similarity_threshold: float = 0.05,
        filters: Optional[Dict[str, Any]] = None,
        use_hybrid_search: bool = True
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: User query
            project_id: Project ID for isolation
            user_id: User ID for isolation
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            filters: Additional metadata filters
            use_hybrid_search: Whether to use hybrid search
            
        Returns:
            List of retrieval results
        """
        try:
            if not self.embedding_service:
                await self.initialize()
            
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Perform search
            if use_hybrid_search:
                search_results = await self.vector_store.search_hybrid(
                    query_embedding=query_embedding,
                    project_id=project_id,
                    user_id=user_id,
                    text_query=query,
                    limit=limit,
                    similarity_threshold=similarity_threshold,
                    filters=filters
                )
            else:
                search_results = await self.vector_store.search_similar(
                    query_embedding=query_embedding,
                    project_id=project_id,
                    user_id=user_id,
                    limit=limit,
                    similarity_threshold=similarity_threshold,
                    filters=filters
                )
            
            # Convert to RetrievalResult objects
            results = []
            for result in search_results:
                retrieval_result = RetrievalResult(
                    content=result['content'],
                    similarity_score=result['similarity'],
                    metadata=result['metadata'],
                    vector_id=result['id'],
                    log_file_id=result.get('log_file_id'),
                    combined_score=result.get('combined_score'),
                    text_score=result.get('text_score')
                )
                results.append(retrieval_result)
            
            logger.info(f"Retrieved {len(results)} relevant chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {e}")
            raise
    
    async def retrieve_with_reranking(
        self,
        query: str,
        project_id: str,
        user_id: str,
        initial_limit: int = 20,
        final_limit: int = 5,
        similarity_threshold: float = 0.6,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve and rerank results for better quality
        
        Args:
            query: User query
            project_id: Project ID for isolation
            user_id: User ID for isolation
            initial_limit: Number of initial results to retrieve
            final_limit: Number of final results after reranking
            similarity_threshold: Minimum similarity score
            filters: Additional metadata filters
            
        Returns:
            List of reranked retrieval results
        """
        try:
            # Get initial results
            initial_results = await self.retrieve_relevant_chunks(
                query=query,
                project_id=project_id,
                user_id=user_id,
                limit=initial_limit,
                similarity_threshold=similarity_threshold,
                filters=filters,
                use_hybrid_search=True
            )
            
            if not initial_results:
                return []
            
            # Rerank results using cross-encoder (if available)
            reranked_results = await self._rerank_results(query, initial_results)
            
            # Return top results
            return reranked_results[:final_limit]
            
        except Exception as e:
            logger.error(f"Error in retrieval with reranking: {e}")
            raise
    
    async def _rerank_results(
        self, 
        query: str, 
        results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        Rerank results using cross-encoder for better quality
        
        Args:
            query: User query
            results: Initial retrieval results
            
        Returns:
            Reranked results
        """
        try:
            # For now, use a simple reranking based on content quality
            # In production, you would use a cross-encoder model
            
            reranked = []
            for result in results:
                # Calculate content quality score
                quality_score = self._calculate_content_quality(result.content)
                
                # Combine similarity and quality scores
                # Weight: 70% similarity, 30% quality
                final_score = (0.7 * result.similarity_score) + (0.3 * quality_score)
                
                # Create new result with reranked score
                reranked_result = RetrievalResult(
                    content=result.content,
                    similarity_score=result.similarity_score,
                    metadata=result.metadata,
                    vector_id=result.vector_id,
                    log_file_id=result.log_file_id,
                    combined_score=final_score,
                    text_score=result.text_score
                )
                reranked.append(reranked_result)
            
            # Sort by final score
            reranked.sort(key=lambda x: x.combined_score or x.similarity_score, reverse=True)
            
            return reranked
            
        except Exception as e:
            logger.error(f"Error reranking results: {e}")
            return results  # Return original results if reranking fails
    
    def _calculate_content_quality(self, content: str) -> float:
        """
        Calculate content quality score
        
        Args:
            content: Text content
            
        Returns:
            Quality score (0-1)
        """
        try:
            if not content:
                return 0.0
            
            score = 0.0
            
            # Length score (optimal length gets higher score)
            length = len(content)
            if 100 <= length <= 1000:
                score += 0.3
            elif 50 <= length < 100 or 1000 < length <= 2000:
                score += 0.2
            else:
                score += 0.1
            
            # Structure score (presence of structured elements)
            if any(keyword in content.lower() for keyword in ['error', 'warning', 'info', 'debug']):
                score += 0.2
            
            if any(keyword in content.lower() for keyword in ['timestamp', 'time', 'date']):
                score += 0.1
            
            if any(keyword in content.lower() for keyword in ['source', 'service', 'component']):
                score += 0.1
            
            # Readability score (simple heuristic)
            words = content.split()
            if words:
                avg_word_length = sum(len(word) for word in words) / len(words)
                if 3 <= avg_word_length <= 8:
                    score += 0.2
                elif 2 <= avg_word_length < 3 or 8 < avg_word_length <= 12:
                    score += 0.1
            
            # Completeness score (presence of complete sentences)
            sentences = content.split('.')
            if len(sentences) > 1:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating content quality: {e}")
            return 0.5  # Default score
    
    async def get_retrieval_statistics(
        self,
        project_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get retrieval statistics for a project
        
        Args:
            project_id: Project ID
            user_id: User ID for isolation
            
        Returns:
            Statistics dictionary
        """
        try:
            # Get vector store statistics
            vector_stats = await self.vector_store.get_vector_statistics(
                project_id=project_id,
                user_id=user_id
            )
            
            # Add retrieval-specific statistics
            stats = {
                'total_vectors': vector_stats['total_vectors'],
                'total_size_bytes': vector_stats['total_size_bytes'],
                'log_files': vector_stats['log_files'],
                'vectors_by_log_file': vector_stats['vectors_by_log_file'],
                'embedding_dimension': self.embedding_service.get_embedding_dimension() if self.embedding_service else 384,
                'model_info': self.embedding_service.get_model_info() if self.embedding_service else {}
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting retrieval statistics: {e}")
            raise
    
    async def search_by_metadata(
        self,
        project_id: str,
        user_id: str,
        filters: Dict[str, Any],
        limit: int = 10
    ) -> List[RetrievalResult]:
        """
        Search vectors by metadata filters only
        
        Args:
            project_id: Project ID for isolation
            user_id: User ID for isolation
            filters: Metadata filters
            limit: Maximum number of results
            
        Returns:
            List of retrieval results
        """
        try:
            # Use vector store to search with filters only
            search_results = await self.vector_store.search_similar(
                query_embedding=[0.0] * 384,  # Dummy embedding
                project_id=project_id,
                user_id=user_id,
                limit=limit,
                similarity_threshold=0.0,  # No similarity threshold
                filters=filters
            )
            
            # Convert to RetrievalResult objects
            results = []
            for result in search_results:
                retrieval_result = RetrievalResult(
                    content=result['content'],
                    similarity_score=result['similarity'],
                    metadata=result['metadata'],
                    vector_id=result['id'],
                    log_file_id=result.get('log_file_id')
                )
                results.append(retrieval_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching by metadata: {e}")
            raise
    
    async def get_similar_chunks(
        self,
        content: str,
        project_id: str,
        user_id: str,
        limit: int = 5,
        similarity_threshold: float = 0.8
    ) -> List[RetrievalResult]:
        """
        Find chunks similar to given content
        
        Args:
            content: Reference content
            project_id: Project ID for isolation
            user_id: User ID for isolation
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar chunks
        """
        try:
            if not self.embedding_service:
                await self.initialize()
            
            # Generate embedding for the content
            content_embedding = await self.embedding_service.generate_embedding(content)
            
            # Search for similar vectors
            search_results = await self.vector_store.search_similar(
                query_embedding=content_embedding,
                project_id=project_id,
                user_id=user_id,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            # Convert to RetrievalResult objects
            results = []
            for result in search_results:
                retrieval_result = RetrievalResult(
                    content=result['content'],
                    similarity_score=result['similarity'],
                    metadata=result['metadata'],
                    vector_id=result['id'],
                    log_file_id=result.get('log_file_id')
                )
                results.append(retrieval_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {e}")
            raise
