from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class NormalizationEngine:
    EPS = 1e-12

    def normalize(
        self, value: object, method: str, params: Optional[dict[str, Any]] = None
    ) -> float:
        params = params or {}
        if value is None:
            return 0.0

        if method == "boolean":
            return self._boolean(value, params)

        try:
            numeric_val = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 0.0

        if isinstance(numeric_val, float) and np.isnan(numeric_val):
            return 0.0

        method_map = {
            "identity": self._identity,
            "log_scale": self._log_scale,
            "sigmoid": self._sigmoid,
            "exp_decay": self._exp_decay,
            "boolean": self._boolean,
            "min_max": self._min_max,
        }

        normalizer = method_map.get(method)
        if normalizer is None:
            logger.warning("Unknown normalization method '%s', using identity", method)
            return self._identity(numeric_val, params)

        return normalizer(numeric_val, params)

    def _identity(self, value: float, params: dict[str, Any]) -> float:
        max_val = float(params.get("max_value", 1.0))
        if max_val <= 0:
            return 0.0
        return max(0.0, min(1.0, value / max_val))

    def _log_scale(self, value: float, params: dict[str, Any]) -> float:
        max_val = float(params.get("max_value", 100000.0))
        cap = float(params.get("cap", max_val))
        if max_val <= 1:
            return 0.0
        capped = min(value, cap)
        return float(min(1.0, np.log1p(capped) / np.log1p(max_val)))

    def _sigmoid(self, value: float, params: dict[str, Any]) -> float:
        midpoint = float(params.get("midpoint", 50.0))
        k = float(params.get("k", 0.1))
        return float(1.0 / (1.0 + np.exp(-k * (value - midpoint))))

    def _exp_decay(self, value: float, params: dict[str, Any]) -> float:
        decay_lambda = float(params.get("lambda", 0.02))
        max_days = float(params.get("max_days", 365.0))
        if value < 0:
            return 1.0
        clamped = min(value, max_days)
        return float(np.exp(-decay_lambda * clamped))

    def _boolean(self, value: object, params: dict[str, Any]) -> float:
        if isinstance(value, str):
            return 1.0 if value.lower() in ("yes", "true", "1") else 0.0
        return 1.0 if bool(value) else 0.0

    def _min_max(self, value: float, params: dict[str, Any]) -> float:
        min_val = float(params.get("min_value", 0.0))
        max_val = float(params.get("max_value", 1.0))
        if max_val <= min_val:
            return 0.0
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
