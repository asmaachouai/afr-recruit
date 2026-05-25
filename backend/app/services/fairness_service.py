"""
Fairness service — orchestrates bias detection and fairness reporting.
"""

import uuid
import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Application, FairnessReport, CVDocument, Job, User, Candidate
)
from app.db.models.cv_document import CVStatus
from app.ml.preprocessing.bias_detector import BiasDetector
from app.ml.preprocessing.fairness_analyzer import FairnessAnalyzer
from app.schemas.fairness import (
    FairnessReportResponse,
    JobFairnessReport,
    CandidateFairnessResponse,
    BiasSignal,
)

logger = structlog.get_logger(__name__)


class FairnessService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.bias_detector = BiasDetector()
        self.fairness_analyzer = FairnessAnalyzer()

    async def analyze_application(
        self, application_id: uuid.UUID
    ) -> FairnessReport:
        """
        Run bias detection on a single application.
        Creates or updates the FairnessReport for this application.
        """
        # Load application
        app_result = await self.db.execute(
            select(Application).where(Application.id == application_id)
        )
        application = app_result.scalar_one_or_none()
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        # Load CV
        cv_result = await self.db.execute(
            select(CVDocument).where(
                CVDocument.candidate_id == application.candidate_id,
                CVDocument.status == CVStatus.PARSED,
            ).order_by(CVDocument.created_at.desc()).limit(1)
        )
        cv_doc = cv_result.scalar_one_or_none()

        raw_text = cv_doc.raw_text or "" if cv_doc else ""
        detected_language = (
            cv_doc.detected_language.value
            if cv_doc and cv_doc.detected_language
            else "fr"
        )
        ats_score = cv_doc.ats_score or 0.0 if cv_doc else 0.0
        parsed_data = cv_doc.parsed_data or {} if cv_doc else {}

        # Run bias detection
        bias_result = self.bias_detector.detect(
            raw_text=raw_text,
            detected_language=detected_language,
            ats_score=ats_score,
            parsed_data=parsed_data,
            ranking_score=application.ranking_score,
        )

        # Compute fairness metrics for this application
        fairness_metrics = self.fairness_analyzer.analyze_single_application(
            ranking_score=application.ranking_score or 0.0,
            detected_language=detected_language,
            language_bias_detected=bias_result.language_bias_detected,
            format_bias_detected=bias_result.format_bias_detected,
            origin_bias_detected=bias_result.origin_bias_detected,
        )

        # Check if report exists
        existing_result = await self.db.execute(
            select(FairnessReport).where(
                FairnessReport.application_id == application_id
            )
        )
        report = existing_result.scalar_one_or_none()

        recommendations_text = "\n".join(bias_result.recommendations)

        if report:
            # Update existing report
            report.disparate_impact_ratio = fairness_metrics["disparate_impact_ratio"]
            report.is_fair = fairness_metrics["is_fair"]
            report.language_bias_detected = bias_result.language_bias_detected
            report.format_bias_detected = bias_result.format_bias_detected
            report.origin_bias_detected = bias_result.origin_bias_detected
            report.bias_signals = {
                "signals": bias_result.bias_signals,
                "overall_bias_score": bias_result.overall_bias_score,
            }
            report.fairness_metrics = fairness_metrics
            report.recommendations = recommendations_text
        else:
            report = FairnessReport(
                id=uuid.uuid4(),
                application_id=application_id,
                disparate_impact_ratio=fairness_metrics["disparate_impact_ratio"],
                is_fair=fairness_metrics["is_fair"],
                language_bias_detected=bias_result.language_bias_detected,
                format_bias_detected=bias_result.format_bias_detected,
                origin_bias_detected=bias_result.origin_bias_detected,
                bias_signals={
                    "signals": bias_result.bias_signals,
                    "overall_bias_score": bias_result.overall_bias_score,
                },
                fairness_metrics=fairness_metrics,
                recommendations=recommendations_text,
            )
            self.db.add(report)

        await self.db.commit()
        await self.db.refresh(report)

        logger.info(
            "Fairness report generated",
            application_id=str(application_id),
            is_fair=report.is_fair,
            language_bias=report.language_bias_detected,
        )
        return report

    async def get_job_fairness_report(
        self, job_id: uuid.UUID
    ) -> JobFairnessReport:
        """
        Generate a fairness report for all applications to a job.
        Used by recruiters to audit their hiring process.
        """
        # Load job
        job_result = await self.db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = job_result.scalar_one_or_none()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        # Load all applications for this job
        apps_result = await self.db.execute(
            select(Application).where(Application.job_id == job_id)
        )
        applications = list(apps_result.scalars().all())

        if not applications:
            return JobFairnessReport(
                job_id=str(job_id),
                job_title=job.title,
                total_applications=0,
                flagged_applications=0,
                overall_fair=True,
                disparate_impact_ratio=1.0,
                language_distribution={},
                bias_summary={},
                recommendations=["No applications to analyze yet."],
                per_language_scores={},
            )

        # Run bias analysis on all applications
        # and collect data for pool-level analysis
        candidate_data = []
        language_distribution: dict[str, int] = {}
        bias_summary = {
            "language_bias": 0,
            "format_bias": 0,
            "origin_bias": 0,
        }
        per_language_scores: dict[str, list[float]] = {}
        flagged_count = 0

        for app in applications:
            # Load CV for language info
            cv_result = await self.db.execute(
                select(CVDocument).where(
                    CVDocument.candidate_id == app.candidate_id,
                    CVDocument.status == CVStatus.PARSED,
                ).order_by(CVDocument.created_at.desc()).limit(1)
            )
            cv_doc = cv_result.scalar_one_or_none()

            detected_language = (
                cv_doc.detected_language.value
                if cv_doc and cv_doc.detected_language
                else "unknown"
            )
            raw_text = cv_doc.raw_text or "" if cv_doc else ""
            ats_score = cv_doc.ats_score or 0.0 if cv_doc else 0.0
            parsed_data = cv_doc.parsed_data or {} if cv_doc else {}

            # Run bias detection
            bias_result = self.bias_detector.detect(
                raw_text=raw_text,
                detected_language=detected_language,
                ats_score=ats_score,
                parsed_data=parsed_data,
                ranking_score=app.ranking_score,
            )

            # Aggregate
            language_distribution[detected_language] = (
                language_distribution.get(detected_language, 0) + 1
            )

            if bias_result.language_bias_detected:
                bias_summary["language_bias"] += 1
                flagged_count += 1
            if bias_result.format_bias_detected:
                bias_summary["format_bias"] += 1
            if bias_result.origin_bias_detected:
                bias_summary["origin_bias"] += 1

            if detected_language not in per_language_scores:
                per_language_scores[detected_language] = []
            if app.ranking_score:
                per_language_scores[detected_language].append(
                    app.ranking_score
                )

            candidate_data.append({
                "candidate_id": str(app.candidate_id),
                "ranking_score": app.ranking_score or 0.0,
                "detected_language": detected_language,
                "language_bias_detected": bias_result.language_bias_detected,
                "format_bias_detected": bias_result.format_bias_detected,
            })

        # Pool-level fairness analysis
        analysis = self.fairness_analyzer.analyze_job_pool(candidate_data)

        # Average scores per language
        avg_per_language = {
            lang: round(sum(scores) / len(scores), 4)
            for lang, scores in per_language_scores.items()
            if scores
        }

        # Aggregate recommendations
        all_recs = [analysis.summary]
        if analysis.flagged_groups:
            all_recs.append(
                f"Groups with lower selection rates: "
                f"{', '.join(analysis.flagged_groups)}. "
                f"Consider reviewing scoring criteria."
            )
        if bias_summary["language_bias"] > 0:
            all_recs.append(
                f"{bias_summary['language_bias']} candidate(s) may be "
                f"affected by language-based scoring bias."
            )
        if bias_summary["origin_bias"] > 0:
            all_recs.append(
                f"{bias_summary['origin_bias']} candidate(s) from African "
                f"institutions may have under-extracted education signals."
            )

        return JobFairnessReport(
            job_id=str(job_id),
            job_title=job.title,
            total_applications=len(applications),
            flagged_applications=flagged_count,
            overall_fair=analysis.is_fair,
            disparate_impact_ratio=analysis.disparate_impact_ratio,
            language_distribution=language_distribution,
            bias_summary=bias_summary,
            recommendations=all_recs,
            per_language_scores=avg_per_language,
        )

    async def get_candidate_fairness(
        self,
        application_id: uuid.UUID,
        candidate_id: uuid.UUID,
    ) -> CandidateFairnessResponse:
        """
        Return a candidate-facing fairness report for their application.
        Explains bias signals in plain language without revealing
        other candidates' scores.
        """
        # Verify ownership
        app_result = await self.db.execute(
            select(Application).where(
                Application.id == application_id,
                Application.candidate_id == candidate_id,
            )
        )
        application = app_result.scalar_one_or_none()
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        # Load fairness report
        report_result = await self.db.execute(
            select(FairnessReport).where(
                FairnessReport.application_id == application_id
            )
        )
        report = report_result.scalar_one_or_none()

        if not report:
            # Generate on demand if not exists
            report = await self.analyze_application(application_id)

        # Build candidate-facing signals
        bias_signals = []
        if report.bias_signals:
            for signal in report.bias_signals.get("signals", []):
                if signal.get("detected"):
                    bias_signals.append(BiasSignal(
                        signal_type=signal["signal_type"],
                        detected=True,
                        confidence=signal.get("confidence", 0.0),
                        description=signal.get("description", ""),
                        recommendation=signal.get("recommendation", ""),
                    ))

        adjusted_score = (
            report.fairness_metrics.get("adjusted_score")
            if report.fairness_metrics
            else None
        )

        explanation = (
            "Your application was analyzed for potential scoring bias. "
            f"{'Bias signals were detected — see details below.' if bias_signals else 'No significant bias was detected in your scoring.'}"
        )

        recommendations = (
            report.recommendations.split("\n")
            if report.recommendations
            else []
        )

        return CandidateFairnessResponse(
            application_id=str(application_id),
            is_fair=report.is_fair,
            bias_detected=len(bias_signals) > 0,
            your_score=application.ranking_score,
            adjusted_score=adjusted_score,
            bias_signals=bias_signals,
            explanation=explanation,
            recommendations=[r for r in recommendations if r.strip()],
        )