"""Tests for the Semantic Search module."""

from __future__ import annotations

import os
import tempfile
from typing import Any

import numpy as np
import pytest

from ai.semantic_search.faiss_index import FAISSVectorIndex
from ai.semantic_search.metadata_store import IndexMetadataStore
from ai.semantic_search.models import IndexStats, SearchHit, SearchResult
from ai.semantic_search.search_engine import SemanticSearchEngine

RNG = np.random.default_rng(42)
DIM = 16


@pytest.fixture
def sample_embeddings() -> np.ndarray:
    return RNG.random((20, DIM)).astype(np.float32)


@pytest.fixture
def sample_ids() -> list[str]:
    return [f"repo-{i}" for i in range(20)]


@pytest.fixture
def sample_metadata() -> list[dict[str, Any]]:
    topics_map = {
        "repo-0": ["gpu", "ml"],
        "repo-1": ["web", "api"],
        "repo-5": ["web", "framework"],
        "repo-10": ["gpu", "compute"],
    }
    return [
        {
            "name": ["alpha", "beta", "gamma", "delta", "epsilon"][i % 5],
            "language": "Rust" if i % 2 == 0 else "Python",
            "topics": topics_map.get(f"repo-{i}", []),
        }
        for i in range(20)
    ]


@pytest.fixture
def sample_repos(sample_ids, sample_metadata) -> list[dict[str, Any]]:
    return [
        {"repo_id": rid, "text": f"Repository {rid} content", "metadata": meta}
        for rid, meta in zip(sample_ids, sample_metadata)
    ]


@pytest.fixture
def faiss_index() -> FAISSVectorIndex:
    return FAISSVectorIndex(dimension=DIM)


@pytest.fixture
def metadata_store() -> IndexMetadataStore:
    return IndexMetadataStore()


@pytest.fixture
def built_index(faiss_index, sample_embeddings, sample_ids) -> FAISSVectorIndex:
    faiss_index.build(sample_embeddings, sample_ids)
    return faiss_index


def dummy_encoder(text: str) -> np.ndarray:
    return RNG.random(DIM).astype(np.float32)


def dummy_batch_encoder(texts: list[str]) -> np.ndarray:
    return RNG.random((len(texts), DIM)).astype(np.float32)


# ===================================================================
#  SECTION 1 — FAISSVectorIndex
# ===================================================================


