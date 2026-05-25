"""
Fairness analyzer — computes disparate impact and fairness metrics
across a pool of candidates for a job posting.

Uses the 4/5ths rule (80% rule) from EEOC guidelines:
If the selection rate for a protected group is less than 80% of the
highest group's rate, disparate impact is present.
"""

from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger(__name__)

FOUR_FIFTHS_THRESHOLD = 0.80  # EEOC 4/5ths rule


@dataclass
class GroupMetrics:
    language: str
    count: int
    avg_score: float
    selection_rate: float  # rate at which this group is shortlisted
    relative_rate: float   # selection_rate / max_selection_rate


@dataclass
class FairnessAnalysis:
    disparate_impact_ratio: float
    is_fair: bool
    group_metrics: list[GroupMetrics]
    language_parity_score: float
    format_parity_score: float
    overall_fairness_score: float
    flagged_groups: list[str]
    summary: str


class FairnessAnalyzer:
    """
    Analyzes fairness across a pool of ranked candidates.
    Computes disparate impact by language group.
    """

    def analyze_job_pool(
        self,
        candidate_scores: list[dict],
        shortlist_threshold: float = 0.5,
    ) -> FairnessAnalysis:
        """
        Analyze fairness across all candidates for a job.

        candidate_scores: list of dicts with keys:
            - candidate_id: str
            - ranking_score: float
            - detected_language: str (fr, ar, en, mixed)
            - language_bias_detected: bool
            - format_bias_detected: bool

        shortlist_threshold: minimum score to be considered shortlisted
        """
        if not candidate_scores:
            return self._empty_analysis()

        # Group candidates by language
        groups: dict[str, list[float]] = {}
        for c in candidate_scores:
            lang = c.get("detected_language") or "unknown"
            if lang not in groups:
                groups[lang] = []
            groups[lang].append(c.get("ranking_score", 0.0))

        # Calculate selection rates per group
        group_metrics = []
        max_selection_rate = 0.0

        for lang, scores in groups.items():
            total = len(scores)
            shortlisted = sum(1 for s in scores if s >= shortlist_threshold)
            selection_rate = shortlisted / total if total > 0 else 0.0
            avg_score = sum(scores) / total if total > 0 else 0.0
            max_selection_rate = max(max_selection_rate, selection_rate)

            group_metrics.append(GroupMetrics(
                language=lang,
                count=total,
                avg_score=round(avg_score, 4),
                selection_rate=round(selection_rate, 4),
                relative_rate=0.0,  # calculated below
            ))

        # Calculate relative rates
        for gm in group_metrics:
            gm.relative_rate = round(
                gm.selection_rate / max_selection_rate
                if max_selection_rate > 0 else 1.0,
                4,
            )

        # Disparate impact ratio = min relative rate across groups
        if len(group_metrics) > 1:
            disparate_impact_ratio = min(
                gm.relative_rate for gm in group_metrics
            )
        else:
            disparate_impact_ratio = 1.0  # single group = no disparity

        is_fair = disparate_impact_ratio >= FOUR_FIFTHS_THRESHOLD

        # Identify flagged groups
        flagged_groups = [
            gm.language
            for gm in group_metrics
            if gm.relative_rate < FOUR_FIFTHS_THRESHOLD
        ]

        # Language parity score
        if len(group_metrics) > 1:
            avg_scores_by_lang = [gm.avg_score for gm in group_metrics]
            max_avg = max(avg_scores_by_lang)
            min_avg = min(avg_scores_by_lang)
            language_parity = 1.0 - (
                (max_avg - min_avg) / max_avg if max_avg > 0 else 0
            )
        else:
            language_parity = 1.0

        # Format parity score
        format_biased = sum(
            1 for c in candidate_scores
            if c.get("format_bias_detected", False)
        )
        format_parity = 1.0 - (
            format_biased / len(candidate_scores)
            if candidate_scores else 0
        )

        # Overall fairness score (weighted average)
        overall = round(
            disparate_impact_ratio * 0.5
            + language_parity * 0.3
            + format_parity * 0.2,
            4,
        )

        # Generate summary
        summary = self._generate_summary(
            disparate_impact_ratio, is_fair, flagged_groups, group_metrics
        )

        return FairnessAnalysis(
            disparate_impact_ratio=round(disparate_impact_ratio, 4),
            is_fair=is_fair,
            group_metrics=group_metrics,
            language_parity_score=round(language_parity, 4),
            format_parity_score=round(format_parity, 4),
            overall_fairness_score=overall,
            flagged_groups=flagged_groups,
            summary=summary,
        )

    def analyze_single_application(
        self,
        ranking_score: float,
        detected_language: str,
        language_bias_detected: bool,
        format_bias_detected: bool,
        origin_bias_detected: bool,
        job_avg_score: float = 0.5,
    ) -> dict:
        """
        Compute fairness metrics for a single application.
        Used when storing per-application fairness reports.
        """
        # Estimate what the score would be without bias
        bias_adjustment = 0.0
        if language_bias_detected:
            bias_adjustment += 0.08
        if format_bias_detected:
            bias_adjustment += 0.05
        if origin_bias_detected:
            bias_adjustment += 0.07

        adjusted_score = min(ranking_score + bias_adjustment, 1.0)

        # Simple disparate impact for single candidate
        # Compare against job average
        if job_avg_score > 0:
            relative_performance = ranking_score / job_avg_score
            disparate_impact = min(relative_performance, 1.0)
        else:
            disparate_impact = 1.0

        is_fair = (
            not language_bias_detected
            and not format_bias_detected
            and not origin_bias_detected
        )

        return {
            "disparate_impact_ratio": round(disparate_impact, 4),
            "is_fair": is_fair,
            "adjusted_score": round(adjusted_score, 4),
            "bias_adjustment": round(bias_adjustment, 4),
            "language_parity_score": 0.7 if language_bias_detected else 1.0,
            "format_parity_score": 0.8 if format_bias_detected else 1.0,
            "overall_fairness_score": round(
                (1.0 - bias_adjustment / 0.20) if bias_adjustment > 0 else 1.0,
                4,
            ),
        }

    def _empty_analysis(self) -> FairnessAnalysis:
        return FairnessAnalysis(
            disparate_impact_ratio=1.0,
            is_fair=True,
            group_metrics=[],
            language_parity_score=1.0,
            format_parity_score=1.0,
            overall_fairness_score=1.0,
            flagged_groups=[],
            summary="No candidates to analyze.",
        )

    def _generate_summary(
        self,
        ratio: float,
        is_fair: bool,
        flagged_groups: list[str],
        group_metrics: list[GroupMetrics],
    ) -> str:
        if is_fair:
            return (
                f"Fairness check passed. Disparate impact ratio: {ratio:.2f} "
                f"(threshold: 0.80). All language groups have comparable "
                f"selection rates."
            )
        else:
            groups_str = ", ".join(flagged_groups)
            return (
                f"Fairness concern detected. Disparate impact ratio: {ratio:.2f} "
                f"(below 0.80 threshold). "
                f"Groups with lower selection rates: {groups_str}. "
                f"Review scoring criteria for potential bias."
            )