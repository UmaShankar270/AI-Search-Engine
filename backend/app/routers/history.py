from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.database_models import SearchHistory

router = APIRouter()


@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    history = db.query(SearchHistory).order_by(
        SearchHistory.searched_at.desc()
    ).all()

    return history

@router.delete("/history")
def delete_history(db: Session = Depends(get_db)):
    db.query(SearchHistory).delete()
    db.commit()

    return {
        "message": "Search history cleared successfully"
    }