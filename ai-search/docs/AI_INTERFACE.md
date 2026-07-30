# AI Module Interface Contract

## Overview

This document defines the public API contract between the AI module and the Backend. The Backend must only interact with the AI module through the `AIFacade` class.

## Public Interface

### AIFacade

The single entry point. Imported as:

```python
from ai.facade import AIFacade
facade = AIFacade()
```

### Query Understanding

#### `understand_query(query: str) -> QueryUnderstandingResult`

Analyzes a natural language query to extract intent, domain, technologies, and filters.

**Input:**
- `query` (str): Raw natural language query (e.g., "best free video editor for linux")

**Output:** `QueryUnderstandingResult`
| Field | Type | Description |
|-------|------|-------------|
| `original_query` | str | Raw query as received |
| `normalized_query` | str | Cleaned and normalized query |
| `corrected_query` | str | Query after spelling correction |
| `expanded_query` | str | Query with synonyms/abbreviations expanded |
| `intent` | IntentType | SEARCH, COMPARE, RECOMMEND, EXPLORE, DISCOVER, UNKNOWN |
| `domain` | str? | Detected application domain (e.g., "video editing") |
| `technologies` | List[Technology] | All detected technologies with types |
| `programming_languages` | List[str] | Detected programming languages |
| `frameworks` | List[str] | Detected frameworks |
| `categories` | List[str] | Detected software categories |
| `libraries` | List[str] | Detected libraries |
| `tools` | List[str] | Detected tools |
| `databases` | List[str] | Detected databases |
| `platforms` | List[str] | Detected platforms |
| `filters` | List[Filter] | Extracted filters (cost, license, platform, etc.) |
| `confidence` | float | Overall confidence score (0.0 - 1.0) |
| `processing_time_ms` | float | Processing time in milliseconds |

**Example:**
```python
result = facade.understand_query("compare react vs vue for web development")
# result.intent == IntentType.COMPARE
# result.frameworks == ["React", "Vue.js"]
# result.categories == ["Web Framework"]
```

### Embedding Generation

#### `generate_embedding(text: str) -> np.ndarray`

Generate a vector embedding for arbitrary text.

#### `generate_embeddings(texts: list[str]) -> np.ndarray`

Generate vector embeddings for a batch of texts.

#### `generate_query_embedding(query: str) -> np.ndarray`

Generate embedding specifically for a search query (normalized).

#### `generate_repository_embedding(name, description, topics, language, readme_text) -> np.ndarray`

Generate embedding from combined repository metadata (name, description, topics, language, README).

#### `warmup_embeddings() -> None`

Pre-load the Sentence Transformer model into memory.

**Example:**
```python
facade = AIFacade()
facade.warmup_embeddings()
vec = facade.generate_query_embedding("machine learning framework")
# vec.shape == (384,)
repo_vec = facade.generate_repository_embedding(
    name="fastapi",
    description="A modern Python web framework",
    topics=["python", "api", "async"],
    language="Python",
)
```

### Semantic Search

#### `search(query, top_k=10, threshold=0.0, boost_exact_match=True) -> SearchResult`

Semantic search over the built index. Encodes the query and retrieves the nearest vectors.

**Input:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | str | — | Natural language search query |
| `top_k` | int | 10 | Max results to return |
| `threshold` | float | 0.0 | Minimum similarity score (0.0–1.0) |
| `boost_exact_match` | bool | True | Boost results matching repo name/topics |

**Output:** `SearchResult`
| Field | Type | Description |
|-------|------|-------------|
| `query` | str | Original query |
| `results` | list[SearchHit] | Ranked results |
| `total_count` | int | Results after threshold |
| `search_time_ms` | float | Duration in ms |
| `threshold` | float | Applied threshold |

**Example:**
```python
result = facade.search("machine learning framework", top_k=5, threshold=0.3)
for hit in result.results:
    print(f"{hit.rank}. {hit.repo_id} (score={hit.score:.4f})")
```

#### `search_by_vector(query_vector, top_k=10, threshold=0.0) -> SearchResult`

