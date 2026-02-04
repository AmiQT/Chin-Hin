from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.db.supabase_client import get_supabase_client
from app.api.deps import get_current_user, require_hr, CurrentUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_users(
    department: Optional[str] = None,
    role: Optional[str] = None,
    current_user: CurrentUser = Depends(require_hr)
):
    """
    Get all users dengan optional filters.
    Requires: HR or Admin role
    """
    supabase = get_supabase_client()
    query = supabase.table("users").select("*")
    
    if department:
        query = query.eq("department", department)
    
    if role:
        query = query.eq("role", role)
    
    result = query.execute()
    
    return {
        "success": True,
        "data": result.data,
        "total": len(result.data)
    }


@router.get("/{user_id}")
async def get_user(user_id: str):
    """
    Get single user by ID.
    """
    supabase = get_supabase_client()
    result = supabase.table("users").select("*").eq("id", user_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "data": result.data[0]
    }


@router.get("/{user_id}/leaves")
async def get_user_leaves(user_id: str):
    """
    Get leave requests for a specific user.
    """
    supabase = get_supabase_client()
    
    # Check if user exists
    user_result = supabase.table("users").select("id").eq("id", user_id).execute()
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get leave requests with leave type info
    result = supabase.table("leave_requests").select(
        "*, leave_types(name)"
    ).eq("user_id", user_id).execute()
    
    # Flatten the response
    leaves = []
    for leave in result.data:
        leave_data = {**leave}
        if "leave_types" in leave_data and leave_data["leave_types"]:
            leave_data["leave_type_name"] = leave_data["leave_types"]["name"]
            del leave_data["leave_types"]
        leaves.append(leave_data)
    
    return {
        "success": True,
        "data": leaves,
        "total": len(leaves)
    }


@router.get("/{user_id}/claims")
async def get_user_claims(user_id: str):
    """
    Get claims for a specific user.
    """
    supabase = get_supabase_client()
    
    # Check if user exists
    user_result = supabase.table("users").select("id").eq("id", user_id).execute()
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get claims with category info
    result = supabase.table("claims").select(
        "*, claim_categories(name)"
    ).eq("user_id", user_id).execute()
    
    # Flatten the response
    claims = []
    for claim in result.data:
        claim_data = {**claim}
        if "claim_categories" in claim_data and claim_data["claim_categories"]:
            claim_data["category_name"] = claim_data["claim_categories"]["name"]
            del claim_data["claim_categories"]
        claims.append(claim_data)
    
    return {
        "success": True,
        "data": claims,
        "total": len(claims)
    }
