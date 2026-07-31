from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.database_models import SearchHistory, SearchCache
from app.services.github_service import search_repositories

import json

router = APIRouter()


@router.get("/search")
def search(
    query: str,
    language: str = None,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    history = SearchHistory(query=query)
    db.add(history)
    db.commit()

    cache_key = f"{query}_{language}_{page}_{per_page}"

    cached = (
        db.query(SearchCache)
        .filter(SearchCache.query == cache_key)
        .first()
    )

    if cached:
        return {
            "source": "cache",
            "results": json.loads(cached.response)
        }

    results = search_repositories(
        query=query,
        language=language,
        page=page,
        per_page=per_page
    )

    cache = SearchCache(
        query=cache_key,
        response=json.dumps(results)
    )

    db.add(cache)
    db.commit()

    return {
        "source": "github",
        "results": results
    }