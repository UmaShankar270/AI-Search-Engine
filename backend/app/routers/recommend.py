import requests
from fastapi import APIRouter

router = APIRouter()

@router.get("/recommend")
def recommend(query: str):

    url = f"https://api.github.com/search/repositories?q={query}"

    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Failed to fetch repositories"}

    data = response.json()

    repos = []

    for repo in data["items"][:20]:

        stars = repo["stargazers_count"]
        forks = repo["forks_count"]

        score = round((stars * 0.7) + (forks * 0.3), 2)

        repos.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "stars": stars,
            "forks": forks,
            "language": repo["language"],
            "score": score,
            "url": repo["html_url"]
        })

    repos.sort(key=lambda x: x["score"], reverse=True)

    return repos[:5]
