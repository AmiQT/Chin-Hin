"""
Supabase client helper for backend.
Uses SERVICE_ROLE key to bypass RLS for backend operations.
"""

from supabase import create_client, Client
from functools import lru_cache
from app.config import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """Get cached Supabase client instance with SERVICE_ROLE for RLS bypass."""
    settings = get_settings()
    # Use service role key for backend (bypasses RLS)
    key = settings.supabase_service_role_key or settings.supabase_key
    return create_client(settings.supabase_url, key)
