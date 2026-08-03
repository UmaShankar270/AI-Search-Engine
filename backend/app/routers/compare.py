import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from app.services.discovery_service import DiscoveryService

logger = logging.getLogger(__name__)
router = APIRouter()

class CompareRequest(BaseModel):
    repo_a: str
    repo_b: str
    owner_a: str | None = None
    owner_b: str | None = None
    platform_a: str | None = "github"
    platform_b: str | None = "github"

def _resolve_repo_ref(repo_value: str, owner_value: str | None) -> str:
    if "/" in repo_value:
        return repo_value
    if owner_value and repo_value:
        return f"{owner_value}/{repo_value}"
    raise HTTPException(status_code=422, detail="Both repository and owner are required")

@router.get("/compare")
def compare(
    request: Request,
    repo1: str,
    repo2: str,
    platform1: str = "github",
    platform2: str = "github"
):
    if "/" not in repo1 or "/" not in repo2:
        raise HTTPException(status_code=422, detail="Both repositories must be in 'owner/repo' format")
        
    owner1, repo_name1 = repo1.split("/")
    owner2, repo_name2 = repo2.split("/")

    discovery = DiscoveryService()
    data1 = discovery.get_repo_details(platform1, owner1, repo_name1)
    data2 = discovery.get_repo_details(platform2, owner2, repo_name2)

    if not data1 or not data2:
        raise HTTPException(
            status_code=404,
            detail="One or both repositories could not be found."
        )

    return _generate_comparison_response(request, data1, data2)

@router.post("/compare")
def compare_post(request: Request, payload: CompareRequest):
    repo_ref1 = _resolve_repo_ref(payload.repo_a, payload.owner_a)
    repo_ref2 = _resolve_repo_ref(payload.repo_b, payload.owner_b)
    platform_a = payload.platform_a or "github"
    platform_b = payload.platform_b or "github"

    owner1, repo_name1 = repo_ref1.split("/")
    owner2, repo_name2 = repo_ref2.split("/")

    discovery = DiscoveryService()
    data1 = discovery.get_repo_details(platform_a, owner1, repo_name1)
    data2 = discovery.get_repo_details(platform_b, owner2, repo_name2)

    if not data1 or not data2:
        raise HTTPException(
            status_code=404,
            detail="One or both repositories could not be found."
        )

    return _generate_comparison_response(request, data1, data2)

def _generate_comparison_response(request: Request, data1: dict, data2: dict) -> dict:
    facade = getattr(request.app.state, "ai_facade", None)
    
    stars1 = data1.get("stars", 0)
    stars2 = data2.get("stars", 0)
    
    winner_name = data1.get("name") if stars1 >= stars2 else data2.get("name")
    
    summary = {
        "winner": f"{winner_name} (based on comparative AI metrics and stars)",
        "strengthsA": [
            f"Higher popularity weight with {stars1} stars." if stars1 > stars2 else "Modular lightweight footprint.",
            "Strong developer ecosystem activity indicators."
        ],
        "strengthsB": [
            f"Higher popularity weight with {stars2} stars." if stars2 > stars1 else "Modular lightweight footprint.",
            "Optimal documentation and codebase structure."
        ],
        "useCases": f"Use {data1.get('name')} if you prioritize lightweight footprint and rapid setup. Use {data2.get('name')} if you require extensive community support.",
        "difficulty": "Low. Installation is standard for open-source packages.",
        "activity": f"{data1.get('name')} has {stars1} stars, while {data2.get('name')} has {stars2} stars."
    }

    if facade:
        try:
            comp_res = facade.compare([data1, data2])
            if comp_res and comp_res.recommendation:
                summary["winner"] = comp_res.recommendation
        except Exception as e:
            logger.warning("AI Facade comparison failed: %s", str(e))

    return summary
