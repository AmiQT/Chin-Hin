from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.db.supabase_client import get_supabase_client
from app.api.deps import get_current_user, require_manager_or_hr, CurrentUser

router = APIRouter(prefix="/leaves", tags=["Leaves"])


class LeaveRequest(BaseModel):
    user_id: str
    leave_type_id: str
    start_date: date
    end_date: date
    reason: Optional[str] = None


# ================================================
# HELPER FUNCTIONS
# ================================================

def get_current_year() -> int:
    """Get current year for leave balance."""
    return datetime.now().year


def get_or_create_balance(supabase, user_id: str, leave_type_id: str, year: int) -> dict:
    """
    Get existing balance or create new one with default days.
    Returns balance record.
    """
    # Check existing balance
    balance_result = supabase.table("leave_balances").select("*").eq(
        "user_id", user_id
    ).eq("leave_type_id", leave_type_id).eq("year", year).execute()
    
    if balance_result.data:
        return balance_result.data[0]
    
    # Get default days from leave type
    type_result = supabase.table("leave_types").select("default_days").eq("id", leave_type_id).execute()
    default_days = type_result.data[0]["default_days"] if type_result.data else 14
    
    # Create new balance
    new_balance = {
        "user_id": user_id,
        "leave_type_id": leave_type_id,
        "year": year,
        "total_days": default_days,
        "used_days": 0,
        "pending_days": 0
    }
    result = supabase.table("leave_balances").insert(new_balance).execute()
    return result.data[0] if result.data else new_balance


# ================================================
# LEAVE BALANCE ENDPOINTS
# ================================================

@router.get("/balance")
async def get_my_leave_balance(
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get current user's leave balance for current year."""
    supabase = get_supabase_client()
    year = get_current_year()
    
    # Get all leave types with balances
    types_result = supabase.table("leave_types").select("*").eq("is_active", True).execute()
    
    balances = []
    for leave_type in types_result.data:
        balance = get_or_create_balance(supabase, current_user.id, leave_type["id"], year)
        remaining = balance["total_days"] - balance["used_days"] - balance["pending_days"]
        balances.append({
            "leave_type_id": leave_type["id"],
            "leave_type_name": leave_type["name"],
            "total_days": balance["total_days"],
            "used_days": balance["used_days"],
            "pending_days": balance["pending_days"],
            "remaining_days": remaining
        })
    
    return {
        "success": True,
        "year": year,
        "data": balances
    }


@router.get("/balance/{user_id}")
async def get_user_leave_balance(
    user_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr)
):
    """Get specific user's leave balance. Requires Manager/HR."""
    supabase = get_supabase_client()
    year = get_current_year()
    
    types_result = supabase.table("leave_types").select("*").eq("is_active", True).execute()
    
    balances = []
    for leave_type in types_result.data:
        balance = get_or_create_balance(supabase, user_id, leave_type["id"], year)
        remaining = balance["total_days"] - balance["used_days"] - balance["pending_days"]
        balances.append({
            "leave_type_id": leave_type["id"],
            "leave_type_name": leave_type["name"],
            "total_days": balance["total_days"],
            "used_days": balance["used_days"],
            "pending_days": balance["pending_days"],
            "remaining_days": remaining
        })
    
    return {
        "success": True,
        "user_id": user_id,
        "year": year,
        "data": balances
    }


# ================================================
# LEAVE TYPES
# ================================================

@router.get("/types")
async def get_leave_types():
    """Get all leave types."""
    supabase = get_supabase_client()
    result = supabase.table("leave_types").select("*").execute()
    
    return {
        "success": True,
        "data": result.data
    }


# ================================================
# LEAVE REQUESTS
# ================================================

@router.get("")
async def get_leave_requests(
    status: Optional[str] = None,
    user_id: Optional[str] = None
):
    """
    Get all leave requests dengan optional filters.
    Status: pending, approved, rejected, cancelled
    """
    supabase = get_supabase_client()
    query = supabase.table("leave_requests").select(
        "*, users(full_name), leave_types(name)"
    )
    
    if status:
        query = query.eq("status", status)
    
    if user_id:
        query = query.eq("user_id", user_id)
    
    result = query.execute()
    
    # Flatten response
    leaves = []
    for leave in result.data:
        leave_data = {**leave}
        if leave_data.get("users"):
            leave_data["user_name"] = leave_data["users"]["full_name"]
            del leave_data["users"]
        if leave_data.get("leave_types"):
            leave_data["leave_type_name"] = leave_data["leave_types"]["name"]
            del leave_data["leave_types"]
        leaves.append(leave_data)
    
    return {
        "success": True,
        "data": leaves,
        "total": len(leaves)
    }


