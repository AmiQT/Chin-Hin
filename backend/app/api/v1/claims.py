from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Optional
from datetime import date
from pydantic import BaseModel
import base64

from app.db.supabase_client import get_supabase_client
from app.api.deps import get_current_user, require_manager_or_hr, CurrentUser
from app.services.ocr_service import get_ocr_service

router = APIRouter(prefix="/claims", tags=["Expense Claims"])


class ClaimRequest(BaseModel):
    user_id: str
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
    supabase = get_supabase_client()
    result = supabase.table("claim_categories").select("*").execute()
    
    return {
        "success": True,
        "data": result.data
    }


# ================================================
# CLAIMS
# ================================================

@router.get("")
async def get_claims(
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    category_id: Optional[str] = None
):
    """
    Get all claims dengan optional filters.
    Status: pending, approved, rejected
    """
    supabase = get_supabase_client()
    query = supabase.table("claims").select(
        "*, users(full_name), claim_categories(name)"
    )
    
    if status:
        query = query.eq("status", status)
    
    if user_id:
        query = query.eq("user_id", user_id)
    
    if category_id:
        query = query.eq("category_id", category_id)
    
    result = query.execute()
    
    # Flatten response and calculate total
    claims = []
    total_amount = 0.0
    for claim in result.data:
        claim_data = {**claim}
        if claim_data.get("users"):
            claim_data["user_name"] = claim_data["users"]["full_name"]
            del claim_data["users"]
        if claim_data.get("claim_categories"):
            claim_data["category_name"] = claim_data["claim_categories"]["name"]
            del claim_data["claim_categories"]
        claims.append(claim_data)
        total_amount += float(claim_data.get("amount", 0))
    
    return {
        "success": True,
        "data": claims,
        "total": len(claims),
        "total_amount": total_amount
    }


