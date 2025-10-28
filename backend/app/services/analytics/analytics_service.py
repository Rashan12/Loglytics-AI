from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from app.models.analysis import Analysis
from app.models.log_entry import LogEntry
from app.models.log_file import LogFile
from app.schemas.analysis import AnalysisCreate
from app.services.llm.llm_service import UnifiedLLMService
from app.services.rag.rag_service import RAGService


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_service = UnifiedLLMService(db)
        self.rag_service = RAGService(db)

    async def create_analysis(self, analysis_data: AnalysisCreate, user_id: int) -> Analysis:
        """Create a new analysis"""
        analysis = Analysis(
            name=analysis_data.name,
            description=analysis_data.description,
            analysis_type=analysis_data.analysis_type,
            log_file_id=analysis_data.log_file_id,
            user_id=user_id,
            results=json.dumps(analysis_data.results),
            status="pending"
        )
        
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        
        # Process analysis asynchronously
        await self.process_analysis(analysis.id)
        
        return analysis

    async def process_analysis(self, analysis_id: int):
        """Process analysis based on type"""
        # Use async query
        result = await self.db.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            return
        
        try:
            analysis.status = "running"
            await self.db.commit()
            
            start_time = datetime.utcnow()
            
            if analysis.analysis_type == "pattern":
                results = await self.analyze_patterns(analysis.log_file_id, "error")
            elif analysis.analysis_type == "anomaly":
                results = await self.detect_anomalies(analysis.log_file_id, 0.8)
            elif analysis.analysis_type == "trend":
                results = await self.analyze_trends(analysis.log_file_id)
            else:
                results = await self.general_analysis(analysis.log_file_id)
            
            # Update analysis with results
            analysis.results = json.dumps(results)
            analysis.status = "completed"
            analysis.completed_at = datetime.utcnow()
            analysis.execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            await self.db.commit()
            
        except Exception as e:
            analysis.status = "failed"
            analysis.error_message = str(e)
            await self.db.commit()

    async def analyze_patterns(self, log_file_id: int, pattern_type: str = "error") -> Dict[str, Any]:
        """Analyze log patterns"""
        # Get log entries using async query
        result = await self.db.execute(
            select(LogEntry).where(LogEntry.log_file_id == log_file_id)
        )
        log_entries = result.scalars().all()
        
        if not log_entries:
            return {"error": "No log entries found"}
        
        # Count patterns by level
        level_counts = {}
        for entry in log_entries:
            level = entry.level or 'UNKNOWN'
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Find most common error messages
        error_messages = {}
        for entry in log_entries:
            if entry.level in ['ERROR', 'FATAL']:
                message = entry.message[:100]  # Truncate long messages
                error_messages[message] = error_messages.get(message, 0) + 1
        
        # Sort by frequency
        top_errors = sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Get time-based patterns
        hourly_counts = {}
        for entry in log_entries:
            if entry.timestamp:
                hour = entry.timestamp.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        results = {
            "pattern_type": pattern_type,
            "total_entries": len(log_entries),
            "level_distribution": level_counts,
            "top_errors": top_errors,
            "hourly_distribution": hourly_counts,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        return results

    async def detect_anomalies(self, log_file_id: int, threshold: float = 0.8) -> Dict[str, Any]:
        """Detect anomalies in logs"""
        result = await self.db.execute(
            select(LogEntry).where(LogEntry.log_file_id == log_file_id)
        )
        log_entries = result.scalars().all()
        
        if not log_entries:
            return {"error": "No log entries found"}
        
        # Calculate baseline metrics
        total_entries = len(log_entries)
        error_count = len([e for e in log_entries if e.level in ['ERROR', 'FATAL']])
        error_rate = error_count / total_entries if total_entries > 0 else 0
        
        # Detect spikes in error rate
        hourly_errors = {}
        for entry in log_entries:
            if entry.timestamp and entry.level in ['ERROR', 'FATAL']:
                hour = entry.timestamp.hour
                hourly_errors[hour] = hourly_errors.get(hour, 0) + 1
        
        # Find hours with unusually high error rates
        anomalies = []
        for hour, error_count in hourly_errors.items():
            hourly_total = len([e for e in log_entries if e.timestamp and e.timestamp.hour == hour])
            hourly_error_rate = error_count / hourly_total if hourly_total > 0 else 0
            
            if hourly_error_rate > error_rate * 2:  # 2x baseline
                anomalies.append({
                    "hour": hour,
                    "error_count": error_count,
                    "error_rate": hourly_error_rate,
                    "baseline_rate": error_rate
                })
        
        results = {
            "total_entries": total_entries,
            "error_count": error_count,
            "baseline_error_rate": error_rate,
            "anomalies": anomalies,
            "threshold": threshold,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        return results

    async def analyze_trends(self, log_file_id: int) -> Dict[str, Any]:
        """Analyze trends in logs"""
        result = await self.db.execute(
            select(LogEntry).where(LogEntry.log_file_id == log_file_id)
        )
        log_entries = result.scalars().all()
        
        if not log_entries:
            return {"error": "No log entries found"}
        
        # Group by day
        daily_counts = {}
        daily_errors = {}
        
        for entry in log_entries:
            if entry.timestamp:
                date = entry.timestamp.date()
                daily_counts[date] = daily_counts.get(date, 0) + 1
                
                if entry.level in ['ERROR', 'FATAL']:
                    daily_errors[date] = daily_errors.get(date, 0) + 1
        
        # Calculate trends
        dates = sorted(daily_counts.keys())
        if len(dates) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Calculate daily error rates
        daily_error_rates = {}
        for date in dates:
            total = daily_counts[date]
            errors = daily_errors.get(date, 0)
            daily_error_rates[date] = errors / total if total > 0 else 0
        
        # Simple trend calculation
        error_rates = list(daily_error_rates.values())
        trend = "stable"
        if len(error_rates) >= 2:
            if error_rates[-1] > error_rates[0] * 1.2:
                trend = "increasing"
            elif error_rates[-1] < error_rates[0] * 0.8:
                trend = "decreasing"
        
        results = {
            "analysis_period": {
                "start_date": dates[0].isoformat(),
                "end_date": dates[-1].isoformat(),
                "days": len(dates)
            },
            "daily_counts": {str(k): v for k, v in daily_counts.items()},
            "daily_errors": {str(k): v for k, v in daily_errors.items()},
            "daily_error_rates": {str(k): v for k, v in daily_error_rates.items()},
            "trend": trend,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        return results

    async def general_analysis(self, log_file_id: int) -> Dict[str, Any]:
        """Perform general log analysis"""
        result = await self.db.execute(
            select(LogEntry).where(LogEntry.log_file_id == log_file_id)
        )
        log_entries = result.scalars().all()
        
        if not log_entries:
            return {"error": "No log entries found"}
        
        # Basic statistics
        total_entries = len(log_entries)
        unique_levels = set(entry.level for entry in log_entries if entry.level)
        unique_sources = set(entry.source for entry in log_entries if entry.source)
        
        # Time range
        timestamps = [entry.timestamp for entry in log_entries if entry.timestamp]
        time_range = {
            "start": min(timestamps).isoformat() if timestamps else None,
            "end": max(timestamps).isoformat() if timestamps else None
        }
        
        # Level distribution
        level_distribution = {}
        for entry in log_entries:
            level = entry.level or 'UNKNOWN'
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        # Source distribution
        source_distribution = {}
        for entry in log_entries:
            source = entry.source or 'UNKNOWN'
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        results = {
            "total_entries": total_entries,
            "unique_levels": list(unique_levels),
            "unique_sources": list(unique_sources),
            "time_range": time_range,
            "level_distribution": level_distribution,
            "source_distribution": source_distribution,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        return results

    async def get_overview_stats(self, log_file_id: Optional[int], days: int, user_id: int) -> Dict[str, Any]:
        """Get overview statistics"""
        # Base query
        query = select(LogEntry)
        
        if log_file_id:
            query = query.where(LogEntry.log_file_id == log_file_id)
        else:
            # Get all log files for user using async
            result = await self.db.execute(
                select(LogFile).where(LogFile.user_id == user_id)
            )
            user_log_files = result.scalars().all()
            log_file_ids = [lf.id for lf in user_log_files]
            query = query.where(LogEntry.log_file_id.in_(log_file_ids))
        
        # Filter by date range
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.where(LogEntry.created_at >= start_date)
        
        # Get statistics using async queries
        total_result = await self.db.execute(select(func.count()).select_from(query))
        total_entries = total_result.scalar() or 0
        
        error_query = query.where(LogEntry.level.in_(['ERROR', 'FATAL']))
        error_result = await self.db.execute(select(func.count()).select_from(error_query))
        error_entries = error_result.scalar() or 0
        
        warning_query = query.where(LogEntry.level.in_(['WARN', 'WARNING']))
        warning_result = await self.db.execute(select(func.count()).select_from(warning_query))
        warning_entries = warning_result.scalar() or 0
        
        # Recent activity (last 24 hours)
        recent_start = datetime.utcnow() - timedelta(hours=24)
        recent_query = query.where(LogEntry.created_at >= recent_start)
        recent_result = await self.db.execute(select(func.count()).select_from(recent_query))
        recent_entries = recent_result.scalar() or 0
        
        # Top error sources
        top_sources_query = error_query.group_by(LogEntry.source).with_only_columns(
            LogEntry.source, func.count(LogEntry.id).label('count')
        ).order_by(desc('count')).limit(5)
        
        top_result = await self.db.execute(top_sources_query)
        top_sources = top_result.all()
        
        return {
            "total_entries": total_entries,
            "error_entries": error_entries,
            "warning_entries": warning_entries,
            "recent_entries": recent_entries,
            "error_rate": error_entries / total_entries if total_entries > 0 else 0,
            "top_error_sources": [{"source": s[0], "count": s[1]} for s in top_sources],
            "analysis_period_days": days,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
