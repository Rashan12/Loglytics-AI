from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, AsyncGenerator
import asyncio
import json
from datetime import datetime, timedelta
import redis.asyncio as redis_async

from app.config import settings
from app.models.log_entry import LogEntry
from app.models.log_file import LogFile


class LiveStreamService:
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = None
        self.connected = False

    async def connect_redis(self):
        """Connect to Redis for real-time streaming"""
        try:
            self.redis_client = redis_async.from_url(settings.REDIS_URL, decode_responses=True)
            await self.redis_client.ping()
            self.connected = True
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            self.connected = False

    async def disconnect_redis(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.connected = False

    async def stream_logs(self, log_file_id: int, user_id: int) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream logs in real-time"""
        # Verify user has access to log file
        log_file = self.db.query(LogFile).filter(
            LogFile.id == log_file_id,
            LogFile.user_id == user_id
        ).first()
        
        if not log_file:
            yield {"error": "Log file not found or access denied"}
            return
        
        # Create Redis channel for this stream
        channel = f"log_stream:{log_file_id}:{user_id}"
        
        if not self.connected:
            await self.connect_redis()
        
        if not self.connected:
            yield {"error": "Redis connection failed"}
            return
        
        try:
            # Subscribe to Redis channel
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)
            
            # Send initial batch of recent logs
            recent_logs = self.db.query(LogEntry).filter(
                LogEntry.log_file_id == log_file_id
            ).order_by(LogEntry.created_at.desc()).limit(50).all()
            
            for log_entry in reversed(recent_logs):
                yield {
                    "type": "log_entry",
                    "data": {
                        "id": log_entry.id,
                        "timestamp": log_entry.timestamp.isoformat() if log_entry.timestamp else None,
                        "level": log_entry.level,
                        "message": log_entry.message,
                        "source": log_entry.source,
                        "line_number": log_entry.line_number
                    }
                }
            
            # Stream new logs
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        yield {
                            "type": "log_entry",
                            "data": data
                        }
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            yield {"error": f"Streaming error: {str(e)}"}
        finally:
            if 'pubsub' in locals():
                await pubsub.unsubscribe(channel)
                await pubsub.close()

    async def publish_log_entry(self, log_entry: LogEntry):
        """Publish a new log entry to Redis for real-time streaming"""
        if not self.connected:
            await self.connect_redis()
        
        if not self.connected:
            return
        
        # Get log file to find user
        log_file = self.db.query(LogFile).filter(LogFile.id == log_entry.log_file_id).first()
        if not log_file:
            return
        
        # Create channel for this log file and user
        channel = f"log_stream:{log_entry.log_file_id}:{log_file.user_id}"
        
        # Prepare log entry data
        log_data = {
            "id": log_entry.id,
            "timestamp": log_entry.timestamp.isoformat() if log_entry.timestamp else None,
            "level": log_entry.level,
            "message": log_entry.message,
            "source": log_entry.source,
            "line_number": log_entry.line_number,
            "created_at": log_entry.created_at.isoformat()
        }
        
        # Publish to Redis
        await self.redis_client.publish(channel, json.dumps(log_data))

    async def get_live_stats(self, log_file_id: int, user_id: int) -> Dict[str, Any]:
        """Get live statistics for a log file"""
        # Verify access
        log_file = self.db.query(LogFile).filter(
            LogFile.id == log_file_id,
            LogFile.user_id == user_id
        ).first()
        
        if not log_file:
            return {"error": "Log file not found or access denied"}
        
        # Get stats for last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        recent_entries = self.db.query(LogEntry).filter(
            LogEntry.log_file_id == log_file_id,
            LogEntry.created_at >= one_hour_ago
        ).all()
        
        # Calculate statistics
        total_entries = len(recent_entries)
        error_entries = len([e for e in recent_entries if e.level in ['ERROR', 'FATAL']])
        warning_entries = len([e for e in recent_entries if e.level in ['WARN', 'WARNING']])
        
        # Count by level
        level_counts = {}
        for entry in recent_entries:
            level = entry.level or 'UNKNOWN'
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Count by source
        source_counts = {}
        for entry in recent_entries:
            source = entry.source or 'UNKNOWN'
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            "log_file_id": log_file_id,
            "time_range": {
                "start": one_hour_ago.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "total_entries": total_entries,
            "error_entries": error_entries,
            "warning_entries": warning_entries,
            "error_rate": error_entries / total_entries if total_entries > 0 else 0,
            "level_distribution": level_counts,
            "source_distribution": source_counts,
            "last_updated": datetime.utcnow().isoformat()
        }

    async def start_log_monitoring(self, log_file_id: int, user_id: int):
        """Start monitoring a log file for new entries"""
        # This would typically be called when a user starts live monitoring
        # Implementation depends on how logs are being written to the file
        
        # For now, we'll just return a success message
        return {
            "status": "monitoring_started",
            "log_file_id": log_file_id,
            "user_id": user_id,
            "started_at": datetime.utcnow().isoformat()
        }

    async def stop_log_monitoring(self, log_file_id: int, user_id: int):
        """Stop monitoring a log file"""
        return {
            "status": "monitoring_stopped",
            "log_file_id": log_file_id,
            "user_id": user_id,
            "stopped_at": datetime.utcnow().isoformat()
        }
