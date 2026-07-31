from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.database_models import SearchHistory, FavoriteRepository

router = APIRouter()

@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    total_searches = db.query(SearchHistory).count()
    total_favorites = db.query(FavoriteRepository).count()

    recent_searches = (
        db.query(SearchHistory)
        .order_by(SearchHistory.id.desc())
        .limit(5)
        .all()
    )

    return {
        "total_searches": total_searches,
        "total_favorites": total_favorites,
        "recent_searches": [
            {
                "query": s.query,
                "searched_at": s.searched_at
            }
            for s in recent_searches
        ]
    }