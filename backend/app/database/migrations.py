"""
Database migrations and indexing strategy
Comprehensive indexing for optimal performance
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
import logging

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Handle database migrations and indexing"""
    
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
    
    async def create_indexes(self):
        """Create all critical indexes for performance optimization"""
        indexes = [
            # Users table indexes
            {
                "name": "idx_users_email",
                "table": "users",
                "columns": "email",
                "type": "btree",
                "unique": True
            },
            {
                "name": "idx_users_subscription_tier",
                "table": "users", 
                "columns": "subscription_tier",
                "type": "btree"
            },
            {
                "name": "idx_users_created_at",
                "table": "users",
                "columns": "created_at",
                "type": "btree"
            },
            {
                "name": "idx_users_is_active",
                "table": "users",
                "columns": "is_active",
                "type": "btree"
            },
            
            # Projects table indexes
            {
                "name": "idx_projects_user_id",
                "table": "projects",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_projects_created_at",
                "table": "projects",
                "columns": "created_at",
                "type": "btree"
            },
            {
                "name": "idx_projects_user_created",
                "table": "projects",
                "columns": "user_id, created_at DESC",
                "type": "btree"
            },
            
            # Chat sessions indexes
            {
                "name": "idx_chat_sessions_user_id",
                "table": "chat_sessions",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_chat_sessions_created_at",
                "table": "chat_sessions",
                "columns": "created_at",
                "type": "btree"
            },
            {
                "name": "idx_chat_sessions_user_created",
                "table": "chat_sessions",
                "columns": "user_id, created_at DESC",
                "type": "btree"
            },
            {
                "name": "idx_chat_sessions_is_active",
                "table": "chat_sessions",
                "columns": "is_active",
                "type": "btree"
            },
            
            # Chat messages indexes
            {
                "name": "idx_chat_messages_session_id",
                "table": "chat_messages",
                "columns": "chat_session_id",
                "type": "btree"
            },
            {
                "name": "idx_chat_messages_created_at",
                "table": "chat_messages",
                "columns": "created_at",
                "type": "btree"
            },
            {
                "name": "idx_chat_messages_session_created",
                "table": "chat_messages",
                "columns": "chat_session_id, created_at",
                "type": "btree"
            },
            
            # Log files indexes
            {
                "name": "idx_log_files_project_id",
                "table": "log_files",
                "columns": "project_id",
                "type": "btree"
            },
            {
                "name": "idx_log_files_user_id",
                "table": "log_files",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_log_files_upload_status",
                "table": "log_files",
                "columns": "upload_status",
                "type": "btree"
            },
            {
                "name": "idx_log_files_created_at",
                "table": "log_files",
                "columns": "created_at",
                "type": "btree"
            },
            {
                "name": "idx_log_files_project_status",
                "table": "log_files",
                "columns": "project_id, upload_status",
                "type": "btree"
            },
            
            # Log entries indexes (critical for performance)
            {
                "name": "idx_log_entries_user_id",
                "table": "log_entries",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_log_entries_project_id",
                "table": "log_entries",
                "columns": "project_id",
                "type": "btree"
            },
            {
                "name": "idx_log_entries_log_level",
                "table": "log_entries",
                "columns": "log_level",
                "type": "btree"
            },
            {
                "name": "idx_log_entries_timestamp",
                "table": "log_entries",
                "columns": "timestamp",
                "type": "btree"
            },
            {
                "name": "idx_log_entries_user_project_timestamp",
                "table": "log_entries",
                "columns": "user_id, project_id, timestamp DESC",
                "type": "btree"
            },
            {
                "name": "idx_log_entries_project_level_timestamp",
                "table": "log_entries",
                "columns": "project_id, log_level, timestamp DESC",
                "type": "btree"
            },
            
            # RAG vectors indexes (for vector search)
            {
                "name": "idx_rag_vectors_project_id",
                "table": "rag_vectors",
                "columns": "project_id",
                "type": "btree"
            },
            {
                "name": "idx_rag_vectors_user_id",
                "table": "rag_vectors",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_rag_vectors_embedding",
                "table": "rag_vectors",
                "columns": "embedding",
                "type": "ivfflat",
                "options": "lists = 100"
            },
            
            # Alerts indexes
            {
                "name": "idx_alerts_user_id",
                "table": "alerts",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_alerts_is_read",
                "table": "alerts",
                "columns": "is_read",
                "type": "btree"
            },
            {
                "name": "idx_alerts_created_at",
                "table": "alerts",
                "columns": "created_at",
                "type": "btree"
            },
            {
                "name": "idx_alerts_user_read_created",
                "table": "alerts",
                "columns": "user_id, is_read, created_at DESC",
                "type": "btree"
            },
            
            # Audit logs indexes
            {
                "name": "idx_audit_logs_user_id",
                "table": "audit_logs",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_audit_logs_created_at",
                "table": "audit_logs",
                "columns": "created_at",
                "type": "btree"
            },
            {
                "name": "idx_audit_logs_action",
                "table": "audit_logs",
                "columns": "action",
                "type": "btree"
            },
            {
                "name": "idx_audit_logs_user_created",
                "table": "audit_logs",
                "columns": "user_id, created_at DESC",
                "type": "btree"
            },
            
            # Usage tracking indexes
            {
                "name": "idx_usage_tracking_user_id",
                "table": "usage_tracking",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_usage_tracking_date",
                "table": "usage_tracking",
                "columns": "date",
                "type": "btree"
            },
            {
                "name": "idx_usage_tracking_user_date",
                "table": "usage_tracking",
                "columns": "user_id, date",
                "type": "btree"
            },
            
            # API keys indexes
            {
                "name": "idx_api_keys_user_id",
                "table": "api_keys",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_api_keys_key_hash",
                "table": "api_keys",
                "columns": "key_hash",
                "type": "btree",
                "unique": True
            },
            {
                "name": "idx_api_keys_is_active",
                "table": "api_keys",
                "columns": "is_active",
                "type": "btree"
            },
            
            # Project shares indexes
            {
                "name": "idx_project_shares_project_id",
                "table": "project_shares",
                "columns": "project_id",
                "type": "btree"
            },
            {
                "name": "idx_project_shares_shared_with_user",
                "table": "project_shares",
                "columns": "shared_with_user_id",
                "type": "btree"
            },
            {
                "name": "idx_project_shares_shared_by_user",
                "table": "project_shares",
                "columns": "shared_by_user_id",
                "type": "btree"
            },
            
            # Webhooks indexes
            {
                "name": "idx_webhooks_project_id",
                "table": "webhooks",
                "columns": "project_id",
                "type": "btree"
            },
            {
                "name": "idx_webhooks_is_active",
                "table": "webhooks",
                "columns": "is_active",
                "type": "btree"
            },
            
            # Live log connections indexes
            {
                "name": "idx_live_connections_project_id",
                "table": "live_log_connections",
                "columns": "project_id",
                "type": "btree"
            },
            {
                "name": "idx_live_connections_user_id",
                "table": "live_log_connections",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_live_connections_status",
                "table": "live_log_connections",
                "columns": "status",
                "type": "btree"
            },
            
            # Analytics cache indexes
            {
                "name": "idx_analytics_cache_project_id",
                "table": "analytics_cache",
                "columns": "project_id",
                "type": "btree"
            },
            {
                "name": "idx_analytics_cache_cache_key",
                "table": "analytics_cache",
                "columns": "cache_key",
                "type": "btree",
                "unique": True
            },
            {
                "name": "idx_analytics_cache_created_at",
                "table": "analytics_cache",
                "columns": "created_at",
                "type": "btree"
            },
            
            # Analysis indexes
            {
                "name": "idx_analysis_user_id",
                "table": "analysis",
                "columns": "user_id",
                "type": "btree"
            },
            {
                "name": "idx_analysis_log_file_id",
                "table": "analysis",
                "columns": "log_file_id",
                "type": "btree"
            },
            {
                "name": "idx_analysis_status",
                "table": "analysis",
                "columns": "status",
                "type": "btree"
            },
            {
                "name": "idx_analysis_created_at",
                "table": "analysis",
                "columns": "created_at",
                "type": "btree"
            }
        ]
        
        created_count = 0
        for index in indexes:
            try:
                await self._create_index(index)
                created_count += 1
                logger.info(f"Created index: {index['name']}")
            except Exception as e:
                logger.error(f"Failed to create index {index['name']}: {e}")
        
        logger.info(f"Created {created_count} indexes successfully")
        return created_count
    
    async def _create_index(self, index_config: dict):
        """Create a single index"""
        index_type = index_config.get("type", "btree")
        unique = index_config.get("unique", False)
        options = index_config.get("options", "")
        
        if index_type == "ivfflat":
            # Special handling for vector indexes
            sql = f"""
            CREATE INDEX CONCURRENTLY {index_config['name']} 
            ON {index_config['table']} 
            USING ivfflat ({index_config['columns']}) 
            {options}
            """
        else:
            unique_clause = "UNIQUE" if unique else ""
            sql = f"""
            CREATE {unique_clause} INDEX CONCURRENTLY {index_config['name']} 
            ON {index_config['table']} 
            USING {index_type} ({index_config['columns']})
            """
        
        async with self.engine.connect() as conn:
            await conn.execute(text(sql))
            await conn.commit()
    
    async def create_partial_indexes(self):
        """Create partial indexes for specific conditions"""
        partial_indexes = [
            {
                "name": "idx_active_connections",
                "table": "live_log_connections",
                "columns": "project_id, user_id",
                "condition": "status = 'active'"
            },
            {
                "name": "idx_unread_alerts",
                "table": "alerts",
                "columns": "user_id, created_at DESC",
                "condition": "is_read = false"
            },
            {
                "name": "idx_active_api_keys",
                "table": "api_keys",
                "columns": "user_id, created_at",
                "condition": "is_active = true"
            },
            {
                "name": "idx_failed_uploads",
                "table": "log_files",
                "columns": "user_id, created_at",
                "condition": "upload_status = 'failed'"
            }
        ]
        
        created_count = 0
        for index in partial_indexes:
            try:
                sql = f"""
                CREATE INDEX CONCURRENTLY {index['name']} 
                ON {index['table']} 
                USING btree ({index['columns']})
                WHERE {index['condition']}
                """
                
                async with self.engine.connect() as conn:
                    await conn.execute(text(sql))
                    await conn.commit()
                
                created_count += 1
                logger.info(f"Created partial index: {index['name']}")
            except Exception as e:
                logger.error(f"Failed to create partial index {index['name']}: {e}")
        
        logger.info(f"Created {created_count} partial indexes successfully")
        return created_count
    
    async def create_timescale_hypertables(self):
        """Create TimescaleDB hypertables for time-series data"""
        try:
            async with self.engine.connect() as conn:
                # Create hypertable for log_entries
                await conn.execute(text("""
                    SELECT create_hypertable('log_entries', 'timestamp', 
                        chunk_time_interval => INTERVAL '1 day',
                        if_not_exists => TRUE)
                """))
                
                # Create hypertable for audit_logs
                await conn.execute(text("""
                    SELECT create_hypertable('audit_logs', 'created_at',
                        chunk_time_interval => INTERVAL '1 day',
                        if_not_exists => TRUE)
                """))
                
                # Create hypertable for usage_tracking
                await conn.execute(text("""
                    SELECT create_hypertable('usage_tracking', 'date',
                        chunk_time_interval => INTERVAL '1 day',
                        if_not_exists => TRUE)
                """))
                
                await conn.commit()
                logger.info("TimescaleDB hypertables created successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to create TimescaleDB hypertables: {e}")
            return False
    
    async def create_continuous_aggregates(self):
        """Create continuous aggregates for analytics"""
        try:
            async with self.engine.connect() as conn:
                # Logs per hour
                await conn.execute(text("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS logs_per_hour
                    WITH (timescaledb.continuous) AS
                    SELECT 
                        time_bucket('1 hour', timestamp) as hour,
                        project_id,
                        log_level,
                        count(*) as log_count
                    FROM log_entries
                    GROUP BY hour, project_id, log_level
                """))
                
                # Error rates per day
                await conn.execute(text("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS error_rates_per_day
                    WITH (timescaledb.continuous) AS
                    SELECT 
                        time_bucket('1 day', timestamp) as day,
                        project_id,
                        count(*) as total_logs,
                        count(*) FILTER (WHERE log_level = 'ERROR') as error_count,
                        (count(*) FILTER (WHERE log_level = 'ERROR')::float / count(*)) * 100 as error_rate
                    FROM log_entries
                    GROUP BY day, project_id
                """))
                
                # Top errors per hour
                await conn.execute(text("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS top_errors_per_hour
                    WITH (timescaledb.continuous) AS
                    SELECT 
                        time_bucket('1 hour', timestamp) as hour,
                        project_id,
                        message,
                        count(*) as error_count
                    FROM log_entries
                    WHERE log_level = 'ERROR'
                    GROUP BY hour, project_id, message
                    ORDER BY error_count DESC
                """))
                
                await conn.commit()
                logger.info("Continuous aggregates created successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to create continuous aggregates: {e}")
            return False
    
    async def setup_data_retention_policies(self):
        """Setup data retention policies"""
        try:
            async with self.engine.connect() as conn:
                # Log entries retention (90 days)
                await conn.execute(text("""
                    SELECT add_retention_policy('log_entries', INTERVAL '90 days', if_not_exists => TRUE)
                """))
                
                # Audit logs retention (7 years)
                await conn.execute(text("""
                    SELECT add_retention_policy('audit_logs', INTERVAL '7 years', if_not_exists => TRUE)
                """))
                
                # Usage tracking retention (1 year)
                await conn.execute(text("""
                    SELECT add_retention_policy('usage_tracking', INTERVAL '1 year', if_not_exists => TRUE)
                """))
                
                await conn.commit()
                logger.info("Data retention policies created successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to create data retention policies: {e}")
            return False
    
    async def run_all_migrations(self):
        """Run all database migrations and optimizations"""
        logger.info("Starting database migrations...")
        
        # Create regular indexes
        await self.create_indexes()
        
        # Create partial indexes
        await self.create_partial_indexes()
        
        # Create TimescaleDB hypertables (if TimescaleDB is available)
        try:
            await self.create_timescale_hypertables()
        except Exception as e:
            logger.warning(f"TimescaleDB not available: {e}")
        
        # Create continuous aggregates
        try:
            await self.create_continuous_aggregates()
        except Exception as e:
            logger.warning(f"Continuous aggregates not available: {e}")
        
        # Setup data retention policies
        try:
            await self.setup_data_retention_policies()
        except Exception as e:
            logger.warning(f"Data retention policies not available: {e}")
        
        logger.info("Database migrations completed successfully")
