from abc import ABC, abstractmethod
from typing import Optional

import numpy as np

from .models import IndexStats, SearchHit


class IVectorIndex(ABC):
    @abstractmethod
    def build(self, embeddings: np.ndarray, ids: list[str]) -> IndexStats:
        ...

    @abstractmethod
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
    ) -> list[SearchHit]:
        ...

    @abstractmethod
    def add(self, embeddings: np.ndarray, ids: list[str]) -> None:
        ...

    @abstractmethod
    def remove(self, ids: list[str]) -> None:
        ...

    @abstractmethod
    def save(self, path: str) -> None:
        ...

    @abstractmethod
    def load(self, path: str) -> None:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...

    @property
    @abstractmethod
    def size(self) -> int:
        ...

    @property
    @abstractmethod
    def dim(self) -> int:
        ...

    @property
    @abstractmethod
    def is_trained(self) -> bool:
        ...


class IMetadataStore(ABC):
    @abstractmethod
    def add_mapping(
        self, vector_id: int, repo_id: str, metadata: Optional[dict] = None
    ) -> None:
        ...

    @abstractmethod
    def get_repo_id(self, vector_id: int) -> Optional[str]:
        ...

    @abstractmethod
    def get_vector_id(self, repo_id: str) -> Optional[int]:
        ...

    @abstractmethod
    def get_metadata(self, repo_id: str) -> Optional[dict]:
        ...

    @abstractmethod
    def repo_exists(self, repo_id: str) -> bool:
        ...

    @abstractmethod
    def remove(self, repo_id: str) -> Optional[int]:
        ...

    @abstractmethod
    def size(self) -> int:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...

    @abstractmethod
    def items(self) -> list[tuple[int, str, Optional[dict]]]:
        ...
