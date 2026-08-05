from __future__ import annotations

import logging
from typing import Optional

from .factors import FACTOR_CLASSES, BaseFactor
from .models import CandidateRepo, FactorScore, RankingResult
from .weight_manager import WeightManager

logger = logging.getLogger(__name__)


class ScoreCalculator:
    def __init__(self, weight_manager: WeightManager):
        self._wm = weight_manager
        self._factors: list[BaseFactor] = [cls(weight_manager) for cls in FACTOR_CLASSES]

    def compute(
        self,
        repo: CandidateRepo,
        query: str = "",
        intent: Optional[str] = None,
    ) -> RankingResult:
        factor_scores: list[FactorScore] = []
        total_weight = 0.0
        weighted_sum = 0.0

        for factor in self._factors:
            try:
                fs = factor.compute(repo, query, intent)
            except Exception as e:
                logger.warning(
                    "Factor %s failed for %s: %s", factor.name, repo.repo_id, str(e)
                )
                continue

            if fs is None:
                continue

            factor_scores.append(fs)
            total_weight += fs.weight
            weighted_sum += fs.contribution

        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        final_score = max(0.0, min(1.0, final_score))

        health_score = self._compute_sub_score(factor_scores, [
            "contributor_count", "commit_frequency", "recent_activity",
            "issue_resolution_rate", "pr_activity", "release_frequency",
        ])
        popularity_score = self._compute_sub_score(factor_scores, [
            "github_stars", "fork_count", "community_adoption", "popularity_trend",
        ])

        return RankingResult(
            repo_id=repo.repo_id,
            final_score=final_score,
            rank=0,
            factor_scores=factor_scores,
            semantic_score=repo.semantic_score,
            health_score=health_score,
            popularity_score=popularity_score,
        )

    def _compute_sub_score(
        self,
        factor_scores: list[FactorScore],
        factor_names: list[str],
    ) -> float:
        scores = {fs.name: fs for fs in factor_scores}
        total = 0.0
        count = 0
        for name in factor_names:
            fs = scores.get(name)
            if fs is not None:
                total += fs.normalized_score
                count += 1
        return total / count if count > 0 else 0.0
