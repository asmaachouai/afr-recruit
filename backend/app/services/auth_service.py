"""
Authentication service — handles registration, login, token refresh, logout.
"""

import uuid
from datetime import timedelta, datetime, timezone

import structlog
from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import blacklist_token, is_token_blacklisted
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.models import User, Candidate, Recruiter
from app.db.models.user import UserRole, UserStatus
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
)

logger = structlog.get_logger(__name__)


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserRegisterRequest) -> User:
        """Register a new user and create their profile."""

        # Check email uniqueness
        existing = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        # Create user
        user = User(
            id=uuid.uuid4(),
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=UserRole(data.role),
            status=UserStatus.ACTIVE,
            preferred_language=data.preferred_language,
        )
        self.db.add(user)
        await self.db.flush()  # get the user.id without committing

        # Create role-specific profile
        if user.role == UserRole.CANDIDATE:
            profile = Candidate(user_id=user.id)
            self.db.add(profile)
        elif user.role == UserRole.RECRUITER:
            profile = Recruiter(
                user_id=user.id,
                company_name="Not specified",
            )
            self.db.add(profile)

        await self.db.commit()
        await self.db.refresh(user)

        logger.info("User registered", email=user.email, role=user.role)
        return user

    async def login(self, data: UserLoginRequest) -> TokenResponse:
        """Authenticate a user and return JWT tokens."""

        # Find user by email
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive or suspended",
            )

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        logger.info("User logged in", email=user.email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Issue a new access token using a valid refresh token."""

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

        if await is_token_blacklisted(refresh_token):
            raise credentials_exception

        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise credentials_exception
            user_id: str = payload.get("sub")
        except JWTError:
            raise credentials_exception

        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()

        if not user or user.status != UserStatus.ACTIVE:
            raise credentials_exception

        new_access_token = create_access_token(subject=str(user.id))

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def logout(self, access_token: str, refresh_token: str | None = None) -> None:
        """Blacklist tokens to invalidate the session immediately."""
        try:
            payload = decode_token(access_token)
            exp = payload.get("exp", 0)
            ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
            await blacklist_token(access_token, ttl)
        except JWTError:
            pass

        if refresh_token:
            try:
                payload = decode_token(refresh_token)
                exp = payload.get("exp", 0)
                ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
                await blacklist_token(refresh_token, ttl)
            except JWTError:
                pass

        logger.info("User logged out")