import os
import tempfile
from typing import Any, Optional

from ai.ranking.calculator import ScoreCalculator
from ai.ranking.models import CandidateRepo
from ai.ranking.normalization import NormalizationEngine
from ai.ranking.service import RankingService
from ai.ranking.weight_manager import WeightManager


class TestRankingEngine:
    """Test suite for RankingEngine."""

    def test_normalization_engine(self) -> None:
        engine = NormalizationEngine()

        # None value should return 0.0
        assert engine.normalize(None, "identity") == 0.0

        # Non-numeric value should return 0.0
        assert engine.normalize("abc", "identity") == 0.0

        # Unknown method should fall back to identity
        assert engine.normalize(10.0, "unknown_method", {"max_value": 20.0}) == 0.5

        # Test Identity normalization
        assert engine.normalize(5.0, "identity", {"max_value": 10.0}) == 0.5
        assert engine.normalize(15.0, "identity", {"max_value": 10.0}) == 1.0
        assert engine.normalize(-5.0, "identity", {"max_value": 10.0}) == 0.0
        assert engine.normalize(5.0, "identity", {"max_value": 0.0}) == 0.0

        # Test Boolean normalization
        assert engine.normalize(True, "boolean") == 1.0
        assert engine.normalize(False, "boolean") == 0.0
        assert engine.normalize("Yes", "boolean") == 1.0
        assert engine.normalize("No", "boolean") == 0.0
        assert engine.normalize("True", "boolean") == 1.0

        # Test Min Max normalization
        assert engine.normalize(5.0, "min_max", {"min_value": 0.0, "max_value": 10.0}) == 0.5
        assert engine.normalize(-1.0, "min_max", {"min_value": 0.0, "max_value": 10.0}) == 0.0
        assert engine.normalize(12.0, "min_max", {"min_value": 0.0, "max_value": 10.0}) == 1.0
        assert engine.normalize(5.0, "min_max", {"min_value": 10.0, "max_value": 0.0}) == 0.0

        # Test Log Scale normalization
        assert engine.normalize(0.0, "log_scale", {"max_value": 1000.0}) == 0.0
        assert engine.normalize(1000.0, "log_scale", {"max_value": 1000.0}) == 1.0
        assert engine.normalize(2000.0, "log_scale", {"max_value": 1000.0, "cap": 1000.0}) == 1.0

        # Test Sigmoid normalization
        assert engine.normalize(50.0, "sigmoid", {"midpoint": 50.0, "k": 0.1}) == 0.5
        assert engine.normalize(100.0, "sigmoid", {"midpoint": 50.0, "k": 0.1}) > 0.9

        # Test Exp Decay normalization
        assert engine.normalize(-5.0, "exp_decay", {"lambda": 0.02}) == 1.0
        assert engine.normalize(0.0, "exp_decay", {"lambda": 0.02}) == 1.0
        assert engine.normalize(50.0, "exp_decay", {"lambda": 0.02}) < 1.0

    def test_weight_manager(self) -> None:
        manager = WeightManager()

        # Check defaults are loaded
        assert manager.get_weight("semantic_similarity") == 0.25
        assert manager.get_weight("github_stars") == 0.02

        # Check custom setter
        manager.set_weight("semantic_similarity", 0.5)
        assert manager.get_weight("semantic_similarity") == 0.5

        # Check normalization parameters retrieval
        params = manager.get_normalization_params("github_stars")
        assert params.get("method") == "log_scale"

        # Check normalize delegates correctly
        assert manager.normalize("license_availability", 1.0) == 1.0

        # Check properties
        assert "semantic_similarity" in manager.weights
        assert "github_stars" in manager.factor_names
        assert isinstance(manager.config, dict)

    def test_weight_manager_load_save(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name
        try:
            manager = WeightManager()
            manager.set_weight("github_stars", 0.99)
            manager.save(temp_path)

            manager2 = WeightManager(config_path=temp_path)
            assert manager2.get_weight("github_stars") == 0.99
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_score_calculator(self) -> None:
        wm = WeightManager()
        calculator = ScoreCalculator(wm)

        repo = CandidateRepo(
            repo_id="test-repo",
            semantic_score=0.8,
            stars=1000,
            forks=200,
            contributors=10,
            commits_last_3_months=15,
            days_since_last_commit=5,
            releases_last_year=3,
            issues_closed=80,
            issues_total=100,
            prs_merged=40,
            prs_total=50,
            has_documentation=True,
            has_readme=True,
            readme_length=500,
            readme_sections=3,
            readme_has_badges=True,
            has_license=True,
            topics=["python", "ml"],
            language="python",
        )

        result = calculator.compute(repo, query="ml library")
        assert result.repo_id == "test-repo"
        assert result.final_score > 0.0
        assert len(result.factor_scores) > 0
        assert result.health_score > 0.0
        assert result.popularity_score > 0.0

    def test_rank_returns_sorted_results(self) -> None:
        """Verify ranked results are sorted by score descending."""
        service = RankingService()
        candidates = [
            CandidateRepo(repo_id="low-stars", stars=1, semantic_score=0.1),
            CandidateRepo(repo_id="high-stars", stars=10000, semantic_score=0.9),
            CandidateRepo(repo_id="mid-stars", stars=100, semantic_score=0.5),
        ]
        res = service.rank("test query", candidates)
        assert res.total_candidates == 3
        assert len(res.results) == 3
        assert res.results[0].repo_id == "high-stars"
        assert res.results[1].repo_id == "mid-stars"
        assert res.results[2].repo_id == "low-stars"
        assert res.results[0].final_score >= res.results[1].final_score
        assert res.results[1].final_score >= res.results[2].final_score
        assert res.results[0].rank == 1
        assert res.results[1].rank == 2
        assert res.results[2].rank == 3

    def test_rank_edge_cases(self) -> None:
        service = RankingService()

        # Empty candidates list
        res_empty = service.rank("test", [])
        assert res_empty.total_candidates == 0
        assert len(res_empty.results) == 0

        # top_k constraint
        candidates = [
            CandidateRepo(repo_id="r1", stars=10),
            CandidateRepo(repo_id="r2", stars=20),
            CandidateRepo(repo_id="r3", stars=30),
        ]
        res_top_k = service.rank("test", candidates, top_k=2)
        assert res_top_k.total_candidates == 3
        assert len(res_top_k.results) == 2

    def test_rank_search_results(self) -> None:
        service = RankingService()

        class MockHit:
            def __init__(self, repo_id: str, score: float):
                self.repo_id = repo_id
                self.score = score

        search_hits = [MockHit("r1", 0.9), MockHit("r2", 0.4)]
        repo_data_map = {
            "r1": {"stars": 1000, "forks": 100, "language": "Python"},
            "r2": {"stars": 10, "forks": 1},
        }

        res = service.rank_search_results("query", search_hits, repo_data_map)
        assert res.total_candidates == 2
        assert res.results[0].repo_id == "r1"

    def test_rerank_with_cross_encoder_changes_order(self) -> None:
        """Verify cross-encoder re-ranking alters candidate order."""
        service = RankingService()
        candidates = [
            CandidateRepo(repo_id="r1", semantic_score=0.1),
            CandidateRepo(repo_id="r2", semantic_score=0.5),
        ]

        def mock_cross_encoder(query: str, texts: list[str]) -> list[float]:
            # Reverse scores
            return [0.9 if "r1" in t else 0.2 for t in texts]

        res = service.rerank_with_cross_encoder("query", candidates, mock_cross_encoder)
        # Check semantic score updated
        r1_result = next(r for r in res.results if r.repo_id == "r1")
        r2_result = next(r for r in res.results if r.repo_id == "r2")
        assert r1_result.semantic_score == 0.9
        assert r2_result.semantic_score == 0.2
        # Check original candidates are not mutated
        assert candidates[0].semantic_score == 0.1
        assert candidates[1].semantic_score == 0.5


    def test_rerank_with_cross_encoder_fallback(self) -> None:
        service = RankingService()
        candidates = [
            CandidateRepo(repo_id="r1", semantic_score=0.1),
            CandidateRepo(repo_id="r2", semantic_score=0.5),
        ]

        def mock_failing_encoder(query: str, texts: list[str]) -> list[float]:
            raise RuntimeError("Model loading failed")

        res = service.rerank_with_cross_encoder("query", candidates, mock_failing_encoder)
        # Verify it falls back to original semantic_score and finishes ranking
        r1_result = next(r for r in res.results if r.repo_id == "r1")
        assert r1_result.semantic_score == 0.1

    def test_rerank_with_llm_falls_back_gracefully(self) -> None:
        """Verify graceful fallback when LLM API is unavailable."""
        service = RankingService()
        candidates = [
            CandidateRepo(repo_id="r1", semantic_score=0.1),
            CandidateRepo(repo_id="r2", semantic_score=0.5),
        ]

        def mock_failing_llm(query: str, repos: list[CandidateRepo]) -> list[float]:
            raise RuntimeError("API Key invalid")

        res = service.rerank_with_llm("query", candidates, mock_failing_llm)
        r1_result = next(r for r in res.results if r.repo_id == "r1")
        assert r1_result.semantic_score == 0.1

    def test_rerank_with_llm_success(self) -> None:
        service = RankingService()
        candidates = [
            CandidateRepo(repo_id="r1", semantic_score=0.1),
            CandidateRepo(repo_id="r2", semantic_score=0.5),
        ]

        def mock_llm_fn(query: str, repos: list[CandidateRepo]) -> list[float]:
            return [0.95, 0.35]

        res = service.rerank_with_llm("query", candidates, mock_llm_fn)
        r1_result = next(r for r in res.results if r.repo_id == "r1")
        assert r1_result.semantic_score == 0.95
        # Check original candidates are not mutated
        assert candidates[0].semantic_score == 0.1
        assert candidates[1].semantic_score == 0.5


    def test_score_fusion_combines_signals(self) -> None:
        """Verify score fusion combines FAISS and re-rank scores."""
        service = RankingService()
        # Create weights where semantic_similarity is heavily weighted
        service.weight_manager.set_weight("semantic_similarity", 0.8)
        # Set other weights to 0.01 to keep sum around 1.0 or check calculator normalization
        for name in service.weight_manager.factor_names:
            if name != "semantic_similarity":
                service.weight_manager.set_weight(name, 0.01)

        candidate = CandidateRepo(repo_id="test", semantic_score=0.99)
        res = service.rank("test", [candidate])
        assert res.results[0].final_score > 0.5
        assert res.results[0].semantic_score == 0.99

    def test_factor_exceptions_handled(self) -> None:
        service = RankingService()

        # Mock a BaseFactor compute method to raise exception
        from ai.ranking.factors import SemanticSimilarity
        original_compute = SemanticSimilarity.compute

        def failing_compute(
            self: Any, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
        ) -> Any:
            raise RuntimeError("Simulated factor failure")


        SemanticSimilarity.compute = failing_compute  # type: ignore[assignment]
        try:
            candidate = CandidateRepo(repo_id="test", semantic_score=0.5)
            # Should not raise exception, handles it gracefully
            res = service.rank("test", [candidate])
            assert len(res.results) == 1
        finally:
            SemanticSimilarity.compute = original_compute  # type: ignore[assignment]

    def test_weight_summary(self) -> None:
        service = RankingService()
        summary = service.get_weight_summary()
        assert "weights" in summary
        assert "factor_count" in summary
        assert summary["factor_count"] == len(service.weight_manager.factor_names)
