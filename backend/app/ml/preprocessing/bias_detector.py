"""
Bias detection for recruitment fairness.
Detects language bias, format bias, and origin bias in CV scoring.

Based on research showing AI recruitment tools systematically
disadvantage non-English speakers and non-Western CV formats.
References:
- Dastin (2018): Amazon's AI hiring tool showed bias against women
- Raghavan et al. (2020): Mitigating bias in algorithmic hiring
- Our context: Moroccan/Francophone Africa recruitment bias
"""

import re
from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger(__name__)

# African universities not well-represented in Western NLP training data
AFRICAN_UNIVERSITIES = [
    "ensias", "emi", "encg", "fsac", "fst", "insea",
    "universite mohammed", "universite hassan", "universite cadi ayyad",
    "universite ibn tofail", "universite abdelmalek",
    "universite cheikh anta diop", "universite felix houphouet",
    "universite de cocody", "universite ouaga",
    "universite de dakar", "ucad", "uac", "ub",
    "université", "ecole nationale",
]

# Moroccan/African city indicators
AFRICAN_LOCATIONS = [
    "casablanca", "rabat", "marrakech", "fes", "tanger", "agadir",
    "meknes", "oujda", "tetouan", "kenitra",
    "dakar", "abidjan", "tunis", "alger", "libreville",
    "douala", "yaounde", "bamako", "ouagadougou", "niamey",
    "lagos", "accra", "nairobi", "addis ababa",
]

# French CV format markers that ATS systems may penalize
FRENCH_CV_MARKERS = [
    "date de naissance", "nationalite", "situation familiale",
    "permis de conduire", "photo", "etat civil",
    "né le", "nee le", "age :", "sexe :",
]

# Arabic CV structure patterns
ARABIC_CV_MARKERS = [
    "\u0627\u0644\u0633\u064a\u0631\u0629 \u0627\u0644\u0630\u0627\u062a\u064a\u0629",  # CV in Arabic
    "\u0627\u0644\u062a\u0639\u0644\u064a\u0645",   # Education
    "\u0627\u0644\u062e\u0628\u0631\u0629",          # Experience
]


@dataclass
class BiasDetectionResult:
    language_bias_detected: bool = False
    format_bias_detected: bool = False
    origin_bias_detected: bool = False
    bias_signals: list[dict] = field(default_factory=list)
    overall_bias_score: float = 0.0  # 0 = no bias, 1 = high bias
    recommendations: list[str] = field(default_factory=list)


