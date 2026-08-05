from __future__ import annotations

import logging
import time
from math import log10
from typing import Any, Optional

import numpy as np

from ai.recommendation.models import Recommendation, RecommendationSet, UserProfile
from ai.recommendation.similarity import AggregatedSimilarity, CosineSimilarity, TopicSimilarity

logger = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self, embedding_generator: Optional[Any] = None):
        self._cosine = CosineSimilarity()
        self._topic = TopicSimilarity()
        self._aggregated = AggregatedSimilarity()
        self._embedding_generator = embedding_generator

    def recommend_from_repo(
        self,
        repo_id: str,
        all_repos: list[dict[str, Any]],
        embedding_map: dict[str, np.ndarray],
        top_n: int = 5,
        exclude_ids: Optional[set[str]] = None,
    ) -> RecommendationSet:
        start = time.perf_counter()
        source_embedding = embedding_map.get(repo_id)
        if source_embedding is None:
            logger.warning("No embedding found for repo '%s'", repo_id)
            return RecommendationSet(
                source=f"repo:{repo_id}",
                total_candidates=0,
                strategy="content_based",
            )

        source_topics = self._get_topics(all_repos, repo_id)
        source_language = self._get_language(all_repos, repo_id)
        excluded = set(exclude_ids or [])
        excluded.add(repo_id)

        scored: list[tuple[float, float, dict[str, Any]]] = []
        for repo in all_repos:
            rid = self._get_repo_id(repo)
            if rid in excluded:
                continue
            target_embedding = embedding_map.get(rid)
            if target_embedding is None:
                continue

            embedding_sim = self._cosine.compute(source_embedding, target_embedding)
            target_topics = repo.get("topics") or []
            topic_sim = self._topic.jaccard(source_topics, target_topics)
            same_language = (
                (repo.get("language") or "").lower()
                == source_language.lower()
                if source_language
                else False
            )
            agg_sim = self._aggregated.compute(
                embedding_sim=embedding_sim,
                topic_sim=topic_sim,
                same_language=same_language,
            )
            scored.append((agg_sim, embedding_sim, repo))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_n]

        matched_topics = self._topic_set(
            source_topics, source_embedding, all_repos, embedding_map, top_n
        )

        recommendations = []
        for score, sim, repo in top:
            rid = self._get_repo_id(repo)
            matched = matched_topics.get(rid, [])
            lang = repo.get("language", "")
            reasons = self._build_reasons(score, matched, lang, source_language)
            recommendations.append(
                Recommendation(
                    repo_id=rid,
                    score=score,
                    reason="; ".join(reasons),
                    similarity_score=sim,
                    language=lang,
                    matched_topics=matched,
                    metadata={"stars": repo.get("stars", 0)},
                )
            )

        elapsed = (time.perf_counter() - start) * 1000
        return RecommendationSet(
            source=f"repo:{repo_id}",
            recommendations=recommendations,
            total_candidates=len(scored),
            processing_time_ms=elapsed,
            strategy="content_based",
        )

    def recommend_from_query(
        self,
        query_vector: np.ndarray,
        all_repos: list[dict[str, Any]],
        embedding_map: dict[str, np.ndarray],
        top_n: int = 5,
        exclude_ids: Optional[set[str]] = None,
    ) -> RecommendationSet:
        start = time.perf_counter()
        excluded = set(exclude_ids or [])

        scored: list[tuple[float, dict[str, Any]]] = []
        for repo in all_repos:
            rid = self._get_repo_id(repo)
            if rid in excluded:
                continue
            target_embedding = embedding_map.get(rid)
            if target_embedding is None:
                continue
            sim = self._cosine.compute(query_vector, target_embedding)
            scored.append((sim, repo))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_n]

        recommendations = []
        for score, repo in top:
            rid = self._get_repo_id(repo)
            lang = repo.get("language", "")
            stars = repo.get("stars", 0) or 0
            
            reasons = [f"Semantic similarity {score:.3f} to query"]
            if stars >= 10000:
                reasons.append("Popular repository")
            elif stars > 0:
                reasons.append(f"Has {stars} stars")
            if lang:
                reasons.append(f"Language: {lang}")
            
            reason_str = "; ".join(reasons)
            
            recommendations.append(
                Recommendation(
                    repo_id=rid,
                    score=score,
                    reason=reason_str,
                    similarity_score=score,
                    language=lang,
                    matched_topics=repo.get("topics") or [],
                    metadata={"stars": stars},
                )
            )

        elapsed = (time.perf_counter() - start) * 1000
        return RecommendationSet(
            source="query",
            recommendations=recommendations,
            total_candidates=len(scored),
            processing_time_ms=elapsed,
            strategy="query_based",
        )

    def recommend_hybrid(
        self,
        repo_id: str,
        all_repos: list[dict[str, Any]],
        embedding_map: dict[str, np.ndarray],
        user_profile: Optional[UserProfile] = None,
        top_n: int = 5,
        content_weight: float = 0.50,
        popularity_weight: float = 0.30,
        profile_weight: float = 0.20,
    ) -> RecommendationSet:
        start = time.perf_counter()
        source_embedding = embedding_map.get(repo_id)
        if source_embedding is None:
            logger.warning("No embedding found for repo '%s'", repo_id)
            return RecommendationSet(
                source=f"hybrid:repo:{repo_id}",
                total_candidates=0,
                strategy="hybrid",
            )

        source_topics = self._get_topics(all_repos, repo_id)
        source_language = self._get_language(all_repos, repo_id)
        excluded = {repo_id}

        scored: list[tuple[float, dict[str, Any], float, float, float, float, list[str]]] = []
        for repo in all_repos:
            rid = self._get_repo_id(repo)
            if rid in excluded:
                continue
            target_embedding = embedding_map.get(rid)
            if target_embedding is None:
                continue

            embedding_sim = self._cosine.compute(source_embedding, target_embedding)
            target_topics = repo.get("topics") or []
            topic_sim = self._topic.jaccard(source_topics, target_topics)
            same_language = (
                (repo.get("language") or "").lower()
                == source_language.lower()
                if source_language
                else False
            )
            content_score = self._aggregated.compute(
                embedding_sim=embedding_sim,
                topic_sim=topic_sim,
                same_language=same_language,
            )

            popularity_score = self._compute_popularity_score(repo)
            profile_score = self._compute_profile_score(
                repo, user_profile
            ) if user_profile else 0.0

            total = (
                content_weight * content_score
                + popularity_weight * popularity_score
                + profile_weight * profile_score
            )
            scored.append((
                total, repo, content_score, popularity_score,
                profile_score, topic_sim, target_topics,
            ))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_n]

        recommendations = []
        for total, repo, cs, ps, pfs, ts, matched in top:
            rid = self._get_repo_id(repo)
            lang = repo.get("language", "")
            reasons = self._build_hybrid_reasons(cs, ps, pfs, ts)
            recommendations.append(
                Recommendation(
                    repo_id=rid,
                    score=total,
                    reason="; ".join(reasons),
                    similarity_score=cs,
                    popularity_score=ps,
                    language=lang,
                    matched_topics=matched or [],
                    metadata={"profile_score": round(pfs, 4), "stars": repo.get("stars", 0)},
                )
            )

        elapsed = (time.perf_counter() - start) * 1000
        return RecommendationSet(
            source=f"hybrid:repo:{repo_id}",
            recommendations=recommendations,
            total_candidates=len(scored),
            processing_time_ms=elapsed,
            strategy="hybrid",
        )

    def recommend_popular(
        self,
        all_repos: list[dict[str, Any]],
        top_n: int = 5,
        sort_key: str = "stars",
    ) -> RecommendationSet:
        start = time.perf_counter()
        if not all_repos:
            return RecommendationSet(
                source="popular",
                total_candidates=0,
                strategy="popular",
            )

        sorted_repos = sorted(
            all_repos,
            key=lambda r: r.get(sort_key, 0) or 0,
            reverse=True,
        )
        top = sorted_repos[:top_n]
        max_val = max((r.get(sort_key, 0) or 0) for r in sorted_repos) or 1

        recommendations = []
        for repo in top:
            rid = self._get_repo_id(repo)
            lang = repo.get("language", "")
            val = repo.get(sort_key, 0) or 0
            score = val / max_val
            recommendations.append(
                Recommendation(
                    repo_id=rid,
                    score=score,
                    reason=f"Top by {sort_key}",
                    similarity_score=0.0,
                    popularity_score=score,
                    language=lang,
                    matched_topics=repo.get("topics") or [],
                    metadata={sort_key: val},
                )
            )

        elapsed = (time.perf_counter() - start) * 1000
        return RecommendationSet(
            source="popular",
            recommendations=recommendations,
            total_candidates=len(all_repos),
            processing_time_ms=elapsed,
            strategy="popular",
        )

    def _get_repo_id(self, repo: dict[str, Any]) -> str:
        return repo.get("full_name") or repo.get("repo_id") or repo.get("id") or ""

    def _get_topics(self, all_repos: list[dict[str, Any]], repo_id: str) -> list[str]:
        for repo in all_repos:
            if self._get_repo_id(repo) == repo_id:
                return repo.get("topics") or []
        return []

    def _get_language(self, all_repos: list[dict[str, Any]], repo_id: str) -> str:
        for repo in all_repos:
            if self._get_repo_id(repo) == repo_id:
                return repo.get("language") or ""
        return ""

    def _compute_popularity_score(self, repo: dict[str, Any]) -> float:
        stars = repo.get("stars", 0) or 0
        forks = repo.get("forks", 0) or 0
        contributors = repo.get("contributors", 0) or 0
        raw = (
            log10(max(stars, 1)) * 0.5
            + log10(max(forks, 1)) * 0.3
            + log10(max(contributors, 1)) * 0.2
        )
        max_raw = log10(1000000) * 0.5 + log10(100000) * 0.3 + log10(10000) * 0.2
        return min(raw / max_raw, 1.0)

    def _compute_profile_score(self, repo: dict[str, Any], profile: Optional[UserProfile]) -> float:
        if not profile:
            return 0.0
        score = 0.0
        total_weight = 0.0
        lang = (repo.get("language") or "").lower()
        topics = set(t.lower() for t in (repo.get("topics") or []))

        if profile.preferred_languages:
            if lang in [pl.lower() for pl in profile.preferred_languages]:
                score += 1.0
            total_weight += 1.0

        if profile.preferred_topics:
            pref_topics = set(t.lower() for t in profile.preferred_topics)
            overlap = topics & pref_topics
            if overlap:
                score += len(overlap) / len(pref_topics)
            total_weight += 1.0

        if profile.weighted_tags:
            tag_score = sum(
                w for t, w in profile.weighted_tags.items() if t.lower() in topics
            )
            max_tag = max(profile.weighted_tags.values()) if profile.weighted_tags else 1.0
            score += tag_score / max_tag
            total_weight += 1.0

        return score / total_weight if total_weight > 0 else 0.0

    def _topic_set(
        self,
        source_topics: list[str],
        source_embedding: np.ndarray,
        all_repos: list[dict[str, Any]],
        embedding_map: dict[str, np.ndarray],
        top_n: int,
    ) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for repo in all_repos:
            rid = repo.get("repo_id", "")
            topics = repo.get("topics") or []
            if not topics:
                continue
            matched = [t for t in topics if t.lower() in {s.lower() for s in source_topics}]
            if matched:
                result[rid] = matched
        return result

    def _build_reasons(
        self,
        score: float,
        matched_topics: list[str],
        language: str,
        source_language: str,
    ) -> list[str]:
        reasons = []
        if score > 0.8:
            reasons.append("Highly similar repository")
        elif score > 0.5:
            reasons.append("Moderately similar repository")
        if matched_topics:
            reasons.append(f"Shared topics: {', '.join(matched_topics[:5])}")
        if language and source_language and language.lower() == source_language.lower():
            reasons.append(f"Same language: {language}")
        return reasons

    def _build_hybrid_reasons(
        self,
        content_score: float,
        popularity_score: float,
        profile_score: float,
        topic_sim: float,
    ) -> list[str]:
        reasons = []
        if content_score > 0.7:
            reasons.append("Strong content match")
        if popularity_score > 0.6:
            reasons.append("Popular repository")
        if profile_score > 0.5:
            reasons.append("Matches your preferences")
        if topic_sim > 0.3:
            reasons.append("Related topics")
        return reasons