class TestFAISSVectorIndex:
    def test_hash_id_consistency(self) -> None:
        rid = "my-repo"
        h1 = FAISSVectorIndex.hash_id(rid)
        h2 = FAISSVectorIndex.hash_id(rid)
        assert h1 == h2
        assert isinstance(h1, int)
        assert 0 <= h1 <= 0x7FFFFFFFFFFFFFFF

    def test_hash_id_uniqueness(self) -> None:
        ids = [f"repo-{i}" for i in range(100)]
        hashes = [FAISSVectorIndex.hash_id(rid) for rid in ids]
        assert len(set(hashes)) > 95

    def test_build_returns_stats(self, faiss_index) -> None:
        vecs = RNG.random((5, DIM)).astype(np.float32)
        stats = faiss_index.build(vecs, ["a", "b", "c", "d", "e"])
        assert isinstance(stats, IndexStats)
        assert stats.total_vectors == 5
        assert stats.dimension == DIM

    def test_size_after_build(self, built_index) -> None:
        assert built_index.size == 20

    def test_dim_returned(self, built_index) -> None:
        assert built_index.dim == DIM

    def test_is_trained_true_after_build(self, built_index) -> None:
        assert built_index.is_trained is True

    def test_search_returns_correct_count(self, built_index) -> None:
        q = RNG.random(DIM).astype(np.float32)
        results = built_index.search(q, top_k=5)
        assert len(results) <= 5
        assert all(isinstance(h, SearchHit) for h in results)

    def test_search_results_are_sorted_by_score_desc(self, built_index) -> None:
        q = RNG.random(DIM).astype(np.float32)
        results = built_index.search(q, top_k=10)
        scores = [h.score for h in results]
        assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))

    def test_search_ranks_are_consecutive(self, built_index) -> None:
        q = RNG.random(DIM).astype(np.float32)
        results = built_index.search(q, top_k=7)
        assert [h.rank for h in results] == list(range(1, len(results) + 1))

    def test_search_on_empty_index_returns_empty(self, faiss_index) -> None:
        q = RNG.random(DIM).astype(np.float32)
        assert faiss_index.search(q, top_k=5) == []

    def test_search_top_k_greater_than_size(self, built_index) -> None:
        q = RNG.random(DIM).astype(np.float32)
        results = built_index.search(q, top_k=100)
        assert len(results) == 20

    def test_add_incremental(self, built_index) -> None:
        new_vecs = RNG.random((3, DIM)).astype(np.float32)
        built_index.add(new_vecs, ["new-1", "new-2", "new-3"])
        assert built_index.size == 23

    def test_add_on_empty_index(self, faiss_index) -> None:
        new_vecs = RNG.random((3, DIM)).astype(np.float32)
        faiss_index.add(new_vecs, ["a", "b", "c"])
        assert faiss_index.size == 3

    def test_remove_vectors(self, built_index) -> None:
        built_index.remove(["repo-0", "repo-1"])
        assert built_index.size == 18

    def test_remove_with_hash(self, built_index) -> None:
        h = FAISSVectorIndex.hash_id("repo-0")
        built_index.remove(["repo-0"])
        q = RNG.random(DIM).astype(np.float32)
        hits = built_index.search(q, top_k=20)
        faiss_ids = [int(h.repo_id) for h in hits]
        assert h not in faiss_ids

    def test_save_and_load(self, built_index) -> None:
        with tempfile.NamedTemporaryFile(suffix=".faiss", delete=False) as f:
            path = f.name
        try:
            built_index.save(path)
            new_index = FAISSVectorIndex(dimension=DIM)
            new_index.load(path)
            assert new_index.size == 20
            assert new_index.dim == DIM
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_load_raises_on_missing_file(self, faiss_index) -> None:
        with pytest.raises(FileNotFoundError):
            faiss_index.load("/nonexistent/path.index")

    def test_save_raises_on_empty_index(self, faiss_index) -> None:
        with pytest.raises(RuntimeError):
            faiss_index.save("/tmp/should-not-exist.index")

    def test_clear_empties_index(self, built_index) -> None:
        built_index.clear()
        assert built_index.size == 0
        assert built_index.is_trained is False

    def test_rebuild_replaces(self, built_index) -> None:
        new_vecs = RNG.random((3, DIM)).astype(np.float32)
        built_index.build(new_vecs, ["x", "y", "z"])
        assert built_index.size == 3

    def test_l2_metric(self) -> None:
        idx = FAISSVectorIndex(dimension=DIM, metric="l2")
        vecs = RNG.random((5, DIM)).astype(np.float32)
        idx.build(vecs, ["a", "b", "c", "d", "e"])
        results = idx.search(RNG.random(DIM).astype(np.float32), top_k=3)
        assert len(results) == 3

    def test_ivf_index(self) -> None:
        idx = FAISSVectorIndex(dimension=DIM, index_type="ivf", nlist=3)
        vecs = RNG.random((100, DIM)).astype(np.float32)
        idx.build(vecs, [f"r-{i}" for i in range(100)])
        assert idx.size == 100
        results = idx.search(RNG.random(DIM).astype(np.float32), top_k=5)
        assert len(results) == 5

    def test_search_score_range_cosine(self, built_index) -> None:
        q = RNG.random(DIM).astype(np.float32)
        for h in built_index.search(q, top_k=5):
            assert 0.0 <= h.score <= 1.0

    def test_search_after_remove_add(self, built_index) -> None:
        built_index.remove(["repo-0", "repo-1"])
        built_index.add(RNG.random((2, DIM)).astype(np.float32), ["new-0", "new-1"])
        assert built_index.size == 20

    def test_search_returns_hash_ids(self, built_index) -> None:
        q = RNG.random(DIM).astype(np.float32)
        for h in built_index.search(q, top_k=5):
            int(h.repo_id)


# ===================================================================
#  SECTION 2 — IndexMetadataStore
# ===================================================================


