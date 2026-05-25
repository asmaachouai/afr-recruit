"""
Import all models here so Alembic can discover them
and SQLAlchemy can resolve all relationships.
"""

from app.db.models.user import User, UserRole, UserStatus
from app.db.models.candidate import Candidate
from app.db.models.recruiter import Recruiter
from app.db.models.job import Job, JobStatus, JobType
from app.db.models.cv_document import CVDocument, CVStatus, CVLanguage
from app.db.models.application import Application, ApplicationStatus
from app.db.models.fairness_report import FairnessReport

__all__ = [
    "User", "UserRole", "UserStatus",
    "Candidate",
    "Recruiter",
    "Job", "JobStatus", "JobType",
    "CVDocument", "CVStatus", "CVLanguage",
    "Application", "ApplicationStatus",
    "FairnessReport",
]