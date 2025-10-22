"""
WebSocket Middleware
Provides comprehensive middleware for WebSocket connections including compression, error handling, and performance optimization
"""

import asyncio
import json
import logging
import time
import zlib
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from app.websockets.auth import message_sanitizer, websocket_security, rate_limiter

logger = logging.getLogger(__name__)


class WebSocketCompression:
    """Handles message compression for WebSocket connections"""
    
    def __init__(self, compression_threshold: int = 1024):
        self.compression_threshold = compression_threshold
        self.compression_level = 6  # Balanced compression
        
    def compress_message(self, message: Dict[str, Any]) -> bytes:
        """
        Compress message if it exceeds threshold
        
        Args:
            message: Message dictionary
            
        Returns:
            Compressed message bytes
        """
        try:
            message_str = json.dumps(message)
            
            if len(message_str) > self.compression_threshold:
                compressed = zlib.compress(message_str.encode('utf-8'), self.compression_level)
                return compressed
            else:
                return message_str.encode('utf-8')
                
        except Exception as e:
            logger.error(f"Error compressing message: {e}")
            return json.dumps(message).encode('utf-8')
    
    def decompress_message(self, data: bytes) -> Dict[str, Any]:
        """
        Decompress message data
        
        Args:
            data: Compressed message bytes
            
        Returns:
            Decompressed message dictionary
        """
        try:
            # Try to decompress first
            try:
                decompressed = zlib.decompress(data)
                return json.loads(decompressed.decode('utf-8'))
            except zlib.error:
                # If decompression fails, try parsing as regular JSON
                return json.loads(data.decode('utf-8'))
                
        except Exception as e:
            logger.error(f"Error decompressing message: {e}")
            return {"type": "error", "message": "Failed to parse message"}


class MessageBatcher:
    """Batches messages for high-frequency streams to improve performance"""
    
    def __init__(self, batch_size: int = 10, batch_timeout: float = 0.1):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_messages = {}  # {connection_id: [messages]}
        self.batch_tasks = {}  # {connection_id: task}
        
    async def add_message(self, connection_id: str, message: Dict[str, Any], 
                         send_callback: Callable[[List[Dict[str, Any]]], None]):
        """
        Add message to batch
        
        Args:
            connection_id: WebSocket connection ID
            message: Message to batch
            send_callback: Function to call when batch is ready
        """
        try:
            if connection_id not in self.pending_messages:
                self.pending_messages[connection_id] = []
                
            self.pending_messages[connection_id].append(message)
            
            # Send immediately if batch is full
            if len(self.pending_messages[connection_id]) >= self.batch_size:
                await self._flush_batch(connection_id, send_callback)
            else:
                # Schedule timeout flush if not already scheduled
                if connection_id not in self.batch_tasks:
                    self.batch_tasks[connection_id] = asyncio.create_task(
                        self._timeout_flush(connection_id, send_callback)
                    )
                    
        except Exception as e:
            logger.error(f"Error adding message to batch: {e}")
    
    async def _timeout_flush(self, connection_id: str, send_callback: Callable):
        """Flush batch after timeout"""
        try:
            await asyncio.sleep(self.batch_timeout)
            await self._flush_batch(connection_id, send_callback)
        except Exception as e:
            logger.error(f"Error in timeout flush: {e}")
    
    async def _flush_batch(self, connection_id: str, send_callback: Callable):
        """Flush pending messages for connection"""
        try:
            if connection_id in self.pending_messages and self.pending_messages[connection_id]:
                messages = self.pending_messages[connection_id].copy()
                self.pending_messages[connection_id] = []
                
                # Cancel timeout task
                if connection_id in self.batch_tasks:
                    self.batch_tasks[connection_id].cancel()
                    del self.batch_tasks[connection_id]
                
                # Send batched messages
                await send_callback(messages)
                
        except Exception as e:
            logger.error(f"Error flushing batch: {e}")
    
    def cleanup_connection(self, connection_id: str):
        """Clean up connection from batcher"""
        if connection_id in self.pending_messages:
            del self.pending_messages[connection_id]
        if connection_id in self.batch_tasks:
            self.batch_tasks[connection_id].cancel()
            del self.batch_tasks[connection_id]


