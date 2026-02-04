from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.api.v1.health import router as health_router
from app.api.v1.users import router as users_router
from app.api.v1.leaves import router as leaves_router
from app.api.v1.rooms import router as rooms_router
from app.api.v1.claims import router as claims_router
from app.api.v1.chat import router as chat_router
from app.api.v1.auth import router as auth_router
from app.api.v1.nudges import router as nudges_router
from app.api.v1.live_vision import router as live_vision_router

# Import core modules - error handling, logging, middleware
from app.core import (
    setup_logging,
    RequestMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)

# Get settings
settings = get_settings()

# Setup structured logging (environment determines format)
logger = setup_logging(environment=settings.environment)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered employee assistant untuk Chin Hin 🚀",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ================================================
# EXCEPTION HANDLERS - standardized error responses
# ================================================
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ================================================
# MIDDLEWARE - order matters! (last added = first executed)
# ================================================

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting - 100 requests per minute per IP
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Request ID tracing & logging
app.add_middleware(RequestMiddleware)

# Security headers (production-ready)
app.add_middleware(SecurityHeadersMiddleware)

# ================================================
# ROUTERS
# ================================================
app.include_router(health_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(leaves_router, prefix="/api/v1")
app.include_router(rooms_router, prefix="/api/v1")
app.include_router(claims_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(nudges_router, prefix="/api/v1")
app.include_router(live_vision_router, prefix="/api/v1/live", tags=["live"])

# ================================================
# LIFECYCLE EVENTS
# ================================================
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 {settings.app_name} starting up...")
    logger.info(f"📍 Environment: {settings.environment}")
    logger.info(f"📊 Rate limit: 100 req/min per IP")

    # Setup Background Tasks (Nudges)
    import asyncio
    from app.services.nudge_service import get_nudge_service
    
    async def nudge_scheduler():
        while True:
            try:
                service = get_nudge_service()
                await service.scan_for_nudges()
                # Run every hour (3600 seconds)
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"❌ Nudge Scheduler Error: {e}")
                await asyncio.sleep(60) # Wait a bit on error
    
    asyncio.create_task(nudge_scheduler())
    logger.info("🤖 Proactive Nudge Scheduler started!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Shutting down...")
