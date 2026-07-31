import threading
import time
from unittest.mock import patch, MagicMock
import pytest

from ai.embeddings.model_manager import ModelManager
from ai.semantic_search.metadata_store import IndexMetadataStore


@patch("sentence_transformers.SentenceTransformer")
def test_model_manager_concurrency(mock_transformer_class: MagicMock) -> None:
    """Stress test ModelManager singleton loading/unloading/encoding concurrently."""
    mock_model = MagicMock()
    mock_model.get_sentence_embedding_dimension.return_value = 384
    mock_model.encode.return_value = [[0.1] * 384]
    mock_transformer_class.return_value = mock_model

    # Use the singleton instance
    manager = ModelManager()

    errors = []

    def worker(worker_id: int) -> None:
        try:
            for _ in range(20):
                # Concurrently load
                manager.load()
                assert manager.is_loaded()

                # Concurrently check dim
                assert manager.dim == 384

                # Concurrently encode
                emb = manager.encode(["hello world"])
                assert emb.shape == (1, 384)

                # Concurrently unload (some workers unload, some load)
                if worker_id % 2 == 0:
                    manager.unload()

                time.sleep(0.001)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Ensure no exceptions were raised
    assert not errors, f"Concurrency errors in ModelManager: {errors}"


def test_metadata_store_concurrency() -> None:
    """Stress test IndexMetadataStore to ensure no dict mutation race conditions occur."""
    store = IndexMetadataStore()
    errors = []

    # Pre-populate some values
    for i in range(50):
        store.add_mapping(i, f"repo-{i}", {"stars": i})

    def writer_worker() -> None:
        try:
            for i in range(50, 100):
                store.add_mapping(i, f"repo-{i}", {"stars": i})
                store.remove(f"repo-{i-20}")
                time.sleep(0.001)
        except Exception as e:
            errors.append(e)

    def reader_worker() -> None:
        try:
            for _ in range(100):
                # Concurrently iterate over items (causes RuntimeError if not locked)
                items = store.items()
                assert len(items) >= 0

                # Concurrently lookup
                for i in range(100):
                    store.get_repo_id(i)
                    store.get_vector_id(f"repo-{i}")
                    store.get_metadata(f"repo-{i}")
                    store.repo_exists(f"repo-{i}")
                    store.size()

                time.sleep(0.001)
        except Exception as e:
            errors.append(e)

    threads = []
    # 5 writers and 5 readers
    for i in range(5):
        threads.append(threading.Thread(target=writer_worker))
        threads.append(threading.Thread(target=reader_worker))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Ensure no exceptions were raised
    assert not errors, f"Concurrency errors in IndexMetadataStore: {errors}"
