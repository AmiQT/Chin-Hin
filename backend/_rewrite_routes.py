"""Script untuk rewrite rooms.py, claims.py, users.py — remove all Supabase."""
import pathlib

BASE = pathlib.Path(r"c:\Users\noora\Documents\Coding\Chin Hin\backend\app\api\v1")

# ============================================================
# rooms.py
# ============================================================
ROOMS = '''\
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


# ================================================
# BOOKINGS
# ================================================

@router.get("/bookings/all")
async def get_all_bookings(
    status: Optional[str] = None,
    user_id: Optional[str] = None,
):
    """Get all room bookings dengan optional filters."""
    store = get_store()
    bookings = store.get_all_room_bookings(user_id=user_id, status=status)
    return {"success": True, "data": bookings, "total": len(bookings)}


@router.get("/bookings/mine")
async def get_my_bookings(current_user: CurrentUser = Depends(get_current_user)):
    """Get current user\'s room bookings."""
    store = get_store()
    bookings = store.get_all_room_bookings(user_id=current_user.id)
    return {"success": True, "data": bookings, "total": len(bookings)}


@router.post("/bookings")
async def create_booking(
    request: BookingRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Book a meeting room."""
    store = get_store()
    if not store.is_room_available(request.room_name, request.date, request.start_time, request.end_time):
        existing = store.get_room_bookings(request.room_name, request.date)
        taken = ", ".join(f"{b[\'start_time\']}-{b[\'end_time\']}" for b in existing)
        raise HTTPException(
            status_code=409,
            detail=f"Bilik {request.room_name} dah ditempah untuk slot {taken}. Cuba masa lain!",
        )
    record = store.add_room_booking(
        current_user.id, request.room_name, request.date,
        request.start_time, request.end_time, request.purpose,
    )
    return {
        "success": True,
        "message": f"Bilik {request.room_name} berjaya dibooking! (ID: {record[\'id\']}) 🎉",
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
        raise HTTPException(status_code=403, detail="Kau tak boleh cancel booking orang lain!")
    store.cancel_room_booking(booking_id)
    return {"success": True, "message": "Booking cancelled.", "data": booking}
'''

# ============================================================
# claims.py
# ============================================================
CLAIMS = '''\
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Optional
from datetime import date
from pydantic import BaseModel
import base64

from app.api.deps import get_current_user, require_manager_or_hr, CurrentUser
from app.services.data_store import get_store
from app.services.ocr_service import get_ocr_service

router = APIRouter(prefix="/claims", tags=["Expense Claims"])


class ClaimRequest(BaseModel):
    category_id: str
    amount: float
    description: Optional[str] = None
    claim_date: Optional[date] = None


# ================================================
# CLAIM CATEGORIES
# ================================================

@router.get("/categories")
async def get_claim_categories():
    """Get all claim categories."""
    store = get_store()
    return {"success": True, "data": store.claim_categories}


# ================================================
# CLAIMS
# ================================================

@router.get("")
async def get_claims(
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get claims. HR/Admin: semua user. Employee: claim sendiri sahaja.
    Status: pending, approved, rejected
    """
    store = get_store()
    is_privileged = current_user.role in ("hr", "admin", "manager")
    target_uid = user_id if (is_privileged and user_id) else (None if is_privileged else current_user.id)
    claims = store.get_all_claims(status=status, user_id=target_uid)
    return {"success": True, "data": claims, "total": len(claims)}


@router.get("/{claim_id}")
async def get_claim(
    claim_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get single claim by ID."""
    store = get_store()
    claim = store.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["user_id"] != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"success": True, "data": claim}


@router.post("")
async def create_claim(
    request: ClaimRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Submit expense claim baru."""
    store = get_store()
    # Validate category & max amount
    category = next((c for c in store.claim_categories if c["id"] == request.category_id), None)
    if not category:
        raise HTTPException(status_code=400, detail=f"Category ID \'{request.category_id}\' tidak wujud")
    if request.amount > category["max_amount"]:
        raise HTTPException(
            status_code=400,
            detail=f"Amount RM{request.amount:.2f} melebihi had kategori {category[\'name\']} (RM{category[\'max_amount\']:.2f})",
        )
    record = store.add_claim(
        user_id=current_user.id,
        category_id=request.category_id,
        category_name=category["name"],
        amount=request.amount,
        description=request.description,
        claim_date=str(request.claim_date) if request.claim_date else None,
    )
    return {
        "success": True,
        "message": f"Claim RM{request.amount:.2f} ({category[\'name\']}) berjaya disubmit! 🎉",
        "data": record,
    }


@router.patch("/{claim_id}/approve")
async def approve_claim(
    claim_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr),
):
    """Approve expense claim. Requires: Manager/HR."""
    store = get_store()
    claim = store.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot approve claim with status \'{claim[\'status\']}\'")
    updated = store.update_claim_status(claim_id, "approved", actor_id=current_user.id)
    return {"success": True, "message": "Claim approved!", "data": updated}


@router.patch("/{claim_id}/reject")
async def reject_claim(
    claim_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr),
):
    """Reject expense claim. Requires: Manager/HR."""
    store = get_store()
    claim = store.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot reject claim with status \'{claim[\'status\']}\'")
    updated = store.update_claim_status(claim_id, "rejected", actor_id=current_user.id)
    return {"success": True, "message": "Claim rejected.", "data": updated}


# ================================================
# OCR RECEIPT SCANNING
# ================================================

@router.post("/scan-receipt")
async def scan_receipt(file: UploadFile = File(...)):
    """Scan receipt untuk extract amount dan details."""
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File terlalu besar (max 10MB)")
    allowed = ["image/jpeg", "image/png", "image/jpg", "application/pdf", "image/webp"]
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Format tidak disokong: {file.content_type}")
    image_data = base64.b64encode(content).decode("utf-8")
    ocr_service = get_ocr_service()
    result = await ocr_service.extract_receipt_data(image_data, file.content_type)
    return {"success": True, "data": result}
'''

