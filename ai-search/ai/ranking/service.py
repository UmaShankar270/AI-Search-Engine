from __future__ import annotations

import logging
import time
from typing import Any, Optional

from .calculator import ScoreCalculator
from .models import CandidateRepo, RankedResultSet, RankingResult
from .weight_manager import WeightManager

logger = logging.getLogger(__name__)


class RankingService:
    def __init__(
        self,
        weight_manager: Optional[WeightManager] = None,
        config_path: Optional[str] = None,
    ):
        self._wm = weight_manager or WeightManager(config_path=config_path)
        self._calculator = ScoreCalculator(self._wm)

    @property
    def weight_manager(self) -> WeightManager:
        return self._wm

    def rank(
        self,
        query: str,
        candidates: list[CandidateRepo],
        intent: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> RankedResultSet:
        start = time.perf_counter()

        if not candidates:
            elapsed = (time.perf_counter() - start) * 1000
            return RankedResultSet(
                query=query,
                total_candidates=0,
                processing_time_ms=round(elapsed, 2),
                intent=intent,
            )

        results: list[RankingResult] = []
        for repo in candidates:
            result = self._calculator.compute(repo, query, intent)
            results.append(result)

        results.sort(key=lambda r: r.final_score, reverse=True)

        for i, r in enumerate(results):
            r.rank = i + 1

        if top_k is not None and top_k > 0:
            results = results[:top_k]

        elapsed = (time.perf_counter() - start) * 1000
        return RankedResultSet(
            query=query,
            results=results,
            total_candidates=len(candidates),
            processing_time_ms=round(elapsed, 2),
            intent=intent,
        )

    def rank_search_results(
        self,
        query: str,
        search_hits: list[Any],
        repo_data_map: dict[str, dict[str, Any]],
        intent: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> RankedResultSet:
        candidates = self._build_candidates(search_hits, repo_data_map)
        return self.rank(query, candidates, intent, top_k)

    def rerank_with_cross_encoder(
        self,
        query: str,
        candidates: list[CandidateRepo],
        cross_encoder_fn: Any,
    ) -> RankedResultSet:
        import copy
        copied_candidates = [copy.copy(c) for c in candidates]

        texts = []
        for repo in copied_candidates:
            parts = [repo.repo_id]
            if repo.topics:
                parts.extend(repo.topics)
            if repo.language:
                parts.append(repo.language)
            texts.append(" ".join(parts))

        try:
            cross_scores = cross_encoder_fn(query, texts)
            for i, repo in enumerate(copied_candidates):
                if i < len(cross_scores):
                    copied_candidates[i].semantic_score = float(cross_scores[i])
        except Exception as e:
            logger.warning("Cross-encoder reranking failed: %s", str(e))

        return self.rank(query, copied_candidates)

    def rerank_with_llm(
        self,
        query: str,
        candidates: list[CandidateRepo],
        llm_fn: Any,
    ) -> RankedResultSet:
        import copy
        copied_candidates = [copy.copy(c) for c in candidates]

        try:
            llm_scores = llm_fn(query, copied_candidates)
            for i, repo in enumerate(copied_candidates):
                if i < len(llm_scores):
                    copied_candidates[i].semantic_score = float(llm_scores[i])
        except Exception as e:
            logger.warning("LLM reranking failed, using existing scores: %s", str(e))

        return self.rank(query, copied_candidates)


    def get_weight_summary(self) -> dict[str, Any]:
        return {
            "weights": self._wm.weights,
            "factor_count": len(self._wm.factor_names),
        }

    def _build_candidates(
        self,
        search_hits: list[Any],
        repo_data_map: dict[str, dict[str, Any]],
    ) -> list[CandidateRepo]:
        candidates: list[CandidateRepo] = []
        for hit in search_hits:
            repo_id = hit.repo_id if hasattr(hit, "repo_id") else hit.get("repo_id", "")
            semantic_score = hit.score if hasattr(hit, "score") else hit.get("score", 0.0)
            data = repo_data_map.get(repo_id, {})

            repo = CandidateRepo(
                repo_id=repo_id,
                semantic_score=semantic_score,
                stars=data.get("stars", 0),
                forks=data.get("forks", 0),
                contributors=data.get("contributors", 0),
                commits_last_3_months=data.get("commits_last_3_months", 0),
                days_since_last_commit=data.get("days_since_last_commit"),
                created_at=data.get("created_at"),
                releases_last_year=data.get("releases_last_year", 0),
                issues_closed=data.get("issues_closed", 0),
                issues_total=data.get("issues_total", 0),
                prs_merged=data.get("prs_merged", 0),
                prs_total=data.get("prs_total", 0),
                has_documentation=data.get("has_documentation", False),
                has_readme=data.get("has_readme", False),
                readme_length=data.get("readme_length", 0),
                readme_sections=data.get("readme_sections", 0),
                readme_has_badges=data.get("readme_has_badges", False),
                has_license=data.get("has_license", False),
                topics=data.get("topics", []),
                language=data.get("language", ""),
                stars_last_90_days=data.get("stars_last_90_days", 0),
                forks_last_90_days=data.get("forks_last_90_days", 0),
                metadata=data.get("metadata", data),
            )
            candidates.append(repo)
        return candidates
