"""
Fairness and bias detection schemas.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, field_validator
from typing import Any


class BiasSignal(BaseModel):
    signal_type: str        # language_bias, format_bias, origin_bias
    detected: bool
    confidence: float       # 0-1
    description: str
    recommendation: str


class FairnessMetrics(BaseModel):
    disparate_impact_ratio: float
    is_fair: bool           # True if ratio >= 0.8
    language_parity_score: float
    format_parity_score: float
    overall_fairness_score: float


class FairnessReportResponse(BaseModel):
    id: UUID
    application_id: UUID
    disparate_impact_ratio: float | None
    is_fair: bool | None
    language_bias_detected: bool
    format_bias_detected: bool
    origin_bias_detected: bool
    bias_signals: dict | None
    fairness_metrics: dict | None
    recommendations: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", "application_id", mode="before")
    @classmethod
    def convert_uuid(cls, v: Any) -> UUID:
        from uuid import UUID as _UUID
        if isinstance(v, _UUID):
            return v
        return _UUID(str(v))


class JobFairnessReport(BaseModel):
    job_id: str
    job_title: str
    total_applications: int
    flagged_applications: int
    overall_fair: bool
    disparate_impact_ratio: float
    language_distribution: dict[str, int]
    bias_summary: dict[str, int]
    recommendations: list[str]
    per_language_scores: dict[str, float]


class CandidateFairnessResponse(BaseModel):
    application_id: str
    is_fair: bool | None
    bias_detected: bool
    your_score: float | None
    adjusted_score: float | None
    bias_signals: list[BiasSignal]
    explanation: str
    recommendations: list[str]