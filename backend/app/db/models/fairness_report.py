"""
FairnessReport model — stores bias detection results per application.
This is the ethical AI layer of the platform.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FairnessReport(Base):
    __tablename__ = "fairness_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Disparate impact ratio (>=0.8 is considered fair by the 4/5ths rule)
    disparate_impact_ratio: Mapped[float | None] = mapped_column(Float)
    is_fair: Mapped[bool | None] = mapped_column(Boolean)

    # Detected bias signals
    language_bias_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    format_bias_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    origin_bias_detected: Mapped[bool] = mapped_column(Boolean, default=False)

    # Detailed metrics stored as JSON
    bias_signals: Mapped[dict | None] = mapped_column(JSONB)
    fairness_metrics: Mapped[dict | None] = mapped_column(JSONB)
    recommendations: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    application: Mapped["Application"] = relationship(
        back_populates="fairness_report"
    )

    def __repr__(self) -> str:
        return f"<FairnessReport application={self.application_id} fair={self.is_fair}>"