from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns status healthy if API is running.
    """
    return {"status": "healthy", "message": "Chin Hin API is running! 🚀"}


@router.get("/")
async def root():
    """Root endpoint with welcome message."""
    return {
        "app": "Chin Hin Employee AI Assistant",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }
