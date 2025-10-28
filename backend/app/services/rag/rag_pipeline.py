"""
RAG Pipeline for Loglytics AI
End-to-end RAG query pipeline
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.services.rag.retrieval_service import RetrievalService, RetrievalResult
from app.services.llm.llm_service import UnifiedLLMService, LLMTask, LLMRequest as ServiceLLMRequest
from app.services.llm.prompt_templates import PromptTemplates
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)

@dataclass
class RAGQuery:
    """RAG query structure"""
    question: str
    project_id: str
    user_id: str
    context: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    max_chunks: int = 5
    similarity_threshold: float = 0.05
    use_reranking: bool = True

@dataclass
class RAGResponse:
    """RAG response structure"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    model_used: str
    tokens_used: int
    latency_ms: float
    metadata: Dict[str, Any]

class RAGPipeline:
    """End-to-end RAG query pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
        self.retrieval_service = RetrievalService(db)
        self.llm_service = UnifiedLLMService(db)
        self.prompt_templates = PromptTemplates()
    
    async def initialize(self):
        """Initialize the RAG pipeline"""
        await self.retrieval_service.initialize()
    
    async def query(
        self,
        rag_query: RAGQuery,
        user: UserResponse
    ) -> RAGResponse:
        """
        Process a RAG query end-to-end
        
        Args:
            rag_query: RAG query parameters
            user: User making the query
            
        Returns:
            RAG response with answer and sources
        """
        try:
            # Step 1: Retrieve relevant chunks
            relevant_chunks = await self.retrieval_service.retrieve_relevant_chunks(
                query=rag_query.question,
                project_id=rag_query.project_id,
                user_id=rag_query.user_id,
                limit=rag_query.max_chunks,
                similarity_threshold=rag_query.similarity_threshold,
                filters=rag_query.filters,
                use_hybrid_search=True
            )
            
            if not relevant_chunks:
                return RAGResponse(
                    answer="I couldn't find any relevant information in your logs to answer this question.",
                    sources=[],
                    confidence_score=0.0,
                    model_used="none",
                    tokens_used=0,
                    latency_ms=0.0,
                    metadata={"error": "No relevant chunks found"}
                )
            
            # Step 2: Rerank results if requested
            if rag_query.use_reranking and len(relevant_chunks) > 3:
                relevant_chunks = await self.retrieval_service.retrieve_with_reranking(
                    query=rag_query.question,
                    project_id=rag_query.project_id,
                    user_id=rag_query.user_id,
                    initial_limit=rag_query.max_chunks * 2,
                    final_limit=rag_query.max_chunks,
                    similarity_threshold=rag_query.similarity_threshold,
                    filters=rag_query.filters
                )
            
            # Step 3: Construct context for LLM
            context = self._construct_context(relevant_chunks, rag_query.question)
            
            # Step 4: Generate answer using LLM
            llm_request = ServiceLLMRequest(
                task=LLMTask.NATURAL_QUERY,
                prompt=rag_query.question,
                context=context,
                temperature=0.3,
                max_tokens=1000,
                stream=False,
                structured_output=False
            )
            
            llm_response = await self.llm_service.generate_response(
                request=llm_request,
                user=user,
                db=self.db
            )
            
            # Step 5: Format sources
            sources = self._format_sources(relevant_chunks)
            
            # Step 6: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                relevant_chunks, 
                llm_response.confidence_score
            )
            
            return RAGResponse(
                answer=llm_response.content,
                sources=sources,
                confidence_score=confidence_score,
                model_used=llm_response.model_used,
                tokens_used=llm_response.tokens_used,
                latency_ms=llm_response.latency_ms,
                metadata={
                    "chunks_retrieved": len(relevant_chunks),
                    "similarity_scores": [chunk.similarity_score for chunk in relevant_chunks],
                    "reranking_used": rag_query.use_reranking
                }
            )
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return RAGResponse(
                answer=f"I encountered an error while processing your question: {str(e)}",
                sources=[],
                confidence_score=0.0,
                model_used="error",
                tokens_used=0,
                latency_ms=0.0,
                metadata={"error": str(e)}
            )
    
    def _construct_context(
        self, 
        chunks: List[RetrievalResult], 
        question: str
    ) -> Dict[str, Any]:
        """
        Construct context for LLM from retrieved chunks
        
        Args:
            chunks: Retrieved chunks
            question: User question
            
        Returns:
            Context dictionary
        """
        try:
            # Format chunks for context
            formatted_chunks = []
            for i, chunk in enumerate(chunks, 1):
                chunk_info = {
                    "chunk_id": i,
                    "content": chunk.content,
                    "similarity_score": chunk.similarity_score,
                    "metadata": chunk.metadata,
                    "log_file_id": chunk.log_file_id
                }
                formatted_chunks.append(chunk_info)
            
            # Create context
            context = {
                "question": question,
                "relevant_logs": formatted_chunks,
                "total_chunks": len(chunks),
                "average_similarity": sum(chunk.similarity_score for chunk in chunks) / len(chunks)
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error constructing context: {e}")
            return {"question": question, "relevant_logs": []}
    
    def _format_sources(self, chunks: List[RetrievalResult]) -> List[Dict[str, Any]]:
        """
        Format sources for response
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            List of formatted sources
        """
        try:
            sources = []
            for i, chunk in enumerate(chunks, 1):
                source = {
                    "chunk_id": i,
                    "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "similarity_score": chunk.similarity_score,
                    "metadata": chunk.metadata,
                    "log_file_id": chunk.log_file_id,
                    "vector_id": chunk.vector_id
                }
                sources.append(source)
            
            return sources
            
        except Exception as e:
            logger.error(f"Error formatting sources: {e}")
            return []
    
    def _calculate_confidence_score(
        self, 
        chunks: List[RetrievalResult], 
        llm_confidence: float
    ) -> float:
        """
        Calculate overall confidence score
        
        Args:
            chunks: Retrieved chunks
            llm_confidence: LLM confidence score
            
        Returns:
            Combined confidence score
        """
        try:
            if not chunks:
                return 0.0
            
            # Calculate retrieval confidence based on similarity scores
            avg_similarity = sum(chunk.similarity_score for chunk in chunks) / len(chunks)
            max_similarity = max(chunk.similarity_score for chunk in chunks)
            
            # Weight: 40% average similarity, 30% max similarity, 30% LLM confidence
            retrieval_confidence = (0.4 * avg_similarity) + (0.3 * max_similarity)
            combined_confidence = (0.7 * retrieval_confidence) + (0.3 * llm_confidence)
            
            return min(combined_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return llm_confidence
    
    async def get_pipeline_statistics(
        self,
        project_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get RAG pipeline statistics
        
        Args:
            project_id: Project ID
            user_id: User ID for isolation
            
        Returns:
            Statistics dictionary
        """
        try:
            # Get retrieval statistics
            retrieval_stats = await self.retrieval_service.get_retrieval_statistics(
                project_id=project_id,
                user_id=user_id
            )
            
            # Get LLM service health
            llm_health = await self.llm_service.health_check()
            
            return {
                "retrieval": retrieval_stats,
                "llm_health": llm_health,
                "pipeline_status": "healthy" if llm_health.get("overall_healthy", False) else "degraded"
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline statistics: {e}")
            return {"error": str(e)}
    
    async def process_log_file_for_rag(
        self,
        log_file_id: str,
        project_id: str,
        user_id: str,
        content: str,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a log file for RAG indexing
        
        Args:
            log_file_id: Log file ID
            project_id: Project ID
            user_id: User ID
            content: Log file content
            file_type: File type (json, standard, etc.)
            
        Returns:
            Processing result
        """
        try:
            from app.services.rag.chunking_service import ChunkingService, ChunkMetadata
            from app.services.rag.vector_store import VectorStore
            from app.services.rag.embedding_service import get_embedding_service
            
            # Initialize services
            chunking_service = ChunkingService()
            vector_store = VectorStore(self.db)
            embedding_service = await get_embedding_service()
            
            # Create chunk metadata
            chunk_metadata = ChunkMetadata(
                log_file_id=log_file_id,
                project_id=project_id,
                user_id=user_id,
                chunk_index=0,
                start_line=0,
                end_line=0,
                file_type=file_type
            )
            
            # Chunk the content
            chunks = chunking_service.chunk_log_file(content, chunk_metadata, file_type)
            
            if not chunks:
                return {"error": "No chunks created from log file"}
            
            # Generate embeddings for chunks
            chunks_with_embeddings = await embedding_service.generate_embeddings_for_chunks(chunks)
            
            # Store vectors
            vector_data = []
            for i, chunk in enumerate(chunks_with_embeddings):
                vector_data.append({
                    'content': chunk['content'],
                    'embedding': chunk['embedding'],
                    'log_file_id': log_file_id,
                    'metadata': {
                        'chunk_index': i,
                        'start_line': chunk['metadata'].start_line,
                        'end_line': chunk['metadata'].end_line,
                        'timestamp': chunk['metadata'].timestamp,
                        'log_level': chunk['metadata'].log_level,
                        'source': chunk['metadata'].source,
                        'file_type': chunk['metadata'].file_type,
                        'size': chunk['size'],
                        'entry_count': chunk['entry_count']
                    }
                })
            
            # Store in vector database
            vector_ids = await vector_store.store_vectors(
                vectors=vector_data,
                project_id=project_id,
                user_id=user_id
            )
            
            # Get chunk statistics
            chunk_stats = chunking_service.get_chunk_statistics(chunks)
            
            return {
                "success": True,
                "chunks_created": len(chunks),
                "vectors_stored": len(vector_ids),
                "chunk_statistics": chunk_stats,
                "vector_ids": vector_ids
            }
            
        except Exception as e:
            logger.error(f"Error processing log file for RAG: {e}")
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
            vector_store = VectorStore(self.db)
            deleted_count = await vector_store.delete_vectors_by_project(
                project_id=project_id,
                user_id=user_id
            )
            
            return {
                "success": True,
                "vectors_deleted": deleted_count
            }
            
        except Exception as e:
            logger.error(f"Error clearing project vectors: {e}")
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
        Reindex a specific log file
        
        Args:
            log_file_id: Log file ID
            project_id: Project ID
            user_id: User ID
            content: Log file content
            file_type: File type
            
        Returns:
            Reindex result
        """
        try:
            vector_store = VectorStore(self.db)
            
            # Delete existing vectors for this log file
            deleted_count = await vector_store.delete_vectors_by_log_file(
                log_file_id=log_file_id,
                project_id=project_id,
                user_id=user_id
            )
            
            # Process the file again
            result = await self.process_log_file_for_rag(
                log_file_id=log_file_id,
                project_id=project_id,
                user_id=user_id,
                content=content,
                file_type=file_type
            )
            
            result["vectors_deleted"] = deleted_count
            result["reindexed"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error reindexing log file: {e}")
            return {"error": str(e)}
