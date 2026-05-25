"""
Matching service — orchestrates semantic search and ML ranking.
"""

import uuid
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models import Job, Candidate, CVDocument, Application, User
from app.db.models.job import JobStatus
from app.db.models.cv_document import CVStatus
from app.db.models.application import ApplicationStatus
from app.ml.models.embedding_service import embedding_service
from app.ml.models.vector_store import vector_store
from app.ml.models.ranking_model import ranking_model
from app.schemas.job import CandidateMatchResult, MatchResponse

logger = structlog.get_logger(__name__)


class MatchingService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def index_candidate_cv(
        self, candidate_id: uuid.UUID, cv_doc: CVDocument
    ) -> None:
        """
        Generate and store embedding for a candidate's CV.
        Called automatically after CV processing.
        """
        if not cv_doc.parsed_data:
            return

        cv_text = embedding_service.prepare_cv_text(cv_doc.parsed_data)
        embedding = embedding_service.embed_text(cv_text)
        vector_store.add_cv(str(candidate_id), embedding)

        logger.info("CV indexed", candidate_id=str(candidate_id))

    async def match_candidates_to_job(
        self, job_id: uuid.UUID, top_k: int = 10
    ) -> MatchResponse:
        """
        Find and rank the best candidates for a job posting.
        Two-stage: semantic search → ML reranking.
        """
        # Load job
        result = await self.db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        # Stage 1 — semantic search
        job_text = embedding_service.prepare_job_text(job)
        job_embedding = embedding_service.embed_text(job_text)
        similar_candidates = vector_store.search(job_embedding, top_k=top_k * 2)

        if not similar_candidates:
            return MatchResponse(
                job_id=str(job_id),
                job_title=job.title,
                total_candidates=0,
                matches=[],
            )

        # Stage 2 — ML reranking
        ranked_results = []

        for candidate_id_str, similarity_score in similar_candidates:
            try:
                candidate_uuid = uuid.UUID(candidate_id_str)

                # Load candidate and their best CV
                cand_result = await self.db.execute(
                    select(Candidate).where(Candidate.id == candidate_uuid)
                )
                candidate = cand_result.scalar_one_or_none()
                if not candidate:
                    continue

                # Load user for name/email
                user_result = await self.db.execute(
                    select(User).where(User.id == candidate.user_id)
                )
                user = user_result.scalar_one_or_none()
                if not user:
                    continue

                # Load best (most recent parsed) CV
                cv_result = await self.db.execute(
                    select(CVDocument)
                    .where(
                        CVDocument.candidate_id == candidate_uuid,
                        CVDocument.status == CVStatus.PARSED,
                    )
                    .order_by(CVDocument.created_at.desc())
                    .limit(1)
                )
                cv_doc = cv_result.scalar_one_or_none()
                parsed_data = cv_doc.parsed_data if cv_doc else {}
                ats_score = cv_doc.ats_score if cv_doc else None

                # Extract features and score
                features = ranking_model.extract_features(
                    similarity_score=similarity_score,
                    candidate_parsed_data=parsed_data or {},
                    job=job,
                    ats_score=ats_score,
                )
                final_score = ranking_model.score(features)
                explanation = ranking_model.explain(features)

                # Skills analysis
                candidate_skills = {
                    s.lower()
                    for s in (parsed_data.get("skills") or [])
                }
                required_skills = {
                    s.lower()
                    for s in (job.required_skills or [])
                }
                skills_matched = sorted(candidate_skills & required_skills)
                skills_missing = sorted(required_skills - candidate_skills)

                ranked_results.append({
                    "candidate_id": str(candidate_uuid),
                    "full_name": user.full_name,
                    "email": user.email,
                    "similarity_score": round(similarity_score, 4),
                    "ranking_score": final_score,
                    "skills_matched": skills_matched,
                    "skills_missing": skills_missing,
                    "experience_years": candidate.years_of_experience,
                    "detected_language": (
                        cv_doc.detected_language.value
                        if cv_doc and cv_doc.detected_language
                        else None
                    ),
                    "explanation": explanation,
                })

            except Exception as e:
                logger.warning(
                    "Failed to rank candidate",
                    candidate_id=candidate_id_str,
                    error=str(e),
                )
                continue

        # Sort by final ranking score descending
        ranked_results.sort(key=lambda x: x["ranking_score"], reverse=True)

        # Take top_k after reranking
        top_results = ranked_results[:top_k]

        # Assign rank positions
        matches = [
            CandidateMatchResult(rank_position=i + 1, **result)
            for i, result in enumerate(top_results)
        ]

        # Store application records and trigger fairness analysis
        await self._store_match_results(job_id, matches)

        return MatchResponse(
            job_id=str(job_id),
            job_title=job.title,
            total_candidates=len(ranked_results),
            matches=matches,
        )

    async def _store_match_results(
        self, job_id: uuid.UUID, matches: list[CandidateMatchResult]
    ) -> None:
        """
        Persist ranking results as Application records,
        then trigger fairness analysis on each application.
        """
        stored_application_ids = []

        for match in matches:
            candidate_uuid = uuid.UUID(match.candidate_id)

            # Check if application already exists
            existing = await self.db.execute(
                select(Application).where(
                    Application.candidate_id == candidate_uuid,
                    Application.job_id == job_id,
                )
            )
            app = existing.scalar_one_or_none()

            if app:
                app.similarity_score = match.similarity_score
                app.ranking_score = match.ranking_score
                app.rank_position = match.rank_position
                app.explanation = match.explanation
            else:
                app = Application(
                    id=uuid.uuid4(),
                    candidate_id=candidate_uuid,
                    job_id=job_id,
                    status=ApplicationStatus.SCREENING,
                    similarity_score=match.similarity_score,
                    ranking_score=match.ranking_score,
                    rank_position=match.rank_position,
                    explanation=match.explanation,
                )
                self.db.add(app)

            await self.db.flush()
            stored_application_ids.append(app.id)

        await self.db.commit()

        # Trigger fairness analysis for each application
        # Import here to avoid circular imports at module level
        from app.services.fairness_service import FairnessService

        fairness_service = FairnessService(self.db)

        for application_id in stored_application_ids:
            try:
                await fairness_service.analyze_application(application_id)
                logger.info(
                    "Fairness analysis completed",
                    application_id=str(application_id),
                )
            except Exception as e:
                logger.warning(
                    "Fairness analysis failed — non-fatal, continuing",
                    application_id=str(application_id),
                    error=str(e),
                )
