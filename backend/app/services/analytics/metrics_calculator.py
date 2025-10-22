from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from app.models import LogEntry
import pandas as pd

class MetricsCalculator:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_overview(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate overview metrics:
        - Total log count
        - Date range
        - Log level distribution
        - Timeline data
        - Top errors/warnings
        - Unique sources
        """
        
        # Build base query
        query = select(LogEntry).filter(LogEntry.project_id == project_id)
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        # Total count
        total_count = await self._get_total_count(project_id, log_file_id)
        
        # Date range
        date_range = await self._get_date_range(project_id, log_file_id)
        
        # Log level distribution
        log_level_dist = await self._get_log_level_distribution(project_id, log_file_id)
        
        # Timeline data
        timeline_data = await self._get_timeline_data(project_id, log_file_id)
        
        # Top errors
        top_errors = await self._get_top_messages(project_id, log_file_id, "ERROR", limit=10)
        
        # Top warnings
        top_warnings = await self._get_top_messages(project_id, log_file_id, "WARN", limit=10)
        
        # Unique sources count
        unique_sources = await self._get_unique_sources_count(project_id, log_file_id)
        
        return {
            "total_count": total_count,
            "date_range": date_range,
            "log_level_distribution": log_level_dist,
            "timeline": timeline_data,
            "top_errors": top_errors,
            "top_warnings": top_warnings,
            "unique_sources": unique_sources,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _get_total_count(self, project_id: str, log_file_id: Optional[str]) -> int:
        """Get total log entries count"""
        query = select(func.count(LogEntry.id)).filter(
            LogEntry.project_id == project_id
        )
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _get_date_range(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> Dict[str, str]:
        """Get first and last log timestamp"""
        query = select(
            func.min(LogEntry.timestamp).label('first'),
            func.max(LogEntry.timestamp).label('last')
        ).filter(LogEntry.project_id == project_id)
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        row = result.one()
        
        return {
            "first": row.first.isoformat() if row.first else None,
            "last": row.last.isoformat() if row.last else None
        }
    
    async def _get_log_level_distribution(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get log level distribution for pie chart"""
        query = select(
            LogEntry.log_level,
            func.count(LogEntry.id).label('count')
        ).filter(
            LogEntry.project_id == project_id
        ).group_by(LogEntry.log_level)
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # Format for Recharts
        return [
            {"name": row.log_level, "value": row.count}
            for row in rows
        ]
    
    async def _get_timeline_data(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get timeline data (logs per hour/day)"""
        # Determine granularity based on date range
        date_range = await self._get_date_range(project_id, log_file_id)
        
        if not date_range["first"]:
            return []
        
        first_date = datetime.fromisoformat(date_range["first"])
        last_date = datetime.fromisoformat(date_range["last"])
        duration = (last_date - first_date).total_seconds() / 3600  # hours
        
        # Use hourly if < 7 days, otherwise daily
        if duration < 168:  # 7 days
            interval = "1 hour"
            time_format = "%Y-%m-%d %H:00"
        else:
            interval = "1 day"
            time_format = "%Y-%m-%d"
        
        # PostgreSQL time_bucket query (TimescaleDB)
        query = f"""
            SELECT 
                time_bucket('{interval}', timestamp) AS bucket,
                log_level,
                COUNT(*) as count
            FROM log_entries
            WHERE project_id = :project_id
            {" AND log_file_id = :log_file_id" if log_file_id else ""}
            GROUP BY bucket, log_level
            ORDER BY bucket
        """
        
        params = {"project_id": project_id}
        if log_file_id:
            params["log_file_id"] = log_file_id
        
        result = await self.db.execute(query, params)
        rows = result.all()
        
        # Transform to Recharts format
        timeline_dict = {}
        for row in rows:
            time_key = row.bucket.strftime(time_format)
            if time_key not in timeline_dict:
                timeline_dict[time_key] = {"time": time_key}
            timeline_dict[time_key][row.log_level] = row.count
        
        return list(timeline_dict.values())
    
    async def _get_top_messages(
        self,
        project_id: str,
        log_file_id: Optional[str],
        log_level: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top N error/warning messages"""
        query = select(
            LogEntry.message,
            func.count(LogEntry.id).label('count')
        ).filter(
            LogEntry.project_id == project_id,
            LogEntry.log_level == log_level
        ).group_by(
            LogEntry.message
        ).order_by(
            desc('count')
        ).limit(limit)
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "message": row.message[:100] + "..." if len(row.message) > 100 else row.message,
                "count": row.count
            }
            for row in rows
        ]
    
    async def _get_unique_sources_count(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> int:
        """Get count of unique log sources"""
        query = select(
            func.count(func.distinct(LogEntry.source))
        ).filter(LogEntry.project_id == project_id)
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def calculate_error_analysis(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate error analysis metrics:
        - Error frequency over time
        - Error categorization
        - MTBF (Mean Time Between Failures)
        - Error hotspots
        """
        
        # Error frequency over time
        error_timeline = await self._get_error_timeline(project_id, log_file_id)
        
        # Error by service/component
        error_by_service = await self._get_errors_by_service(project_id, log_file_id)
        
        # MTBF calculation
        mtbf = await self._calculate_mtbf(project_id, log_file_id)
        
        # Error hotspots (sources with most errors)
        error_hotspots = await self._get_error_hotspots(project_id, log_file_id)
        
        # Error categorization
        error_categories = await self._categorize_errors(project_id, log_file_id)
        
        # Recurring vs first-time errors
        error_recurrence = await self._analyze_error_recurrence(project_id, log_file_id)
        
        return {
            "error_timeline": error_timeline,
            "errors_by_service": error_by_service,
            "mtbf_hours": mtbf,
            "error_hotspots": error_hotspots,
            "error_categories": error_categories,
            "error_recurrence": error_recurrence,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def _get_error_timeline(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get error count over time"""
        query = """
            SELECT 
                time_bucket('1 hour', timestamp) AS bucket,
                COUNT(*) as error_count
            FROM log_entries
            WHERE project_id = :project_id
            AND log_level IN ('ERROR', 'CRITICAL')
            {log_file_filter}
            GROUP BY bucket
            ORDER BY bucket
        """.format(
            log_file_filter="AND log_file_id = :log_file_id" if log_file_id else ""
        )
        
        params = {"project_id": project_id}
        if log_file_id:
            params["log_file_id"] = log_file_id
        
        result = await self.db.execute(query, params)
        rows = result.all()
        
        return [
            {
                "time": row.bucket.isoformat(),
                "count": row.error_count
            }
            for row in rows
        ]

    async def _get_errors_by_service(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get error count by service/source"""
        query = select(
            LogEntry.source,
            func.count(LogEntry.id).label('count')
        ).filter(
            LogEntry.project_id == project_id,
            LogEntry.log_level.in_(['ERROR', 'CRITICAL'])
        ).group_by(
            LogEntry.source
        ).order_by(
            desc('count')
        ).limit(20)
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {"service": row.source or "Unknown", "count": row.count}
            for row in rows
        ]

    async def _calculate_mtbf(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> float:
        """Calculate Mean Time Between Failures in hours"""
        query = select(LogEntry.timestamp).filter(
            LogEntry.project_id == project_id,
            LogEntry.log_level.in_(['ERROR', 'CRITICAL'])
        ).order_by(LogEntry.timestamp)
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        timestamps = [row[0] for row in result.all()]
        
        if len(timestamps) < 2:
            return 0.0
        
        # Calculate time differences
        intervals = []
        for i in range(1, len(timestamps)):
            delta = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
            intervals.append(delta)
        
        # Return average
        return sum(intervals) / len(intervals) if intervals else 0.0

    async def _get_error_hotspots(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get sources with most errors"""
        query = select(
            LogEntry.source,
            func.count(LogEntry.id).label('error_count'),
            func.count(func.distinct(LogEntry.message)).label('unique_errors')
        ).filter(
            LogEntry.project_id == project_id,
            LogEntry.log_level.in_(['ERROR', 'CRITICAL'])
        ).group_by(
            LogEntry.source
        ).order_by(
            desc('error_count')
        ).limit(10)
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "source": row.source or "Unknown",
                "error_count": row.error_count,
                "unique_errors": row.unique_errors
            }
            for row in rows
        ]

    async def _categorize_errors(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> Dict[str, int]:
        """Categorize errors by type (timeout, connection, etc.)"""
        # Get all error messages
        query = select(LogEntry.message).filter(
            LogEntry.project_id == project_id,
            LogEntry.log_level.in_(['ERROR', 'CRITICAL'])
        )
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        messages = [row[0].lower() for row in result.all()]
        
        # Simple keyword-based categorization
        categories = {
            "timeout": 0,
            "connection": 0,
            "null_pointer": 0,
            "permission": 0,
            "not_found": 0,
            "database": 0,
            "network": 0,
            "other": 0
        }
        
        keywords = {
            "timeout": ["timeout", "timed out", "time out"],
            "connection": ["connection refused", "connection failed", "cannot connect"],
            "null_pointer": ["null pointer", "nullpointerexception", "none type"],
            "permission": ["permission denied", "access denied", "forbidden"],
            "not_found": ["not found", "404", "does not exist"],
            "database": ["database error", "sql", "query failed"],
            "network": ["network error", "unreachable", "connection reset"]
        }
        
        for message in messages:
            categorized = False
            for category, terms in keywords.items():
                if any(term in message for term in terms):
                    categories[category] += 1
                    categorized = True
                    break
            if not categorized:
                categories["other"] += 1
        
        return categories

    async def _analyze_error_recurrence(
        self,
        project_id: str,
        log_file_id: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze recurring vs first-time errors"""
        query = select(
            LogEntry.message,
            func.count(LogEntry.id).label('count'),
            func.min(LogEntry.timestamp).label('first_seen'),
            func.max(LogEntry.timestamp).label('last_seen')
        ).filter(
            LogEntry.project_id == project_id,
            LogEntry.log_level.in_(['ERROR', 'CRITICAL'])
        ).group_by(LogEntry.message)
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        recurring = sum(1 for row in rows if row.count > 1)
        first_time = sum(1 for row in rows if row.count == 1)
        
        return {
            "recurring_errors": recurring,
            "first_time_errors": first_time,
            "total_unique_errors": len(rows)
        }
