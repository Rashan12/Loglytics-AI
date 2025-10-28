#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import get_db
from app.models.project import Project
from app.models.user import User
from sqlalchemy import select
from datetime import datetime
import uuid

async def test_project_creation():
    """Test project creation"""
    print("Testing project creation...")
    
    async for db in get_db():
        try:
            # Check if user exists
            result = await db.execute(
                select(User).where(User.email == "rashandissanayaka@gmail.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("User not found")
                return
                
            print(f"User found: {user.email}")
            
            # Try to create a project
            new_project = Project(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name="Test Project",
                description="Testing project creation",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            print("Adding project to database...")
            db.add(new_project)
            
            print("Committing to database...")
            await db.commit()
            
            print("Refreshing project...")
            await db.refresh(new_project)
            
            print(f"Project created successfully: {new_project.id}")
            print(f"   Name: {new_project.name}")
            print(f"   Created: {new_project.created_at}")
            print(f"   Updated: {new_project.updated_at}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        break

if __name__ == "__main__":
    asyncio.run(test_project_creation())
