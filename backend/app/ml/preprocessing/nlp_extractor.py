"""
NLP information extraction from CV text.
Extracts skills, education, experience, contact info using
spaCy NER + rule-based patterns.
Supports Arabic, French, and English CVs.
"""

import re
from typing import Any

import spacy
import structlog

logger = structlog.get_logger(__name__)

# Skills taxonomy relevant to Morocco/Francophone Africa tech market
TECH_SKILLS = {
    "programming": [
        "python", "javascript", "typescript", "java", "c++", "c#", "php",
        "ruby", "go", "rust", "kotlin", "swift", "r", "matlab", "scala",
    ],
    "web": [
        "react", "angular", "vue", "nextjs", "nodejs", "django", "fastapi",
        "flask", "laravel", "spring", "express", "html", "css", "tailwind",
    ],
    "data": [
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "spark", "hadoop", "tableau", "power bi", "sql", "nosql",
    ],
    "cloud": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
        "git", "github", "gitlab", "jenkins", "linux",
    ],
    "soft": [
        "leadership", "communication", "teamwork", "agile", "scrum",
        "gestion de projet", "travail en equipe", "communication",
    ],
}

ALL_SKILLS = {
    skill.lower()
    for category in TECH_SKILLS.values()
    for skill in category
}

# Education keywords in French and English
EDUCATION_KEYWORDS_FR = [
    "licence", "master", "doctorat", "bac", "bts", "dut", "ingenieur",
    "ecole", "universite", "faculte", "formation", "diplome",
]
EDUCATION_KEYWORDS_EN = [
    "bachelor", "master", "phd", "degree", "university", "college",
    "school", "institute", "diploma", "certificate",
]

# Experience section markers
EXPERIENCE_MARKERS = [
    "experience", "experiences", "emploi", "poste", "travail",
    "professional experience", "work experience", "career",
]


