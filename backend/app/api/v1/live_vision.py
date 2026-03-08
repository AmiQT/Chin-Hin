"""
==============================================================================
MODULE: Live Vision API
==============================================================================

Live Vision endpoint - DISABLED.
Feature ini menggunakan Gemini Live API dan tidak dalam scope semasa.
"""

from fastapi import APIRouter
import logging

router = APIRouter(prefix="/live-vision", tags=["Live Vision"])
logger = logging.getLogger(__name__)


@router.get("/token")
async def get_live_token():
    """
    Live Vision feature - disabled.
    Feature ini memerlukan Gemini Live API yang tidak dalam scope challenge.
    """
    return {
        "success": False,
        "message": "Live Vision feature tidak tersedia dalam versi semasa.",
        "status": "disabled"
    }
