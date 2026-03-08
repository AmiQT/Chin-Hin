"""FastAPI Dependencies untuk Authentication dan Authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

_TOKEN_STORE: dict = {}


def register_token(token: str, user_id: str, email: str, full_name: str, role: str = "employee"):
    _TOKEN_STORE[token] = {"id": user_id, "email": email, "full_name": full_name, "role": role}


def revoke_token(token: str):
    _TOKEN_STORE.pop(token, None)


class CurrentUser:
    def __init__(self, id: str, email: str, full_name: str = "", role: str = "employee", department: Optional[str] = None):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.role = role
        self.department = department

    def has_role(self, roles: List[str]) -> bool:
        return self.role in roles

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_manager(self) -> bool:
        return self.role in ["manager", "admin"]

    def is_hr(self) -> bool:
        return self.role in ["hr", "admin"]


_DEV_USER = CurrentUser(
    id="11111111-1111-1111-1111-111111111111",
    email="dev@chinhin.com",
    full_name="Dev Tester",
    role="admin",
)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> CurrentUser:
    settings = get_settings()
    if settings.dev_mode:
        logger.warning("DEV_MODE active - returning mock user!")
        return _DEV_USER
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token diperlukan untuk access endpoint ni!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    user_data = _TOKEN_STORE.get(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid atau dah expired!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return CurrentUser(
        id=user_data["id"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        role=user_data.get("role", "employee"),
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[CurrentUser]:
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_roles(allowed_roles: List[str]):
    async def role_checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.has_role(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tak ada permission. Perlu role: " + ", ".join(allowed_roles),
            )
        return user
    return role_checker


require_admin = require_roles(["admin"])
require_manager = require_roles(["manager", "admin"])
require_hr = require_roles(["hr", "admin"])
require_manager_or_hr = require_roles(["manager", "hr", "admin"])
