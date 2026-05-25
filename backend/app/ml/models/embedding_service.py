"""
Multilingual sentence embedding service.
Uses paraphrase-multilingual-MiniLM-L12-v2 — trained on 50+ languages
including French and Arabic, making it ideal for Moroccan/African CVs.
"""

import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

logger = structlog.get_logger(__name__)

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingService:
    """
    Generates sentence embeddings for CVs and job descriptions.
    Singleton pattern — model is loaded once and reused.
    """

    _instance: "EmbeddingService | None" = None
    _model: SentenceTransformer | None = None

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self) -> None:
        """Load the embedding model. Call once at startup."""
        if self._model is None:
            logger.info("Loading embedding model", model=MODEL_NAME)
            self._model = SentenceTransformer(MODEL_NAME)
            logger.info("Embedding model loaded successfully")

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self.load()
        return self._model

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate a single embedding vector for a text.
        Returns numpy array of shape (384,).
        """
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,  # L2 normalize for cosine similarity
            show_progress_bar=False,
        )
        return embedding.astype(np.float32)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.
        Returns numpy array of shape (n, 384).
        """
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )
        return embeddings.astype(np.float32)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two normalized vectors.
        Since vectors are L2-normalized, dot product = cosine similarity.
        Returns value between 0 and 1.
        """
        return float(np.dot(vec1, vec2))

    def prepare_cv_text(self, parsed_data: dict) -> str:
        """
        Convert parsed CV data into a single text for embedding.
        Concatenates the most semantically meaningful fields.
        """
        parts = []

        if parsed_data.get("summary"):
            parts.append(parsed_data["summary"])

        skills = parsed_data.get("skills", [])
        if skills:
            parts.append("Skills: " + ", ".join(skills))

        education = parsed_data.get("education", [])
        for edu in education[:3]:
            if edu.get("raw_line"):
                parts.append(edu["raw_line"])

        experience = parsed_data.get("experience", [])
        for exp in experience[:5]:
            if exp.get("context"):
                parts.append(exp["context"][:200])

        languages = parsed_data.get("languages", [])
        if languages:
            parts.append("Languages: " + ", ".join(languages))

        return " | ".join(parts) if parts else "CV document"

    def prepare_job_text(self, job) -> str:
        """
        Convert a job posting into a single text for embedding.
        """
        parts = [job.title, job.description]

        if job.requirements:
            parts.append(job.requirements)

        if job.required_skills:
            parts.append("Required skills: " + ", ".join(job.required_skills))

        if job.required_languages:
            parts.append("Languages: " + ", ".join(job.required_languages))

        return " | ".join(parts)


# Global singleton instance
embedding_service = EmbeddingService()