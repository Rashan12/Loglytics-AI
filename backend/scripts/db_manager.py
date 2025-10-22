#!/usr/bin/env python3
"""
Database Management CLI
Command-line interface for database operations
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import (
    DatabaseMigration, DatabaseMonitor, DatabaseBackup,
    get_database_health, optimize_database, cleanup_old_data,
    test_db_connection, init_db
)
from app.config import settings

class DatabaseManager:
    """Database management CLI"""
    
    def __init__(self):
        self.engine = None
        self.migration = None
        self.monitor = None
        self.backup = None
    
    async def initialize(self):
        """Initialize database components"""
        from app.database import engine
        self.engine = engine
        self.migration = DatabaseMigration(engine)
        self.monitor = DatabaseMonitor(engine)
        self.backup = DatabaseBackup(settings.DATABASE_URL)
    
    async def create_indexes(self):
        """Create all database indexes"""
        print("Creating database indexes...")
        try:
            count = await self.migration.create_indexes()
            print(f"✅ Created {count} indexes successfully")
            
            count = await self.migration.create_partial_indexes()
            print(f"✅ Created {count} partial indexes successfully")
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
            return False
        
        return True
    
    async def run_migrations(self):
        """Run all database migrations"""
        print("Running database migrations...")
        try:
            await self.migration.run_all_migrations()
            print("✅ All migrations completed successfully")
        except Exception as e:
            print(f"❌ Error running migrations: {e}")
            return False
        
        return True
    
    async def check_health(self):
        """Check database health"""
        print("Checking database health...")
        try:
            health = await get_database_health()
            
            if health["status"] == "healthy":
                print("✅ Database is healthy")
                print(f"   Version: {health.get('version', 'Unknown')}")
                print(f"   Database size: {health.get('database_size', 'Unknown')}")
                print(f"   Active connections: {health.get('active_connections', 'Unknown')}")
                
                pool_status = health.get("pool_status", {})
                print(f"   Pool size: {pool_status.get('pool_size', 'Unknown')}")
                print(f"   Checked out: {pool_status.get('checked_out', 'Unknown')}")
                
            else:
                print(f"❌ Database is unhealthy: {health.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking database health: {e}")
            return False
        
        return True
    
    async def optimize_database(self):
        """Optimize database performance"""
        print("Optimizing database...")
        try:
            result = await optimize_database()
            if result:
                print("✅ Database optimization completed")
            else:
                print("❌ Database optimization failed")
                return False
        except Exception as e:
            print(f"❌ Error optimizing database: {e}")
            return False
        
        return True
    
    async def cleanup_data(self):
        """Clean up old data"""
        print("Cleaning up old data...")
        try:
            result = await cleanup_old_data()
            print(f"✅ Data cleanup completed: {result}")
        except Exception as e:
            print(f"❌ Error cleaning up data: {e}")
            return False
        
        return True
    
    async def create_backup(self, backup_type="full", name=None):
        """Create database backup"""
        print(f"Creating {backup_type} backup...")
        try:
            result = await self.backup.create_backup(backup_type, name)
            
            if result["status"] == "completed":
                print(f"✅ Backup created successfully: {result['backup_name']}")
                print(f"   File: {result['backup_file']}")
                print(f"   Size: {result['backup_size']} bytes")
            else:
                print(f"❌ Backup failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
        
        return True
    
    async def list_backups(self):
        """List all backups"""
        print("Listing backups...")
        try:
            backups = await self.backup.list_backups()
            
            if not backups:
                print("No backups found")
                return True
            
            print(f"Found {len(backups)} backups:")
            for backup in backups:
                print(f"  {backup['backup_name']} - {backup['created_at']} - {backup['backup_size']} bytes")
                
        except Exception as e:
            print(f"❌ Error listing backups: {e}")
            return False
        
        return True
    
    async def restore_backup(self, backup_name, target_db=None):
        """Restore database from backup"""
        print(f"Restoring backup: {backup_name}")
        try:
            result = await self.backup.restore_backup(backup_name, target_db)
            
            if result["status"] == "completed":
                print(f"✅ Backup restored successfully to {result['target_database']}")
            else:
                print(f"❌ Restore failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            return False
        
        return True
    
    async def monitor_database(self, duration=60):
        """Monitor database for specified duration"""
        print(f"Monitoring database for {duration} seconds...")
        try:
            # Start monitoring
            monitor_task = asyncio.create_task(
                self.monitor.start_monitoring(interval_seconds=10)
            )
            
            # Wait for specified duration
            await asyncio.sleep(duration)
            
            # Stop monitoring
            self.monitor.stop_monitoring()
            monitor_task.cancel()
            
            print("✅ Monitoring completed")
            
        except Exception as e:
            print(f"❌ Error monitoring database: {e}")
            return False
        
        return True
    
    async def get_recommendations(self):
        """Get database optimization recommendations"""
        print("Getting optimization recommendations...")
        try:
            recommendations = await self.monitor.get_recommendations()
            
            if not recommendations:
                print("No recommendations available")
                return True
            
            print(f"Found {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec['title']} ({rec['priority']} priority)")
                print(f"     {rec['description']}")
                print(f"     Action: {rec['action']}")
                print(f"     Impact: {rec['impact']}")
                print()
                
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}")
            return False
        
        return True

async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Database Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check command
    subparsers.add_parser("health", help="Check database health")
    
    # Migration commands
    subparsers.add_parser("migrate", help="Run database migrations")
    subparsers.add_parser("indexes", help="Create database indexes")
    
    # Optimization commands
    subparsers.add_parser("optimize", help="Optimize database performance")
    subparsers.add_parser("cleanup", help="Clean up old data")
    subparsers.add_parser("recommendations", help="Get optimization recommendations")
    
    # Backup commands
    backup_parser = subparsers.add_parser("backup", help="Create database backup")
    backup_parser.add_argument("--type", choices=["full", "incremental", "schema_only"], 
                              default="full", help="Backup type")
    backup_parser.add_argument("--name", help="Custom backup name")
    
    subparsers.add_parser("list-backups", help="List all backups")
    
    restore_parser = subparsers.add_parser("restore", help="Restore database from backup")
    restore_parser.add_argument("backup_name", help="Name of backup to restore")
    restore_parser.add_argument("--target-db", help="Target database name")
    
    # Monitoring commands
    monitor_parser = subparsers.add_parser("monitor", help="Monitor database performance")
    monitor_parser.add_argument("--duration", type=int, default=60, 
                               help="Monitoring duration in seconds")
    
    # Test connection command
    subparsers.add_parser("test", help="Test database connection")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database manager
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    # Execute command
    success = False
    
    if args.command == "health":
        success = await db_manager.check_health()
    elif args.command == "migrate":
        success = await db_manager.run_migrations()
    elif args.command == "indexes":
        success = await db_manager.create_indexes()
    elif args.command == "optimize":
        success = await db_manager.optimize_database()
    elif args.command == "cleanup":
        success = await db_manager.cleanup_data()
    elif args.command == "recommendations":
        success = await db_manager.get_recommendations()
    elif args.command == "backup":
        success = await db_manager.create_backup(args.type, args.name)
    elif args.command == "list-backups":
        success = await db_manager.list_backups()
    elif args.command == "restore":
        success = await db_manager.restore_backup(args.backup_name, args.target_db)
    elif args.command == "monitor":
        success = await db_manager.monitor_database(args.duration)
    elif args.command == "test":
        success = await test_db_connection()
    
    if success:
        print("✅ Command completed successfully")
        sys.exit(0)
    else:
        print("❌ Command failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
