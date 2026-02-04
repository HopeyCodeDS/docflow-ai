from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session

from ...application.use_cases.login import LoginUseCase, RefreshTokenUseCase
from ...application.dtos.auth_dto import LoginRequest, TokenResponse, RefreshRequest
from ...infrastructure.persistence.repositories import UserRepository
from ...api.dependencies import get_db_session
from ...api.middleware.rate_limit import rate_limit_login, rate_limit_refresh

router = APIRouter()


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
