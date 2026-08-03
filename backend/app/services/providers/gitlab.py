import requests
from typing import Any, Optional
from app.services.providers.base import RepositoryProvider

class GitLabProvider(RepositoryProvider):
    def __init__(self):
        self.base_url = "https://gitlab.com/api/v4"

    def search(self, query: str, language: Optional[str] = None, page: int = 1, per_page: int = 10) -> list[dict[str, Any]]:
        url = f"{self.base_url}/projects"
        params = {
            "search": query,
            "visibility": "public",
            "page": page,
            "per_page": per_page
        }
        if language and language != "All":
            params["with_programming_language"] = language

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            repos = []
            for item in response.json():
                repos.append(self._normalize(item))
            return repos
        except Exception:
            return []

    def getRepository(self, owner: str, repo: str) -> Optional[dict[str, Any]]:
        # For GitLab, project identifier is often URL-encoded namespace/project_name
        path = f"{owner}/{repo}"
        encoded_path = requests.utils.quote(path, safe="")
        url = f"{self.base_url}/projects/{encoded_path}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
            return self._normalize(response.json())
        except Exception:
            return None

    def getReadme(self, owner: str, repo: str) -> Optional[str]:
        path = f"{owner}/{repo}"
        encoded_path = requests.utils.quote(path, safe="")
        
        # Get project details first to find default branch
        project = self.getRepository(owner, repo)
        default_branch = "main"
        if project and "default_branch" in project:
            default_branch = project["default_branch"]
        elif project and "metadata" in project and "default_branch" in project["metadata"]:
            default_branch = project["metadata"]["default_branch"]

        # Try README.md and readme.md
        for filename in ["README.md", "readme.md", "README.rst"]:
            encoded_file = requests.utils.quote(filename, safe="")
            url = f"{self.base_url}/projects/{encoded_path}/repository/files/{encoded_file}/raw?ref={default_branch}"
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
        path_with_ns = item.get("path_with_namespace", "")
        owner_name = path_with_ns.split("/")[0] if "/" in path_with_ns else "unknown"
        
        # GitLab ratings are not directly available, so we use star_count
        stars = item.get("star_count", 0)
        forks = item.get("forks_count", 0)
        
        return {
            "name": item.get("name", ""),
            "full_name": path_with_ns,
            "owner": owner_name,
            "description": item.get("description") or "",
            "stars": stars,
            "forks": forks,
            "watchers": stars,
            "language": item.get("language") or "Unknown",
            "open_issues": item.get("open_issues_count", 0) or 0,
            "url": item.get("web_url", ""),
            "platform": "GitLab",
            "topics": item.get("topics") or [],
            "last_updated": item.get("last_activity_at") or "",
            "license": item.get("license", {}).get("name") if item.get("license") else None,
            "default_branch": item.get("default_branch", "main")
        }
