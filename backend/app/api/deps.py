"""
FastAPI Dependencies untuk Authentication & Authorization.
Guna ni untuk protect routes! 🔐
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import logging

from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# Security scheme untuk Swagger UI
security = HTTPBearer(auto_error=False)


# ================================================
# USER MODEL
# ================================================

class CurrentUser:
    """Current authenticated user model."""
    
    def __init__(
        self,
        id: str,
        email: str,
        full_name: str = "",
        role: str = "employee",
        department: Optional[str] = None
    ):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.role = role
        self.department = department
    
    def has_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return self.role in roles
    
    def is_admin(self) -> bool:
        return self.role == "admin"
    
    def is_manager(self) -> bool:
        return self.role in ["manager", "admin"]
    
    def is_hr(self) -> bool:
        return self.role in ["hr", "admin"]


# ================================================
# AUTH DEPENDENCIES
# ================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    Validate JWT token and return current user.
    Use as dependency: user = Depends(get_current_user)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token diperlukan untuk access endpoint ni! 🔒",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    supabase = get_supabase_client()
    
    try:
        # Verify token with Supabase
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalid atau dah expired! 🚫",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_response.user
        
        # Get user profile with role
        profile_result = supabase.table("users").select(
            "id, email, full_name, role, department"
        ).eq("id", user.id).execute()
        
        if profile_result.data:
            profile = profile_result.data[0]
            return CurrentUser(
                id=profile["id"],
                email=profile.get("email", user.email),
                full_name=profile.get("full_name", ""),
                role=profile.get("role", "employee"),
                department=profile.get("department")
            )
        else:
            # User exists in auth but no profile yet
            return CurrentUser(
                id=user.id,
                email=user.email or "",
                full_name=user.user_metadata.get("full_name", ""),
                role="employee"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed! 🚫",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[CurrentUser]:
    """
    Optional auth - returns None if no token provided.
    Use for endpoints that work with or without auth.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# ================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ================================================

def require_roles(allowed_roles: List[str]):
    """
    Dependency factory untuk role-based access.
    Usage: Depends(require_roles(["admin", "hr"]))
    """
    async def role_checker(
        user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        if not user.has_role(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Kau tak ada permission untuk buat ni! 🚫 Perlu role: {', '.join(allowed_roles)}"
            )
        return user
    
    return role_checker


# Shortcut dependencies untuk common roles
require_admin = require_roles(["admin"])
require_manager = require_roles(["manager", "admin"])
require_hr = require_roles(["hr", "admin"])
require_manager_or_hr = require_roles(["manager", "hr", "admin"])
