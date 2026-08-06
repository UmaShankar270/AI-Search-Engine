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

    # Persistent class-level ThreadPoolExecutor to prevent cross-request thread starvation and blocking on shutdown
    _executor = ThreadPoolExecutor(max_workers=50)

    def search_all_platforms(
        self,
        query: str,
        language: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
        sortBy: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Concurrently fetch repositories from all platforms."""
        logger.info("[Stage 2: Discovery Service] Entering with query='%s', language='%s'", query, language)
        results = []
        
        def safe_search(provider, **kwargs):
            import inspect
            sig = inspect.signature(provider.search)
            if "sort" in sig.parameters:
                return provider.search(**kwargs)
            else:
                kwargs.pop("sort", None)
                return provider.search(**kwargs)

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
                logger.info("[Stage 2: Discovery Service] Platform '%s' returned %d projects", platform, len(platform_results))
                results.extend(platform_results)
            except Exception as exc:
                logger.error("[Stage 2: Discovery Service] Platform '%s' search failed: %s", platform, str(exc))

        if not_done:
            timed_out_platforms = [future_to_platform[f] for f in not_done]
            logger.warning("[Stage 2: Discovery Service] Platform search timed out after 3.0 seconds for: %s. Filtering them out (timed out).", timed_out_platforms)
            for fut in not_done:
                if not fut.done():
                    fut.cancel()
                        
        logger.info("[Stage 2: Discovery Service] Leaving: total accumulated projects=%d", len(results))
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
