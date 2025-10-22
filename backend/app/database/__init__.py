"""
Database package initialization
Import all database modules and provide unified interface
"""

from .database import (
    engine, AsyncSessionLocal, get_db, get_db_transaction, execute_with_retry,
    init_db, close_db, test_db_connection, test_connection,
    get_database_health, optimize_database, get_table_sizes, get_index_usage,
    cleanup_old_data, query_monitor, db_config
)
from .migrations import DatabaseMigration
from .queries import OptimizedQueries
from .cache import DatabaseCache, db_cache
from .bulk_ops import BulkOperations
from .monitor import DatabaseMonitor
from .backup import DatabaseBackup

__all__ = [
    # Core database functions
    "engine", "AsyncSessionLocal", "get_db", "get_db_transaction", "execute_with_retry",
    "init_db", "close_db", "test_db_connection", "test_connection",
    "get_database_health", "optimize_database", "get_table_sizes", "get_index_usage",
    "cleanup_old_data", "query_monitor", "db_config",
    
    # Database classes
    "DatabaseMigration", "OptimizedQueries", "DatabaseCache", "db_cache",
    "BulkOperations", "DatabaseMonitor", "DatabaseBackup"
]
