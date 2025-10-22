"""
Database monitoring and performance tracking
Real-time monitoring of database health and performance
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class DatabaseMonitor:
    """Monitor database performance and health"""
    
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self.monitoring_enabled = True
        self.alert_thresholds = {
            "slow_query_time": 2.0,  # seconds
            "connection_usage": 0.8,  # 80% of pool
            "disk_usage": 0.9,  # 90% disk usage
            "memory_usage": 0.85,  # 85% memory usage
            "error_rate": 0.05  # 5% error rate
        }
        self.metrics_history = []
        self.max_history_size = 1000
    
    async def get_database_metrics(self) -> Dict[str, Any]:
        """Get comprehensive database metrics"""
        try:
            async with self.engine.connect() as conn:
                metrics = {}
                
                # Basic connection info
                metrics.update(await self._get_connection_metrics(conn))
                
                # Performance metrics
                metrics.update(await self._get_performance_metrics(conn))
                
                # Storage metrics
                metrics.update(await self._get_storage_metrics(conn))
                
                # Query metrics
                metrics.update(await self._get_query_metrics(conn))
                
                # Index metrics
                metrics.update(await self._get_index_metrics(conn))
                
                # Lock metrics
                metrics.update(await self._get_lock_metrics(conn))
                
                # Add timestamp
                metrics["timestamp"] = datetime.utcnow().isoformat()
                
                # Store in history
                self._store_metrics(metrics)
                
                return metrics
                
        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def _get_connection_metrics(self, conn) -> Dict[str, Any]:
        """Get connection pool metrics"""
        try:
            # Connection pool status
            pool_status = {
                "pool_size": self.engine.pool.size(),
                "checked_in": self.engine.pool.checkedin(),
                "checked_out": self.engine.pool.checkedout(),
                "overflow": self.engine.pool.overflow(),
                "invalid": self.engine.pool.invalid()
            }
            
            # Active connections
            result = await conn.execute(text("""
                SELECT 
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections,
                    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
                FROM pg_stat_activity 
                WHERE datname = current_database()
            """))
            
            connection_stats = dict(result.first())
            
            return {
                "connection_pool": pool_status,
                "active_connections": connection_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting connection metrics: {e}")
            return {}
    
    async def _get_performance_metrics(self, conn) -> Dict[str, Any]:
        """Get database performance metrics"""
        try:
            # Database statistics
            result = await conn.execute(text("""
                SELECT 
                    numbackends as backend_processes,
                    xact_commit as transactions_committed,
                    xact_rollback as transactions_rolled_back,
                    blks_read as blocks_read,
                    blks_hit as blocks_hit,
                    tup_returned as tuples_returned,
                    tup_fetched as tuples_fetched,
                    tup_inserted as tuples_inserted,
                    tup_updated as tuples_updated,
                    tup_deleted as tuples_deleted,
                    temp_files as temporary_files,
                    temp_bytes as temporary_bytes,
                    deadlocks as deadlocks,
                    checksum_failures as checksum_failures
                FROM pg_stat_database 
                WHERE datname = current_database()
            """))
            
            db_stats = dict(result.first())
            
            # Calculate hit ratio
            if db_stats["blocks_read"] + db_stats["blocks_hit"] > 0:
                hit_ratio = db_stats["blocks_hit"] / (db_stats["blocks_read"] + db_stats["blocks_hit"])
            else:
                hit_ratio = 0
            
            return {
                "database_stats": db_stats,
                "cache_hit_ratio": hit_ratio
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def _get_storage_metrics(self, conn) -> Dict[str, Any]:
        """Get storage and disk usage metrics"""
        try:
            # Database size
            result = await conn.execute(text("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as database_size,
                    pg_database_size(current_database()) as database_size_bytes
            """))
            
            db_size = dict(result.first())
            
            # Table sizes
            result = await conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 20
            """))
            
            table_sizes = [dict(row) for row in result]
            
            # Index sizes
            result = await conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||indexname)) as size,
                    pg_relation_size(schemaname||'.'||indexname) as size_bytes
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY pg_relation_size(schemaname||'.'||indexname) DESC
                LIMIT 20
            """))
            
            index_sizes = [dict(row) for row in result]
            
            return {
                "database_size": db_size,
                "table_sizes": table_sizes,
                "index_sizes": index_sizes
            }
            
        except Exception as e:
            logger.error(f"Error getting storage metrics: {e}")
            return {}
    
    async def _get_query_metrics(self, conn) -> Dict[str, Any]:
        """Get query performance metrics"""
        try:
            # Slow queries (if pg_stat_statements is enabled)
            slow_queries = []
            try:
                result = await conn.execute(text("""
                    SELECT 
                        query,
                        calls,
                        total_exec_time,
                        mean_exec_time,
                        stddev_exec_time,
                        rows,
                        100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                    FROM pg_stat_statements 
                    WHERE mean_exec_time > 1000
                    ORDER BY mean_exec_time DESC 
                    LIMIT 10
                """))
                
                slow_queries = [dict(row) for row in result]
            except Exception:
                # pg_stat_statements might not be enabled
                pass
            
            # Query statistics
            result = await conn.execute(text("""
                SELECT 
                    count(*) as total_queries,
                    sum(calls) as total_calls,
                    avg(mean_exec_time) as avg_exec_time,
                    max(mean_exec_time) as max_exec_time
                FROM pg_stat_statements
            """))
            
            query_stats = dict(result.first()) if result.first() else {}
            
            return {
                "slow_queries": slow_queries,
                "query_statistics": query_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting query metrics: {e}")
            return {}
    
    async def _get_index_metrics(self, conn) -> Dict[str, Any]:
        """Get index usage and performance metrics"""
        try:
            # Index usage statistics
            result = await conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    CASE 
                        WHEN idx_scan = 0 THEN 'UNUSED'
                        WHEN idx_scan < 100 THEN 'LOW_USAGE'
                        ELSE 'HIGH_USAGE'
                    END as usage_level
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC
                LIMIT 50
            """))
            
            index_usage = [dict(row) for row in result]
            
            # Unused indexes
            result = await conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||indexname)) as size
                FROM pg_stat_user_indexes 
                WHERE idx_scan = 0
                ORDER BY pg_relation_size(schemaname||'.'||indexname) DESC
            """))
            
            unused_indexes = [dict(row) for row in result]
            
            return {
                "index_usage": index_usage,
                "unused_indexes": unused_indexes
            }
            
        except Exception as e:
            logger.error(f"Error getting index metrics: {e}")
            return {}
    
    async def _get_lock_metrics(self, conn) -> Dict[str, Any]:
        """Get lock and blocking metrics"""
        try:
            # Current locks
            result = await conn.execute(text("""
                SELECT 
                    mode,
                    count(*) as lock_count
                FROM pg_locks 
                WHERE granted = true
                GROUP BY mode
                ORDER BY lock_count DESC
            """))
            
            current_locks = [dict(row) for row in result]
            
            # Blocking queries
            result = await conn.execute(text("""
                SELECT 
                    blocked_locks.pid AS blocked_pid,
                    blocked_activity.usename AS blocked_user,
                    blocking_locks.pid AS blocking_pid,
                    blocking_activity.usename AS blocking_user,
                    blocked_activity.query AS blocked_statement,
                    blocking_activity.query AS current_statement_in_blocking_process
                FROM pg_catalog.pg_locks blocked_locks
                JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
                JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
                    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
                    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                    AND blocking_locks.pid != blocked_locks.pid
                JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
                WHERE NOT blocked_locks.granted
            """))
            
            blocking_queries = [dict(row) for row in result]
            
            return {
                "current_locks": current_locks,
                "blocking_queries": blocking_queries
            }
            
        except Exception as e:
            logger.error(f"Error getting lock metrics: {e}")
            return {}
    
    def _store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in history"""
        self.metrics_history.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts"""
        alerts = []
        
        try:
            metrics = await self.get_database_metrics()
            
            # Check connection usage
            if "connection_pool" in metrics:
                pool = metrics["connection_pool"]
                usage_ratio = pool["checked_out"] / (pool["pool_size"] + pool["overflow"])
                
                if usage_ratio > self.alert_thresholds["connection_usage"]:
                    alerts.append({
                        "type": "high_connection_usage",
                        "severity": "warning",
                        "message": f"Connection pool usage is {usage_ratio:.1%}",
                        "value": usage_ratio,
                        "threshold": self.alert_thresholds["connection_usage"]
                    })
            
            # Check cache hit ratio
            if "cache_hit_ratio" in metrics:
                hit_ratio = metrics["cache_hit_ratio"]
                
                if hit_ratio < 0.95:  # Less than 95% hit ratio
                    alerts.append({
                        "type": "low_cache_hit_ratio",
                        "severity": "warning",
                        "message": f"Cache hit ratio is {hit_ratio:.1%}",
                        "value": hit_ratio,
                        "threshold": 0.95
                    })
            
            # Check for slow queries
            if "slow_queries" in metrics and metrics["slow_queries"]:
                for query in metrics["slow_queries"][:5]:  # Top 5 slow queries
                    if query["mean_exec_time"] > self.alert_thresholds["slow_query_time"] * 1000:  # Convert to ms
                        alerts.append({
                            "type": "slow_query",
                            "severity": "info",
                            "message": f"Slow query detected: {query['mean_exec_time']:.0f}ms",
                            "query": query["query"][:100] + "..." if len(query["query"]) > 100 else query["query"],
                            "execution_time": query["mean_exec_time"]
                        })
            
            # Check for unused indexes
            if "unused_indexes" in metrics and metrics["unused_indexes"]:
                large_unused = [idx for idx in metrics["unused_indexes"] if "MB" in idx.get("size", "")]
                
                if large_unused:
                    alerts.append({
                        "type": "unused_indexes",
                        "severity": "info",
                        "message": f"Found {len(large_unused)} large unused indexes",
                        "unused_indexes": large_unused[:5]  # Top 5
                    })
            
            # Check for blocking queries
            if "blocking_queries" in metrics and metrics["blocking_queries"]:
                alerts.append({
                    "type": "blocking_queries",
                    "severity": "warning",
                    "message": f"Found {len(metrics['blocking_queries'])} blocking queries",
                    "blocking_queries": metrics["blocking_queries"]
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return [{
                "type": "monitoring_error",
                "severity": "error",
                "message": f"Error checking database alerts: {e}"
            }]
    
    async def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Filter metrics from the specified time period
            recent_metrics = [
                m for m in self.metrics_history
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ]
            
            if not recent_metrics:
                return {"error": "No metrics available for the specified period"}
            
            # Extract trends
            trends = {
                "cache_hit_ratios": [],
                "connection_usage": [],
                "timestamps": []
            }
            
            for metrics in recent_metrics:
                trends["timestamps"].append(metrics["timestamp"])
                
                if "cache_hit_ratio" in metrics:
                    trends["cache_hit_ratios"].append(metrics["cache_hit_ratio"])
                else:
                    trends["cache_hit_ratios"].append(None)
                
                if "connection_pool" in metrics:
                    pool = metrics["connection_pool"]
                    usage = pool["checked_out"] / (pool["pool_size"] + pool["overflow"])
                    trends["connection_usage"].append(usage)
                else:
                    trends["connection_usage"].append(None)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return {"error": str(e)}
    
    async def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get database optimization recommendations"""
        recommendations = []
        
        try:
            metrics = await self.get_database_metrics()
            
            # Check for unused indexes
            if "unused_indexes" in metrics and metrics["unused_indexes"]:
                large_unused = [idx for idx in metrics["unused_indexes"] if "MB" in idx.get("size", "")]
                
                if large_unused:
                    recommendations.append({
                        "type": "index_optimization",
                        "priority": "medium",
                        "title": "Remove unused indexes",
                        "description": f"Found {len(large_unused)} large unused indexes that can be removed to improve write performance",
                        "action": "Consider dropping unused indexes",
                        "impact": "Improved write performance, reduced storage usage"
                    })
            
            # Check cache hit ratio
            if "cache_hit_ratio" in metrics:
                hit_ratio = metrics["cache_hit_ratio"]
                
                if hit_ratio < 0.90:
                    recommendations.append({
                        "type": "cache_optimization",
                        "priority": "high",
                        "title": "Improve cache hit ratio",
                        "description": f"Cache hit ratio is {hit_ratio:.1%}, consider increasing shared_buffers",
                        "action": "Increase shared_buffers in postgresql.conf",
                        "impact": "Better query performance, reduced I/O"
                    })
            
            # Check for slow queries
            if "slow_queries" in metrics and metrics["slow_queries"]:
                slow_count = len([q for q in metrics["slow_queries"] if q["mean_exec_time"] > 2000])
                
                if slow_count > 0:
                    recommendations.append({
                        "type": "query_optimization",
                        "priority": "high",
                        "title": "Optimize slow queries",
                        "description": f"Found {slow_count} queries taking more than 2 seconds",
                        "action": "Review and optimize slow queries, add appropriate indexes",
                        "impact": "Improved query performance"
                    })
            
            # Check connection usage
            if "connection_pool" in metrics:
                pool = metrics["connection_pool"]
                usage_ratio = pool["checked_out"] / (pool["pool_size"] + pool["overflow"])
                
                if usage_ratio > 0.7:
                    recommendations.append({
                        "type": "connection_optimization",
                        "priority": "medium",
                        "title": "Optimize connection pool",
                        "description": f"Connection pool usage is {usage_ratio:.1%}",
                        "action": "Consider increasing pool size or optimizing connection usage",
                        "impact": "Better connection availability"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return [{
                "type": "error",
                "priority": "low",
                "title": "Monitoring Error",
                "description": f"Error generating recommendations: {e}",
                "action": "Check monitoring system",
                "impact": "Unable to provide optimization recommendations"
            }]
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous monitoring"""
        self.monitoring_enabled = True
        
        while self.monitoring_enabled:
            try:
                # Collect metrics
                metrics = await self.get_database_metrics()
                
                # Check for alerts
                alerts = await self.check_alerts()
                
                # Log alerts
                for alert in alerts:
                    if alert["severity"] == "error":
                        logger.error(f"Database alert: {alert['message']}")
                    elif alert["severity"] == "warning":
                        logger.warning(f"Database alert: {alert['message']}")
                    else:
                        logger.info(f"Database alert: {alert['message']}")
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_enabled = False
        logger.info("Database monitoring stopped")
