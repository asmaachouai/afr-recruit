"""
CV document schemas — request/response DTOs.
"""

from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, field_validator


class CVUploadResponse(BaseModel):
    id: str
    original_filename: str
    status: str
    detected_language: str | None
    message: str


class CVStatusResponse(BaseModel):
    id: UUID
    original_filename: str
    status: str
    detected_language: str | None
    ats_score: float | None
    ats_feedback: dict | None
    parsed_data: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, v: Any) -> UUID:
        """Accept both UUID objects and strings."""
        if isinstance(v, UUID):
            return v
        return UUID(str(v))

    @field_validator("status", mode="before")
    @classmethod
    def convert_status(cls, v: Any) -> str:
        """Accept enum values and return their string value."""
        if hasattr(v, "value"):
            return v.value
        return str(v)

    @field_validator("detected_language", mode="before")
    @classmethod
    def convert_language(cls, v: Any) -> str | None:
        """Accept enum values and return their string value."""
        if v is None:
            return None
        if hasattr(v, "value"):
            return v.value
        return str(v)


class ATSFeedback(BaseModel):
    score: float
    grade: str
    issues: list[str]
    suggestions: list[str]
    keyword_match_rate: float


class ParsedCVData(BaseModel):
    contact: dict[str, Any]
    skills: list[str]
    education: list[dict[str, Any]]
    experience: list[dict[str, Any]]
    languages: list[str]
    summary: str | None
    raw_sections: dict[str, str]