Search using a pre-computed embedding vector. Useful for "more like this" scenarios.

#### `batch_search(queries, top_k=10, threshold=0.0, boost_exact_match=True) -> list[SearchResult]`

Execute multiple searches in a single call. Uses batch encoding when available.

#### `build_index(repositories) -> IndexStats`

Build or rebuild the vector index from a list of repository dicts.

**Input:** Each repo dict:
| Key | Type | Description |
|-----|------|-------------|
| `repo_id` | str | Unique identifier |
| `text` | str | Text content to embed |
| `metadata` | dict | Optional: name, topics, language, etc. |

**Example:**
```python
repos = [
    {"repo_id": "fastapi", "text": "modern python web framework",
     "metadata": {"name": "FastAPI", "topics": ["python", "api"]}},
]
stats = facade.build_index(repos)
# stats.total_vectors == 1
```

#### `build_index_from_embeddings(embeddings, ids, metadata_list=None) -> IndexStats`

Build index from pre-computed embeddings (avoids re-encoding).

#### `add_repository(repo_id, text, metadata=None) -> None`

Incrementally add a single repository to the index.

#### `add_embeddings(embeddings, ids, metadata_list=None) -> None`

Add pre-computed embeddings incrementally.

#### `remove_repository(repo_id) -> bool`

Remove a repository from the index by ID. Returns True if found.

#### `save_index(path) -> None`
#### `load_index(path) -> None`

Persist / restore the vector index to/from disk.

#### `get_index_stats() -> IndexStats`

Retrieve current index statistics (vector count, dimension, type).

#### `clear_index() -> None`

Remove all vectors and metadata from the index.

### Ranking

#### `rank(query, candidates, intent=None, top_k=None) -> RankedResultSet`

Rank a list of `CandidateRepo` objects using the 18-factor weighted scoring model.

**Input:**
| Param | Type | Description |
|-------|------|-------------|
| `query` | str | Original search query |
| `candidates` | list[CandidateRepo] | Repository candidates with metrics |
| `intent` | str? | Query intent from understanding module |
| `top_k` | int? | Max results to return |

**Output:** `RankedResultSet`
| Field | Type | Description |
|-------|------|-------------|
| `query` | str | Original query |
| `results` | list[RankingResult] | Ranked results with per-factor breakdown |
| `total_candidates` | int | Input candidate count |
| `processing_time_ms` | float | Duration in ms |
| `intent` | str? | Matching intent |

**Example:**
```python
from ai.ranking.models import CandidateRepo

candidates = [
    CandidateRepo(repo_id="fastapi", semantic_score=0.92,
                  stars=85000, forks=12000, contributors=500,
                  days_since_last_commit=1, has_license=True,
                  has_readme=True, readme_length=5000,
                  issues_closed=2000, issues_total=2100,
                  topics=["python", "api"], language="Python"),
]
result = facade.rank("python web framework", candidates, top_k=10)
for r in result.results:
    print(f"#{r.rank}: {r.repo_id} (score={r.final_score:.4f})")
    breakpoint = [f"{fs.label}={fs.normalized_score:.2f}" for fs in r.factor_scores[:3]]
```

#### `rank_search_results(query, search_hits, repo_data_map, intent=None, top_k=None) -> RankedResultSet`

Rank the output of `search()` by building `CandidateRepo` objects from search hits and a repo data dictionary.

#### `rerank_with_cross_encoder(query, candidates, cross_encoder_fn) -> RankedResultSet`

