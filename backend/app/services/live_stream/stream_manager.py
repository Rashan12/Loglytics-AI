from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

from app.models.live_log_connection import LiveLogConnection
from app.models.user import User
from app.services.live_stream.cloud_connectors.aws_cloudwatch import AWSCloudWatchConnector
from app.services.live_stream.cloud_connectors.azure_monitor import AzureMonitorConnector
from app.services.live_stream.cloud_connectors.gcp_logging import GCPLoggingConnector
from app.services.live_stream.stream_processor import StreamProcessor
from app.services.live_stream.alert_engine import AlertEngine
from app.services.live_stream.websocket_broadcaster import WebSocketBroadcaster

logger = logging.getLogger(__name__)

class StreamStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPING = "stopping"

@dataclass
class StreamInfo:
    connection_id: str
    project_id: str
    user_id: str
    status: StreamStatus
    connector: Optional[object] = None
    processor: Optional[StreamProcessor] = None
    task: Optional[asyncio.Task] = None
    last_sync: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None

class StreamManager:
    """
    Manages active log streams from various cloud providers
    Handles connection lifecycle, error recovery, and resource management
    """
    
    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client
        self.active_streams: Dict[str, StreamInfo] = {}
        self.connector_classes = {
            "aws": AWSCloudWatchConnector,
            "azure": AzureMonitorConnector,
            "gcp": GCPLoggingConnector
        }
        self.alert_engine = AlertEngine(db_session, redis_client)
        self.websocket_broadcaster = WebSocketBroadcaster(redis_client)
        self._shutdown_event = asyncio.Event()
        
    async def start_stream(self, connection_id: str) -> bool:
        """Start a log stream for the given connection"""
        try:
            # Get connection details from database
            connection = await self._get_connection(connection_id)
            if not connection:
                logger.error(f"Connection {connection_id} not found")
                return False
            
            # Check if stream is already running
            if connection_id in self.active_streams:
                logger.warning(f"Stream {connection_id} is already running")
                return True
            
            # Create connector based on cloud provider
            connector_class = self.connector_classes.get(connection.cloud_provider)
            if not connector_class:
                logger.error(f"Unsupported cloud provider: {connection.cloud_provider}")
                return False
            
            connector = connector_class(connection.connection_config)
            
            # Test connection before starting
            if not await connector.test_connection():
                logger.error(f"Connection test failed for {connection_id}")
                return False
            
            # Create stream processor
            processor = StreamProcessor(
                db=self.db,
                redis=self.redis,
                project_id=connection.project_id,
                user_id=connection.user_id,
                connection_id=connection_id
            )
            
            # Create stream info
            stream_info = StreamInfo(
                connection_id=connection_id,
                project_id=connection.project_id,
                user_id=connection.user_id,
                status=StreamStatus.STARTING,
                connector=connector,
                processor=processor
            )
            
            # Start the stream task
            task = asyncio.create_task(self._run_stream(stream_info))
            stream_info.task = task
            
            # Register stream
            self.active_streams[connection_id] = stream_info
            
            # Update connection status
            await self._update_connection_status(connection_id, "active")
            
            logger.info(f"Started stream for connection {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start stream {connection_id}: {str(e)}")
            return False
    
    async def stop_stream(self, connection_id: str) -> bool:
        """Stop a log stream"""
        try:
            if connection_id not in self.active_streams:
                logger.warning(f"Stream {connection_id} is not running")
                return True
            
            stream_info = self.active_streams[connection_id]
            stream_info.status = StreamStatus.STOPPING
            
            # Cancel the task
            if stream_info.task and not stream_info.task.done():
                stream_info.task.cancel()
                try:
                    await stream_info.task
                except asyncio.CancelledError:
                    pass
            
            # Clean up
            if stream_info.connector:
                await stream_info.connector.close()
            
            # Remove from active streams
            del self.active_streams[connection_id]
            
            # Update connection status
            await self._update_connection_status(connection_id, "paused")
            
            logger.info(f"Stopped stream for connection {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop stream {connection_id}: {str(e)}")
            return False
    
    async def pause_stream(self, connection_id: str) -> bool:
        """Pause a log stream (temporarily stop polling)"""
        try:
            if connection_id not in self.active_streams:
                logger.warning(f"Stream {connection_id} is not running")
                return False
            
            stream_info = self.active_streams[connection_id]
            stream_info.status = StreamStatus.PAUSED
            
            # Update connection status
            await self._update_connection_status(connection_id, "paused")
            
            logger.info(f"Paused stream for connection {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause stream {connection_id}: {str(e)}")
            return False
    
    async def resume_stream(self, connection_id: str) -> bool:
        """Resume a paused log stream"""
        try:
            if connection_id not in self.active_streams:
                logger.warning(f"Stream {connection_id} is not running")
                return False
            
            stream_info = self.active_streams[connection_id]
            stream_info.status = StreamStatus.RUNNING
            
            # Update connection status
            await self._update_connection_status(connection_id, "active")
            
            logger.info(f"Resumed stream for connection {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume stream {connection_id}: {str(e)}")
            return False
    
    async def get_stream_status(self, connection_id: str) -> Optional[Dict]:
        """Get status of a specific stream"""
        if connection_id not in self.active_streams:
            return None
        
        stream_info = self.active_streams[connection_id]
        return {
            "connection_id": connection_id,
            "project_id": stream_info.project_id,
            "status": stream_info.status.value,
            "last_sync": stream_info.last_sync.isoformat() if stream_info.last_sync else None,
            "error_count": stream_info.error_count,
            "last_error": stream_info.last_error
        }
    
    async def get_all_streams_status(self) -> List[Dict]:
        """Get status of all active streams"""
        return [
            await self.get_stream_status(connection_id)
            for connection_id in self.active_streams.keys()
        ]
    
    async def _run_stream(self, stream_info: StreamInfo):
        """Main stream processing loop"""
        try:
            stream_info.status = StreamStatus.RUNNING
            logger.info(f"Starting stream processing for {stream_info.connection_id}")
            
            while not self._shutdown_event.is_set():
                try:
                    # Check if stream is paused
                    if stream_info.status == StreamStatus.PAUSED:
                        await asyncio.sleep(5)  # Check every 5 seconds
                        continue
                    
                    # Fetch new logs
                    logs = await stream_info.connector.fetch_logs(
                        since=stream_info.last_sync
                    )
                    
                    if logs:
                        # Process logs
                        await stream_info.processor.process_logs(logs)
                        
                        # Update last sync time
                        stream_info.last_sync = datetime.utcnow()
                        
                        # Reset error count on success
                        stream_info.error_count = 0
                        stream_info.last_error = None
                        
                        logger.debug(f"Processed {len(logs)} logs for {stream_info.connection_id}")
                    
                    # Wait before next poll
                    await asyncio.sleep(30)  # Poll every 30 seconds
                    
                except Exception as e:
                    stream_info.error_count += 1
                    stream_info.last_error = str(e)
                    stream_info.status = StreamStatus.ERROR
                    
                    logger.error(f"Error in stream {stream_info.connection_id}: {str(e)}")
                    
                    # Exponential backoff on errors
                    wait_time = min(300, 30 * (2 ** min(stream_info.error_count, 5)))
                    await asyncio.sleep(wait_time)
                    
                    # If too many errors, stop the stream
                    if stream_info.error_count > 10:
                        logger.error(f"Too many errors for stream {stream_info.connection_id}, stopping")
                        break
                    
        except asyncio.CancelledError:
            logger.info(f"Stream {stream_info.connection_id} was cancelled")
        except Exception as e:
            logger.error(f"Fatal error in stream {stream_info.connection_id}: {str(e)}")
            stream_info.status = StreamStatus.ERROR
        finally:
            # Clean up
            if stream_info.connector:
                await stream_info.connector.close()
    
    async def _get_connection(self, connection_id: str) -> Optional[LiveLogConnection]:
        """Get connection details from database"""
        from sqlalchemy import select
        
        query = select(LiveLogConnection).filter(
            LiveLogConnection.id == connection_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _update_connection_status(self, connection_id: str, status: str):
        """Update connection status in database"""
        from sqlalchemy import update
        
        query = update(LiveLogConnection).where(
            LiveLogConnection.id == connection_id
        ).values(
            status=status,
            last_sync_at=datetime.utcnow()
        )
        await self.db.execute(query)
        await self.db.commit()
    
    async def shutdown(self):
        """Gracefully shutdown all streams"""
        logger.info("Shutting down stream manager...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop all active streams
        for connection_id in list(self.active_streams.keys()):
            await self.stop_stream(connection_id)
        
        logger.info("Stream manager shutdown complete")
    
    async def health_check(self) -> Dict:
        """Get health status of the stream manager"""
        total_streams = len(self.active_streams)
        running_streams = sum(
            1 for stream in self.active_streams.values()
            if stream.status == StreamStatus.RUNNING
        )
        error_streams = sum(
            1 for stream in self.active_streams.values()
            if stream.status == StreamStatus.ERROR
        )
        
        return {
            "total_streams": total_streams,
            "running_streams": running_streams,
            "error_streams": error_streams,
            "uptime": "N/A",  # Could track start time
            "status": "healthy" if error_streams == 0 else "degraded"
        }
