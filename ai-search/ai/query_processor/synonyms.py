import re
from typing import Any

from ai.query_processor.entity_registry import EntityRegistry
from ai.query_processor.interfaces import ISynonymResolver


class SynonymResolver(ISynonymResolver):

    def __init__(self) -> None:
        self.registry = EntityRegistry()

    def resolve(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        if not text:
            return text, []
        resolved = []
        changes = []
        words = re.findall(r"[a-zA-Z0-9+#.]+", text)
        for word in words:
            lower = word.lower()
            expanded = self.registry.resolve_synonym(lower)
            if expanded:
                changes.append({
                    "original": word,
                    "resolved": expanded,
                    "type": "synonym",
                })
                resolved.append(expanded)
            else:
                expanded_abbr = self.registry.resolve_abbreviation(lower)
                if expanded_abbr:
                    changes.append({
                        "original": word,
                        "resolved": expanded_abbr,
                        "type": "abbreviation",
                    })
                    resolved.append(expanded_abbr)
                else:
                    resolved.append(word)
        expanded_text = " ".join(resolved)
        return expanded_text, changes
