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
    category_id: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get all claims dengan optional filters.
    Status: pending, approved, rejected
    """
    store = get_store()
    is_privileged = current_user.role in ("hr", "admin", "manager")
    target_uid = user_id if (is_privileged and user_id) else (None if is_privileged else current_user.id)
    claims = store.get_all_claims(status=status, user_id=target_uid)
    if category_id:
        claims = [c for c in claims if c.get("category_id") == category_id]
    total_amount = sum(float(c.get("amount", 0)) for c in claims)
    return {"success": True, "data": claims, "total": len(claims), "total_amount": total_amount}


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
    """Create new expense claim. Requires: Authenticated user."""
    store = get_store()
    category = next((c for c in store.claim_categories if c["id"] == request.category_id), None)
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if request.amount > category["max_amount"]:
        raise HTTPException(
            status_code=400,
            detail=f"Amount exceeds max limit RM{category['max_amount']} for {category['name']}",
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
        "message": f"Claim RM{request.amount:.2f} submitted! 💰",
        "data": record,
    }


@router.patch("/{claim_id}/approve")
async def approve_claim(
    claim_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr),
):
    """Approve an expense claim. Requires: Manager or HR role."""
    store = get_store()
    claim = store.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["status"] != "pending":
        raise HTTPException(status_code=400, detail="Only pending claims can be approved")
    updated = store.update_claim_status(claim_id, "approved", actor_id=current_user.id)
    return {"success": True, "message": f"Claim RM{updated['amount']:.2f} approved! ✅", "data": updated}


@router.patch("/{claim_id}/reject")
async def reject_claim(
    claim_id: str,
    reason: Optional[str] = None,
    current_user: CurrentUser = Depends(require_manager_or_hr),
):
    """Reject an expense claim. Requires: Manager or HR role."""
    store = get_store()
    claim = store.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["status"] != "pending":
        raise HTTPException(status_code=400, detail="Only pending claims can be rejected")
    updated = store.update_claim_status(claim_id, "rejected", actor_id=current_user.id)
    return {"success": True, "message": "Claim rejected ❌", "data": updated}


# ================================================
# RECEIPT UPLOAD WITH OCR
# ================================================

@router.post("/{claim_id}/receipt")
async def upload_receipt(
    claim_id: str,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Upload receipt for a claim and extract data using OCR."""
    store = get_store()
    claim = store.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["user_id"] != current_user.id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Not authorized to upload receipt for this claim")
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not supported. Allowed: JPEG, PNG, PDF")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")
    ocr_service = get_ocr_service()
    receipt_data = await ocr_service.extract_receipt_data(content)
    response_data = {"claim_id": claim_id, "filename": file.filename, "ocr_result": receipt_data.to_dict()}
    if receipt_data.total_amount and claim.get("amount"):
        if abs(receipt_data.total_amount - float(claim.get("amount", 0))) > 0.01:
            response_data["suggestion"] = f"OCR detected RM{receipt_data.total_amount:.2f}, but claim amount is RM{claim.get('amount'):.2f}"
    return {"success": True, "message": "Receipt uploaded and processed! 📸", "data": response_data}


@router.post("/scan-receipt")
async def scan_receipt_only(
    file: UploadFile = File(...),
):
    """Scan a receipt without attaching to a claim."""
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Format tidak disokong: {file.content_type}")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File terlalu besar (max 10MB)")
    ocr_service = get_ocr_service()
    receipt_data = await ocr_service.extract_receipt_data(content)
    return {"success": True, "message": "Receipt scanned! 🔍", "data": receipt_data.to_dict()}
