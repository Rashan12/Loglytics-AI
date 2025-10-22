"""
Bulk operations for large data imports and updates
Optimized for handling large datasets efficiently
"""

from sqlalchemy import text, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import List, Dict, Any, Optional, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class BulkOperations:
    """Handle bulk database operations efficiently"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.batch_size = 1000  # Process 1000 records at a time
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def bulk_insert_log_entries(
        self, 
        log_entries: List[Dict[str, Any]], 
        batch_size: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        Bulk insert log entries using PostgreSQL COPY or batch insert
        
        Args:
            log_entries: List of log entry dictionaries
            batch_size: Number of records per batch
            
        Returns:
            Tuple of (successful_inserts, failed_inserts)
        """
        batch_size = batch_size or self.batch_size
        successful = 0
        failed = 0
        
        try:
            # Process in batches
            for i in range(0, len(log_entries), batch_size):
                batch = log_entries[i:i + batch_size]
                
                try:
                    # Use PostgreSQL COPY for maximum performance
                    await self._bulk_insert_with_copy(batch)
                    successful += len(batch)
                    logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
                    
                except Exception as e:
                    logger.error(f"Error inserting batch {i//batch_size + 1}: {e}")
                    # Fallback to individual inserts
                    for entry in batch:
                        try:
                            await self._insert_single_log_entry(entry)
                            successful += 1
                        except Exception as entry_error:
                            logger.error(f"Error inserting log entry: {entry_error}")
                            failed += 1
                
                # Small delay to prevent overwhelming the database
                await asyncio.sleep(0.01)
            
            logger.info(f"Bulk insert completed: {successful} successful, {failed} failed")
            return successful, failed
            
        except Exception as e:
            logger.error(f"Error in bulk insert log entries: {e}")
            return successful, failed
    
    async def _bulk_insert_with_copy(self, log_entries: List[Dict[str, Any]]):
        """Use PostgreSQL COPY for bulk insert"""
        try:
            # Prepare data for COPY
            copy_data = []
            for entry in log_entries:
                copy_data.append((
                    entry.get('id'),
                    entry.get('user_id'),
                    entry.get('project_id'),
                    entry.get('log_file_id'),
                    entry.get('timestamp'),
                    entry.get('log_level'),
                    entry.get('message'),
                    entry.get('source'),
                    json.dumps(entry.get('metadata', {})) if entry.get('metadata') else None
                ))
            
            # Use COPY FROM for maximum performance
            copy_sql = """
                COPY log_entries (id, user_id, project_id, log_file_id, timestamp, log_level, message, source, metadata)
                FROM STDIN WITH (FORMAT csv, HEADER false)
            """
            
            # Convert to CSV format
            csv_data = '\n'.join([
                ','.join([
                    f'"{str(value)}"' if value is not None else 'NULL'
                    for value in row
                ])
                for row in copy_data
            ])
            
            await self.session.execute(text(copy_sql), {"data": csv_data})
            await self.session.commit()
            
        except Exception as e:
            # Fallback to batch insert if COPY fails
            logger.warning(f"COPY failed, falling back to batch insert: {e}")
            await self._bulk_insert_with_batch(log_entries)
    
    async def _bulk_insert_with_batch(self, log_entries: List[Dict[str, Any]]):
        """Fallback batch insert method"""
        from app.models import LogEntry
        
        # Prepare data for batch insert
        insert_data = []
        for entry in log_entries:
            insert_data.append({
                'id': entry.get('id'),
                'user_id': entry.get('user_id'),
                'project_id': entry.get('project_id'),
                'log_file_id': entry.get('log_file_id'),
                'timestamp': entry.get('timestamp'),
                'log_level': entry.get('log_level'),
                'message': entry.get('message'),
                'source': entry.get('source'),
                'metadata': entry.get('metadata', {})
            })
        
        # Use bulk insert
        await self.session.execute(
            insert(LogEntry),
            insert_data
        )
        await self.session.commit()
    
    async def _insert_single_log_entry(self, entry: Dict[str, Any]):
        """Insert a single log entry (fallback method)"""
        from app.models import LogEntry
        
        log_entry = LogEntry(
            id=entry.get('id'),
            user_id=entry.get('user_id'),
            project_id=entry.get('project_id'),
            log_file_id=entry.get('log_file_id'),
            timestamp=entry.get('timestamp'),
            log_level=entry.get('log_level'),
            message=entry.get('message'),
            source=entry.get('source'),
            metadata=entry.get('metadata', {})
        )
        
        self.session.add(log_entry)
        await self.session.commit()
    
    async def bulk_insert_rag_vectors(
        self, 
        vectors: List[Dict[str, Any]], 
        batch_size: Optional[int] = None
    ) -> Tuple[int, int]:
        """Bulk insert RAG vectors"""
        batch_size = batch_size or self.batch_size
        successful = 0
        failed = 0
        
        try:
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                
                try:
                    await self._bulk_insert_vectors_batch(batch)
                    successful += len(batch)
                    logger.info(f"Inserted vector batch {i//batch_size + 1}: {len(batch)} records")
                    
                except Exception as e:
                    logger.error(f"Error inserting vector batch {i//batch_size + 1}: {e}")
                    failed += len(batch)
                
                await asyncio.sleep(0.01)
            
            return successful, failed
            
        except Exception as e:
            logger.error(f"Error in bulk insert RAG vectors: {e}")
            return successful, failed
    
    async def _bulk_insert_vectors_batch(self, vectors: List[Dict[str, Any]]):
        """Insert a batch of RAG vectors"""
        from app.models import RAGVector
        
        insert_data = []
        for vector in vectors:
            insert_data.append({
                'id': vector.get('id'),
                'project_id': vector.get('project_id'),
                'user_id': vector.get('user_id'),
                'content': vector.get('content'),
                'embedding': vector.get('embedding'),
                'metadata': vector.get('metadata', {})
            })
        
        await self.session.execute(
            insert(RAGVector),
            insert_data
        )
        await self.session.commit()
    
    async def bulk_update_log_entries(
        self, 
        updates: List[Dict[str, Any]], 
        batch_size: Optional[int] = None
    ) -> Tuple[int, int]:
        """Bulk update log entries"""
        batch_size = batch_size or self.batch_size
        successful = 0
        failed = 0
        
        try:
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                
                try:
                    await self._bulk_update_batch(batch)
                    successful += len(batch)
                    logger.info(f"Updated batch {i//batch_size + 1}: {len(batch)} records")
                    
                except Exception as e:
                    logger.error(f"Error updating batch {i//batch_size + 1}: {e}")
                    failed += len(batch)
                
                await asyncio.sleep(0.01)
            
            return successful, failed
            
        except Exception as e:
            logger.error(f"Error in bulk update log entries: {e}")
            return successful, failed
    
    async def _bulk_update_batch(self, updates: List[Dict[str, Any]]):
        """Update a batch of records"""
        from app.models import LogEntry
        
        for update_data in updates:
            entry_id = update_data.pop('id')
            await self.session.execute(
                update(LogEntry)
                .where(LogEntry.id == entry_id)
                .values(**update_data)
            )
        
        await self.session.commit()
    
    async def bulk_delete_log_entries(
        self, 
        entry_ids: List[str], 
        batch_size: Optional[int] = None
    ) -> int:
        """Bulk delete log entries"""
        batch_size = batch_size or self.batch_size
        deleted = 0
        
        try:
            for i in range(0, len(entry_ids), batch_size):
                batch = entry_ids[i:i + batch_size]
                
                try:
                    from app.models import LogEntry
                    
                    result = await self.session.execute(
                        delete(LogEntry)
                        .where(LogEntry.id.in_(batch))
                    )
                    
                    deleted += result.rowcount
                    await self.session.commit()
                    
                    logger.info(f"Deleted batch {i//batch_size + 1}: {result.rowcount} records")
                    
                except Exception as e:
                    logger.error(f"Error deleting batch {i//batch_size + 1}: {e}")
                
                await asyncio.sleep(0.01)
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error in bulk delete log entries: {e}")
            return deleted
    
    async def bulk_upsert_usage_tracking(
        self, 
        usage_data: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """Bulk upsert usage tracking data"""
        successful = 0
        failed = 0
        
        try:
            from app.models import UsageTracking
            
            # Use PostgreSQL UPSERT (ON CONFLICT)
            for data in usage_data:
                try:
                    await self.session.execute(
                        pg_insert(UsageTracking)
                        .values(**data)
                        .on_conflict_do_update(
                            index_elements=['user_id', 'date'],
                            set_={
                                'api_calls': data['api_calls'],
                                'llm_tokens': data['llm_tokens'],
                                'storage_used': data['storage_used'],
                                'updated_at': datetime.utcnow()
                            }
                        )
                    )
                    successful += 1
                    
                except Exception as e:
                    logger.error(f"Error upserting usage tracking: {e}")
                    failed += 1
            
            await self.session.commit()
            return successful, failed
            
        except Exception as e:
            logger.error(f"Error in bulk upsert usage tracking: {e}")
            return successful, failed
    
    async def bulk_insert_audit_logs(
        self, 
        audit_logs: List[Dict[str, Any]], 
        batch_size: Optional[int] = None
    ) -> Tuple[int, int]:
        """Bulk insert audit logs"""
        batch_size = batch_size or self.batch_size
        successful = 0
        failed = 0
        
        try:
            for i in range(0, len(audit_logs), batch_size):
                batch = audit_logs[i:i + batch_size]
                
                try:
                    from app.models import AuditLog
                    
                    insert_data = []
                    for log in batch:
                        insert_data.append({
                            'id': log.get('id'),
                            'user_id': log.get('user_id'),
                            'action': log.get('action'),
                            'resource_type': log.get('resource_type'),
                            'resource_id': log.get('resource_id'),
                            'ip_address': log.get('ip_address'),
                            'user_agent': log.get('user_agent'),
                            'path': log.get('path'),
                            'method': log.get('method'),
                            'status_code': log.get('status_code'),
                            'query_params': log.get('query_params', {}),
                            'metadata': log.get('metadata', {}),
                            'created_at': log.get('created_at', datetime.utcnow())
                        })
                    
                    await self.session.execute(
                        insert(AuditLog),
                        insert_data
                    )
                    await self.session.commit()
                    
                    successful += len(batch)
                    logger.info(f"Inserted audit log batch {i//batch_size + 1}: {len(batch)} records")
                    
                except Exception as e:
                    logger.error(f"Error inserting audit log batch {i//batch_size + 1}: {e}")
                    failed += len(batch)
                
                await asyncio.sleep(0.01)
            
            return successful, failed
            
        except Exception as e:
            logger.error(f"Error in bulk insert audit logs: {e}")
            return successful, failed
    
    async def bulk_update_project_shares(
        self, 
        project_id: str, 
        share_updates: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """Bulk update project shares"""
        successful = 0
        failed = 0
        
        try:
            from app.models import ProjectShare
            
            for update_data in share_updates:
                try:
                    share_id = update_data.pop('id')
                    await self.session.execute(
                        update(ProjectShare)
                        .where(
                            ProjectShare.id == share_id,
                            ProjectShare.project_id == project_id
                        )
                        .values(**update_data)
                    )
                    successful += 1
                    
                except Exception as e:
                    logger.error(f"Error updating project share: {e}")
                    failed += 1
            
            await self.session.commit()
            return successful, failed
            
        except Exception as e:
            logger.error(f"Error in bulk update project shares: {e}")
            return successful, failed
    
    async def cleanup_old_data_bulk(
        self, 
        table_name: str, 
        date_column: str, 
        retention_days: int
    ) -> int:
        """Bulk cleanup old data based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Use raw SQL for better performance on large datasets
            delete_sql = f"""
                DELETE FROM {table_name} 
                WHERE {date_column} < :cutoff_date
            """
            
            result = await self.session.execute(
                text(delete_sql),
                {"cutoff_date": cutoff_date}
            )
            
            deleted_count = result.rowcount
            await self.session.commit()
            
            logger.info(f"Cleaned up {deleted_count} old records from {table_name}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data from {table_name}: {e}")
            return 0
    
    async def get_bulk_operation_stats(self) -> Dict[str, Any]:
        """Get statistics about bulk operations"""
        try:
            # Get table sizes
            table_sizes = await self.session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """))
            
            # Get row counts for main tables
            row_counts = {}
            main_tables = ['log_entries', 'audit_logs', 'rag_vectors', 'usage_tracking']
            
            for table in main_tables:
                try:
                    result = await self.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    row_counts[table] = result.scalar()
                except Exception:
                    row_counts[table] = 0
            
            return {
                "table_sizes": [dict(row) for row in table_sizes],
                "row_counts": row_counts,
                "batch_size": self.batch_size,
                "max_retries": self.max_retries
            }
            
        except Exception as e:
            logger.error(f"Error getting bulk operation stats: {e}")
            return {}
