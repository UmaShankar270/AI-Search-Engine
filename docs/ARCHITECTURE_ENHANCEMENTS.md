# Architecture Enhancements & Optimizations

This document summarizes the architectural improvements and optimizations implemented to enhance search relevance, query performance, and platform responsiveness.

## 1. High-Performance Repository Discovery
- **Parallel Fetching**: Discovery requests to hosting platforms are executed concurrently using Python's `ThreadPoolExecutor`. Up to 5 pages per query (up to 500 repository candidates) are pulled concurrently at `per_page=100` page sizes.
- **Fail-Safe Aggregation**: A timeout threshold (3.0s) prevents hanging threads from blocking responses. If a provider times out or fails (e.g., due to rate limits), the engine gracefully returns all accumulated results.
- **Smart Query Scoping**: If the search string has no specific constraints, the engine automatically appends `in:name,description,topics` scope filters to maximize repository recall rates.

## 2. Advanced Hybrid Scoring & Query Expansion
- **Lexical Blending**: Combines embedding similarity with token overlap keywords. The blended score is defined as:
  $$\text{Score} = 0.5 \times \text{SemanticSimilarity} + 0.5 \times \text{LexicalScore}$$
- **Synonym Expansion**: Expands general search intents (`video editor` and `chatbot` synonyms) to pull contextually rich candidates in parallel.
- **Dynamic exact-match boosting**: Multiplies matching relevance scores by up to 2.0x for exact repository name, programming language, topic tag, or substring occurrences.

## 3. Performance Bugfixes (O(N+M) Jaccard Similarity)
- **Bottleneck Resolution**: Previously, comparing candidate description fields using Levenshtein distance took $O(N \times M)$ operations, which would stall the server for large candidate pools.
- **Hybrid String Comparison**: Long text segments (descriptions $\geq 50$ characters) are now matched using Jaccard token-overlap. Short texts (e.g., repository names) continue to use Levenshtein distance for precise spelling verification.

## 4. Query-Level Caching & Filtering
- **SQLite Cached Pools**: Full sorted search result listings are cached at a query-level key (`ranked_query_{query}_{language}`) in SQLite.
- **Local Database Slicing**: When the user requests different pages or toggles filters, the backend loads the full list from the cache, runs `apply_backend_filters` locally, and slices the result. This delivers instant sub-millisecond pagination transitions.

## 5. Rich Explanations & Trust/Maturity Factors
- **RepositoryTrust factor**: Rewards verified organization owners (e.g. google, microsoft, apache) and high contributor/stars numbers.
- **ProjectMaturity factor**: Disincentivizes archived repositories and boosts projects with frequent version releases or established ages.
- **Explainable Bullets**: Dynamically builds reason lists (e.g., `"Highly trusted publisher"`, `"Stable release maturity"`) based on normalized calculator factor scores.
