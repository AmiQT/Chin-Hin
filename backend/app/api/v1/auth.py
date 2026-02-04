from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from app.db.supabase_client import get_supabase_client

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


# ================================================
# REQUEST/RESPONSE MODELS
# ================================================

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


# ================================================
# AUTH ENDPOINTS
# ================================================

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """
    Register a new user with email and password.
    Profile will be auto-created via database trigger.
    """
    supabase = get_supabase_client()
    
    try:
        # Sign up with Supabase Auth
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name or request.email.split("@")[0]
                }
            }
        })
        
        if response.user:
            logger.info(f"✅ New user registered: {request.email}")
            return AuthResponse(
                message="Account created! 🎉 Check email untuk verify.",
                user_id=response.user.id,
                access_token=response.session.access_token if response.session else None
            )
        else:
            raise HTTPException(status_code=400, detail="Signup failed")
            
    except Exception as e:
        logger.error(f"❌ Signup error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: SignInRequest):
    """
    Sign in with email and password.
    Returns access token for authenticated requests.
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.user and response.session:
            logger.info(f"✅ User logged in: {request.email}")
            return AuthResponse(
                message="Login successful! 🚀",
                user_id=response.user.id,
                access_token=response.session.access_token
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post("/logout")
async def logout():
    """
    Sign out current user.
    Note: For stateless JWT, client should discard the token.
    """
    supabase = get_supabase_client()
    
    try:
        supabase.auth.sign_out()
        return {
            "success": True,
            "message": "Logged out successfully! 👋"
        }
    except Exception as e:
        logger.error(f"❌ Logout error: {str(e)}")
        return {
            "success": True,
            "message": "Logged out 👋"
        }


@router.get("/me")
async def get_current_user(authorization: Optional[str] = None):
    """
    Get current user profile from token.
    Pass token in Authorization header as 'Bearer <token>'.
    """
    supabase = get_supabase_client()
    
    try:
        # Get user from current session
        user_response = supabase.auth.get_user()
        
        if user_response and user_response.user:
            user = user_response.user
            
            # Get profile from users table
            profile_result = supabase.table("users").select("*").eq("id", user.id).execute()
            
            profile = profile_result.data[0] if profile_result.data else {
                "id": user.id,
                "email": user.email,
                "full_name": user.user_metadata.get("full_name", "Unknown")
            }
            
            return {
                "success": True,
                "data": profile
            }
        else:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
    except Exception as e:
        logger.error(f"❌ Get user error: {str(e)}")
        raise HTTPException(status_code=401, detail="Not authenticated")
