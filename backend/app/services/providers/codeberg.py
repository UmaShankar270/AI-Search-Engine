import requests
from typing import Any, Optional
from app.services.providers.base import RepositoryProvider

class CodebergProvider(RepositoryProvider):
    def __init__(self):
        self.base_url = "https://codeberg.org/api/v1"

    def search(self, query: str, language: Optional[str] = None, page: int = 1, per_page: int = 10) -> list[dict[str, Any]]:
        url = f"{self.base_url}/repos/search"
        params = {
            "q": query,
            "page": page,
            "limit": per_page
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            # Gitea search returns a list directly or inside a dictionary.
            # Usually it returns a list of repo dictionaries.
            data = response.json()
            repos = []
            
            # If Gitea returns pagination wrapper (though usually it returns a list directly):
            items = data if isinstance(data, list) else data.get("data", [])
            for item in items:
                normalized = self._normalize(item)
                # Post-filter by language
                if language and language != "All":
                    lang = normalized.get("language", "") or ""
                    if lang.lower() != language.lower():
                        continue
                repos.append(normalized)
            return repos
        except Exception:
            return []

    def getRepository(self, owner: str, repo: str) -> Optional[dict[str, Any]]:
        url = f"{self.base_url}/repos/{owner}/{repo}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
            return self._normalize(response.json())
        except Exception:
            return None

    def getReadme(self, owner: str, repo: str) -> Optional[str]:
        # Gitea provides a direct raw readme or raw file download
        # E.g. /repos/{owner}/{repo}/raw/README.md
        for filename in ["README.md", "readme.md", "README.rst"]:
            url = f"{self.base_url}/repos/{owner}/{repo}/raw/{filename}"
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
        owner_name = item.get("owner", {}).get("login") or item.get("owner", {}).get("username") or "unknown"
        return {
            "name": item.get("name", ""),
            "full_name": item.get("full_name", f"{owner_name}/{item.get('name', '')}"),
            "owner": owner_name,
            "description": item.get("description") or "",
            "stars": item.get("stars_count", 0),
            "forks": item.get("forks_count", 0),
            "watchers": item.get("watchers_count", 0),
            "language": item.get("language") or "Unknown",
            "open_issues": item.get("open_issues_count", 0) or 0,
            "url": item.get("html_url", ""),
            "platform": "Codeberg",
            "topics": item.get("topics") or [],
            "last_updated": item.get("updated_at") or "",
            "license": item.get("license") if isinstance(item.get("license"), str) else None
        }
