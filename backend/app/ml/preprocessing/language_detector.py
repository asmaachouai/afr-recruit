"""
Language detection for multilingual CVs.
Detects Arabic, French, English, and mixed-language documents.
"""

import re
import structlog
from langdetect import detect, detect_langs, LangDetectException

logger = structlog.get_logger(__name__)

# Arabic Unicode range
ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F]+")


class LanguageDetector:
    """
    Detects the primary language of a CV.
    Handles mixed Arabic/French documents common in Morocco.
    """

    def detect(self, text: str) -> str:
        """
        Returns one of: 'ar', 'fr', 'en', 'mixed'
        """
        if not text or len(text.strip()) < 20:
            return "fr"  # default for Moroccan context

        arabic_chars = len(ARABIC_PATTERN.findall(text))
        total_words = len(text.split())
        arabic_ratio = arabic_chars / max(total_words, 1)

        # If more than 20% Arabic characters, flag as Arabic or mixed
        if arabic_ratio > 0.4:
            return "ar"
        elif arabic_ratio > 0.2:
            return "mixed"

        # Use langdetect for French/English distinction
        try:
            langs = detect_langs(text[:2000])  # use first 2000 chars for speed
            primary = langs[0]

            if primary.lang == "fr" and primary.prob > 0.7:
                return "fr"
            elif primary.lang == "en" and primary.prob > 0.7:
                return "en"
            elif primary.lang in ("fr", "en"):
                return primary.lang
            else:
                # Default to French for Moroccan context
                return "fr"

        except LangDetectException:
            logger.warning("Language detection failed, defaulting to fr")
            return "fr"

    def get_confidence(self, text: str) -> dict:
        """Returns language probabilities for explainability."""
        try:
            langs = detect_langs(text[:2000])
            return {lang.lang: round(lang.prob, 3) for lang in langs}
        except LangDetectException:
            return {"fr": 1.0}