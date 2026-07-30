from fastapi import APIRouter
from app.services.github_service import search_repositories

router = APIRouter()

@router.get("/search")
def search(query: str):
    return search_repositories(query)