import json
import logging
import numpy as np
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.database_models import SearchHistory, SearchCache
from app.services.discovery_service import DiscoveryService
from ai.ranking.models import CandidateRepo

logger = logging.getLogger(__name__)
router = APIRouter()

def _build_candidate_from_repo(repo: dict[str, Any], query_vector: Optional[np.ndarray], facade: Any) -> CandidateRepo:
    name = repo.get("name", "")
    description = repo.get("description", "")
    topics = repo.get("topics", [])
    language = repo.get("language", "")
    
    # Compute semantic score on the fly
    semantic_score = repo.get("semantic_score", 0.0)
    if semantic_score == 0.0 and query_vector is not None and facade is not None:
        try:
            repo_vector = facade.generate_repository_embedding(
                name=name,
                description=description,
                topics=topics,
                language=language
            )
            val = float(np.dot(query_vector, repo_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(repo_vector) + 1e-8))
            # Clip between 0 and 1
            semantic_score = max(0.0, min(1.0, val))
        except Exception:
            semantic_score = 0.5
            
    stars = int(repo.get("stars") or 0)
    forks = int(repo.get("forks") or 0)
    has_readme = len(description) > 30
    readme_length = len(description) * 5
    
    return CandidateRepo(
        repo_id=repo.get("full_name", f"{repo.get('owner')}/{name}"),
        semantic_score=semantic_score,
        stars=stars,
        forks=forks,
        contributors=max(1, int(stars * 0.01)),
        commits_last_3_months=max(1, int(forks * 0.05)),
        days_since_last_commit=14,
        created_at=repo.get("last_updated") or "2026-01-01T00:00:00Z",
        releases_last_year=3,
        issues_closed=10,
        issues_total=12,
        prs_merged=8,
        prs_total=10,
        has_documentation=True,
        has_readme=has_readme,
        readme_length=readme_length,
        readme_sections=3,
        readme_has_badges=stars > 150,
        has_license=repo.get("license") is not None,
        topics=topics,
        language=language,
        stars_last_90_days=int(stars * 0.03),
        forks_last_90_days=int(forks * 0.03),
        metadata=repo
    )

