# AI Module FastAPI Integration Specifications

This integration guide provides backend developers with detailed technical specifications, dependency configurations, model mappings, and code templates to integrate the **AI Module** into the FastAPI web backend.

---

## 1. Introduction

### 1.1. Purpose of the AI Module
The AI Module provides natural language processing, semantic search, fuzzy deduplication, multi-dimensional ranking, personalized recommendations, and automated summarizations for repository searches, replacing standard keyword query filters with AI capabilities.

### 1.2. High-Level Architecture
The module is encapsulated using the **Facade Design Pattern**. The FastAPI application interacts strictly with a single interface: [AIFacade](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/facade.py). Subsystem engine details (FAISS, ranking logic, embedding models) are hidden from FastAPI router contexts.

### 1.3. Integration Goals
- **Modular Autonomy:** FastAPI routers are decoupled from search indexes.
- **Concurrent Non-blocking Loops:** Heavy calculations and remote API requests run inside executor thread pools to prevent blocking FastAPI’s event loop.
- **Clean Schema Maps:** Data transfers occur via validated Pydantic models.

---

## 2. AIFacade Overview

### 2.1. Responsibilities
- Coordinates natural language query parsing.
- Drives vector search indexing and cosine similarities.
- Integrates repository metrics scoring (18-factor ranking).
- Executes duplicate detection and groups cross-platform mirrors.
- Runs generative summaries and comparison models.

### 2.2. Lifecycle & Dependency Injection
For production FastAPI environments, **Dependency Injection** is preferred over singletons. This allows easy mock setups during integration tests. 

We initialize a single instance of `AIFacade` during FastAPI startup, store it in the application state, and inject it into routers using FastAPI's `Depends`.

```mermaid
graph TD
    Start[FastAPI Startup] ──> Init[Instantiate AIFacade]
    Init ──> State[Store in app.state.ai_facade]
    State ──> Router[Inject via Depends into Routers]
    Router ──> Request[Process Client Requests]
```

---

## 3. Environment Setup

### 3.1. Prerequisites
- Python 3.12+ (Python 3.14 compatible)
- Environment Variables prefixed with `AI_` loaded from `.env` files.

### 3.2. Required Packages
Ensure the following packages (defined in `requirements.txt`) are present in the FastAPI runtime environment:
- `openai>=1.0.0`
- `sentence-transformers>=2.2.0`
- `faiss-cpu>=1.7.0`
- `pydantic>=2.0.0`
- `pydantic-settings>=2.0.0`
- `numpy>=1.24.0`

---

## 4. FastAPI Integration Blueprint

Here is the setup for initializing and injecting the facade in your FastAPI application (`app/main.py`):

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from ai.facade import AIFacade

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup Initialization
    # Initialize facade and load FAISS vector index
    facade = AIFacade(
        embedding_dim=384,
        search_index_path="data/faiss_index.index",
        ranking_config_path="configs/ranking_weights.json"
    )
    # Warm up sentence-transformer models in memory
    facade.warmup_embeddings()
    app.state.ai_facade = facade
    
    yield
    
    # 2. Shutdown Cleanup
    # Unload embedding model to release CPU/GPU memory resources
    if hasattr(app.state, "ai_facade"):
        app.state.ai_facade._embedding_generator._model.unload()

app = FastAPI(lifespan=lifespan)

# Dependency Injector
def get_ai_facade(request: Request) -> AIFacade:
    return request.app.state.ai_facade
```

### Route Injection Example (`app/routers/search.py`):
```python
from fastapi import APIRouter, Depends, Query
from ai.facade import AIFacade
from app.dependencies import get_ai_facade

router = APIRouter()

@router.get("/search")
async def semantic_search(
    q: str = Query(..., description="Natural language search query"),
    facade: AIFacade = Depends(get_ai_facade)
):
    # Run the query understanding engine
    query_details = facade.understand_query(q)
    
    # Execute semantic search against FAISS index
    search_hits = facade.search(q, top_k=10)
    
    return {
        "query": q,
        "intent": query_details.intent,
        "results": [hit.to_dict() for hit in search_hits.results]
    }
