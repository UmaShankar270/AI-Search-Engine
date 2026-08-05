from abc import ABC, abstractmethod
from typing import Any

from ai.query_processor.models import (
    ExtractionContext,
    ExtractionResult,
    IntentType,
    QueryUnderstandingResult,
)


class IQueryUnderstandingEngine(ABC):

    @abstractmethod
    def understand(self, query: str) -> QueryUnderstandingResult:
        pass


class ISpellingCorrector(ABC):

    @abstractmethod
    def correct(self, text: str, known_terms: set[str]) -> tuple[str, list[dict[str, Any]]]:
        pass


class ISynonymResolver(ABC):

    @abstractmethod
    def resolve(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        pass


class IExtractor(ABC):

    @abstractmethod
    def extract(self, context: ExtractionContext) -> ExtractionResult:
        pass


class IIntentExtractor(IExtractor):

    @abstractmethod
    def extract_intent(self, context: ExtractionContext) -> tuple[IntentType, float]:
        pass
