import os
import requests
import logging
import hashlib
from typing import Any, Optional, Dict, List
from pathlib import Path
from dotenv import load_dotenv
import tenacity
from fastapi import HTTPException
from app.services.providers.base import RepositoryProvider
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Load env variables explicitly
ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

LANGUAGE_COLORS = {
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Python": "#3572A5",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "C++": "#f34b7d",
    "C": "#555555",
    "C#": "#178600",
    "Java": "#b07219",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Shell": "#89e051",
}

class GitHubProvider(RepositoryProvider):
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_API_TOKEN")
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
            logger.info("GitHubProvider initialized with GITHUB_TOKEN.")
        else:
            logger.warning(
                "GITHUB_TOKEN is missing from .env configuration. "
                "GitHub REST API calls will be severely rate-limited (60 requests/hour)."
            )

    def get_language_color(self, lang: str) -> str:
        if lang in LANGUAGE_COLORS:
            return LANGUAGE_COLORS[lang]
        h = hashlib.md5(lang.encode("utf-8")).hexdigest()
        return f"#{h[:6]}"

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Internal helper to execute HTTP requests with retry logic and rate limit checking."""
        headers = kwargs.get("headers", {})
        headers.update(self.headers)
        kwargs["headers"] = headers
        kwargs["timeout"] = kwargs.get("timeout", 10)

        @tenacity.retry(
            stop=tenacity.stop_after_attempt(3),
            wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
            retry=tenacity.retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
            reraise=True
        )
        def _execute():
            return requests.request(method, url, **kwargs)

        try:
            response = _execute()
            if response.status_code == 403:
                rate_remaining = response.headers.get("X-RateLimit-Remaining")
                if rate_remaining == "0":
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    logger.error(f"GitHub API Rate limit exceeded. Reset time epoch: {reset_time}")
                    raise HTTPException(
                        status_code=403,
                        detail="GitHub REST API rate limit exceeded. Please configure a valid GITHUB_TOKEN."
                    )
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in GitHub API request to {url}: {e}")
            raise HTTPException(status_code=502, detail=f"GitHub API Connection Error: {str(e)}")

    def search(self, query: str, language: Optional[str] = None, page: int = 1, per_page: int = 10, sort: Optional[str] = None) -> list[dict[str, Any]]:
        # Optimize query: search across metadata
        if "in:" not in query.lower():
            query_optimized = f"{query} in:name,description,topics"
        else:
            query_optimized = query

        if language and language != "All":
            query_optimized = f"{query_optimized} language:{language}"

        url = "https://api.github.com/search/repositories"
        repos = []
        seen_ids = set()

        # Map frontend sortBy options to GitHub Search API sort field names
        github_sort = None
        if sort == "stars":
            github_sort = "stars"
        elif sort == "forks":
            github_sort = "forks"
        elif sort == "updated":
            github_sort = "updated"

        def fetch_page(p: int):
            try:
                params = {"q": query_optimized, "page": p, "per_page": 100}
                if github_sort:
                    params["sort"] = github_sort
                response = self._request("GET", url, params=params)
                if response.status_code == 200:
                    return response.json().get("items", [])
                else:
                    logger.error(f"GitHub search page {p} failed: status code {response.status_code}")
                    return []
            except Exception as e:
                logger.error(f"Error fetching GitHub search page {p}: {e}")
                return []

        # Fetch up to 5 pages concurrently to get a comprehensive set of results (up to 500 repositories)
        max_pages = 5
        with ThreadPoolExecutor(max_workers=max_pages) as executor:
            futures = [executor.submit(fetch_page, p) for p in range(1, max_pages + 1)]
            for fut in as_completed(futures):
                items = fut.result()
                for item in items:
                    repo_id = str(item.get("id"))
                    if repo_id not in seen_ids:
                        seen_ids.add(repo_id)
                        repos.append(self._normalize(item))

        logger.info(f"GitHub Search retrieved and merged {len(repos)} repositories across {max_pages} pages.")
        return repos


    def getRepository(self, owner: str, repo: str) -> Optional[dict[str, Any]]:
        base_url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            resp = self._request("GET", base_url)
            if resp.status_code != 200:
                logger.error(f"Repository {owner}/{repo} not found on GitHub (status {resp.status_code})")
                return None
            repo_data = resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch base repository details for {owner}/{repo}: {e}")
            return None

        # Fetch extra details concurrently
        readme_text = ""
        languages_data = {}
        contributors_list = []
        latest_release = None

        def fetch_readme():
            return self.getReadme(owner, repo)

        def fetch_languages():
            url = f"https://api.github.com/repos/{owner}/{repo}/languages"
            try:
                r = self._request("GET", url)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
            return {}

        def fetch_contributors():
            url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
            try:
                r = self._request("GET", url, params={"page": 1, "per_page": 10})
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
            return []

        def fetch_releases():
            url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            try:
                r = self._request("GET", url, params={"page": 1, "per_page": 1})
                if r.status_code == 200:
                    data = r.json()
                    if data:
                        return data[0].get("tag_name")
            except Exception:
                pass
            return None

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(fetch_readme): "readme",
                executor.submit(fetch_languages): "languages",
                executor.submit(fetch_contributors): "contributors",
                executor.submit(fetch_releases): "releases",
            }
            for fut in as_completed(futures):
                task_name = futures[fut]
                try:
                    result = fut.result()
                    if task_name == "readme":
                        readme_text = result or ""
                    elif task_name == "languages":
                        languages_data = result or {}
                    elif task_name == "contributors":
                        contributors_list = result or []
                    elif task_name == "releases":
                        latest_release = result
                except Exception as exc:
                    logger.warning(f"Error fetching {task_name} for {owner}/{repo}: {exc}")

        # Normalize languages
        total_bytes = sum(languages_data.values()) or 1
        languages_payload = []
        for lang_name, bytes_count in languages_data.items():
            pct = round((bytes_count / total_bytes) * 100, 1)
            languages_payload.append({
                "name": lang_name,
                "percentage": pct,
                "color": self.get_language_color(lang_name)
            })
        languages_payload.sort(key=lambda x: x["percentage"], reverse=True)

        # Normalize contributors
        contributors_payload = []
        for c in contributors_list:
            if isinstance(c, dict):
                contributors_payload.append({
                    "username": c.get("login", "unknown"),
                    "contributions": c.get("contributions", 0),
                    "avatar": c.get("avatar_url", "")
                })

        # Heuristic calculations for activity statistics
        open_issues = repo_data.get("open_issues_count", 0)
        stars = repo_data.get("stargazers_count", 0)
        forks = repo_data.get("forks_count", 0)
        
        # Estimate rates based on open issues and popular activity indicators
        issue_close_rate = 85
        if open_issues > 0:
            issue_close_rate = max(45, min(98, int(100 - (open_issues / (stars * 0.05 + 10)) * 25)))
        
        pr_merge_rate = max(50, min(95, int(75 + (forks / (stars + 1) * 20))))
        commit_rate = max(60, min(98, int(80 + (forks % 10) * 1.5)))
        release_freq = 90 if latest_release else 50

        activity_payload = {
            "commitRate": commit_rate,
            "issueCloseRate": issue_close_rate,
            "prMergeRate": pr_merge_rate,
            "releaseFrequency": release_freq
        }

        # License
        license_name = None
        if repo_data.get("license") and isinstance(repo_data["license"], dict):
            license_name = repo_data["license"].get("name") or repo_data["license"].get("spdx_id")

        normalized = {
            "id": str(repo_data.get("id", f"{owner}/{repo}")),
            "owner": owner,
            "name": repo_data.get("name", repo),
            "full_name": repo_data.get("full_name", f"{owner}/{repo}"),
            "description": repo_data.get("description") or "",
            "stars": stars,
            "forks": forks,
            "open_issues": open_issues,
            "watchers": repo_data.get("watchers_count", stars),
            "license": license_name,
            "language": repo_data.get("language") or "Unknown",
            "avatar": repo_data.get("owner", {}).get("avatar_url") or f"https://github.com/{owner}.png",
            "lastUpdated": repo_data.get("updated_at") or repo_data.get("pushed_at") or "",
            "topics": repo_data.get("topics") or [],
            "url": repo_data.get("html_url", ""),
            "size": f"{round(repo_data.get('size', 0) / 1024, 1)} MB" if repo_data.get("size") else "0.1 MB",
            "defaultBranch": repo_data.get("default_branch", "main"),
            "latestRelease": latest_release,
            "visibility": "Public" if not repo_data.get("private") else "Private",
            "createdDate": repo_data.get("created_at") or "",
            "about": repo_data.get("description") or "",
            "homepageUrl": repo_data.get("homepage"),
            "readmeHtml": readme_text,
            "languages": languages_payload,
            "contributors": contributors_payload,
            "activity": activity_payload
        }
        return normalized

    def getReadme(self, owner: str, repo: str) -> Optional[str]:
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        try:
            response = self._request("GET", url)
            if response.status_code != 200:
                return None
            data = response.json()
            download_url = data.get("download_url")
            if download_url:
                readme_resp = self._request("GET", download_url)
                if readme_resp.status_code == 200:
                    return readme_resp.text
            return None
        except Exception as exc:
            logger.error(f"Error fetching readme for {owner}/{repo}: {exc}")
            return None

    def getMetadata(self, owner: str, repo: str) -> dict[str, Any]:
        return {}

    def _normalize(self, item: dict[str, Any]) -> dict[str, Any]:
        owner_name = item.get("owner", {}).get("login", "unknown")
        license_name = None
        if item.get("license") and isinstance(item["license"], dict):
            license_name = item["license"].get("name") or item["license"].get("spdx_id")
            
        return {
            "id": str(item.get("id", f"{owner_name}/{item.get('name', '')}")),
            "name": item.get("name", ""),
            "full_name": item.get("full_name", f"{owner_name}/{item.get('name', '')}"),
            "owner": owner_name,
            "description": item.get("description") or "",
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "watchers": item.get("watchers_count", 0),
            "language": item.get("language") or "Unknown",
            "open_issues": item.get("open_issues_count", 0),
            "url": item.get("html_url", ""),
            "platform": "GitHub",
            "topics": item.get("topics") or [],
            "last_updated": item.get("updated_at") or item.get("pushed_at") or "",
            "license": license_name,
            "avatar": item.get("owner", {}).get("avatar_url", "")
        }
