import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.repository import RepositoryResponse
from app.services.discovery_service import DiscoveryService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/repo/{owner}/{repo}",
    response_model=RepositoryResponse
)
def repo_details(request: Request, owner: str, repo: str, platform: str = "github", db: Session = Depends(get_db)):
    discovery = DiscoveryService()
    data = discovery.get_repo_details(platform, owner, repo)

    if not data:
        # Self-healing fallback: check database search cache for this repository metadata
        logger.warning(f"Repository details query failed for {owner}/{repo} on {platform}. Attempting search cache fallback...")
        try:
            from app.database_models import SearchCache
            import json
            
            caches = db.query(SearchCache).all()
            for c in caches:
                try:
                    payload = json.loads(c.response)
                    results_list = payload if isinstance(payload, list) else payload.get("results", [])
                    matched = next((r for r in results_list if r.get("full_name") == f"{owner}/{repo}"), None)
                    if matched:
                        logger.info(f"Self-healing: restored {owner}/{repo} details from search cache.")
                        data = {
                            "name": matched.get("name"),
                            "full_name": matched.get("full_name"),
                            "owner": matched.get("owner"),
                            "description": matched.get("description"),
                            "stars": matched.get("stars", 0),
                            "forks": matched.get("forks", 0),
                            "watchers": matched.get("watchers", 0),
                            "language": matched.get("language") or "Unknown",
                            "open_issues": matched.get("open_issues", 0),
                            "url": matched.get("url"),
                            "platform": matched.get("platform") or "GitHub",
                            "topics": matched.get("topics") or [],
                            "last_updated": matched.get("last_updated") or "",
                            "license": matched.get("license"),
                            "default_branch": "main",
                            "readmeHtml": f"<h1>{matched.get('name')}</h1><p>{matched.get('description')}</p>"
                        }
                        break
                except Exception:
                    pass
        except Exception as cache_err:
            logger.error(f"Search cache self-healing lookup failed: {cache_err}")

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found on {platform}"
        )

    # Generate AI Analysis
    readme_text = data.get("readmeHtml") or ""
    facade = getattr(request.app.state, "ai_facade", None)
    ai_analysis = None
    
    # Prepare basic metadata dictionary for facade
    repo_metadata = {
        "name": data.get("name"),
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stars", 0),
        "forks": data.get("forks", 0),
        "open_issues": data.get("open_issues", 0)
    }

    if facade:
        try:
            ai_analysis = facade.generate_insight_report(repo_metadata, readme_text)
        except Exception as exc:
            logger.warning("AI Insight Report generation failed: %s", exc)

    if not ai_analysis:
        try:
            from ai.summarizer.summarizer import SummaryGenerator
            generator = SummaryGenerator()
            ai_analysis = generator.generate_insight_report(repo_metadata, readme_text)
        except Exception as exc:
            logger.error("Failed to generate fallback mock insight report: %s", exc)

    data["aiAnalysis"] = ai_analysis

    return RepositoryResponse(**data)
