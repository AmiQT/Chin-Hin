from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.api.deps import get_current_user, require_hr, CurrentUser
from app.services.data_store import get_store
from app.api.v1.auth import _MOCK_USERS

router = APIRouter(prefix="/users", tags=["Users"])


def _find_user_by_id(user_id: str) -> Optional[dict]:
    """Lookup user by user_id since _MOCK_USERS is keyed by email."""
    for email, u in _MOCK_USERS.items():
        if u.get("user_id") == user_id:
            return {"email": email, **u}
    return None


def _format_user(email: str, u: dict, uid: str) -> dict:
    return {
        "id": uid or u.get("user_id", ""),
        "name": u.get("full_name", ""),
        "email": email,
        "role": u.get("role", "employee"),
        "department": u.get("department", ""),
        "position": u.get("position", ""),
    }


@router.get("")
async def get_users(
    department: Optional[str] = None,
    role: Optional[str] = None,
    current_user: CurrentUser = Depends(require_hr),
):
    """
    Get all users dengan optional filters.
    Requires: HR or Admin role
    """
    users = []
    for email, u in _MOCK_USERS.items():
        if department and u.get("department") != department:
            continue
        if role and u.get("role") != role:
            continue
        users.append(_format_user(email, u, u.get("user_id", "")))
    return {"success": True, "data": users, "total": len(users)}


@router.get("/{user_id}")
async def get_user(user_id: str):
    """
    Get single user by ID.
    """
    u = _find_user_by_id(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": _format_user(u["email"], u, user_id)}


@router.get("/{user_id}/leaves")
async def get_user_leaves(
    user_id: str,
    status: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get leave requests for a specific user.
    """
    if user_id != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Forbidden")
    if not _find_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    store = get_store()
    leaves = store.get_leave_applications(user_id, status=status)
    return {"success": True, "data": leaves, "total": len(leaves)}


@router.get("/{user_id}/claims")
async def get_user_claims(
    user_id: str,
    status: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get claims for a specific user.
    """
    if user_id != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Forbidden")
    if not _find_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    store = get_store()
    claims = store.get_claims(user_id, status=status)
    return {"success": True, "data": claims, "total": len(claims)}
