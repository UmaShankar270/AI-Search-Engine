"""Tests for the Recommendation Engine module."""

import math
from typing import Any

import numpy as np
import pytest

from ai.recommendation.engine import RecommendationEngine
from ai.recommendation.models import Recommendation, RecommendationSet, UserProfile
from ai.recommendation.similarity import (
    AggregatedSimilarity,
    CosineSimilarity,
    TopicSimilarity,
)

# ============================================================================
# Models
# ============================================================================

class TestRecommendationModel:
    def test_default_values(self) -> None:
        rec = Recommendation(repo_id="fastapi", score=0.95)
        assert rec.repo_id == "fastapi"
        assert rec.score == 0.95
        assert rec.reason == ""
        assert rec.similarity_score == 0.0
        assert rec.popularity_score == 0.0
        assert rec.matched_topics == []

    def test_to_dict(self) -> None:
        rec = Recommendation(
            repo_id="fastapi",
            score=0.95,
            reason="Shared topics",
            similarity_score=0.95,
            popularity_score=0.5,
            language="Python",
            matched_topics=["api", "python"],
        )
        d = rec.to_dict()
        assert d["repo_id"] == "fastapi"
        assert d["score"] == 0.95
        assert d["reason"] == "Shared topics"
        assert d["similarity_score"] == 0.95
        assert d["popularity_score"] == 0.5
        assert d["language"] == "Python"
        assert "matched_topics" in d

    def test_to_dict_rounds_floats(self) -> None:
        rec = Recommendation(repo_id="x", score=0.12345678)
        assert rec.to_dict()["score"] == 0.123457


class TestRecommendationSetModel:
    def test_default_values(self) -> None:
        rs = RecommendationSet(source="repo:fastapi")
        assert rs.source == "repo:fastapi"
        assert rs.recommendations == []
        assert rs.total_candidates == 0
        assert rs.processing_time_ms == 0.0
        assert rs.strategy == "content_based"

    def test_to_dict(self) -> None:
        rec = Recommendation(repo_id="flask", score=0.85)
        rs = RecommendationSet(
            source="repo:fastapi",
            recommendations=[rec],
            total_candidates=10,
            processing_time_ms=5.2,
            strategy="content_based",
        )
        d = rs.to_dict()
        assert d["source"] == "repo:fastapi"
        assert len(d["recommendations"]) == 1
        assert d["recommendations"][0]["repo_id"] == "flask"
        assert d["total_candidates"] == 10
        assert d["strategy"] == "content_based"
        assert d["processing_time_ms"] == 5.2


class TestUserProfileModel:
    def test_default_values(self) -> None:
        p = UserProfile()
        assert p.preferred_languages == []
        assert p.preferred_topics == []
        assert p.weighted_tags == {}
        assert p.liked_repos == []

    def test_to_dict(self) -> None:
        p = UserProfile(
            preferred_languages=["Python", "TypeScript"],
            preferred_topics=["api", "web"],
            weighted_tags={"machine-learning": 2.0},
        )
        d = p.to_dict()
        assert d["preferred_languages"] == ["Python", "TypeScript"]
        assert d["weighted_tags"]["machine-learning"] == 2.0


# ============================================================================
# Similarity
# ============================================================================

