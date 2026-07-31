from __future__ import annotations

import logging
import time
from typing import Any, Callable, Optional

import numpy as np

from .faiss_index import FAISSVectorIndex
from .interfaces import IMetadataStore, IVectorIndex
from .models import IndexStats, SearchHit, SearchResult

logger = logging.getLogger(__name__)

EncoderFn = Callable[[str], np.ndarray]
BatchEncoderFn = Callable[[list[str]], np.ndarray]


class SemanticSearchEngine:
    def __init__(
        self,
        vector_index: IVectorIndex,
        metadata_store: IMetadataStore,
        encoder: Optional[EncoderFn] = None,
        batch_encoder: Optional[BatchEncoderFn] = None,
        default_top_k: int = 10,
        default_threshold: float = 0.0,
        boost_factor: float = 1.5,
    ):
        self._vector_index = vector_index
        self._metadata_store = metadata_store
        self._encoder = encoder
        self._batch_encoder = batch_encoder
        self._default_top_k = default_top_k
        self._default_threshold = default_threshold
        self._boost_factor = boost_factor

    def set_encoder(self, encoder: EncoderFn) -> None:
        self._encoder = encoder

    def set_batch_encoder(self, batch_encoder: BatchEncoderFn) -> None:
        self._batch_encoder = batch_encoder

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        boost_exact_match: bool = True,
    ) -> SearchResult:
        start = time.perf_counter()

        if not query or not query.strip():
            logger.warning("Empty query received")
            return SearchResult(query=query or "")

        k = top_k if top_k is not None else self._default_top_k
        thr = threshold if threshold is not None else self._default_threshold

        query_vector = self._encode_query(query)
        if query_vector is None:
            logger.error("Failed to encode query: %s", query)
            return SearchResult(query=query)

        hits = self._vector_index.search(query_vector, top_k=k)
        scored = self._apply_search_metadata(hits)

        if thr > 0.0:
            scored = [h for h in scored if h.score >= thr]

        if boost_exact_match and scored:
            scored = self._apply_exact_match_boost(query, scored)

        elapsed = (time.perf_counter() - start) * 1000

        return SearchResult(
            query=query,
            results=scored[:k],
            total_count=len(scored),
            search_time_ms=round(elapsed, 2),
            threshold=thr,
        )

    def search_by_vector(
        self,
        query_vector: np.ndarray,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> SearchResult:
        start = time.perf_counter()
        k = top_k if top_k is not None else self._default_top_k
        thr = threshold if threshold is not None else self._default_threshold

        hits = self._vector_index.search(query_vector, top_k=k)
        scored = self._apply_search_metadata(hits)

        if thr > 0.0:
            scored = [h for h in scored if h.score >= thr]

        elapsed = (time.perf_counter() - start) * 1000
        return SearchResult(
            query="",
            results=scored[:k],
            total_count=len(scored),
            search_time_ms=round(elapsed, 2),
            threshold=thr,
        )

    def batch_search(
        self,
        queries: list[str],
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        boost_exact_match: bool = True,
    ) -> list[SearchResult]:
        if not queries:
            return []

        k = top_k if top_k is not None else self._default_top_k
        thr = threshold if threshold is not None else self._default_threshold

        if self._batch_encoder is not None:
            query_vectors = self._batch_encoder(queries)
        else:
            query_vectors = None

        results: list[SearchResult] = []
        for i, query in enumerate(queries):
            if query_vectors is not None:
                qv = query_vectors[i]
            else:
                qv = self._encode_query(query)

            if qv is None:
                results.append(SearchResult(query=query))
                continue

            hits = self._vector_index.search(qv, top_k=k)
            scored = self._apply_search_metadata(hits)

            if thr > 0.0:
                scored = [h for h in scored if h.score >= thr]

            if boost_exact_match and scored:
                scored = self._apply_exact_match_boost(query, scored)

            results.append(
                SearchResult(
                    query=query,
                    results=scored[:k],
                    total_count=len(scored),
                    threshold=thr,
                )
            )

        return results

    def build_index(
        self,
        repositories: list[dict[str, Any]],
        encoder: Optional[EncoderFn] = None,
    ) -> IndexStats:
        if not repositories:
            logger.warning("No repositories provided to build_index")
            return IndexStats()

        enc = encoder or self._encoder
        if enc is None:
            raise ValueError("No encoder available for building index")

        repo_ids = []
        texts = []
        metadata_list = []

        for repo in repositories:
            repo_id = repo.get("repo_id") or repo.get("id", "")
            text = repo.get("text") or repo.get("content", "")
            repo_ids.append(repo_id)
            texts.append(text)
            metadata_list.append(repo.get("metadata", {}))

        if self._batch_encoder is not None:
            batch_embeddings = self._batch_encoder(texts)
        else:
            batch_embeddings = np.array([enc(t) for t in texts], dtype=np.float32)

        self._vector_index.clear()
        self._metadata_store.clear()
        stats = self._vector_index.build(batch_embeddings, repo_ids)

        for repo_id, meta in zip(repo_ids, metadata_list):
            self._metadata_store.add_mapping(
                vector_id=FAISSVectorIndex.hash_id(repo_id),
                repo_id=repo_id,
                metadata=meta,
            )

        logger.info(
            "Built search index with %d repositories, stats=%s",
            len(repo_ids),
            stats,
        )
        return stats

    def build_index_from_embeddings(
        self,
        embeddings: np.ndarray,
        ids: list[str],
        metadata_list: Optional[list[Optional[dict[str, Any]]]] = None,
    ) -> IndexStats:
        if len(embeddings) != len(ids):
            raise ValueError(
                f"Embeddings length {len(embeddings)} != ids length {len(ids)}"
            )

        self._vector_index.clear()
        self._metadata_store.clear()
        stats = self._vector_index.build(embeddings, ids)

        for i, repo_id in enumerate(ids):
            meta = metadata_list[i] if metadata_list else None
            self._metadata_store.add_mapping(
                vector_id=FAISSVectorIndex.hash_id(repo_id),
                repo_id=repo_id,
                metadata=meta,
            )

        return stats

    def add_repositories(
        self,
        repositories: list[dict[str, Any]],
        encoder: Optional[EncoderFn] = None,
    ) -> None:
        if not repositories:
            return

        enc = encoder or self._encoder
        if enc is None:
            raise ValueError("No encoder available for adding repositories")

        repo_ids = []
        texts = []
        metadata_list = []

        for repo in repositories:
            repo_id = repo.get("repo_id") or repo.get("id", "")
            text = repo.get("text") or repo.get("content", "")
            repo_ids.append(repo_id)
            texts.append(text)
            metadata_list.append(repo.get("metadata", {}))

        if self._batch_encoder is not None:
            batch_embeddings = self._batch_encoder(texts)
        else:
            batch_embeddings = np.array([enc(t) for t in texts], dtype=np.float32)

        self._vector_index.add(batch_embeddings, repo_ids)

        for repo_id, meta in zip(repo_ids, metadata_list):
            self._metadata_store.add_mapping(
                vector_id=FAISSVectorIndex.hash_id(repo_id),
                repo_id=repo_id,
                metadata=meta,
            )

        logger.info("Added %d repositories to search index", len(repo_ids))

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        ids: list[str],
        metadata_list: Optional[list[Optional[dict[str, Any]]]] = None,
    ) -> None:
        if len(embeddings) != len(ids):
            raise ValueError(
                f"Embeddings length {len(embeddings)} != ids length {len(ids)}"
            )

        self._vector_index.add(embeddings, ids)

        for i, repo_id in enumerate(ids):
            meta = metadata_list[i] if metadata_list else None
            self._metadata_store.add_mapping(
                vector_id=FAISSVectorIndex.hash_id(repo_id),
                repo_id=repo_id,
                metadata=meta,
            )

    def remove_repository(self, repo_id: str) -> bool:
        vector_id = self._metadata_store.remove(repo_id)
        if vector_id is not None:
            self._vector_index.remove([repo_id])
            logger.info("Removed repository %s from search index", repo_id)
            return True
        logger.warning("Repository %s not found in index", repo_id)
        return False

    def save(self, path: str) -> None:
        self._vector_index.save(path)
        self._metadata_store.save(path + ".json")

    def load(self, path: str) -> None:
        self._vector_index.load(path)
        self._metadata_store.load(path + ".json")


    def clear(self) -> None:
        self._vector_index.clear()
        self._metadata_store.clear()
        logger.info("Cleared search engine state")

    def get_index_stats(self) -> IndexStats:
        return IndexStats(
            total_vectors=self._vector_index.size,
            dimension=self._vector_index.dim,
            index_type=getattr(self._vector_index, "_index_type", "unknown"),
            memory_usage_bytes=0,
        )

    def _encode_query(self, query: str) -> Optional[np.ndarray]:
        if self._encoder is None:
            logger.error("No encoder configured for query encoding")
            return None
        try:
            return self._encoder(query)
        except Exception as e:
            logger.error("Failed to encode query '%s': %s", query, str(e))
            return None

    def _apply_search_metadata(self, hits: list[SearchHit]) -> list[SearchHit]:
        result = []
        for hit in hits:
            try:
                faiss_id = int(hit.repo_id)
                repo_id = self._metadata_store.get_repo_id(faiss_id)
                if repo_id is None:
                    continue
                metadata = self._metadata_store.get_metadata(repo_id)
                result.append(
                    SearchHit(
                        repo_id=repo_id,
                        score=hit.score,
                        rank=hit.rank,
                        metadata=metadata,
                    )
                )
            except (ValueError, TypeError):
                result.append(hit)
        return result

    def _apply_exact_match_boost(
        self, query: str, hits: list[SearchHit]
    ) -> list[SearchHit]:
        query_lower = query.lower().strip()

        for hit in hits:
            boost = False
            if hit.repo_id and query_lower in hit.repo_id.lower():
                boost = True
            if hit.metadata:
                name = hit.metadata.get("name", "")
                if query_lower in name.lower():
                    boost = True
                topics = hit.metadata.get("topics", []) or []
                for topic in topics:
                    if query_lower in topic.lower():
                        boost = True
                        break
            if boost:
                hit.score = min(1.0, hit.score * self._boost_factor)

        hits.sort(key=lambda h: h.score, reverse=True)
        for i, hit in enumerate(hits):
            hit.rank = i + 1
        return hits
