from __future__ import annotations

import logging
from threading import Lock
from typing import Any, Optional

from .interfaces import IMetadataStore

logger = logging.getLogger(__name__)


class IndexMetadataStore(IMetadataStore):
    def __init__(self) -> None:
        self._repo_to_vector: dict[str, int] = {}
        self._vector_to_repo: dict[int, str] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def add_mapping(
        self, vector_id: int, repo_id: str, metadata: Optional[dict[str, Any]] = None
    ) -> None:
        with self._lock:
            self._repo_to_vector[repo_id] = vector_id
            self._vector_to_repo[vector_id] = repo_id
            if metadata:
                self._metadata[repo_id] = metadata
        logger.debug("Mapped vector_id=%d <-> repo_id=%s", vector_id, repo_id)

    def get_repo_id(self, vector_id: int) -> Optional[str]:
        return self._vector_to_repo.get(vector_id)

    def get_vector_id(self, repo_id: str) -> Optional[int]:
        return self._repo_to_vector.get(repo_id)

    def get_metadata(self, repo_id: str) -> Optional[dict[str, Any]]:
        return self._metadata.get(repo_id)

    def repo_exists(self, repo_id: str) -> bool:
        return repo_id in self._repo_to_vector

    def remove(self, repo_id: str) -> Optional[int]:
        with self._lock:
            vector_id = self._repo_to_vector.pop(repo_id, None)
            if vector_id is not None:
                self._vector_to_repo.pop(vector_id, None)
                self._metadata.pop(repo_id, None)
                logger.info(
                    "Removed mapping for repo_id=%s (vector_id=%d)", repo_id, vector_id
                )
            return vector_id

    def size(self) -> int:
        return len(self._repo_to_vector)

    def clear(self) -> None:
        with self._lock:
            self._repo_to_vector.clear()
            self._vector_to_repo.clear()
            self._metadata.clear()
        logger.info("Cleared metadata store")

    def items(self) -> list[tuple[int, str, Optional[dict[str, Any]]]]:
        result = []
        for repo_id, vector_id in self._repo_to_vector.items():
            result.append((vector_id, repo_id, self._metadata.get(repo_id)))
        return result
