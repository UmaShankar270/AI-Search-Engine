from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.database_models import FavoriteRepository
from fastapi import HTTPException


router = APIRouter()


@router.post("/favorites")
def add_favorite(
    owner: str,
    repo: str,
    db: Session = Depends(get_db)
):
    favorite = FavoriteRepository(
        owner=owner,
        repo=repo
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return {
        "message": "Repository added to favorites",
        "favorite": favorite
    }

@router.get("/favorites")
def get_favorites(db: Session = Depends(get_db)):
    favorites = db.query(FavoriteRepository).all()
    return favorites

@router.delete("/favorites/{favorite_id}")
def delete_favorite(
    favorite_id: int,
    db: Session = Depends(get_db)
):
    favorite = db.query(FavoriteRepository).filter(
        FavoriteRepository.id == favorite_id
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=404,
            detail="Favorite repository not found"
        )

    db.delete(favorite)
    db.commit()

    return {
        "message": "Favorite repository deleted successfully"
    }