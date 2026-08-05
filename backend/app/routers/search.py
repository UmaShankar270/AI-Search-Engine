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

def compute_lexical_score(repo: dict[str, Any], query_terms: list[str]) -> float:
    if not query_terms:
        return 0.0
    name = (repo.get("name") or "").lower()
    desc = (repo.get("description") or "").lower()
    topics = [t.lower() for t in (repo.get("topics") or [])]
    lang = (repo.get("language") or "").lower()
    
    score = 0.0
    for term in query_terms:
        term_lower = term.lower()
        matched = False
        if term_lower in name:
            score += 1.0
            matched = True
        elif any(term_lower in t or t in term_lower for t in topics):
            score += 0.8
            matched = True
        elif term_lower in desc:
            score += 0.5
            matched = True
        elif term_lower in lang:
            score += 0.2
            matched = True
            
    return min(1.0, score / len(query_terms))

def _build_candidate_from_repo(repo: dict[str, Any], query_vector: Optional[np.ndarray], facade: Any, query_terms: Optional[list[str]] = None) -> CandidateRepo:
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
            
    # Hybrid Search Scoring: Blend lexical similarity and semantic similarity
    if query_terms:
        lexical_score = compute_lexical_score(repo, query_terms)
        semantic_score = 0.5 * max(0.0, semantic_score) + 0.5 * lexical_score

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

def apply_backend_filters(
    repos: list[dict[str, Any]],
    language: Optional[str] = None,
    stars: Optional[str] = None,
    forks: Optional[str] = None,
    license: Optional[str] = None,
    updated: Optional[str] = None,
    sortBy: Optional[str] = None
) -> list[dict[str, Any]]:
    filtered = list(repos)
    
    # 1. Language Filter
    if language and language != "All":
        filtered = [r for r in filtered if r.get("language", "").lower() == language.lower()]
        
    # 2. Stars Filter
    if stars and stars != "All":
        try:
            min_stars = int(stars)
            filtered = [r for r in filtered if int(r.get("stars") or 0) >= min_stars]
        except ValueError:
            pass
            
    # 3. Forks Filter
    if forks and forks != "All":
        try:
            min_forks = int(forks)
            filtered = [r for r in filtered if int(r.get("forks") or 0) >= min_forks]
        except ValueError:
            pass
            
    # 4. License Filter
    if license and license != "All":
        filtered = [r for r in filtered if r.get("license") and str(r.get("license")).lower() == license.lower()]
        
    # 5. Updated Filter (days ago)
    if updated and updated != "All":
        try:
            days_limit = int(updated)
            from datetime import datetime, timedelta, timezone
            now = datetime(2026, 8, 4, tzinfo=timezone.utc)
            limit_date = now - timedelta(days=days_limit)
            
            res = []
            for r in filtered:
                lu_str = r.get("last_updated") or r.get("lastUpdated")
                if lu_str:
                    try:
                        lu_dt = datetime.fromisoformat(lu_str.replace("Z", "+00:00"))
                        if lu_dt >= limit_date:
                            res.append(r)
                    except Exception:
                        res.append(r)
                else:
                    res.append(r)
            filtered = res
        except ValueError:
            pass
            
    # 6. Sorting
    if sortBy == "stars":
        filtered.sort(key=lambda r: int(r.get("stars") or 0), reverse=True)
    elif sortBy == "forks":
        filtered.sort(key=lambda r: int(r.get("forks") or 0), reverse=True)
    elif sortBy == "updated":
        from datetime import datetime, timezone
        def get_updated_time(r):
            lu_str = r.get("last_updated") or r.get("lastUpdated") or ""
            try:
                return datetime.fromisoformat(lu_str.replace("Z", "+00:00"))
            except Exception:
                return datetime.min.replace(tzinfo=timezone.utc)
        filtered.sort(key=get_updated_time, reverse=True)
    elif sortBy == "name":
        filtered.sort(key=lambda r: (r.get("name") or "").lower())
    else:
        # Default match / aiScore sorting
        filtered.sort(key=lambda r: r.get("matchScore", 0.0), reverse=True)
        
    return filtered

