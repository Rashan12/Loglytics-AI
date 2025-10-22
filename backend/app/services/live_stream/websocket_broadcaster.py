import asyncio
import json
import logging
from typing import Dict, List, Any, Set
from datetime import datetime
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class WebSocketBroadcaster:
    """
    WebSocket broadcaster for real-time log streaming to frontend
    Uses Redis pub/sub for multi-instance broadcasting
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.pubsub = None
        self.active_connections: Dict[str, Set[str]] = {}  # project_id -> set of connection_ids
        self._running = False
        
    async def start(self):
        """Start the broadcaster"""
        try:
            self.pubsub = self.redis.pubsub()
            self._running = True
            
            # Subscribe to log channels
            await self.pubsub.subscribe("logs:live")
            
            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            
            logger.info("WebSocket broadcaster started")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket broadcaster: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the broadcaster"""
        try:
            self._running = False
            
            if self.pubsub:
                await self.pubsub.unsubscribe("logs:live")
                await self.pubsub.close()
            
            logger.info("WebSocket broadcaster stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop WebSocket broadcaster: {str(e)}")
    
    async def register_connection(self, project_id: str, connection_id: str):
        """Register a WebSocket connection for a project"""
        try:
            if project_id not in self.active_connections:
                self.active_connections[project_id] = set()
            
            self.active_connections[project_id].add(connection_id)
            
            logger.debug(f"Registered connection {connection_id} for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to register connection: {str(e)}")
    
    async def unregister_connection(self, project_id: str, connection_id: str):
        """Unregister a WebSocket connection"""
        try:
            if project_id in self.active_connections:
                self.active_connections[project_id].discard(connection_id)
                
                # Clean up empty project sets
                if not self.active_connections[project_id]:
                    del self.active_connections[project_id]
            
            logger.debug(f"Unregistered connection {connection_id} for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to unregister connection: {str(e)}")
    
    async def broadcast_logs(self, project_id: str, logs: List[Dict[str, Any]]):
        """Broadcast logs to all connected clients for a project"""
        try:
            if not logs:
                return
            
            # Prepare broadcast message
            message = {
                "type": "logs",
                "project_id": project_id,
                "logs": logs,
                "timestamp": datetime.utcnow().isoformat(),
                "count": len(logs)
            }
            
            # Publish to Redis for multi-instance broadcasting
            await self.redis.publish(
                "logs:live",
                json.dumps(message)
            )
            
            logger.debug(f"Broadcasted {len(logs)} logs for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast logs: {str(e)}")
    
    async def broadcast_alert(self, project_id: str, alert: Dict[str, Any]):
        """Broadcast an alert to all connected clients for a project"""
        try:
            message = {
                "type": "alert",
                "project_id": project_id,
                "alert": alert,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish to Redis
            await self.redis.publish(
                "logs:live",
                json.dumps(message)
            )
            
            logger.debug(f"Broadcasted alert for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast alert: {str(e)}")
    
    async def broadcast_connection_status(self, project_id: str, connection_id: str, status: str):
        """Broadcast connection status update"""
        try:
            message = {
                "type": "connection_status",
                "project_id": project_id,
                "connection_id": connection_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish to Redis
            await self.redis.publish(
                "logs:live",
                json.dumps(message)
            )
            
            logger.debug(f"Broadcasted connection status for {connection_id}: {status}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast connection status: {str(e)}")
    
    async def _listen_for_messages(self):
        """Listen for Redis pub/sub messages"""
        try:
            while self._running:
                try:
                    message = await self.pubsub.get_message(timeout=1.0)
                    
                    if message and message['type'] == 'message':
                        await self._handle_redis_message(message)
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing Redis message: {str(e)}")
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error(f"Failed to listen for messages: {str(e)}")
    
    async def _handle_redis_message(self, message):
        """Handle incoming Redis pub/sub message"""
        try:
            data = json.loads(message['data'])
            message_type = data.get('type')
            project_id = data.get('project_id')
            
            if not project_id or project_id not in self.active_connections:
                return
            
            # Forward to WebSocket connections
            await self._forward_to_websockets(project_id, data)
            
        except Exception as e:
            logger.error(f"Failed to handle Redis message: {str(e)}")
    
    async def _forward_to_websockets(self, project_id: str, data: Dict[str, Any]):
        """Forward data to WebSocket connections"""
        try:
            # This would integrate with actual WebSocket connections
            # For now, just log the forwarding
            connection_count = len(self.active_connections.get(project_id, set()))
            
            if connection_count > 0:
                logger.debug(f"Forwarding message to {connection_count} connections for project {project_id}")
                # In a real implementation, this would send to actual WebSocket connections
            else:
                logger.debug(f"No active connections for project {project_id}")
                
        except Exception as e:
            logger.error(f"Failed to forward to WebSockets: {str(e)}")
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        try:
            total_connections = sum(len(connections) for connections in self.active_connections.values())
            project_count = len(self.active_connections)
            
            return {
                "total_connections": total_connections,
                "project_count": project_count,
                "projects": {
                    project_id: len(connections)
                    for project_id, connections in self.active_connections.items()
                },
                "status": "running" if self._running else "stopped"
            }
            
        except Exception as e:
            logger.error(f"Failed to get connection stats: {str(e)}")
            return {"error": str(e)}
    
    async def send_heartbeat(self, project_id: str):
        """Send heartbeat to keep connections alive"""
        try:
            message = {
                "type": "heartbeat",
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.redis.publish(
                "logs:live",
                json.dumps(message)
            )
            
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {str(e)}")
    
    async def broadcast_system_status(self, status: Dict[str, Any]):
        """Broadcast system status to all connections"""
        try:
            message = {
                "type": "system_status",
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.redis.publish(
                "logs:live",
                json.dumps(message)
            )
            
            logger.debug("Broadcasted system status")
            
        except Exception as e:
            logger.error(f"Failed to broadcast system status: {str(e)}")
    
    async def cleanup_stale_connections(self, max_age_minutes: int = 30):
        """Clean up stale connections (placeholder for connection health checking)"""
        try:
            # This would implement connection health checking
            # For now, just log that cleanup is not implemented
            logger.debug("Connection cleanup not yet implemented")
            
        except Exception as e:
            logger.error(f"Failed to cleanup stale connections: {str(e)}")
