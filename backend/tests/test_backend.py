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
    monkeypatch.setattr("app.routers.search.search_repositories", lambda **kwargs: [{"name": "fastapi"}])

    response = client.get("/search?q=fastapi")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] in {"github", "cache"}
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
