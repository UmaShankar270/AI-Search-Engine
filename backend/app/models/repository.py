from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class RepositoryResponse(BaseModel):
    id: Optional[str] = None
    owner: str
    name: str
    full_name: str
    description: Optional[str] = None
    stars: int
    forks: int
    open_issues: int
    watchers: int
    license: Optional[str] = None
    language: Optional[str] = None
    avatar: Optional[str] = None
    lastUpdated: Optional[str] = None
    topics: List[str] = []
    url: str
    matchScore: Optional[int] = 0
    matchReasonBullets: List[str] = []
    size: Optional[str] = None
    defaultBranch: Optional[str] = "main"
    latestRelease: Optional[str] = None
    visibility: Optional[str] = "Public"
    createdDate: Optional[str] = None
    about: Optional[str] = None
    homepageUrl: Optional[str] = None
    readmeHtml: Optional[str] = None
    aiAnalysis: Optional[Dict[str, Any]] = None
    contributors: List[Dict[str, Any]] = []
    activity: Optional[Dict[str, Any]] = None
    languages: List[Dict[str, Any]] = []