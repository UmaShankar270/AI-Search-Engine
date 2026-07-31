from pydantic import BaseModel
from typing import Optional


class RecommendationResponse(BaseModel):
    name: str
    full_name: str
    stars: int
    forks: int
    language: Optional[str] = None
    score: float
    url: str