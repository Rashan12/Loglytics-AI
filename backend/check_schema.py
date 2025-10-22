import asyncio
from sqlalchemy import text
from app.database import engine

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """))
        print("\nUSERS table schema:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")

asyncio.run(check())
