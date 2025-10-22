#!/usr/bin/env python3
"""
Simple test app for Loglytics AI
Minimal version that can run without complex dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Loglytics AI - Test API",
    description="Simplified test version of Loglytics AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Loglytics AI - Test API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

# Basic API endpoints for testing
@app.get("/api/v1/auth/register")
async def register_endpoint():
    """Test registration endpoint"""
    return {"message": "Registration endpoint available", "status": "ok"}

@app.get("/api/v1/users/me")
async def get_user():
    """Test user endpoint"""
    return {"message": "User endpoint available", "status": "ok"}

@app.get("/api/v1/projects")
async def get_projects():
    """Test projects endpoint"""
    return {"message": "Projects endpoint available", "status": "ok"}

@app.get("/api/v1/logs")
async def get_logs():
    """Test logs endpoint"""
    return {"message": "Logs endpoint available", "status": "ok"}

@app.get("/api/v1/analytics")
async def get_analytics():
    """Test analytics endpoint"""
    return {"message": "Analytics endpoint available", "status": "ok"}

@app.get("/api/v1/chat")
async def get_chat():
    """Test chat endpoint"""
    return {"message": "Chat endpoint available", "status": "ok"}

@app.get("/api/v1/llm")
async def get_llm():
    """Test LLM endpoint"""
    return {"message": "LLM endpoint available", "status": "ok"}

@app.get("/api/v1/rag")
async def get_rag():
    """Test RAG endpoint"""
    return {"message": "RAG endpoint available", "status": "ok"}

@app.get("/api/v1/live-logs")
async def get_live_logs():
    """Test live logs endpoint"""
    return {"message": "Live logs endpoint available", "status": "ok"}

@app.get("/api/v1/settings")
async def get_settings():
    """Test settings endpoint"""
    return {"message": "Settings endpoint available", "status": "ok"}

@app.get("/security/status")
async def security_status():
    """Security status endpoint"""
    return {
        "status": "operational",
        "security_features": ["rate_limiting", "cors", "validation"],
        "timestamp": time.time()
    }

@app.get("/database/health")
async def database_health():
    """Database health endpoint"""
    return {
        "status": "connected",
        "database": "test_mode",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