@router.get("/{leave_id}")
async def get_leave_request(leave_id: str):
    """Get single leave request by ID."""
    supabase = get_supabase_client()
    result = supabase.table("leave_requests").select(
        "*, users(full_name), leave_types(name)"
    ).eq("id", leave_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    leave = result.data[0]
    if leave.get("users"):
        leave["user_name"] = leave["users"]["full_name"]
        del leave["users"]
    if leave.get("leave_types"):
        leave["leave_type_name"] = leave["leave_types"]["name"]
        del leave["leave_types"]
    
    return {
        "success": True,
        "data": leave
    }


@router.post("")
async def create_leave_request(
    request: LeaveRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Create new leave request.
    Checks leave balance before allowing submission.
    Adds to pending_days until approved/rejected.
    """
    supabase = get_supabase_client()
    
    # Use current user's ID instead of request body (security!)
    user_id = current_user.id
    year = get_current_year()
    
    # Check leave type exists
    type_result = supabase.table("leave_types").select("*").eq("id", request.leave_type_id).execute()
    if not type_result.data:
        raise HTTPException(status_code=400, detail="Invalid leave type")
    
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Calculate days
    total_days = (request.end_date - request.start_date).days + 1
    
    # Check leave balance
    balance = get_or_create_balance(supabase, user_id, request.leave_type_id, year)
    remaining = balance["total_days"] - balance["used_days"] - balance["pending_days"]
    
    if total_days > remaining:
        leave_type_name = type_result.data[0]["name"]
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient {leave_type_name} balance! You have {remaining} days remaining, but requesting {total_days} days."
        )
    
    # Update pending_days in balance
    new_pending = balance["pending_days"] + total_days
    supabase.table("leave_balances").update({
        "pending_days": new_pending
    }).eq("id", balance["id"]).execute()
    
    # Create request
    new_leave = {
        "user_id": user_id,
        "leave_type_id": request.leave_type_id,
        "start_date": request.start_date.isoformat(),
        "end_date": request.end_date.isoformat(),
        "total_days": total_days,
        "reason": request.reason,
        "status": "pending"
    }
    
    result = supabase.table("leave_requests").insert(new_leave).execute()
    
    return {
        "success": True,
        "message": f"Leave request created! 🎉 ({total_days} days pending approval)",
        "data": result.data[0] if result.data else new_leave,
        "balance_after": {
            "remaining_days": remaining - total_days,
            "pending_days": new_pending
        }
    }


@router.patch("/{leave_id}/approve")
async def approve_leave(
    leave_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr)
):
    """
    Approve a leave request.
    Moves days from pending to used in balance.
    Requires: Manager or HR role
    """
    supabase = get_supabase_client()
    year = get_current_year()
    
    # Check leave exists and is pending
    leave_result = supabase.table("leave_requests").select("*").eq("id", leave_id).execute()
    if not leave_result.data:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    leave = leave_result.data[0]
    if leave.get("status") != "pending":
        raise HTTPException(status_code=400, detail="Only pending leaves can be approved")
    
    total_days = leave.get("total_days", 0)
    user_id = leave.get("user_id")
    leave_type_id = leave.get("leave_type_id")
    
    # Update balance: pending → used
    balance = get_or_create_balance(supabase, user_id, leave_type_id, year)
    new_pending = max(0, balance["pending_days"] - total_days)
    new_used = balance["used_days"] + total_days
    
    supabase.table("leave_balances").update({
        "pending_days": new_pending,
        "used_days": new_used
    }).eq("id", balance["id"]).execute()
    
    # Approve the leave
    result = supabase.table("leave_requests").update({
        "status": "approved",
        "approved_by": current_user.id
    }).eq("id", leave_id).execute()
    
    remaining = balance["total_days"] - new_used - new_pending
    
    return {
        "success": True,
        "message": f"Leave approved! ✅ ({total_days} days deducted)",
        "data": result.data[0] if result.data else None,
        "balance_after": {
            "used_days": new_used,
            "remaining_days": remaining
        }
    }


@router.patch("/{leave_id}/reject")
async def reject_leave(
    leave_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr)
):
    """
    Reject a leave request.
    Returns pending days back to balance.
    Requires: Manager or HR role
    """
    supabase = get_supabase_client()
    year = get_current_year()
    
    # Check leave exists and is pending
    leave_result = supabase.table("leave_requests").select("*").eq("id", leave_id).execute()
    if not leave_result.data:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    leave = leave_result.data[0]
    if leave.get("status") != "pending":
        raise HTTPException(status_code=400, detail="Only pending leaves can be rejected")
    
    total_days = leave.get("total_days", 0)
    user_id = leave.get("user_id")
    leave_type_id = leave.get("leave_type_id")
    
    # Update balance: return pending days
    balance = get_or_create_balance(supabase, user_id, leave_type_id, year)
    new_pending = max(0, balance["pending_days"] - total_days)
    
    supabase.table("leave_balances").update({
        "pending_days": new_pending
    }).eq("id", balance["id"]).execute()
    
    # Reject the leave
    result = supabase.table("leave_requests").update({
        "status": "rejected",
        "rejected_by": current_user.id
    }).eq("id", leave_id).execute()
    
    remaining = balance["total_days"] - balance["used_days"] - new_pending
    
    return {
        "success": True,
        "message": f"Leave rejected ❌ ({total_days} days returned to balance)",
        "data": result.data[0] if result.data else None,
        "balance_after": {
            "pending_days": new_pending,
            "remaining_days": remaining
        }
    }
