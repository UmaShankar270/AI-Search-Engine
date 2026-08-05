# AI E2E Execution Pipeline Specifications

This document defines the E2E execution pipeline of the **AI Module**, detailing the input, processing, output, algorithms, complexity, and components for every stage of query execution.

---

## E2E Pipeline Flowchart

```mermaid
graph TD
    UserQuery[User Query] ──> Step1[1. Query Understanding]
    Step1 ──> Step2[2. Entity Extraction]
    Step2 ──> Step3[3. Intent Detection]
    Step3 ──> Step4[4. Search Collection]
    Step4 ──> Step5[5. Duplicate Detection]
    Step5 ──> Step6[6. Embedding Generation]
    Step6 ──> Step7[7. Semantic Search]
    Step7 ──> Step8[8. Ranking]
    Step8 ──> Step9[9. Recommendation]
    Step9 ──> Step10[10. Summarization]
    Step10 ──> Step11[11. Comparison]
    Step11 ──> Step12[12. Final Response]
```

---

## E2E Pipeline Stages

### 1. Query Understanding
* **Input:** Raw query string (e.g. `"best free python video editor for linux"`).
* **Processing:** Strips extra whitespaces, applies spelling corrections, and expands synonyms/abbreviations using Levenshtein distance against the registry.
* **Output:** Structured search context (`ExtractionContext`).
* **Algorithms Used:** Levenshtein distance matrix calculations.
* **Complexity:** $O(W \times K \times L)$ where $W$ is words in the query, $K$ is known terms, and $L$ is word length.
* **Components Involved:** [SpellingCorrector](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/query_processor/spelling.py#L7), [SynonymResolver](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/query_processor/synonyms.py#L8).

---

### 2. Entity Extraction
* **Input:** Normalised and expanded `ExtractionContext`.
* **Processing:** Scans tokens using regex patterns and checks the registry to identify categories, platforms, databases, programming languages, libraries, and frameworks.
* **Output:** A list of `ExtractedEntity` instances.
* **Algorithms Used:** Regular expression scanning, dictionary mapping lookup.
* **Complexity:** $O(N)$ where $N$ is the number of tokens in the query.
* **Components Involved:** [TechnologyExtractor](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/query_processor/extractors/technology_extractor.py#L12), [DomainExtractor](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/query_processor/extractors/domain_extractor.py#L13), [EntityRegistry](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/query_processor/entity_registry.py#L4).

---

### 3. Intent Detection
* **Input:** Normalised query context and extracted entities list.
* **Processing:** Scores candidate intents (SEARCH, COMPARE, RECOMMEND, EXPLORE, DISCOVER) based on keyword matching.
* **Output:** Primary `IntentType` enum (e.g. `IntentType.RECOMMEND`) with a confidence float.
* **Algorithms Used:** Rule-based scoring with intent decay.
* **Complexity:** $O(P)$ where $P$ is the number of patterns defined.
* **Components Involved:** [IntentExtractor](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/query_processor/extractors/intent_extractor.py#L13).

---

### 4. Search Collection
* **Input:** Query entities (e.g. `FilterType.COST: free`).
* **Processing:** Collects candidate repositories matching filter configurations to establish target search scope.
* **Output:** Scoped list of repository candidates.
* **Algorithms Used:** Metadata logical filtering.
* **Complexity:** $O(C)$ where $C$ is catalog records.
* **Components Involved:** [FilterExtractor](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/query_processor/extractors/filter_extractor.py#L14).

---

### 5. Duplicate Detection
* **Input:** Collected list of candidate repository dictionaries.
* **Processing:** Group duplicate repository names and mirror URLs. Identifies platform mirrors (GitHub ↔ GitLab) using name-normalization and description Levenshtein checks.
* **Output:** Filtered repository list with mirror data appended to canonical repository metadata.
* **Algorithms Used:** Normalized Levenshtein distance string similarity, canonical sorting (stars desc, forks desc, platform priority).
* **Complexity:** $O(M^2 \times D)$ where $M$ is repository count, and $D$ is average description length.
* **Components Involved:** [DuplicateDetector](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/duplicate_detection/detector.py#L7).

---

### 6. Embedding Generation
* **Input:** Cleansed query string or repository documents.
* **Processing:** Preprocesses text, checks the LRU cache (SHA-256 key), and executes batch transformer encoding if not cached.
* **Output:** A dense 1-dimensional float vector (`np.ndarray`).
* **Algorithms Used:** SentenceTransformer dense vector encoding, SHA-256 hash hashing, LRU cache eviction.
* **Complexity:** $O(E)$ for encoding inference (bound by model parameters). Cache retrieval is $O(1)$.
* **Components Involved:** [ModelManager](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/embeddings/model_manager.py#L11), [EmbeddingGenerator](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/embeddings/generator.py#L13), [EmbeddingCache](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/embeddings/cache.py#L12), [CompositionStrategy](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/embeddings/strategies.py#L5).

---

### 7. Semantic Search
* **Input:** Dense query vector and target index.
* **Processing:** Queries the FAISS index for nearest neighbors, maps results to string repository IDs, boosts scores matching names/topics exactly, and filters by score thresholds.
* **Output:** A `SearchResult` containing ranked semantic hits with raw scores.
* **Algorithms Used:** FAISS Inner-Product nearest neighbor calculation, exact-match keyword boosting.
* **Complexity:** $O(V \times D)$ for flat index search, where $V$ is total vectors, and $D$ is embedding dimension.
* **Components Involved:** [FAISSVectorIndex](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/semantic_search/faiss_index.py#L15), [IndexMetadataStore](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/semantic_search/metadata_store.py#L12), [SemanticSearchEngine](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/semantic_search/search_engine.py#L19).

---

### 8. Ranking
* **Input:** Semantic search hits and candidate repository metadata (stars, forks, commits).
* **Processing:** Calculates 18 score factors, normalizes scores using log-scale/sigmoid functions, and aggregates them into weighted scores and sub-scores.
* **Output:** Sorted `RankedResultSet` containing `RankingResult` models.
* **Algorithms Used:** Logarithmic scaling, sigmoid curves, exponential decay, weighted sum aggregation.
* **Complexity:** $O(R \times F)$ where $R$ is candidates, and $F$ is number of active scoring factors (18).
* **Components Involved:** [RankingService](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/ranking/service.py#L14), [ScoreCalculator](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/ranking/calculator.py#L13), [WeightManager](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/ranking/weight_manager.py#L15).

---

### 9. Recommendation
* **Input:** Source repository ID, global catalog, and user preferences.
* **Processing:** Computes content similarity (embedding Cosine + Jaccard topic overlaps) and merges it with popularity and profile preferences.
* **Output:** A `RecommendationSet`.
* **Algorithms Used:** Cosine similarity, Jaccard overlap, hybrid score blending.
* **Complexity:** $O(U \times (D + T))$ where $U$ is total catalog size, $D$ is vector dimensions, and $T$ is topic count.
* **Components Involved:** [RecommendationEngine](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/recommendation/engine.py#L16).

---

### 10. Summarization
* **Input:** Target repository metadata and README text.
* **Processing:** Truncates README text and sends the request to the configured LLM API (Gemini/OpenAI) using asynchronous concurrent thread pools, falling back to a local heuristic summarizer if keys are missing.
* **Output:** Plain-text repository summary string.
* **Algorithms Used:** Concurrent task gathering, text truncation.
* **Complexity:** $O(1)$ network dependency (fallback has $O(\text{description length})$ complexity).
* **Components Involved:** [SummaryGenerator](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/summarizer/summarizer.py#L11).

---

### 11. Comparison
* **Input:** A list of repositories to compare.
* **Processing:** Sends metadata to the LLM to rate the repositories across Features, Activity, Documentation, and Community dimensions in a structured JSON schema.
* **Output:** A `ComparisonResult` object.
* **Algorithms Used:** JSON structure extraction and schema mapping.
* **Complexity:** $O(1)$ network dependency (fallback is $O(\text{repositories})$).
* **Components Involved:** [SummaryGenerator.compare](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/summarizer/summarizer.py#L147).

---

### 12. Final Response
* **Input:** Aggregated results, rankings, summaries, and comparison models.
* **Processing:** Packages the outputs into standard Pydantic models.
* **Output:** Validated JSON-ready payload.
* **Complexity:** $O(\text{output size})$.
* **Components Involved:** [AIFacade](file:///c:/Users/Trinesh/OneDrive/Desktop/AI-Search-Engine/ai-search/ai/facade.py#L21).
