from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
import json
import logging

from app.database import get_db
from app.services.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.live_log_connection import LiveLogConnection
from app.models.log_entry import LogEntry
from app.schemas.live_log_connection import (
    LiveLogConnectionCreate,
    LiveLogConnectionUpdate,
    LiveLogConnectionResponse,
    LiveLogConnectionTest
)
from app.schemas.alert import AlertResponse
from app.services.live_stream.stream_manager import StreamManager
from app.services.live_stream.websocket_broadcaster import WebSocketBroadcaster
from app.services.live_stream.alert_engine import AlertEngine
from app.core.security import encrypt_credentials, decrypt_credentials
from app.utils.helpers import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (would be injected via dependency injection in production)
stream_manager = None
websocket_broadcaster = None
alert_engine = None

async def get_stream_manager() -> StreamManager:
    """Get stream manager instance"""
    global stream_manager
    if not stream_manager:
        db = next(get_db())
        redis_client = await get_redis_client()
        stream_manager = StreamManager(db, redis_client)
    return stream_manager

async def get_websocket_broadcaster() -> WebSocketBroadcaster:
    """Get WebSocket broadcaster instance"""
    global websocket_broadcaster
    if not websocket_broadcaster:
        redis_client = await get_redis_client()
        websocket_broadcaster = WebSocketBroadcaster(redis_client)
        await websocket_broadcaster.start()
    return websocket_broadcaster

async def get_alert_engine() -> AlertEngine:
    """Get alert engine instance"""
    global alert_engine
    if not alert_engine:
        db = next(get_db())
        redis_client = await get_redis_client()
        alert_engine = AlertEngine(db, redis_client)
    return alert_engine

