#!/usr/bin/env python3
"""
Ultra-simple test server for Loglytics AI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Loglytics AI - Test Server",
    description="Simple test server for Loglytics AI",
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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Loglytics AI - Test Server",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/database/health")
async def database_health():
    """Database health endpoint"""
    return {"status": "connected", "database": "test"}

@app.get("/security/status")
async def security_status():
    """Security status endpoint"""
    return {"status": "operational", "security_features": ["cors"]}

# API endpoints
@app.get("/api/v1/auth/register")
async def register():
    return {"message": "Registration endpoint available", "status": "ok"}

@app.get("/api/v1/users/me")
async def get_user():
    return {"message": "User endpoint available", "status": "ok"}

@app.get("/api/v1/projects")
async def get_projects():
    return {"message": "Projects endpoint available", "status": "ok"}

@app.get("/api/v1/logs")
async def get_logs():
    return {"message": "Logs endpoint available", "status": "ok"}

@app.get("/api/v1/analytics")
async def get_analytics():
    return {"message": "Analytics endpoint available", "status": "ok"}

@app.get("/api/v1/chat")
async def get_chat():
    return {"message": "Chat endpoint available", "status": "ok"}

@app.get("/api/v1/llm")
async def get_llm():
    return {"message": "LLM endpoint available", "status": "ok"}

@app.get("/api/v1/rag")
async def get_rag():
    return {"message": "RAG endpoint available", "status": "ok"}

@app.get("/api/v1/live-logs")
async def get_live_logs():
    return {"message": "Live logs endpoint available", "status": "ok"}

@app.get("/api/v1/settings")
async def get_settings():
    return {"message": "Settings endpoint available", "status": "ok"}

if __name__ == "__main__":
    print("Starting Loglytics AI Test Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
