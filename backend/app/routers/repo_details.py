import logging
from fastapi import APIRouter, HTTPException, Request
from app.models.repository import RepositoryResponse
from app.services.discovery_service import DiscoveryService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/repo/{owner}/{repo}",
    response_model=RepositoryResponse
)
def repo_details(request: Request, owner: str, repo: str, platform: str = "github"):
    discovery = DiscoveryService()
    data = discovery.get_repo_details(platform, owner, repo)

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
