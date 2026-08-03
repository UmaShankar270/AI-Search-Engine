import logging
from fastapi import APIRouter, Request
from app.services.discovery_service import DiscoveryService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/trending")
def trending(request: Request, language: str = None):
    # Fetch trending repositories using multi-platform discovery
    discovery = DiscoveryService()
    
    query = "stars:>5000" if not language or language == "All" else f"stars:>2000 language:{language}"
    
    # Fetch candidate repositories from all platforms
    candidates = discovery.search_all_platforms(
        query=query,
        page=1,
        per_page=15
    )

    if not candidates:
        return []

    facade = getattr(request.app.state, "ai_facade", None)
    if not facade:
        # Fallback sorting by stars
        candidates.sort(key=lambda x: x.get("stars", 0), reverse=True)
        return candidates[:10]

    try:
        # Sort and rank popular projects using recommendation engine popularity sorting
        pop_set = facade.recommend_popular(
            all_repositories=candidates,
            top_n=10,
            sort_key="stars"
        )
        
        trending_list = []
        for item in pop_set.recommendations:
            orig_repo = next(
                (c for c in candidates if c.get("full_name") == item.repo_id),
                None
            )
            if orig_repo:
                trending_list.append({
                    **orig_repo,
                    "aiPopularityScore": int(item.score * 100) if item.score <= 1.0 else int(item.score)
                })
        return trending_list
    except Exception as e:
        logger.warning("AI trending ranking failed: %s", str(e))
        candidates.sort(key=lambda x: x.get("stars", 0), reverse=True)
        return candidates[:10]