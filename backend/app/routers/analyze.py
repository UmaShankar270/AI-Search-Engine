from base64 import b64decode

import requests
from fastapi import APIRouter, HTTPException

from app.services.ai_service import summarize

router = APIRouter()


@router.get("/analyze/{owner}/{repo}")
def analyze_repository(owner: str, repo: str):
    """Fetch and summarize the repository README from GitHub."""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Repository or README not found"
            )

        raise HTTPException(
            status_code=response.status_code,
            detail="GitHub returned an error while fetching the README"
        )
    except requests.exceptions.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Network error while fetching README: {exc}"
        )

    payload = response.json()
    readme_content = payload.get("content")

    if not readme_content:
        raise HTTPException(
            status_code=404,
            detail="README content is unavailable"
        )

    try:
        clean_content = readme_content.replace("\n", "")
        decoded = b64decode(clean_content).decode(
            "utf-8",
            errors="replace"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to decode README content: {str(e)}"
        )

    summary = summarize(decoded)

    return {
        "repository": f"{owner}/{repo}",
        "summary": summary,
        "readme_length": len(decoded)
    }