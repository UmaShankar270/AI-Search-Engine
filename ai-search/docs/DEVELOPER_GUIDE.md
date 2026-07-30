# AI Module Developer & Contributor Guide

This guide is intended for engineers contributing to the **AI Module** of the Repository Discovery Platform. It outlines environment configurations, package standards, testing processes, and extension guides.

---

## 1. Project Setup & Installation

### 1.1. Prerequisites
- Python 3.12+ (Project is Python 3.14 compatible)
- Virtual Environment tool (`venv`)

### 1.2. Local Installation
From the repository root directory, navigate to `ai-search` and create the environment:
```bash
cd ai-search
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Validation & Code Quality Pipelines

Before committing code, ensure it passes all testing, linting, and formatting checks.

### 2.1. Running Pytest
Run the full test suite from the `ai-search` directory:
```bash
.venv\Scripts\pytest
```

### 2.2. Running Ruff (Linter & Formatter)
The project enforces a strict line length of 100 characters. Check styling using:
```bash
.venv\Scripts\ruff check .
```
To automatically apply safe format fixes:
```bash
.venv\Scripts\ruff check --fix .
```

### 2.3. Running MyPy (Strict Type Verification)
Verify type hints on all source files:
```bash
.venv\Scripts\mypy .
```

---

## 3. Folder Conventions & Coding Standards

- **Folder Names:** All folder names inside `ai/` represent single subsystems. They must contain an `__init__.py` exposing only public methods and models.
- **Type Hints:** Use strict type hints on all function signatures. Avoid using `Any` where possible.
- **Error Handling:** Submodule operations must raise subclasses of `AIModuleError` defined in [exceptions.py](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/models/exceptions.py). Do not raise generic exceptions.
- **Logger Usage:** Use `logging.getLogger(__name__)` at the top of each file rather than printing to stdout.

---

## 4. Subsystem Extension Tutorials

### 4.1. How to Add a New Ranking Factor
1. Define a subclass of `BaseFactor` inside [factors.py](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/ranking/factors.py#L13):
   ```python
   class MyNewFactor(BaseFactor):
       name = "my_new_factor"
       label = "My New Score Factor"

       def compute(self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None) -> FactorScore:
           raw_value = float(repo.metadata.get("some_metric", 0.0))
           return self._make_score(raw_value, {"some_metric": raw_value})
   ```
2. Register the class by appending it to `FACTOR_CLASSES` at the bottom of [factors.py](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/ranking/factors.py#L328).
3. Set the default weight (summing up to 1.0) and normalization configuration in [defaults.py](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/ranking/defaults.py#L5).

### 4.2. How to Add a New Recommendation Algorithm
1. Open [similarity.py](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/recommendation/similarity.py#L11).
2. Create your similarity metric class (e.g. `PearsonSimilarity`).
3. Add the logic to compute similarity values.
4. Integrate the new similarity score inside the recommendation strategies of `RecommendationEngine` in [engine.py](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/recommendation/engine.py#L16).

### 4.3. How to Add a New Embedding Model
1. Open `.env` or [Settings](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/config/settings.py#L4).
2. Update `AI_MODEL_NAME` to the new SentenceTransformer identifier (e.g., `sentence-transformers/all-mpnet-base-v2`).
3. If the embedding dimension size changes, update `AI_EMBEDDING_DIM` accordingly (e.g., to `768`).
4. Rebuild the vector index using `AIFacade.build_index()`.

### 4.4. How to Add a New Search Platform Adapter
1. Subclass the abstract class [IVectorIndex](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/semantic_search/interfaces.py) in a new integration module (e.g., `ai/semantic_search/qdrant_index.py`):
   ```python
   from ai.semantic_search.interfaces import IVectorIndex

   class QdrantVectorIndex(IVectorIndex):
       def build(self, embeddings, ids): ...
       def search(self, query_vector, top_k): ...
       # ... implement abstract methods
   ```
2. Instantiation: Swap the `vector_index` dependency passed to `SemanticSearchEngine` inside [AIFacade.__init__](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/facade.py#L33) with your new adapter.

---

## 5. Performance Optimization & Debugging

* **RAM Optimization:** If loading multiple embedding models, call `facade._embedding_generator._model.unload()` to release CUDA/VRAM resources.
* **Batch Retrieval:** Always use `generate_embeddings(list[str])` for batch jobs instead of single `generate_embedding()` loops to leverage vector batching optimizations.
* **TTL Cache Tuning:** Adjust cache expiration parameters in `AI_CACHE_TTL_SECONDS` to optimize memory footprints during high-traffic intervals.

---

## 6. Contribution Workflow

1. **Branch Naming:** Format branches as `feature/ai-<name>` or `bugfix/ai-<name>`.
2. **Implementation:** Write clean code conforming to SOLID standards.
3. **Tests:** Implement matching pytest cases in the `tests/` directory.
4. **Verification:** Run `pytest`, `ruff check .`, and `mypy .` locally before pushing code.
5. **Git Protocol:** Commit clean chunks and submit Pull Requests to `backend-dev`.