# ============================================================
# users.py
# ============================================================
USERS = '''\
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.api.deps import get_current_user, require_hr, CurrentUser
from app.services.data_store import get_store
from app.api.v1.auth import _MOCK_USERS

router = APIRouter(prefix="/users", tags=["Users"])


def _all_mock_users(department: Optional[str] = None, role: Optional[str] = None) -> list:
    """Return sanitised list of mock users, applying optional filters."""
    users = []
    for uid, u in _MOCK_USERS.items():
        user_dict = {
            "id": uid,
            "name": u["name"],
            "email": u["email"],
            "role": u["role"],
            "department": u.get("department", ""),
            "position": u.get("position", ""),
        }
        if department and user_dict["department"] != department:
            continue
        if role and user_dict["role"] != role:
            continue
        users.append(user_dict)
    return users


@router.get("")
async def get_users(
    department: Optional[str] = None,
    role: Optional[str] = None,
    current_user: CurrentUser = Depends(require_hr),
):
    """Get all users. Requires: HR or Admin role."""
    users = _all_mock_users(department=department, role=role)
    return {"success": True, "data": users, "total": len(users)}


@router.get("/me")
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Get current user profile."""
    u = _MOCK_USERS.get(current_user.id, {})
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "name": u.get("name", current_user.name),
            "email": u.get("email", ""),
            "role": current_user.role,
            "department": u.get("department", ""),
            "position": u.get("position", ""),
        },
    }


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get single user by ID."""
    u = _MOCK_USERS.get(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "success": True,
        "data": {
            "id": user_id,
            "name": u["name"],
            "email": u["email"],
            "role": u["role"],
            "department": u.get("department", ""),
            "position": u.get("position", ""),
        },
    }


@router.get("/{user_id}/leaves")
async def get_user_leaves(
    user_id: str,
    status: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get leave applications for a user."""
    if user_id != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Forbidden")
    store = get_store()
    leaves = store.get_leave_applications(user_id, status=status)
    return {"success": True, "data": leaves, "total": len(leaves)}


@router.get("/{user_id}/claims")
async def get_user_claims(
    user_id: str,
    status: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get expense claims for a user."""
    if user_id != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Forbidden")
    store = get_store()
    claims = store.get_claims(user_id, status=status)
    return {"success": True, "data": claims, "total": len(claims)}
'''

# ============================================================
# Write files
# ============================================================
files = {
    BASE / "rooms.py": ROOMS,
    BASE / "claims.py": CLAIMS,
    BASE / "users.py": USERS,
}

for path, content in files.items():
    path.write_text(content, encoding="utf-8")
    print(f"✅ Written: {path} ({len(content)} chars)")

print("\nDone! All 3 files rewritten.")
