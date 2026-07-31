import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class CompareRequest(BaseModel):
    repo_a: str
    repo_b: str
    owner_a: str | None = None
    owner_b: str | None = None


def _resolve_repo_ref(repo_value: str, owner_value: str | None) -> str:
    if "/" in repo_value:
        return repo_value
    if owner_value and repo_value:
        return f"{owner_value}/{repo_value}"
    raise HTTPException(status_code=422, detail="Both repository and owner are required")


@router.get("/compare")
def compare(repo1: str, repo2: str):
    owner1, repo_name1 = repo1.split("/")
    owner2, repo_name2 = repo2.split("/")

    url1 = f"https://api.github.com/repos/{owner1}/{repo_name1}"
    url2 = f"https://api.github.com/repos/{owner2}/{repo_name2}"

    data1 = requests.get(url1, timeout=10).json()
    data2 = requests.get(url2, timeout=10).json()

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


@router.post("/compare")
def compare_post(payload: CompareRequest):
    repo_ref1 = _resolve_repo_ref(payload.repo_a, payload.owner_a)
    repo_ref2 = _resolve_repo_ref(payload.repo_b, payload.owner_b)

    owner1, repo_name1 = repo_ref1.split("/")
    owner2, repo_name2 = repo_ref2.split("/")

    url1 = f"https://api.github.com/repos/{owner1}/{repo_name1}"
    url2 = f"https://api.github.com/repos/{owner2}/{repo_name2}"

    data1 = requests.get(url1, timeout=10).json()
    data2 = requests.get(url2, timeout=10).json()

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
