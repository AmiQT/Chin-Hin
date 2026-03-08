import pathlib

base = pathlib.Path("app/api/v1")

# ── rooms.py ──────────────────────────────────────────────────────────────────
rooms = """\
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


@router.get("")
async def get_rooms(min_capacity: Optional[int] = None):
    store = get_store()
    rooms = [r for r in store.rooms if r["is_active"]]
    if min_capacity:
        rooms = [r for r in rooms if r["capacity"] >= min_capacity]
    return {"success": True, "data": rooms, "total": len(rooms)}


@router.get("/bookings/all")
async def get_all_bookings(status: Optional[str] = None, user_id: Optional[str] = None):
    store = get_store()
    bookings = store.get_all_room_bookings(user_id=user_id, status=status)
    return {"success": True, "data": bookings, "total": len(bookings)}


@router.get("/bookings/mine")
async def get_my_bookings(current_user: CurrentUser = Depends(get_current_user)):
    store = get_store()
    bookings = store.get_all_room_bookings(user_id=current_user.id)
    return {"success": True, "data": bookings, "total": len(bookings)}


@router.post("/bookings")
async def create_booking(
    request: BookingRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    store = get_store()
    if not store.is_room_available(request.room_name, request.date, request.start_time, request.end_time):
        existing = store.get_room_bookings(request.room_name, request.date)
        taken = ", ".join(f"{b['start_time']}-{b['end_time']}" for b in existing)
        raise HTTPException(status_code=409, detail=f"Bilik {request.room_name} dah ditempah slot {taken}. Cuba masa lain!")
    record = store.add_room_booking(
        current_user.id, request.room_name, request.date,
        request.start_time, request.end_time, request.purpose
    )
    return {"success": True, "message": f"Bilik {request.room_name} berjaya dibooking! (ID: {record['id']}) \U0001f389", "data": record}


@router.delete("/bookings/{booking_id}")
async def cancel_booking(booking_id: str, current_user: CurrentUser = Depends(get_current_user)):
    store = get_store()
    booking = store.get_room_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking["user_id"] != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Kau tak boleh cancel booking orang lain!")
    store.cancel_room_booking(booking_id)
    return {"success": True, "message": "Booking cancelled.", "data": booking}
"""

# ── claims.py ─────────────────────────────────────────────────────────────────
claims = """\
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Optional
from datetime import date
from pydantic import BaseModel

from app.api.deps import get_current_user, require_manager_or_hr, CurrentUser
from app.services.data_store import get_store
from app.services.ocr_service import get_ocr_service

router = APIRouter(prefix="/claims", tags=["Expense Claims"])


class ClaimRequest(BaseModel):
    category: str
    amount: float
    description: Optional[str] = None
    claim_date: Optional[date] = None


@router.get("/categories")
async def get_claim_categories():
    store = get_store()
    return {"success": True, "data": store.claim_categories}


@router.get("")
async def get_claims(
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    store = get_store()
    if current_user.is_admin() or current_user.has_role("hr") or current_user.has_role("manager"):
        data = store.get_all_claims(status=status, user_id=user_id)
    else:
        data = store.get_claims(current_user.id, status=status)
    total = sum(c["amount"] for c in data)
    return {"success": True, "data": data, "total": len(data), "total_amount": total}


@router.get("/{claim_id}")
async def get_claim(claim_id: str):
    store = get_store()
    claim = store.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return {"success": True, "data": claim}


@router.post("")
async def create_claim(
    request: ClaimRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    store = get_store()
    cat = next((c for c in store.claim_categories if c["name"].lower() == request.category.lower()), None)
    max_amount = cat["max_amount"] if cat else 9999.0
    if request.amount > max_amount:
        raise HTTPException(status_code=400, detail=f"Amount melebihi had RM{max_amount:.2f} untuk {request.category}")
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount mestilah lebih dari 0")
    record = store.add_claim(
        current_user.id, request.category, request.amount,
        request.description or "",
        (request.claim_date or date.today()).isoformat()
    )
    return {"success": True, "message": f"Claim RM{request.amount:.2f} submitted! \U0001f4b0", "data": record}


@router.patch("/{claim_id}/approve")
async def approve_claim(claim_id: str, current_user: CurrentUser = Depends(require_manager_or_hr)):
    store = get_store()
    claim = store.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["status"] != "pending":
        raise HTTPException(status_code=400, detail="Hanya claim pending boleh diluluskan")
    updated = store.update_claim_status(claim_id, "approved", current_user.id)
    return {"success": True, "message": f"Claim RM{claim['amount']:.2f} diluluskan! \u2705", "data": updated}


@router.patch("/{claim_id}/reject")
async def reject_claim(claim_id: str, current_user: CurrentUser = Depends(require_manager_or_hr)):
    store = get_store()
    claim = store.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["status"] != "pending":
        raise HTTPException(status_code=400, detail="Hanya claim pending boleh ditolak")
    updated = store.update_claim_status(claim_id, "rejected", current_user.id)
    return {"success": True, "message": "Claim ditolak \u274c", "data": updated}


@router.post("/scan-receipt")
async def scan_receipt_only(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user)
):
    allowed = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Format tidak disokong. Guna JPEG, PNG, atau PDF.")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fail terlalu besar. Max 10MB.")
    ocr_service = get_ocr_service()
    receipt_data = await ocr_service.extract_receipt_data(content)
    return {"success": True, "message": "Resit berjaya diimbas! \U0001f50d", "data": receipt_data.to_dict()}
"""

# ── users.py ──────────────────────────────────────────────────────────────────
users = """\
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.api.deps import require_hr, get_current_user, CurrentUser
from app.services.data_store import get_store

router = APIRouter(prefix="/users", tags=["Users"])


def _get_mock_users():
    from app.api.v1.auth import _MOCK_USERS
    return [
        {
            "id": v["id"],
            "email": email,
            "full_name": v["full_name"],
            "role": v["role"],
            "department": v.get("department", "General"),
        }
        for email, v in _MOCK_USERS.items()
    ]


@router.get("")
async def get_users(
    department: Optional[str] = None,
    role: Optional[str] = None,
    current_user: CurrentUser = Depends(require_hr)
):
    users = _get_mock_users()
    if department:
        users = [u for u in users if u.get("department", "").lower() == department.lower()]
    if role:
        users = [u for u in users if u.get("role", "").lower() == role.lower()]
    return {"success": True, "data": users, "total": len(users)}


@router.get("/me")
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    users = _get_mock_users()
    user = next((u for u in users if u["id"] == current_user.id), None)
    if not user:
        return {"success": True, "data": {"id": current_user.id, "email": current_user.email, "role": current_user.role}}
    return {"success": True, "data": user}


@router.get("/{user_id}")
async def get_user(user_id: str):
    users = _get_mock_users()
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": user}


@router.get("/{user_id}/leaves")
async def get_user_leaves(user_id: str):
    store = get_store()
    leaves = store.get_leave_applications(user_id)
    return {"success": True, "data": leaves, "total": len(leaves)}


@router.get("/{user_id}/claims")
async def get_user_claims(user_id: str):
    store = get_store()
    claims = store.get_claims(user_id)
    return {"success": True, "data": claims, "total": len(claims)}
"""

(base / "rooms.py").write_text(rooms, encoding="utf-8")
(base / "claims.py").write_text(claims, encoding="utf-8")
(base / "users.py").write_text(users, encoding="utf-8")
print("All 3 files written OK")
