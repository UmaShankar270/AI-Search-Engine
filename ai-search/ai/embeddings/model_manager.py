import logging
import threading
from typing import Any, Optional

import numpy as np

from ai.config.settings import Settings

logger = logging.getLogger(__name__)


class ModelManager:
    _instance: Optional["ModelManager"] = None
    _initialized: bool = False
    _class_lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "ModelManager":
        with cls._class_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None) -> None:
        with self._class_lock:
            if self._initialized:
                return
            self._initialized = True
            self._model_name = model_name or Settings().model_name
            self._device = device or "cpu"
            self._loaded = False
            self._model_lock = threading.RLock()
            self._model: Any = None

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dim(self) -> int:
        with self._model_lock:
            if self._model is None:
                return Settings().embedding_dim
            return self._model.get_sentence_embedding_dimension()

    def load(self) -> None:
        with self._model_lock:
            if self._loaded and self._model is not None:
                return
            try:
                logger.info("Loading model: %s on %s", self._model_name, self._device)
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(
                    self._model_name,
                    device=self._device,
                )
                self._loaded = True
                logger.info("Model loaded. Dim=%d", self.dim)
            except Exception as exc:
                logger.error("Failed to load model '%s': %s", self._model_name, str(exc))
                raise

    def unload(self) -> None:
        with self._model_lock:
            if self._model is not None:
                import gc
                try:
                    import torch
                    if hasattr(self._model, "to"):
                        self._model.to("cpu")
                    del self._model
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except Exception:
                    gc.collect()
                self._model = None
                self._loaded = False
                logger.info("Model unloaded")

    def is_loaded(self) -> bool:
        with self._model_lock:
            return self._loaded and self._model is not None

    def encode(self, texts: list[str]) -> np.ndarray:
        with self._model_lock:
            if not self._loaded or self._model is None:
                self.load()
            model = self._model

        if model is None:
            raise RuntimeError("Model failed to load")

        try:
            embeddings = model.encode(  # type: ignore[attr-defined]
                texts,
                convert_to_numpy=True,
                normalize_embeddings=False,
                show_progress_bar=False,
            )
            return np.array(embeddings, dtype=np.float32)
        except Exception as exc:
            logger.error("Encoding failed: %s", str(exc))
            raise

    def warmup(self) -> None:
        self.encode(["warmup"])
        logger.info("Model warmup complete")

