from abc import ABC, abstractmethod
from ai.query_processor.models import (
    QueryUnderstandingResult,
    ExtractionContext,
    ExtractionResult,
    IntentType,
)


class IQueryUnderstandingEngine(ABC):

    @abstractmethod
    def understand(self, query: str) -> QueryUnderstandingResult:
        pass


class ISpellingCorrector(ABC):

    @abstractmethod
    def correct(self, text: str, known_terms: set[str]) -> tuple[str, list[dict]]:
        pass


class ISynonymResolver(ABC):

    @abstractmethod
    def resolve(self, text: str) -> tuple[str, list[dict]]:
        pass


class IExtractor(ABC):

    @abstractmethod
    def extract(self, context: ExtractionContext) -> ExtractionResult:
        pass


class IIntentExtractor(IExtractor):

    @abstractmethod
    def extract_intent(self, context: ExtractionContext) -> tuple[IntentType, float]:
        pass
