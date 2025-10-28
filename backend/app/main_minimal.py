"""
Minimal FastAPI application for Loglytics AI
Disables all problematic middleware to get basic functionality working
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Loglytics AI - Minimal",
    description="Minimal version with all middleware disabled",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Simple health check
@app.get("/")
async def root():
    return {"message": "Loglytics AI - Minimal Version", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Simple projects endpoint without authentication
@app.get("/api/v1/projects")
async def get_projects():
    """Get projects - simplified version"""
    try:
        # Return mock data for now
        return {
            "projects": [
                {
                    "id": "1",
                    "name": "Test Project",
                    "description": "A test project",
                    "created_at": "2024-01-01T00:00:00Z",
                    "status": "active"
                }
            ],
            "total": 1
        }
    except Exception as e:
        logger.error(f"Error in get_projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Simple analytics endpoint
@app.get("/api/v1/analytics/dashboard")
async def get_dashboard_analytics():
    """Get dashboard analytics - simplified version"""
    try:
        return {
            "total_projects": 1,
            "total_logs": 0,
            "total_chats": 0,
            "error_rate": "0%",
            "insights": []
        }
    except Exception as e:
        logger.error(f"Error in get_dashboard_analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Simple chat endpoint
@app.post("/api/v1/chat")
async def chat():
    """Simple chat endpoint"""
    try:
        return {
            "response": "Hello! This is a minimal chat response.",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
