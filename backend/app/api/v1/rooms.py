from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel

from app.api.deps import get_current_user, CurrentUser
from app.services.data_store import get_store

router = APIRouter(prefix="/rooms", tags=["Room Bookings"])


class BookingRequest(BaseModel):
    room_name: str
    date: str
    start_time: str
    end_time: str
    purpose: str


# ================================================
# ROOMS
# ================================================

@router.get("")
async def get_rooms(min_capacity: Optional[int] = None):
    """Get all active rooms."""
    store = get_store()
    rooms = [r for r in store.rooms if r["is_active"]]
    if min_capacity:
        rooms = [r for r in rooms if r["capacity"] >= min_capacity]
    return {"success": True, "data": rooms, "total": len(rooms)}


@router.get("/{room_id}")
async def get_room(room_id: str):
    """Get single room by ID."""
    store = get_store()
    room = store.get_room_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"success": True, "data": room}


@router.get("/{room_id}/bookings")
async def get_room_bookings(room_id: str, date: Optional[str] = None):
    """Get bookings for a specific room."""
    store = get_store()
    room = store.get_room_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    bookings = store.get_room_bookings(room["name"], date)
    return {"success": True, "data": bookings, "total": len(bookings)}


# ================================================
# BOOKINGS
# ================================================

@router.get("/bookings/all")
async def get_all_bookings(
    status: Optional[str] = None,
    user_id: Optional[str] = None,
):
    """Get all room bookings."""
    store = get_store()
    bookings = store.get_all_room_bookings(user_id=user_id, status=status)
    return {"success": True, "data": bookings, "total": len(bookings)}


@router.post("/bookings")
async def create_booking(
    request: BookingRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create new room booking. Requires: Authenticated user."""
    store = get_store()
    if not store.is_room_available(request.room_name, request.date, request.start_time, request.end_time):
        existing = store.get_room_bookings(request.room_name, request.date)
        taken = ", ".join(f"{b['start_time']}-{b['end_time']}" for b in existing)
        raise HTTPException(
            status_code=409,
            detail=f"Bilik {request.room_name} dah ditempah slot {taken}. Cuba masa lain!",
        )
    record = store.add_room_booking(
        current_user.id, request.room_name, request.date,
        request.start_time, request.end_time, request.purpose,
    )
    return {
        "success": True,
        "message": f"Bilik {request.room_name} berjaya dibooking! 🎉",
        "data": record,
    }


@router.delete("/bookings/{booking_id}")
async def cancel_booking(
    booking_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Cancel a room booking. Owner atau admin sahaja."""
    store = get_store()
    booking = store.get_room_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking["user_id"] != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Kau tak boleh cancel booking orang lain! 🚫")
    store.cancel_room_booking(booking_id)
    return {"success": True, "message": "Booking cancelled ❌", "data": booking}
