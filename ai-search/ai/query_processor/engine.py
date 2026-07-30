import re
import time

from ai.query_processor.interfaces import (
    IQueryUnderstandingEngine,
    ISpellingCorrector,
    ISynonymResolver,
    IExtractor,
)
from ai.query_processor.models import (
    QueryUnderstandingResult,
    ExtractionContext,
    ExtractionResult,
    IntentType,
    Technology,
    Filter,
    FilterType,
    TechnologyType,
    EntityType,
)
from ai.query_processor.entity_registry import EntityRegistry
from ai.query_processor.spelling import SpellingCorrector
from ai.query_processor.synonyms import SynonymResolver
from ai.query_processor.extractors.intent_extractor import IntentExtractor
from ai.query_processor.extractors.domain_extractor import DomainExtractor
from ai.query_processor.extractors.technology_extractor import TechnologyExtractor
from ai.query_processor.extractors.filter_extractor import FilterExtractor


class QueryUnderstandingEngine(IQueryUnderstandingEngine):

    def __init__(
        self,
        corrector: ISpellingCorrector | None = None,
        resolver: ISynonymResolver | None = None,
        extractors: list[IExtractor] | None = None,
        llm_extractor: IExtractor | None = None,
        enable_spelling: bool = True,
        enable_synonyms: bool = True,
    ):
        self.registry = EntityRegistry()
        self.corrector = corrector or SpellingCorrector()
        self.resolver = resolver or SynonymResolver()
        self.enable_spelling = enable_spelling
        self.enable_synonyms = enable_synonyms

        self._extractors = extractors or [
            IntentExtractor(),
            DomainExtractor(),
            TechnologyExtractor(),
            FilterExtractor(),
        ]
        self._llm_extractor = llm_extractor

    def understand(self, query: str) -> QueryUnderstandingResult:
        start_time = time.perf_counter()

        if not query or not query.strip():
            return QueryUnderstandingResult(
                original_query=query or "",
                normalized_query="",
                corrected_query="",
                expanded_query="",
                confidence=0.0,
                processing_time_ms=0.0,
            )

        normalized = self._normalize(query)
        tokens = self._tokenize(normalized)

        context = ExtractionContext(
            original_query=query,
            normalized_query=normalized,
            corrected_query=normalized,
            expanded_query=normalized,
            tokens=tokens,
        )

        self._run_spelling(context)
        self._run_synonyms(context)

        all_entities = []
        pipeline_confidence = 0.0
        extractor_count = 0

        for extractor in self._extractors:
            try:
                result = extractor.extract(context)
                all_entities.extend(result.entities)
                pipeline_confidence += result.confidence
                extractor_count += 1
            except Exception:
                pass

        if self._llm_extractor:
            try:
                llm_result = self._llm_extractor.extract(context)
                all_entities.extend(llm_result.entities)
                if llm_result.confidence > 0.5:
                    pipeline_confidence += llm_result.confidence
                    extractor_count += 1
            except Exception:
                pass

        overall_confidence = pipeline_confidence / max(extractor_count, 1)
        result = self._build_result(context, all_entities, overall_confidence)
        result.processing_time_ms = (time.perf_counter() - start_time) * 1000
        return result

    def _normalize(self, query: str) -> str:
        text = query.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s+#./@-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'[a-zA-Z0-9+#.@/-]+', text.lower())

    def _run_spelling(self, context: ExtractionContext):
        if not self.enable_spelling:
            return
        corrected, corrections = self.corrector.correct(
            context.normalized_query,
            self.registry.all_known_terms,
        )
        if corrections:
            context.corrected_query = corrected
            for c in corrections:
                context.extracted_entities.append(
                    self._make_entity(
                        c["original"], EntityType.TECHNOLOGY, 0.6, "spelling", c["corrected"]
                    )
                )
        else:
            context.corrected_query = context.normalized_query

    def _run_synonyms(self, context: ExtractionContext):
        if not self.enable_synonyms:
            context.expanded_query = context.corrected_query
            return
        expanded, changes = self.resolver.resolve(context.corrected_query)
        if changes:
            context.expanded_query = expanded
            for c in changes:
                context.extracted_entities.append(
                    self._make_entity(
                        c["original"], EntityType.TECHNOLOGY, 0.8, c["type"], c["resolved"]
                    )
                )
        else:
            context.expanded_query = context.corrected_query

    def _make_entity(self, text: str, etype: EntityType, confidence: float,
                     source: str, normalized: str | None = None):
        from ai.query_processor.models import ExtractedEntity
        return ExtractedEntity(
            text=text,
            entity_type=etype,
            confidence=confidence,
            source=source,
            normalized=normalized,
        )

    def _build_result(
        self,
        context: ExtractionContext,
        entities: list,
        confidence: float,
    ) -> QueryUnderstandingResult:
        intent = IntentType.UNKNOWN
        domain = None
        technologies = []
        programming_languages = set()
        frameworks = set()
        categories = set()
        libraries = set()
        tools = set()
        databases = set()
        platforms = set()
        filters = []

        for entity in entities:
            etype = entity.entity_type
            text = entity.normalized or entity.text

            if etype == EntityType.CATEGORY:
                if text in (it.value for it in IntentType):
                    try:
                        intent = IntentType(text)
                    except ValueError:
                        pass

            elif etype == EntityType.DOMAIN:
                if domain is None:
                    domain = text
                categories.add(text)

            elif etype == EntityType.PROGRAMMING_LANGUAGE:
                programming_languages.add(text)
                tech = Technology(name=text, type=TechnologyType.LANGUAGE, category="language")
                technologies.append(tech)

            elif etype == EntityType.FRAMEWORK:
                frameworks.add(text)
                tech = Technology(name=text, type=TechnologyType.FRAMEWORK, category="framework")
                technologies.append(tech)

            elif etype == EntityType.LIBRARY:
                libraries.add(text)
                tech = Technology(name=text, type=TechnologyType.LIBRARY, category="library")
                technologies.append(tech)

            elif etype == EntityType.TOOL:
                tools.add(text)
                tech = Technology(name=text, type=TechnologyType.TOOL, category="tool")
                technologies.append(tech)

            elif etype == EntityType.DATABASE:
                databases.add(text)
                tech = Technology(name=text, type=TechnologyType.DATABASE, category="database")
                technologies.append(tech)

            elif etype == EntityType.PLATFORM:
                platforms.add(text)
                tech = Technology(name=text, type=TechnologyType.PLATFORM, category="platform")
                technologies.append(tech)

            elif etype == EntityType.TECHNOLOGY:
                tech = Technology(name=text, type=TechnologyType.TOOL, category="technology")
                technologies.append(tech)

            elif etype == EntityType.FILTER:
                if entity.normalized and ":" in entity.normalized:
                    parts = entity.normalized.split(":", 1)
                    try:
                        ftype = FilterType(parts[0])
                        fvalue = parts[1]
                        if not any(f.type == ftype and f.value == fvalue for f in filters):
                            filters.append(Filter(type=ftype, value=fvalue, original_text=entity.text))
                    except ValueError:
                        pass

        if intent == IntentType.UNKNOWN:
            intent = IntentType.SEARCH
            confidence = max(confidence, 0.4)

        return QueryUnderstandingResult(
            original_query=context.original_query,
            normalized_query=context.normalized_query,
            corrected_query=context.corrected_query,
            expanded_query=context.expanded_query,
            intent=intent,
            domain=domain,
            technologies=technologies,
            programming_languages=sorted(programming_languages),
            frameworks=sorted(frameworks),
            categories=sorted(categories),
            libraries=sorted(libraries),
            tools=sorted(tools),
            databases=sorted(databases),
            platforms=sorted(platforms),
            filters=filters,
            extracted_entities=entities,
            confidence=round(confidence, 4),
        )
