import requests
from bs4 import BeautifulSoup
from typing import Any, Optional

class WebScraperProvider:
    """Fallback scraper to fetch repository data when standard API calls fail or get rate-limited."""

    @staticmethod
    def scrape_github_repo(owner: str, repo: str) -> Optional[dict[str, Any]]:
        url = f"https://github.com/{owner}/{repo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract description
            desc_tag = soup.find("meta", {"name": "description"})
            description = desc_tag.get("content", "").strip() if desc_tag else ""
            if "About" in description and " - " in description:
                # GitHub meta description is often "About: project description - owner/repo"
                description = description.split(" - ")[0].replace("About", "").strip(": ")

            # Parse stars and forks
            stars = 0
            star_tag = soup.find("span", {"id": "repo-stars-counter-star"})
            if star_tag:
                stars = WebScraperProvider._parse_metric(star_tag.text)

            forks = 0
            fork_tag = soup.find("span", {"id": "repo-network-counter"})
            if fork_tag:
                forks = WebScraperProvider._parse_metric(fork_tag.text)

            # Language
            lang_tag = soup.select_one("span.color-fg-default.text-bold")
            language = lang_tag.text.strip() if lang_tag else "Unknown"

            # Topics
            topics = [tag.text.strip() for tag in soup.select("a.topic-tag")]

            # Readme
            readme_body = soup.select_one("article.markdown-body")
            readme_text = readme_body.text.strip() if readme_body else ""

            return {
                "name": repo,
                "full_name": f"{owner}/{repo}",
                "owner": owner,
                "description": description,
                "stars": stars,
                "forks": forks,
                "watchers": stars,
                "language": language,
                "open_issues": 0,
                "url": url,
                "platform": "GitHub",
                "topics": topics,
                "last_updated": "Just scraped",
                "license": None,
                "readme_text": readme_text
            }
        except Exception:
            return None

    @staticmethod
    def scrape_github_readme(owner: str, repo: str) -> Optional[str]:
        url = f"https://github.com/{owner}/{repo}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                readme_body = soup.select_one("article.markdown-body")
                if readme_body:
                    return readme_body.text.strip()
            return None
        except Exception:
            return None

    @staticmethod
    def _parse_metric(text: str) -> int:
        clean = text.strip().lower().replace(",", "")
        if not clean:
            return 0
        try:
            if "k" in clean:
                return int(float(clean.replace("k", "")) * 1000)
            if "m" in clean:
                return int(float(clean.replace("m", "")) * 1000000)
            return int(clean)
        except ValueError:
            return 0
