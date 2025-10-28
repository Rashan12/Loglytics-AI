from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.user import User
from app.services.auth.jwt_handler import get_current_user

router = APIRouter()

@router.post("/debug-chat")
async def debug_chat(
    message: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Debug chat endpoint to isolate the 500 error"""
    try:
        print(f"DEBUG: Received message: {message}")
        print(f"DEBUG: User: {current_user.email}")
        print(f"DEBUG: Database session: {db}")
        
        return {
            "message": f"Debug: Received '{message}' from {current_user.email}",
            "success": True
        }
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")
