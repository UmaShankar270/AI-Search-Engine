from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    repo_id: str
    score: float
    reason: str = ""
    similarity_score: float = 0.0
    popularity_score: float = 0.0
    language: str = ""
    matched_topics: list[str] = field(default_factory=list)
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "score": round(self.score, 6),
            "reason": self.reason,
            "similarity_score": round(self.similarity_score, 6),
            "popularity_score": round(self.popularity_score, 6),
            "language": self.language,
            "matched_topics": self.matched_topics[:10],
        }


@dataclass
class RecommendationSet:
    source: str
    recommendations: list[Recommendation] = field(default_factory=list)
    total_candidates: int = 0
    processing_time_ms: float = 0.0
    strategy: str = "content_based"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "total_candidates": self.total_candidates,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "strategy": self.strategy,
        }


@dataclass
class UserProfile:
    preferred_languages: list[str] = field(default_factory=list)
    preferred_topics: list[str] = field(default_factory=list)
    preferred_categories: list[str] = field(default_factory=list)
    weighted_tags: dict[str, float] = field(default_factory=dict)
    liked_repos: list[str] = field(default_factory=list)
    disliked_repos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "preferred_languages": self.preferred_languages,
            "preferred_topics": self.preferred_topics,
            "preferred_categories": self.preferred_categories,
            "weighted_tags": self.weighted_tags,
            "liked_repos": self.liked_repos,
            "disliked_repos": self.disliked_repos,
        }
