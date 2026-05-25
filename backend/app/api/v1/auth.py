"""
Authentication endpoints.
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
GET  /api/v1/auth/test/candidate-only
GET  /api/v1/auth/test/recruiter-only
GET  /api/v1/auth/test/admin-only
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    get_current_user,
    require_candidate,
    require_recruiter,
    require_admin,
)
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    RegisterResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new candidate or recruiter account",
)
async def register(
    data: UserRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RegisterResponse:
    service = AuthService(db)
    user = await service.register(data)
    return RegisterResponse(
        message="Account created successfully",
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            preferred_language=user.preferred_language,
            is_verified=user.is_verified,
        ),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT tokens",
)
async def login(
    data: UserLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    service = AuthService(db)
    return await service.login(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using refresh token",
)
async def refresh(
    data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and invalidate tokens",
)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    data: RefreshTokenRequest | None = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> None:
    service = AuthService(db)
    refresh_token = data.refresh_token if data else None
    await service.logout(credentials.credentials, refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        status=current_user.status.value,
        preferred_language=current_user.preferred_language,
        is_verified=current_user.is_verified,
    )


# ── RBAC Test Routes ─────────────────────────────────────────────────────────

@router.get(
    "/test/candidate-only",
    summary="RBAC test — candidates only",
    tags=["RBAC Tests"],
)
async def test_candidate_only(
    current_user: Annotated[User, Depends(require_candidate)],
):
    return {"message": f"Hello candidate {current_user.full_name}"}


@router.get(
    "/test/recruiter-only",
    summary="RBAC test — recruiters only",
    tags=["RBAC Tests"],
)
async def test_recruiter_only(
    current_user: Annotated[User, Depends(require_recruiter)],
):
    return {"message": f"Hello recruiter {current_user.full_name}"}


@router.get(
    "/test/admin-only",
    summary="RBAC test — admins only",
    tags=["RBAC Tests"],
)
async def test_admin_only(
    current_user: Annotated[User, Depends(require_admin)],
):
    return {"message": f"Hello admin {current_user.full_name}"}