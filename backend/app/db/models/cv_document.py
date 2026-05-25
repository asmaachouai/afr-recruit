"""
CVDocument model — stores uploaded CV files and their parsed content.
One candidate can have multiple CV versions.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CVStatus(str, PyEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PARSED = "parsed"
    FAILED = "failed"


class CVLanguage(str, PyEnum):
    ARABIC = "ar"
    FRENCH = "fr"
    ENGLISH = "en"
    MIXED = "mixed"


class CVDocument(Base):
    __tablename__ = "cv_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column()
    mime_type: Mapped[str | None] = mapped_column(String(100))

    # Processing state
    status: Mapped[CVStatus] = mapped_column(
        Enum(CVStatus), default=CVStatus.UPLOADED, index=True
    )
    detected_language: Mapped[CVLanguage | None] = mapped_column(Enum(CVLanguage))

    # NLP-extracted content stored as JSON
    raw_text: Mapped[str | None] = mapped_column(Text)
    parsed_data: Mapped[dict | None] = mapped_column(JSONB)
    # Structure: {skills, education, experience, contact, summary}

    # ATS compatibility score (0-100)
    ats_score: Mapped[float | None] = mapped_column(Float)
    ats_feedback: Mapped[dict | None] = mapped_column(JSONB)

    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship(back_populates="cv_documents")
    applications: Mapped[list["Application"]] = relationship(
        back_populates="cv_document"
    )

    def __repr__(self) -> str:
        return f"<CVDocument {self.original_filename} [{self.status}]>"