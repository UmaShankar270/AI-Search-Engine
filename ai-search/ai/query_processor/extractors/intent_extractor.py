import re

from ai.query_processor.interfaces import IIntentExtractor
from ai.query_processor.models import (
    EntityType,
    ExtractedEntity,
    ExtractionContext,
    ExtractionResult,
    IntentType,
)


class IntentExtractor(IIntentExtractor):

    def __init__(self) -> None:
        self._patterns = {
            IntentType.COMPARE: [
                r'\bcompare\b', r'\bvs\b', r'\bversus\b',
                r'\bdifference\b', r'\bdiff\b', r'\bwhich\s+(is\s+)?better\b',
                r'\bcompare\s+to\b', r'\bvs\.?\b', r'\bversus\b',
            ],
            IntentType.RECOMMEND: [
                r'\brecommend\b', r'\bbest\b', r'\btop\b',
                r'\bsuggest\b', r'\balternative\b', r'\balternatives\b',
                r'\bwhat\s+(is\s+)?the\s+best\b', r'\bpopular\b',
                r'\bshould\s+(i\s+)?use\b', r'\bpick\b', r'\bchoice\b',
            ],
            IntentType.EXPLORE: [
                r'\bexplore\b', r'\bdiscover\b', r'\bbrowse\b',
                r'\bwhat\s+is\b', r'\bwhat\s+are\b', r'\bshow\s+me\b',
            ],
            IntentType.DISCOVER: [
                r'\btrending\b', r'\bnew\b', r'\bupcoming\b',
                r'\brising\b', r'\bhot\b', r'\brecent\b',
                r'\bmost\s+starred\b', r'\bgrowing\b',
            ],
            IntentType.SEARCH: [
                r'\bfind\b', r'\bsearch\b', r'\blook\s+for\b',
                r'\bneed\b', r'\bwant\b', r'\bi\'?m\s+looking\s+for\b',
                r'^[^?]*\?$',
            ],
        }

    def extract_intent(self, context: ExtractionContext) -> tuple[IntentType, float]:
        query_lower = context.normalized_query.lower()
        scores = {intent: 0.0 for intent in IntentType}

        for intent, patterns in self._patterns.items():
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    match_count += 1
            if match_count > 0:
                scores[intent] = min(0.3 + (match_count * 0.25), 0.95)

        if scores[IntentType.COMPARE] > 0:
            scores[IntentType.SEARCH] *= 0.3

        if scores[IntentType.RECOMMEND] > 0:
            scores[IntentType.SEARCH] *= 0.4

        best_intent = max(scores, key=lambda k: scores[k])
        best_score = scores[best_intent]

        if best_score < 0.2:
            domain_keywords = self._detect_domain_keywords(query_lower)
            if domain_keywords:
                best_intent = IntentType.SEARCH
                best_score = 0.5

        return best_intent, best_score

    def extract(self, context: ExtractionContext) -> ExtractionResult:
        intent, confidence = self.extract_intent(context)
        entity = ExtractedEntity(
            text=intent.value,
            entity_type=EntityType.CATEGORY,
            confidence=confidence,
            source="rule_based",
        )
        return ExtractionResult(entities=[entity], confidence=confidence)

    def _detect_domain_keywords(self, text: str) -> bool:
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        significant = [w for w in words if len(w) > 2]
        return len(significant) >= 2
