from fastapi import APIRouter, Depends
from app.services.auth.jwt_handler import get_current_user

router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/auth")
async def test_auth(current_user: dict = Depends(get_current_user)):
    """Test authentication without database"""
    return {
        "message": "Auth works!",
        "user_id": current_user["id"],
        "email": current_user["email"]
    }

@router.get("/public")
async def test_public():
    """Public endpoint"""
    return {"message": "Public endpoint works!"}
