"""
==============================================================================
MODULE: Live Vision API
==============================================================================

PURPOSE:
Provides endpoint to get credentials for Gemini Live API WebSocket connection.
For testing, returns API key directly. In production, consider using
server-side WebSocket proxy for better security.

NOTE: The ephemeral token format (auth_tokens/xxx) doesn't work directly
in WebSocket URL query params. Official SDKs handle this internally.
==============================================================================
"""
from fastapi import APIRouter, Depends, HTTPException
from app.config import get_settings, Settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/token")
async def get_live_token(settings: Settings = Depends(get_settings)):
    """
    Get credentials for Gemini Live API WebSocket connection.
    
    Returns API key and WebSocket URL for direct connection.
    Uses v1alpha API which supports the native audio model.
    """
    api_key = settings.gemini_api_key
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    logger.info("Returning Gemini Live API connection info")
    
    return {
        "token": api_key,
        "websocket_url": "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent",
        "model": "models/gemini-2.5-flash-native-audio-preview-12-2025"
    }
