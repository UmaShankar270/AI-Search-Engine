import hashlib
import logging
import time
from collections import OrderedDict
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingCache:
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[np.ndarray, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _make_key(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> Optional[np.ndarray]:
        key = self._make_key(text)
        if key in self._cache:
            embedding, expiry = self._cache[key]
            if time.time() < expiry:
                self._cache.move_to_end(key)
                self._hits += 1
                return embedding
            else:
                del self._cache[key]
        self._misses += 1
        return None

    def set(self, text: str, embedding: np.ndarray) -> None:
        key = self._make_key(text)
        expiry = time.time() + self._ttl
        self._cache[key] = (embedding.copy(), expiry)
        self._cache.move_to_end(key)
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def invalidate(self, text: str) -> bool:
        key = self._make_key(text)
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")

    @property
    def size(self) -> int:
        return len(self._cache)

    @property
    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        return {
            "size": self.size,
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 4),
            "ttl_seconds": self._ttl,
        }
