# AI Module Architecture

## Overview

The AI module follows a clean layered architecture with the `AIFacade` as the single public entry point. Internal modules are organized by responsibility and communicate through well-defined interfaces.

## Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                         AI FACADE                               │
│              Single entry point for Backend                     │
├─────────────────────────────────────────────────────────────────┤
│  understand_query()  search()  recommend()  summarize()         │
└───────┬──────────────────────┬──────────────────┬───────────────┘
        │                      │                  │
        ▼                      │                  │
┌───────────────────┐          │                  │
│ QUERY UNDERSTAND  │          │                  │
│                   │          │                  │
│ QueryUnderstanding│          │                  │
│ Engine            │          │                  │
├───────────────────┤          │                  │
│ SpellingCorrector │          │                  │
│ SynonymResolver   │          │                  │
│ IntentExtractor   │          │                  │
│ DomainExtractor   │          │                  │
│ TechnologyExtract │          │                  │
│ FilterExtractor   │          │                  │
│ LLMExtractor(opt) │          │                  │
└───────────────────┘          │                  │
                               ▼                  ▼
                       ┌──────────────┐  ┌──────────────┐
                       │  EMBED GEN   │  │  SUMMARY GEN │
                       │  FAISS       │  │              │
                       │  RANKER      │  │              │
                       │  RECOMMENDER │  │              │
                       └──────────────┘  └──────────────┘
```

## Design Principles

1. **Single Responsibility** — Each module does exactly one thing.
2. **Dependency Inversion** — Modules depend on abstractions, not concretions.
3. **Fail Fast** — Validate inputs at the facade boundary.
4. **Graceful Degradation** — If LLM API fails, fall back to embedding-only mode.

## Data Flow

See `docs/AI_INTERFACE.md` for detailed interface contracts.
