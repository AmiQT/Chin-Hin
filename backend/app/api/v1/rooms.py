from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.db.supabase_client import get_supabase_client
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/rooms", tags=["Room Bookings"])


class BookingRequest(BaseModel):
    room_id: str
    user_id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None


# ================================================
# ROOMS
# ================================================

@router.get("")
async def get_rooms(
    is_active: Optional[bool] = True,
    min_capacity: Optional[int] = None
):
    """Get all rooms dengan optional filters."""
    supabase = get_supabase_client()
    query = supabase.table("rooms").select("*")
    
    if is_active is not None:
        query = query.eq("is_active", is_active)
    
    if min_capacity:
        query = query.gte("capacity", min_capacity)
    
    result = query.execute()
    
    return {
        "success": True,
        "data": result.data,
        "total": len(result.data)
    }


@router.get("/{room_id}")
async def get_room(room_id: str):
    """Get single room by ID."""
    supabase = get_supabase_client()
    result = supabase.table("rooms").select("*").eq("id", room_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return {
        "success": True,
        "data": result.data[0]
    }


@router.get("/{room_id}/bookings")
async def get_room_bookings(
    room_id: str,
    date: Optional[str] = None
):
    """Get bookings for a specific room."""
    supabase = get_supabase_client()
    
    room_result = supabase.table("rooms").select("id").eq("id", room_id).execute()
    if not room_result.data:
        raise HTTPException(status_code=404, detail="Room not found")
    
    query = supabase.table("room_bookings").select(
        "*, users(full_name)"
    ).eq("room_id", room_id)
    
    if date:
        query = query.gte("start_time", f"{date}T00:00:00").lte("start_time", f"{date}T23:59:59")
    
    result = query.execute()
    
    # Flatten response
    bookings = []
    for booking in result.data:
        booking_data = {**booking}
        if booking_data.get("users"):
            booking_data["user_name"] = booking_data["users"]["full_name"]
            del booking_data["users"]
        bookings.append(booking_data)
    
    return {
        "success": True,
        "data": bookings,
        "total": len(bookings)
    }


# ================================================
# BOOKINGS
# ================================================

@router.get("/bookings/all")
async def get_all_bookings(
    status: Optional[str] = None,
    user_id: Optional[str] = None
):
    """Get all room bookings."""
    supabase = get_supabase_client()
    query = supabase.table("room_bookings").select(
        "*, rooms(name), users(full_name)"
    )
    
    if status:
        query = query.eq("status", status)
    
    if user_id:
        query = query.eq("user_id", user_id)
    
    result = query.execute()
    
    # Flatten response
    bookings = []
    for booking in result.data:
        booking_data = {**booking}
        if booking_data.get("rooms"):
            booking_data["room_name"] = booking_data["rooms"]["name"]
            del booking_data["rooms"]
        if booking_data.get("users"):
            booking_data["user_name"] = booking_data["users"]["full_name"]
            del booking_data["users"]
        bookings.append(booking_data)
    
    return {
        "success": True,
        "data": bookings,
        "total": len(bookings)
    }


@router.post("/bookings")
async def create_booking(
    request: BookingRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Create new room booking.
    Requires: Authenticated user
    """
    supabase = get_supabase_client()
    
    # Use current user's ID for security
    user_id = current_user.id
    
    # Check room exists
    room_result = supabase.table("rooms").select("*").eq("id", request.room_id).execute()
    if not room_result.data:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if request.end_time <= request.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    # Check for conflicts
    conflict_result = supabase.table("room_bookings").select("id").eq(
        "room_id", request.room_id
    ).eq("status", "confirmed").gte(
        "end_time", request.start_time.isoformat()
    ).lte("start_time", request.end_time.isoformat()).execute()
    
    if conflict_result.data:
        raise HTTPException(
            status_code=409, 
            detail="Room sudah di-book pada waktu ni! 😅"
        )
    
    new_booking = {
        "room_id": request.room_id,
        "user_id": user_id,  # Use authenticated user's ID
        "title": request.title,
        "start_time": request.start_time.isoformat(),
        "end_time": request.end_time.isoformat(),
        "description": request.description,
        "status": "confirmed"
    }
    
    result = supabase.table("room_bookings").insert(new_booking).execute()
    
    room = room_result.data[0]
    return {
        "success": True,
        "message": f"Room {room.get('name')} booked! 🎉",
        "data": result.data[0] if result.data else new_booking
    }


@router.delete("/bookings/{booking_id}")
async def cancel_booking(
    booking_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Cancel a room booking.
    Requires: Authenticated user (owner or admin)
    """
    supabase = get_supabase_client()
    
    booking_result = supabase.table("room_bookings").select("*").eq("id", booking_id).execute()
    if not booking_result.data:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check ownership or admin
    booking = booking_result.data[0]
    if booking.get("user_id") != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Kau tak boleh cancel booking orang lain! 🚫")
    
    result = supabase.table("room_bookings").update({"status": "cancelled"}).eq("id", booking_id).execute()
    
    return {
        "success": True,
        "message": "Booking cancelled ❌",
        "data": result.data[0] if result.data else None
    }
