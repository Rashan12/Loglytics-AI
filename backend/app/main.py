"""
Main FastAPI application for Loglytics AI
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time
from contextlib import asynccontextmanager

from app.config import settings
from app.database.database import init_db, get_database_health, optimize_database
from app.api.v1.router import api_router
from app.middleware.rate_limit import create_rate_limit_middleware
from app.core.security_init import setup_security_middleware, initialize_security_services, setup_security_logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Loglytics AI application...")

    # Setup security logging
    setup_security_logging()
    logger.info("Security logging configured")

    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Run database optimizations
    try:
        await optimize_database()
        logger.info("Database optimizations applied")
    except Exception as e:
        logger.warning(f"Database optimization failed: {e}")

    # Initialize security services
    security_services = initialize_security_services()
    logger.info("Security services initialized")

    # Initialize WebSocket connection manager
    from app.websockets.manager import connection_manager
    await connection_manager.initialize_redis()
    logger.info("WebSocket manager initialized")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Loglytics AI application...")

    # Cleanup WebSocket manager
    await connection_manager.cleanup()
    logger.info("WebSocket manager cleaned up")

    logger.info("Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered log analysis and monitoring platform",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Setup comprehensive security middleware
setup_security_middleware(app)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.loglytics.ai"]
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Add request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request"""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle Starlette HTTP exceptions"""
    logger.warning(f"Starlette HTTP {exc.status_code}: {exc.detail} - {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()} - {request.url}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "details": exc.errors(),
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)} - {request.url}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }

# Security status endpoint
@app.get("/security/status")
async def security_status():
    """Security status endpoint"""
    from app.core.security_init import get_security_status, validate_security_config
    
    status = get_security_status()
    validation_errors = validate_security_config()
    
    return {
        "status": "operational" if not validation_errors else "configuration_errors",
        "configuration": status,
        "validation_errors": validation_errors,
        "timestamp": time.time()
    }

# Database health endpoint
@app.get("/database/health")
async def database_health():
    """Database health endpoint"""
    try:
        health = await get_database_health()
        return health
    except Exception as e:
        logger.error(f"Error getting database health: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# Database optimization endpoint
@app.post("/database/optimize")
async def database_optimize():
    """Database optimization endpoint"""
    try:
        result = await optimize_database()
        return {
            "status": "success" if result else "failed",
            "message": "Database optimization completed" if result else "Database optimization failed",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation not available in production"
    }

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Include WebSocket router
from app.websockets.router import router as websocket_router
app.include_router(websocket_router, prefix="/api/v1", tags=["websockets"])

# Add startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started successfully")

# Add shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} shutting down")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )