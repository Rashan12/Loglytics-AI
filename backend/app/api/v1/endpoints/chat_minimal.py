from fastapi import APIRouter, Form, File, UploadFile
from typing import Optional

router = APIRouter()

@router.post("")
async def general_chat(
    message: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Minimal AI chat endpoint for debugging
    """
    print(f"\n{'='*60}")
    print(f"📨 MINIMAL CHAT REQUEST")
    print(f"{'='*60}")
    print(f"Message: '{message}'")
    print(f"File: {file.filename if file else 'None'}")
    print(f"{'='*60}\n")
    
    # Simple response
    response_text = f"Hello! I received your message: '{message}'. This is a test response."
    
    result = {
        "response": response_text,
        "file_processed": file is not None,
        "success": True
    }
    
    print(f"✅ Sending response: {response_text}")
    print(f"{'='*60}\n")
    
    return result