@router.post("/connections", response_model=LiveLogConnectionResponse)
async def create_connection(
    connection_data: LiveLogConnectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new live log connection"""
    try:
        # Encrypt credentials before storing
        encrypted_config = encrypt_credentials(connection_data.connection_config)
        
        # Create connection
        connection = LiveLogConnection(
            id=str(uuid.uuid4()),
            project_id=connection_data.project_id,
            user_id=current_user.id,
            connection_name=connection_data.connection_name,
            cloud_provider=connection_data.cloud_provider,
            connection_config=encrypted_config,
            status="inactive"
        )
        
        db.add(connection)
        await db.commit()
        await db.refresh(connection)
        
        logger.info(f"Created connection {connection.id} for user {current_user.id}")
        
        return LiveLogConnectionResponse.from_orm(connection)
        
    except Exception as e:
        logger.error(f"Failed to create connection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create connection")

@router.get("/connections/{project_id}", response_model=List[LiveLogConnectionResponse])
async def list_connections(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all connections for a project"""
    try:
        from sqlalchemy import select
        
        query = select(LiveLogConnection).filter(
            LiveLogConnection.project_id == project_id,
            LiveLogConnection.user_id == current_user.id
        )
        
        result = await db.execute(query)
        connections = result.scalars().all()
        
        # Decrypt credentials for response (but don't expose sensitive data)
        response_connections = []
        for conn in connections:
            conn_dict = conn.__dict__.copy()
            conn_dict['connection_config'] = {}  # Don't expose encrypted config
            response_connections.append(LiveLogConnectionResponse(**conn_dict))
        
        return response_connections
        
    except Exception as e:
        logger.error(f"Failed to list connections: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list connections")

@router.get("/connections/{connection_id}", response_model=LiveLogConnectionResponse)
async def get_connection(
    connection_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get connection details"""
    try:
        from sqlalchemy import select
        
        query = select(LiveLogConnection).filter(
            LiveLogConnection.id == connection_id,
            LiveLogConnection.user_id == current_user.id
        )
        
        result = await db.execute(query)
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Don't expose encrypted config
        conn_dict = connection.__dict__.copy()
        conn_dict['connection_config'] = {}
        
        return LiveLogConnectionResponse(**conn_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get connection")

@router.put("/connections/{connection_id}", response_model=LiveLogConnectionResponse)
async def update_connection(
    connection_id: str,
    connection_data: LiveLogConnectionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update connection"""
    try:
        from sqlalchemy import select, update
        
        # Get existing connection
        query = select(LiveLogConnection).filter(
            LiveLogConnection.id == connection_id,
            LiveLogConnection.user_id == current_user.id
        )
        
        result = await db.execute(query)
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Update fields
        update_data = connection_data.dict(exclude_unset=True)
        
        if 'connection_config' in update_data:
            update_data['connection_config'] = encrypt_credentials(update_data['connection_config'])
        
        # Update in database
        update_query = update(LiveLogConnection).where(
            LiveLogConnection.id == connection_id
        ).values(**update_data)
        
        await db.execute(update_query)
        await db.commit()
        
        # Get updated connection
        result = await db.execute(query)
        updated_connection = result.scalar_one()
        
        # Don't expose encrypted config
        conn_dict = updated_connection.__dict__.copy()
        conn_dict['connection_config'] = {}
        
        return LiveLogConnectionResponse(**conn_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update connection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update connection")

@router.delete("/connections/{connection_id}")
async def delete_connection(
    connection_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete connection"""
    try:
        from sqlalchemy import select, delete
        
        # Stop stream if running
        stream_mgr = await get_stream_manager()
        await stream_mgr.stop_stream(connection_id)
        
        # Delete from database
        query = delete(LiveLogConnection).where(
            LiveLogConnection.id == connection_id,
            LiveLogConnection.user_id == current_user.id
        )
        
        result = await db.execute(query)
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        logger.info(f"Deleted connection {connection_id}")
        
        return {"message": "Connection deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete connection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete connection")

@router.post("/connections/{connection_id}/start")
async def start_streaming(
    connection_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Start log streaming for a connection"""
    try:
        stream_mgr = await get_stream_manager()
        success = await stream_mgr.start_stream(connection_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to start streaming")
        
        # Broadcast status update
        broadcaster = await get_websocket_broadcaster()
        await broadcaster.broadcast_connection_status(
            project_id="",  # Would get from connection
            connection_id=connection_id,
            status="started"
        )
        
        return {"message": "Streaming started successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start streaming: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start streaming")

@router.post("/connections/{connection_id}/stop")
async def stop_streaming(
    connection_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Stop log streaming for a connection"""
    try:
        stream_mgr = await get_stream_manager()
        success = await stream_mgr.stop_stream(connection_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to stop streaming")
        
        # Broadcast status update
        broadcaster = await get_websocket_broadcaster()
        await broadcaster.broadcast_connection_status(
            project_id="",  # Would get from connection
            connection_id=connection_id,
            status="stopped"
        )
        
        return {"message": "Streaming stopped successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop streaming: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop streaming")

@router.post("/connections/{connection_id}/test")
async def test_connection(
    connection_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Test connection to cloud provider"""
    try:
        from sqlalchemy import select
        
        # Get connection
        query = select(LiveLogConnection).filter(
            LiveLogConnection.id == connection_id,
            LiveLogConnection.user_id == current_user.id
        )
        
        result = await db.execute(query)
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Decrypt credentials
        decrypted_config = decrypt_credentials(connection.connection_config)
        
        # Test connection based on provider
        if connection.cloud_provider == "aws":
            from app.services.live_stream.cloud_connectors.aws_cloudwatch import AWSCloudWatchConnector
            connector = AWSCloudWatchConnector(decrypted_config)
        elif connection.cloud_provider == "azure":
            from app.services.live_stream.cloud_connectors.azure_monitor import AzureMonitorConnector
            connector = AzureMonitorConnector(decrypted_config)
        elif connection.cloud_provider == "gcp":
            from app.services.live_stream.cloud_connectors.gcp_logging import GCPLoggingConnector
            connector = GCPLoggingConnector(decrypted_config)
        else:
            raise HTTPException(status_code=400, detail="Unsupported cloud provider")
        
        # Test connection
        success = await connector.test_connection()
        await connector.close()
        
        if success:
            return {"status": "success", "message": "Connection test successful"}
        else:
            return {"status": "error", "message": "Connection test failed"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test connection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test connection")

@router.get("/stream/{project_id}")
async def get_recent_logs(
    project_id: str,
    limit: int = Query(100, ge=1, le=1000),
    log_level: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent live logs for a project"""
    try:
        from sqlalchemy import select, and_
        
        # Build query
        query = select(LogEntry).filter(
            and_(
                LogEntry.project_id == project_id,
                LogEntry.user_id == current_user.id,
                LogEntry.live_connection_id.isnot(None)  # Only live logs
            )
        )
        
        if log_level:
            query = query.filter(LogEntry.log_level == log_level.upper())
        
        if since:
            query = query.filter(LogEntry.timestamp >= since)
        
        query = query.order_by(LogEntry.timestamp.desc()).limit(limit)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "log_level": log.log_level,
                "message": log.message,
                "source": log.source,
                "metadata": log.metadata,
                "connection_id": log.live_connection_id
            }
            for log in logs
        ]
        
    except Exception as e:
        logger.error(f"Failed to get recent logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recent logs")

@router.get("/alerts/{project_id}", response_model=List[AlertResponse])
async def get_alerts(
    project_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user)
):
    """Get active alerts for a project"""
    try:
        alert_eng = await get_alert_engine()
        alerts = await alert_eng.get_active_alerts(project_id, limit)
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")

@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Mark an alert as read"""
    try:
        alert_eng = await get_alert_engine()
        success = await alert_eng.mark_alert_read(alert_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": "Alert marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark alert as read: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to mark alert as read")

@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    token: str = Query(...)
):
    """WebSocket endpoint for real-time log streaming"""
    try:
        # Authenticate WebSocket connection
        # In production, this would validate the JWT token
        user_id = await authenticate_websocket_token(token)
        
        if not user_id:
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        # Accept connection
        await websocket.accept()
        
        # Register with broadcaster
        broadcaster = await get_websocket_broadcaster()
        connection_id = f"ws_{project_id}_{user_id}_{datetime.utcnow().timestamp()}"
        await broadcaster.register_connection(project_id, connection_id)
        
        try:
            # Send initial connection confirmation
            await websocket.send_text(json.dumps({
                "type": "connected",
                "project_id": project_id,
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            # Keep connection alive and forward messages
            while True:
                try:
                    # Send heartbeat every 30 seconds
                    await asyncio.sleep(30)
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"WebSocket error: {str(e)}")
                    break
                    
        finally:
            # Unregister connection
            await broadcaster.unregister_connection(project_id, connection_id)
            
    except Exception as e:
        logger.error(f"WebSocket connection failed: {str(e)}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass

async def authenticate_websocket_token(token: str) -> Optional[str]:
    """Authenticate WebSocket token (placeholder)"""
    # In production, this would validate JWT token
    # For now, just return a mock user ID
    return "mock_user_id"

# Import uuid at the top
import uuid
import asyncio

# Additional endpoints for enhanced live logs functionality

@router.post("/connections/test", response_model=dict)
async def test_connection_config(
    test_data: LiveLogConnectionTest,
    current_user: User = Depends(get_current_active_user)
):
    """Test connection configuration without saving"""
    try:
        # Test connection based on provider
        if test_data.cloud_provider == "aws":
            from app.services.live_stream.cloud_connectors.aws_cloudwatch import AWSCloudWatchConnector
            connector = AWSCloudWatchConnector(test_data.connection_config)
        elif test_data.cloud_provider == "azure":
            from app.services.live_stream.cloud_connectors.azure_monitor import AzureMonitorConnector
            connector = AzureMonitorConnector(test_data.connection_config)
        elif test_data.cloud_provider == "gcp":
            from app.services.live_stream.cloud_connectors.gcp_logging import GCPLoggingConnector
            connector = GCPLoggingConnector(test_data.connection_config)
        else:
            raise HTTPException(status_code=400, detail="Unsupported cloud provider")
        
        # Test connection
        success = await connector.test_connection()
        await connector.close()
        
        if success:
            return {
                "success": True,
                "message": "Connection test successful",
                "details": {
                    "provider": test_data.cloud_provider,
                    "tested_at": datetime.utcnow().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": "Connection test failed",
                "details": {
                    "provider": test_data.cloud_provider,
                    "tested_at": datetime.utcnow().isoformat()
                }
            }
        
    except Exception as e:
        logger.error(f"Failed to test connection config: {str(e)}")
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}",
            "details": {
                "provider": test_data.cloud_provider,
                "tested_at": datetime.utcnow().isoformat()
            }
        }

@router.get("/stats/{project_id}")
async def get_connection_stats(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get connection statistics for a project"""
    try:
        from sqlalchemy import select, func, and_
        
        # Get connection counts
        connections_query = select(LiveLogConnection).filter(
            and_(
                LiveLogConnection.project_id == project_id,
                LiveLogConnection.user_id == current_user.id
            )
        )
        connections_result = await db.execute(connections_query)
        connections = connections_result.scalars().all()
        
        active_connections = len([c for c in connections if c.status == "active"])
        total_connections = len(connections)
        
        # Get log statistics
        logs_query = select(
            func.count(LogEntry.id).label('total_logs'),
            func.count(LogEntry.id).filter(LogEntry.log_level.in_(['ERROR', 'CRITICAL'])).label('error_logs')
        ).filter(
            and_(
                LogEntry.project_id == project_id,
                LogEntry.user_id == current_user.id,
                LogEntry.live_connection_id.isnot(None),
                LogEntry.timestamp >= datetime.utcnow() - timedelta(days=1)
            )
        )
        
        logs_result = await db.execute(logs_query)
        logs_stats = logs_result.first()
        
        total_logs_today = logs_stats.total_logs or 0
        error_logs_today = logs_stats.error_logs or 0
        error_rate = (error_logs_today / total_logs_today * 100) if total_logs_today > 0 else 0
        
        # Mock real-time metrics (in production, these would come from Redis/streaming)
        logs_per_second = sum(conn.logs_per_second or 0 for conn in connections if conn.status == "active")
        
        # Get top errors
        top_errors_query = select(
            LogEntry.message,
            func.count(LogEntry.id).label('count')
        ).filter(
            and_(
                LogEntry.project_id == project_id,
                LogEntry.user_id == current_user.id,
                LogEntry.live_connection_id.isnot(None),
                LogEntry.log_level.in_(['ERROR', 'CRITICAL']),
                LogEntry.timestamp >= datetime.utcnow() - timedelta(hours=1)
            )
        ).group_by(LogEntry.message).order_by(func.count(LogEntry.id).desc()).limit(5)
        
        top_errors_result = await db.execute(top_errors_query)
        top_errors = [
            {"message": row.message, "count": row.count}
            for row in top_errors_result
        ]
        
        return {
            "total_logs_today": total_logs_today,
            "logs_per_second": logs_per_second,
            "error_rate": round(error_rate, 2),
            "top_errors": top_errors,
            "active_connections": active_connections,
            "total_connections": total_connections,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get connection stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get connection stats")

@router.get("/connections/{connection_id}/metrics")
async def get_connection_metrics(
    connection_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get metrics for a specific connection"""
    try:
        from sqlalchemy import select, func, and_
        
        # Get connection
        conn_query = select(LiveLogConnection).filter(
            and_(
                LiveLogConnection.id == connection_id,
                LiveLogConnection.user_id == current_user.id
            )
        )
        conn_result = await db.execute(conn_query)
        connection = conn_result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Get today's logs
        today = datetime.utcnow().date()
        logs_query = select(
            func.count(LogEntry.id).label('total_logs'),
            func.count(LogEntry.id).filter(LogEntry.log_level.in_(['ERROR', 'CRITICAL'])).label('error_logs')
        ).filter(
            and_(
                LogEntry.live_connection_id == connection_id,
                LogEntry.timestamp >= today
            )
        )
        
        logs_result = await db.execute(logs_query)
        logs_stats = logs_result.first()
        
        total_logs = logs_stats.total_logs or 0
        error_logs = logs_stats.error_logs or 0
        error_rate = (error_logs / total_logs * 100) if total_logs > 0 else 0
        
        # Mock real-time metrics
        logs_per_second = connection.logs_per_second or 0
        
        return {
            "logs_per_second": logs_per_second,
            "error_rate": round(error_rate, 2),
            "logs_today": total_logs,
            "errors_today": error_logs,
            "connection_status": connection.status,
            "last_sync_at": connection.last_sync_at.isoformat() if connection.last_sync_at else None,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connection metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get connection metrics")

@router.get("/export/{project_id}")
async def export_logs(
    project_id: str,
    format: str = Query(..., regex="^(json|csv|txt)$"),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    connection_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Export logs in various formats"""
    try:
        from sqlalchemy import select, and_
        
        # Build query
        query = select(LogEntry).filter(
            and_(
                LogEntry.project_id == project_id,
                LogEntry.user_id == current_user.id,
                LogEntry.live_connection_id.isnot(None)
            )
        )
        
        if connection_id:
            query = query.filter(LogEntry.live_connection_id == connection_id)
        
        if start_time:
            query = query.filter(LogEntry.timestamp >= start_time)
        
        if end_time:
            query = query.filter(LogEntry.timestamp <= end_time)
        
        query = query.order_by(LogEntry.timestamp.desc()).limit(10000)  # Limit for performance
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        # Format data based on requested format
        if format == "json":
            data = [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.log_level,
                    "message": log.message,
                    "source": log.source,
                    "metadata": log.metadata
                }
                for log in logs
            ]
            content = json.dumps(data, indent=2)
            media_type = "application/json"
            filename = f"logs_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["timestamp", "level", "message", "source", "metadata"])
            
            for log in logs:
                writer.writerow([
                    log.timestamp.isoformat(),
                    log.log_level,
                    log.message,
                    log.source or "",
                    json.dumps(log.metadata) if log.metadata else ""
                ])
            
            content = output.getvalue()
            media_type = "text/csv"
            filename = f"logs_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            
        else:  # txt
            content = "\n".join([
                f"[{log.timestamp.isoformat()}] {log.log_level}: {log.message}"
                for log in logs
            ])
            media_type = "text/plain"
            filename = f"logs_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
        
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Failed to export logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export logs")

@router.get("/health")
async def health_check():
    """Health check endpoint for live logs service"""
    try:
        # Check Redis connection
        redis_client = await get_redis_client()
        await redis_client.ping()
        redis_status = True
    except:
        redis_status = False
    
    # Check database connection
    try:
        db = next(get_db())
        await db.execute(select(1))
        db_status = True
    except:
        db_status = False
    
    overall_status = "healthy" if redis_status and db_status else "degraded"
    
    return {
        "status": overall_status,
        "message": "Live logs service is operational" if overall_status == "healthy" else "Some services are unavailable",
        "services": {
            "redis": redis_status,
            "database": db_status,
            "websocket": True  # Assume WebSocket is always available
        },
        "timestamp": datetime.utcnow().isoformat()
    }