class TestIndexMetadataStore:
    def test_add_and_retrieve(self, metadata_store) -> None:
        metadata_store.add_mapping(vector_id=42, repo_id="repo-a", metadata={"name": "A"})
        assert metadata_store.get_repo_id(42) == "repo-a"
        assert metadata_store.get_vector_id("repo-a") == 42

    def test_get_metadata(self, metadata_store) -> None:
        metadata_store.add_mapping(1, "repo-b", {"name": "Beta", "stars": 100})
        assert metadata_store.get_metadata("repo-b") == {"name": "Beta", "stars": 100}

    def test_repo_exists(self, metadata_store) -> None:
        metadata_store.add_mapping(2, "repo-c")
        assert metadata_store.repo_exists("repo-c") is True
        assert metadata_store.repo_exists("none") is False

    def test_remove_mapping(self, metadata_store) -> None:
        metadata_store.add_mapping(3, "repo-d")
        metadata_store.add_mapping(4, "repo-e")
        assert metadata_store.remove("repo-d") == 3
        assert metadata_store.repo_exists("repo-d") is False
        assert metadata_store.size() == 1

    def test_remove_nonexistent(self, metadata_store) -> None:
        assert metadata_store.remove("ghost") is None

    def test_clear(self, metadata_store) -> None:
        for i in range(10):
            metadata_store.add_mapping(i, f"repo-{i}")
        metadata_store.clear()
        assert metadata_store.size() == 0

    def test_items(self, metadata_store) -> None:
        metadata_store.add_mapping(0, "r1", {"x": 1})
        metadata_store.add_mapping(1, "r2", {"y": 2})
        items = metadata_store.items()
        assert len(items) == 2
        assert (0, "r1", {"x": 1}) in items
        assert (1, "r2", {"y": 2}) in items

    def test_empty_store(self, metadata_store) -> None:
        assert metadata_store.size() == 0
        assert metadata_store.items() == []

    def test_add_without_metadata(self, metadata_store) -> None:
        metadata_store.add_mapping(5, "no-meta")
        assert metadata_store.get_metadata("no-meta") is None

    def test_metadata_isolation(self, metadata_store) -> None:
        metadata_store.add_mapping(0, "r1", {"a": 1})
        metadata_store.add_mapping(1, "r2", {"b": 2})
        assert "b" not in metadata_store.get_metadata("r1")


# ===================================================================
#  SECTION 3 — SemanticSearchEngine
# ===================================================================