Re-score candidates using a cross-encoder model (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`). Falls back gracefully on failure.

#### `rerank_with_llm(query, candidates, llm_fn) -> RankedResultSet`

Re-score candidates using an LLM. The `llm_fn` receives `(query, candidates)` and must return a list of scores. Falls back gracefully on failure.

#### `get_ranking_weights() -> dict`

Return current weight configuration for all 18 factors.

#### `set_ranking_weight(factor_name, weight) -> None`

Override a factor's weight at runtime. Persist with `save_ranking_config()`.

#### `save_ranking_config(path) -> None`
#### `load_ranking_config(path) -> None`

Persist / restore ranking weights to/from a JSON file.

### Recommendation

#### `recommend(repository_id, all_repositories, embedding_map=None, top_n=5) -> RecommendationSet`

Content-based recommendations: finds repositories similar to `repository_id` using embedding cosine similarity, topic Jaccard overlap, and language match.

**Input:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `repository_id` | str | — | Source repository ID to base recommendations on |
| `all_repositories` | list[dict] | — | All candidate repos, each with `repo_id`, `topics`, `language`, `stars`, etc. |
| `embedding_map` | dict[str, np.ndarray]? | None | Pre-computed embeddings (auto-generated if omitted) |
| `top_n` | int | 5 | Max recommendations to return |

**Output:** `RecommendationSet`
| Field | Type | Description |
|-------|------|-------------|
| `source` | str | e.g. `"repo:fastapi"` |
| `recommendations` | list[Recommendation] | Ranked recommendations |
| `total_candidates` | int | Candidates considered |
| `processing_time_ms` | float | Duration in ms |
| `strategy` | str | `"content_based"` |

**Each `Recommendation`:**
| Field | Type | Description |
|-------|------|-------------|
| `repo_id` | str | Recommended repo ID |
| `score` | float | Aggregate similarity (0–1) |
| `reason` | str | Human-readable explanation |
| `similarity_score` | float | Raw embedding similarity |
| `popularity_score` | float | Popularity component (0 for content-based) |
| `language` | str | Repository language |
| `matched_topics` | list[str] | Overlapping topics |

**Example:**
```python
repos = [
    {"repo_id": "fastapi", "topics": ["python", "api"], "language": "Python"},
    {"repo_id": "flask", "topics": ["python", "web"], "language": "Python"},
]
result = facade.recommend("fastapi", repos, top_n=3)
for rec in result.recommendations:
    print(f"{rec.repo_id}: {rec.score:.3f} — {rec.reason}")
```

#### `recommend_from_query(query, all_repositories, embedding_map=None, top_n=5) -> RecommendationSet`

Query-to-repository recommendations. Encodes the query and finds repos with highest cosine similarity.

#### `recommend_hybrid(repository_id, all_repositories, embedding_map=None, user_profile=None, top_n=5) -> RecommendationSet`

Hybrid recommendations combining content similarity (50%), popularity (30%), and user profile (20%). The `user_profile` is a `UserProfile` with `preferred_languages`, `preferred_topics`, `weighted_tags`.

#### `recommend_popular(all_repositories, top_n=5, sort_key="stars") -> RecommendationSet`

Simple popular recommendations: top-N repos sorted by `sort_key` (stars, forks, etc.).

### Summary (future)

#### `summarize(repository) -> str`

Generates an AI summary for a single repository. (Planned.)

#### `compare(repositories) -> ComparisonResult`

Compares multiple repositories across dimensions. (Planned.)

## Data Models

| Model | Location | Description |
|-------|----------|-------------|
| `QueryUnderstandingResult` | `ai/query_processor/models.py` | Query analysis output |
| `SearchHit` | `ai/semantic_search/models.py` | Single search result with score + metadata |
| `SearchResult` | `ai/semantic_search/models.py` | Complete search response |
| `IndexStats` | `ai/semantic_search/models.py` | Index statistics |
| `CandidateRepo` | `ai/ranking/models.py` | Repository candidate with all ranking metrics |
| `RankingResult` | `ai/ranking/models.py` | Ranked result with per-factor breakdown |
| `RankedResultSet` | `ai/ranking/models.py` | Complete ranking response |
| `FactorScore` | `ai/ranking/models.py` | Individual factor score with contribution |

## Error Handling

All exceptions inherit from `AIModuleError` (defined in `ai/models/exceptions.py`).

## Backend Swap

The vector index backend (currently FAISS) can be replaced by implementing `IVectorIndex`:

```python
from ai.semantic_search.interfaces import IVectorIndex

class PineconeIndex(IVectorIndex):
    def build(self, embeddings, ids): ...
    def search(self, query_vector, top_k): ...
    # ... implement all abstract methods
```