class BackpressureHandler:
    """Handles backpressure for high-frequency message streams"""
    
    def __init__(self, max_queue_size: int = 1000, drop_threshold: int = 800):
        self.max_queue_size = max_queue_size
        self.drop_threshold = drop_threshold
        self.message_queues = {}  # {connection_id: asyncio.Queue}
        self.processing_tasks = {}  # {connection_id: task}
        
    async def queue_message(self, connection_id: str, message: Dict[str, Any]):
        """
        Queue message for processing with backpressure handling
        
        Args:
            connection_id: WebSocket connection ID
            message: Message to queue
        """
        try:
            if connection_id not in self.message_queues:
                self.message_queues[connection_id] = asyncio.Queue(maxsize=self.max_queue_size)
                
                # Start processing task
                self.processing_tasks[connection_id] = asyncio.create_task(
                    self._process_messages(connection_id)
                )
            
            queue = self.message_queues[connection_id]
            
            # Check if queue is getting full
            if queue.qsize() > self.drop_threshold:
                # Drop oldest messages to prevent memory issues
                try:
                    while queue.qsize() > self.drop_threshold // 2:
                        queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                
                logger.warning(f"Dropping messages for connection {connection_id} due to backpressure")
            
            # Add message to queue
            await queue.put(message)
            
        except Exception as e:
            logger.error(f"Error queueing message: {e}")
    
    async def _process_messages(self, connection_id: str):
        """Process messages from queue"""
        try:
            queue = self.message_queues[connection_id]
            
            while True:
                try:
                    message = await queue.get()
                    # Message processing would be handled by the specific WebSocket handler
                    # This is just a placeholder for the queue processing logic
                    await asyncio.sleep(0.001)  # Small delay to prevent overwhelming
                    queue.task_done()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except Exception as e:
            logger.error(f"Error in message processing loop: {e}")
    
    def cleanup_connection(self, connection_id: str):
        """Clean up connection from backpressure handler"""
        if connection_id in self.processing_tasks:
            self.processing_tasks[connection_id].cancel()
            del self.processing_tasks[connection_id]
        if connection_id in self.message_queues:
            del self.message_queues[connection_id]


class WebSocketErrorHandler:
    """Comprehensive error handling for WebSocket connections"""
    
    def __init__(self):
        self.error_counts = {}  # {connection_id: count}
        self.max_errors = 10
        
    async def handle_error(self, connection_id: str, error: Exception, 
                          websocket: WebSocket, user_id: str = None):
        """
        Handle WebSocket errors with appropriate responses
        
        Args:
            connection_id: WebSocket connection ID
            error: Exception that occurred
            websocket: WebSocket instance
            user_id: User ID if available
        """
        try:
            # Track error count
            if connection_id not in self.error_counts:
                self.error_counts[connection_id] = 0
            self.error_counts[connection_id] += 1
            
            # Log error
            logger.error(f"WebSocket error for connection {connection_id}: {error}")
            
            # Check if too many errors
            if self.error_counts[connection_id] > self.max_errors:
                logger.warning(f"Too many errors for connection {connection_id}, closing")
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Too many errors")
                return
            
            # Send error message to client
            error_message = {
                "type": "error",
                "message": "An error occurred. Please try again.",
                "timestamp": datetime.utcnow().isoformat(),
                "error_id": str(uuid.uuid4())
            }
            
            try:
                await websocket.send_json(error_message)
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
                
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
    def cleanup_connection(self, connection_id: str):
        """Clean up connection from error handler"""
        if connection_id in self.error_counts:
            del self.error_counts[connection_id]


