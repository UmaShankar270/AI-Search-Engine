import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from app.services.discovery_service import DiscoveryService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/recommend")
def recommend(request: Request, query: str = None, q: str = None):
    effective_query = query or q
    if not effective_query:
        effective_query = "awesome open source"

    discovery = DiscoveryService()
    # Concurrently search all platforms for candidate repositories
    candidates = discovery.search_all_platforms(
        query=effective_query,
        page=1,
        per_page=15
    )

    if not candidates:
        return []

    facade = getattr(request.app.state, "ai_facade", None)
    if not facade:
        # Fallback sorting by stars
        candidates.sort(key=lambda x: x.get("stars", 0), reverse=True)
        return candidates[:5]

    try:
        # Build embedding map for candidates
        embedding_map = facade._build_embedding_map(candidates)
        # Get recommended set
        rec_set = facade.recommend_from_query(
            query=effective_query,
            all_repositories=candidates,
            embedding_map=embedding_map,
            top_n=5
        )
        
        recommended_list = []
        for rec in rec_set.recommendations:
            orig_repo = next(
                (c for c in candidates if c.get("full_name") == rec.repo_id),
                None
            )
            if orig_repo:
                recommended_list.append({
                    **orig_repo,
                    "score": round(float(rec.score), 2),
                    "reason": rec.reason
                })
        return recommended_list
    except Exception as e:
        logger.warning("AI recommendation failed: %s", str(e))
        # Fallback sorting
        candidates.sort(key=lambda x: x.get("stars", 0), reverse=True)
        return candidates[:5]
