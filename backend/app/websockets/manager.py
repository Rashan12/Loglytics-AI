"""
WebSocket Connection Manager
Manages active WebSocket connections with authentication and broadcasting
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any, List
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Centralized WebSocket connection manager
    Handles connection lifecycle, authentication, and message broadcasting
    """

    def __init__(self):
        # Active connections: {user_id: {connection_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = defaultdict(dict)

        # Project subscriptions: {project_id: {user_id: connection_id}}
        self.project_subscriptions: Dict[str, Dict[str, str]] = defaultdict(dict)

        # Chat subscriptions: {chat_id: {user_id: connection_id}}
        self.chat_subscriptions: Dict[str, Dict[str, str]] = defaultdict(dict)

        # Connection metadata: {connection_id: metadata}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

        # Heartbeat tracking: {connection_id: last_heartbeat}
        self.last_heartbeat: Dict[str, datetime] = {}

        # Redis client for pub/sub
        self.redis: Optional[redis.Redis] = None
        self.pubsub = None
        self._running = False

    async def initialize_redis(self):
        """Initialize Redis connection for pub/sub. If Redis is unavailable, continue without it."""
        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe(
                "websocket:broadcast",
                "websocket:chat",
                "websocket:logs",
                "websocket:notifications"
            )
            self._running = True

            # Start listening for Redis messages
            asyncio.create_task(self._listen_redis_messages())

            logger.info("WebSocket manager initialized with Redis pub/sub")
        except Exception as e:
            # Graceful degrade: log warning and proceed without Redis so app can start
            self.redis = None
            self.pubsub = None
            self._running = False
            logger.warning(f"Redis unavailable for WebSocket pub/sub, continuing without it: {e}")

    async def cleanup(self):
        """Cleanup Redis connections"""
        try:
            self._running = False
            if self.pubsub:
                await self.pubsub.unsubscribe()
                await self.pubsub.close()
            if self.redis:
                await self.redis.close()
            logger.info("WebSocket manager cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up WebSocket manager: {e}")

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        connection_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register a new WebSocket connection

        Args:
            websocket: FastAPI WebSocket instance
            user_id: Authenticated user ID
            connection_id: Unique connection identifier
            metadata: Optional connection metadata
        """
        try:
            await websocket.accept()

            # Store connection
            if user_id not in self.active_connections:
                self.active_connections[user_id] = {}

            self.active_connections[user_id][connection_id] = websocket

            # Store metadata
            self.connection_metadata[connection_id] = metadata or {}
            self.connection_metadata[connection_id].update({
                "user_id": user_id,
                "connected_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            })

            # Initialize heartbeat
            self.last_heartbeat[connection_id] = datetime.utcnow()

            logger.info(f"WebSocket connected: user={user_id}, connection={connection_id}")

            # Send connection confirmation
            await self.send_personal_message(
                user_id,
                connection_id,
                {
                    "type": "connection_established",
                    "connection_id": connection_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            raise

    async def disconnect(self, user_id: str, connection_id: str):
        """
        Unregister a WebSocket connection

        Args:
            user_id: User ID
            connection_id: Connection identifier
        """
        try:
            # Remove from active connections
            if user_id in self.active_connections:
                if connection_id in self.active_connections[user_id]:
                    del self.active_connections[user_id][connection_id]

                # Clean up empty user dict
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]

            # Remove from project subscriptions
            for project_id, subs in list(self.project_subscriptions.items()):
                if user_id in subs and subs[user_id] == connection_id:
                    del subs[user_id]
                if not subs:
                    del self.project_subscriptions[project_id]

            # Remove from chat subscriptions
            for chat_id, subs in list(self.chat_subscriptions.items()):
                if user_id in subs and subs[user_id] == connection_id:
                    del subs[user_id]
                if not subs:
                    del self.chat_subscriptions[chat_id]

            # Clean up metadata
            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]

            # Clean up heartbeat
            if connection_id in self.last_heartbeat:
                del self.last_heartbeat[connection_id]

            logger.info(f"WebSocket disconnected: user={user_id}, connection={connection_id}")

        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")

    async def subscribe_to_project(self, user_id: str, connection_id: str, project_id: str):
        """Subscribe connection to project updates"""
        try:
            self.project_subscriptions[project_id][user_id] = connection_id
            logger.debug(f"User {user_id} subscribed to project {project_id}")
        except Exception as e:
            logger.error(f"Error subscribing to project: {e}")

    async def unsubscribe_from_project(self, user_id: str, project_id: str):
        """Unsubscribe connection from project updates"""
        try:
            if project_id in self.project_subscriptions:
                if user_id in self.project_subscriptions[project_id]:
                    del self.project_subscriptions[project_id][user_id]
                if not self.project_subscriptions[project_id]:
                    del self.project_subscriptions[project_id]
            logger.debug(f"User {user_id} unsubscribed from project {project_id}")
        except Exception as e:
            logger.error(f"Error unsubscribing from project: {e}")

    async def subscribe_to_chat(self, user_id: str, connection_id: str, chat_id: str):
        """Subscribe connection to chat updates"""
        try:
            self.chat_subscriptions[chat_id][user_id] = connection_id
            logger.debug(f"User {user_id} subscribed to chat {chat_id}")
        except Exception as e:
            logger.error(f"Error subscribing to chat: {e}")

    async def unsubscribe_from_chat(self, user_id: str, chat_id: str):
        """Unsubscribe connection from chat updates"""
        try:
            if chat_id in self.chat_subscriptions:
                if user_id in self.chat_subscriptions[chat_id]:
                    del self.chat_subscriptions[chat_id][user_id]
                if not self.chat_subscriptions[chat_id]:
                    del self.chat_subscriptions[chat_id]
            logger.debug(f"User {user_id} unsubscribed from chat {chat_id}")
        except Exception as e:
            logger.error(f"Error unsubscribing from chat: {e}")

    async def send_personal_message(self, user_id: str, connection_id: str, message: Dict[str, Any]):
        """Send message to a specific connection"""
        try:
            if user_id in self.active_connections:
                if connection_id in self.active_connections[user_id]:
                    websocket = self.active_connections[user_id][connection_id]
                    await websocket.send_json(message)
                    self._update_activity(connection_id)
        except WebSocketDisconnect:
            await self.disconnect(user_id, connection_id)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections of a user"""
        try:
            if user_id in self.active_connections:
                disconnected = []
                for connection_id, websocket in self.active_connections[user_id].items():
                    try:
                        await websocket.send_json(message)
                        self._update_activity(connection_id)
                    except WebSocketDisconnect:
                        disconnected.append(connection_id)
                    except Exception as e:
                        logger.error(f"Error sending to user connection: {e}")

                # Clean up disconnected
                for conn_id in disconnected:
                    await self.disconnect(user_id, conn_id)
        except Exception as e:
            logger.error(f"Error sending to user: {e}")

    async def broadcast_to_project(self, project_id: str, message: Dict[str, Any]):
        """Broadcast message to all project subscribers"""
        try:
            if project_id in self.project_subscriptions:
                for user_id, connection_id in list(self.project_subscriptions[project_id].items()):
                    await self.send_personal_message(user_id, connection_id, message)
        except Exception as e:
            logger.error(f"Error broadcasting to project: {e}")

    async def broadcast_to_chat(self, chat_id: str, message: Dict[str, Any]):
        """Broadcast message to all chat subscribers"""
        try:
            if chat_id in self.chat_subscriptions:
                for user_id, connection_id in list(self.chat_subscriptions[chat_id].items()):
                    await self.send_personal_message(user_id, connection_id, message)
        except Exception as e:
            logger.error(f"Error broadcasting to chat: {e}")

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected users"""
        try:
            for user_id in list(self.active_connections.keys()):
                await self.send_to_user(user_id, message)
        except Exception as e:
            logger.error(f"Error broadcasting to all: {e}")

    async def publish_to_redis(self, channel: str, message: Dict[str, Any]):
        """Publish message to Redis for multi-worker broadcasting"""
        try:
            if self.redis:
                await self.redis.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Error publishing to Redis: {e}")

    async def _listen_redis_messages(self):
        """Listen for Redis pub/sub messages"""
        try:
            while self._running and self.pubsub:
                try:
                    message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                    if message and message['type'] == 'message':
                        channel = message['channel']
                        data = json.loads(message['data'])

                        # Route message based on channel
                        if channel == "websocket:broadcast":
                            await self.broadcast_to_all(data)
                        elif channel == "websocket:chat":
                            chat_id = data.get("chat_id")
                            if chat_id:
                                await self.broadcast_to_chat(chat_id, data)
                        elif channel == "websocket:logs":
                            project_id = data.get("project_id")
                            if project_id:
                                await self.broadcast_to_project(project_id, data)
                        elif channel == "websocket:notifications":
                            user_id = data.get("user_id")
                            if user_id:
                                await self.send_to_user(user_id, data)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error in Redis message listener: {e}")

    async def send_heartbeat(self, user_id: str, connection_id: str):
        """Send heartbeat/ping to connection"""
        try:
            await self.send_personal_message(
                user_id,
                connection_id,
                {
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")

    async def check_stale_connections(self, timeout_minutes: int = 5):
        """Check and disconnect stale connections"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)

            for connection_id, last_beat in list(self.last_heartbeat.items()):
                if last_beat < cutoff_time:
                    # Find and disconnect stale connection
                    metadata = self.connection_metadata.get(connection_id, {})
                    user_id = metadata.get("user_id")
                    if user_id:
                        await self.disconnect(user_id, connection_id)
                        logger.info(f"Disconnected stale connection: {connection_id}")

        except Exception as e:
            logger.error(f"Error checking stale connections: {e}")

    def _update_activity(self, connection_id: str):
        """Update last activity timestamp"""
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow().isoformat()
        if connection_id in self.last_heartbeat:
            self.last_heartbeat[connection_id] = datetime.utcnow()

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        try:
            total_connections = sum(len(conns) for conns in self.active_connections.values())

            return {
                "total_connections": total_connections,
                "total_users": len(self.active_connections),
                "project_subscriptions": len(self.project_subscriptions),
                "chat_subscriptions": len(self.chat_subscriptions),
                "redis_connected": self.redis is not None,
                "status": "running" if self._running else "stopped"
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}


# Global connection manager instance
connection_manager = ConnectionManager()