class WebSocketPerformanceMonitor:
    """Monitors WebSocket performance and connection health"""
    
    def __init__(self):
        self.connection_stats = {}  # {connection_id: stats}
        self.performance_thresholds = {
            "max_message_size": 1024 * 1024,  # 1MB
            "max_messages_per_second": 100,
            "max_connection_duration": 3600,  # 1 hour
        }
        
    def record_message(self, connection_id: str, message_size: int, message_type: str):
        """Record message statistics"""
        try:
            if connection_id not in self.connection_stats:
                self.connection_stats[connection_id] = {
                    "message_count": 0,
                    "total_bytes": 0,
                    "message_types": {},
                    "first_message": datetime.utcnow(),
                    "last_message": datetime.utcnow(),
                    "messages_per_second": 0
                }
            
            stats = self.connection_stats[connection_id]
            stats["message_count"] += 1
            stats["total_bytes"] += message_size
            stats["last_message"] = datetime.utcnow()
            
            if message_type not in stats["message_types"]:
                stats["message_types"][message_type] = 0
            stats["message_types"][message_type] += 1
            
            # Calculate messages per second
            duration = (stats["last_message"] - stats["first_message"]).total_seconds()
            if duration > 0:
                stats["messages_per_second"] = stats["message_count"] / duration
                
        except Exception as e:
            logger.error(f"Error recording message stats: {e}")
    
    def check_performance_issues(self, connection_id: str) -> List[str]:
        """Check for performance issues with connection"""
        issues = []
        
        try:
            if connection_id not in self.connection_stats:
                return issues
                
            stats = self.connection_stats[connection_id]
            
            # Check message size
            if stats["total_bytes"] > self.performance_thresholds["max_message_size"]:
                issues.append("Message size too large")
            
            # Check message rate
            if stats["messages_per_second"] > self.performance_thresholds["max_messages_per_second"]:
                issues.append("Message rate too high")
            
            # Check connection duration
            duration = (datetime.utcnow() - stats["first_message"]).total_seconds()
            if duration > self.performance_thresholds["max_connection_duration"]:
                issues.append("Connection duration too long")
                
        except Exception as e:
            logger.error(f"Error checking performance issues: {e}")
            
        return issues
    
    def get_connection_stats(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a connection"""
        return self.connection_stats.get(connection_id)
    
    def cleanup_connection(self, connection_id: str):
        """Clean up connection from performance monitor"""
        if connection_id in self.connection_stats:
            del self.connection_stats[connection_id]


class WebSocketMiddleware:
    """Main WebSocket middleware that combines all functionality"""
    
    def __init__(self):
        self.compression = WebSocketCompression()
        self.batcher = MessageBatcher()
        self.backpressure = BackpressureHandler()
        self.error_handler = WebSocketErrorHandler()
        self.performance_monitor = WebSocketPerformanceMonitor()
        
    async def process_incoming_message(self, websocket: WebSocket, connection_id: str, 
                                     user_id: str, raw_data: str) -> Optional[Dict[str, Any]]:
        """
        Process incoming WebSocket message through all middleware
        
        Args:
            websocket: WebSocket instance
            connection_id: Connection ID
            user_id: User ID
            raw_data: Raw message data
            
        Returns:
            Processed message dictionary or None if invalid
        """
        try:
            # Parse JSON
            try:
                message = json.loads(raw_data)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON from connection {connection_id}: {e}")
                await self.error_handler.handle_error(connection_id, e, websocket, user_id)
                return None
            
            # Validate message structure
            if not message_sanitizer.validate_message_structure(message):
                logger.warning(f"Invalid message structure from connection {connection_id}")
                await self.error_handler.handle_error(
                    connection_id, 
                    ValueError("Invalid message structure"), 
                    websocket, 
                    user_id
                )
                return None
            
            # Sanitize message
            message = message_sanitizer.sanitize_message(message)
            
            # Check rate limit
            allowed, error = await rate_limiter.check_rate_limit(connection_id, user_id)
            if not allowed:
                logger.warning(f"Rate limit exceeded for connection {connection_id}")
                await websocket.send_json({
                    "type": "error",
                    "message": error,
                    "timestamp": datetime.utcnow().isoformat()
                })
                return None
            
            # Record performance stats
            self.performance_monitor.record_message(
                connection_id, 
                len(raw_data), 
                message.get("type", "unknown")
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing incoming message: {e}")
            await self.error_handler.handle_error(connection_id, e, websocket, user_id)
            return None
    
    async def process_outgoing_message(self, connection_id: str, message: Dict[str, Any]) -> bytes:
        """
        Process outgoing WebSocket message through all middleware
        
        Args:
            connection_id: Connection ID
            message: Message dictionary
            
        Returns:
            Processed message bytes
        """
        try:
            # Sanitize outgoing message
            message = message_sanitizer.sanitize_message(message)
            
            # Compress if needed
            compressed_data = self.compression.compress_message(message)
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"Error processing outgoing message: {e}")
            return json.dumps({"type": "error", "message": "Failed to process message"}).encode('utf-8')
    
    def cleanup_connection(self, connection_id: str):
        """Clean up all middleware for a connection"""
        self.batcher.cleanup_connection(connection_id)
        self.backpressure.cleanup_connection(connection_id)
        self.error_handler.cleanup_connection(connection_id)
        self.performance_monitor.cleanup_connection(connection_id)


# Global middleware instance
websocket_middleware = WebSocketMiddleware()
