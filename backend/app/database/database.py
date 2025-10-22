"""
Database configuration for Loglytics AI
Optimized for high performance with connection pooling, query optimization, and monitoring
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from app.config import settings
from app.base import Base
import logging
import time
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Enhanced database configuration
class DatabaseConfig:
    """Database configuration with performance optimizations"""
    
    def __init__(self):
        self.pool_size = 20
        self.max_overflow = 10
        self.pool_timeout = 30
        self.pool_recycle = 3600
        self.pool_pre_ping = True
        self.echo = settings.DEBUG
        self.future = True
        
        # Query optimization settings
        self.query_cache_size = 500
        self.slow_query_threshold = 1.0  # seconds
        
        # Connection management
        self.max_connections = self.pool_size + self.max_overflow
        self.connection_retry_attempts = 3
        self.connection_retry_delay = 1.0

# Create database configuration
db_config = DatabaseConfig()

# Create async database engine with optimized settings
engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=db_config.pool_size,
    max_overflow=db_config.max_overflow,
    pool_timeout=db_config.pool_timeout,
    pool_recycle=db_config.pool_recycle,
    pool_pre_ping=db_config.pool_pre_ping,
    echo=db_config.echo,
    future=db_config.future,
    # Additional optimizations
    connect_args={
        # Avoid setting server-level parameters that require a DB restart (e.g., shared_preload_libraries)
        "server_settings": {
            "application_name": "loglytics_ai",
            "jit": "off",
        }
    }
)

# Query monitoring and optimization
class QueryMonitor:
    """Monitor and optimize database queries"""
    
    def __init__(self):
        self.slow_queries = []
        self.query_stats = {}
        self.slow_query_threshold = db_config.slow_query_threshold
    
    def log_slow_query(self, statement: str, parameters: Dict, duration: float):
        """Log slow queries for optimization"""
        if duration > self.slow_query_threshold:
            slow_query = {
                "statement": statement,
                "parameters": parameters,
                "duration": duration,
                "timestamp": time.time()
            }
            self.slow_queries.append(slow_query)
            logger.warning(f"Slow query detected ({duration:.2f}s): {statement[:100]}...")
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return {
            "total_queries": len(self.query_stats),
            "slow_queries": len(self.slow_queries),
            "average_duration": sum(self.query_stats.values()) / len(self.query_stats) if self.query_stats else 0,
            "slow_query_threshold": self.slow_query_threshold
        }

# Global query monitor
query_monitor = QueryMonitor()

# Add query monitoring event listeners
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution start time"""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution end time and monitor performance"""
    if hasattr(context, '_query_start_time'):
        duration = time.time() - context._query_start_time
        query_monitor.log_slow_query(statement, parameters, duration)
        
        # Update query stats
        query_key = statement[:50]  # Use first 50 chars as key
        if query_key not in query_monitor.query_stats:
            query_monitor.query_stats[query_key] = []
        query_monitor.query_stats[query_key].append(duration)

# Create async session factory with enhanced configuration
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


async def get_db():
    """Dependency to get database session with retry logic"""
    retry_count = 0
    max_retries = db_config.connection_retry_attempts
    
    while retry_count < max_retries:
        try:
            async with AsyncSessionLocal() as session:
                try:
                    yield session
                except Exception as e:
                    logger.error(f"Database session error: {e}")
                    await session.rollback()
                    raise
                finally:
                    await session.close()
            break
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                raise
            else:
                logger.warning(f"Database connection attempt {retry_count} failed, retrying...")
                await asyncio.sleep(db_config.connection_retry_delay * retry_count)

@asynccontextmanager
async def get_db_transaction():
    """Context manager for database transactions with automatic rollback"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            await session.close()

async def execute_with_retry(query, parameters=None, max_retries=3):
    """Execute query with retry logic for transient failures"""
    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(query, parameters or {})
                await session.commit()
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Query execution failed after {max_retries} attempts: {e}")
                raise
            else:
                logger.warning(f"Query execution attempt {attempt + 1} failed, retrying...")
                await asyncio.sleep(1 * (attempt + 1))


async def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they are registered
        from app.models import (
            User, Project, Chat, Message, LogFile, LogEntry,
            RAGVector, AnalyticsCache, LiveLogConnection, Alert,
            APIKey, AuditLog, ProjectShare, Webhook, UsageTracking
        )
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")


