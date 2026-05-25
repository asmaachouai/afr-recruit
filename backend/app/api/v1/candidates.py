"""
Candidate endpoints including CV upload and management.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import require_candidate
from app.db.models import User, Candidate
from app.db.session import get_db
from app.schemas.cv import CVUploadResponse, CVStatusResponse
from app.services.cv_service import CVService

router = APIRouter(prefix="/candidates", tags=["Candidates"])


async def get_candidate_profile(
    current_user: Annotated[User, Depends(require_candidate)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Candidate:
    """Get the candidate profile for the current user."""
    result = await db.execute(
        select(Candidate).where(Candidate.user_id == current_user.id)
    )
    return result.scalar_one_or_none()


@router.post(
    "/cv/upload",
    response_model=CVUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a CV for NLP processing",
)
async def upload_cv(
    file: Annotated[UploadFile, File(description="CV file — PDF, DOCX, or TXT")],
    current_user: Annotated[User, Depends(require_candidate)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CVUploadResponse:
    candidate = await get_candidate_profile(current_user, db)
    service = CVService(db)
    cv_doc = await service.upload_cv(file, candidate.id)

    return CVUploadResponse(
        id=str(cv_doc.id),
        original_filename=cv_doc.original_filename,
        status=cv_doc.status.value,
        detected_language=(
            cv_doc.detected_language.value
            if cv_doc.detected_language
            else None
        ),
        message="CV uploaded and processed successfully",
    )


@router.get(
    "/cv",
    response_model=list[CVStatusResponse],
    summary="List all uploaded CVs",
)
async def list_cvs(
    current_user: Annotated[User, Depends(require_candidate)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CVStatusResponse]:
    candidate = await get_candidate_profile(current_user, db)
    service = CVService(db)
    cvs = await service.list_cvs(candidate.id)
    return [CVStatusResponse.model_validate(cv) for cv in cvs]


@router.get(
    "/cv/{cv_id}",
    response_model=CVStatusResponse,
    summary="Get CV processing results and ATS score",
)
async def get_cv(
    cv_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_candidate)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CVStatusResponse:
    candidate = await get_candidate_profile(current_user, db)
    service = CVService(db)
    cv_doc = await service.get_cv(cv_id, candidate.id)
    return CVStatusResponse.model_validate(cv_doc)