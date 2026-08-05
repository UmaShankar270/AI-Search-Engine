import requests
from bs4 import BeautifulSoup
from typing import Any, Optional
from app.services.providers.base import RepositoryProvider

class SourceForgeProvider(RepositoryProvider):
    def __init__(self):
        self.base_url = "https://sourceforge.net"

    def search(self, query: str, language: Optional[str] = None, page: int = 1, per_page: int = 10) -> list[dict[str, Any]]:
        # SourceForge directory URL
        url = f"{self.base_url}/directory/"
        params = {
            "q": query,
            "page": page
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            project_items = soup.select("li.project-oss, li.project")
            
            repos = []
            for item in project_items[:per_page]:
                try:
                    title_el = item.select_one(".result-heading-title")
                    if not title_el:
                        continue
                    
                    link = title_el.get("href", "")
                    if link.startswith("/"):
                        link = self.base_url + link
                    
                    name = title_el.text.strip()
                    
                    desc_el = item.select_one(".description")
                    description = desc_el.text.strip() if desc_el else ""
                    
                    # Parse downloads
                    downloads_val = 0
                    stats_el = item.select_one(".stats")
                    if stats_el:
                        stats_text = stats_el.text.lower()
                        if "downloads:" in stats_text:
                            # Extract number before "this week" or "total"
                            parts = stats_text.split("downloads:")
                            if len(parts) > 1:
                                num_str = "".join(c for c in parts[1].split()[0] if c.isdigit())
                                if num_str:
                                    downloads_val = int(num_str)
                    
                    # Parse rating (stars count)
                    rating_score = 0.0
                    rating_el = item.select_one(".rating")
                    if rating_el:
                        yellow_stars = len(rating_el.select(".star.yellow, .star.responsive.yellow"))
                        half_stars = len(rating_el.select(".star.half, .star.responsive.half"))
                        rating_score = yellow_stars + (half_stars * 0.5)

                    # Compute a virtual stars count based on downloads and rating
                    stars_count = int(downloads_val * 5 + rating_score * 20)
                    
                    # Parse last updated
                    last_updated = ""
                    time_el = item.select_one(".dateUpdated, time")
                    if time_el:
                        last_updated = time_el.get("datetime") or time_el.text.strip()

                    # Extract project key as owner fallback
                    owner = link.rstrip("/").split("/")[-1] if "/" in link else "sourceforge"
                    
                    normalized = {
                        "name": name,
                        "full_name": f"sourceforge/{owner}",
                        "owner": owner,
                        "description": description,
                        "stars": stars_count,
                        "forks": int(downloads_val * 0.1),
                        "watchers": int(downloads_val * 0.2),
                        "language": "Unknown",  # HTML doesn't list primary language cleanly on card, defaults to Unknown
                        "open_issues": 0,
                        "url": link,
                        "platform": "SourceForge",
                        "topics": [],
                        "last_updated": last_updated,
                        "license": "Open Source"
                    }
                    
                    # Post-filter by language (topics/description check if primary lang is Unknown)
                    if language and language != "All":
                        if language.lower() not in description.lower():
                            continue
                    
                    repos.append(normalized)
                except Exception:
                    pass
            return repos
        except Exception:
            return []

    def getRepository(self, owner: str, repo: str) -> Optional[dict[str, Any]]:
        # SourceForge project summary page URL: https://sourceforge.net/projects/{repo}/
        url = f"{self.base_url}/projects/{repo}/"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, "html.parser")
            desc_el = soup.select_one("#project-description") or soup.select_one(".description")
            description = desc_el.text.strip() if desc_el else ""
            
            title_el = soup.select_one("h1")
            name = title_el.text.strip() if title_el else repo
            
            return {
                "name": name,
                "full_name": f"sourceforge/{repo}",
                "owner": repo,
                "description": description,
                "stars": 100,
                "forks": 10,
                "watchers": 20,
                "language": "Unknown",
                "open_issues": 0,
                "url": url,
                "platform": "SourceForge",
                "topics": [],
                "last_updated": "",
                "license": "Open Source"
            }
        except Exception:
            return None

    def getReadme(self, owner: str, repo: str) -> Optional[str]:
        # SourceForge projects don't have a standardized README file endpoint,
        # but the description section acts as the primary project README.
        project = self.getRepository(owner, repo)
        if project:
            return project.get("description")
        return None

    def getMetadata(self, owner: str, repo: str) -> dict[str, Any]:
        return {}
