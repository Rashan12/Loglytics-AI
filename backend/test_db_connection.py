"""
Test PostgreSQL Database Connection
Run this script to verify your database connection is working correctly
"""

import asyncio
import sys
import os
from pathlib import Path

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import test_connection, test_db_connection
from app.config import settings


async def main():
    """Main test function"""
    print("=" * 60)
    print("PostgreSQL Connection Test")
    print("=" * 60)

    # Display current configuration
    print("\n📋 Current Configuration:")
    print(f"  Database: {settings.POSTGRES_DB}")
    print(f"  Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print(f"  User: {settings.POSTGRES_USER}")
    print(f"  Password: {'*' * len(settings.POSTGRES_PASSWORD)}")
    print(f"\n  Connection URL: postgresql+asyncpg://{settings.POSTGRES_USER}:{'*' * len(settings.POSTGRES_PASSWORD)}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")

    print("\n" + "=" * 60)
    print("Testing Database Connection...")
    print("=" * 60 + "\n")

    # Test the connection
    success = await test_connection()

    print("\n" + "=" * 60)
    if success:
        print("✅ Database connection test PASSED!")
        print("\nYour PostgreSQL database is configured correctly.")
        print("You can now run the application with:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
    else:
        print("❌ Database connection test FAILED!")
        print("\n⚠️  Troubleshooting Steps:")
        print("  1. Verify PostgreSQL is running:")
        print("     - Windows: Check Services for 'postgresql' service")
        print("     - Run: pg_ctl status")
        print("\n  2. Verify your credentials in backend/.env file:")
        print("     - POSTGRES_PASSWORD=Rashan12")
        print("     - POSTGRES_USER=postgres")
        print("     - POSTGRES_DB=loglytics_ai")
        print("\n  3. Reset PostgreSQL password if needed:")
        print("     - Open psql as postgres user")
        print("     - Run: ALTER USER postgres PASSWORD 'Rashan12';")
        print("\n  4. Check if the database exists:")
        print("     - Run: psql -U postgres -l")
        print("     - Create if missing: CREATE DATABASE loglytics_ai;")
        print("\n  5. Verify PostgreSQL is listening on localhost:5432")
        print("     - Check pg_hba.conf for proper authentication settings")

    print("=" * 60)

    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
