"""
Optimized database queries with eager loading and pagination
Performance-optimized query patterns for Loglytics AI
"""

from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OptimizedQueries:
    """Optimized database queries with performance best practices"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_with_projects_and_recent_chats(self, user_id: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """Get user with projects and recent chats (eager loading)"""
        try:
            from app.models import User, Project, ChatSession
            
            # Eager load relationships to avoid N+1 queries
            result = await self.session.execute(
                select(User)
                .options(
                    selectinload(User.projects)
                    .selectinload(Project.chat_sessions)
                    .options(selectinload(ChatSession.messages).limit(limit))
                )
                .where(User.id == user_id)
            )
            
            user = result.scalar_one_or_none()
            if not user:
                return None
            
            # Convert to dict for better performance
            return {
                "id": user.id,
                "email": user.email,
                "subscription_tier": user.subscription_tier,
                "projects": [
                    {
                        "id": project.id,
                        "name": project.name,
                        "recent_chats": [
                            {
                                "id": chat.id,
                                "title": chat.title,
                                "created_at": chat.created_at,
                                "message_count": len(chat.messages)
                            }
                            for chat in project.chat_sessions[-limit:]
                        ]
                    }
                    for project in user.projects
                ]
            }
        except Exception as e:
            logger.error(f"Error getting user with projects: {e}")
            return None
    
    async def get_paginated_log_entries(
        self, 
        user_id: str, 
        project_id: Optional[str] = None,
        log_level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 0,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Get paginated log entries with filters"""
        try:
            from app.models import LogEntry
            
            # Build query with filters
            query = select(LogEntry).where(LogEntry.user_id == user_id)
            
            if project_id:
                query = query.where(LogEntry.project_id == project_id)
            
            if log_level:
                query = query.where(LogEntry.log_level == log_level)
            
            if start_date:
                query = query.where(LogEntry.timestamp >= start_date)
            
            if end_date:
                query = query.where(LogEntry.timestamp <= end_date)
            
            # Get total count for pagination
            count_query = select(func.count(LogEntry.id)).where(LogEntry.user_id == user_id)
            if project_id:
                count_query = count_query.where(LogEntry.project_id == project_id)
            if log_level:
                count_query = count_query.where(LogEntry.log_level == log_level)
            if start_date:
                count_query = count_query.where(LogEntry.timestamp >= start_date)
            if end_date:
                count_query = count_query.where(LogEntry.timestamp <= end_date)
            
            total_count = await self.session.scalar(count_query)
            
            # Apply pagination and ordering
            query = query.order_by(desc(LogEntry.timestamp)).offset(page * page_size).limit(page_size)
            
            result = await self.session.execute(query)
            log_entries = result.scalars().all()
            
            return {
                "log_entries": [
                    {
                        "id": entry.id,
                        "timestamp": entry.timestamp,
                        "log_level": entry.log_level,
                        "message": entry.message,
                        "source": entry.source,
                        "metadata": entry.metadata
                    }
                    for entry in log_entries
                ],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size,
                    "has_next": (page + 1) * page_size < total_count,
                    "has_prev": page > 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting paginated log entries: {e}")
            return {"log_entries": [], "pagination": {}}
    
    async def get_log_level_stats(self, project_id: str) -> Dict[str, int]:
        """Get log level statistics using database aggregation"""
        try:
            from app.models import LogEntry
            
            result = await self.session.execute(
                select(
                    LogEntry.log_level,
                    func.count(LogEntry.id).label('count')
                )
                .where(LogEntry.project_id == project_id)
                .group_by(LogEntry.log_level)
            )
            
            return {row.log_level: row.count for row in result}
        except Exception as e:
            logger.error(f"Error getting log level stats: {e}")
            return {}
    
    async def get_recent_errors(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent error logs with optimized query"""
        try:
            from app.models import LogEntry
            
            result = await self.session.execute(
                select(LogEntry)
                .where(
                    and_(
                        LogEntry.project_id == project_id,
                        LogEntry.log_level == 'ERROR'
                    )
                )
                .order_by(desc(LogEntry.timestamp))
                .limit(limit)
            )
            
            return [
                {
                    "id": entry.id,
                    "timestamp": entry.timestamp,
                    "message": entry.message,
                    "source": entry.source,
                    "metadata": entry.metadata
                }
                for entry in result.scalars().all()
            ]
        except Exception as e:
            logger.error(f"Error getting recent errors: {e}")
            return []
    
    async def get_user_activity_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user activity summary with database aggregations"""
        try:
            from app.models import LogEntry, Project, ChatSession
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get log entry counts
            log_count = await self.session.scalar(
                select(func.count(LogEntry.id))
                .where(
                    and_(
                        LogEntry.user_id == user_id,
                        LogEntry.timestamp >= start_date
                    )
                )
            )
            
            # Get project count
            project_count = await self.session.scalar(
                select(func.count(Project.id))
                .where(Project.user_id == user_id)
            )
            
            # Get chat session count
            chat_count = await self.session.scalar(
                select(func.count(ChatSession.id))
                .where(
                    and_(
                        ChatSession.user_id == user_id,
                        ChatSession.created_at >= start_date
                    )
                )
            )
            
            # Get log level distribution
            log_level_stats = await self.session.execute(
                select(
                    LogEntry.log_level,
                    func.count(LogEntry.id).label('count')
                )
                .where(
                    and_(
                        LogEntry.user_id == user_id,
                        LogEntry.timestamp >= start_date
                    )
                )
                .group_by(LogEntry.log_level)
            )
            
            return {
                "period_days": days,
                "log_entries": log_count,
                "projects": project_count,
                "chat_sessions": chat_count,
                "log_level_distribution": {row.log_level: row.count for row in log_level_stats},
                "start_date": start_date,
                "end_date": end_date
            }
        except Exception as e:
            logger.error(f"Error getting user activity summary: {e}")
            return {}
    
    async def search_logs(
        self, 
        user_id: str, 
        search_term: str, 
        project_id: Optional[str] = None,
        log_level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search logs with full-text search optimization"""
        try:
            from app.models import LogEntry
            
            # Use PostgreSQL full-text search
            query = select(LogEntry).where(
                and_(
                    LogEntry.user_id == user_id,
                    LogEntry.message.ilike(f"%{search_term}%")
                )
            )
            
            if project_id:
                query = query.where(LogEntry.project_id == project_id)
            
            if log_level:
                query = query.where(LogEntry.log_level == log_level)
            
            query = query.order_by(desc(LogEntry.timestamp)).limit(limit)
            
            result = await self.session.execute(query)
            
            return [
                {
                    "id": entry.id,
                    "timestamp": entry.timestamp,
                    "log_level": entry.log_level,
                    "message": entry.message,
                    "source": entry.source,
                    "project_id": entry.project_id
                }
                for entry in result.scalars().all()
            ]
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return []
    
    async def get_project_analytics(self, project_id: str, days: int = 7) -> Dict[str, Any]:
        """Get project analytics with optimized aggregations"""
        try:
            from app.models import LogEntry, LogFile, ChatSession
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get log entry statistics
            log_stats = await self.session.execute(
                select(
                    func.count(LogEntry.id).label('total_logs'),
                    func.count(LogEntry.id).filter(LogEntry.log_level == 'ERROR').label('error_count'),
                    func.count(LogEntry.id).filter(LogEntry.log_level == 'WARNING').label('warning_count'),
                    func.count(LogEntry.id).filter(LogEntry.log_level == 'INFO').label('info_count')
                )
                .where(
                    and_(
                        LogEntry.project_id == project_id,
                        LogEntry.timestamp >= start_date
                    )
                )
            )
            
            stats = log_stats.first()
            
            # Get file upload statistics
            file_count = await self.session.scalar(
                select(func.count(LogFile.id))
                .where(
                    and_(
                        LogFile.project_id == project_id,
                        LogFile.created_at >= start_date
                    )
                )
            )
            
            # Get chat session count
            chat_count = await self.session.scalar(
                select(func.count(ChatSession.id))
                .where(
                    and_(
                        ChatSession.project_id == project_id,
                        ChatSession.created_at >= start_date
                    )
                )
            )
            
            return {
                "project_id": project_id,
                "period_days": days,
                "total_logs": stats.total_logs or 0,
                "error_count": stats.error_count or 0,
                "warning_count": stats.warning_count or 0,
                "info_count": stats.info_count or 0,
                "file_uploads": file_count or 0,
                "chat_sessions": chat_count or 0,
                "error_rate": (stats.error_count / stats.total_logs * 100) if stats.total_logs else 0,
                "start_date": start_date,
                "end_date": end_date
            }
        except Exception as e:
            logger.error(f"Error getting project analytics: {e}")
            return {}
    
    async def get_top_error_patterns(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top error patterns using database aggregation"""
        try:
            from app.models import LogEntry
            
            result = await self.session.execute(
                select(
                    LogEntry.message,
                    func.count(LogEntry.id).label('count'),
                    func.max(LogEntry.timestamp).label('last_seen')
                )
                .where(
                    and_(
                        LogEntry.project_id == project_id,
                        LogEntry.log_level == 'ERROR'
                    )
                )
                .group_by(LogEntry.message)
                .order_by(desc(func.count(LogEntry.id)))
                .limit(limit)
            )
            
            return [
                {
                    "message": row.message,
                    "count": row.count,
                    "last_seen": row.last_seen
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error getting top error patterns: {e}")
            return []
    
    async def get_vector_search_results(
        self, 
        project_id: str, 
        query_vector: List[float], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get vector search results using pgvector"""
        try:
            from app.models import RAGVector
            
            # Use pgvector cosine similarity
            result = await self.session.execute(
                select(RAGVector)
                .where(RAGVector.project_id == project_id)
                .order_by(RAGVector.embedding.cosine_distance(query_vector))
                .limit(limit)
            )
            
            return [
                {
                    "id": vector.id,
                    "content": vector.content,
                    "metadata": vector.metadata,
                    "similarity": 1 - vector.embedding.cosine_distance(query_vector)
                }
                for vector in result.scalars().all()
            ]
        except Exception as e:
            logger.error(f"Error getting vector search results: {e}")
            return []
    
    async def get_usage_tracking_data(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get usage tracking data with date range"""
        try:
            from app.models import UsageTracking
            
            result = await self.session.execute(
                select(UsageTracking)
                .where(
                    and_(
                        UsageTracking.user_id == user_id,
                        UsageTracking.date >= start_date,
                        UsageTracking.date <= end_date
                    )
                )
                .order_by(UsageTracking.date)
            )
            
            return [
                {
                    "date": tracking.date,
                    "api_calls": tracking.api_calls,
                    "llm_tokens": tracking.llm_tokens,
                    "storage_used": tracking.storage_used,
                    "metadata": tracking.metadata
                }
                for tracking in result.scalars().all()
            ]
        except Exception as e:
            logger.error(f"Error getting usage tracking data: {e}")
            return []
    
    async def get_audit_logs(
        self, 
        user_id: str, 
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 0,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get audit logs with pagination and filters"""
        try:
            from app.models import AuditLog
            
            query = select(AuditLog).where(AuditLog.user_id == user_id)
            
            if action:
                query = query.where(AuditLog.action == action)
            
            if start_date:
                query = query.where(AuditLog.created_at >= start_date)
            
            if end_date:
                query = query.where(AuditLog.created_at <= end_date)
            
            # Get total count
            count_query = select(func.count(AuditLog.id)).where(AuditLog.user_id == user_id)
            if action:
                count_query = count_query.where(AuditLog.action == action)
            if start_date:
                count_query = count_query.where(AuditLog.created_at >= start_date)
            if end_date:
                count_query = count_query.where(AuditLog.created_at <= end_date)
            
            total_count = await self.session.scalar(count_query)
            
            # Apply pagination
            query = query.order_by(desc(AuditLog.created_at)).offset(page * page_size).limit(page_size)
            
            result = await self.session.execute(query)
            audit_logs = result.scalars().all()
            
            return {
                "audit_logs": [
                    {
                        "id": log.id,
                        "action": log.action,
                        "resource_type": log.resource_type,
                        "resource_id": log.resource_id,
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent,
                        "created_at": log.created_at,
                        "metadata": log.metadata
                    }
                    for log in audit_logs
                ],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size,
                    "has_next": (page + 1) * page_size < total_count,
                    "has_prev": page > 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return {"audit_logs": [], "pagination": {}}