class TestCosineSimilarity:
    def test_identical_vectors(self) -> None:
        cs = CosineSimilarity()
        v = np.array([1.0, 2.0, 3.0])
        assert cs.compute(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self) -> None:
        cs = CosineSimilarity()
        a = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        assert cs.compute(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self) -> None:
        cs = CosineSimilarity()
        a = np.array([1.0, 0.0])
        b = np.array([-1.0, 0.0])
        assert cs.compute(a, b) == pytest.approx(-1.0)

    def test_similar_vectors(self) -> None:
        cs = CosineSimilarity()
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([1.1, 2.1, 3.1])
        assert cs.compute(a, b) == pytest.approx(0.999, abs=1e-3)

    def test_zero_vector_returns_zero(self) -> None:
        cs = CosineSimilarity()
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([1.0, 2.0, 3.0])
        assert cs.compute(a, b) == 0.0

    def test_both_zero_vectors_returns_zero(self) -> None:
        cs = CosineSimilarity()
        a = np.array([0.0, 0.0])
        b = np.array([0.0, 0.0])
        assert cs.compute(a, b) == 0.0

    def test_raises_on_dimension_mismatch(self) -> None:
        cs = CosineSimilarity()
        a = np.array([1.0, 2.0])
        b = np.array([1.0, 2.0, 3.0])
        with pytest.raises(ValueError, match="Shape mismatch"):
            cs.compute(a, b)

    def test_raises_on_non_1d(self) -> None:
        cs = CosineSimilarity()
        a = np.array([[1.0, 2.0], [3.0, 4.0]])
        b = np.array([1.0, 2.0])
        with pytest.raises(ValueError, match="1-dimensional"):
            cs.compute(a, b)

    def test_similarity_matrix(self) -> None:
        cs = CosineSimilarity()
        vectors = [
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([1.0, 1.0, 0.0]),
        ]
        m = cs.compute_similarity_matrix(vectors)
        assert m.shape == (3, 3)
        assert m[0, 0] == pytest.approx(1.0)
        assert m[0, 1] == pytest.approx(0.0)
        assert m[1, 0] == pytest.approx(0.0)
        assert m[0, 2] == pytest.approx(1.0 / math.sqrt(2))

    def test_similarity_matrix_empty(self) -> None:
        cs = CosineSimilarity()
        m = cs.compute_similarity_matrix([])
        assert m.shape == (0, 0)


class TestTopicSimilarity:
    def test_jaccard_identical(self) -> None:
        ts = TopicSimilarity()
        topics = ["python", "api", "web"]
        assert ts.jaccard(topics, topics) == pytest.approx(1.0)

    def test_jaccard_half_overlap(self) -> None:
        ts = TopicSimilarity()
        a = ["python", "api", "web"]
        b = ["python", "javascript", "react"]
        assert ts.jaccard(a, b) == pytest.approx(1.0 / 5.0)

    def test_jaccard_no_overlap(self) -> None:
        ts = TopicSimilarity()
        a = ["python", "api"]
        b = ["rust", "systems"]
        assert ts.jaccard(a, b) == 0.0

    def test_jaccard_empty_topics(self) -> None:
        ts = TopicSimilarity()
        assert ts.jaccard([], ["a"]) == 0.0
        assert ts.jaccard(["a"], []) == 0.0
        assert ts.jaccard([], []) == 0.0

    def test_jaccard_case_insensitive(self) -> None:
        ts = TopicSimilarity()
        a = ["Python", "API"]
        b = ["python", "api"]
        assert ts.jaccard(a, b) == pytest.approx(1.0)

    def test_weighted_jaccard_no_weights(self) -> None:
        ts = TopicSimilarity()
        a = ["python", "api"]
        b = ["python", "rust"]
        assert ts.weighted_jaccard(a, b) == pytest.approx(1.0 / 3.0)

    def test_weighted_jaccard_with_weights(self) -> None:
        ts = TopicSimilarity()
        a = ["python", "api"]
        b = ["python", "rust"]
        weights = {"python": 3.0, "api": 2.0, "rust": 1.0}
        w = ts.weighted_jaccard(a, b, weights)
        assert w == pytest.approx(3.0 / (3.0 + 2.0 + 1.0))

    def test_overlap_coefficient(self) -> None:
        ts = TopicSimilarity()
        a = ["python", "api", "web", "fast"]
        b = ["python", "api", "rust"]
        assert ts.overlap_coefficient(a, b) == pytest.approx(2.0 / 3.0)

    def test_overlap_coefficient_no_overlap(self) -> None:
        ts = TopicSimilarity()
        assert ts.overlap_coefficient(["a"], ["b"]) == 0.0

    def test_overlap_coefficient_empty(self) -> None:
        ts = TopicSimilarity()
        assert ts.overlap_coefficient([], ["a"]) == 0.0


