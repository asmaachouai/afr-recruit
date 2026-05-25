# backend/app/schemas/__init__.py
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    RegisterResponse,
)
from app.schemas.cv import CVUploadResponse, CVStatusResponse
from app.schemas.job import (
    JobCreateRequest,
    JobResponse,
    MatchRequest,
    MatchResponse,
    CandidateMatchResult,
)

__all__ = [
    "UserRegisterRequest", "UserLoginRequest", "TokenResponse",
    "RefreshTokenRequest", "UserResponse", "RegisterResponse",
    "CVUploadResponse", "CVStatusResponse",
    "JobCreateRequest", "JobResponse",
    "MatchRequest", "MatchResponse", "CandidateMatchResult",
]