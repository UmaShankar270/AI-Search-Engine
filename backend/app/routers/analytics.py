from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.database_models import SearchHistory, FavoriteRepository

router = APIRouter()

@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total_searches = db.query(SearchHistory).count()
    total_favorites = db.query(FavoriteRepository).count()

    recent_searches = (
        db.query(SearchHistory)
        .order_by(SearchHistory.id.desc())
        .limit(5)
        .all()
    )

    top_queries = (
        db.query(SearchHistory.query, func.count(SearchHistory.query).label("count"))
        .group_by(SearchHistory.query)
        .order_by(func.count(SearchHistory.query).desc())
        .limit(10)
        .all()
    )

    all_queries = db.query(SearchHistory.query).all()
    avg_len = sum(len(q[0]) for q in all_queries) / len(all_queries) if all_queries else 0.0

    top_favorited_owners = (
        db.query(FavoriteRepository.owner, func.count(FavoriteRepository.owner).label("count"))
        .group_by(FavoriteRepository.owner)
        .order_by(func.count(FavoriteRepository.owner).desc())
        .limit(5)
        .all()
    )

    return {
        "total_searches": total_searches,
        "total_favorites": total_favorites,
        "average_query_length": round(avg_len, 2),
        "recent_searches": [
            {
                "query": s.query,
                "searched_at": s.searched_at
            }
            for s in recent_searches
        ],
        "top_queries": [
            {
                "query": q,
                "count": count
            }
            for q, count in top_queries
        ],
        "top_favorited_owners": [
            {
                "owner": owner,
                "count": count
            }
            for owner, count in top_favorited_owners
        ]
    }