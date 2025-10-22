"""
Main API router for Loglytics AI v1
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, logs, analytics, chat, llm, rag, live_logs, settings, projects

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(llm.router, prefix="/llm", tags=["LLM"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(live_logs.router, prefix="/live-logs", tags=["Live Logs"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(projects.router, tags=["Projects"])