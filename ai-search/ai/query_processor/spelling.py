import re
from typing import Any

from ai.query_processor.interfaces import ISpellingCorrector
from ai.utils.text_utils import TextUtils


class SpellingCorrector(ISpellingCorrector):

    def __init__(self, max_distance: int = 2):
        self.max_distance = max_distance

    def correct(self, text: str, known_terms: set[str]) -> tuple[str, list[dict[str, Any]]]:
        if not text:
            return text, []
        words = re.findall(r"[a-zA-Z0-9+#.]+", text)
        corrections = []
        result_words = []
        for word in words:
            lower_word = word.lower()
            if lower_word in known_terms or len(word) <= 2:
                result_words.append(word)
                continue
            suggestion = self._find_closest(lower_word, known_terms)
            if suggestion:
                corrections.append({
                    "original": word,
                    "corrected": suggestion,
                    "confidence": 0.6,
                })
                result_words.append(suggestion)
            else:
                result_words.append(word)
        corrected_text = self._rebuild_text(text, words, result_words)
        return corrected_text, corrections

    def _find_closest(self, word: str, known_terms: set[str]) -> str | None:
        best_match = None
        best_distance = self.max_distance + 1
        for term in known_terms:
            distance = TextUtils.levenshtein_distance(word, term)
            if distance < best_distance:
                best_distance = distance
                best_match = term
        if best_match and best_distance <= self.max_distance:
            if best_distance > 0 and len(word) > 3:
                if word[0] != best_match[0] and best_distance > 1:
                    return None
            return best_match
        return None

    def _rebuild_text(self, original: str, words: list[str], replacements: list[str]) -> str:
        result = original
        for orig, repl in zip(words, replacements):
            if orig.lower() != repl.lower():
                result = re.sub(r'\b' + re.escape(orig) + r'\b', repl, result, count=1)
        return result

