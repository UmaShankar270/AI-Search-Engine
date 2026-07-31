from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/trending")
def trending():
    url = "https://api.github.com/search/repositories"

    params = {
        "q": "stars:>10000",
        "sort": "stars",
        "order": "desc",
        "per_page": 10
    }

    response = requests.get(url, params=params)

    data = response.json()

    repos = []

    for repo in data["items"]:
        repos.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "stars": repo["stargazers_count"],
            "language": repo["language"],
            "url": repo["html_url"]
        })

    return repos