"""
Reset Database Script
Drops all tables and recreates them with the updated schema
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import engine, Base
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def drop_all_tables():
    """Drop all tables in the database"""
    try:
        async with engine.begin() as conn:
            logger.info("Dropping all tables...")

            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)

            logger.info("All tables dropped successfully")
            return True
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        return False


async def create_all_tables():
    """Create all tables in the database"""
    try:
        # Import all models to ensure they are registered
        from app.models import (
            User, Project, Chat, Message, LogFile, LogEntry,
            RAGVector, AnalyticsCache, LiveLogConnection, Alert,
            APIKey, AuditLog, ProjectShare, Webhook, UsageTracking
        )

        async with engine.begin() as conn:
            logger.info("Creating all tables...")

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)

            logger.info("All tables created successfully")
            return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False


async def verify_tables():
    """Verify that tables were created correctly"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))

            tables = [row[0] for row in result]

            logger.info(f"\nTables in database: {len(tables)}")
            for table in tables:
                logger.info(f"  - {table}")

            return True
    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
        return False


async def main():
    """Main reset function"""
    print("=" * 60)
    print("PostgreSQL Database Reset")
    print("=" * 60)

    print(f"\nDatabase: {settings.POSTGRES_DB}")
    print(f"Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print(f"User: {settings.POSTGRES_USER}")

    print("\n" + "=" * 60)
    print("WARNING: This will DELETE ALL DATA in the database!")
    print("=" * 60)

    confirm = input("\nAre you sure you want to continue? (yes/no): ")

    if confirm.lower() != 'yes':
        print("\nDatabase reset cancelled.")
        return False

    print("\n" + "=" * 60)
    print("Step 1: Dropping all tables...")
    print("=" * 60)

    if not await drop_all_tables():
        print("\nFailed to drop tables!")
        return False

    print("\n" + "=" * 60)
    print("Step 2: Creating all tables...")
    print("=" * 60)

    if not await create_all_tables():
        print("\nFailed to create tables!")
        return False

    print("\n" + "=" * 60)
    print("Step 3: Verifying tables...")
    print("=" * 60)

    await verify_tables()

    print("\n" + "=" * 60)
    print("Database reset completed successfully!")
    print("=" * 60)
    print("\nYou can now run the application with:")
    print("  cd backend")
    print("  uvicorn app.main:app --reload")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nDatabase reset cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
