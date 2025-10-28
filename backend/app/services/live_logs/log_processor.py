from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.live_log_connection import LiveLog, LiveLogAlert, LiveLogConnection
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class LogProcessor:
    """Background processor for analyzing logs with AI"""
    
    @staticmethod
    async def process_logs_batch(db: AsyncSession, batch_size: int = 50):
        """Process unanalyzed logs in batches"""
        
        # Get unanalyzed logs
        result = await db.execute(
            select(LiveLog)
            .where(LiveLog.analyzed == False)
            .limit(batch_size)
        )
        logs = result.scalars().all()
        
        if not logs:
            return 0
        
        print(f"🤖 Processing {len(logs)} logs for AI analysis")
        
        for log in logs:
            try:
                # Analyze log
                analysis = await LogProcessor.analyze_log(log)
                
                # Update log
                log.analyzed = True
                log.is_error = analysis.get("is_error", False)
                log.is_anomaly = analysis.get("is_anomaly", False)
                log.ai_summary = analysis.get("summary")
                
                # Create alert if needed
                if log.is_error or log.is_anomaly:
                    await LogProcessor.create_alert(db, log, analysis)
                
            except Exception as e:
                print(f"❌ Error analyzing log {log.id}: {e}")
                log.analyzed = True  # Mark as analyzed to avoid retry loop
        
        await db.commit()
        return len(logs)
    
    @staticmethod
    async def analyze_log(log: LiveLog) -> dict:
        """Analyze a single log entry"""
        
        # Simple rule-based analysis for now
        # TODO: Integrate with LLM service
        
        message_lower = log.message.lower()
        
        is_error = False
        is_anomaly = False
        summary = ""
        severity = "low"
        
        # Error detection
        error_keywords = ["error", "exception", "fatal", "failed", "crash", "panic"]
        if log.log_level in ["ERROR", "FATAL"] or any(kw in message_lower for kw in error_keywords):
            is_error = True
            severity = "high"
            summary = f"Error detected in {log.source}: {log.message[:200]}"
        
        # Warning detection
        elif log.log_level == "WARN" or "warn" in message_lower:
            is_anomaly = True
            severity = "medium"
            summary = f"Warning in {log.source}: {log.message[:200]}"
        
        # Pattern detection (e.g., repeated errors, timeouts)
        if "timeout" in message_lower or "connection refused" in message_lower:
            is_anomaly = True
            severity = "high"
            summary = f"Connection issue detected: {log.message[:200]}"
        
        return {
            "is_error": is_error,
            "is_anomaly": is_anomaly,
            "summary": summary,
            "severity": severity
        }
    
    @staticmethod
    async def create_alert(db: AsyncSession, log: LiveLog, analysis: dict):
        """Create an alert for significant log events"""
        
        # Get connection to find user_id
        result = await db.execute(
            select(LiveLogConnection).where(LiveLogConnection.id == log.connection_id)
        )
        connection = result.scalar_one()
        
        alert_type = "error_detected" if analysis["is_error"] else "anomaly_detected"
        
        alert = LiveLogAlert(
            log_id=log.id,
            user_id=connection.user_id,
            alert_type=alert_type,
            severity=analysis.get("severity", "medium"),
            title=f"{alert_type.replace('_', ' ').title()} in {log.source}",
            description=analysis.get("summary", "")
        )
        
        db.add(alert)
