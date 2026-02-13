"""Use case for user registration."""
import uuid
from typing import Optional

from sqlalchemy.exc import IntegrityError

from ...domain.entities.user import User
from ...infrastructure.persistence.repositories import UserRepository
from ...infrastructure.auth.jwt import (
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from ...infrastructure.auth.rbac import Role
from ...infrastructure.monitoring.logging import get_logger
from ..dtos.auth_dto import RegisterResponse, UserResponse

logger = get_logger("sortex.api.auth.register")


class RegisterUseCase:
    """Use case for user registration."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(
        self,
        email: str,
        password: str,
        requested_role: str = "viewer",
        caller_role: Optional[str] = None,
    ) -> RegisterResponse:
        """
        Register a new user and return tokens + user info.

        Raises:
            ValueError: If email already exists or role is invalid.
        """
        role = self._resolve_role(requested_role, caller_role)

        existing = self.user_repository.get_by_email(email)
        if existing:
            logger.warning("Registration failed: email already exists", email=email)
            raise ValueError("An account with this email already exists")

        password_hash = get_password_hash(password)
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=password_hash,
            role=role,
        )

        try:
            created_user = self.user_repository.create(user)
        except IntegrityError:
            logger.warning("Registration failed: duplicate email (race condition)", email=email)
            raise ValueError("An account with this email already exists")

        token_data = {
            "sub": str(created_user.id),
            "email": created_user.email,
            "role": created_user.role,
        }
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        logger.info(
            "User registered successfully",
            user_id=str(created_user.id),
            email=created_user.email,
            role=created_user.role,
        )

        return RegisterResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(
                id=created_user.id,
                email=created_user.email,
                role=created_user.role,
                created_at=created_user.created_at,
            ),
        )

    def _resolve_role(self, requested_role: str, caller_role: Optional[str]) -> str:
        """Resolve effective role. Only admins can assign non-viewer roles."""
        valid_roles = {r.value for r in Role}
        if requested_role not in valid_roles:
            raise ValueError(
                f"Invalid role '{requested_role}'. Must be one of: {', '.join(sorted(valid_roles))}"
            )

        if caller_role is None:
            return Role.VIEWER.value

        if caller_role == Role.ADMIN.value:
            return requested_role

        return Role.VIEWER.value
