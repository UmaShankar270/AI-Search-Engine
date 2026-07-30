# Changelog

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
