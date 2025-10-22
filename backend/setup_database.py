#!/usr/bin/env python3
"""
Database setup script for Loglytics AI
This script sets up the database with all required extensions and initial data
"""

import asyncio
import asyncpg
import os
from pathlib import Path
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_database():
    """Set up the database with all required extensions and initial data"""
    
    # Parse database URL to get connection details
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    
    # Extract connection details
    if "@" in db_url:
        auth_part, host_part = db_url.split("@", 1)
        if ":" in auth_part:
            user, password = auth_part.split(":", 1)
        else:
            user = auth_part
            password = ""
        
        if "/" in host_part:
            host_port, database = host_part.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":", 1)
                port = int(port)
            else:
                host = host_port
                port = 5432
        else:
            host = host_part
            port = 5432
            database = "postgres"
    else:
        raise ValueError("Invalid database URL format")
    
    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    
    try:
        logger.info("Connected to PostgreSQL database")
        
        # Read and execute SQL scripts
        sql_dir = Path(__file__).parent / "sql"
        
        # 1. Enable extensions
        logger.info("Enabling PostgreSQL extensions...")
        with open(sql_dir / "enable_extensions.sql", "r") as f:
            await conn.execute(f.read())
        
        # 2. Create database if it doesn't exist
        logger.info(f"Creating database 'loglytics_db' if it doesn't exist...")
        await conn.execute("""
            SELECT 'CREATE DATABASE loglytics_db'
            WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'loglytics_db')
        """)
        
        # 3. Connect to the new database
        await conn.close()
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="loglytics_db"
        )
        
        # 4. Run the complete setup
        logger.info("Running complete database setup...")
        with open(sql_dir / "setup_database.sql", "r") as f:
            await conn.execute(f.read())
        
        # 5. Set up RLS policies
        logger.info("Setting up Row-Level Security policies...")
        with open(sql_dir / "rls_policies.sql", "r") as f:
            await conn.execute(f.read())
        
        # 6. Create performance indexes
        logger.info("Creating performance indexes...")
        with open(sql_dir / "performance_indexes.sql", "r") as f:
            await conn.execute(f.read())
        
        logger.info("Database setup completed successfully!")
        
        # Verify setup
        logger.info("Verifying database setup...")
        
        # Check extensions
        extensions = await conn.fetch("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname IN ('uuid-ossp', 'vector', 'timescaledb', 'pg_trgm')
        """)
        logger.info(f"Installed extensions: {[ext['extname'] for ext in extensions]}")
        
        # Check tables
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        logger.info(f"Created tables: {[table['tablename'] for table in tables]}")
        
        # Check RLS is enabled
        rls_tables = await conn.fetch("""
            SELECT schemaname, tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' AND rowsecurity = true
        """)
        logger.info(f"Tables with RLS enabled: {[table['tablename'] for table in rls_tables]}")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise
    finally:
        await conn.close()


async def run_migrations():
    """Run Alembic migrations"""
    import subprocess
    import sys
    
    logger.info("Running Alembic migrations...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    try:
        # Run alembic upgrade
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, check=True)
        
        logger.info("Migrations completed successfully")
        logger.info(f"Alembic output: {result.stdout}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        raise


async def main():
    """Main setup function"""
    try:
        # Set up database
        await setup_database()
        
        # Run migrations
        await run_migrations()
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