```

---

## 5. Public API Reference

The AIFacade API is frozen with the following definitions:

### 5.1. `understand_query(query: str) -> QueryUnderstandingResult`
* **Purpose:** Performs spell correction, abbreviation expansions, and extracts semantic intents, domains, and filters.
* **Exceptions:** Raises `EmptyQueryError` if query is empty.

### 5.2. `search(query: str, top_k: int = 10, threshold: float = 0.0) -> SearchResult`
* **Purpose:** Queries nearest vector records inside the FAISS index.
* **Exceptions:** Raises `SearchError`, `IndexNotBuiltError`.

### 5.3. `deduplicate(repositories: list[dict[str, Any]]) -> list[dict[str, Any]]`
* **Purpose:** Identifies duplicate/mirror repositories, keeping only the canonical ones.
* **Exceptions:** None.

### 5.4. `rank(query: str, candidates: list[CandidateRepo], intent: str) -> RankedResultSet`
* **Purpose:** Computes weighted multi-factor rankings on repositories.
* **Exceptions:** Raises `RankingError`.

### 5.5. `recommend(repository_id: str, all_repositories: list[dict]) -> RecommendationSet`
* **Purpose:** Generates content-based or hybrid recommendations.
* **Exceptions:** None.

### 5.6. `summarize(repository: Any) -> str`
* **Purpose:** Generates a 2-3 sentence summary of a repository.
* **Exceptions:** Raises `SummaryError`.

### 5.7. `compare(repositories: list[Any]) -> ComparisonResult`
* **Purpose:** Generates a structured comparison matrix across dimensions.
* **Exceptions:** Raises `SummaryError`.

---

## 6. End-to-End Request Flow

```
   [Frontend Client]
         │
         ▼  (HTTP GET /search?q="free python api")
   [FastAPI Route]
         │
         ▼  (facade.understand_query)
   [Query Understanding]  ───> Extracts intent, tech tags, and filters
         │
         ▼  (Fetch repositories from DB / Github)
   [Candidate Collection]
         │
         ▼  (facade.deduplicate)
   [Duplicate Detection]  ───> Merges duplicates (GitLab mirrors, etc.)
         │
         ▼  (facade.search)
   [Semantic Search]      ───> Vector lookup in FAISS Index
         │
         ▼  (facade.rank)
   [Intelligent Ranking]  ───> Calculates health, activity, and documentation scores
         │
         ▼  (facade.summarize)
   [AI Summarizer]        ───> Generates summaries (Gemini/OpenAI or local fallback)
         │
         ▼  (HTTP Response JSON)
   [Frontend Render]
```

---

## 7. Model Mappings

FastAPI schemas inside `backend/app/schemas.py` must align with the AI Module models:

### 7.1. Repository Model
* **AI Target Model:** [Repository](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/models/repository.py#L5)
* **Pydantic Schema mapping:**
  ```python
  from pydantic import BaseModel
  from typing import Optional, List

  class RepositorySchema(BaseModel):
      id: str
      name: str
      full_name: str
      description: Optional[str] = ""
      url: str
      stars: int = 0
      forks: int = 0
      topics: List[str] = []
      language: Optional[str] = ""
      readme_text: Optional[str] = ""
  ```

### 7.2. Search Result Model
* **AI Target Model:** [SearchResult](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/semantic_search/models.py#L35)
* **JSON Mapping Structure:**
  ```json
  {
    "query": "best framework",
    "results": [
      {
        "repo_id": "fastapi",
        "score": 0.895,
        "rank": 1,
        "metadata": {"name": "FastAPI", "language": "Python"}
      }
    ],
    "total_count": 1,
    "search_time_ms": 12.4,
    "threshold": 0.0
  }
  ```

---

## 8. Error Handling & Recovery Protocols

All AI module exceptions inherit from `AIModuleError`. Handle exceptions using FastAPI custom handlers:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ai.models.exceptions import AIModuleError, SummaryError

app = FastAPI()

@app.exception_handler(AIModuleError)
async def ai_module_exception_handler(request: Request, exc: AIModuleError):
    return JSONResponse(
        status_code=400,
        content={"status": "error", "message": f"AI Processing failed: {str(exc)}"}
    )
```

### Fallback Behavior:
- **LLM API Failures:** If Gemini/OpenAI fails during `summarize()` or `compare()`, `SummaryGenerator` catches the exception and falls back to generating a local summary/comparison matrix using repository metadata.
- **Cache Eviction:** Cache miss operations fall back to SentenceTransformer model encoding automatically.

---

## 9. Performance & Resource Optimization

1. **Async Contexts:** Since some AI methods are synchronous and network-bound (e.g. LLM API calls), execute them in async routes using `asyncio.to_thread` to prevent thread blocks:
   ```python
   summary = await asyncio.to_thread(facade.summarize, repo)
   ```
2. **Batch Encoding:** Use `generate_embeddings()` rather than a loop of `generate_embedding()` calls to take advantage of vector processing parallelization.
3. **Memory Garbage Collection:** Call the `unload()` method on `ModelManager` during system updates to release unused RAM/VRAM resources.

---

## 10. Troubleshooting & Deployment Notes

- **Model Download Failures:** Ensure the deployment server has outbound internet access to download Hugging Face models (`all-MiniLM-L6-v2`) during first-time initialization.
- **API Key Configuration:** If Gemini API keys are configured, ensure the environment variable `AI_LLM_PROVIDER="gemini"` is set.