class BiasDetector:
    """
    Detects three types of bias in CV processing:
    1. Language bias — scoring disadvantage for French/Arabic CVs
    2. Format bias — penalty for non-Western CV formats
    3. Origin bias — under-recognition of African institutions
    """

    def detect(
        self,
        raw_text: str,
        detected_language: str,
        ats_score: float,
        parsed_data: dict,
        ranking_score: float | None = None,
    ) -> BiasDetectionResult:
        """
        Run full bias detection pipeline.
        Returns BiasDetectionResult with all detected signals.
        """
        result = BiasDetectionResult()
        text_lower = raw_text.lower() if raw_text else ""

        # 1. Language bias detection
        lang_bias = self._detect_language_bias(
            detected_language, ats_score, ranking_score
        )
        if lang_bias["detected"]:
            result.language_bias_detected = True
            result.bias_signals.append(lang_bias)

        # 2. Format bias detection
        format_bias = self._detect_format_bias(text_lower, detected_language)
        if format_bias["detected"]:
            result.format_bias_detected = True
            result.bias_signals.append(format_bias)

        # 3. Origin bias detection
        origin_bias = self._detect_origin_bias(text_lower, parsed_data)
        if origin_bias["detected"]:
            result.origin_bias_detected = True
            result.bias_signals.append(origin_bias)

        # Calculate overall bias score
        bias_count = sum([
            result.language_bias_detected,
            result.format_bias_detected,
            result.origin_bias_detected,
        ])
        result.overall_bias_score = round(bias_count / 3.0, 3)

        # Generate recommendations
        result.recommendations = self._generate_recommendations(result)

        return result

    def _detect_language_bias(
        self,
        detected_language: str,
        ats_score: float,
        ranking_score: float | None,
    ) -> dict:
        """
        Detect if a non-English CV is being unfairly penalized.
        French and Arabic CVs often score lower on ATS systems
        trained primarily on English data.
        """
        # Baseline: English CVs average ~65 ATS score in our system
        # If French/Arabic CV scores significantly below this with
        # otherwise good content, language bias is likely
        ENGLISH_BASELINE = 65.0
        BIAS_THRESHOLD = 15.0  # points below baseline = potential bias

        detected = False
        confidence = 0.0
        description = ""

        if detected_language in ("fr", "ar", "mixed"):
            if ats_score < (ENGLISH_BASELINE - BIAS_THRESHOLD):
                detected = True
                gap = ENGLISH_BASELINE - ats_score
                confidence = min(gap / 30.0, 0.95)
                description = (
                    f"CV in {detected_language.upper()} scored {ats_score:.1f}/100 "
                    f"— {gap:.1f} points below the English baseline. "
                    f"This may indicate language-based scoring disadvantage."
                )
            elif detected_language == "ar" and ats_score < ENGLISH_BASELINE:
                # Arabic CVs face higher baseline disadvantage
                detected = True
                confidence = 0.6
                description = (
                    "Arabic CV detected. NLP models have limited Arabic training data "
                    "which may result in under-extraction of skills and experience."
                )

        return {
            "signal_type": "language_bias",
            "detected": detected,
            "confidence": confidence,
            "language": detected_language,
            "ats_score": ats_score,
            "description": description,
            "recommendation": (
                "Consider language-normalized scoring that adjusts for "
                "the detected CV language when comparing candidates."
            ) if detected else "",
        }

    def _detect_format_bias(
        self, text_lower: str, detected_language: str
    ) -> dict:
        """
        Detect French/Arabic CV format elements that ATS systems
        may incorrectly penalize or misparse.
        """
        detected_markers = []

        for marker in FRENCH_CV_MARKERS:
            if marker in text_lower:
                detected_markers.append(marker)

        for marker in ARABIC_CV_MARKERS:
            if marker in text_lower:
                detected_markers.append("arabic_section_marker")

        detected = len(detected_markers) > 0
        confidence = min(len(detected_markers) * 0.25, 0.90)

        description = ""
        if detected:
            description = (
                f"CV contains {len(detected_markers)} format element(s) "
                f"common in Moroccan/Francophone CVs "
                f"(e.g. date of birth, nationality, photo) that Western ATS "
                f"systems may misparse or penalize."
            )

        return {
            "signal_type": "format_bias",
            "detected": detected,
            "confidence": confidence,
            "markers_found": detected_markers[:5],
            "description": description,
            "recommendation": (
                "Use format-neutral evaluation criteria. "
                "Personal information fields (age, nationality) should not "
                "affect candidate ranking."
            ) if detected else "",
        }

    def _detect_origin_bias(
        self, text_lower: str, parsed_data: dict
    ) -> dict:
        """
        Detect if African educational institutions or locations
        are being under-recognized by NLP models.
        """
        # Check if African university names appear in text
        # but were NOT extracted by the NLP pipeline
        african_unis_in_text = [
            uni for uni in AFRICAN_UNIVERSITIES
            if uni in text_lower
        ]

        # Check extracted education
        extracted_education = parsed_data.get("education", [])
        extracted_institutions = [
            (e.get("institution") or "").lower()
            for e in extracted_education
        ]

        # Count how many African unis in text were NOT extracted
        missed_institutions = [
            uni for uni in african_unis_in_text
            if not any(uni in inst for inst in extracted_institutions)
        ]

        # Also check if location is African
        african_location_found = any(
            loc in text_lower for loc in AFRICAN_LOCATIONS
        )

        detected = len(missed_institutions) > 0 or (
            african_location_found and len(extracted_institutions) == 0
        )
        confidence = min(len(missed_institutions) * 0.35, 0.90)

        description = ""
        if detected:
            description = (
                f"Detected {len(missed_institutions)} African institution(s) "
                f"in CV text that were not extracted by the NLP model. "
                f"This indicates the NLP model may not recognize "
                f"Moroccan/African university names, leading to "
                f"under-scoring of education signals."
            )

        return {
            "signal_type": "origin_bias",
            "detected": detected,
            "confidence": confidence,
            "missed_institutions": missed_institutions[:3],
            "description": description,
            "recommendation": (
                "Expand the NLP training data to include Moroccan and "
                "Francophone African institution names. "
                "Consider manual review for candidates from African universities."
            ) if detected else "",
        }

    def _generate_recommendations(
        self, result: BiasDetectionResult
    ) -> list[str]:
        """Generate actionable recommendations based on detected bias."""
        recs = []

        if result.language_bias_detected:
            recs.append(
                "Apply language-normalized scoring: compare candidates "
                "within the same language group before cross-group ranking."
            )
            recs.append(
                "Use the multilingual embedding similarity score as the "
                "primary signal rather than keyword-based ATS score."
            )

        if result.format_bias_detected:
            recs.append(
                "Strip format-specific fields (age, photo, nationality) "
                "before ATS scoring to ensure format-neutral evaluation."
            )

        if result.origin_bias_detected:
            recs.append(
                "Flag applications from African universities for human review "
                "to compensate for NLP under-extraction of institution names."
            )
            recs.append(
                "Expand the skills taxonomy with institution aliases for "
                "major Moroccan universities (ENSIAS, EMI, ENCG, FSAC)."
            )

        if not recs:
            recs.append(
                "No significant bias detected. Continue monitoring "
                "score distributions across language groups."
            )

        return recs