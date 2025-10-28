from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
import logging
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Loglytics AI API",
    description="Intelligent Log Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===== CORS MIDDLEWARE - MUST BE FIRST =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Rate limiting storage
request_counts = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests
    cutoff = current_time - 60
    request_counts[client_ip] = [
        ts for ts in request_counts[client_ip] if ts > cutoff
    ]
    
    # Check rate limit
    if len(request_counts[client_ip]) > 100:
        logger.warning(f"⚠️ Rate limit exceeded for {client_ip}")
        return Response(
            content="Rate limit exceeded",
            status_code=429
        )
    
    request_counts[client_ip].append(current_time)
    response = await call_next(request)
    return response

@app.middleware("http")
async def handle_cors_preflight(request: Request, call_next):
    """Handle CORS preflight requests"""
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    return await call_next(request)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    logger.info(f"📥 {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"📤 {request.method} {request.url} - {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ {request.method} {request.url} - ERROR: {e}")
        raise

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Include API router
from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "loglytics-ai"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Loglytics AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Application started")
    
    # Initialize database
    from app.database.database import init_db
    from app.services.database_init import fix_database_indexes
    from app.database.session import get_db
    
    await init_db()
    
    # Fix problematic indexes and schema
    async for db in get_db():
        from app.services.database_init import alter_log_files_schema
        await alter_log_files_schema(db)
        await db.commit()
        await fix_database_indexes(db)
        break
    
    logger.info("✅ Database initialized")
    
    # Start background tasks for live logs
    from app.services.live_logs.background_tasks import background_runner
    await background_runner.start()
    logger.info("✅ Background tasks started")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("👋 Application shutting down")
    
    # Stop background tasks
    from app.services.live_logs.background_tasks import background_runner
    await background_runner.stop()
    logger.info("✅ Background tasks stopped")