class TestAggregatedSimilarity:
    def test_default_weights_sum_to_one(self) -> None:
        agg = AggregatedSimilarity()
        assert sum(agg.weights.values()) == pytest.approx(1.0)

    def test_default_weights(self) -> None:
        agg = AggregatedSimilarity()
        assert agg.weights["embedding"] == 0.60
        assert agg.weights["topic"] == 0.25
        assert agg.weights["language"] == 0.15

    def test_custom_weights_normalized(self) -> None:
        agg = AggregatedSimilarity(embedding_weight=0.5, topic_weight=0.5, language_weight=0.5)
        assert sum(agg.weights.values()) == pytest.approx(1.0)
        assert agg.weights["embedding"] == pytest.approx(0.5 / 1.5)
        assert agg.weights["topic"] == pytest.approx(0.5 / 1.5)

    def test_compute_perfect_match(self) -> None:
        agg = AggregatedSimilarity()
        score = agg.compute(embedding_sim=1.0, topic_sim=1.0, same_language=True)
        assert score == pytest.approx(1.0)

    def test_compute_no_match(self) -> None:
        agg = AggregatedSimilarity()
        score = agg.compute(embedding_sim=0.0, topic_sim=0.0, same_language=False)
        assert score == pytest.approx(0.0)

    def test_compute_with_language_only(self) -> None:
        agg = AggregatedSimilarity()
        score = agg.compute(embedding_sim=0.0, topic_sim=0.0, same_language=True)
        assert score == pytest.approx(0.15)


# ============================================================================
# Engine - Helpers
# ============================================================================

def _make_repo(
    repo_id: str,
    topics: list[str] | None = None,
    language: str = "",
    stars: int = 0,
    forks: int = 0,
    contributors: int = 0,
) -> dict[str, Any]:
    return {
        "repo_id": repo_id,
        "topics": topics or [],
        "language": language,
        "stars": stars,
        "forks": forks,
        "contributors": contributors,
        "name": repo_id,
        "description": f"Description for {repo_id}",
    }


def _make_embedding_map(repo_ids: list[str]) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(42)
    return {rid: rng.random(384).astype(np.float32) for rid in repo_ids}


# ============================================================================
# Engine - recommend_from_repo
# ============================================================================

