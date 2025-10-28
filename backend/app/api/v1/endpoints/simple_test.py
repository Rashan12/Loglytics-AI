from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.user import User
from app.services.auth.jwt_handler import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/simple")
async def simple_test():
    """Simple test endpoint"""
    return {"status": "simple test working"}

@router.get("/auth-test")
async def auth_test(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test authentication"""
    return {
        "status": "auth test working",
        "user_id": current_user.id,
        "user_email": current_user.email
    }

@router.post("/create-test")
async def create_test(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test project creation"""
    try:
        from app.models.project import Project
        import uuid
        from datetime import datetime
        
        new_project = Project(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            name="Simple Test Project",
            description="Testing simple endpoint"
        )
        
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        
        return {
            "status": "project created",
            "project_id": new_project.id,
            "project_name": new_project.name
        }
        
    except Exception as e:
        logger.error(f"Create test error: {e}", exc_info=True)
        raise HTTPException(500, str(e))
