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
    logger.info("[Stage 8: Backend Filters] Entering with %d repos, filters: language='%s', stars='%s', forks='%s', license='%s', updated='%s', sortBy='%s'", len(repos), language, stars, forks, license, updated, sortBy)
    filtered = list(repos)
    
    # 1. Language Filter
    if language and language != "All":
        prev_len = len(filtered)
        filtered = [r for r in filtered if r.get("language", "").lower() == language.lower()]
        logger.info("[Stage 8: Backend Filters] Language filter ('%s') entering: %d, leaving: %d (filtered %d due to language mismatch)", language, prev_len, len(filtered), prev_len - len(filtered))
    else:
        logger.info("[Stage 8: Backend Filters] Language filter skipped")
        
    # 2. Stars Filter
    if stars and stars != "All":
        try:
            min_stars = int(stars)
            prev_len = len(filtered)
            filtered = [r for r in filtered if int(r.get("stars") or 0) >= min_stars]
            logger.info("[Stage 8: Backend Filters] Stars filter (>=%d) entering: %d, leaving: %d (filtered %d due to low stars)", min_stars, prev_len, len(filtered), prev_len - len(filtered))
        except ValueError:
            logger.info("[Stage 8: Backend Filters] Stars filter skipped due to invalid value '%s'", stars)
            pass
    else:
        logger.info("[Stage 8: Backend Filters] Stars filter skipped")
            
    # 3. Forks Filter
    if forks and forks != "All":
        try:
            min_forks = int(forks)
            prev_len = len(filtered)
            filtered = [r for r in filtered if int(r.get("forks") or 0) >= min_forks]
            logger.info("[Stage 8: Backend Filters] Forks filter (>=%d) entering: %d, leaving: %d (filtered %d due to low forks)", min_forks, prev_len, len(filtered), prev_len - len(filtered))
        except ValueError:
            logger.info("[Stage 8: Backend Filters] Forks filter skipped due to invalid value '%s'", forks)
            pass
    else:
        logger.info("[Stage 8: Backend Filters] Forks filter skipped")
            
    # 4. License Filter
    if license and license != "All":
        prev_len = len(filtered)
        filtered = [r for r in filtered if r.get("license") and str(r.get("license")).lower() == license.lower()]
        logger.info("[Stage 8: Backend Filters] License filter ('%s') entering: %d, leaving: %d (filtered %d due to license mismatch or missing license)", license, prev_len, len(filtered), prev_len - len(filtered))
    else:
        logger.info("[Stage 8: Backend Filters] License filter skipped")
        
    # 5. Updated Filter (days ago)
    if updated and updated != "All":
        try:
            days_limit = int(updated)
            from datetime import datetime, timedelta, timezone
            now = datetime(2026, 8, 4, tzinfo=timezone.utc)
            limit_date = now - timedelta(days=days_limit)
            
            prev_len = len(filtered)
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
            logger.info("[Stage 8: Backend Filters] Updated filter (pushed within %d days, limit_date=%s) entering: %d, leaving: %d (filtered %d due to push date limit)", days_limit, limit_date, prev_len, len(filtered), prev_len - len(filtered))
        except ValueError:
            logger.info("[Stage 8: Backend Filters] Updated filter skipped due to invalid value '%s'", updated)
            pass
    else:
        logger.info("[Stage 8: Backend Filters] Updated filter skipped")
            
    # 6. Sorting
    logger.info("[Stage 8: Backend Filters] Applying sorting by '%s'", sortBy)
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
        
    logger.info("[Stage 8: Backend Filters] Leaving: %d repos", len(filtered))
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
        
        # Apply filters on cached results (Stage 8 logging will be triggered inside apply_backend_filters)
        filtered_results = apply_backend_filters(
            all_results,
            language=language,
            stars=stars,
            forks=forks,
            license=license,
            updated=updated,
            sortBy=sortBy
        )
        
        logger.info("[Stage 9: Pagination] (Cache Hit) Entering: filtered_results=%d, page=%d, per_page=%d", len(filtered_results), page, per_page)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_results = filtered_results[start_idx:end_idx]
        logger.info("[Stage 9: Pagination] (Cache Hit) Leaving: paginated_results=%d", len(paginated_results))

        res_payload = {
            "source": "cache",
            "results": paginated_results,
            "total_count": len(filtered_results),
            "page": page,
            "per_page": per_page
        }
        logger.info("[Stage 10: API Response] (Cache Hit) Leaving: total_count=%d, results_count=%d", res_payload["total_count"], len(res_payload["results"]))
        return res_payload

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

    # 4. Hybrid Retrieval - Semantic search from local database (Stage 6)
    semantic_results = []
    logger.info("[Stage 6: Semantic Search] Entering with query='%s'", effective_query)
    if facade:
        try:
            sem_start = time.perf_counter()
            if query_vector is not None:
                logger.info("[Stage 6: Semantic Search] Generated query embedding of dimension: %d, shape: %s", len(query_vector), query_vector.shape)
            
            sem_res = facade.search(query=effective_query, top_k=50)
            
            logger.info("[Stage 6: Semantic Search] Nearest neighbors from FAISS:")
            for rank_idx, hit in enumerate(sem_res.results):
                logger.info("  Rank %d: ID=%s, Cosine Similarity Score=%.4f", rank_idx + 1, hit.repo_id, hit.score)
                
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
            logger.info("[Stage 6: Semantic Search] Retrieved semantic repositories: %s", [r["full_name"] for r in semantic_results])
            logger.info("[Stage 6: Semantic Search] Retrieved %d repositories in %.2fms", len(semantic_results), (time.perf_counter() - sem_start) * 1000)
        except Exception as e:
            logger.warning("[Stage 6: Semantic Search] index search failed: %s", str(e))
    else:
        logger.info("[Stage 6: Semantic Search] Skipped (AI Facade unavailable)")

    logger.info("[Stage 6: Semantic Search] Leaving: semantic_results=%d", len(semantic_results))

    # Merge results (Stage 4)
    logger.info("[Stage 4: Multi-provider Merge] Entering: keyword_results=%d, semantic_results=%d", len(keyword_results), len(semantic_results))
    merged_results = keyword_results + semantic_results
    logger.info("[Stage 4: Multi-provider Merge] Leaving: merged_results=%d", len(merged_results))

    # If no results found, return baseline fallback mock data or empty list
    if not merged_results:
        logger.info("No repositories found in any platform. Returning empty list.")
        res_payload = {
            "source": "hybrid",
            "results": [],
            "total_count": 0,
            "page": page,
            "per_page": per_page
        }
        logger.info("[Stage 10: API Response] (Empty Results) Leaving: total_count=0, results_count=0")
        return res_payload

    # 5. Duplicate Detection (Stage 5)
    logger.info("[Stage 5: Duplicate Removal] Entering: merged_results=%d", len(merged_results))
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
    logger.info("[Stage 5: Duplicate Removal] Leaving: deduplicated=%d (removed %d duplicates in %.2fms)", len(deduplicated), len(merged_results) - len(deduplicated), (time.perf_counter() - dedup_start) * 1000)

    # 6. AI Ranking (Stage 7)
    logger.info("[Stage 7: AI Ranking] Entering: candidates=%d", len(deduplicated))
    ranking_start = time.perf_counter()
    ranked_repos = []
    if facade:
        try:
            # Batch generate embeddings for candidates that don't have a semantic_score
            needing_embeddings = [r for r in deduplicated if r.get("semantic_score", 0.0) == 0.0]
            if needing_embeddings and query_vector is not None:
                # Heuristically rank candidates to select the top 100 for deep embedding computation
                def get_heuristic_score(r):
                    lex = compute_lexical_score(r, expanded_queries)
                    stars = int(r.get("stars") or 0)
                    star_score = min(1.0, stars / 1000.0)
                    return 0.7 * lex + 0.3 * star_score
                
                needing_embeddings.sort(key=get_heuristic_score, reverse=True)
                
                MAX_EMBED = 100
                to_embed = needing_embeddings[:MAX_EMBED]
                remaining = needing_embeddings[MAX_EMBED:]
                
                try:
                    embed_start = time.perf_counter()
                    repo_embeddings = facade.generate_repository_embeddings(to_embed)
                    
                    q_norm = np.linalg.norm(query_vector)
                    for idx, r in enumerate(to_embed):
                        repo_vector = repo_embeddings[idx]
                        r_norm = np.linalg.norm(repo_vector)
                        if q_norm > 0 and r_norm > 0:
                            sim = float(np.dot(query_vector, repo_vector) / (q_norm * r_norm + 1e-8))
                            r["semantic_score"] = max(0.0, min(1.0, sim))
                        else:
                            r["semantic_score"] = 0.5
                    logger.info("Batch computed embeddings for %d repositories in %.2fms", len(to_embed), (time.perf_counter() - embed_start) * 1000)
                except Exception as batch_exc:
                    logger.warning("Batch embedding generation failed: %s", str(batch_exc))
                
                # Assign default semantic score to the remaining candidates to prevent slow on-the-fly sequential generation
                for r in remaining:
                    r["semantic_score"] = 0.1

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
                lexical_score = compute_lexical_score(orig_repo, expanded_queries)
                semantic_similarity = orig_repo.get("semantic_score", 0.0)
                ai_ranking_score = item.final_score
                
                # Hybrid Search: Final Score = Lexical Score + Semantic Similarity + AI Ranking Score (scaled to 100)
                combined_score = (lexical_score + semantic_similarity + ai_ranking_score) / 3.0
                ai_score_val = round(float(combined_score * 100), 1)
                
                logger.info("[Stage 7: AI Ranking] Score Blending for %s: Lexical=%.2f, Semantic=%.2f, AI Ranking=%.2f -> Blended=%.2f", item.repo_id, lexical_score, semantic_similarity, ai_ranking_score, combined_score)

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

    logger.info("[Stage 7: AI Ranking] Leaving: ranked_repos=%d (completed in %.2fms)", len(ranked_repos), (time.perf_counter() - ranking_start) * 1000)

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

    # Apply filters on ranked results before paginating (Stage 8)
    filtered_repos = apply_backend_filters(
        ranked_repos,
        language=language,
        stars=stars,
        forks=forks,
        license=license,
        updated=updated,
        sortBy=sortBy
    )

    # Pagination slice (Stage 9)
    logger.info("[Stage 9: Pagination] Entering: filtered_repos=%d, page=%d, per_page=%d", len(filtered_repos), page, per_page)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_results = filtered_repos[start_idx:end_idx]
    logger.info("[Stage 9: Pagination] Leaving: paginated_results=%d", len(paginated_results))

    total_time = (time.perf_counter() - start_time) * 1000
    logger.info("Search pipeline completed in %.2fms. Returning %d results (page %d).", total_time, len(paginated_results), page)

    res_payload = {
        "source": "hybrid",
        "results": paginated_results,
        "total_count": len(filtered_repos),
        "page": page,
        "per_page": per_page
    }
    logger.info("[Stage 10: API Response] Leaving: total_count=%d, results_count=%d", res_payload["total_count"], len(res_payload["results"]))
    return res_payload