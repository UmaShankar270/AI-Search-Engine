import logging
from typing import Any, Optional

import numpy as np

from ai.duplicate_detection.detector import DuplicateDetector
from ai.embeddings.generator import EmbeddingGenerator
from ai.models.comparison import ComparisonResult
from ai.query_processor.engine import QueryUnderstandingEngine
from ai.query_processor.models import QueryUnderstandingResult
from ai.ranking.models import CandidateRepo, RankedResultSet
from ai.ranking.service import RankingService
from ai.recommendation.engine import RecommendationEngine
from ai.recommendation.models import RecommendationSet, UserProfile
from ai.semantic_search.faiss_index import FAISSVectorIndex
from ai.semantic_search.metadata_store import IndexMetadataStore
from ai.semantic_search.models import IndexStats, SearchResult
from ai.semantic_search.search_engine import SemanticSearchEngine
from ai.summarizer.summarizer import SummaryGenerator

logger = logging.getLogger(__name__)


class AIFacade:
    """Single entry point for Backend integration with the AI module."""

    def __init__(
        self,
        embedding_dim: int = 384,
        search_index_path: Optional[str] = None,
        ranking_config_path: Optional[str] = None,
    ):
        self._query_engine = QueryUnderstandingEngine()
        self._embedding_generator = EmbeddingGenerator()

        vector_index = FAISSVectorIndex(dimension=embedding_dim)
        metadata_store = IndexMetadataStore()

        self._search_engine = SemanticSearchEngine(
            vector_index=vector_index,
            metadata_store=metadata_store,
            encoder=self.generate_query_embedding,
            batch_encoder=self.generate_embeddings,
        )

        self._search_index_path = search_index_path
        self._ranking_service = RankingService(config_path=ranking_config_path)
        self._recommendation_engine = RecommendationEngine(
            embedding_generator=self._embedding_generator,
        )
        self._summarizer = SummaryGenerator()
        self._duplicate_detector = DuplicateDetector()

    # --- Query Understanding ---

    def understand_query(self, query: str) -> QueryUnderstandingResult:
        return self._query_engine.understand(query)

    # --- Embedding Generation ---

    def generate_embedding(self, text: str) -> np.ndarray:
        return self._embedding_generator.generate(text)

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        return self._embedding_generator.generate_batch(texts)

    def generate_query_embedding(self, query: str) -> np.ndarray:
        return self._embedding_generator.generate_for_query(query)

    def generate_repository_embedding(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        topics: Optional[list[str]] = None,
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
        metadata_list: Optional[list[Optional[dict[str, Any]]]] = None,
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
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self._search_engine.add_repositories(
            repositories=[{"repo_id": repo_id, "text": text, "metadata": metadata or {}}],
        )

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        ids: list[str],
        metadata_list: Optional[list[Optional[dict[str, Any]]]] = None,
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

    # --- Ranking ---

    def rank(
        self,
        query: str,
        candidates: list[CandidateRepo],
        intent: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> RankedResultSet:
        return self._ranking_service.rank(
            query=query,
            candidates=candidates,
            intent=intent,
            top_k=top_k,
        )

    def rank_search_results(
        self,
        query: str,
        search_hits: list[str],
        repo_data_map: dict[str, dict[str, Any]],
        intent: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> RankedResultSet:
        return self._ranking_service.rank_search_results(
            query=query,
            search_hits=search_hits,
            repo_data_map=repo_data_map,
            intent=intent,
            top_k=top_k,
        )

    def rerank_with_cross_encoder(
        self,
        query: str,
        candidates: list[CandidateRepo],
        cross_encoder_fn: Any,
    ) -> RankedResultSet:
        return self._ranking_service.rerank_with_cross_encoder(
            query=query,
            candidates=candidates,
            cross_encoder_fn=cross_encoder_fn,
        )

    def rerank_with_llm(
        self,
        query: str,
        candidates: list[CandidateRepo],
        llm_fn: Any,
    ) -> RankedResultSet:
        return self._ranking_service.rerank_with_llm(
            query=query,
            candidates=candidates,
            llm_fn=llm_fn,
        )

    def get_ranking_weights(self) -> dict[str, Any]:
        return self._ranking_service.get_weight_summary()

    def set_ranking_weight(self, factor_name: str, weight: float) -> None:
        self._ranking_service.weight_manager.set_weight(factor_name, weight)

    def save_ranking_config(self, path: str) -> None:
        self._ranking_service.weight_manager.save(path)

    def load_ranking_config(self, path: str) -> None:
        self._ranking_service.weight_manager.load(path)

    # --- Recommendation ---

    def recommend(
        self,
        repository_id: str,
        all_repositories: list[dict[str, Any]],
        embedding_map: Optional[dict[str, np.ndarray]] = None,
        top_n: int = 5,
    ) -> RecommendationSet:
        if embedding_map is None:
            embedding_map = self._build_embedding_map(all_repositories)
        return self._recommendation_engine.recommend_from_repo(
            repo_id=repository_id,
            all_repos=all_repositories,
            embedding_map=embedding_map,
            top_n=top_n,
        )

    def recommend_from_query(
        self,
        query: str,
        all_repositories: list[dict[str, Any]],
        embedding_map: Optional[dict[str, np.ndarray]] = None,
        top_n: int = 5,
    ) -> RecommendationSet:
        if embedding_map is None:
            embedding_map = self._build_embedding_map(all_repositories)
        query_vector = self.generate_query_embedding(query)
        return self._recommendation_engine.recommend_from_query(
            query_vector=query_vector,
            all_repos=all_repositories,
            embedding_map=embedding_map,
            top_n=top_n,
        )

    def recommend_hybrid(
        self,
        repository_id: str,
        all_repositories: list[dict[str, Any]],
        embedding_map: Optional[dict[str, np.ndarray]] = None,
        user_profile: Optional[UserProfile] = None,
        top_n: int = 5,
    ) -> RecommendationSet:
        if embedding_map is None:
            embedding_map = self._build_embedding_map(all_repositories)
        return self._recommendation_engine.recommend_hybrid(
            repo_id=repository_id,
            all_repos=all_repositories,
            embedding_map=embedding_map,
            user_profile=user_profile,
            top_n=top_n,
        )

    def recommend_popular(
        self,
        all_repositories: list[dict[str, Any]],
        top_n: int = 5,
        sort_key: str = "stars",
    ) -> RecommendationSet:
        return self._recommendation_engine.recommend_popular(
            all_repos=all_repositories,
            top_n=top_n,
            sort_key=sort_key,
        )

    def _build_embedding_map(
        self,
        repositories: list[dict[str, Any]],
    ) -> dict[str, np.ndarray]:
        result: dict[str, np.ndarray] = {}
        for repo in repositories:
            repo_id = repo.get("repo_id", "")
            if not repo_id:
                continue
            try:
                embedding = self.generate_repository_embedding(
                    name=repo.get("name"),
                    description=repo.get("description"),
                    topics=repo.get("topics"),
                    language=repo.get("language"),
                    readme_text=repo.get("readme_text"),
                )
                result[repo_id] = embedding
            except Exception:
                logger.exception("Failed to generate embedding for %s", repo_id)
        return result

    # --- Summarization & Comparison ---

    def summarize(self, repository: Any) -> str:
        return self._summarizer.generate(repository)

    def generate_insight_report(self, repository: Any, readme_text: str = "") -> dict[str, Any]:
        return self._summarizer.generate_insight_report(repository, readme_text)

    def compare(self, repositories: list[Any]) -> ComparisonResult:
        return self._summarizer.compare(repositories)

    # --- Duplicate Detection ---

    def deduplicate(self, repositories: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self._duplicate_detector.deduplicate(repositories)
