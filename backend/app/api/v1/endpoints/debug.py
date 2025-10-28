from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.user import User
from app.services.auth.jwt_handler import get_current_user
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/debug/auth")
async def debug_auth(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Debug authentication"""
    try:
        logger.info(f"Debug auth - User: {current_user.email}")
        return {
            "status": "success",
            "user_id": current_user.id,
            "user_email": current_user.email
        }
    except Exception as e:
        logger.error(f"Debug auth error: {e}", exc_info=True)
        raise HTTPException(500, str(e))

@router.post("/debug/project")
async def debug_project_creation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Debug project creation"""
    try:
        logger.info(f"Debug project creation - User: {current_user.email}")
        
        # Simple project creation test
        from app.models.project import Project
        from datetime import datetime
        import uuid
        
        new_project = Project(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            name="Debug Project",
            description="Testing debug endpoint",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        
        logger.info(f"Debug project created: {new_project.id}")
        
        return {
            "status": "success",
            "project_id": new_project.id,
            "project_name": new_project.name
        }
        
    except Exception as e:
        logger.error(f"Debug project creation error: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(500, str(e))
