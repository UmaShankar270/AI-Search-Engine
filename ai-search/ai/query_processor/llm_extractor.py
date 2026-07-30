from ai.query_processor.interfaces import IExtractor
from ai.query_processor.models import (
    ExtractionContext,
    ExtractionResult,
)


class LLMExtractor(IExtractor):
    """LLM-based query understanding extractor.

    Uses an external LLM to enrich or override rule-based extraction.
    This class is a pluggable strategy — swap the provider without
    changing the pipeline. When the LLM is unavailable, the pipeline
    degrades gracefully (returns empty result, rule-based takes priority).
    """

    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini"):
        self.provider: str | None = provider
        self.model = model
        self._client: str | None = None

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        if not self._is_available():
            return ExtractionResult(entities=[], confidence=0.0)
        try:
            return self._call_llm(context)
        except Exception:
            return ExtractionResult(entities=[], confidence=0.0)

    def _is_available(self) -> bool:
        return False

    def _call_llm(self, context: ExtractionContext) -> ExtractionResult:
        return ExtractionResult(entities=[], confidence=0.0)

    def configure(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        if provider:
            self.provider = provider
        if model:
            self.model = model
        if api_key:
            self._client = api_key
