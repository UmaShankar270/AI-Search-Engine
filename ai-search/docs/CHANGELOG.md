# Changelog

## [0.6.0] - 2026-07-30
### Added
- Recommendation Engine (Phase 7)
- `CosineSimilarity` — vector cosine similarity with similarity matrix support
- `TopicSimilarity` — Jaccard, weighted Jaccard, and overlap coefficient for topic sets
- `AggregatedSimilarity` — configurable weighted combination of embedding, topic, and language similarity
- `RecommendationEngine` — 4 strategies: `recommend_from_repo` (content-based), `recommend_from_query` (query-based), `recommend_hybrid` (content + popularity + user profile), `recommend_popular` (top-N by sort key)
- `UserProfile` — preferences for languages, topics, categories, and weighted tags
- `Recommendation` / `RecommendationSet` — data models with per-recommendation breakdown
- `AIFacade.recommend()`, `recommend_from_query()`, `recommend_hybrid()`, `recommend_popular()` — public API
- 77 recommendation tests (models, similarity, engine strategies, edge cases, consistency)

## [0.5.0] - 2026-07-30
### Added
- Intelligent Repository Ranking Engine (Phase 6)
- 18 configurable ranking factors with normalization (identity, log-scale, sigmoid, exp-decay, boolean, min-max)
- `NormalizationEngine` — 6 normalization strategies for diverse metrics
- `WeightManager` — load/save/override weights from JSON config with deep-copied defaults
- `BaseFactor` / 18 factor calculators — SemanticSimilarity, GitHubStars, ForkCount, ContributorCount, CommitFrequency, RecentActivity, RepositoryAge, ReleaseFrequency, IssueResolutionRate, PRActivity, DocumentationQuality, READMECompleteness, LicenseAvailability, RepositoryHealth, CommunityAdoption, PopularityTrend, TechnologyMatch, UserIntentMatch
- `ScoreCalculator` — weighted sum composable scoring with health/popularity sub-scores
- `RankingService` — orchestrator: rank, rank_search_results, rerank_with_cross_encoder, rerank_with_llm
- `AIFacade.rank()`, `rank_search_results()`, `rerank_with_cross_encoder()`, `rerank_with_llm()`, `get_ranking_weights()`, `set_ranking_weight()`, `save_ranking_config()`, `load_ranking_config()` — public API
- 63 ranking tests (normalization, weights, factors, calculator, service, integration)

## [0.4.0] - 2026-07-30
### Added
- Semantic Search Engine (Phase 5)
- `IVectorIndex` / `IMetadataStore` — abstract interfaces for backend swaps
- `FAISSVectorIndex` — FAISS-based vector index (IndexFlatIP, IndexIDMap, IVF)
- `IndexMetadataStore` — thread-safe mapping of FAISS hash IDs ↔ repo IDs + metadata
- `SemanticSearchEngine` — orchestrator: search, search_by_vector, batch_search, build_index, add_embeddings, remove_repository, save/load/clear
- `AIFacade.search()`, `search_by_vector()`, `batch_search()`, `build_index()`, `build_index_from_embeddings()`, `add_repository()`, `add_embeddings()`, `remove_repository()`, `save_index()`, `load_index()`, `get_index_stats()`, `clear_index()` — public API
- 73 semantic search tests (FAISS index, metadata store, search engine, integration, edge cases)

## [0.3.0] - 2026-07-30
### Added
- Embedding Module (Phase 4)
- `ModelManager` — Sentence Transformer singleton lifecycle (lazy load, warmup, unload)
- `EmbeddingGenerator` — single, batch, and content-type-specific embedding generation
- `CompositionStrategy` — text preprocessing for query, description, README, topics, repository metadata, tags
- `EmbeddingCache` — LRU cache with TTL-based expiry, eviction, hit-rate stats
- `AIFacade.generate_embedding()`, `generate_embeddings()`, `generate_query_embedding()`, `generate_repository_embedding()`, `warmup_embeddings()` — public API
- 56 embedding module tests (32 unit + 24 integration)
- Model availability detection for graceful test skipping

## [0.2.0] - 2026-07-30
### Added
- Query Understanding Module (Phase 3)
- `QueryUnderstandingEngine` — pipeline orchestrator
- `SpellingCorrector` — Levenshtein-based spelling correction
- `SynonymResolver` — synonym and abbreviation resolution
- `IntentExtractor` — detects SEARCH, COMPARE, RECOMMEND, EXPLORE, DISCOVER
- `DomainExtractor` — detects application domain/category
- `TechnologyExtractor` — detects programming languages, frameworks, libraries, tools, databases, platforms
- `FilterExtractor` — detects cost, license, platform, popularity, maintenance filters
- `LLMExtractor` — pluggable LLM-based extraction (extensible future use)
- `EntityRegistry` — singleton knowledge base with 300+ entities
- Comprehensive test suite (50+ tests) covering all modules and edge cases
- `AIFacade.understand_query()` — public API for Backend integration

## [0.1.0] - 2026-07-30
### Added
- Initial project scaffold
- Architecture design
- Folder structure and placeholder files