class TestRecommendFromRepo:
    def test_returns_recommendations(self) -> None:
        repos = [_make_repo("source", topics=["python"]), _make_repo("target", topics=["python"])]
        emb = _make_embedding_map(["source", "target"])
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("source", repos, emb, top_n=5)
        assert result.source == "repo:source"
        assert len(result.recommendations) == 1
        assert result.recommendations[0].repo_id == "target"
        assert result.strategy == "content_based"

    def test_excludes_source_repo(self) -> None:
        repos = [_make_repo("only")]
        emb = _make_embedding_map(["only"])
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("only", repos, emb)
        assert len(result.recommendations) == 0

    def test_excludes_ids(self) -> None:
        repos = [
            _make_repo("source", topics=["python"]),
            _make_repo("a", topics=["python"]),
            _make_repo("b", topics=["python"]),
        ]
        emb = _make_embedding_map(["source", "a", "b"])
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("source", repos, emb, exclude_ids={"a"})
        assert len(result.recommendations) == 1
        assert result.recommendations[0].repo_id == "b"

    def test_respects_top_n(self) -> None:
        repos = [_make_repo(f"r{i}") for i in range(10)]
        emb = _make_embedding_map([f"r{i}" for i in range(10)])
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("r0", repos, emb, top_n=3)
        assert len(result.recommendations) <= 3

    def test_missing_source_embedding_returns_empty(self) -> None:
        repos = [_make_repo("source")]
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("source", repos, {})
        assert len(result.recommendations) == 0
        assert result.total_candidates == 0

    def test_skips_repos_without_embeddings(self) -> None:
        repos = [
            _make_repo("source", topics=["python"]),
            _make_repo("has_emb", topics=["python"]),
            _make_repo("no_emb", topics=["python"]),
        ]
        emb = {"source": np.array([1.0, 0.0]), "has_emb": np.array([1.0, 0.1])}
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("source", repos, emb)
        found_ids = [r.repo_id for r in result.recommendations]
        assert "has_emb" in found_ids
        assert "no_emb" not in found_ids

    def test_returns_sorted_by_score_descending(self) -> None:
        repos = [
            _make_repo("source", topics=["python"]),
            _make_repo("close", topics=["python"]),
            _make_repo("far", topics=["rust"]),
        ]
        emb = {
            "source": np.array([1.0, 0.0, 0.0]),
            "close": np.array([0.9, 0.1, 0.0]),
            "far": np.array([0.0, 1.0, 0.0]),
        }
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("source", repos, emb, top_n=5)
        assert len(result.recommendations) == 2
        assert result.recommendations[0].score >= result.recommendations[1].score

    def test_topic_overlap_boost(self) -> None:
        repos = [
            _make_repo("source", topics=["python", "api"]),
            _make_repo("match_topics", topics=["python", "api", "web"]),
            _make_repo("no_topic", topics=["rust", "systems"]),
        ]
        emb = {
            "source": np.array([1.0, 0.0]),
            "match_topics": np.array([0.8, 0.2]),
            "no_topic": np.array([0.7, 0.3]),
        }
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("source", repos, emb, top_n=5)
        assert result.recommendations[0].repo_id == "match_topics"

    def test_reason_highly_similar(self) -> None:
        repos = [_make_repo("source", topics=["a"]), _make_repo("t", topics=["a"])]
        emb = {"source": np.array([1.0, 0.0]), "t": np.array([1.0, 0.001])}
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("source", repos, emb)
        assert "Highly similar" in result.recommendations[0].reason

    def test_reason_same_language(self) -> None:
        repos = [
            _make_repo("source", language="Python"),
            _make_repo("t", topics=["python"], language="Python"),
        ]
        emb = {"source": np.array([1.0, 0.0]), "t": np.array([0.5, 0.5])}
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("source", repos, emb)
        assert "Same language" in result.recommendations[0].reason

    def test_total_candidates_counted(self) -> None:
        repos = [_make_repo(f"r{i}", topics=["python"]) for i in range(5)]
        emb = _make_embedding_map([f"r{i}" for i in range(5)])
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("r0", repos, emb)
        assert result.total_candidates == 4

    def test_processing_time_nonzero(self) -> None:
        repos = [_make_repo(f"r{i}") for i in range(20)]
        emb = _make_embedding_map([f"r{i}" for i in range(20)])
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("r0", repos, emb, top_n=5)
        assert result.processing_time_ms > 0


# ============================================================================
# Engine - recommend_from_query
# ============================================================================

