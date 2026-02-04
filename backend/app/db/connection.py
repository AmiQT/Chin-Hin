from supabase import create_client, Client
from functools import lru_cache
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get cached Supabase client instance.
    Uses environment variables for URL and key.
    """
    settings = get_settings()
    
    if not settings.supabase_url or not settings.supabase_key:
        logger.warning("⚠️ Supabase credentials not configured!")
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    
    client = create_client(settings.supabase_url, settings.supabase_key)
    logger.info("✅ Supabase client initialized")
    return client


# Dependency for FastAPI
async def get_db() -> Client:
    """FastAPI dependency to get Supabase client."""
    return get_supabase_client()
