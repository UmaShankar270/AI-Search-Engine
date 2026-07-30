import re
from typing import Optional


class CompositionStrategy:
    MAX_README_CHARS = 2048
    MAX_DESC_CHARS = 512
    MAX_QUERY_CHARS = 512
    MAX_TOPIC_CHARS = 256

    @staticmethod
    def for_query(query: str) -> str:
        if not query:
            return ""
        cleaned = query.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned[:CompositionStrategy.MAX_QUERY_CHARS]

    @staticmethod
    def for_description(description: Optional[str]) -> str:
        if not description:
            return ""
        cleaned = description.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned[:CompositionStrategy.MAX_DESC_CHARS]

    @staticmethod
    def for_readme(readme_text: Optional[str]) -> str:
        if not readme_text:
            return ""
        text = re.sub(r"!\[.*?\]\(.*?\)", "", readme_text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"#{1,6}\s+", "", text)
        text = re.sub(r"[*_~`]", "", text)
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
        return text[:CompositionStrategy.MAX_README_CHARS]

    @staticmethod
    def for_topics(topics: Optional[list[str]]) -> str:
        if not topics:
            return ""
        joined = ", ".join(t for t in topics if t)
        return joined[:CompositionStrategy.MAX_TOPIC_CHARS]

    @staticmethod
    def for_tags(tags: Optional[list[str]]) -> str:
        return CompositionStrategy.for_topics(tags)

    @staticmethod
    def for_repository(
        name: Optional[str] = None,
        description: Optional[str] = None,
        topics: Optional[list[str]] = None,
        language: Optional[str] = None,
        readme_text: Optional[str] = None,
    ) -> str:
        parts = []
        if name:
            parts.append(f"Repository: {name}")
        if description:
            parts.append(f"Description: {CompositionStrategy.for_description(description)}")
        if topics:
            parts.append(f"Topics: {CompositionStrategy.for_topics(topics)}")
        if language:
            parts.append(f"Language: {language}")
        if readme_text:
            readme_clean = CompositionStrategy.for_readme(readme_text)
            if readme_clean:
                parts.append(f"README: {readme_clean}")
        return "\n".join(parts)

    @staticmethod
    def for_metadata(text: str) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned[:1024]
