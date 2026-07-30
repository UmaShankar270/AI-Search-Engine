from typing import Any, Optional

import numpy as np

from ai.embeddings.generator import EmbeddingGenerator
from ai.query_processor.engine import QueryUnderstandingEngine
from ai.query_processor.models import QueryUnderstandingResult
from ai.semantic_search.faiss_index import FAISSVectorIndex
from ai.semantic_search.metadata_store import IndexMetadataStore
from ai.semantic_search.models import IndexStats, SearchHit, SearchResult
from ai.semantic_search.search_engine import SemanticSearchEngine


class AIFacade:
    """Single entry point for Backend integration with the AI module."""

    def __init__(
        self,
        embedding_dim: int = 384,
        search_index_path: Optional[str] = None,
    ):
        self._query_engine = QueryUnderstandingEngine()
        self._embedding_generator = EmbeddingGenerator()

        vector_index = FAISSVectorIndex(dimension=embedding_dim)
        metadata_store = IndexMetadataStore()

        self._search_engine = SemanticSearchEngine(
            vector_index=vector_index,
            metadata_store=metadata_store,
            encoder=self._embedding_generator.generate_query_embedding,
            batch_encoder=self._embedding_generator.generate_embeddings,
        )

        self._search_index_path = search_index_path

    # --- Query Understanding ---

    def understand_query(self, query: str) -> QueryUnderstandingResult:
        return self._query_engine.understand(query)

    # --- Embedding Generation ---

    def generate_embedding(self, text: str) -> np.ndarray:
        return self._embedding_generator.generate(text)

    def generate_embeddings(self, texts: list) -> np.ndarray:
        return self._embedding_generator.generate_batch(texts)

    def generate_query_embedding(self, query: str) -> np.ndarray:
        return self._embedding_generator.generate_for_query(query)

    def generate_repository_embedding(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        topics: Optional[list] = None,
        language: Optional[str] = None,
        readme_text: Optional[str] = None,
    ) -> np.ndarray:
        return self._embedding_generator.generate_for_repository(
            name=name,
            description=description,
            topics=topics,
            language=language,
            readme_text=readme_text,
        )

    def warmup_embeddings(self) -> None:
        self._embedding_generator.warmup()

    @property
    def embedding_dim(self) -> int:
        return self._embedding_generator.dim

    @property
    def embedding_model_name(self) -> str:
        return self._embedding_generator.model_name

    # --- Semantic Search ---

    def search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.0,
        boost_exact_match: bool = True,
    ) -> SearchResult:
        return self._search_engine.search(
            query=query,
            top_k=top_k,
            threshold=threshold,
            boost_exact_match=boost_exact_match,
        )

    def search_by_vector(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.0,
    ) -> SearchResult:
        return self._search_engine.search_by_vector(
            query_vector=query_vector,
            top_k=top_k,
            threshold=threshold,
        )

    def batch_search(
        self,
        queries: list[str],
        top_k: int = 10,
        threshold: float = 0.0,
        boost_exact_match: bool = True,
    ) -> list[SearchResult]:
        return self._search_engine.batch_search(
            queries=queries,
            top_k=top_k,
            threshold=threshold,
            boost_exact_match=boost_exact_match,
        )

    def build_index(
        self,
        repositories: list[dict[str, Any]],
    ) -> IndexStats:
        stats = self._search_engine.build_index(
            repositories=repositories,
        )
        if self._search_index_path:
            self._search_engine.save(self._search_index_path)
        return stats

    def build_index_from_embeddings(
        self,
        embeddings: np.ndarray,
        ids: list[str],
        metadata_list: Optional[list[Optional[dict]]] = None,
    ) -> IndexStats:
        return self._search_engine.build_index_from_embeddings(
            embeddings=embeddings,
            ids=ids,
            metadata_list=metadata_list,
        )

    def add_repository(
        self,
        repo_id: str,
        text: str,
        metadata: Optional[dict] = None,
    ) -> None:
        self._search_engine.add_repositories(
            repositories=[{"repo_id": repo_id, "text": text, "metadata": metadata or {}}],
        )

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        ids: list[str],
        metadata_list: Optional[list[Optional[dict]]] = None,
    ) -> None:
        self._search_engine.add_embeddings(
            embeddings=embeddings,
            ids=ids,
            metadata_list=metadata_list,
        )

    def remove_repository(self, repo_id: str) -> bool:
        return self._search_engine.remove_repository(repo_id=repo_id)

    def save_index(self, path: str) -> None:
        self._search_engine.save(path)

    def load_index(self, path: str) -> None:
        self._search_engine.load(path)

    def get_index_stats(self) -> IndexStats:
        return self._search_engine.get_index_stats()

    def clear_index(self) -> None:
        self._search_engine.clear()

    # --- Stubs for future phases ---

    def recommend(self, repository_id: str, all_repositories: list, top_n: int = 5):
        pass

    def summarize(self, repository):
        pass

    def compare(self, repositories: list):
        pass
