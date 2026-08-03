import requests
from typing import Any, Optional
from app.services.providers.base import RepositoryProvider

class BitbucketProvider(RepositoryProvider):
    def __init__(self):
        self.base_url = "https://api.bitbucket.org/2.0"

    def search(self, query: str, language: Optional[str] = None, page: int = 1, per_page: int = 10) -> list[dict[str, Any]]:
        # Bitbucket search uses query language (role queries)
        # E.g. name ~ "video editor" OR description ~ "video editor"
        query_str = f'name ~ "{query}" OR description ~ "{query}"'
        url = f"{self.base_url}/repositories"
        params = {
            "q": query_str,
            "page": page,
            "pagelen": per_page
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            data = response.json()
            repos = []
            for item in data.get("values", []):
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
        url = f"{self.base_url}/repositories/{owner}/{repo}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
            return self._normalize(response.json())
        except Exception:
            return None

    def getReadme(self, owner: str, repo: str) -> Optional[str]:
        # Try master and main branches
        for branch in ["main", "master", "default"]:
            for filename in ["README.md", "readme.md", "README.rst"]:
                url = f"{self.base_url}/repositories/{owner}/{repo}/src/{branch}/{filename}"
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
        # Owner nickname/username extraction
        owner_obj = item.get("owner", {})
        owner_name = owner_obj.get("nickname") or owner_obj.get("username") or owner_obj.get("display_name") or "unknown"
        
        # Link extraction
        html_link = item.get("links", {}).get("html", {}).get("href", "")
        
        # In Bitbucket v2 API, main language is in 'language'
        return {
            "name": item.get("name", ""),
            "full_name": item.get("full_name", f"{owner_name}/{item.get('name', '')}"),
            "owner": owner_name,
            "description": item.get("description") or "",
            "stars": 0,  # Bitbucket v2 API doesn't return stars count directly
            "forks": 0,
            "watchers": 0,
            "language": item.get("language") or "Unknown",
            "open_issues": 0,
            "url": html_link,
            "platform": "Bitbucket",
            "topics": [],
            "last_updated": item.get("updated_on") or "",
            "license": None
        }
