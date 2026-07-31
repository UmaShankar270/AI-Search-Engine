import requests
<<<<<<< HEAD
from fastapi import APIRouter, HTTPException
=======
from app.models.repository import RepositoryResponse
>>>>>>> e0ea162 (Added analytics, favorites, history, trending repositories, pagination, caching and database models)

router = APIRouter()

@router.get(
    "/repo/{owner}/{repo}",
    response_model=RepositoryResponse
)
def repo_details(owner: str, repo: str):

    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Repository not found"
        )

    data = response.json()

    return {
        "name": data["name"],
        "full_name": data["full_name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "watchers": data["watchers_count"],
        "language": data["language"],
        "open_issues": data["open_issues_count"],
        "url": data["html_url"]
    }
