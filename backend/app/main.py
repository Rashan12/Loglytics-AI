from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from fastapi.middleware.asyncexitstack import AsyncExitStackMiddleware
from typing import Any
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

# Rate limiting storage
request_counts = defaultdict(list)

# Define all middleware as BaseHTTPMiddleware classes
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests (older than 60 seconds)
        cutoff = current_time - 60
        request_counts[client_ip] = [
            ts for ts in request_counts[client_ip] if ts > cutoff
        ]
        
        # Check rate limit (100 requests per minute)
        if len(request_counts[client_ip]) > 100:
            logger.warning(f"⚠️ Rate limit exceeded for {client_ip}")
            return Response(
                content="Rate limit exceeded",
                status_code=429
            )
        
        request_counts[client_ip].append(current_time)
        response = await call_next(request)
        return response

class LogRequestsMiddleware(BaseHTTPMiddleware):
    """Log all requests"""
    async def dispatch(self, request: Request, call_next):
        logger.info(f"📥 {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"📤 {request.method} {request.url} - {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"❌ {request.method} {request.url} - ERROR: {e}")
            raise

class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """Add processing time header"""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to all requests"""
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# Create FastAPI app
app = FastAPI(
    title="Loglytics AI API",
    description="Intelligent Log Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===== ADD ALL MIDDLEWARE USING app.add_middleware() =====
# CORS middleware first (critical for cross-origin requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Add all custom middleware using app.add_middleware()
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LogRequestsMiddleware)
app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(RequestIDMiddleware)

# ===== COMPLETELY REWRITE build_middleware_stack TO HANDLE Middleware OBJECTS =====
def fixed_build_middleware_stack(self) -> Any:
    """Fixed middleware stack builder that properly handles Middleware objects"""
    # Duplicate/override from Starlette to add AsyncExitStackMiddleware
    # inside of ExceptionMiddleware, inside of custom user middlewares
    debug = self.debug
    error_handler = None
    exception_handlers = {}

    for key, value in self.exception_handlers.items():
        if key in (500, Exception):
            error_handler = value
        else:
            exception_handlers[key] = value

    # Normalize user_middleware - convert Middleware objects to tuples for consistent processing
    normalized_user_middleware = []
    for m in self.user_middleware:
        if isinstance(m, StarletteMiddleware):
            # Extract cls and kwargs from Middleware object
            cls = m.cls
            kwargs = m.kwargs if hasattr(m, 'kwargs') else {}
            normalized_user_middleware.append((cls, kwargs))
        elif isinstance(m, tuple) and len(m) == 2:
            # Already a tuple
            normalized_user_middleware.append(m)
        else:
            logger.warning(f"Unexpected middleware format: {type(m)} - {m}")

    # Build middleware list - convert all to tuples for consistent processing
    middleware = (
        [(ServerErrorMiddleware, {'handler': error_handler, 'debug': debug})]
        + normalized_user_middleware
        + [
            (ExceptionMiddleware, {'handlers': exception_handlers, 'debug': debug}),
            (AsyncExitStackMiddleware, {}),
        ]
    )

    # Build the app by wrapping in reverse order
    # All middleware is now in (cls, options) tuple format
    app_instance = self.router
    for cls, options in reversed(middleware):
        app_instance = cls(app=app_instance, **options)
    
    return app_instance

# Replace the method
from types import MethodType
app.build_middleware_stack = MethodType(fixed_build_middleware_stack, app)

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
    try:
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
    except Exception as e:
        logger.error(f"⚠️ Database initialization error: {e}")
    
    # Start background tasks for live logs
    try:
        from app.services.live_logs.background_tasks import background_runner
        await background_runner.start()
        logger.info("✅ Background tasks started")
    except Exception as e:
        logger.warning(f"⚠️ Background tasks error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("👋 Application shutting down")
    
    # Stop background tasks
    try:
        from app.services.live_logs.background_tasks import background_runner
        await background_runner.stop()
        logger.info("✅ Background tasks stopped")
    except Exception as e:
        logger.warning(f"⚠️ Background tasks shutdown error: {e}")
