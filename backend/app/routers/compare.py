import requests
from fastapi import APIRouter

router = APIRouter()

@router.get("/compare")
def compare(repo1: str, repo2: str):

    owner1, repo_name1 = repo1.split("/")
    owner2, repo_name2 = repo2.split("/")

    url1 = f"https://api.github.com/repos/{owner1}/{repo_name1}"
    url2 = f"https://api.github.com/repos/{owner2}/{repo_name2}"

    data1 = requests.get(url1).json()
    data2 = requests.get(url2).json()

    return {
        "repo1": {
            "name": data1["full_name"],
            "stars": data1["stargazers_count"],
            "forks": data1["forks_count"],
            "language": data1["language"]
        },
        "repo2": {
            "name": data2["full_name"],
            "stars": data2["stargazers_count"],
            "forks": data2["forks_count"],
            "language": data2["language"]
        }
    }
