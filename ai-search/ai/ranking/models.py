from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class FactorScore:
    name: str
    label: str
    raw_value: float
    normalized_score: float
    weight: float
    contribution: float
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "raw_value": round(self.raw_value, 6),
            "normalized_score": round(self.normalized_score, 6),
            "weight": self.weight,
            "contribution": round(self.contribution, 6),
        }


@dataclass
class CandidateRepo:
    repo_id: str
    semantic_score: float = 0.0

    stars: int = 0
    forks: int = 0
    contributors: int = 0
    commits_last_3_months: int = 0
    days_since_last_commit: Optional[int] = None
    created_at: Optional[str] = None
    releases_last_year: int = 0
    issues_closed: int = 0
    issues_total: int = 0
    prs_merged: int = 0
    prs_total: int = 0

    has_documentation: bool = False
    has_readme: bool = False
    readme_length: int = 0
    readme_sections: int = 0
    readme_has_badges: bool = False

    has_license: bool = False
    topics: list[str] = field(default_factory=list)
    language: str = ""

    stars_last_90_days: int = 0
    forks_last_90_days: int = 0

    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "semantic_score": self.semantic_score,
            "stars": self.stars,
            "forks": self.forks,
            "contributors": self.contributors,
            "commits_last_3_months": self.commits_last_3_months,
            "days_since_last_commit": self.days_since_last_commit,
            "created_at": self.created_at,
            "releases_last_year": self.releases_last_year,
            "issues_closed": self.issues_closed,
            "issues_total": self.issues_total,
            "prs_merged": self.prs_merged,
            "prs_total": self.prs_total,
            "has_documentation": self.has_documentation,
            "has_readme": self.has_readme,
            "readme_length": self.readme_length,
            "has_license": self.has_license,
            "topics": self.topics,
            "language": self.language,
        }


@dataclass
class RankingResult:
    repo_id: str
    final_score: float
    rank: int
    factor_scores: list[FactorScore] = field(default_factory=list)
    semantic_score: float = 0.0
    health_score: float = 0.0
    popularity_score: float = 0.0
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "final_score": round(self.final_score, 6),
            "rank": self.rank,
            "factor_scores": [f.to_dict() for f in self.factor_scores],
            "semantic_score": round(self.semantic_score, 6),
            "health_score": round(self.health_score, 6),
            "popularity_score": round(self.popularity_score, 6),
        }


@dataclass
class RankedResultSet:
    query: str
    results: list[RankingResult] = field(default_factory=list)
    total_candidates: int = 0
    processing_time_ms: float = 0.0
    intent: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_candidates": self.total_candidates,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "intent": self.intent,
        }
