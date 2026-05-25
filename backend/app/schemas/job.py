"""
Job posting schemas.
"""

from datetime import datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel, field_validator


class JobCreateRequest(BaseModel):
    title: str
    description: str
    requirements: str | None = None
    location: str | None = None
    job_type: str = "full_time"
    required_skills: list[str] = []
    required_languages: list[str] = ["fr"]
    experience_years_min: int | None = None
    experience_years_max: int | None = None
    is_remote: bool = False
    salary_min: int | None = None
    salary_max: int | None = None
    language: str = "fr"


class JobResponse(BaseModel):
    id: UUID
    title: str
    description: str
    requirements: str | None
    location: str | None
    job_type: str
    status: str
    required_skills: list[str] | None
    required_languages: list[str] | None
    experience_years_min: int | None
    is_remote: bool
    language: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("status", "job_type", mode="before")
    @classmethod
    def convert_enum(cls, v: Any) -> str:
        if hasattr(v, "value"):
            return v.value
        return str(v)

    @field_validator("required_skills", "required_languages", mode="before")
    @classmethod
    def convert_list(cls, v: Any) -> list:
        if v is None:
            return []
        return v


class MatchRequest(BaseModel):
    job_id: UUID
    top_k: int = 10


class CandidateMatchResult(BaseModel):
    candidate_id: str
    full_name: str
    email: str
    similarity_score: float
    ranking_score: float
    rank_position: int
    skills_matched: list[str]
    skills_missing: list[str]
    experience_years: int | None
    detected_language: str | None
    explanation: str


class MatchResponse(BaseModel):
    job_id: str
    job_title: str
    total_candidates: int
    matches: list[CandidateMatchResult]