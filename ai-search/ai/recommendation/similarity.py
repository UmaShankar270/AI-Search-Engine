from __future__ import annotations

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class CosineSimilarity:
    def compute(self, vector_a: np.ndarray, vector_b: np.ndarray) -> float:
        if vector_a.ndim != 1 or vector_b.ndim != 1:
            raise ValueError("Both vectors must be 1-dimensional")
        if vector_a.shape != vector_b.shape:
            raise ValueError(f"Shape mismatch: {vector_a.shape} vs {vector_b.shape}")
        norm_a = np.linalg.norm(vector_a)
        norm_b = np.linalg.norm(vector_b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(vector_a, vector_b) / (norm_a * norm_b))

    def compute_similarity_matrix(self, vectors: list[np.ndarray]) -> np.ndarray:
        if not vectors:
            return np.empty((0, 0))
        matrix = np.stack(vectors, axis=0)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        normalized = matrix / norms
        result: np.ndarray = normalized @ normalized.T
        return result


class TopicSimilarity:
    def jaccard(self, topics_a: list[str], topics_b: list[str]) -> float:
        if not topics_a or not topics_b:
            return 0.0
        set_a = set(t.lower() for t in topics_a)
        set_b = set(t.lower() for t in topics_b)
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union) if union else 0.0

    def weighted_jaccard(
        self,
        topics_a: list[str],
        topics_b: list[str],
        weight_map: Optional[dict[str, float]] = None,
    ) -> float:
        if not topics_a or not topics_b:
            return 0.0
        set_a = set(t.lower() for t in topics_a)
        set_b = set(t.lower() for t in topics_b)
        intersection = set_a & set_b
        union = set_a | set_b
        if not union:
            return 0.0
        if weight_map:
            weight_a = sum(weight_map.get(t, 1.0) for t in intersection)
            weight_u = sum(weight_map.get(t, 1.0) for t in union)
            return weight_a / weight_u if weight_u else 0.0
        return len(intersection) / len(union)

    def overlap_coefficient(self, topics_a: list[str], topics_b: list[str]) -> float:
        if not topics_a or not topics_b:
            return 0.0
        set_a = set(t.lower() for t in topics_a)
        set_b = set(t.lower() for t in topics_b)
        intersection = set_a & set_b
        denominator = min(len(set_a), len(set_b))
        return len(intersection) / denominator if denominator > 0 else 0.0


class AggregatedSimilarity:
    def __init__(
        self,
        embedding_weight: float = 0.60,
        topic_weight: float = 0.25,
        language_weight: float = 0.15,
    ):
        self.weights = {
            "embedding": embedding_weight,
            "topic": topic_weight,
            "language": language_weight,
        }
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            factor = 1.0 / total
            self.weights = {k: v * factor for k, v in self.weights.items()}

    def compute(
        self,
        embedding_sim: float = 0.0,
        topic_sim: float = 0.0,
        same_language: bool = False,
    ) -> float:
        lang_score = 1.0 if same_language else 0.0
        return (
            self.weights["embedding"] * embedding_sim
            + self.weights["topic"] * topic_sim
            + self.weights["language"] * lang_score
        )
