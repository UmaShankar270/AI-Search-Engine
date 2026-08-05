import re

from ai.query_processor.entity_registry import EntityRegistry
from ai.query_processor.interfaces import IExtractor
from ai.query_processor.models import (
    EntityType,
    ExtractedEntity,
    ExtractionContext,
    ExtractionResult,
)


class DomainExtractor(IExtractor):

    def __init__(self) -> None:
        self.registry = EntityRegistry()

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        entities = []
        query_text = f"{context.normalized_query} {context.expanded_query}"
        query_lower = query_text.lower()
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", query_lower)

        trigrams = self._ngrams(words, 3)
        bigrams = self._ngrams(words, 2)

        matched_domains = set()

        for ngram in trigrams + bigrams:
            domain = self.registry.resolve_category(ngram)
            if domain:
                matched_domains.add(domain)
                score = 0.8 if " " in ngram else 0.6
                entities.append(ExtractedEntity(
                    text=ngram,
                    entity_type=EntityType.DOMAIN,
                    confidence=score,
                    source="rule_based",
                    normalized=domain,
                ))

        for word in words:
            if word in matched_domains:
                continue
            domain = self.registry.resolve_category(word)
            if domain:
                matched_domains.add(domain)
                entities.append(ExtractedEntity(
                    text=word,
                    entity_type=EntityType.DOMAIN,
                    confidence=0.5,
                    source="rule_based",
                    normalized=domain,
                ))

        return ExtractionResult(
            entities=entities,
            confidence=max((e.confidence for e in entities), default=0.0),
        )

    def _ngrams(self, words: list[str], n: int) -> list[str]:
        return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]
