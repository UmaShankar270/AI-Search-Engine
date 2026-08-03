import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional
from app.services.providers import (
    GitHubProvider,
    GitLabProvider,
    CodebergProvider,
    BitbucketProvider,
    SourceForgeProvider
)

logger = logging.getLogger(__name__)

class DiscoveryService:
    def __init__(self):
        self.providers = {
            "github": GitHubProvider(),
            "gitlab": GitLabProvider(),
            "codeberg": CodebergProvider(),
            "bitbucket": BitbucketProvider(),
            "sourceforge": SourceForgeProvider()
        }

    def search_all_platforms(
        self,
        query: str,
        language: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> list[dict[str, Any]]:
        """Concurrently fetch repositories from all platforms."""
        results = []
        
        # Parallel execution using a ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            future_to_platform = {
                executor.submit(
                    provider.search,
                    query=query,
                    language=language,
                    page=page,
                    per_page=per_page
                ): platform
                for platform, provider in self.providers.items()
            }
            
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    platform_results = future.result()
                    logger.info("Retrieved %d projects from %s", len(platform_results), platform)
                    results.extend(platform_results)
                except Exception as exc:
                    logger.error("Platform search failed for %s: %s", platform, str(exc))
                    
        return results

    def get_repo_details(self, platform: str, owner: str, repo: str) -> Optional[dict[str, Any]]:
        provider = self.providers.get(platform.lower())
        if provider:
            return provider.getRepository(owner, repo)
        return self.providers["github"].getRepository(owner, repo)

    def get_repo_readme(self, platform: str, owner: str, repo: str) -> Optional[str]:
        provider = self.providers.get(platform.lower())
        if provider:
            return provider.getReadme(owner, repo)
        return self.providers["github"].getReadme(owner, repo)
