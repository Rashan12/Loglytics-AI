"""
Notifications WebSocket Endpoint
Handles real-time user notifications
"""

import json
import logging
import uuid
from typing import Dict, Any, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.websockets.manager import connection_manager
from app.websockets.auth import authenticate_websocket, close_websocket_with_error, rate_limiter
from app.websockets.middleware import websocket_middleware
from app.database import get_db
try:
    from app.services.notification.notification_service import NotificationService  # type: ignore
except Exception:
    class NotificationService:
        """Fallback notification service when real service is unavailable.
        Provides no-op implementations to keep websockets running.
        """
        def __init__(self, db: Session):
            self.db = db

        async def get_unread_notifications(self, user_id: str, limit: int = 20):
            return []

        async def get_user_notifications(self, user_id: str, limit: int = 50):
            return []

        async def mark_notification_read(self, notification_id: str, user_id: str):
            return True

        async def mark_all_notifications_read(self, user_id: str):
            return True

logger = logging.getLogger(__name__)


async def notifications_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for user notifications

    Endpoint: ws://api/v1/notifications/ws

    Message Types:
    - notification: New notification
    - alert: Alert notification
    - system: System announcement
    - task_progress: Progress update for long tasks
    - mark_read: Mark notification as read
    """
    connection_id = str(uuid.uuid4())
    user_id = None

    try:
        # Authenticate
        authenticated, user_id, error = await authenticate_websocket(websocket)
        if not authenticated:
            await close_websocket_with_error(websocket, error or "Authentication failed")
            return

        # Connect to manager
        await connection_manager.connect(
            websocket,
            user_id,
            connection_id,
            metadata={"type": "notifications"}
        )

        logger.info(f"Notifications WebSocket connected: user={user_id}")

        # Send welcome
        await connection_manager.send_personal_message(
            user_id,
            connection_id,
            {
                "type": "system",
                "message": "Connected to notifications",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Initialize notification service
        db = next(get_db())
        try:
            notification_service = NotificationService(db)
            
            # Send pending notifications
            await send_pending_notifications(user_id, connection_id, notification_service)
            
            # Message loop
            while True:
                try:
                    data = await websocket.receive_text()
                    
                    # Process message through middleware
                    message = await websocket_middleware.process_incoming_message(
                        websocket, connection_id, user_id, data
                    )
                    
                    if not message:
                        continue

                    message_type = message.get("type")

                    if message_type == "mark_read":
                        notification_id = message.get("notification_id")
                        if notification_id:
                            await notification_service.mark_notification_read(notification_id, user_id)
                            await connection_manager.send_personal_message(
                                user_id,
                                connection_id,
                                {
                                    "type": "marked_read",
                                    "notification_id": notification_id,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            )

                    elif message_type == "get_notifications":
                        limit = message.get("limit", 50)
                        await send_notification_list(user_id, connection_id, notification_service, limit)

                    elif message_type == "mark_all_read":
                        await notification_service.mark_all_notifications_read(user_id)
                        await connection_manager.send_personal_message(
                            user_id,
                            connection_id,
                            {
                                "type": "all_marked_read",
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )

                    elif message_type == "ping":
                        await connection_manager.send_personal_message(
                            user_id,
                            connection_id,
                            {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                        )

                except WebSocketDisconnect:
                    break
                    
        finally:
            db.close()

    except WebSocketDisconnect:
        logger.info(f"Notifications WebSocket disconnected: user={user_id}")
    except Exception as e:
        logger.error(f"Error in notifications WebSocket: {e}")
    finally:
        if user_id:
            await connection_manager.disconnect(user_id, connection_id)
            rate_limiter.cleanup_connection(connection_id)
            websocket_middleware.cleanup_connection(connection_id)


async def send_pending_notifications(user_id: str, connection_id: str, notification_service: NotificationService):
    """Send pending notifications to user on connection"""
    try:
        notifications = await notification_service.get_unread_notifications(user_id, limit=20)
        
        for notification in notifications:
            await connection_manager.send_personal_message(
                user_id,
                connection_id,
                {
                    "type": "notification",
                    "notification_id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.type,
                    "created_at": notification.created_at.isoformat(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    except Exception as e:
        logger.error(f"Error sending pending notifications: {e}")


async def send_notification_list(user_id: str, connection_id: str, notification_service: NotificationService, limit: int):
    """Send list of notifications to user"""
    try:
        notifications = await notification_service.get_user_notifications(user_id, limit=limit)
        
        notification_list = []
        for notification in notifications:
            notification_list.append({
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "read": notification.read,
                "created_at": notification.created_at.isoformat()
            })
        
        await connection_manager.send_personal_message(
            user_id,
            connection_id,
            {
                "type": "notification_list",
                "notifications": notification_list,
                "count": len(notification_list),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error sending notification list: {e}")


async def send_notification(user_id: str, notification: Dict[str, Any]):
    """Send notification to user"""
    try:
        await connection_manager.publish_to_redis(
            "websocket:notifications",
            {
                "type": "notification",
                "user_id": user_id,
                "notification": notification,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error sending notification: {e}")


async def send_task_progress(user_id: str, task_id: str, progress: int, message: str):
    """Send task progress update"""
    try:
        await connection_manager.publish_to_redis(
            "websocket:notifications",
            {
                "type": "task_progress",
                "user_id": user_id,
                "task_id": task_id,
                "progress": progress,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error sending task progress: {e}")


async def broadcast_system_announcement(message: str, level: str = "info"):
    """Broadcast system announcement to all users"""
    try:
        await connection_manager.publish_to_redis(
            "websocket:broadcast",
            {
                "type": "system",
                "level": level,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error broadcasting system announcement: {e}")
