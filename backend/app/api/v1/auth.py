"""Auth endpoints - mock local auth, no Supabase."""

import uuid
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.api.deps import register_token, revoke_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

_MOCK_USERS: dict = {
    "test@chinhin.com": {
        "password": "password123",
        "user_id": "11111111-1111-1111-1111-111111111111",
        "full_name": "Ahmad Fauzi",
        "role": "employee",
        "department": "Operations",
        "position": "Executive",
    },
    "admin@chinhin.com": {
        "password": "admin123",
        "user_id": "22222222-2222-2222-2222-222222222222",
        "full_name": "Siti Rahimah",
        "role": "admin",
        "department": "HR",
        "position": "HR Manager",
    },
    "hr@chinhin.com": {
        "password": "hr123",
        "user_id": "33333333-3333-3333-3333-333333333333",
        "full_name": "Razif Hamdan",
        "role": "hr",
        "department": "HR",
        "position": "HR Executive",
    },
}


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    success: bool = True
    message: str
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    full_name: Optional[str] = None


class LogoutRequest(BaseModel):
    access_token: str


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    if request.email in _MOCK_USERS:
        raise HTTPException(status_code=400, detail="Email dah didaftarkan!")
    user_id = str(uuid.uuid4())
    full_name = request.full_name or request.email.split("@")[0]
    _MOCK_USERS[request.email] = {"password": request.password, "user_id": user_id, "full_name": full_name, "role": "employee"}
    token = str(uuid.uuid4())
    register_token(token, user_id, request.email, full_name, "employee")
    logger.info(f"New user registered: {request.email}")
    return AuthResponse(message="Akaun berjaya dibuat!", user_id=user_id, access_token=token, full_name=full_name)


@router.post("/login", response_model=AuthResponse)
async def login(request: SignInRequest):
    user = _MOCK_USERS.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Email atau password salah!")
    token = str(uuid.uuid4())
    register_token(token, user["user_id"], request.email, user["full_name"], user.get("role", "employee"))
    logger.info(f"User logged in: {request.email}")
    return AuthResponse(message="Login berjaya!", user_id=user["user_id"], access_token=token, full_name=user["full_name"])


@router.post("/logout")
async def logout(request: LogoutRequest):
    revoke_token(request.access_token)
    return {"success": True, "message": "Logout berjaya!"}


@router.get("/me")
async def get_me():
    return {"success": True, "message": "Auth endpoint aktif"}
