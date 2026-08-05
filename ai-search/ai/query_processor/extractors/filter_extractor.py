import re

from ai.query_processor.interfaces import IExtractor
from ai.query_processor.models import (
    EntityType,
    ExtractedEntity,
    ExtractionContext,
    ExtractionResult,
    Filter,
    FilterType,
)


class FilterExtractor(IExtractor):

    def __init__(self) -> None:
        self._filter_patterns: list[tuple[FilterType, list[str], str]] = [
            (
                FilterType.COST,
                [r'\bfree\b', r'\bopen\s*source\b', r'\bfreeware\b', r'\bgratis\b'],
                "free",
            ),
            (
                FilterType.COST,
                [r'\bpaid\b', r'\bcommercial\b', r'\bpremium\b', r'\benterprise\b'],
                "paid",
            ),
            (FilterType.LICENSE, [r'\bmit\b', r'\bmit\s+license\b'], "MIT"),
            (FilterType.LICENSE, [r'\bgpl\b', r'\bgplv\d\b', r'\bgnu\b'], "GPL"),
            (
                FilterType.LICENSE,
                [r'\bapache\b', r'\bapache\s+2\.0\b', r'\bapache\s+license\b'],
                "Apache-2.0",
            ),
            (FilterType.LICENSE, [r'\bb\s?sd\b', r'\bbSD\b', r'\bbSD\s+license\b'], "BSD"),
            (
                FilterType.PLATFORM,
                [r'\bcross\s*platform\b', r'\bmulti\s*platform\b'],
                "cross-platform",
            ),
            (FilterType.PLATFORM, [r'\bmobile\b', r'\bphone\b', r'\bsmartphone\b'], "mobile"),
            (FilterType.PLATFORM, [r'\bweb\b', r'\bbrowser\b', r'\bonline\b'], "web"),
            (FilterType.PLATFORM, [r'\bdesktop\b', r'\bpc\b', r'\blaptop\b'], "desktop"),
            (FilterType.PLATFORM, [r'\bcli\b', r'\bcommand\s+line\b', r'\bterminal\b'], "cli"),
            (FilterType.LANGUAGE, [r'\bwritten\s+in\b', r'\bbuilt\s+with\b'], "language_filter"),
            (
                FilterType.POPULARITY,
                [r'\bpopular\b', r'\bmost\s+starred\b', r'\bhighly\s+rated\b'],
                "popular",
            ),
            (
                FilterType.MAINTAINED,
                [r'\bactive\b', r'\bmaintained\b', r'\bactively\s+maintained\b'],
                "active",
            ),
            (FilterType.MAINTAINED, [r'\bnew\b', r'\brecent\b', r'\bupdated\b'], "recent"),
            (FilterType.FEATURE, [r'\breal.?time\b', r'\blive\b'], "real-time"),
            (FilterType.FEATURE, [r'\boffline\b', r'\bno\s+internet\b'], "offline"),
            (FilterType.FEATURE, [r'\bcloud\b', r'\bsaas\b', r'\bhosted\b'], "cloud"),
            (FilterType.FEATURE, [r'\bself.?hosted\b', r'\bon.?premise\b'], "self-hosted"),
            (FilterType.FEATURE, [r'\bopen\s+source\b', r'\bopen\s*source\b'], "open-source"),
        ]

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        entities = []
        filters: list[Filter] = []
        query_lower = context.normalized_query.lower()

        for filter_type, patterns, value in self._filter_patterns:
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    matched_text = match.group(0).strip()
                    if not any(f.type == filter_type and f.value == value for f in filters):
                        filters.append(Filter(
                            type=filter_type,
                            value=value,
                            original_text=matched_text,
                        ))
                    entities.append(ExtractedEntity(
                        text=matched_text,
                        entity_type=EntityType.FILTER,
                        confidence=0.8,
                        source="rule_based",
                        normalized=f"{filter_type.value}:{value}",
                    ))
                    break

        if self._has_language_filter(query_lower):
            entities.append(ExtractedEntity(
                text="language_filter",
                entity_type=EntityType.FILTER,
                confidence=0.5,
                source="rule_based",
            ))

        confidence = 0.7 if filters else 0.0
        return ExtractionResult(entities=entities, confidence=confidence)

    def _has_language_filter(self, text: str) -> bool:
        patterns = [
            r'\b(in|for|with|using)\s+[a-z]+\b',
        ]
        return any(re.search(p, text) for p in patterns)