@router.get("/search")
def search(
    request: Request,
    query: str = None,
    q: str = None,
    language: str = None,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    effective_query = query or q
    if not effective_query:
        raise HTTPException(status_code=422, detail="Query is required")

    # 1. Log query history
    history = SearchHistory(query=effective_query)
    db.add(history)
    db.commit()

    cache_key = f"{effective_query}_{language}_{page}_{per_page}"
    cached = db.query(SearchCache).filter(SearchCache.query == cache_key).first()
    if cached:
        return {
            "source": "cache",
            "results": json.loads(cached.response)
        }

    # Obtain AI Facade
    facade = getattr(request.app.state, "ai_facade", None)
    discovery = DiscoveryService()

    # 2. AI Query Understanding
    query_intent = None
    query_vector = None
    if facade:
        try:
            query_intent = facade.understand_query(effective_query)
            query_vector = facade.generate_query_embedding(effective_query)
            logger.info("Query understanding intent: %s", query_intent.intent)
        except Exception as e:
            logger.warning("AI query understanding failed: %s", str(e))

    # 3. Hybrid Retrieval - Keyword search from all platforms
    keyword_results = discovery.search_all_platforms(
        query=effective_query,
        language=language,
        page=page,
        per_page=per_page
    )

    # 4. Hybrid Retrieval - Semantic search from local database
    semantic_results = []
    if facade:
        try:
            # We search top 30 historically indexed repos
            sem_res = facade.search(query=effective_query, top_k=30)
            for hit in sem_res.results:
                meta = hit.metadata or {}
                # Ensure structure is normalized
                normalized = {
                    "name": meta.get("name") or hit.repo_id.split("/")[-1],
                    "full_name": hit.repo_id,
                    "owner": meta.get("owner") or hit.repo_id.split("/")[0],
                    "description": meta.get("description") or "",
                    "stars": meta.get("stars", 0),
                    "forks": meta.get("forks", 0),
                    "watchers": meta.get("watchers", 0),
                    "language": meta.get("language") or "Unknown",
                    "open_issues": meta.get("open_issues", 0),
                    "url": meta.get("url") or f"https://github.com/{hit.repo_id}",
                    "platform": meta.get("platform") or "GitHub",
                    "topics": meta.get("topics") or [],
                    "last_updated": meta.get("last_updated") or "",
                    "license": meta.get("license"),
                    "semantic_score": float(hit.score)
                }
                semantic_results.append(normalized)
        except Exception as e:
            logger.warning("Semantic search index search failed: %s", str(e))

    # Merge results
    merged_results = keyword_results + semantic_results

    # If no results found, return baseline fallback mock data or empty list
    if not merged_results:
        return {
            "source": "hybrid",
            "results": []
        }

    # 5. Duplicate Detection
    deduplicated = []
    if facade:
        try:
            deduplicated = facade.deduplicate(merged_results)
        except Exception as e:
            logger.warning("AI deduplication failed: %s", str(e))
            deduplicated = merged_results
    else:
        # Simple fallback deduplication by URL / full_name
        seen_urls = set()
        for repo in merged_results:
            url = (repo.get("url") or "").lower().strip()
            if url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(repo)

    # 6. AI Ranking
    ranked_repos = []
    if facade:
        try:
            candidates = [
                _build_candidate_from_repo(repo, query_vector, facade)
                for repo in deduplicated
            ]
            intent_val = query_intent.intent.value if query_intent else "search"
            ranked_set = facade.rank(effective_query, candidates, intent=intent_val)
            
            for item in ranked_set.results:
                # Find matching original repo
                orig_repo = next(
                    (r for r in deduplicated if r.get("full_name") == item.repo_id),
                    None
                )
                if not orig_repo:
                    continue
                
                # Build match reason bullets
                bullets = []
                if item.semantic_score > 0.65:
                    bullets.append("Strong conceptual alignment with your query")
                if item.popularity_score > 0.5:
                    bullets.append("Highly popular project with active adoption")
                if item.health_score > 0.6:
                    bullets.append("Well-maintained repository with regular commits")
                if not bullets:
                    bullets.append("Relevant project match")

                ranked_repos.append({
                    **orig_repo,
                    "matchScore": int(item.final_score * 100),
                    "aiScore": int(item.final_score * 100),
                    "healthScore": int(item.health_score * 100),
                    "popularityScore": int(item.popularity_score * 100),
                    "matchReasonBullets": bullets
                })
        except Exception as e:
            logger.warning("AI ranking failed: %s", str(e))
            for idx, repo in enumerate(deduplicated):
                ranked_repos.append({
                    **repo,
                    "matchScore": int((1.0 - (idx / len(deduplicated))) * 100),
                    "matchReasonBullets": ["Platform keyword match"]
                })
    else:
        for idx, repo in enumerate(deduplicated):
            ranked_repos.append({
                **repo,
                "matchScore": int((1.0 - (idx / len(deduplicated))) * 100),
                "matchReasonBullets": ["Keyword baseline match"]
            })

    # Sort results by match score
    ranked_repos.sort(key=lambda r: r.get("matchScore", 0), reverse=True)

    # 7. Index Learning (Add new discoveries to local index for persistent search improvement)
    if facade:
        try:
            for repo in ranked_repos[:5]:
                # Text formulation for semantic search indexing
                text = f"{repo.get('name')} {repo.get('description')} {' '.join(repo.get('topics', []))} {repo.get('language')}"
                facade.add_repository(
                    repo_id=repo.get("full_name"),
                    text=text,
                    metadata=repo
                )
            # Save updated index
            if facade._search_index_path:
                facade.save_index(facade._search_index_path)
        except Exception as e:
            logger.warning("Index learning failed: %s", str(e))

    # Pagination slice
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_results = ranked_repos[start_idx:end_idx]

    # Cache response
    cache = SearchCache(query=cache_key, response=json.dumps(ranked_repos))
    db.add(cache)
    db.commit()

    return {
        "source": "hybrid",
        "results": paginated_results
    }