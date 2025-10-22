#!/usr/bin/env python3
"""
Initialize SQLite database for Loglytics AI
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.base import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_sqlite_database():
    """Initialize SQLite database"""
    try:
        logger.info("Initializing SQLite database...")
        
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=True
        )
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully!")
        
        # Close engine
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def main():
    """Main function"""
    try:
        await init_sqlite_database()
        print("Database initialization completed successfully!")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
