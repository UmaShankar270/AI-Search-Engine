from __future__ import annotations

import copy
import json
import logging
from pathlib import Path
from typing import Any, Optional

from .defaults import DEFAULT_RANKING_CONFIG
from .normalization import NormalizationEngine

logger = logging.getLogger(__name__)


class WeightManager:
    def __init__(self, config_path: Optional[str] = None):
        self._normalization = NormalizationEngine()
        self._config: dict[str, Any] = copy.deepcopy(DEFAULT_RANKING_CONFIG)
        self._config_path = config_path

        if config_path:
            self.load(config_path)

    def load(self, path: str) -> None:
        p = Path(path)
        if not p.exists():
            logger.warning("Config file not found: %s, using defaults", path)
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "weights" in data:
                self._config["weights"].update(data["weights"])
            if "normalization" in data:
                self._config["normalization"].update(data["normalization"])
            if "version" in data:
                self._config["version"] = data["version"]
            logger.info("Loaded ranking config from %s", path)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load config %s: %s", path, str(e))

    def save(self, path: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2)
        logger.info("Saved ranking config to %s", path)

    def get_weight(self, factor_name: str) -> float:
        weights: dict[str, float] = self._config["weights"]
        return weights.get(factor_name, 0.0)

    def set_weight(self, factor_name: str, weight: float) -> None:
        self._config["weights"][factor_name] = max(0.0, weight)

    def get_normalization_params(self, factor_name: str) -> dict[str, Any]:
        normalization: dict[str, dict[str, Any]] = self._config["normalization"]
        return normalization.get(factor_name, {"method": "identity"})

    def normalize(self, factor_name: str, raw_value: float) -> float:
        params = self.get_normalization_params(factor_name)
        return self._normalization.normalize(raw_value, params.get("method", "identity"), params)

    @property
    def weights(self) -> dict[str, float]:
        return dict(self._config["weights"])

    @property
    def factor_names(self) -> list[str]:
        return list(self._config["weights"].keys())

    @property
    def config(self) -> dict[str, Any]:
        return dict(self._config)
