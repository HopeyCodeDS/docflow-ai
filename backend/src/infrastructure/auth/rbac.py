from enum import Enum
from typing import List
from functools import wraps
from fastapi import HTTPException, status
from uuid import UUID


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


def has_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission"""
    role = Role(user_role)
    permissions = ROLE_PERMISSIONS.get(role, [])
    
    # Admin has all permissions
    if "*" in permissions:
        return True
    
    return required_permission in permissions


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

