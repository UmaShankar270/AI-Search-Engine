import logging
from fastapi import APIRouter, HTTPException, Request
from app.services.discovery_service import DiscoveryService
from app.services.ai_service import summarize

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/analyze/{owner}/{repo}")
def analyze_repository(request: Request, owner: str, repo: str, platform: str = "github"):
    """Fetch and summarize the repository README from any platform."""
    discovery = DiscoveryService()
    
    # Fetch README using the appropriate platform provider
    readme_content = discovery.get_repo_readme(platform, owner, repo)
    
    if not readme_content:
        raise HTTPException(
            status_code=404,
            detail=f"Repository or README not found on {platform}"
        )

    # Use AIFacade to summarize README if loaded, otherwise fallback to basic summarizer
    facade = getattr(request.app.state, "ai_facade", None)
    summary = ""
    
    if facade:
        try:
            # We build a temporary repo dict for AIFacade
            repo_dict = {
                "name": repo,
                "full_name": f"{owner}/{repo}",
                "description": readme_content[:200],
                "language": "",
                "stars": 100
            }
            summary = facade.summarize(repo_dict)
        except Exception as e:
            logger.warning("AI Facade summarization failed: %s", str(e))
            summary = summarize(readme_content)
    else:
        summary = summarize(readme_content)

    return {
        "repository": f"{owner}/{repo}",
        "platform": platform,
        "summary": summary,
        "readme_length": len(readme_content)
    }