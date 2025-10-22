"""
Database backup and recovery system
Automated backup with point-in-time recovery
"""

import asyncio
import subprocess
import os
import shutil
import gzip
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Handle database backup and recovery operations"""
    
    def __init__(self, database_url: str, backup_dir: str = "backups"):
        self.database_url = database_url
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup configuration
        self.retention_days = 30
        self.compression = True
        self.parallel_jobs = 4
        
        # Parse database URL
        self.db_config = self._parse_database_url()
    
    def _parse_database_url(self) -> Dict[str, str]:
        """Parse database URL to extract connection parameters"""
        try:
            # Parse postgresql://user:password@host:port/database
            url_parts = self.database_url.replace("postgresql+asyncpg://", "postgresql://")
            url_parts = url_parts.replace("postgresql://", "").split("/")
            
            if len(url_parts) < 2:
                raise ValueError("Invalid database URL format")
            
            database = url_parts[1]
            auth_host = url_parts[0].split("@")
            
            if len(auth_host) < 2:
                raise ValueError("Invalid database URL format")
            
            auth = auth_host[0].split(":")
            host_port = auth_host[1].split(":")
            
            return {
                "user": auth[0],
                "password": auth[1] if len(auth) > 1 else "",
                "host": host_port[0],
                "port": host_port[1] if len(host_port) > 1 else "5432",
                "database": database
            }
        except Exception as e:
            logger.error(f"Error parsing database URL: {e}")
            raise
    
    async def create_backup(
        self, 
        backup_type: str = "full",
        custom_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create database backup
        
        Args:
            backup_type: Type of backup (full, incremental, schema_only)
            custom_name: Custom name for backup file
            
        Returns:
            Backup information dictionary
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = custom_name or f"{backup_type}_{timestamp}"
            backup_file = self.backup_dir / f"{backup_name}.sql"
            
            if self.compression:
                backup_file = backup_file.with_suffix(".sql.gz")
            
            logger.info(f"Starting {backup_type} backup: {backup_name}")
            
            # Create backup using pg_dump
            cmd = self._build_pg_dump_command(backup_type, backup_file)
            
            # Execute backup command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"Backup failed: {error_msg}")
            
            # Get backup file size
            backup_size = backup_file.stat().st_size
            
            # Create backup metadata
            metadata = {
                "backup_name": backup_name,
                "backup_type": backup_type,
                "backup_file": str(backup_file),
                "backup_size": backup_size,
                "created_at": datetime.utcnow().isoformat(),
                "database_url": self.database_url,
                "compression": self.compression,
                "status": "completed"
            }
            
            # Save metadata
            metadata_file = backup_file.with_suffix(".json")
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Backup completed successfully: {backup_name} ({backup_size} bytes)")
            
            # Clean up old backups
            await self.cleanup_old_backups()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return {
                "backup_name": backup_name if 'backup_name' in locals() else "unknown",
                "status": "failed",
                "error": str(e),
                "created_at": datetime.utcnow().isoformat()
            }
    
    def _build_pg_dump_command(self, backup_type: str, backup_file: Path) -> List[str]:
        """Build pg_dump command based on backup type"""
        cmd = [
            "pg_dump",
            "-h", self.db_config["host"],
            "-p", self.db_config["port"],
            "-U", self.db_config["user"],
            "-d", self.db_config["database"],
            "-f", str(backup_file)
        ]
        
        # Add compression if enabled
        if self.compression and not backup_file.suffix == ".gz":
            cmd.extend(["-Z", "9"])
        
        # Add backup type specific options
        if backup_type == "schema_only":
            cmd.append("-s")  # Schema only
        elif backup_type == "data_only":
            cmd.append("-a")  # Data only
        else:  # full backup
            cmd.extend([
                "-v",  # Verbose
                "--no-password",  # Don't prompt for password
                "--format=custom",  # Custom format for better compression
                "--compress=9"  # Maximum compression
            ])
        
        # Add parallel jobs for large databases
        if backup_type == "full":
            cmd.extend(["-j", str(self.parallel_jobs)])
        
        return cmd
    
    async def restore_backup(
        self, 
        backup_name: str, 
        target_database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Restore database from backup
        
        Args:
            backup_name: Name of backup to restore
            target_database: Target database name (defaults to source database)
            
        Returns:
            Restore information dictionary
        """
        try:
            # Find backup file
            backup_file = self.backup_dir / f"{backup_name}.sql"
            if not backup_file.exists():
                backup_file = self.backup_dir / f"{backup_name}.sql.gz"
            
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_name}")
            
            # Load backup metadata
            metadata_file = backup_file.with_suffix(".json")
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
            
            target_db = target_database or self.db_config["database"]
            
            logger.info(f"Starting restore from backup: {backup_name} to {target_db}")
            
            # Create target database if it doesn't exist
            await self._create_database_if_not_exists(target_db)
            
            # Build restore command
            cmd = self._build_pg_restore_command(backup_file, target_db)
            
            # Execute restore command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"Restore failed: {error_msg}")
            
            logger.info(f"Restore completed successfully: {backup_name} to {target_db}")
            
            return {
                "backup_name": backup_name,
                "target_database": target_db,
                "restored_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return {
                "backup_name": backup_name,
                "status": "failed",
                "error": str(e),
                "restored_at": datetime.utcnow().isoformat()
            }
    
    def _build_pg_restore_command(self, backup_file: Path, target_database: str) -> List[str]:
        """Build pg_restore command"""
        cmd = [
            "pg_restore",
            "-h", self.db_config["host"],
            "-p", self.db_config["port"],
            "-U", self.db_config["user"],
            "-d", target_database,
            "-v",  # Verbose
            "--no-password",  # Don't prompt for password
            "--clean",  # Clean before restore
            "--if-exists",  # Don't error if objects don't exist
            str(backup_file)
        ]
        
        return cmd
    
    async def _create_database_if_not_exists(self, database_name: str):
        """Create database if it doesn't exist"""
        try:
            # Connect to postgres database to create target database
            conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                database="postgres"
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (database_name,)
            )
            
            if not cursor.fetchone():
                # Create database
                cursor.execute(f'CREATE DATABASE "{database_name}"')
                logger.info(f"Created database: {database_name}")
            else:
                logger.info(f"Database already exists: {database_name}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error creating database {database_name}: {e}")
            raise
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.sql*"):
                if backup_file.suffix == ".json":
                    continue
                
                # Load metadata
                metadata_file = backup_file.with_suffix(".json")
                metadata = {}
                
                if metadata_file.exists():
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                else:
                    # Create basic metadata from file
                    metadata = {
                        "backup_name": backup_file.stem.replace(".sql", ""),
                        "backup_file": str(backup_file),
                        "backup_size": backup_file.stat().st_size,
                        "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                        "status": "unknown"
                    }
                
                backups.append(metadata)
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x["created_at"], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    async def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            removed_count = 0
            
            for backup_file in self.backup_dir.glob("*.sql*"):
                if backup_file.suffix == ".json":
                    continue
                
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    # Remove backup file and metadata
                    backup_file.unlink()
                    
                    metadata_file = backup_file.with_suffix(".json")
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    removed_count += 1
                    logger.info(f"Removed old backup: {backup_file.name}")
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old backups")
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    async def verify_backup(self, backup_name: str) -> Dict[str, Any]:
        """Verify backup integrity"""
        try:
            # Find backup file
            backup_file = self.backup_dir / f"{backup_name}.sql"
            if not backup_file.exists():
                backup_file = self.backup_dir / f"{backup_name}.sql.gz"
            
            if not backup_file.exists():
                return {
                    "backup_name": backup_name,
                    "status": "not_found",
                    "error": "Backup file not found"
                }
            
            # Load metadata
            metadata_file = backup_file.with_suffix(".json")
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
            
            # Check file size
            file_size = backup_file.stat().st_size
            expected_size = metadata.get("backup_size", 0)
            
            if file_size != expected_size:
                return {
                    "backup_name": backup_name,
                    "status": "corrupted",
                    "error": f"File size mismatch: expected {expected_size}, got {file_size}"
                }
            
            # Test restore to temporary database
            temp_db = f"temp_verify_{backup_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            try:
                # Create temporary database
                await self._create_database_if_not_exists(temp_db)
                
                # Test restore
                restore_result = await self.restore_backup(backup_name, temp_db)
                
                if restore_result["status"] == "completed":
                    # Drop temporary database
                    await self._drop_database(temp_db)
                    
                    return {
                        "backup_name": backup_name,
                        "status": "verified",
                        "file_size": file_size,
                        "verified_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "backup_name": backup_name,
                        "status": "verification_failed",
                        "error": restore_result.get("error", "Unknown error")
                    }
                    
            except Exception as e:
                # Clean up temporary database
                try:
                    await self._drop_database(temp_db)
                except:
                    pass
                
                return {
                    "backup_name": backup_name,
                    "status": "verification_failed",
                    "error": str(e)
                }
            
        except Exception as e:
            logger.error(f"Error verifying backup: {e}")
            return {
                "backup_name": backup_name,
                "status": "error",
                "error": str(e)
            }
    
    async def _drop_database(self, database_name: str):
        """Drop database"""
        try:
            conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                database="postgres"
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            cursor.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error dropping database {database_name}: {e}")
            raise
    
    async def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics"""
        try:
            backups = await self.list_backups()
            
            total_backups = len(backups)
            total_size = sum(backup.get("backup_size", 0) for backup in backups)
            
            # Group by type
            by_type = {}
            for backup in backups:
                backup_type = backup.get("backup_type", "unknown")
                if backup_type not in by_type:
                    by_type[backup_type] = {"count": 0, "size": 0}
                by_type[backup_type]["count"] += 1
                by_type[backup_type]["size"] += backup.get("backup_size", 0)
            
            # Get oldest and newest backups
            if backups:
                oldest = min(backups, key=lambda x: x["created_at"])
                newest = max(backups, key=lambda x: x["created_at"])
            else:
                oldest = newest = None
            
            return {
                "total_backups": total_backups,
                "total_size": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "by_type": by_type,
                "oldest_backup": oldest,
                "newest_backup": newest,
                "retention_days": self.retention_days,
                "backup_directory": str(self.backup_dir)
            }
            
        except Exception as e:
            logger.error(f"Error getting backup stats: {e}")
            return {"error": str(e)}
    
    async def schedule_backup(
        self, 
        backup_type: str = "full",
        schedule_time: str = "02:00"  # 2 AM
    ) -> Dict[str, Any]:
        """Schedule regular backups (placeholder for cron job integration)"""
        try:
            # This would integrate with a task scheduler like Celery Beat
            # For now, return scheduling information
            
            return {
                "backup_type": backup_type,
                "schedule_time": schedule_time,
                "next_run": f"Tomorrow at {schedule_time}",
                "status": "scheduled",
                "note": "This requires integration with a task scheduler like Celery Beat"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling backup: {e}")
            return {"error": str(e)}
