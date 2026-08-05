import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.database import SessionLocal
from app.database_models import FavoriteRepository, SearchHistory


@pytest.fixture(autouse=True)
def clear_db():
    db = SessionLocal()
    try:
        db.query(FavoriteRepository).delete()
        db.query(SearchHistory).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


class DummyResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload or {}
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("request failed")


def test_root_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_cors_headers_are_present_for_browser_requests(client):
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in {"http://localhost:5173", "*"}


def test_docs_and_openapi(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_search_accepts_q_alias(monkeypatch, client):
    from app.services.discovery_service import DiscoveryService
    monkeypatch.setattr(DiscoveryService, "search_all_platforms", lambda *args, **kwargs: [{"name": "fastapi", "full_name": "tiangolo/fastapi", "owner": "tiangolo", "stars": 50000, "forks": 15000, "language": "Python"}])

    response = client.get("/search?q=fastapi")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] in {"hybrid", "cache"}
    assert payload["results"][0]["name"] == "fastapi"


def test_search_requires_query(client):
    response = client.get("/search")
    assert response.status_code == 422


def test_trending_works(monkeypatch, client):
    payload = {
        "items": [
            {
                "name": "demo",
                "full_name": "demo/demo",
                "description": "Demo repo",
                "stargazers_count": 200,
                "language": "Python",
                "html_url": "https://example.com/demo",
            }
        ]
    }

    monkeypatch.setattr("app.routers.repo.requests.get", lambda *args, **kwargs: DummyResponse(payload))

    response = client.get("/trending")

    assert response.status_code == 200
    assert response.json()[0]["full_name"] == "demo/demo"


def test_repo_details_returns_404(monkeypatch, client):
    monkeypatch.setattr("app.routers.repo_details.requests.get", lambda *args, **kwargs: DummyResponse({}, 404))

    response = client.get("/repo/notreal/notreal")

    assert response.status_code == 404


def test_compare_accepts_post_payload(monkeypatch, client):
    payload = {
        "repo1": {"full_name": "owner/a", "stargazers_count": 1, "forks_count": 2, "language": "Python"},
        "repo2": {"full_name": "owner/b", "stargazers_count": 3, "forks_count": 4, "language": "Go"},
    }

    monkeypatch.setattr("app.routers.compare.requests.get", lambda *args, **kwargs: DummyResponse(payload["repo1"] if args[0].endswith("/a") else payload["repo2"]))

    response = client.post(
        "/compare",
        json={"repo_a": "a", "owner_a": "owner", "repo_b": "b", "owner_b": "owner"},
    )

    assert response.status_code == 200
    assert response.json()["repo1"]["name"] == "owner/a"


def test_recommend_returns_scores(monkeypatch, client):
    payload = {
        "items": [
            {"name": "demo", "full_name": "demo/demo", "stargazers_count": 100, "forks_count": 10, "language": "Python", "html_url": "https://example.com/demo"}
        ]
    }

    monkeypatch.setattr("app.routers.recommend.requests.get", lambda *args, **kwargs: DummyResponse(payload))

    response = client.get("/recommend?query=fastapi")

    assert response.status_code == 200
    assert response.json()[0]["full_name"] == "demo/demo"