@router.get("/{claim_id}")
async def get_claim(claim_id: str):
    """Get single claim by ID."""
    supabase = get_supabase_client()
    result = supabase.table("claims").select(
        "*, users(full_name), claim_categories(name)"
    ).eq("id", claim_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim = result.data[0]
    if claim.get("users"):
        claim["user_name"] = claim["users"]["full_name"]
        del claim["users"]
    if claim.get("claim_categories"):
        claim["category_name"] = claim["claim_categories"]["name"]
        del claim["claim_categories"]
    
    return {
        "success": True,
        "data": claim
    }


@router.post("")
async def create_claim(
    request: ClaimRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Create new expense claim.
    Requires: Authenticated user
    """
    supabase = get_supabase_client()
    
    # Use current user's ID for security
    user_id = current_user.id
    
    # Check category exists and get max amount
    cat_result = supabase.table("claim_categories").select("*").eq("id", request.category_id).execute()
    if not cat_result.data:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    category = cat_result.data[0]
    max_amount = float(category.get("max_amount", 9999))
    
    if request.amount > max_amount:
        raise HTTPException(
            status_code=400, 
            detail=f"Amount exceeds max limit RM{max_amount} for {category.get('name')}"
        )
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    new_claim = {
        "user_id": user_id,  # Use authenticated user's ID
        "category_id": request.category_id,
        "amount": request.amount,
        "description": request.description,
        "claim_date": (request.claim_date or date.today()).isoformat(),
        "status": "pending"
    }
    
    result = supabase.table("claims").insert(new_claim).execute()
    
    return {
        "success": True,
        "message": f"Claim RM{request.amount:.2f} submitted! 💰",
        "data": result.data[0] if result.data else new_claim
    }


@router.patch("/{claim_id}/approve")
async def approve_claim(
    claim_id: str,
    current_user: CurrentUser = Depends(require_manager_or_hr)
):
    """
    Approve an expense claim.
    Requires: Manager or HR role
    """
    supabase = get_supabase_client()
    
    claim_result = supabase.table("claims").select("*").eq("id", claim_id).execute()
    if not claim_result.data:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim_result.data[0].get("status") != "pending":
        raise HTTPException(status_code=400, detail="Only pending claims can be approved")
    
    result = supabase.table("claims").update({
        "status": "approved",
        "approved_by": current_user.id
    }).eq("id", claim_id).execute()
    amount = result.data[0].get("amount", 0) if result.data else 0
    
    return {
        "success": True,
        "message": f"Claim RM{amount:.2f} approved! ✅",
        "data": result.data[0] if result.data else None
    }


@router.patch("/{claim_id}/reject")
async def reject_claim(
    claim_id: str,
    reason: Optional[str] = None,
    current_user: CurrentUser = Depends(require_manager_or_hr)
):
    """
    Reject an expense claim.
    Requires: Manager or HR role
    """
    supabase = get_supabase_client()
    
    claim_result = supabase.table("claims").select("*").eq("id", claim_id).execute()
    if not claim_result.data:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim_result.data[0].get("status") != "pending":
        raise HTTPException(status_code=400, detail="Only pending claims can be rejected")
    
    result = supabase.table("claims").update({
        "status": "rejected",
        "rejected_by": current_user.id
    }).eq("id", claim_id).execute()
    
    return {
        "success": True,
        "message": "Claim rejected ❌",
        "data": result.data[0] if result.data else None
    }


# ================================================
# RECEIPT UPLOAD WITH OCR
# ================================================

@router.post("/{claim_id}/receipt")
async def upload_receipt(
    claim_id: str,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Upload receipt for a claim and extract data using OCR.
    
    Supported formats: JPEG, PNG, PDF
    Max size: 10MB
    """
    supabase = get_supabase_client()
    
    # Verify claim exists and belongs to user
    claim_result = supabase.table("claims").select("*").eq("id", claim_id).execute()
    if not claim_result.data:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim = claim_result.data[0]
    if claim.get("user_id") != current_user.id and current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Not authorized to upload receipt for this claim")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not supported. Allowed: JPEG, PNG, PDF"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size (10MB max)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")
    
    # Perform OCR
    ocr_service = get_ocr_service()
    receipt_data = await ocr_service.extract_receipt_data(content)
    
    # Store receipt data in claim
    # For now, store base64 encoded image (in production, use Supabase Storage)
    receipt_base64 = base64.b64encode(content).decode('utf-8')
    
    update_data = {
        "receipt_url": f"data:{file.content_type};base64,{receipt_base64[:100]}...",  # Truncated for DB
        "receipt_data": receipt_data.to_dict()
    }
    
    # Auto-fill amount if OCR detected it and claim has no amount
    if receipt_data.total_amount and not claim.get("amount"):
        update_data["amount"] = receipt_data.total_amount
    
    result = supabase.table("claims").update(update_data).eq("id", claim_id).execute()
    
    response_data = {
        "claim_id": claim_id,
        "filename": file.filename,
        "ocr_result": receipt_data.to_dict()
    }
    
    # Add suggestion if OCR found different amount
    if receipt_data.total_amount and claim.get("amount"):
        if abs(receipt_data.total_amount - float(claim.get("amount", 0))) > 0.01:
            response_data["suggestion"] = f"OCR detected RM{receipt_data.total_amount:.2f}, but claim amount is RM{claim.get('amount'):.2f}"
    
    return {
        "success": True,
        "message": f"Receipt uploaded and processed! 📸",
        "data": response_data
    }


@router.post("/scan-receipt")
async def scan_receipt_only(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Scan a receipt without attaching to a claim.
    Useful for previewing OCR results before creating claim.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not supported. Allowed: JPEG, PNG, PDF"
        )
    
    # Read and process
    content = await file.read()
    
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")
    
    # Perform OCR
    ocr_service = get_ocr_service()
    receipt_data = await ocr_service.extract_receipt_data(content)
    
    return {
        "success": True,
        "message": "Receipt scanned! 🔍",
        "data": receipt_data.to_dict()
    }
