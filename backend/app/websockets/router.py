"""
WebSocket Router
Registers all WebSocket endpoints
"""

from fastapi import APIRouter, WebSocket
from app.websockets.chat_ws import chat_websocket
from app.websockets.live_logs_ws import live_logs_websocket
from app.websockets.notifications_ws import notifications_websocket

router = APIRouter()


@router.websocket("/chat/ws/{chat_id}")
async def websocket_chat_endpoint(websocket: WebSocket, chat_id: str):
    """
    Chat WebSocket endpoint

    Connect: ws://api/v1/chat/ws/{chat_id}?token=<jwt_token>
    """
    await chat_websocket(websocket, chat_id)


@router.websocket("/live-logs/ws/{project_id}")
async def websocket_live_logs_endpoint(websocket: WebSocket, project_id: str):
    """
    Live logs WebSocket endpoint

    Connect: ws://api/v1/live-logs/ws/{project_id}?token=<jwt_token>
    """
    await live_logs_websocket(websocket, project_id)


@router.websocket("/notifications/ws")
async def websocket_notifications_endpoint(websocket: WebSocket):
    """
    Notifications WebSocket endpoint

    Connect: ws://api/v1/notifications/ws?token=<jwt_token>
    """
    await notifications_websocket(websocket)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    from app.websockets.manager import connection_manager
    return connection_manager.get_stats()