QUERY_EXPANSIONS = {
    "video editor": ["video editing", "media editing", "ffmpeg", "video processing", "movie editing", "subtitle generation", "video pipelines"],
    "chatbot": ["chatbot", "llm chatbot", "conversational ai", "ai assistant", "rag chatbot", "langchain chatbot", "openai chatbot", "gemini chatbot", "vercel ai chatbot"]
}

def expand_query(query: str) -> list[str]:
    q_clean = query.lower().strip()
    expanded = [query]
    for key, synonyms in QUERY_EXPANSIONS.items():
        if key in q_clean or q_clean in key:
            for syn in synonyms:
                if syn.lower() not in [e.lower() for e in expanded]:
                    expanded.append(syn)
    return expanded

@router.get("/search")
def search(
    request: Request,
    query: str = None,
    q: str = None,
    language: str = None,
    page: int = 1,
    per_page: int = 10,
    stars: Optional[str] = None,
    forks: Optional[str] = None,
    license: Optional[str] = None,
    updated: Optional[str] = None,
    sortBy: Optional[str] = None,
    db: Session = Depends(get_db)
):
    import time
    import json
    start_time = time.perf_counter()
    effective_query = query or q
    if not effective_query:
        raise HTTPException(status_code=422, detail="Query is required")

    logger.info("Search pipeline started for query: '%s', language: %s, page: %d", effective_query, language, page)

    # 1. Log query history
    history = SearchHistory(query=effective_query)
    db.add(history)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning("Failed to log query history to DB: %s", str(e))

    # Query-level cache key (ignores page / per_page / filters to optimize reuse)
    cache_key = f"ranked_query_{effective_query.lower().strip()}_{language or 'all'}"
    cached = db.query(SearchCache).filter(SearchCache.query == cache_key).first()
    if cached:
        logger.info("Search cache HIT for key: %s", cache_key)
        all_results = json.loads(cached.response)
        
        # Apply filters on cached results
        filtered_results = apply_backend_filters(
            all_results,
            language=language,
            stars=stars,
            forks=forks,
            license=license,
            updated=updated,
            sortBy=sortBy
        )
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_results = filtered_results[start_idx:end_idx]
        return {
            "source": "cache",
            "results": paginated_results,
            "total_count": len(filtered_results),
            "page": page,
            "per_page": per_page
        }

    logger.info("Search cache MISS for key: %s. Running search pipeline...", cache_key)

    # Obtain AI Facade
    facade = getattr(request.app.state, "ai_facade", None)
    discovery = DiscoveryService()

    # 2. AI Query Understanding
    query_intent = None
    query_vector = None
    if facade:
        try:
            q_intent_start = time.perf_counter()
            query_intent = facade.understand_query(effective_query)
            query_vector = facade.generate_query_embedding(effective_query)
            logger.info("Query understanding completed in %.2fms. Intent: %s", (time.perf_counter() - q_intent_start) * 1000, query_intent.intent)
        except Exception as e:
            logger.warning("AI query understanding failed: %s", str(e))

    # 3. Hybrid Retrieval - Keyword search from all platforms (including Query Expansion)
    retrieval_start = time.perf_counter()
    expanded_queries = expand_query(effective_query)
    logger.info("Expanded query '%s' to: %s", effective_query, expanded_queries)
    
    keyword_results = []
    
    # Define a sub-search helper for parallel calls
    def search_term(term):
        return discovery.search_all_platforms(
            query=term,
            language=language,
            page=1,
            per_page=100,
            sortBy=sortBy
        )
    
    # Execute query expansion search concurrently for top terms to manage rate limit
    terms_to_search = expanded_queries[:4]
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=len(terms_to_search)) as executor:
        futures = {executor.submit(search_term, term): term for term in terms_to_search}
        for fut in as_completed(futures):
            term = futures[fut]
            try:
                platform_res = fut.result()
                logger.info("Search term '%s' retrieved %d projects", term, len(platform_res))
                keyword_results.extend(platform_res)
            except Exception as e:
                logger.error("Failed fetching for term '%s': %s", term, str(e))

    if not keyword_results:
        # Fallback to simple keyword search
        keyword_results = discovery.search_all_platforms(
            query=effective_query,
            language=language,
            page=1,
            per_page=100,
            sortBy=sortBy
        )
    logger.info("Keyword search (with query expansion) retrieved %d repositories in %.2fms", len(keyword_results), (time.perf_counter() - retrieval_start) * 1000)

    # 4. Hybrid Retrieval - Semantic search from local database
    semantic_results = []
    if facade:
        try:
            sem_start = time.perf_counter()
            sem_res = facade.search(query=effective_query, top_k=50)
            for hit in sem_res.results:
                meta = hit.metadata or {}
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
            logger.info("Semantic search retrieved %d repositories in %.2fms", len(semantic_results), (time.perf_counter() - sem_start) * 1000)
        except Exception as e:
            logger.warning("Semantic search index search failed: %s", str(e))

    # Merge results
    merged_results = keyword_results + semantic_results
    logger.info("Total repositories retrieved (merged): %d", len(merged_results))

    # If no results found, return baseline fallback mock data or empty list
    if not merged_results:
        logger.info("No repositories found in any platform. Returning empty list.")
        return {
            "source": "hybrid",
            "results": [],
            "total_count": 0,
            "page": page,
            "per_page": per_page
        }

    # 5. Duplicate Detection
    dedup_start = time.perf_counter()
    deduplicated = []
    if facade:
        try:
            deduplicated = facade.deduplicate(merged_results)
        except Exception as e:
            logger.warning("AI deduplication failed: %s", str(e))
            deduplicated = merged_results
    else:
        seen_urls = set()
        for repo in merged_results:
            url = (repo.get("url") or "").lower().strip()
            if url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(repo)
    logger.info("Deduplication completed in %.2fms. Repositories before: %d, after: %d", (time.perf_counter() - dedup_start) * 1000, len(merged_results), len(deduplicated))

    # 6. AI Ranking
    ranking_start = time.perf_counter()
    ranked_repos = []
    if facade:
        try:
            # Batch generate embeddings for candidates that don't have a semantic_score
            needing_embeddings = [r for r in deduplicated if r.get("semantic_score", 0.0) == 0.0]
            if needing_embeddings and query_vector is not None:
                try:
                    embed_start = time.perf_counter()
                    repo_embeddings = facade.generate_repository_embeddings(needing_embeddings)
                    
                    q_norm = np.linalg.norm(query_vector)
                    for idx, r in enumerate(needing_embeddings):
                        repo_vector = repo_embeddings[idx]
                        r_norm = np.linalg.norm(repo_vector)
                        if q_norm > 0 and r_norm > 0:
                            sim = float(np.dot(query_vector, repo_vector) / (q_norm * r_norm + 1e-8))
                            r["semantic_score"] = max(0.0, min(1.0, sim))
                        else:
                            r["semantic_score"] = 0.5
                    logger.info("Batch computed embeddings for %d repositories in %.2fms", len(needing_embeddings), (time.perf_counter() - embed_start) * 1000)
                except Exception as batch_exc:
                    logger.warning("Batch embedding generation failed: %s", str(batch_exc))

            candidates = [
                _build_candidate_from_repo(repo, query_vector, facade, expanded_queries)
                for repo in deduplicated
            ]
            intent_val = query_intent.intent.value if query_intent else "search"
            ranked_set = facade.rank(effective_query, candidates, intent=intent_val)
            
            for item in ranked_set.results:
                orig_repo = next(
                    (r for r in deduplicated if r.get("full_name") == item.repo_id),
                    None
                )
                if not orig_repo:
                    continue
                
                # Build match reason bullets dynamically from ranking factor scores
                bullets = []
                factors_map = {f.name: f.normalized_score for f in item.factor_scores}
                
                if factors_map.get("semantic_similarity", 0.0) >= 0.75:
                    bullets.append("Excellent semantic match")
                elif factors_map.get("semantic_similarity", 0.0) >= 0.6:
                    bullets.append("Good conceptual alignment")

                if factors_map.get("recent_activity", 0.0) >= 0.75 or factors_map.get("commit_frequency", 0.0) >= 0.75:
                    bullets.append("Recently maintained")

                if factors_map.get("documentation_quality", 0.0) >= 0.75 or factors_map.get("readme_completeness", 0.0) >= 0.75:
                    bullets.append("High documentation quality")

                if factors_map.get("community_adoption", 0.0) >= 0.75 or factors_map.get("popularity_trend", 0.0) >= 0.75:
                    bullets.append("Strong community adoption")

                if factors_map.get("contributor_count", 0.0) >= 0.7:
                    bullets.append("Active contributors")

                if factors_map.get("repository_trust", 0.0) >= 0.7:
                    bullets.append("Highly trusted publisher")

                if factors_map.get("project_maturity", 0.0) >= 0.7:
                    bullets.append("Stable release maturity")

                owner_lower = (orig_repo.get("owner") or "").lower()
                trusted_orgs = {"google", "facebook", "meta", "microsoft", "netflix", "hashicorp", "apache", "vercel", "airbnb", "uber", "aws", "docker", "kubernetes", "openjs-foundation", "github", "cloudflare"}
                if owner_lower in trusted_orgs or orig_repo.get("stars", 0) > 10000:
                    bullets.append("Trusted organization")

                if not bullets:
                    bullets.append("Relevant project match")

                # Store rounded score representation (float rounded to 1 decimal place, e.g. 96.3)
                ai_score_val = round(float(item.final_score * 100), 1)

                ranked_repos.append({
                    **orig_repo,
                    "matchScore": ai_score_val,
                    "aiScore": ai_score_val,
                    "healthScore": round(float(item.health_score * 100), 1),
                    "popularityScore": round(float(item.popularity_score * 100), 1),
                    "matchReasonBullets": bullets
                })
        except Exception as e:
            logger.warning("AI ranking failed: %s", str(e))
            for idx, repo in enumerate(deduplicated):
                score_val = round(float((1.0 - (idx / len(deduplicated))) * 100), 1)
                ranked_repos.append({
                    **repo,
                    "matchScore": score_val,
                    "aiScore": score_val,
                    "matchReasonBullets": ["Platform keyword match"]
                })
    else:
        for idx, repo in enumerate(deduplicated):
            score_val = round(float((1.0 - (idx / len(deduplicated))) * 100), 1)
            ranked_repos.append({
                **repo,
                "matchScore": score_val,
                "aiScore": score_val,
                "matchReasonBullets": ["Keyword baseline match"]
            })

    # Sort results by match score
    ranked_repos.sort(key=lambda r: r.get("matchScore", 0), reverse=True)
    
    # Assign ranks sequentially
    for rank_idx, repo in enumerate(ranked_repos):
        repo["rank"] = rank_idx + 1

    logger.info("AI ranking completed in %.2fms. Top repository: %s with score %s", (time.perf_counter() - ranking_start) * 1000, ranked_repos[0].get("full_name") if ranked_repos else "None", str(ranked_repos[0].get("matchScore", 0)) if ranked_repos else "0")

    # 7. Index Learning (Add new discoveries to local index for persistent search improvement)
    if facade:
        try:
            learning_start = time.perf_counter()
            new_repos = []
            for repo in ranked_repos[:5]:
                text = f"{repo.get('name')} {repo.get('description')} {' '.join(repo.get('topics', []))} {repo.get('language')}"
                new_repos.append({
                    "repo_id": repo.get("full_name"),
                    "text": text,
                    "metadata": repo
                })
            facade.add_repositories(new_repos)
            if facade._search_index_path:
                facade.save_index(facade._search_index_path)
            logger.info("Index learning batch added 5 repositories and saved index in %.2fms", (time.perf_counter() - learning_start) * 1000)
        except Exception as e:
            logger.warning("Index learning failed: %s", str(e))

    # Cache response (store full list)
    try:
        cache = SearchCache(query=cache_key, response=json.dumps(ranked_repos))
        db.add(cache)
        db.commit()
        logger.info("Cached search response successfully for query key: %s", cache_key)
    except Exception as cache_exc:
        db.rollback()
        logger.warning("Failed to cache search response or duplicate query committed concurrently: %s", str(cache_exc))

    # Apply filters on ranked results before paginating
    filtered_repos = apply_backend_filters(
        ranked_repos,
        language=language,
        stars=stars,
        forks=forks,
        license=license,
        updated=updated,
        sortBy=sortBy
    )

    # Pagination slice
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_results = filtered_repos[start_idx:end_idx]

    total_time = (time.perf_counter() - start_time) * 1000
    logger.info("Search pipeline completed in %.2fms. Returning %d results (page %d).", total_time, len(paginated_results), page)

    return {
        "source": "hybrid",
        "results": paginated_results,
        "total_count": len(filtered_repos),
        "page": page,
        "per_page": per_page
    }