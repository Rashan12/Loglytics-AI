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

async def debug_endpoint():
    """Debug the endpoint logic"""
    print("Debugging endpoint logic...")
    
    # Test JWT token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiODEwOGFmZi02MDIyLTQxYTEtOTg0ZS05ODEzMTUxN2ZlMTQiLCJlbWFpbCI6InJhc2hhbmRpc3NhbmF5YWthQGdtYWlsLmNvbSIsImV4cCI6MTc2MTMwNDcyNywiaWF0IjoxNzYxMzAyOTI3fQ.vO5DtSaWuPLxmbRhlB7sBPQRerW_7uzsqJNwvYf32BE"
    
    try:
        # Test JWT decoding
        from jose import jwt
        from app.config import settings
        
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        print(f"JWT decoded successfully. User ID: {user_id}")
        
        # Test database connection
        async for db in get_db():
            try:
                # Get user from database
                result = await db.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    print("User not found in database")
                    return
                    
                print(f"User found: {user.email}")
                
                # Test project creation
                project_data = {
                    "name": "Debug Test Project",
                    "description": "Testing debug endpoint"
                }
                
                new_project = Project(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    name=project_data["name"],
                    description=project_data["description"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                print("Adding project...")
                db.add(new_project)
                
                print("Committing...")
                await db.commit()
                
                print("Refreshing...")
                await db.refresh(new_project)
                
                print(f"Project created: {new_project.id}")
                
            except Exception as e:
                print(f"Database error: {e}")
                import traceback
                traceback.print_exc()
            break
            
    except Exception as e:
        print(f"JWT error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_endpoint())
