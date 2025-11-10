from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.session import get_db

router = APIRouter()

@router.get("/test")
async def test_chat():
    """
    Test endpoint to verify chat router is working
    """
    return {"status": "Chat endpoint working", "message": "This is a test response"}

@router.post("")
async def general_chat(
    message: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Ultra simple AI chat endpoint for debugging
    """
    print(f"\n{'='*60}")
    print(f"📨 ULTRA SIMPLE CHAT REQUEST")
    print(f"{'='*60}")
    print(f"Message: '{message}'")
    print(f"File: {file.filename if file else 'None'}")
    print(f"{'='*60}\n")
    
    # Simple response for debugging
    response_text = f"Hello! I received your message: '{message}'. This is a test response."
    
    result = {
        "response": response_text,
        "file_processed": file is not None,
        "success": True
    }
    
    print(f"✅ Sending response: {response_text}")
    print(f"{'='*60}\n")
    
    return result
