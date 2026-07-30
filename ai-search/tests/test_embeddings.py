import numpy as np
import pytest

from ai.embeddings.cache import EmbeddingCache
from ai.embeddings.strategies import CompositionStrategy

# --- CompositionStrategy Tests ---


class TestCompositionStrategy:
    def test_for_query_normalizes(self) -> None:
        result = CompositionStrategy.for_query("  Hello   World  ")
        assert result == "Hello World"

    def test_for_query_empty(self) -> None:
        assert CompositionStrategy.for_query("") == ""

    def test_for_query_truncates(self) -> None:
        long = "x" * 1000
        result = CompositionStrategy.for_query(long)
        assert len(result) <= 512

    def test_for_description_empty(self) -> None:
        assert CompositionStrategy.for_description(None) == ""
        assert CompositionStrategy.for_description("") == ""

    def test_for_description_normalizes(self) -> None:
        result = CompositionStrategy.for_description("  Cool  Project  ")
        assert result == "Cool Project"

    def test_for_readme_strips_markdown(self) -> None:
        readme = "# Title\n\nSome **bold** text and `code`"
        result = CompositionStrategy.for_readme(readme)
        assert "# Title" not in result
        assert "Some" in result
        assert "bold" in result
        assert "text" in result
        assert "code" in result

    def test_for_readme_empty(self) -> None:
        assert CompositionStrategy.for_readme(None) == ""

    def test_for_readme_removes_image_links(self) -> None:
        readme = "![alt](image.png) description"
        result = CompositionStrategy.for_readme(readme)
        assert "image.png" not in result

    def test_for_readme_removes_links(self) -> None:
        readme = "click [here](https://example.com) for info"
        result = CompositionStrategy.for_readme(readme)
        assert "here" in result

    def test_for_topics_empty(self) -> None:
        assert CompositionStrategy.for_topics(None) == ""
        assert CompositionStrategy.for_topics([]) == ""

    def test_for_topics_joins(self) -> None:
        result = CompositionStrategy.for_topics(["python", "ml", "nlp"])
        assert "python" in result
        assert "nlp" in result

    def test_for_tags_delegates(self) -> None:
        result = CompositionStrategy.for_tags(["web", "react"])
        assert "web" in result

    def test_for_repository_composes(self) -> None:
        result = CompositionStrategy.for_repository(
            name="test-repo",
            description="A test repo",
            topics=["python", "cli"],
            language="Python",
        )
        assert "test-repo" in result
        assert "A test repo" in result
        assert "python" in result
        assert "Python" in result

    def test_for_repository_with_readme(self) -> None:
        result = CompositionStrategy.for_repository(
            name="test",
            description="desc",
            readme_text="## Installation\npip install test",
        )
        assert "Installation" in result
        assert "pip install test" in result

    def test_for_repository_empty(self) -> None:
        result = CompositionStrategy.for_repository()
        assert result == ""

    def test_for_metadata_empty(self) -> None:
        assert CompositionStrategy.for_metadata("") == ""

    def test_for_metadata_normalizes(self) -> None:
        result = CompositionStrategy.for_metadata("  spaced   out  text  ")
        assert result == "spaced out text"


# --- EmbeddingCache Tests ---


