from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.api.deps import get_current_user, require_manager_or_hr, CurrentUser
from app.services.data_store import get_store

router = APIRouter(prefix="/leaves", tags=["Leaves"])


class LeaveRequest(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None


# ================================================
# LEAVE TYPES
# ================================================

@router.get("/types")
async def get_leave_types():
    """Get all leave types."""
    store = get_store()
    return {"success": True, "data": store.leave_types}


# ================================================
# LEAVE BALANCE
# ================================================

@router.get("/balance")
async def get_my_leave_balance(
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get current user leave balances."""
    store = get_store()
    raw = store.get_leave_balances(current_user.id)
    balances = []
    for lt in store.leave_types:
        name = lt["name"]
        total = lt["default_days"]
        remaining = raw.get(name, total)
        used = total - remaining
        balances.append({
            "leave_type_id": lt["id"],
            "leave_type_name": name,
            "total_days": total,
            "used_days": used,
            "pending_days": 0,
            "remaining_days": remaining,
        })
    return {"success": True, "year": datetime.now().year, "data": balances}


@router.get("/balance/{user_id}")
async def get_user_leave_balance(
    user_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr)
):
    """Get specific user leave balances. Requires Manager/HR."""
    store = get_store()
    raw = store.get_leave_balances(user_id)
    balances = []
    for lt in store.leave_types:
        name = lt["name"]
        total = lt["default_days"]
        remaining = raw.get(name, total)
        used = total - remaining
        balances.append({
            "leave_type_id": lt["id"],
            "leave_type_name": name,
            "total_days": total,
            "used_days": used,
            "pending_days": 0,
            "remaining_days": remaining,
        })
    return {"success": True, "user_id": user_id, "year": datetime.now().year, "data": balances}


# ================================================
# LEAVE REQUESTS
# ================================================

@router.get("")
async def get_leave_requests(
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get leave requests. HR/Manager gets all; employee gets own."""
    store = get_store()
    if current_user.is_admin() or current_user.has_role("hr") or current_user.has_role("manager"):
        leaves = store.get_all_leave_applications(status=status)
        if user_id:
            leaves = [l for l in leaves if l["user_id"] == user_id]
    else:
        leaves = store.get_leave_applications(current_user.id)
        if status:
            leaves = [l for l in leaves if l["status"] == status]
    return {"success": True, "data": leaves, "total": len(leaves)}


@router.get("/{leave_id}")
async def get_leave_request(leave_id: str):
    """Get single leave request by ID."""
    store = get_store()
    leave = next((a for a in store.get_all_leave_applications() if a["id"] == leave_id), None)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return {"success": True, "data": leave}


@router.post("")
async def create_leave_request(
    request: LeaveRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Create new leave request."""
    store = get_store()
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    total_days = (request.end_date - request.start_date).days + 1
    balance = store.get_leave_balance(current_user.id, request.leave_type)

    if total_days > balance:
        raise HTTPException(
            status_code=400,
            detail=f"Baki cuti {request.leave_type} tidak mencukupi! Ada {balance} hari, mohon {total_days} hari."
        )

    new_balance = store.deduct_leave(current_user.id, request.leave_type, total_days)
    record = store.add_leave_application(
        current_user.id,
        request.leave_type,
        request.start_date.isoformat(),
        request.end_date.isoformat(),
        request.reason or "",
        total_days,
    )
    return {
        "success": True,
        "message": f"Permohonan cuti berjaya! ({total_days} hari) 🎉",
        "data": record,
        "balance_after": {"remaining_days": new_balance},
    }


@router.patch("/{leave_id}/approve")
async def approve_leave(
    leave_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr)
):
    """Approve a leave request. Requires Manager or HR."""
    store = get_store()
    leave = store.update_leave_application(leave_id, "approved", current_user.id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return {"success": True, "message": "Cuti diluluskan! ✅", "data": leave}


@router.patch("/{leave_id}/reject")
async def reject_leave(
    leave_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr)
):
    """Reject a leave request. Days restored automatically."""
    store = get_store()
    leave = store.update_leave_application(leave_id, "rejected", current_user.id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return {"success": True, "message": "Cuti ditolak ❌", "data": leave}
