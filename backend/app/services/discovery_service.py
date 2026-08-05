import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional
from app.services.providers import (
    GitHubProvider,
    GitLabProvider,
    CodebergProvider,
    BitbucketProvider,
    SourceForgeProvider,
    HuggingFaceProvider,
    PapersWithCodeProvider
)

logger = logging.getLogger(__name__)

class DiscoveryService:
    def __init__(self):
        self.providers = {
            "github": GitHubProvider(),
            "gitlab": GitLabProvider(),
            "codeberg": CodebergProvider(),
            "bitbucket": BitbucketProvider(),
            "sourceforge": SourceForgeProvider(),
            "huggingface": HuggingFaceProvider(),
            "paperswithcode": PapersWithCodeProvider()
        }
        self._executor = ThreadPoolExecutor(max_workers=len(self.providers))

    def search_all_platforms(
        self,
        query: str,
        language: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
        sortBy: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Concurrently fetch repositories from all platforms."""
        results = []
        
        def safe_search(provider, **kwargs):
            import inspect
            sig = inspect.signature(provider.search)
            if "sort" in sig.parameters:
                return provider.search(**kwargs)
            else:
                kwargs.pop("sort", None)
                return provider.search(**kwargs)

        # Parallel execution using a shared ThreadPoolExecutor
        future_to_platform = {
            self._executor.submit(
                safe_search,
                provider,
                query=query,
                language=language,
                page=page,
                per_page=per_page,
                sort=sortBy
            ): platform
            for platform, provider in self.providers.items()
        }
        
        from concurrent.futures import wait
        done, not_done = wait(future_to_platform.keys(), timeout=3.0)

        for future in done:
            platform = future_to_platform[future]
            try:
                platform_results = future.result()
                logger.info("Retrieved %d projects from %s", len(platform_results), platform)
                results.extend(platform_results)
            except Exception as exc:
                logger.error("Platform search failed for %s: %s", platform, str(exc))

        if not_done:
            logger.warning("Platform search timed out after 3.0 seconds for platforms: %s. Returning accumulated results.", [future_to_platform[f] for f in not_done])
            for fut in not_done:
                if not fut.done():
                    fut.cancel()
                    
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