class TestEmbeddingCache:
    def test_cache_miss(self) -> None:
        cache = EmbeddingCache(max_size=100, ttl_seconds=60)
        result = cache.get("hello world")
        assert result is None

    def test_cache_hit(self) -> None:
        cache = EmbeddingCache(max_size=100, ttl_seconds=60)
        vec = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        cache.set("hello", vec)
        result = cache.get("hello")
        assert result is not None
        assert np.allclose(result, vec)

    def test_cache_expiry(self) -> None:
        cache = EmbeddingCache(max_size=100, ttl_seconds=0)
        vec = np.array([0.1, 0.2], dtype=np.float32)
        cache.set("temp", vec)
        result = cache.get("temp")
        assert result is None

    def test_cache_eviction(self) -> None:
        cache = EmbeddingCache(max_size=2, ttl_seconds=60)
        cache.set("a", np.array([1.0], dtype=np.float32))
        cache.set("b", np.array([2.0], dtype=np.float32))
        cache.set("c", np.array([3.0], dtype=np.float32))
        assert cache.get("a") is None
        assert cache.get("b") is not None
        assert cache.get("c") is not None

    def test_invalidate(self) -> None:
        cache = EmbeddingCache(max_size=100, ttl_seconds=60)
        cache.set("key", np.array([1.0], dtype=np.float32))
        assert cache.invalidate("key") is True
        assert cache.get("key") is None
        assert cache.invalidate("nonexistent") is False

    def test_clear(self) -> None:
        cache = EmbeddingCache(max_size=100, ttl_seconds=60)
        cache.set("a", np.array([1.0], dtype=np.float32))
        cache.set("b", np.array([2.0], dtype=np.float32))
        cache.clear()
        assert cache.size == 0
        assert cache.stats["hits"] == 0

    def test_stats(self) -> None:
        cache = EmbeddingCache(max_size=100, ttl_seconds=60)
        cache.get("miss")
        vec = np.array([1.0], dtype=np.float32)
        cache.set("hit", vec)
        cache.get("hit")
        stats = cache.stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_copy_on_set(self) -> None:
        cache = EmbeddingCache(max_size=100, ttl_seconds=60)
        vec = np.array([1.0, 2.0], dtype=np.float32)
        cache.set("key", vec)
        vec[0] = 99.0
        cached = cache.get("key")
        assert cached is not None
        assert cached[0] == 1.0

    def test_deterministic_key(self) -> None:
        cache = EmbeddingCache()
        vec = np.array([1.0], dtype=np.float32)
        cache.set("same text", vec)
        assert cache.get("same text") is not None
        assert cache.get("SAME TEXT") is None


# --- EmbeddingGenerator Integration Tests ---


def _model_available() -> bool:
    import os
    cache_dir = os.path.expanduser(
        "~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2"
    )
    snapshots_dir = os.path.join(cache_dir, "snapshots")
    if not os.path.isdir(snapshots_dir):
        return False
    for root, _dirs, files in os.walk(snapshots_dir):
        if any(f.endswith(".bin") or f.endswith(".safetensors") for f in files):
            return True
    return False


@pytest.fixture(scope="module")
def generator():
    if not _model_available():
        pytest.skip("Sentence Transformer model not available (check network)")
    from ai.embeddings.generator import EmbeddingGenerator
    gen = EmbeddingGenerator(use_cache=True)
    gen.warmup()
    return gen


class TestEmbeddingGeneratorReal:
    def test_generate_returns_vector(self, generator) -> None:
        vec = generator.generate("hello world")
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (generator.dim,)
        assert vec.dtype == np.float32

    def test_generate_normalized_not_empty(self, generator) -> None:
        vec1 = generator.generate("python framework")
        vec2 = generator.generate("python framework")
        assert np.allclose(vec1, vec2)

    def test_generate_empty_returns_zeros(self, generator) -> None:
        vec = generator.generate("")
        assert np.allclose(vec, np.zeros(generator.dim))

    def test_generate_batch_returns_matrix(self, generator) -> None:
        texts = ["a", "b", "c"]
        vectors = generator.generate_batch(texts)
        assert vectors.shape == (3, generator.dim)

    def test_generate_batch_empty(self, generator) -> None:
        vectors = generator.generate_batch([])
        assert vectors.shape == (0, generator.dim)

    def test_generate_batch_with_empty_texts(self, generator) -> None:
        texts = ["hello", "", "world"]
        vectors = generator.generate_batch(texts)
        assert vectors.shape == (3, generator.dim)
        assert np.allclose(vectors[1], np.zeros(generator.dim))

    def test_generate_for_query(self, generator) -> None:
        vec = generator.generate_for_query("find me a python library")
        assert vec.shape == (generator.dim,)

    def test_generate_for_description(self, generator) -> None:
        vec = generator.generate_for_description("A machine learning framework")
        assert vec.shape == (generator.dim,)

    def test_generate_for_description_none(self, generator) -> None:
        vec = generator.generate_for_description(None)
        assert np.allclose(vec, np.zeros(generator.dim))

    def test_generate_for_readme(self, generator) -> None:
        vec = generator.generate_for_readme("# Install\npip install foo")
        assert vec.shape == (generator.dim,)

    def test_generate_for_readme_none(self, generator) -> None:
        vec = generator.generate_for_readme(None)
        assert np.allclose(vec, np.zeros(generator.dim))

    def test_generate_for_topics(self, generator) -> None:
        vec = generator.generate_for_topics(["python", "machine-learning"])
        assert vec.shape == (generator.dim,)

    def test_generate_for_topics_none(self, generator) -> None:
        vec = generator.generate_for_topics(None)
        assert np.allclose(vec, np.zeros(generator.dim))

    def test_generate_for_tags(self, generator) -> None:
        vec = generator.generate_for_tags(["web", "react"])
        assert vec.shape == (generator.dim,)

    def test_generate_for_repository(self, generator) -> None:
        vec = generator.generate_for_repository(
            name="fastapi",
            description="A modern web framework",
            topics=["python", "api"],
            language="Python",
            readme_text="# FastAPI\nA modern web framework",
        )
        assert vec.shape == (generator.dim,)

    def test_generate_for_repository_partial(self, generator) -> None:
        vec = generator.generate_for_repository(name="test-repo")
        assert vec.shape == (generator.dim,)

    def test_cache_hit_returns_same_vector(self, generator) -> None:
        vec1 = generator.generate("cache test string")
        vec2 = generator.generate("cache test string")
        assert np.allclose(vec1, vec2)

    def test_cache_miss_different_returns_different(self, generator) -> None:
        vec1 = generator.generate("first unique query XKCD")
        vec2 = generator.generate("second unique query XKCD")
        assert not np.allclose(vec1, vec2)

    def test_model_name_property(self, generator) -> None:
        assert generator.model_name is not None

    def test_dim_property(self, generator) -> None:
        dim = generator.dim
        assert dim == 384 or dim > 0

    def test_cache_stats_property(self, generator) -> None:
        stats = generator.cache_stats
        assert "hit_rate" in stats

    def test_clear_cache(self, generator) -> None:
        generator.generate("cache_clear_test")
        generator.clear_cache()
        stats = generator.cache_stats
        assert stats["size"] == 0

    def test_generate_for_metadata(self, generator) -> None:
        vec = generator.generate_for_metadata("name owner stars 100")
        assert vec.shape == (generator.dim,)

    def test_similar_query_embeddings(self, generator) -> None:
        vec_py = generator.generate_for_query("python library")
        vec_js = generator.generate_for_query("javascript library")
        vec_py2 = generator.generate_for_query("python package")
        cos_py = np.dot(vec_py, vec_py2) / (np.linalg.norm(vec_py) * np.linalg.norm(vec_py2))
        cos_diff = np.dot(vec_py, vec_js) / (np.linalg.norm(vec_py) * np.linalg.norm(vec_js))
        assert cos_py > cos_diff


