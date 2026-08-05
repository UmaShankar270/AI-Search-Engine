
# AI Module — Repository Discovery Platform

## Purpose

The AI module powers the intelligent search, ranking, recommendation, and summarization capabilities of the AI-Powered Repository Discovery Platform. It transforms raw repository metadata and natural language queries into semantically meaningful results.

## Responsibilities

- Natural language query processing and normalization
- Vector embedding generation using Sentence Transformers
- Semantic similarity search via FAISS
- Multi-stage result ranking (BM25 → cross-encoder → LLM re-rank)
- Content-based and hybrid repository recommendations
- AI-generated repository summaries using Gemini/OpenAI

## Architecture

```
ai/
├── config/            # Configuration and settings
├── query_processor/   # NL query normalization & expansion
├── embeddings/        # Vector embedding generation
├── semantic_search/   # FAISS index management & search
├── ranking/           # Multi-stage ranking pipeline
├── recommendation/    # Recommendation engine
├── summarizer/        # AI summary generation
├── models/            # Shared Pydantic data models
├── interfaces/        # Abstract interfaces / contracts
├── utils/             # Shared utilities
├── cache/             # Caching layer
```

## Dependencies

See `requirements.txt`. Key packages: `sentence-transformers`, `faiss-cpu`, `openai`, `numpy`, `pydantic`.

## Usage

```python
from ai.facade import AIFacade

facade = AIFacade()
result = facade.search("machine learning framework", repositories)
```

## Documentation

- `docs/AI_INTERFACE.md` — Full interface contract for Backend integration
- `docs/ARCHITECTURE.md` — Detailed architecture design
- `docs/MODULE_STATUS.md` — Current development status
- `docs/CHANGELOG.md` — Version history
