"""
Embedding Service for Loglytics AI
Generates embeddings using all-MiniLM-L6-v2 model
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union
from sentence_transformers import SentenceTransformer
import torch
from functools import lru_cache
import gc

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers"""
    
    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2"
        self.model = None
        self.embedding_dim = 384
        self.batch_size = 32
        self.max_sequence_length = 512
        self._model_loaded = False
        
    async def initialize(self):
        """Initialize the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Load model with optimized settings
            self.model = SentenceTransformer(
                self.model_name,
                device='cuda' if torch.cuda.is_available() else 'cpu',
                cache_folder='./models'
            )
            
            # Set model to evaluation mode
            self.model.eval()
            
            # Mark as loaded first
            self._model_loaded = True
            
            # Test the model
            test_embedding = await self.generate_embedding("test")
            if len(test_embedding) == self.embedding_dim:
                logger.info(f"Embedding model loaded successfully. Dimension: {self.embedding_dim}")
            else:
                logger.error(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {len(test_embedding)}")
                self._model_loaded = False
                
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self._model_loaded = False
            raise
    
    async def health_check(self) -> bool:
        """Check if embedding service is healthy"""
        return self._model_loaded and self.model is not None
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not self._model_loaded:
            raise ValueError("Embedding model not loaded")
        
        try:
            # Clean and prepare text
            clean_text = self._preprocess_text(text)
            
            # Generate embedding
            with torch.no_grad():
                embedding = self.model.encode(
                    clean_text,
                    convert_to_tensor=False,
                    normalize_embeddings=True
                )
            
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def generate_embeddings_batch(
        self, 
        texts: List[str], 
        batch_size: Optional[int] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not self._model_loaded:
            raise ValueError("Embedding model not loaded")
        
        if not texts:
            return []
        
        try:
            # Clean and prepare texts
            clean_texts = [self._preprocess_text(text) for text in texts]
            
            # Process in batches
            batch_size = batch_size or self.batch_size
            embeddings = []
            
            for i in range(0, len(clean_texts), batch_size):
                batch_texts = clean_texts[i:i + batch_size]
                
                with torch.no_grad():
                    batch_embeddings = self.model.encode(
                        batch_texts,
                        convert_to_tensor=False,
                        normalize_embeddings=True,
                        show_progress_bar=False
                    )
                
                embeddings.extend(batch_embeddings.tolist())
                
                # Clear cache periodically
                if i % (batch_size * 4) == 0:
                    torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    async def generate_embeddings_for_chunks(
        self, 
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks with metadata
        
        Args:
            chunks: List of chunk dictionaries with 'content' field
            
        Returns:
            List of chunks with added 'embedding' field
        """
        try:
            # Extract texts for embedding
            texts = [chunk['content'] for chunk in chunks]
            
            # Generate embeddings
            embeddings = await self.generate_embeddings_batch(texts)
            
            # Add embeddings to chunks
            result = []
            for chunk, embedding in zip(chunks, embeddings):
                chunk_with_embedding = chunk.copy()
                chunk_with_embedding['embedding'] = embedding
                result.append(chunk_with_embedding)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating embeddings for chunks: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before embedding
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Truncate if too long
        if len(text) > self.max_sequence_length:
            text = text[:self.max_sequence_length]
        
        return text.strip()
    
    async def compute_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (-1 to 1)
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    async def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]]
    ) -> List[Dict[str, Any]]:
        """
        Find most similar embeddings to query
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embeddings
            
        Returns:
            List of similarity scores with indices
        """
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                similarity = await self.compute_similarity(query_embedding, candidate)
                similarities.append({
                    'index': i,
                    'similarity': similarity
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error finding most similar embeddings: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return self.embedding_dim
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "max_sequence_length": self.max_sequence_length,
            "batch_size": self.batch_size,
            "loaded": self._model_loaded,
            "device": str(self.model.device) if self.model else None
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.model:
                del self.model
                self.model = None
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Force garbage collection
            gc.collect()
            
            self._model_loaded = False
            logger.info("Embedding service cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up embedding service: {e}")

# Global embedding service instance
_embedding_service = None

async def get_embedding_service() -> EmbeddingService:
    """Get or create global embedding service instance"""
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
        await _embedding_service.initialize()
    
    return _embedding_service

async def cleanup_embedding_service():
    """Cleanup global embedding service"""
    global _embedding_service
    
    if _embedding_service:
        await _embedding_service.cleanup()
        _embedding_service = None