class TestEmbeddingGeneratorUnit:
    def test_with_mock_model(self, mocker) -> None:
        mock_mgr = mocker.patch("ai.embeddings.generator.ModelManager")
        mock_mgr.return_value.dim = 384
        mock_mgr.return_value.encode.return_value = np.array([[0.5] * 384], dtype=np.float32)

        from ai.embeddings.generator import EmbeddingGenerator
        gen = EmbeddingGenerator(use_cache=False)
        vec = gen.generate("test")
        assert vec.shape == (384,)

    def test_batch_with_mock(self, mocker) -> None:
        mock_mgr = mocker.patch("ai.embeddings.generator.ModelManager")
        mock_mgr.return_value.dim = 384
        mock_mgr.return_value.encode.return_value = np.array(
            [[0.1] * 384, [0.2] * 384], dtype=np.float32,
        )

        from ai.embeddings.generator import EmbeddingGenerator
        gen = EmbeddingGenerator(use_cache=False)
        vecs = gen.generate_batch(["a", "b"])
        assert vecs.shape == (2, 384)

    def test_error_handling(self, mocker) -> None:
        mock_mgr = mocker.patch("ai.embeddings.generator.ModelManager")
        mock_mgr.return_value.dim = 384
        mock_mgr.return_value.encode.side_effect = RuntimeError("model error")

        from ai.embeddings.generator import EmbeddingGenerator
        gen = EmbeddingGenerator(use_cache=False)
        with pytest.raises(RuntimeError):
            gen.generate("test")


# --- ModelManager Unit Tests ---


class TestModelManager:
    def test_singleton(self) -> None:
        from ai.embeddings.model_manager import ModelManager
        m1 = ModelManager()
        m2 = ModelManager()
        assert m1 is m2

    def test_dim_before_load(self) -> None:
        from ai.embeddings.model_manager import ModelManager
        mgr = ModelManager.__new__(ModelManager)
        mgr._initialized = False
        mgr.__init__()
        dim = mgr.dim
        assert dim > 0

    def test_is_loaded_false_initially(self) -> None:
        from ai.embeddings.model_manager import ModelManager
        m = ModelManager.__new__(ModelManager)
        m._initialized = False
        m.__init__()
        assert not m.is_loaded()
