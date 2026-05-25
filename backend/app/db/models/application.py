"""
Application model — links a Candidate to a Job.
Stores matching scores, ranking, and fairness analysis results.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ApplicationStatus(str, PyEnum):
    SUBMITTED = "submitted"
    SCREENING = "screening"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cv_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cv_documents.id", ondelete="SET NULL"),
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.SUBMITTED,
        index=True,
    )

    # ML scoring results
    similarity_score: Mapped[float | None] = mapped_column(Float)
    ranking_score: Mapped[float | None] = mapped_column(Float)
    rank_position: Mapped[int | None] = mapped_column()

    # Explainability — SHAP values and human-readable explanation
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB)
    explanation: Mapped[str | None] = mapped_column(Text)

    # Recruiter notes
    recruiter_notes: Mapped[str | None] = mapped_column(Text)

    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship(back_populates="applications")
    cv_document: Mapped["CVDocument"] = relationship(back_populates="applications")
    fairness_report: Mapped["FairnessReport"] = relationship(
        back_populates="application", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Application {self.candidate_id} → {self.job_id} [{self.status}]>"