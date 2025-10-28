#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import get_db
from app.models.project import Project
from app.models.user import User
from app.services.auth.jwt_handler import get_current_user
from sqlalchemy import select
from datetime import datetime
import uuid

async def test_api_endpoint():
    """Test the API endpoint logic"""
    print("Testing API endpoint logic...")
    
    # Simulate the project creation logic
    async for db in get_db():
        try:
            # Get user (simulate authentication)
            result = await db.execute(
                select(User).where(User.email == "rashandissanayaka@gmail.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("User not found")
                return
                
            print(f"User found: {user.email} (ID: {user.id})")
            
            # Simulate project creation request
            project_data = {
                "name": "API Test Project",
                "description": "Testing API endpoint"
            }
            
            print(f"Creating project: {project_data['name']}")
            
            # Create project (same logic as API endpoint)
            new_project = Project(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name=project_data["name"],
                description=project_data["description"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            print("Adding project to database...")
            db.add(new_project)
            
            print("Committing...")
            await db.commit()
            
            print("Refreshing...")
            await db.refresh(new_project)
            
            print(f"Project created: {new_project.id}")
            
            # Return the same format as API
            result = {
                "id": new_project.id,
                "name": new_project.name,
                "description": new_project.description,
                "created_at": new_project.created_at.isoformat(),
                "updated_at": new_project.updated_at.isoformat() if new_project.updated_at else None
            }
            
            print(f"API Response: {result}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        break

if __name__ == "__main__":
    asyncio.run(test_api_endpoint())
