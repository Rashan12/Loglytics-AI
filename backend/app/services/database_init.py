"""
Database initialization - fix issues with existing indexes
"""
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def alter_log_files_schema(db):
    """Alter log_files and log_entries tables to make project_id nullable"""
    try:
        # Use raw SQL to alter the columns
        await db.execute(
            text("ALTER TABLE log_files ALTER COLUMN project_id DROP NOT NULL;")
        )
        logger.info("✅ Altered log_files.project_id to nullable")
        
        # Also make log_entries.project_id nullable
        await db.execute(
            text("ALTER TABLE log_entries ALTER COLUMN project_id DROP NOT NULL;")
        )
        logger.info("✅ Altered log_entries.project_id to nullable")
    except Exception as e:
        logger.warning(f"Could not alter project_id columns: {e}")

async def fix_database_indexes(db):
    """Remove problematic indexes that cause size errors"""
    try:
        # Drop the ix_rag_vectors_embedding index if it exists and is causing issues
        # This index is too large for btree and causes ProgramLimitExceededError
        await db.execute(text("DROP INDEX IF EXISTS ix_rag_vectors_embedding"))
        
        # Also drop any IVFFlat index that might exist
        await db.execute(text("DROP INDEX IF EXISTS rag_vectors_embedding_idx"))
        
        await db.commit()
        logger.info("✅ Fixed database indexes - removed problematic embedding index")
    except Exception as e:
        logger.warning(f"Could not drop embedding index (might not exist): {e}")
        await db.rollback()

