"""
Vector Store for Loglytics AI
pgvector operations for rag_vectors table with project-level isolation
"""

import logging
import uuid
import json
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, and_, or_, func, select
from sqlalchemy.dialects.postgresql import insert
import numpy as np

from app.models.rag_vector import RAGVector
from app.services.rag.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for managing embeddings in pgvector"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
    
    async def store_vectors(
        self, 
        vectors: List[Dict[str, Any]], 
        project_id: str, 
        user_id: str
    ) -> List[str]:
        """
        Store multiple vectors in the database
        
        Args:
            vectors: List of vector dictionaries with 'embedding' and 'content'
            project_id: Project ID for isolation
            user_id: User ID for isolation
            
        Returns:
            List of created vector IDs
        """
        try:
            vector_ids = []
            
            for vector_data in vectors:
                vector_id = await self.store_vector(
                    content=vector_data['content'],
                    embedding=vector_data['embedding'],
                    project_id=project_id,
                    user_id=user_id,
                    log_file_id=vector_data.get('log_file_id'),
                    metadata=vector_data.get('metadata', {})
                )
                vector_ids.append(vector_id)
            
            await self.db.commit()
            logger.info(f"Stored {len(vector_ids)} vectors for project {project_id}")
            return vector_ids
            
        except Exception as e:
            logger.error(f"Error storing vectors: {e}")
            await self.db.rollback()
            raise
    
    async def store_vector(
        self,
        content: str,
        embedding: List[float],
        project_id: str,
        user_id: str,
        log_file_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a single vector in the database
        
        Args:
            content: Text content
            embedding: Embedding vector
            project_id: Project ID for isolation
            user_id: User ID for isolation
            log_file_id: Associated log file ID
            metadata: Additional metadata
            
        Returns:
            Created vector ID
        """
        try:
            # Validate embedding dimension
            if len(embedding) != self.embedding_dim:
                raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {len(embedding)}")
            
            # Serialize embedding list to JSON string for storage
            embedding_json = json.dumps(embedding)
            
            # Create vector record
            vector = RAGVector(
                id=str(uuid.uuid4()),
                project_id=project_id,
                user_id=user_id,
                log_file_id=log_file_id,
                content=content,
                embedding=embedding_json,  # Store as JSON string
                vector_metadata=json.dumps(metadata) if metadata else None
            )
            
            self.db.add(vector)
            await self.db.flush()  # Flush to get the ID
            
            logger.debug(f"Stored vector {vector.id} for project {project_id}")
            return vector.id
            
        except Exception as e:
            logger.error(f"Error storing vector: {e}")
            raise
    
    async def search_similar(
        self,
        query_embedding: List[float],
        project_id: str,
        user_id: str,
        limit: int = 5,
        similarity_threshold: float = 0.05,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using cosine similarity
        
        Args:
            query_embedding: Query embedding vector
            project_id: Project ID for isolation
            user_id: User ID for isolation
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            filters: Additional metadata filters
            
        Returns:
            List of similar vectors with scores
        """
        try:
            # Validate embedding dimension
            if len(query_embedding) != self.embedding_dim:
                raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {len(query_embedding)}")
            
            # Build base query with isolation
            query = select(RAGVector).where(
                and_(
                    RAGVector.project_id == project_id,
                    RAGVector.user_id == user_id
                )
            )
            
            # Apply metadata filters
            if filters:
                query = self._apply_filters(query, filters)
            
            # Execute query and manually calculate similarity
            # Note: embedding is stored as JSON string in Text column
            query = query.limit(limit * 2)  # Get more results for manual filtering
            
            result = await self.db.execute(query)
            results = result.scalars().all()
            
            # Format results and calculate similarity
            similar_vectors = []
            for vector in results:
                # Parse embedding from JSON string
                embedding_list = []
                if isinstance(vector.embedding, str):
                    embedding_list = json.loads(vector.embedding)
                elif isinstance(vector.embedding, list):
                    embedding_list = vector.embedding
                else:
                    # Handle np.array or other types
                    embedding_list = list(vector.embedding) if hasattr(vector.embedding, '__iter__') else []
                
                # Calculate similarity score
                similarity_score = await self._calculate_cosine_similarity(
                    query_embedding, 
                    embedding_list
                )
                
                # Only include vectors above similarity threshold
                if similarity_score >= similarity_threshold:
                    # Parse metadata from JSON string
                    metadata = {}
                    metadata_field = vector.vector_metadata
                    if isinstance(metadata_field, str):
                        try:
                            metadata = json.loads(metadata_field)
                        except:
                            pass
                    elif isinstance(metadata_field, dict):
                        metadata = metadata_field
                    
                    similar_vectors.append({
                        'id': vector.id,
                        'content': vector.content,
                        'similarity': similarity_score,
                        'metadata': metadata,
                        'log_file_id': vector.log_file_id,
                        'created_at': vector.created_at
                    })
            
            # Sort by similarity and return top results
            similar_vectors.sort(key=lambda x: x['similarity'], reverse=True)
            similar_vectors = similar_vectors[:limit]
            
            logger.info(f"🔍 Search results for project {project_id}: {len(results)} total vectors retrieved, {len(similar_vectors)} above threshold {similarity_threshold}")
            if results and len(similar_vectors) == 0:
                # Log top scores for debugging
                top_scores = []
                for vector in results[:5]:
                    embedding_list = []
                    if isinstance(vector.embedding, str):
                        embedding_list = json.loads(vector.embedding)
                    elif isinstance(vector.embedding, list):
                        embedding_list = vector.embedding
                    score = await self._calculate_cosine_similarity(query_embedding, embedding_list)
                    top_scores.append(f"{score:.4f}")
                logger.warning(f"⚠️ No vectors above threshold. Top 5 scores: {', '.join(top_scores)}")
            
            return similar_vectors
            
        except Exception as e:
            logger.error(f"Error searching similar vectors: {e}")
            raise
    
    async def search_hybrid(
        self,
        query_embedding: List[float],
        project_id: str,
        user_id: str,
        text_query: Optional[str] = None,
        limit: int = 5,
        similarity_threshold: float = 0.05,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and text search
        
        Args:
            query_embedding: Query embedding vector
            project_id: Project ID for isolation
            user_id: User ID for isolation
            text_query: Optional text search query
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            filters: Additional metadata filters
            
        Returns:
            List of similar vectors with scores
        """
        try:
            # Start with vector similarity search
            vector_results = await self.search_similar(
                query_embedding=query_embedding,
                project_id=project_id,
                user_id=user_id,
                limit=limit * 2,  # Get more results for hybrid ranking
                similarity_threshold=similarity_threshold,
                filters=filters
            )
            
            # If no text query, return vector results
            if not text_query:
                return vector_results[:limit]
            
            # Apply text search boost
            text_boosted_results = []
            for result in vector_results:
                # Calculate text relevance score
                text_score = self._calculate_text_relevance(
                    result['content'], 
                    text_query
                )
                
                # Combine vector similarity and text relevance
                # Weight: 70% vector similarity, 30% text relevance
                combined_score = (0.7 * result['similarity']) + (0.3 * text_score)
                
                result['combined_score'] = combined_score
                result['text_score'] = text_score
                text_boosted_results.append(result)
            
            # Sort by combined score
            text_boosted_results.sort(key=lambda x: x['combined_score'], reverse=True)
            
            return text_boosted_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            raise
    
    async def get_vectors_by_log_file(
        self,
        log_file_id: str,
        project_id: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all vectors for a specific log file
        
        Args:
            log_file_id: Log file ID
            project_id: Project ID for isolation
            user_id: User ID for isolation
            
        Returns:
            List of vectors
        """
        try:
            query = select(RAGVector).where(
                and_(
                    RAGVector.log_file_id == log_file_id,
                    RAGVector.project_id == project_id,
                    RAGVector.user_id == user_id
                )
            )
            result = await self.db.execute(query)
            vectors = result.scalars().all()
            
            return [
                {
                    'id': vector.id,
                    'content': vector.content,
                    'metadata': json.loads(vector.vector_metadata) if isinstance(vector.vector_metadata, str) else (vector.vector_metadata or {}),
                    'created_at': vector.created_at
                }
                for vector in vectors
            ]
            
        except Exception as e:
            logger.error(f"Error getting vectors by log file: {e}")
            raise
    
    async def delete_vectors_by_log_file(
        self,
        log_file_id: str,
        project_id: str,
        user_id: str
    ) -> int:
        """
        Delete all vectors for a specific log file
        
        Args:
            log_file_id: Log file ID
            project_id: Project ID for isolation
            user_id: User ID for isolation
            
        Returns:
            Number of deleted vectors
        """
        try:
            query = select(RAGVector).where(
                and_(
                    RAGVector.log_file_id == log_file_id,
                    RAGVector.project_id == project_id,
                    RAGVector.user_id == user_id
                )
            )
            result = await self.db.execute(query)
            vectors_to_delete = result.scalars().all()
            deleted_count = len(vectors_to_delete)
            
            for vector in vectors_to_delete:
                await self.db.delete(vector)
            
            await self.db.commit()
            logger.info(f"Deleted {deleted_count} vectors for log file {log_file_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting vectors by log file: {e}")
            await self.db.rollback()
            raise
    
    async def delete_vectors_by_project(
        self,
        project_id: str,
        user_id: str
    ) -> int:
        """
        Delete all vectors for a project
        
        Args:
            project_id: Project ID
            user_id: User ID for isolation
            
        Returns:
            Number of deleted vectors
        """
        try:
            deleted_count = self.db.query(RAGVector).filter(
                and_(
                    RAGVector.project_id == project_id,
                    RAGVector.user_id == user_id
                )
            ).delete()
            
            self.db.commit()
            logger.info(f"Deleted {deleted_count} vectors for project {project_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting vectors by project: {e}")
            self.db.rollback()
            raise
    
    async def get_vector_statistics(
        self,
        project_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get statistics for vectors in a project
        
        Args:
            project_id: Project ID
            user_id: User ID for isolation
            
        Returns:
            Statistics dictionary
        """
        try:
            # Count total vectors
            total_vectors = self.db.query(RAGVector).filter(
                and_(
                    RAGVector.project_id == project_id,
                    RAGVector.user_id == user_id
                )
            ).count()
            
            # Count by log file
            log_file_counts = self.db.query(
                RAGVector.log_file_id,
                func.count(RAGVector.id).label('count')
            ).filter(
                and_(
                    RAGVector.project_id == project_id,
                    RAGVector.user_id == user_id
                )
            ).group_by(RAGVector.log_file_id).all()
            
            # Calculate total content size
            total_size = self.db.query(
                func.sum(func.length(RAGVector.content))
            ).filter(
                and_(
                    RAGVector.project_id == project_id,
                    RAGVector.user_id == user_id
                )
            ).scalar() or 0
            
            return {
                'total_vectors': total_vectors,
                'total_size_bytes': total_size,
                'log_files': len(log_file_counts),
                'vectors_by_log_file': [
                    {'log_file_id': lf_id, 'count': count}
                    for lf_id, count in log_file_counts
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting vector statistics: {e}")
            raise
    
    async def update_vector_metadata(
        self,
        vector_id: str,
        project_id: str,
        user_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update metadata for a vector
        
        Args:
            vector_id: Vector ID
            project_id: Project ID for isolation
            user_id: User ID for isolation
            metadata: New metadata
            
        Returns:
            True if updated successfully
        """
        try:
            vector = self.db.query(RAGVector).filter(
                and_(
                    RAGVector.id == vector_id,
                    RAGVector.project_id == project_id,
                    RAGVector.user_id == user_id
                )
            ).first()
            
            if not vector:
                return False
            
            vector.metadata = metadata
            self.db.commit()
            
            logger.debug(f"Updated metadata for vector {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating vector metadata: {e}")
            self.db.rollback()
            raise
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply metadata filters to query"""
        # Note: Since metadata is stored as JSON string, we'll apply filters after retrieval
        # For now, return the query as-is
        # TODO: Implement proper JSON filtering if needed
        return query
    
    async def _calculate_cosine_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def _calculate_text_relevance(self, content: str, query: str) -> float:
        """Calculate text relevance score"""
        try:
            content_lower = content.lower()
            query_lower = query.lower()
            
            # Simple word overlap scoring
            content_words = set(content_lower.split())
            query_words = set(query_lower.split())
            
            if not query_words:
                return 0.0
            
            overlap = len(content_words.intersection(query_words))
            return overlap / len(query_words)
            
        except Exception as e:
            logger.error(f"Error calculating text relevance: {e}")
            return 0.0
