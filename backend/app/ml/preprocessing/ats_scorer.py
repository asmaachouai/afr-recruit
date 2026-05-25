"""
ATS (Applicant Tracking System) compatibility scorer.
Evaluates how well a CV would perform in automated screening systems.
Gives candidates actionable feedback to improve their CV.
"""

import re
from dataclasses import dataclass, field


@dataclass
class ATSResult:
    score: float
    grade: str
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    keyword_match_rate: float = 0.0
    section_scores: dict[str, float] = field(default_factory=dict)


class ATSScorer:
    """
    Scores a CV for ATS compatibility.
    Based on real ATS screening criteria used by major platforms.
    """

    def score(self, parsed_data: dict, raw_text: str) -> ATSResult:
        """
        Score the CV across multiple dimensions.
        Returns ATSResult with score, grade, issues, and suggestions.
        """
        scores = {}
        issues = []
        suggestions = []

        # 1. Contact information completeness (20 points)
        contact_score, contact_issues = self._score_contact(
            parsed_data.get("contact", {})
        )
        scores["contact"] = contact_score
        issues.extend(contact_issues)

        # 2. Skills presence (25 points)
        skills_score, skills_issues = self._score_skills(
            parsed_data.get("skills", [])
        )
        scores["skills"] = skills_score
        issues.extend(skills_issues)

        # 3. Education section (20 points)
        education_score, education_issues = self._score_education(
            parsed_data.get("education", [])
        )
        scores["education"] = education_score
        issues.extend(education_issues)

        # 4. Experience section (20 points)
        experience_score, experience_issues = self._score_experience(
            parsed_data.get("experience", [])
        )
        scores["experience"] = experience_score
        issues.extend(experience_issues)

        # 5. Document structure (15 points)
        structure_score, structure_issues = self._score_structure(
            raw_text, parsed_data.get("raw_sections", {})
        )
        scores["structure"] = structure_score
        issues.extend(structure_issues)

        # Calculate total
        total = sum(scores.values())

        # Generate suggestions
        suggestions = self._generate_suggestions(issues, parsed_data)

        # Assign grade
        grade = self._assign_grade(total)

        return ATSResult(
            score=round(total, 1),
            grade=grade,
            issues=issues,
            suggestions=suggestions,
            keyword_match_rate=round(skills_score / 25, 2),
            section_scores=scores,
        )

    def _score_contact(self, contact: dict) -> tuple[float, list[str]]:
        score = 0.0
        issues = []
        if contact.get("email"):
            score += 10
        else:
            issues.append("No email address found")
        if contact.get("phone"):
            score += 7
        else:
            issues.append("No phone number found")
        if contact.get("linkedin"):
            score += 3
        else:
            issues.append("No LinkedIn profile URL found")
        return score, issues

    def _score_skills(self, skills: list[str]) -> tuple[float, list[str]]:
        issues = []
        count = len(skills)
        if count == 0:
            issues.append("No technical skills detected")
            return 0.0, issues
        elif count < 5:
            issues.append(f"Only {count} skills detected — aim for at least 8")
            return 10.0, issues
        elif count < 10:
            return 18.0, issues
        else:
            return 25.0, issues

    def _score_education(self, education: list[dict]) -> tuple[float, list[str]]:
        issues = []
        if not education:
            issues.append("No education section detected")
            return 0.0, issues
        score = min(20.0, len(education) * 8.0)
        return score, issues

    def _score_experience(self, experience: list[dict]) -> tuple[float, list[str]]:
        issues = []
        if not experience:
            issues.append("No work experience detected — add dates to experience entries")
            return 0.0, issues
        score = min(20.0, len(experience) * 5.0)
        return score, issues

    def _score_structure(
        self, raw_text: str, sections: dict
    ) -> tuple[float, list[str]]:
        score = 0.0
        issues = []

        # Check minimum length
        word_count = len(raw_text.split())
        if word_count < 100:
            issues.append("CV is too short — aim for at least 300 words")
        elif word_count < 300:
            score += 5
        else:
            score += 10

        # Check section presence
        required_sections = ["experience", "education", "competences", "skills"]
        found = sum(1 for s in required_sections if s in sections)
        score += found * 1.25

        if found < 3:
            issues.append("Missing key sections — add clear section headers")

        return min(15.0, score), issues

    def _generate_suggestions(
        self, issues: list[str], parsed_data: dict
    ) -> list[str]:
        suggestions = []
        if not parsed_data.get("contact", {}).get("linkedin"):
            suggestions.append(
                "Add your LinkedIn profile URL to increase ATS visibility by up to 30%"
            )
        if len(parsed_data.get("skills", [])) < 8:
            suggestions.append(
                "Add a dedicated Skills section with at least 8-10 technical keywords"
            )
        if not parsed_data.get("summary"):
            suggestions.append(
                "Add a 3-5 sentence professional summary at the top of your CV"
            )
        suggestions.append(
            "Use standard section headers: Education, Experience, Skills, Languages"
        )
        suggestions.append(
            "Include dates (month/year) for all education and experience entries"
        )
        return suggestions

    def _assign_grade(self, score: float) -> str:
        if score >= 85:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 55:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"