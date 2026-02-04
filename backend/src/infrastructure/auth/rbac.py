from enum import Enum
from typing import List
from functools import wraps
from fastapi import HTTPException, status, Depends
from uuid import UUID
from ...api.middleware.auth import get_current_user


class Role(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


# Role permissions mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: ["*"],  # All permissions
    Role.OPERATOR: ["upload", "review", "export", "view"],
    Role.REVIEWER: ["review", "view"],
    Role.VIEWER: ["view"],
}


# Permission constants for type safety
class Permission:
    VIEW = "view"
    UPLOAD = "upload"
    REVIEW = "review"
    EXPORT = "export"
    ADMIN = "admin"


def has_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission"""
    try:
        role = Role(user_role)
    except ValueError:
        return False
    permissions = ROLE_PERMISSIONS.get(role, [])

    # Admin has all permissions
    if "*" in permissions:
        return True

    return required_permission in permissions


def get_permission_checker(permission: str):
    """
    FastAPI dependency factory for permission checking.

    Usage:
        @router.post("/documents")
        async def upload_document(
            current_user: dict = Depends(get_permission_checker("upload")),
        ):
    """
    async def permission_checker(
        credentials = Depends(lambda: None)  # Placeholder, will be replaced
    ):
        raise NotImplementedError("Use require_permission instead")

    async def _check_permission(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "viewer")
        if not has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required. Your role: '{user_role}'"
            )
        return current_user

    return _check_permission


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs (should be injected by auth middleware)
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = current_user.get("role")
            if not has_permission(user_role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

