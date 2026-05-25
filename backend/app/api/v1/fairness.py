"""
Fairness and bias detection endpoints.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    require_recruiter_or_admin,
    require_candidate,
    get_current_user,
)
from app.db.models import User, Candidate
from app.db.session import get_db
from app.schemas.fairness import (
    FairnessReportResponse,
    JobFairnessReport,
    CandidateFairnessResponse,
)
from app.services.fairness_service import FairnessService

router = APIRouter(prefix="/fairness", tags=["Fairness & Bias Detection"])


@router.post(
    "/analyze/{application_id}",
    response_model=FairnessReportResponse,
    summary="Run bias detection on a specific application",
)
async def analyze_application(
    application_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_recruiter_or_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FairnessReportResponse:
    service = FairnessService(db)
    report = await service.analyze_application(application_id)
    return FairnessReportResponse.model_validate(report)


@router.get(
    "/job/{job_id}",
    response_model=JobFairnessReport,
    summary="Get full fairness audit report for a job posting",
)
async def get_job_fairness_report(
    job_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_recruiter_or_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobFairnessReport:
    service = FairnessService(db)
    return await service.get_job_fairness_report(job_id)


@router.get(
    "/my-application/{application_id}",
    response_model=CandidateFairnessResponse,
    summary="Get fairness report for your own application",
)
async def get_my_application_fairness(
    application_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_candidate)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CandidateFairnessResponse:
    # Get candidate profile
    result = await db.execute(
        select(Candidate).where(Candidate.user_id == current_user.id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found",
        )

    service = FairnessService(db)
    return await service.get_candidate_fairness(
        application_id, candidate.id
    )


@router.post(
    "/job/{job_id}/analyze-all",
    response_model=JobFairnessReport,
    summary="Run bias detection on all applications for a job",
)
async def analyze_all_applications(
    job_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_recruiter_or_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobFairnessReport:
    """
    Runs bias detection on every application for this job
    and returns the aggregated fairness report.
    """
    from sqlalchemy import select
    from app.db.models import Application

    # Get all applications for this job
    apps_result = await db.execute(
        select(Application).where(Application.job_id == job_id)
    )
    applications = list(apps_result.scalars().all())

    # Analyze each application
    service = FairnessService(db)
    for app in applications:
        try:
            await service.analyze_application(app.id)
        except Exception as e:
            import structlog
            log = structlog.get_logger()
            log.warning(
                "Failed to analyze application",
                application_id=str(app.id),
                error=str(e),
            )

    # Return aggregated report
    return await service.get_job_fairness_report(job_id)