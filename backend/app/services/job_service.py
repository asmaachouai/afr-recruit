"""
Job service — handles job posting CRUD for recruiters.
"""

import uuid
import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Job, Recruiter
from app.db.models.job import JobStatus, JobType
from app.schemas.job import JobCreateRequest

logger = structlog.get_logger(__name__)


class JobService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(
        self, data: JobCreateRequest, recruiter_id: uuid.UUID
    ) -> Job:
        job = Job(
            id=uuid.uuid4(),
            recruiter_id=recruiter_id,
            title=data.title,
            description=data.description,
            requirements=data.requirements,
            location=data.location,
            job_type=JobType(data.job_type),
            status=JobStatus.PUBLISHED,
            required_skills=data.required_skills,
            required_languages=data.required_languages,
            experience_years_min=data.experience_years_min,
            experience_years_max=data.experience_years_max,
            is_remote=data.is_remote,
            salary_min=data.salary_min,
            salary_max=data.salary_max,
            language=data.language,
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        logger.info("Job created", job_id=str(job.id), title=job.title)
        return job

    async def list_jobs(self, status_filter: str | None = None) -> list[Job]:
        query = select(Job).order_by(Job.created_at.desc())
        if status_filter:
            query = query.where(Job.status == JobStatus(status_filter))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_job(self, job_id: uuid.UUID) -> Job:
        result = await self.db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )
        return job

    async def get_recruiter_profile(
        self, user_id: uuid.UUID
    ) -> Recruiter:
        result = await self.db.execute(
            select(Recruiter).where(Recruiter.user_id == user_id)
        )
        recruiter = result.scalar_one_or_none()
        if not recruiter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recruiter profile not found",
            )
        return recruiter