class TestRecommendFromQuery:
    def test_returns_recommendations(self) -> None:
        repos = [_make_repo("r1"), _make_repo("r2")]
        emb = _make_embedding_map(["r1", "r2"])
        engine = RecommendationEngine()
        qvec = np.array([1.0, 0.0] + [0.0] * 382, dtype=np.float32)
        result = engine.recommend_from_query(qvec, repos, emb, top_n=5)
        assert len(result.recommendations) == 2
        assert result.strategy == "query_based"
        assert result.source == "query"

    def test_respects_top_n(self) -> None:
        repos = [_make_repo(f"r{i}") for i in range(10)]
        emb = _make_embedding_map([f"r{i}" for i in range(10)])
        engine = RecommendationEngine()
        qvec = np.random.default_rng(0).random(384).astype(np.float32)
        result = engine.recommend_from_query(qvec, repos, emb, top_n=3)
        assert len(result.recommendations) == 3

    def test_excludes_ids(self) -> None:
        repos = [
            _make_repo("a", topics=["py"]),
            _make_repo("b", topics=["py"]),
            _make_repo("c", topics=["py"]),
        ]
        emb = _make_embedding_map(["a", "b", "c"])
        engine = RecommendationEngine()
        qvec = np.random.default_rng(0).random(384).astype(np.float32)
        result = engine.recommend_from_query(qvec, repos, emb, exclude_ids={"a"})
        found = [r.repo_id for r in result.recommendations]
        assert "a" not in found

    def test_reason_includes_score(self) -> None:
        repos = [_make_repo("r1")]
        emb = _make_embedding_map(["r1"])
        engine = RecommendationEngine()
        qvec = np.array([1.0, 0.0] + [0.0] * 382, dtype=np.float32)
        result = engine.recommend_from_query(qvec, repos, emb)
        assert "Semantic similarity" in result.recommendations[0].reason

    def test_skips_missing_embeddings(self) -> None:
        repos = [_make_repo("has_emb"), _make_repo("no_emb")]
        emb = {"has_emb": np.array([1.0, 0.0])}
        engine = RecommendationEngine()
        qvec = np.array([1.0, 0.0])
        result = engine.recommend_from_query(qvec, repos, emb)
        assert len(result.recommendations) == 1
        assert result.recommendations[0].repo_id == "has_emb"

    def test_empty_result_when_no_embeddings(self) -> None:
        repos = [_make_repo("r1")]
        engine = RecommendationEngine()
        qvec = np.array([1.0, 0.0])
        result = engine.recommend_from_query(qvec, repos, {})
        assert len(result.recommendations) == 0


# ============================================================================
# Engine - recommend_hybrid
# ============================================================================

class TestRecommendHybrid:
    def test_returns_recommendations(self) -> None:
        repos = [
            _make_repo("source", topics=["python"], language="Python", stars=1000),
            _make_repo("target", topics=["python"], language="Python", stars=500),
        ]
        emb = _make_embedding_map(["source", "target"])
        engine = RecommendationEngine()
        result = engine.recommend_hybrid("source", repos, emb, top_n=5)
        assert len(result.recommendations) == 1
        assert result.strategy == "hybrid"

    def test_with_user_profile(self) -> None:
        repos = [
            _make_repo("source", topics=["python"], language="Python"),
            _make_repo("target", topics=["python", "ml"], language="Python"),
        ]
        emb = _make_embedding_map(["source", "target"])
        profile = UserProfile(
            preferred_languages=["Python"],
            preferred_topics=["ml"],
            weighted_tags={"ml": 2.0},
        )
        engine = RecommendationEngine()
        result = engine.recommend_hybrid("source", repos, emb, user_profile=profile)
        assert len(result.recommendations) > 0

    def test_missing_source_embedding_returns_empty(self) -> None:
        repos = [_make_repo("source")]
        engine = RecommendationEngine()
        result = engine.recommend_hybrid("source", repos, {})
        assert len(result.recommendations) == 0
        assert result.total_candidates == 0

    def test_popularity_high_stars_boost(self) -> None:
        repos = [
            _make_repo("source", topics=["python"], stars=1),
            _make_repo("popular", topics=["python"], stars=100000),
            _make_repo("unpopular", topics=["python"], stars=1),
        ]
        emb = {
            "source": np.array([1.0, 0.0]),
            "popular": np.array([0.6, 0.4]),
            "unpopular": np.array([0.6, 0.4]),
        }
        engine = RecommendationEngine()
        result = engine.recommend_hybrid("source", repos, emb, top_n=5)
        assert result.recommendations[0].repo_id == "popular"

    def test_profile_score_affects_ordering(self) -> None:
        repos = [
            _make_repo("source", topics=["a"]),
            _make_repo("r1", topics=["python", "ml"], language="Python", stars=10),
            _make_repo("r2", topics=["rust", "systems"], language="Rust", stars=10),
        ]
        emb = {
            "source": np.array([1.0, 0.0]),
            "r1": np.array([0.5, 0.5]),
            "r2": np.array([0.5, 0.5]),
        }
        profile = UserProfile(
            preferred_languages=["Python"],
            preferred_topics=["ml"],
            weighted_tags={"ml": 2.0},
        )
        engine = RecommendationEngine()
        result = engine.recommend_hybrid(
            "source", repos, emb, user_profile=profile, top_n=5
        )
        assert result.recommendations[0].repo_id == "r1"

    def test_profile_zero_when_no_profile(self) -> None:
        repos = [
            _make_repo("source", topics=["python"]),
            _make_repo("target", topics=["python"]),
        ]
        emb = _make_embedding_map(["source", "target"])
        engine = RecommendationEngine()
        result = engine.recommend_hybrid("source", repos, emb)
        rec = result.recommendations[0]
        assert rec.popularity_score >= 0.0
        assert rec.similarity_score >= 0.0


