from fastapi import APIRouter, Depends
from typing import List
from app.api.deps import get_current_user, CurrentUser
from app.services.nudge_service import get_nudge_service

router = APIRouter(prefix="/nudges", tags=["Nudges"])

@router.get("", response_model=List[dict])
async def get_my_nudges(
    unread_only: bool = True,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get proactive reminders for the current user."""
    service = get_nudge_service()
    return await service.get_user_nudges(current_user.id, only_unread=unread_only)

@router.post("/{nudge_id}/read")
async def mark_nudge_as_read(
    nudge_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Mark a nudge as seen by the user."""
    service = get_nudge_service()
    # Logic to check ownership could be added here
    await service.mark_as_read(nudge_id)
    return {"success": True, "message": "Nudge marked as read"}
