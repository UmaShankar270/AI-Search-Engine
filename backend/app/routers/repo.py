import requests
from fastapi import APIRouter

router = APIRouter()

@router.get("/trending")
def trending():
    url = "https://api.github.com/search/repositories"

    response = requests.get(
        url,
        params={
            "q": "stars:>10000",
            "sort": "stars",
            "order": "desc",
            "per_page": "10"
        }
    )

    data = response.json()

    repos = []

    for repo in data["items"]:
        repos.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "description": repo["description"],
            "stars": repo["stargazers_count"],
            "language": repo["language"],
            "url": repo["html_url"]
        })

    return repos
