"""Use cases for authentication."""
from ...infrastructure.persistence.repositories import UserRepository
from ...infrastructure.auth.jwt import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ..dtos.auth_dto import TokenResponse


class LoginUseCase:
    """Use case for user login."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, email: str, password: str) -> TokenResponse:
        """Authenticate user and return tokens. Raises ValueError if credentials are invalid."""
        user = self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Incorrect email or password")

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


class RefreshTokenUseCase:
    """Use case for refreshing access token."""

    def execute(self, refresh_token: str) -> TokenResponse:
        """Validate refresh token and return new token pair. Raises ValueError if invalid."""
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        access_token = create_access_token(
            data={
                "sub": payload["sub"],
                "email": payload.get("email"),
                "role": payload.get("role"),
            }
        )
        new_refresh_token = create_refresh_token(
            data={
                "sub": payload["sub"],
                "email": payload.get("email"),
                "role": payload.get("role"),
            }
        )
        return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)
