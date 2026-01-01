from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ...infrastructure.auth.jwt import (
    create_access_token, create_refresh_token, verify_password, get_password_hash
)
from ...infrastructure.persistence.database import Database
from ...infrastructure.persistence.models import UserModel
import os

router = APIRouter()
database_url = os.getenv("DATABASE_URL", "postgresql://docflow:docflow@localhost:5432/docflow")
db = Database(database_url)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Login and get JWT tokens"""
    session = db.get_session()
    try:
        user = session.query(UserModel).filter(UserModel.email == login_data.email).first()
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    finally:
        session.close()


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    from ...infrastructure.auth.jwt import decode_token
    
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    access_token = create_access_token(data={"sub": payload["sub"], "email": payload.get("email"), "role": payload.get("role")})
    new_refresh_token = create_refresh_token(data={"sub": payload["sub"], "email": payload.get("email"), "role": payload.get("role")})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )

