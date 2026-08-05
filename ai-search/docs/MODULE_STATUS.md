# AI Module Status

## Current Phase: Phase 7 — Recommendation Engine

## Completed
- Architecture design and documentation
- Project folder structure and scaffold
- **Query Understanding Module** (Phase 3)
- **Embedding Module** (Phase 4)
- **Semantic Search Engine** (Phase 5)
- **Intelligent Repository Ranking Engine** (Phase 6)
  - 18 configurable ranking factors with per-factor weights summing to 1.00
  - `NormalizationEngine` — 6 normalization methods: identity, log-scale, sigmoid, exp-decay, boolean, min-max
  - `WeightManager` — load/save/override weights from JSON config, deep-copied defaults
  - 18 `BaseFactor` calculators — each with name, label, raw_value, normalized_score, weight, contribution
  - `ScoreCalculator` — weighted sum composable scoring, sub-scores (health, popularity)
  - `RankingService` — orchestrator with `rank()`, `rank_search_results()`, `rerank_with_cross_encoder()`, `rerank_with_llm()`
  - `AIFacade.rank/rank_search_results/rerank_with_*/get_ranking_weights/set_ranking_weight/save/load_ranking_config`
  - Future ML-ready: ScoreCalculator can be replaced by an ML ranker implementing same interface
  - **63 tests** — normalization, weight management, factors, calculator, service, integration

- **Recommendation Engine** (Phase 7)
  - `CosineSimilarity` — vector cosine similarity with similarity matrix support
  - `TopicSimilarity` — Jaccard, weighted Jaccard, overlap coefficient for topic sets
  - `AggregatedSimilarity` — configurable weighted combo of embedding (0.60), topic (0.25), language (0.15)
  - `RecommendationEngine` — 4 recommendation strategies:
    - `recommend_from_repo` — content-based: embedding similarity + topic overlap + language match
    - `recommend_from_query` — query-based: cosine similarity to query vector
    - `recommend_hybrid` — hybrid: content similarity (0.50) + popularity (0.30) + user profile (0.20)
    - `recommend_popular` — top-N by configurable sort key (default: stars)
  - `UserProfile` — preferences for languages, topics, categories, weighted tags
  - `Recommendation` / `RecommendationSet` — data models with per-recommendation breakdown
  - `AIFacade.recommend()`, `recommend_from_query()`, `recommend_hybrid()`, `recommend_popular()` — public API
  - **77 tests** — models, similarity, engine strategies, popularity/profile scores, edge cases

## Pending
- Phase 8: Summarization Module
- Phase 9: Facade integration
- Phase 10: Benchmarking and optimization

## Test Status
- **316 passed** (all unit + search + ranking + recommendation + summarization)
- **24 skipped** (real embedding model integration — blocked by network policy)
- **1 warning** (asyncio_mode config — cosmetic)
