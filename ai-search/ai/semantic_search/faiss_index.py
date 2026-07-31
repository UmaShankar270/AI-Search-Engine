from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from .interfaces import IVectorIndex
from .models import IndexStats, SearchHit

logger = logging.getLogger(__name__)


class FAISSVectorIndex(IVectorIndex):
    NORMALIZE_EPS = 1e-12

    def __init__(
        self,
        dimension: int = 384,
        index_type: str = "flat",
        nlist: int = 100,
        metric: str = "cosine",
        use_id_map: bool = True,
    ):
        self._dimension = dimension
        self._index_type = index_type
        self._nlist = nlist
        self._metric = metric
        self._use_id_map = use_id_map
        self._index: Any = None
        self._total = 0

    @staticmethod
    def hash_id(repo_id: str) -> int:
        import hashlib
        h = hashlib.sha256(repo_id.encode("utf-8")).digest()
        val = int.from_bytes(h[:8], byteorder="big")
        return val & 0x7FFFFFFFFFFFFFFF


    def _lazy_init_index(self) -> None:
        if self._index is not None:
            return
        import faiss

        if self._metric == "cosine":
            metric = faiss.METRIC_INNER_PRODUCT
        elif self._metric == "l2":
            metric = faiss.METRIC_L2
        else:
            raise ValueError(f"Unsupported metric: {self._metric}")

        base: Any = None
        if self._index_type == "flat":
            base = faiss.IndexFlat(self._dimension, metric)
        elif self._index_type == "ivf":
            quantizer = faiss.IndexFlat(self._dimension, metric)
            base = faiss.IndexIVFFlat(quantizer, self._dimension, self._nlist, metric)
            base.nprobe = min(self._nlist, 10)
        else:
            raise ValueError(f"Unsupported index type: {self._index_type}")

        if self._use_id_map:
            self._index = faiss.IndexIDMap(base)
        else:
            self._index = base

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.maximum(norms, self.NORMALIZE_EPS)
        result: np.ndarray = vectors / norms
        return result

    def _ensure_contiguous(self, vectors: np.ndarray) -> np.ndarray:
        return np.ascontiguousarray(vectors, dtype=np.float32)

    def build(self, embeddings: np.ndarray, ids: list[str]) -> IndexStats:

        self.clear()
        self._dimension = embeddings.shape[1]

        self._lazy_init_index()

        if self._metric == "cosine":
            embeddings = self._normalize(embeddings)

        id_array = np.array([self.hash_id(i) for i in ids], dtype=np.int64)

        if self._index_type == "ivf" and not self._index.is_trained:
            self._index.train(embeddings)

        self._index.add_with_ids(embeddings, id_array)
        self._total = self._index.ntotal

        memory = embeddings.nbytes + (self._total * self._dimension * 4)
        logger.info(
            "Built FAISS index: %d vectors, dim=%d, type=%s",
            self._total,
            self._dimension,
            self._index_type,
        )
        return IndexStats(
            total_vectors=self._total,
            dimension=self._dimension,
            index_type=self._index_type,
            memory_usage_bytes=memory,
        )

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
    ) -> list[SearchHit]:
        if self._index is None or self._total == 0:
            return []

        query = self._ensure_contiguous(query_vector.reshape(1, -1))
        if self._metric == "cosine":
            query = self._normalize(query)

        actual_k = min(top_k, self._total)
        distances, indices = self._index.search(query, actual_k)

        results = []
        for i in range(actual_k):
            idx = indices[0][i]
            dist = float(distances[0][i])
            if idx == -1:
                continue
            score = dist if self._metric == "l2" else float(max(0.0, dist))
            results.append(
                SearchHit(
                    repo_id=str(idx),
                    score=score,
                    rank=i + 1,
                )
            )

        return results

    def add(self, embeddings: np.ndarray, ids: list[str]) -> None:

        if self._index is None:
            self._lazy_init_index()

        embeddings = self._ensure_contiguous(embeddings)
        if self._metric == "cosine":
            embeddings = self._normalize(embeddings)

        id_array = np.array([self.hash_id(i) for i in ids], dtype=np.int64)

        if self._index_type == "ivf" and not self._index.is_trained:
            self._index.train(embeddings)

        self._index.add_with_ids(embeddings, id_array)
        self._total = self._index.ntotal
        logger.info("Added %d vectors to FAISS index, total=%d", len(ids), self._total)

    def remove(self, ids: list[str]) -> None:
        if self._index is None:
            return

        id_array = np.array(
            [self.hash_id(i) for i in ids], dtype=np.int64
        )

        if hasattr(self._index, "remove_ids"):
            import faiss

            id_selector = faiss.IDSelectorArray(id_array)
            self._index.remove_ids(id_selector)
            self._total = self._index.ntotal
            logger.info(
                "Removed %d vectors from FAISS index, total=%d",
                len(ids),
                self._total,
            )
        else:
            raise NotImplementedError(
                "remove() requires an index that supports remove_ids"
            )

    def save(self, path: str) -> None:
        if self._index is None:
            raise RuntimeError("No index to save")
        import faiss

        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(path_obj))
        logger.info("Saved FAISS index to %s (%d vectors)", path, self._total)

    def load(self, path: str) -> None:
        import faiss

        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Index file not found: {path}")

        self._index = faiss.read_index(str(path_obj))
        self._total = self._index.ntotal
        self._dimension = self._index.d

        logger.info(
            "Loaded FAISS index from %s (%d vectors, dim=%d)",
            path,
            self._total,
            self._dimension,
        )

    def clear(self) -> None:
        self._index = None
        self._total = 0
        logger.info("Cleared FAISS index")

    @property
    def size(self) -> int:
        return self._total

    @property
    def dim(self) -> int:
        return self._dimension

    @property
    def is_trained(self) -> bool:
        if self._index is None:
            return False
        result: bool = self._index.is_trained
        return result

    @property
    def index(self) -> Any:
        return self._index
