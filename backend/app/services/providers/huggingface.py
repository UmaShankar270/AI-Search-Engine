import requests
from typing import Any, Optional
from app.services.providers.base import RepositoryProvider

class HuggingFaceProvider(RepositoryProvider):
    def __init__(self):
        self.base_url = "https://huggingface.co/api"

    def search(self, query: str, language: Optional[str] = None, page: int = 1, per_page: int = 10) -> list[dict[str, Any]]:
        url = f"{self.base_url}/models"
        params = {
            "search": query,
            "limit": per_page,
            "full": "true"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            repos = []
            for item in data:
                normalized = self._normalize(item)
                repos.append(normalized)
            return repos
        except Exception:
            return []

    def getRepository(self, owner: str, repo: str) -> Optional[dict[str, Any]]:
        url = f"{self.base_url}/models/{owner}/{repo}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
            return self._normalize(response.json())
        except Exception:
            return None

    def getReadme(self, owner: str, repo: str) -> Optional[str]:
        url = f"https://huggingface.co/{owner}/{repo}/raw/main/README.md"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass
        return None

    def getMetadata(self, owner: str, repo: str) -> dict[str, Any]:
        return {}

    def _normalize(self, item: dict[str, Any]) -> dict[str, Any]:
        full_id = item.get("id", "")
        parts = full_id.split("/")
        if len(parts) > 1:
            owner = parts[0]
            name = parts[1]
        else:
            owner = item.get("author") or "unknown"
            name = full_id

        tags = item.get("tags", [])
        
        license_name = None
        for t in tags:
            if t.startswith("license:"):
                license_name = t.replace("license:", "").upper()
                break

        downloads = item.get("downloads", 0)
        likes = item.get("likes", 0)
        
        desc = f"Hugging Face Model Hub repository. Likes: {likes}. Downloads: {downloads}."
        if tags:
            desc += f" Tags: {', '.join(tags[:6])}."
        
        return {
            "name": name,
            "full_name": full_id,
            "owner": owner,
            "description": desc,
            "stars": likes,
            "forks": downloads // 20,
            "watchers": likes,
            "language": "Python",
            "open_issues": 0,
            "url": f"https://huggingface.co/{full_id}",
            "platform": "Hugging Face",
            "topics": tags[:12],
            "last_updated": item.get("lastModified") or "",
            "license": license_name
        }
