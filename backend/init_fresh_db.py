"""
Initialize fresh database - import models and create tables
"""
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import init_db
from sqlalchemy import text
from app.database import engine

async def main():
    print("=" * 60)
    print("Initializing Fresh Database")
    print("=" * 60)

    # Initialize database (creates all tables)
    print("\nCreating tables...")
    await init_db()

    # Verify schema
    print("\nVerifying users table schema...")
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """))
        print("\nUSERS table schema:")
        for row in result:
            col_name, data_type, max_length = row
            if max_length:
                print(f"  {col_name}: {data_type}({max_length})")
            else:
                print(f"  {col_name}: {data_type}")

    print("\n" + "=" * 60)
    print("Database initialized successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
