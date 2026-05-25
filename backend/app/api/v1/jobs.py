"""
Job posting and candidate matching endpoints.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    require_recruiter_or_admin,
    get_current_user,
)
from app.db.models import User
from app.db.session import get_db
from app.schemas.job import (
    JobCreateRequest,
    JobResponse,
    MatchRequest,
    MatchResponse,
)
from app.services.job_service import JobService
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/jobs", tags=["Jobs & Matching"])


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job posting",
)
async def create_job(
    data: JobCreateRequest,
    current_user: Annotated[User, Depends(require_recruiter_or_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    service = JobService(db)
    recruiter = await service.get_recruiter_profile(current_user.id)
    job = await service.create_job(data, recruiter.id)
    return JobResponse.model_validate(job)


@router.get(
    "",
    response_model=list[JobResponse],
    summary="List all published job postings",
)
async def list_jobs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[JobResponse]:
    service = JobService(db)
    jobs = await service.list_jobs(status_filter="published")
    return [JobResponse.model_validate(job) for job in jobs]


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get a specific job posting",
)
async def get_job(
    job_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    service = JobService(db)
    job = await service.get_job(job_id)
    return JobResponse.model_validate(job)


@router.post(
    "/{job_id}/match",
    response_model=MatchResponse,
    summary="Run AI matching — rank candidates for a job",
)
async def match_candidates(
    job_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_recruiter_or_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    top_k: int = 10,
) -> MatchResponse:
    service = MatchingService(db)
    return await service.match_candidates_to_job(job_id, top_k=top_k)