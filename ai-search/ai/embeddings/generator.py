import logging
from typing import Any, Optional

import numpy as np

from ai.embeddings.cache import EmbeddingCache
from ai.embeddings.model_manager import ModelManager
from ai.embeddings.strategies import CompositionStrategy

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        cache_max_size: int = 10000,
        cache_ttl: int = 3600,
        use_cache: bool = True,
    ):
        self._model = ModelManager(model_name=model_name, device=device)
        self._cache = EmbeddingCache(max_size=cache_max_size, ttl_seconds=cache_ttl)
        self._use_cache = use_cache
        self._dim = self._model.dim

    @property
    def dim(self) -> int:
        return self._model.dim

    @property
    def model_name(self) -> str:
        return self._model.model_name

    @property
    def cache_stats(self) -> dict[str, Any]:
        return self._cache.stats

    def warmup(self) -> None:
        self._model.warmup()

    def generate(self, text: str) -> np.ndarray:
        if not text:
            return np.zeros(self._model.dim, dtype=np.float32)
        if self._use_cache:
            cached = self._cache.get(text)
            if cached is not None:
                return cached
        embedding: np.ndarray = self._encode([text])[0]
        if self._use_cache:
            self._cache.set(text, embedding)
        return embedding

    def generate_batch(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self._model.dim), dtype=np.float32)
        results = np.empty((len(texts), self._model.dim), dtype=np.float32)
        uncached_indices = []
        uncached_texts = []
        if self._use_cache:
            for i, text in enumerate(texts):
                if not text:
                    results[i] = np.zeros(self._model.dim, dtype=np.float32)
                    continue
                cached = self._cache.get(text)
                if cached is not None:
                    results[i] = cached
                else:
                    results[i] = np.zeros(self._model.dim, dtype=np.float32)
                    uncached_indices.append(i)
                    uncached_texts.append(text)
        else:
            for i, text in enumerate(texts):
                if not text:
                    results[i] = np.zeros(self._model.dim, dtype=np.float32)
                else:
                    results[i] = np.zeros(self._model.dim, dtype=np.float32)
                    uncached_indices.append(i)
                    uncached_texts.append(text)
        if uncached_texts:
            encoded = self._encode(uncached_texts)
            for idx, vec in zip(uncached_indices, encoded):
                results[idx] = vec
                if self._use_cache:
                    self._cache.set(uncached_texts[uncached_indices.index(idx)], vec)
        return results

    def generate_for_query(self, query: str) -> np.ndarray:
        processed = CompositionStrategy.for_query(query)
        return self.generate(processed)

    def generate_for_description(self, description: Optional[str]) -> np.ndarray:
        processed = CompositionStrategy.for_description(description)
        return self.generate(processed)

    def generate_for_readme(self, readme_text: Optional[str]) -> np.ndarray:
        processed = CompositionStrategy.for_readme(readme_text)
        return self.generate(processed)

    def generate_for_topics(self, topics: Optional[list[str]]) -> np.ndarray:
        processed = CompositionStrategy.for_topics(topics)
        return self.generate(processed)

    def generate_for_tags(self, tags: Optional[list[str]]) -> np.ndarray:
        return self.generate_for_topics(tags)

    def generate_for_repository(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        topics: Optional[list[str]] = None,
        language: Optional[str] = None,
        readme_text: Optional[str] = None,
    ) -> np.ndarray:
        composed = CompositionStrategy.for_repository(
            name=name,
            description=description,
            topics=topics,
            language=language,
            readme_text=readme_text,
        )
        return self.generate(composed)

    def generate_for_metadata(self, text: str) -> np.ndarray:
        processed = CompositionStrategy.for_metadata(text)
        return self.generate(processed)

    def _encode(self, texts: list[str]) -> np.ndarray:
        try:
            return self._model.encode(texts)
        except Exception as exc:
            logger.error("Batch encode failed for %d texts: %s", len(texts), str(exc))
            raise

    def clear_cache(self) -> None:
        self._cache.clear()