class TestSemanticSearchEngine:
    @pytest.fixture
    def engine(self, built_index, metadata_store) -> SemanticSearchEngine:
        eng = SemanticSearchEngine(
            vector_index=built_index,
            metadata_store=metadata_store,
            encoder=dummy_encoder,
            batch_encoder=dummy_batch_encoder,
        )
        for i in range(20):
            rid = f"repo-{i}"
            eng._metadata_store.add_mapping(
                vector_id=FAISSVectorIndex.hash_id(rid),
                repo_id=rid,
                metadata={"name": f"Repo-{i}"},
            )
        return eng

    def test_search_returns_result(self, engine) -> None:
        assert isinstance(engine.search("test"), SearchResult)

    def test_search_default_top_k(self, engine) -> None:
        assert len(engine.search("test").results) <= 10

    def test_search_custom_top_k(self, engine) -> None:
        assert len(engine.search("test", top_k=3).results) <= 3

    def test_search_results_have_metadata(self, engine) -> None:
        for hit in engine.search("test", top_k=5).results:
            assert hit.repo_id is not None
            assert isinstance(hit.score, float)

    def test_search_empty_query(self, engine) -> None:
        result = engine.search("")
        assert result.total_count == 0

    def test_search_whitespace_query(self, engine) -> None:
        assert engine.search("   ").total_count == 0

    def test_search_by_vector(self, engine) -> None:
        result = engine.search_by_vector(RNG.random(DIM).astype(np.float32), top_k=4)
        assert len(result.results) <= 4

    def test_search_by_vector_threshold(self, engine) -> None:
        all_r = engine.search_by_vector(np.ones(DIM, dtype=np.float32), top_k=20, threshold=0.0)
        high_r = engine.search_by_vector(np.ones(DIM, dtype=np.float32), top_k=20, threshold=0.5)
        assert len(high_r.results) <= len(all_r.results)

    def test_batch_search(self, engine) -> None:
        results = engine.batch_search(["q1", "q2"], top_k=3)
        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)

    def test_batch_search_empty(self, engine) -> None:
        assert engine.batch_search([]) == []

    def test_build_index_from_repos(self, faiss_index, metadata_store) -> None:
        engine = SemanticSearchEngine(
            faiss_index, metadata_store,
            encoder=dummy_encoder, batch_encoder=dummy_batch_encoder,
        )
        repos = [
            {"repo_id": "a", "text": "alpha", "metadata": {"name": "Alpha"}},
            {"repo_id": "b", "text": "beta", "metadata": {"name": "Beta"}},
        ]
        stats = engine.build_index(repos)
        assert stats.total_vectors == 2
        assert engine._metadata_store.repo_exists("a")
        assert engine._metadata_store.repo_exists("b")

    def test_build_index_empty_repos(self, faiss_index, metadata_store) -> None:
        engine = SemanticSearchEngine(faiss_index, metadata_store, encoder=dummy_encoder)
        stats = engine.build_index([])
        assert stats.total_vectors == 0

    def test_build_index_from_embeddings(self, faiss_index, metadata_store) -> None:
        engine = SemanticSearchEngine(faiss_index, metadata_store)
        vecs = RNG.random((3, DIM)).astype(np.float32)
        stats = engine.build_index_from_embeddings(
            vecs, ["e1", "e2", "e3"],
            [{"n": "A"}, {"n": "B"}, {"n": "C"}],
        )
        assert stats.total_vectors == 3
        assert engine._metadata_store.get_metadata("e1") == {"n": "A"}
        assert engine._metadata_store.get_vector_id("e1") == FAISSVectorIndex.hash_id("e1")

    def test_add_repositories(self, engine) -> None:
        engine.add_repositories(
            [{"repo_id": "new-repo", "text": "new",
              "metadata": {"name": "New"}}],
        )
        assert engine._metadata_store.repo_exists("new-repo")

    def test_add_embeddings(self, engine) -> None:
        vecs = RNG.random((2, DIM)).astype(np.float32)
        engine.add_embeddings(vecs, ["add-a", "add-b"], [{"x": 1}, {"x": 2}])
        assert engine._metadata_store.repo_exists("add-a")
        assert engine._metadata_store.repo_exists("add-b")

    def test_remove_repository(self, engine) -> None:
        engine._metadata_store.add_mapping(FAISSVectorIndex.hash_id("to-remove"), "to-remove")
        r = np.zeros((1, DIM), dtype=np.float32)
        engine._vector_index.add(r, ["to-remove"])
        assert engine.remove_repository("to-remove") is True
        assert engine._metadata_store.repo_exists("to-remove") is False

    def test_remove_nonexistent(self, engine) -> None:
        assert engine.remove_repository("ghost") is False

    def test_clear(self, engine) -> None:
        engine.clear()
        assert engine._vector_index.size == 0
        assert engine._metadata_store.size() == 0

    def test_get_index_stats(self, engine) -> None:
        stats = engine.get_index_stats()
        assert stats.total_vectors == 20
        assert stats.dimension == DIM

    def test_get_index_stats_empty(self, faiss_index, metadata_store) -> None:
        stats = SemanticSearchEngine(faiss_index, metadata_store).get_index_stats()
        assert stats.total_vectors == 0

    def test_set_encoder(self, engine) -> None:
        engine.set_encoder(lambda t: np.zeros(DIM, dtype=np.float32))
        result = engine.search("anything")
        assert isinstance(result, SearchResult)

    def test_no_encoder_returns_empty(self, faiss_index, metadata_store) -> None:
        result = SemanticSearchEngine(faiss_index, metadata_store).search("test")
        assert result.total_count == 0

    def test_search_time_positive(self, engine) -> None:
        assert engine.search("test query", top_k=3).search_time_ms > 0

    def test_threshold_filters(self, engine) -> None:
        no_thr = engine.search("test", top_k=20, threshold=0.0)
        high = engine.search("test", top_k=20, threshold=0.99)
        assert len(high.results) <= len(no_thr.results)

    def test_save_and_load(self, built_index) -> None:
        store = IndexMetadataStore()
        engine = SemanticSearchEngine(built_index, store, encoder=dummy_encoder)
        for i in range(20):
            store.add_mapping(FAISSVectorIndex.hash_id(f"repo-{i}"), f"repo-{i}")

        with tempfile.NamedTemporaryFile(suffix=".faiss", delete=False) as f:
            path = f.name
        try:
            engine.save(path)
            engine2 = SemanticSearchEngine(
                FAISSVectorIndex(dimension=DIM), IndexMetadataStore(), encoder=dummy_encoder
            )
            engine2.load(path)
            assert engine2._vector_index.size == 20
            assert engine2._vector_index.dim == DIM
            assert engine2._metadata_store.size() == 20
            repo_0_hash = FAISSVectorIndex.hash_id("repo-0")
            assert engine2._metadata_store.get_repo_id(repo_0_hash) == "repo-0"
        finally:

            if os.path.exists(path):
                os.remove(path)
            if os.path.exists(path + ".json"):
                os.remove(path + ".json")