# ============================================================================
# Engine - recommend_popular
# ============================================================================

class TestRecommendPopular:
    def test_returns_top_by_stars(self) -> None:
        repos = [_make_repo(f"r{i}", stars=i * 100) for i in range(1, 6)]
        engine = RecommendationEngine()
        result = engine.recommend_popular(repos, top_n=3, sort_key="stars")
        assert len(result.recommendations) == 3
        assert result.recommendations[0].repo_id == "r5"
        assert result.strategy == "popular"

    def test_respects_top_n(self) -> None:
        repos = [_make_repo(f"r{i}", stars=i) for i in range(10)]
        engine = RecommendationEngine()
        result = engine.recommend_popular(repos, top_n=3)
        assert len(result.recommendations) == 3

    def test_scores_normalized_by_max(self) -> None:
        repos = [
            _make_repo("top", stars=100),
            _make_repo("mid", stars=50),
            _make_repo("low", stars=10),
        ]
        engine = RecommendationEngine()
        result = engine.recommend_popular(repos, top_n=3)
        assert result.recommendations[0].score == 1.0
        assert result.recommendations[1].score == 0.5
        assert result.recommendations[2].score == 0.1

    def test_empty_repos_returns_empty(self) -> None:
        engine = RecommendationEngine()
        result = engine.recommend_popular([])
        assert len(result.recommendations) == 0
        assert result.total_candidates == 0

    def test_custom_sort_key(self) -> None:
        repos = [
            _make_repo("a", forks=10, stars=100),
            _make_repo("b", forks=50, stars=10),
        ]
        engine = RecommendationEngine()
        result = engine.recommend_popular(repos, top_n=2, sort_key="forks")
        assert result.recommendations[0].repo_id == "b"

    def test_processing_time_nonzero(self) -> None:
        repos = [_make_repo(f"r{i}", stars=i) for i in range(100)]
        engine = RecommendationEngine()
        result = engine.recommend_popular(repos, top_n=5)
        assert result.processing_time_ms > 0


# ============================================================================
# Engine - popularity score
# ============================================================================

class TestPopularityScore:
    def test_popularity_increases_with_stars(self) -> None:
        engine = RecommendationEngine()
        low = engine._compute_popularity_score({"stars": 1, "forks": 0, "contributors": 0})
        high = engine._compute_popularity_score(
            {"stars": 100000, "forks": 5000, "contributors": 500},
        )
        assert high > low

    def test_popularity_between_0_and_1(self) -> None:
        engine = RecommendationEngine()
        for stars, forks, contribs in [
            (0, 0, 0), (1, 0, 0), (100, 10, 5), (1000000, 100000, 10000),
        ]:
            score = engine._compute_popularity_score({
                "stars": stars, "forks": forks, "contributors": contribs,
            })
            assert 0.0 <= score <= 1.0


# ============================================================================
# Engine - profile score
# ============================================================================