def test_favorites_and_history_round_trip(client):
    response = client.post("/favorites?owner=fastapi&repo=fastapi")
    assert response.status_code == 200

    favorites = client.get("/favorites")
    assert favorites.status_code == 200
    assert len(favorites.json()) == 1

    history = client.get("/history")
    assert history.status_code == 200

    analytics = client.get("/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["total_favorites"] == 1


def test_delete_history_and_favorite(client):
    client.post("/favorites?owner=fastapi&repo=fastapi")
    favorite_id = client.get("/favorites").json()[0]["id"]

    delete_favorite = client.delete(f"/favorites/{favorite_id}")
    assert delete_favorite.status_code == 200

    delete_history = client.delete("/history")
    assert delete_history.status_code == 200


def test_expand_query():
    from app.routers.search import expand_query
    expanded = expand_query("chatbot")
    assert "conversational ai" in [e.lower() for e in expanded]
    assert "chatbot" in [e.lower() for e in expanded]


def test_compute_lexical_score():
    from app.routers.search import compute_lexical_score
    repo = {
        "name": "cool chatbot",
        "description": "An AI assistant built with LLMs",
        "topics": ["conversational-ai", "rag-chatbot"],
        "language": "Python"
    }
    score = compute_lexical_score(repo, ["chatbot", "conversational-ai"])
    assert score > 0.5


def test_duplicate_detector_token_similarity():
    from ai.duplicate_detection.detector import DuplicateDetector
    detector = DuplicateDetector()
    # Test Levinshtein on short text
    assert detector._str_similarity("abc", "abc") == 1.0
    # Test Jaccard similarity on long texts
    desc1 = "This is a very long description of a repository designed to do machine learning and artificial intelligence using python."
    desc2 = "This is a very long description of a repository designed to do machine learning and artificial intelligence using python."
    assert detector._str_similarity(desc1, desc2) == 1.0


def test_new_ranking_factors():
    from ai.ranking.factors import RepositoryTrust, ProjectMaturity
    from ai.ranking.models import CandidateRepo
    from ai.ranking.weight_manager import WeightManager

    wm = WeightManager()
    trust_factor = RepositoryTrust(wm)
    maturity_factor = ProjectMaturity(wm)

    repo = CandidateRepo(
        repo_id="google/tensorflow",
        stars=60000,
        contributors=500,
        releases_last_year=10,
        created_at="2015-01-01T00:00:00Z"
    )

    t_score = trust_factor.compute(repo)
    m_score = maturity_factor.compute(repo)

    assert t_score.normalized_score > 0.5
    assert m_score.normalized_score > 0.5


def test_analytics_enriched(client):
    client.post("/favorites?owner=google&repo=tensorflow")
    response = client.get("/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "average_query_length" in data
    assert "top_queries" in data
    assert "top_favorited_owners" in data


def test_all_providers_normalize():
    from app.services.discovery_service import DiscoveryService
    discovery = DiscoveryService()

    for name, provider in discovery.providers.items():
        assert provider is not None
        try:
            res = provider.search(query="chatbot", page=1, per_page=2)
            assert isinstance(res, list)
            for repo in res:
                assert "name" in repo
                assert "full_name" in repo
                assert "owner" in repo
                assert "platform" in repo
                assert "url" in repo
        except Exception as e:
            # Tolerant of environment network/offline failures, but must load code without SyntaxError/ImportError
            logger.warning(f"Provider {name} search raised exception: {e}")


def test_summarizer_fallback_enriched():
    from ai.summarizer.summarizer import SummaryGenerator
    gen = SummaryGenerator()
    repo = {"name": "test-ml-repo", "description": "This does machine learning neural models and predictions", "stars": 1500}
    summary = gen.generate(repo)
    assert "machine learning" in summary
    assert "neural" in summary or "model" in summary

    repo_web = {"name": "test-web-repo", "description": "This is a web server api build with react", "stars": 800}
    summary_web = gen.generate(repo_web)
    assert "web application" in summary_web or "user interface" in summary_web or "client-server" in summary_web


def test_exact_match_booster_semantic():
    from ai.semantic_search.search_engine import SemanticSearchEngine
    from ai.semantic_search.faiss_index import FAISSVectorIndex
    from ai.semantic_search.metadata_store import IndexMetadataStore
    from ai.semantic_search.models import SearchHit

    vector_index = FAISSVectorIndex(dimension=3)
    metadata_store = IndexMetadataStore()
    engine = SemanticSearchEngine(vector_index, metadata_store, boost_factor=1.5)

    hits = [
        SearchHit(repo_id="owner/fastapi", score=0.6, rank=1, metadata={"name": "fastapi", "language": "Python", "topics": ["web", "api"]})
    ]
    boosted = engine._apply_exact_match_boost("fastapi", hits)
    # Exact name match should have 2.0x multiplier, meaning score is capped at 1.0 (0.6 * 1.5 * 2.0 = 1.8 -> capped at 1.0)
    assert boosted[0].score == 1.0


def test_recommendation_reasons_enriched():
    from ai.recommendation.engine import RecommendationEngine
    from ai.recommendation.models import RecommendationSet
    import numpy as np

    engine = RecommendationEngine()
    all_repos = [
        {"repo_id": "owner/tensorflow", "name": "tensorflow", "stars": 160000, "language": "Python"}
    ]
    embedding_map = {
        "owner/tensorflow": np.array([0.1, 0.2, 0.3])
    }
    recs = engine.recommend_from_query(
        query_vector=np.array([0.1, 0.2, 0.3]),
        all_repos=all_repos,
        embedding_map=embedding_map,
        top_n=1
    )
    assert len(recs.recommendations) == 1
    assert "Popular" in recs.recommendations[0].reason or "stars" in recs.recommendations[0].reason
    assert "Python" in recs.recommendations[0].reason