# ===================================================================
#  SECTION 4 — Integration
# ===================================================================


class TestIntegration:
    def test_full_pipeline(self) -> None:
        index = FAISSVectorIndex(dimension=DIM)
        store = IndexMetadataStore()
        engine = SemanticSearchEngine(
            index, store,
            encoder=dummy_encoder, batch_encoder=dummy_batch_encoder,
        )
        repos = [
            {"repo_id": "r1", "text": "gpu machine learning framework",
             "metadata": {"name": "TensorFlow"}},
            {"repo_id": "r2", "text": "web api framework", "metadata": {"name": "FastAPI"}},
            {"repo_id": "r3", "text": "gpu compute library", "metadata": {"name": "CUDA"}},
        ]
        stats = engine.build_index(repos)
        assert stats.total_vectors == 3
        result = engine.search("machine learning", top_k=3)
        assert result.total_count <= 3
        assert all(h.repo_id in ("r1", "r2", "r3") for h in result.results)
        engine.add_repositories(
            [{"repo_id": "r4", "text": "image processing",
              "metadata": {"name": "OpenCV"}}],
        )
        assert engine._vector_index.size == 4
        engine.remove_repository("r2")
        assert engine._metadata_store.repo_exists("r2") is False
        assert engine.get_index_stats().total_vectors == 3

    def test_exact_match_boost(self) -> None:
        index = FAISSVectorIndex(dimension=DIM)
        store = IndexMetadataStore()
        engine = SemanticSearchEngine(
            index, store,
            encoder=dummy_encoder, boost_factor=2.0,
        )
        repos = [
            {"repo_id": "pytorch", "text": "deep learning framework",
             "metadata": {"name": "PyTorch"}},
            {"repo_id": "tensorflow", "text": "machine learning platform",
             "metadata": {"name": "TensorFlow"}},
            {"repo_id": "jax", "text": "ml library", "metadata": {"name": "JAX"}},
        ]
        engine.build_index(repos)
        boosted = engine.search("pytorch", top_k=3, boost_exact_match=True)
        plain = engine.search("pytorch", top_k=3, boost_exact_match=False)
        b = next((h for h in boosted.results if h.repo_id == "pytorch"), None)
        p = next((h for h in plain.results if h.repo_id == "pytorch"), None)
        if b and p:
            assert b.score >= p.score

    def test_large_collection(self) -> None:
        index = FAISSVectorIndex(dimension=DIM)
        store = IndexMetadataStore()
        engine = SemanticSearchEngine(index, store, encoder=dummy_encoder)
        repos = [
            {"repo_id": f"r-{i}", "text": f"content {i}",
             "metadata": {"name": f"Repo {i}"}}
            for i in range(200)
        ]
        engine.build_index(repos)
        assert engine._vector_index.size == 200
        result = engine.search("test", top_k=10)
        assert len(result.results) == 10

    def test_vector_count_preserved_across_save(self) -> None:
        """FAISS save/load preserves vector count and metadata is persisted."""
        index = FAISSVectorIndex(dimension=DIM)
        store = IndexMetadataStore()
        engine = SemanticSearchEngine(index, store, encoder=dummy_encoder)
        engine.build_index([
            {"repo_id": "s1", "text": "save me", "metadata": {"name": "SaveTest"}},
            {"repo_id": "s2", "text": "keep me", "metadata": {"name": "KeepTest"}},
        ])
        with tempfile.NamedTemporaryFile(suffix=".faiss", delete=False) as f:
            path = f.name
        try:
            engine.save(path)
            engine2 = SemanticSearchEngine(
                FAISSVectorIndex(DIM), IndexMetadataStore(), encoder=None,
            )
            engine2.load(path)
            assert engine2._vector_index.size == 2
            assert engine2._vector_index.dim == DIM
            assert engine2._metadata_store.get_metadata("s1") == {"name": "SaveTest"}
        finally:
            if os.path.exists(path):
                os.remove(path)
            if os.path.exists(path + ".json"):
                os.remove(path + ".json")


    def test_empty_index_search(self) -> None:
        engine = SemanticSearchEngine(
            FAISSVectorIndex(DIM), IndexMetadataStore(),
            encoder=dummy_encoder,
        )
        result = engine.search("anything")
        assert result.total_count == 0

    def test_rebuild_replaces(self) -> None:
        index = FAISSVectorIndex(dimension=DIM)
        store = IndexMetadataStore()
        engine = SemanticSearchEngine(
            index, store,
            encoder=dummy_encoder, batch_encoder=dummy_batch_encoder,
        )
        engine.build_index([{"repo_id": "old", "text": "old", "metadata": {}}])
        stats = engine.build_index([
            {"repo_id": "new-a", "text": "new a", "metadata": {}},
            {"repo_id": "new-b", "text": "new b", "metadata": {}},
        ])
        assert stats.total_vectors == 2
        assert engine._metadata_store.repo_exists("old") is False
        assert engine._metadata_store.repo_exists("new-a")

    def test_batch_search_multiple(self) -> None:
        index = FAISSVectorIndex(DIM)
        store = IndexMetadataStore()
        engine = SemanticSearchEngine(
            index, store,
            encoder=dummy_encoder, batch_encoder=dummy_batch_encoder,
        )
        engine.build_index([
            {"repo_id": f"r{i}", "text": f"content {i}", "metadata": {}}
            for i in range(10)
        ])
        results = engine.batch_search(["q1", "q2", "q3"], top_k=5, threshold=0.0)
        assert len(results) == 3


