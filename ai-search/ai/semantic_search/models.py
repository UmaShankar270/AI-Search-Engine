from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SearchHit:
    repo_id: str
    score: float
    rank: int
    metadata: Optional[dict] = None

    def __post_init__(self):
        if self.score < 0 or self.score > 1:
            logger.warning(
                "SearchHit score %.4f outside [0, 1] for repo %s",
                self.score,
                self.repo_id,
            )

    def to_dict(self) -> dict:
        return {
            "repo_id": self.repo_id,
            "score": self.score,
            "rank": self.rank,
            "metadata": self.metadata,
        }


@dataclass
class SearchResult:
    query: str
    results: list[SearchHit] = field(default_factory=list)
    total_count: int = 0
    search_time_ms: float = 0.0
    threshold: float = 0.0

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_count": self.total_count,
            "search_time_ms": self.search_time_ms,
            "threshold": self.threshold,
        }


@dataclass
class IndexStats:
    total_vectors: int = 0
    dimension: int = 0
    index_type: str = ""
    memory_usage_bytes: int = 0

    def to_dict(self) -> dict:
        return {
            "total_vectors": self.total_vectors,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "memory_usage_bytes": self.memory_usage_bytes,
        }
