"""
Hard reset - Drop entire schema and recreate
"""
import asyncio
from sqlalchemy import text
from app.database import engine

async def hard_reset():
    async with engine.begin() as conn:
        print("Dropping public schema...")
        await conn.execute(text('DROP SCHEMA IF EXISTS public CASCADE;'))
        print("Creating public schema...")
        await conn.execute(text('CREATE SCHEMA public;'))
        print("Schema reset complete!")

asyncio.run(hard_reset())
