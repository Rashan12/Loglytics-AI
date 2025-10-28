from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.live_log_connection import LiveLog, LiveLogAlert, LiveLogConnection
from app.services.llm.llm_service import UnifiedLLMService
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class LiveLogAIAnalyzer:
    """AI analyzer for live logs"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_service = UnifiedLLMService(db)
    
    async def analyze_recent_logs(self, batch_size: int = 20):
        """Analyze recent unanalyzed logs"""
        
        # Get unanalyzed logs
        result = await self.db.execute(
            select(LiveLog)
            .where(LiveLog.analyzed == False)
            .order_by(LiveLog.timestamp.desc())
            .limit(batch_size)
        )
        logs = result.scalars().all()
        
        if not logs:
            return 0
        
        print(f"\n{'='*60}")
        print(f"🤖 AI ANALYZING {len(logs)} LOGS")
        print(f"{'='*60}\n")
        
        for log in logs:
            try:
                # Quick rule-based analysis
                quick_analysis = self.quick_analyze(log)
                
                log.is_error = quick_analysis['is_error']
                log.is_anomaly = quick_analysis['is_anomaly']
                
                # If significant, do deeper AI analysis
                if quick_analysis['is_error'] or quick_analysis['is_anomaly']:
                    ai_analysis = await self.deep_ai_analyze(log)
                    log.ai_summary = ai_analysis['summary']
                    
                    # Create alert
                    await self.create_alert(log, quick_analysis, ai_analysis)
                
                log.analyzed = True
                
                print(f"✅ Analyzed log {log.id}: Error={log.is_error}, Anomaly={log.is_anomaly}")
                
            except Exception as e:
                print(f"❌ Error analyzing log {log.id}: {e}")
                log.analyzed = True  # Mark as analyzed to avoid retry loop
        
        await self.db.commit()
        print(f"\n{'='*60}\n")
        
        return len(logs)
    
    def quick_analyze(self, log: LiveLog) -> dict:
        """Quick rule-based analysis"""
        
        message_lower = log.message.lower()
        
        # Error detection
        error_keywords = [
            'error', 'exception', 'fatal', 'failed', 'failure',
            'crash', 'panic', 'died', 'killed', 'terminated'
        ]
        is_error = (
            log.log_level in ['ERROR', 'FATAL', 'CRITICAL'] or
            any(kw in message_lower for kw in error_keywords)
        )
        
        # Anomaly detection
        anomaly_keywords = [
            'timeout', 'connection refused', 'out of memory', 'disk full',
            'permission denied', 'access denied', 'unauthorized',
            'slow', 'high latency', 'bottleneck'
        ]
        is_anomaly = (
            log.log_level in ['WARN', 'WARNING'] or
            any(kw in message_lower for kw in anomaly_keywords)
        )
        
        # Severity
        if 'fatal' in message_lower or 'critical' in message_lower:
            severity = 'critical'
        elif is_error:
            severity = 'high'
        elif is_anomaly:
            severity = 'medium'
        else:
            severity = 'low'
        
        return {
            'is_error': is_error,
            'is_anomaly': is_anomaly,
            'severity': severity
        }
    
    async def deep_ai_analyze(self, log: LiveLog) -> dict:
        """Deep AI analysis using LLM"""
        
        try:
            prompt = f"""Analyze this log entry and provide a brief summary:

Log Level: {log.log_level}
Source: {log.source}
Timestamp: {log.timestamp}
Message: {log.message}

Provide a concise analysis (max 2 sentences) of:
1. What this log indicates
2. Potential impact or action needed"""

            response = await self.llm_service.generate_response(
                session_id=f"log_analysis_{log.id}",
                message=prompt
            )
            
            summary = response.get('content', 'AI analysis completed')
            
            return {
                'summary': summary[:500],  # Limit length
                'analyzed_at': datetime.utcnow()
            }
            
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}")
            return {
                'summary': f"Detected {log.log_level} in {log.source}",
                'analyzed_at': datetime.utcnow()
            }
    
    async def create_alert(self, log: LiveLog, quick_analysis: dict, ai_analysis: dict):
        """Create an alert for significant log events"""
        
        # Get connection to find user_id
        result = await self.db.execute(
            select(LiveLogConnection).where(
                LiveLogConnection.id == log.connection_id
            )
        )
        connection = result.scalar_one()
        
        alert_type = "error_detected" if quick_analysis['is_error'] else "anomaly_detected"
        
        title = f"{alert_type.replace('_', ' ').title()} in {log.source or 'unknown'}"
        description = ai_analysis.get('summary', log.message[:200])
        
        alert = LiveLogAlert(
            log_id=log.id,
            user_id=connection.user_id,
            alert_type=alert_type,
            severity=quick_analysis['severity'],
            title=title,
            description=description
        )
        
        self.db.add(alert)
        
        print(f"🚨 Created {quick_analysis['severity']} severity alert: {title}")
