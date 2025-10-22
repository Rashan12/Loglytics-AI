import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
import json

from app.models.log_entry import LogEntry
from app.models.live_log_connection import LiveLogConnection
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.chunking_service import ChunkingService
from app.services.live_stream.alert_engine import AlertEngine
from app.services.live_stream.websocket_broadcaster import WebSocketBroadcaster

logger = logging.getLogger(__name__)

class StreamProcessor:
    """
    Processes incoming logs in real-time
    Handles parsing, storage, embedding generation, and broadcasting
    """
    
    def __init__(self, db: AsyncSession, redis_client, project_id: str, user_id: str, connection_id: str):
        self.db = db
        self.redis = redis_client
        self.project_id = project_id
        self.user_id = user_id
        self.connection_id = connection_id
        
        # Initialize services
        self.embedding_service = EmbeddingService()
        self.chunking_service = ChunkingService()
        self.alert_engine = AlertEngine(db, redis_client)
        self.websocket_broadcaster = WebSocketBroadcaster(redis_client)
        
        # Processing configuration
        self.batch_size = 100  # Process logs in batches
        self.max_retries = 3
        
    async def process_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of logs"""
        if not logs:
            return {"processed": 0, "errors": 0}
        
        try:
            # Normalize logs to standard format
            normalized_logs = await self._normalize_logs(logs)
            
            # Store logs in database
            stored_count = await self._store_logs(normalized_logs)
            
            # Generate embeddings for RAG (async, non-blocking)
            asyncio.create_task(self._generate_embeddings(normalized_logs))
            
            # Check for alerts
            asyncio.create_task(self._check_alerts(normalized_logs))
            
            # Broadcast to frontend
            asyncio.create_task(self._broadcast_logs(normalized_logs))
            
            logger.info(f"Processed {stored_count} logs for connection {self.connection_id}")
            
            return {
                "processed": stored_count,
                "errors": len(logs) - stored_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process logs: {str(e)}")
            return {"processed": 0, "errors": len(logs)}
    
    async def _normalize_logs(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize logs to standard format"""
        normalized = []
        
        for log in logs:
            try:
                normalized_log = {
                    "timestamp": log.get("timestamp", datetime.utcnow()),
                    "log_level": self._normalize_log_level(log.get("log_level", "INFO")),
                    "message": str(log.get("message", "")),
                    "source": str(log.get("source", "unknown")),
                    "metadata": log.get("metadata", {}),
                    "raw_content": str(log.get("raw_content", "")),
                    "project_id": self.project_id,
                    "user_id": self.user_id,
                    "live_connection_id": self.connection_id
                }
                
                # Ensure metadata is JSON serializable
                if isinstance(normalized_log["metadata"], dict):
                    normalized_log["metadata"] = self._clean_metadata(normalized_log["metadata"])
                
                normalized.append(normalized_log)
                
            except Exception as e:
                logger.error(f"Failed to normalize log: {str(e)}")
                continue
        
        return normalized
    
    def _normalize_log_level(self, level: str) -> str:
        """Normalize log level to standard values"""
        level_upper = str(level).upper()
        
        if level_upper in ['CRITICAL', 'FATAL', 'EMERGENCY']:
            return 'CRITICAL'
        elif level_upper in ['ERROR', 'ERR']:
            return 'ERROR'
        elif level_upper in ['WARN', 'WARNING']:
            return 'WARN'
        elif level_upper in ['INFO', 'INFORMATION']:
            return 'INFO'
        elif level_upper in ['DEBUG', 'DBG']:
            return 'DEBUG'
        else:
            return 'INFO'
    
    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata to ensure JSON serialization"""
        cleaned = {}
        
        for key, value in metadata.items():
            try:
                # Test if value is JSON serializable
                json.dumps(value)
                cleaned[key] = value
            except (TypeError, ValueError):
                # Convert non-serializable values to strings
                cleaned[key] = str(value)
        
        return cleaned
    
    async def _store_logs(self, logs: List[Dict[str, Any]]) -> int:
        """Store logs in database"""
        if not logs:
            return 0
        
        try:
            # Prepare log entries for bulk insert
            log_entries = []
            for log in logs:
                log_entry = {
                    "id": self._generate_uuid(),
                    "log_file_id": None,  # Live logs don't have a file
                    "project_id": log["project_id"],
                    "user_id": log["user_id"],
                    "timestamp": log["timestamp"],
                    "log_level": log["log_level"],
                    "message": log["message"],
                    "source": log["source"],
                    "metadata": log["metadata"],
                    "raw_content": log["raw_content"],
                    "created_at": datetime.utcnow()
                }
                log_entries.append(log_entry)
            
            # Bulk insert
            await self.db.execute(
                insert(LogEntry),
                log_entries
            )
            await self.db.commit()
            
            logger.debug(f"Stored {len(log_entries)} logs in database")
            return len(log_entries)
            
        except Exception as e:
            logger.error(f"Failed to store logs: {str(e)}")
            await self.db.rollback()
            return 0
    
    async def _generate_embeddings(self, logs: List[Dict[str, Any]]):
        """Generate embeddings for RAG (async, non-blocking)"""
        try:
            # Filter logs that need embeddings (ERROR, WARN, CRITICAL)
            important_logs = [
                log for log in logs
                if log["log_level"] in ["ERROR", "WARN", "CRITICAL"]
            ]
            
            if not important_logs:
                return
            
            # Generate embeddings in batches
            for i in range(0, len(important_logs), self.batch_size):
                batch = important_logs[i:i + self.batch_size]
                await self._process_embedding_batch(batch)
                
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
    
    async def _process_embedding_batch(self, logs: List[Dict[str, Any]]):
        """Process a batch of logs for embedding generation"""
        try:
            # Create chunks for each log
            chunks = []
            for log in logs:
                log_chunks = self.chunking_service.create_chunks(
                    content=log["raw_content"],
                    metadata={
                        "log_id": log.get("id"),
                        "timestamp": log["timestamp"].isoformat(),
                        "log_level": log["log_level"],
                        "source": log["source"],
                        "project_id": self.project_id,
                        "user_id": self.user_id,
                        "live_connection_id": self.connection_id
                    }
                )
                chunks.extend(log_chunks)
            
            if not chunks:
                return
            
            # Generate embeddings
            embeddings = await self.embedding_service.generate_embeddings_batch(
                [chunk["content"] for chunk in chunks]
            )
            
            # Store embeddings (this would be implemented in vector_store.py)
            # await self.vector_store.store_embeddings_batch(chunks, embeddings)
            
            logger.debug(f"Generated embeddings for {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to process embedding batch: {str(e)}")
    
    async def _check_alerts(self, logs: List[Dict[str, Any]]):
        """Check logs against alert rules"""
        try:
            # Get alert rules for this project
            alert_rules = await self.alert_engine.get_alert_rules(self.project_id)
            
            if not alert_rules:
                return
            
            # Check each log against rules
            for log in logs:
                await self.alert_engine.check_log(log, alert_rules)
                
        except Exception as e:
            logger.error(f"Failed to check alerts: {str(e)}")
    
    async def _broadcast_logs(self, logs: List[Dict[str, Any]]):
        """Broadcast logs to frontend via WebSocket"""
        try:
            # Prepare logs for broadcasting
            broadcast_logs = []
            for log in logs:
                broadcast_log = {
                    "id": log.get("id"),
                    "timestamp": log["timestamp"].isoformat(),
                    "log_level": log["log_level"],
                    "message": log["message"],
                    "source": log["source"],
                    "metadata": log["metadata"],
                    "project_id": self.project_id,
                    "connection_id": self.connection_id
                }
                broadcast_logs.append(broadcast_log)
            
            # Broadcast to WebSocket clients
            await self.websocket_broadcaster.broadcast_logs(
                project_id=self.project_id,
                logs=broadcast_logs
            )
            
        except Exception as e:
            logger.error(f"Failed to broadcast logs: {str(e)}")
    
    def _generate_uuid(self) -> str:
        """Generate a UUID string"""
        import uuid
        return str(uuid.uuid4())
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        try:
            # Get recent log count
            query = select(LogEntry).filter(
                LogEntry.project_id == self.project_id,
                LogEntry.live_connection_id == self.connection_id,
                LogEntry.created_at >= datetime.utcnow() - timedelta(hours=1)
            )
            result = await self.db.execute(query)
            recent_logs = result.scalars().all()
            
            # Count by log level
            level_counts = {}
            for log in recent_logs:
                level = log.log_level
                level_counts[level] = level_counts.get(level, 0) + 1
            
            return {
                "connection_id": self.connection_id,
                "project_id": self.project_id,
                "total_logs_last_hour": len(recent_logs),
                "level_distribution": level_counts,
                "last_processed": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get processing stats: {str(e)}")
            return {
                "connection_id": self.connection_id,
                "project_id": self.project_id,
                "error": str(e)
            }
