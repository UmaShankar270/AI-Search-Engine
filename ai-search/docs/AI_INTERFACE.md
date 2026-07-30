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

### Recommendation (future)

#### `recommend(repository_id, all_repositories, top_n=5) -> List[Recommendation]`

Generates recommendations for a given repository. (Planned.)

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
