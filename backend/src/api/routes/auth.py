from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session

from ...application.use_cases.login import LoginUseCase, RefreshTokenUseCase
from ...application.use_cases.register import RegisterUseCase
from ...application.dtos.auth_dto import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
)
from ...infrastructure.persistence.repositories import UserRepository
from ...api.dependencies import get_db_session
from ...api.middleware.rate_limit import rate_limit_login, rate_limit_refresh, rate_limit_register
from ...api.middleware.auth import get_optional_user

router = APIRouter()


@router.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    register_data: RegisterRequest,
    session: Session = Depends(get_db_session),
    _: None = Depends(rate_limit_register),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Register a new user account. Returns tokens for auto-login."""
    user_repo = UserRepository(session)
    use_case = RegisterUseCase(user_repository=user_repo)
    try:
        result = use_case.execute(
            email=register_data.email,
            password=register_data.password,
            requested_role=register_data.role,
            caller_role=current_user.get("role") if current_user else None,
        )
        session.commit()
        return result
    except ValueError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    session: Session = Depends(get_db_session),
    _: None = Depends(rate_limit_login),
):
    """Login and get JWT tokens"""
    user_repo = UserRepository(session)
    use_case = LoginUseCase(user_repository=user_repo)
    try:
        return use_case.execute(login_data.email, login_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    body: RefreshRequest,
    _: None = Depends(rate_limit_refresh),
):
    """Refresh access token"""
    use_case = RefreshTokenUseCase()
    try:
        return use_case.execute(body.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
