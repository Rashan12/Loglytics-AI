from fastapi import APIRouter

# Import all endpoint routers
from app.api.v1.endpoints import auth, projects, chat, test, debug, simple_test, analytics, debug_chat, rag, logs, live_logs

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(live_logs.router, prefix="/live-logs", tags=["Live Logs"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(test.router, tags=["Test"])
api_router.include_router(debug.router, prefix="/debug", tags=["Debug"])
api_router.include_router(simple_test.router, prefix="/simple", tags=["Simple Test"])
api_router.include_router(debug_chat.router, prefix="/debug", tags=["Debug Chat"])

# Test endpoint
@api_router.get("/test")
async def test_endpoint():
    return {"status": "API router working", "version": "1.0"}