# ===================================================================
#  SECTION 5 — Error & Edge Cases
# ===================================================================


class TestEdgeCases:
    def test_build_mismatched_lengths(self, faiss_index, metadata_store) -> None:
        engine = SemanticSearchEngine(faiss_index, metadata_store)
        with pytest.raises(ValueError):
            engine.build_index_from_embeddings(
                RNG.random((3, DIM)).astype(np.float32), ["only-one-id"],
            )

    def test_add_embeddings_mismatched_lengths(self) -> None:
        se = SemanticSearchEngine(
            FAISSVectorIndex(DIM), IndexMetadataStore(),
            encoder=dummy_encoder,
        )
        with pytest.raises(ValueError):
            se.add_embeddings(RNG.random((3, DIM)).astype(np.float32), ["too-few"])

    def test_unknown_index_type(self) -> None:
        idx = FAISSVectorIndex(dimension=DIM, index_type="unknown")
        with pytest.raises(ValueError):
            idx.build(RNG.random((5, DIM)).astype(np.float32), ["a", "b", "c", "d", "e"])

    def test_unknown_metric(self) -> None:
        idx = FAISSVectorIndex(dimension=DIM, metric="manhattan")
        with pytest.raises(ValueError):
            idx.build(RNG.random((5, DIM)).astype(np.float32), ["a", "b", "c"])

    def test_build_no_encoder_raises(self, faiss_index, metadata_store) -> None:
        engine = SemanticSearchEngine(faiss_index, metadata_store)
        with pytest.raises(ValueError):
            engine.build_index([{"repo_id": "x", "text": "y"}])

    def test_add_no_encoder_raises(self, faiss_index, metadata_store) -> None:
        engine = SemanticSearchEngine(faiss_index, metadata_store)
        with pytest.raises(ValueError):
            engine.add_repositories([{"repo_id": "x", "text": "y"}])
