from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class ComparisonDimension:
    name: str
    scores: dict[str, float]

@dataclass
class ComparisonResult:
    repositories: list[str]
    dimensions: list[ComparisonDimension]
    recommendation: Optional[str] = None