class NLPExtractor:
    """
    Extracts structured data from CV text.
    Loads spaCy models lazily to avoid startup overhead.
    """

    def __init__(self):
        self._models: dict[str, spacy.language.Language] = {}

    def _get_model(self, language: str) -> spacy.language.Language:
        """Load and cache spaCy model for the given language."""
        if language not in self._models:
            model_map = {
                "fr": "fr_core_news_sm",
                "en": "en_core_web_sm",
                "mixed": "fr_core_news_sm",
                "ar": "fr_core_news_sm",  # fallback — Arabic NLP via rules
            }
            model_name = model_map.get(language, "fr_core_news_sm")
            try:
                self._models[language] = spacy.load(model_name)
                logger.info("spaCy model loaded", model=model_name)
            except OSError:
                logger.warning(
                    f"Model {model_name} not found, falling back to en_core_web_sm"
                )
                self._models[language] = spacy.load("en_core_web_sm")
        return self._models[language]

    def extract(self, text: str, language: str) -> dict[str, Any]:
        """
        Main extraction method.
        Returns structured dict with all extracted CV fields.
        """
        nlp = self._get_model(language)
        doc = nlp(text[:100000])  # limit to 100k chars for performance

        return {
            "contact": self._extract_contact(text),
            "skills": self._extract_skills(text),
            "education": self._extract_education(text, language),
            "experience": self._extract_experience(text, language),
            "languages": self._extract_languages(text),
            "summary": self._extract_summary(text),
            "entities": self._extract_entities(doc),
            "raw_sections": self._split_sections(text),
        }

    def _extract_contact(self, text: str) -> dict[str, str | None]:
        """Extract email, phone, LinkedIn from text."""
        email_pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
        phone_pattern = r"(?:\+212|0)[\s\-]?[5-7][\d\s\-]{8,}"
        linkedin_pattern = r"linkedin\.com/in/[\w\-]+"

        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        linkedins = re.findall(linkedin_pattern, text, re.IGNORECASE)

        return {
            "email": emails[0] if emails else None,
            "phone": phones[0].strip() if phones else None,
            "linkedin": linkedins[0] if linkedins else None,
        }

    def _extract_skills(self, text: str) -> list[str]:
        """Extract technical and soft skills using keyword matching."""
        text_lower = text.lower()
        found_skills = []

        for skill in ALL_SKILLS:
            # Use word boundary matching to avoid partial matches
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                found_skills.append(skill.title())

        return sorted(set(found_skills))

    def _extract_education(
        self, text: str, language: str
    ) -> list[dict[str, str | None]]:
        """Extract education entries from CV text."""
        education = []
        lines = text.split("\n")

        keywords = (
            EDUCATION_KEYWORDS_FR
            if language in ("fr", "ar", "mixed")
            else EDUCATION_KEYWORDS_EN
        )

        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords):
                # Extract year from nearby lines
                context = " ".join(lines[max(0, i - 1) : i + 3])
                years = re.findall(r"\b(19|20)\d{2}\b", context)

                education.append(
                    {
                        "raw_line": line.strip(),
                        "year_start": years[0] if len(years) > 0 else None,
                        "year_end": years[1] if len(years) > 1 else None,
                        "institution": self._find_institution(context),
                    }
                )

        return education[:10]  # cap at 10 entries

    def _extract_experience(
        self, text: str, language: str
    ) -> list[dict[str, str | None]]:
        """Extract work experience entries."""
        experience = []
        lines = text.split("\n")

        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Look for date ranges indicating a job entry
            date_range = re.search(
                r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|"
                r"janv|fevr|mars|avr|mai|juin|juil|aout|sept|oct|nov|dec)"
                r"[\w\s]*\d{4}",
                line_lower,
            )
            year_range = re.search(r"\b(20|19)\d{2}\b.*\b(20|19)\d{2}\b", line)

            if date_range or year_range:
                context = " ".join(lines[max(0, i - 1) : i + 4])
                years = re.findall(r"\b(19|20)\d{2}\b", context)

                experience.append(
                    {
                        "raw_line": line.strip(),
                        "year_start": years[0] if len(years) > 0 else None,
                        "year_end": years[1] if len(years) > 1 else None,
                        "context": context[:300],
                    }
                )

        return experience[:15]  # cap at 15 entries

    def _extract_languages(self, text: str) -> list[str]:
        """Extract spoken languages from CV."""
        language_keywords = {
            "arabe": "Arabic",
            "arabic": "Arabic",
            "francais": "French",
            "french": "French",
            "anglais": "English",
            "english": "English",
            "espagnol": "Spanish",
            "spanish": "Spanish",
            "allemand": "German",
            "german": "German",
            "darija": "Darija",
        }
        text_lower = text.lower()
        found = []
        for keyword, normalized in language_keywords.items():
            if keyword in text_lower and normalized not in found:
                found.append(normalized)
        return found

    def _extract_summary(self, text: str) -> str | None:
        """Extract professional summary or objective section."""
        summary_markers = [
            "profil", "resume", "objectif", "a propos", "presentation",
            "summary", "profile", "objective", "about",
        ]
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(marker in line.lower() for marker in summary_markers):
                # Take next 3-5 non-empty lines as summary
                summary_lines = []
                for j in range(i + 1, min(i + 6, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                if summary_lines:
                    return " ".join(summary_lines)
        return None

    def _extract_entities(self, doc) -> dict[str, list[str]]:
        """Extract named entities using spaCy NER."""
        entities: dict[str, list[str]] = {
            "organizations": [],
            "locations": [],
            "persons": [],
        }
        for ent in doc.ents:
            if ent.label_ == "ORG" and ent.text not in entities["organizations"]:
                entities["organizations"].append(ent.text)
            elif ent.label_ in ("GPE", "LOC") and ent.text not in entities["locations"]:
                entities["locations"].append(ent.text)
            elif ent.label_ == "PER" and ent.text not in entities["persons"]:
                entities["persons"].append(ent.text)
        return entities

    def _find_institution(self, context: str) -> str | None:
        """Try to find institution name in context text."""
        institution_patterns = [
            r"(?:universite|university|ecole|school|institut|college)\s+[\w\s]+",
        ]
        for pattern in institution_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(0)[:100]
        return None

    def _split_sections(self, text: str) -> dict[str, str]:
        """Split CV into major sections for structured access."""
        section_markers = [
            "education", "formation", "experience", "competences",
            "skills", "langues", "languages", "projets", "projects",
            "certifications", "publications",
        ]
        sections: dict[str, str] = {}
        lines = text.split("\n")
        current_section = "header"
        current_content: list[str] = []

        for line in lines:
            line_lower = line.strip().lower()
            matched_section = None
            for marker in section_markers:
                if line_lower.startswith(marker) and len(line_lower) < 50:
                    matched_section = marker
                    break

            if matched_section:
                sections[current_section] = "\n".join(current_content).strip()
                current_section = matched_section
                current_content = []
            else:
                current_content.append(line)

        sections[current_section] = "\n".join(current_content).strip()
        return {k: v for k, v in sections.items() if v}