class TestProfileScore:
    def test_language_match(self) -> None:
        engine = RecommendationEngine()
        repo = {"language": "Python", "topics": []}
        profile = UserProfile(preferred_languages=["Python"])
        score = engine._compute_profile_score(repo, profile)
        assert score > 0.0

    def test_language_no_match(self) -> None:
        engine = RecommendationEngine()
        repo = {"language": "Rust", "topics": []}
        profile = UserProfile(preferred_languages=["Python"])
        score = engine._compute_profile_score(repo, profile)
        assert score == 0.0

    def test_topic_match(self) -> None:
        engine = RecommendationEngine()
        repo = {"language": "", "topics": ["ml", "python"]}
        profile = UserProfile(preferred_topics=["ml"])
        score = engine._compute_profile_score(repo, profile)
        assert score > 0.0

    def test_weighted_tags(self) -> None:
        engine = RecommendationEngine()
        repo = {"language": "", "topics": ["machine-learning"]}
        profile = UserProfile(weighted_tags={"machine-learning": 2.0, "web": 1.0})
        score = engine._compute_profile_score(repo, profile)
        assert score > 0.0

    def test_no_profile_returns_zero(self) -> None:
        engine = RecommendationEngine()
        score = engine._compute_profile_score({"language": "Python", "topics": []}, None)
        assert score == 0.0

    def test_no_preferences_returns_zero(self) -> None:
        engine = RecommendationEngine()
        score = engine._compute_profile_score(
            {"language": "Python", "topics": ["ml"]},
            UserProfile(),
        )
        assert score == 0.0


# ============================================================================
# Engine - topic_set
# ============================================================================

class TestTopicSet:
    def test_returns_matched_topics(self) -> None:
        engine = RecommendationEngine()
        repos = [
            {"repo_id": "a", "topics": ["python", "api"]},
            {"repo_id": "b", "topics": ["python", "web"]},
            {"repo_id": "c", "topics": ["rust"]},
        ]
        result = engine._topic_set(
            ["python", "api"],
            np.array([1.0, 0.0]),
            repos,
            {"a": np.array([1.0, 0.0]), "b": np.array([0.5, 0.5]), "c": np.array([0.0, 1.0])},
            top_n=5,
        )
        assert "a" in result
        assert "b" in result
        assert "c" not in result
        assert "python" in result["a"]


# ============================================================================
# Edge cases
# ============================================================================

class TestEdgeCases:
    def test_single_repo(self) -> None:
        repos = [_make_repo("only")]
        emb = _make_embedding_map(["only"])
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("only", repos, emb)
        assert len(result.recommendations) == 0

    def test_duplicate_repo_ids(self) -> None:
        repos = [
            _make_repo("dup", topics=["a"]),
            _make_repo("dup", topics=["b"]),
        ]
        emb = {"dup": np.array([1.0, 0.0])}
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("dup", repos, emb)
        assert len(result.recommendations) == 0

    def test_large_topic_lists(self) -> None:
        repos = [
            _make_repo("source", topics=[f"t{i}" for i in range(100)]),
            _make_repo("target", topics=[f"t{i}" for i in range(100)]),
        ]
        emb = _make_embedding_map(["source", "target"])
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("source", repos, emb)
        assert len(result.recommendations) == 1

    def test_all_without_embeddings(self) -> None:
        repos = [_make_repo("a"), _make_repo("b")]
        engine = RecommendationEngine()
        result = engine.recommend_from_repo("a", repos, {})
        assert len(result.recommendations) == 0

    def test_consistency(self) -> None:
        repos = [_make_repo(f"r{i}", topics=["python"], stars=i * 10) for i in range(10)]
        emb = _make_embedding_map([f"r{i}" for i in range(10)])
        engine = RecommendationEngine()
        r1 = engine.recommend_from_repo("r0", repos, emb, top_n=5)
        r2 = engine.recommend_from_repo("r0", repos, emb, top_n=5)
        ids1 = [r.repo_id for r in r1.recommendations]
        ids2 = [r.repo_id for r in r2.recommendations]
        assert ids1 == ids2
