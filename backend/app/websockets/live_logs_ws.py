"""
Live Logs WebSocket Endpoint
Handles real-time log streaming
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.websockets.manager import connection_manager
from app.websockets.auth import authenticate_websocket, close_websocket_with_error, rate_limiter, verify_resource_access
from app.websockets.middleware import websocket_middleware
from app.database import get_db
from app.services.live_stream.live_stream_service import LiveStreamService
from app.services.live_stream.alert_engine import AlertEngine

logger = logging.getLogger(__name__)


async def live_logs_websocket(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for live log streaming

    Endpoint: ws://api/v1/live-logs/ws/{project_id}

    Message Types:
    - log_entry: New log received
    - connection_status: Live connection status changed
    - alert: New alert triggered
    - stats_update: Real-time metrics update
    - filter_update: Filter configuration changed
    """
    connection_id = str(uuid.uuid4())
    user_id = None
    current_filters = {}

    try:
        # Authenticate
        authenticated, user_id, error = await authenticate_websocket(websocket)
        if not authenticated:
            await close_websocket_with_error(websocket, error or "Authentication failed")
            return

        # Verify user has access to project
        has_access = await verify_resource_access(user_id, "project", project_id)
        if not has_access:
            logger.warning(f"User {user_id} denied access to project {project_id}")
            await close_websocket_with_error(websocket, "Access denied to this project")
            return

        # Connect to manager
        await connection_manager.connect(
            websocket,
            user_id,
            connection_id,
            metadata={
                "type": "live_logs",
                "project_id": project_id
            }
        )

        # Subscribe to project
        await connection_manager.subscribe_to_project(user_id, connection_id, project_id)

        logger.info(f"Live logs WebSocket connected: project={project_id}, user={user_id}")

        # Send welcome
        await connection_manager.send_personal_message(
            user_id,
            connection_id,
            {
                "type": "system",
                "message": "Connected to live logs",
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Initialize live stream service
        db = next(get_db())
        try:
            live_stream_service = LiveStreamService(db)
            alert_engine = AlertEngine(db)
            
            # Start live log streaming for this project
            await live_stream_service.start_project_streaming(project_id, user_id)
            
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

                    if message_type == "set_filters":
                        current_filters = message.get("filters", {})
                        await live_stream_service.update_user_filters(project_id, user_id, current_filters)
                        await connection_manager.send_personal_message(
                            user_id,
                            connection_id,
                            {
                                "type": "filters_updated",
                                "filters": current_filters,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )

                    elif message_type == "request_stats":
                        await send_stats_update(project_id, user_id, connection_id, live_stream_service)

                    elif message_type == "request_logs":
                        limit = message.get("limit", 100)
                        await send_recent_logs(project_id, user_id, connection_id, live_stream_service, limit)

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
        logger.info(f"Live logs WebSocket disconnected: project={project_id}, user={user_id}")
    except Exception as e:
        logger.error(f"Error in live logs WebSocket: {e}")
    finally:
        if user_id:
            await connection_manager.unsubscribe_from_project(user_id, project_id)
            await connection_manager.disconnect(user_id, connection_id)
            rate_limiter.cleanup_connection(connection_id)
            websocket_middleware.cleanup_connection(connection_id)


async def send_stats_update(project_id: str, user_id: str, connection_id: str, live_stream_service: LiveStreamService):
    """Send real-time stats update"""
    try:
        # Fetch actual stats from live stream service
        stats = await live_stream_service.get_project_stats(project_id)

        await connection_manager.send_personal_message(
            user_id,
            connection_id,
            {
                "type": "stats_update",
                "project_id": project_id,
                "stats": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error sending stats update: {e}")


async def send_recent_logs(project_id: str, user_id: str, connection_id: str, 
                          live_stream_service: LiveStreamService, limit: int = 100):
    """Send recent logs to client"""
    try:
        # Fetch recent logs from live stream service
        logs = await live_stream_service.get_recent_logs(project_id, limit=limit)

        await connection_manager.send_personal_message(
            user_id,
            connection_id,
            {
                "type": "recent_logs",
                "project_id": project_id,
                "logs": logs,
                "count": len(logs),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error sending recent logs: {e}")


async def broadcast_log_entry(project_id: str, log_entry: Dict[str, Any]):
    """Broadcast new log entry to all project subscribers"""
    try:
        await connection_manager.publish_to_redis(
            "websocket:logs",
            {
                "type": "log_entry",
                "project_id": project_id,
                "log": log_entry,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error broadcasting log entry: {e}")


async def broadcast_alert(project_id: str, alert: Dict[str, Any]):
    """Broadcast alert to all project subscribers"""
    try:
        await connection_manager.publish_to_redis(
            "websocket:logs",
            {
                "type": "alert",
                "project_id": project_id,
                "alert": alert,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error broadcasting alert: {e}")