async def test_db_connection():
    """Test PostgreSQL database connection"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"✅ PostgreSQL connection successful!")
            logger.info(f"PostgreSQL version: {version}")
            return True, version
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False, str(e)


async def test_connection():
    """
    Test database connection and print results
    Convenience function for quick connection testing
    """
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text('SELECT version()'))
            version = result.scalar()
            print(f'✅ Connected to PostgreSQL: {version}')
            return True
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        return False

async def get_database_health() -> Dict[str, Any]:
    """Get comprehensive database health status"""
    try:
        async with engine.connect() as conn:
            # Get basic connection info
            version_result = await conn.execute(text("SELECT version()"))
            version = version_result.scalar()
            
            # Get connection pool status
            pool_status = {
                "pool_size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
                "invalid": engine.pool.invalid()
            }
            
            # Get database size
            size_result = await conn.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
            """))
            db_size = size_result.scalar()
            
            # Get active connections
            connections_result = await conn.execute(text("""
                SELECT count(*) as active_connections 
                FROM pg_stat_activity 
                WHERE state = 'active'
            """))
            active_connections = connections_result.scalar()
            
            # Get slow queries (if pg_stat_statements is enabled)
            slow_queries = []
            try:
                slow_result = await conn.execute(text("""
                    SELECT query, mean_exec_time, calls, total_exec_time
                    FROM pg_stat_statements 
                    WHERE mean_exec_time > 1000
                    ORDER BY mean_exec_time DESC 
                    LIMIT 10
                """))
                slow_queries = [dict(row) for row in slow_result]
            except Exception:
                # pg_stat_statements might not be enabled
                pass
            
            # Get index usage statistics
            index_stats = []
            try:
                index_result = await conn.execute(text("""
                    SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes 
                    ORDER BY idx_scan DESC 
                    LIMIT 20
                """))
                index_stats = [dict(row) for row in index_result]
            except Exception:
                pass
            
            return {
                "status": "healthy",
                "version": version,
                "pool_status": pool_status,
                "database_size": db_size,
                "active_connections": active_connections,
                "slow_queries": slow_queries,
                "index_usage": index_stats,
                "query_monitor_stats": query_monitor.get_query_stats(),
                "timestamp": time.time()
            }
            
    except Exception as e:
        logger.error(f"Error getting database health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

async def optimize_database():
    """Run database optimization tasks"""
    try:
        async with engine.connect() as conn:
            # Update table statistics
            await conn.execute(text("ANALYZE"))
            logger.info("Database statistics updated")
            
            # Reindex if needed (this can be expensive, so run during maintenance windows)
            # await conn.execute(text("REINDEX DATABASE loglytics_ai"))
            
            # Vacuum analyze
            await conn.execute(text("VACUUM ANALYZE"))
            logger.info("Database vacuum and analyze completed")
            
            return True
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return False

async def get_table_sizes() -> Dict[str, str]:
    """Get sizes of all tables in the database"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """))
            return {row.tablename: row.size for row in result}
    except Exception as e:
        logger.error(f"Error getting table sizes: {e}")
        return {}

async def get_index_usage() -> Dict[str, Any]:
    """Get index usage statistics for optimization"""
    try:
        async with engine.connect() as conn:
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
            """))
            return [dict(row) for row in result]
    except Exception as e:
        logger.error(f"Error getting index usage: {e}")
        return []

async def cleanup_old_data():
    """Clean up old data based on retention policies"""
    try:
        async with engine.connect() as conn:
            # Clean up old audit logs (older than 7 years)
            audit_result = await conn.execute(text("""
                DELETE FROM audit_logs 
                WHERE created_at < NOW() - INTERVAL '7 years'
            """))
            audit_deleted = audit_result.rowcount
            
            # Clean up old log entries (older than 90 days)
            log_result = await conn.execute(text("""
                DELETE FROM log_entries 
                WHERE timestamp < NOW() - INTERVAL '90 days'
            """))
            log_deleted = log_result.rowcount
            
            # Clean up old analytics cache (older than 30 days)
            cache_result = await conn.execute(text("""
                DELETE FROM analytics_cache 
                WHERE created_at < NOW() - INTERVAL '30 days'
            """))
            cache_deleted = cache_result.rowcount
            
            await conn.commit()
            
            logger.info(f"Data cleanup completed: {audit_deleted} audit logs, {log_deleted} log entries, {cache_deleted} cache entries deleted")
            return {
                "audit_logs_deleted": audit_deleted,
                "log_entries_deleted": log_deleted,
                "cache_entries_deleted": cache_deleted
            }
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        return {}