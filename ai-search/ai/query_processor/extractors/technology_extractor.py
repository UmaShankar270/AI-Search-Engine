from ai.query_processor.interfaces import IExtractor
from ai.query_processor.models import (
    ExtractionContext, ExtractionResult,
    ExtractedEntity, EntityType, Technology, TechnologyType,
)
from ai.query_processor.entity_registry import EntityRegistry


class TechnologyExtractor(IExtractor):

    def __init__(self):
        self.registry = EntityRegistry()

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        entities = []
        query_text = f"{context.normalized_query} {context.expanded_query}".lower()
        results = self.registry.search_entities(query_text)

        seen = set()
        for key, tech, score in results:
            if tech.name in seen:
                continue
            seen.add(tech.name)
            entity_type = self._map_entity_type(tech.type)
            entities.append(ExtractedEntity(
                text=tech.name,
                entity_type=entity_type,
                confidence=score,
                source="rule_based",
                normalized=tech.name,
            ))

        return ExtractionResult(
            entities=entities,
            confidence=max((e.confidence for e in entities), default=0.0),
        )

    def _map_entity_type(self, tech_type: TechnologyType) -> EntityType:
        mapping = {
            TechnologyType.LANGUAGE: EntityType.PROGRAMMING_LANGUAGE,
            TechnologyType.FRAMEWORK: EntityType.FRAMEWORK,
            TechnologyType.LIBRARY: EntityType.LIBRARY,
            TechnologyType.TOOL: EntityType.TOOL,
            TechnologyType.DATABASE: EntityType.DATABASE,
            TechnologyType.PLATFORM: EntityType.PLATFORM,
            TechnologyType.RUNTIME: EntityType.TECHNOLOGY,
        }
        return mapping.get(tech_type, EntityType.TECHNOLOGY)
