"""
FAISS vector store for fast candidate similarity search.
Stores CV embeddings and enables sub-second similarity search
across thousands of candidates.
"""

import os
from pathlib import Path

import faiss
import numpy as np
import structlog

logger = structlog.get_logger(__name__)

EMBEDDING_DIM = 384  # dimension of MiniLM embeddings


class FAISSVectorStore:
    """
    Manages FAISS index for CV embeddings.
    Uses IndexFlatIP (inner product) since our vectors are L2-normalized,
    making inner product equivalent to cosine similarity.
    """

    def __init__(self, index_path: str = "./ml/faiss_index"):
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.index_path / "cv_index.faiss"
        self.mapping_file = self.index_path / "cv_mapping.npy"

        # FAISS index — IndexFlatIP for exact cosine similarity
        self.index = faiss.IndexFlatIP(EMBEDDING_DIM)

        # Maps FAISS integer ID → candidate UUID string
        self.id_mapping: list[str] = []

        self._load_if_exists()

    def _load_if_exists(self) -> None:
        """Load existing index from disk if available."""
        if self.index_file.exists() and self.mapping_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
                self.id_mapping = list(np.load(str(self.mapping_file),
                                               allow_pickle=True))
                logger.info(
                    "FAISS index loaded",
                    vectors=self.index.ntotal,
                )
            except Exception as e:
                logger.warning("Failed to load FAISS index", error=str(e))
                self.index = faiss.IndexFlatIP(EMBEDDING_DIM)
                self.id_mapping = []

    def save(self) -> None:
        """Persist index to disk."""
        faiss.write_index(self.index, str(self.index_file))
        np.save(str(self.mapping_file), np.array(self.id_mapping,
                                                  dtype=object))
        logger.info("FAISS index saved", vectors=self.index.ntotal)

    def add_cv(self, candidate_id: str, embedding: np.ndarray) -> None:
        """Add or update a CV embedding in the index."""
        # Remove existing entry if present
        if candidate_id in self.id_mapping:
            self._remove_candidate(candidate_id)

        vector = embedding.reshape(1, -1).astype(np.float32)
        self.index.add(vector)
        self.id_mapping.append(candidate_id)
        self.save()

    def search(
        self, query_embedding: np.ndarray, top_k: int = 10
    ) -> list[tuple[str, float]]:
        """
        Find the top-k most similar CVs to a query embedding.
        Returns list of (candidate_id, similarity_score) tuples.
        """
        if self.index.ntotal == 0:
            return []

        k = min(top_k, self.index.ntotal)
        query = query_embedding.reshape(1, -1).astype(np.float32)

        scores, indices = self.index.search(query, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.id_mapping):
                candidate_id = self.id_mapping[idx]
                results.append((candidate_id, float(score)))

        return results

    def _remove_candidate(self, candidate_id: str) -> None:
        """Remove a candidate from the index (rebuild required)."""
        if candidate_id not in self.id_mapping:
            return

        # FAISS FlatIndex doesn't support deletion — rebuild without this entry
        idx_to_remove = self.id_mapping.index(candidate_id)
        self.id_mapping.pop(idx_to_remove)

        # Reconstruct index without the removed vector
        if self.index.ntotal > 0:
            all_vectors = np.zeros(
                (self.index.ntotal, EMBEDDING_DIM), dtype=np.float32
            )
            for i in range(self.index.ntotal):
                self.index.reconstruct(i, all_vectors[i])

            kept_vectors = np.delete(all_vectors, idx_to_remove, axis=0)
            self.index = faiss.IndexFlatIP(EMBEDDING_DIM)
            if len(kept_vectors) > 0:
                self.index.add(kept_vectors)

    @property
    def total_vectors(self) -> int:
        return self.index.ntotal


# Global singleton instance
vector_store = FAISSVectorStore()