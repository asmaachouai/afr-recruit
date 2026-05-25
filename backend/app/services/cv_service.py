"""
CV service — handles upload, storage, and orchestrates NLP processing.
"""

import uuid
import mimetypes
from pathlib import Path

import structlog
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.models import CVDocument, Candidate
from app.db.models.cv_document import CVStatus, CVLanguage
from app.ml.preprocessing.text_extractor import TextExtractor
from app.ml.preprocessing.language_detector import LanguageDetector
from app.ml.preprocessing.nlp_extractor import NLPExtractor
from app.ml.preprocessing.ats_scorer import ATSScorer

logger = structlog.get_logger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
}
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


class CVService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.text_extractor = TextExtractor()
        self.language_detector = LanguageDetector()
        self.nlp_extractor = NLPExtractor()
        self.ats_scorer = ATSScorer()

    async def upload_cv(
        self, file: UploadFile, candidate_id: uuid.UUID
    ) -> CVDocument:
        """
        Validate, store, and begin processing a CV file.
        Returns the CVDocument with status=PROCESSING.
        """
        # Validate candidate exists
        result = await self.db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate profile not found",
            )

        # Read file content
        file_bytes = await file.read()

        # Validate file size
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB",
            )

        # Validate file extension
        original_filename = file.filename or "cv"
        ext = Path(original_filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type. Allowed: PDF, DOCX, TXT",
            )

        # Determine MIME type
        mime_type = file.content_type
        if not mime_type or mime_type == "application/octet-stream":
            mime_type, _ = mimetypes.guess_type(original_filename)
            mime_type = mime_type or "application/octet-stream"

        # Store file securely with UUID name
        stored_filename = f"{uuid.uuid4()}{ext}"
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / stored_filename

        file_path.write_bytes(file_bytes)

        # Create CVDocument record
        cv_doc = CVDocument(
            id=uuid.uuid4(),
            candidate_id=candidate_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_size_bytes=len(file_bytes),
            mime_type=mime_type,
            status=CVStatus.PROCESSING,
        )
        self.db.add(cv_doc)
        await self.db.commit()
        await self.db.refresh(cv_doc)

        # Process synchronously for now
        # In Phase 13 this will become an async Celery task
        await self.process_cv(cv_doc.id, file_bytes, mime_type, original_filename)

        await self.db.refresh(cv_doc)
        return cv_doc

    async def process_cv(
        self,
        cv_id: uuid.UUID,
        file_bytes: bytes,
        mime_type: str,
        filename: str,
    ) -> None:
        """
        Run the full NLP pipeline on a CV.
        Updates the CVDocument with extracted data and ATS score.
        """
        result = await self.db.execute(
            select(CVDocument).where(CVDocument.id == cv_id)
        )
        cv_doc = result.scalar_one_or_none()
        if not cv_doc:
            return

        try:
            # Step 1: Extract text
            raw_text = self.text_extractor.extract(file_bytes, mime_type, filename)

            # Step 2: Detect language
            language = self.language_detector.detect(raw_text)

            # Step 3: Extract structured data with NLP
            parsed_data = self.nlp_extractor.extract(raw_text, language)

            # Step 4: Score ATS compatibility
            ats_result = self.ats_scorer.score(parsed_data, raw_text)

            # Step 5: Update CVDocument
            cv_doc.raw_text = raw_text[:50000]  # store first 50k chars
            cv_doc.detected_language = CVLanguage(language) if language in [
                e.value for e in CVLanguage
            ] else CVLanguage.MIXED
            cv_doc.parsed_data = parsed_data
            cv_doc.ats_score = ats_result.score
            cv_doc.ats_feedback = {
                "score": ats_result.score,
                "grade": ats_result.grade,
                "issues": ats_result.issues,
                "suggestions": ats_result.suggestions,
                "keyword_match_rate": ats_result.keyword_match_rate,
                "section_scores": ats_result.section_scores,
            }
            cv_doc.status = CVStatus.PARSED

            # Step 6: Update candidate profile with extracted skills
            candidate_result = await self.db.execute(
                select(Candidate).where(Candidate.id == cv_doc.candidate_id)
            )
            candidate = candidate_result.scalar_one_or_none()
            if candidate and parsed_data.get("skills"):
                candidate.skills = parsed_data["skills"][:20]

            await self.db.commit()
            logger.info(
                "CV processed successfully",
                cv_id=str(cv_id),
                language=language,
                ats_score=ats_result.score,
            )

        except Exception as e:
            cv_doc.status = CVStatus.FAILED
            await self.db.commit()
            logger.error("CV processing failed", cv_id=str(cv_id), error=str(e))
            raise

    async def get_cv(self, cv_id: uuid.UUID, candidate_id: uuid.UUID) -> CVDocument:
        """Get a CV document, ensuring it belongs to the requesting candidate."""
        result = await self.db.execute(
            select(CVDocument).where(
                CVDocument.id == cv_id,
                CVDocument.candidate_id == candidate_id,
            )
        )
        cv_doc = result.scalar_one_or_none()
        if not cv_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found",
            )
        return cv_doc

    async def list_cvs(self, candidate_id: uuid.UUID) -> list[CVDocument]:
        """List all CVs for a candidate."""
        result = await self.db.execute(
            select(CVDocument)
            .where(CVDocument.candidate_id == candidate_id)
            .order_by(CVDocument.created_at.desc())
        )
        return list(result.scalars().all())