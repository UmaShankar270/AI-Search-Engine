from pydantic import BaseModel
from typing import Optional


class RepositoryResponse(BaseModel):
    name: str
    full_name: str
    description: Optional[str] = None
    stars: int
    forks: int
    watchers: int
    language: Optional[str] = None
    open_issues: int
    url: str