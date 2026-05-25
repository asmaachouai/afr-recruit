"""
Authentication schemas — request/response DTOs for auth endpoints.
"""

from pydantic import BaseModel, EmailStr, field_validator
import re


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "candidate"
    preferred_language: str = "fr"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        if v not in ("candidate", "recruiter"):
            raise ValueError("Role must be candidate or recruiter")
        return v

    @field_validator("preferred_language")
    @classmethod
    def valid_language(cls, v: str) -> str:
        if v not in ("fr", "ar", "en"):
            raise ValueError("Language must be fr, ar, or en")
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    status: str
    preferred_language: str
    is_verified: bool

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse