"""
Recruiter model — company/HR profile linked to a User.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Recruiter(Base):
    __tablename__ = "recruiters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    company_name: Mapped[str] = mapped_column(String(300), nullable=False)
    company_website: Mapped[str | None] = mapped_column(String(500))
    company_description: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(String(200))
    company_size: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100), default="Morocco")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="recruiter_profile")
    jobs: Mapped[list["Job"]] = relationship(
        back_populates="recruiter", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Recruiter {self.company_name}>"