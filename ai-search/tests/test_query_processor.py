import pytest

from ai.query_processor.engine import QueryUnderstandingEngine
from ai.query_processor.entity_registry import EntityRegistry
from ai.query_processor.models import FilterType, IntentType, TechnologyType
from ai.query_processor.spelling import SpellingCorrector
from ai.query_processor.synonyms import SynonymResolver


@pytest.fixture
def engine():
    return QueryUnderstandingEngine()


@pytest.fixture
def registry():
    return EntityRegistry()


# --- Entity Registry Tests ---


class TestEntityRegistry:
    def test_resolve_python(self, registry) -> None:
        tech = registry.resolve_entity("python")
        assert tech is not None
        assert tech.name == "Python"
        assert tech.type == TechnologyType.LANGUAGE

    def test_resolve_synonym_ml(self, registry) -> None:
        result = registry.resolve_synonym("ml")
        assert result == "machine learning"

    def test_resolve_synonym_ai(self, registry) -> None:
        result = registry.resolve_synonym("ai")
        assert result == "artificial intelligence"

    def test_resolve_abbreviation_repo(self, registry) -> None:
        result = registry.resolve_abbreviation("repo")
        assert result == "repository"

    def test_resolve_abbreviation_app(self, registry) -> None:
        result = registry.resolve_abbreviation("app")
        assert result == "application"

    def test_resolve_category_video_editing(self, registry) -> None:
        result = registry.resolve_category("video editor")
        assert result is not None

    def test_resolve_category_password_manager(self, registry) -> None:
        result = registry.resolve_category("password manager")
        assert result is not None

    def test_known_terms_not_empty(self, registry) -> None:
        terms = registry.all_known_terms
        assert len(terms) > 100

    def test_search_entities_finds_react(self, registry) -> None:
        results = registry.search_entities("build a web app with react")
        found = any(tech.name == "React" for _, tech, _ in results)
        assert found

    def test_search_entities_finds_python(self, registry) -> None:
        results = registry.search_entities("python data analysis")
        found = any(tech.name == "Python" for _, tech, _ in results)
        assert found


# --- Spelling Corrector Tests ---


class TestSpellingCorrector:
    def test_correct_known_word_unchanged(self) -> None:
        corrector = SpellingCorrector()
        known = {"python", "javascript", "react"}
        text, changes = corrector.correct("python", known)
        assert len(changes) == 0

    def test_correct_minor_typo(self) -> None:
        corrector = SpellingCorrector(max_distance=2)
        known = {"python", "javascript"}
        text, changes = corrector.correct("pythno", known)
        assert len(changes) > 0
        assert changes[0]["corrected"] == "python"

    def test_correct_unknown_word_ignored(self) -> None:
        corrector = SpellingCorrector(max_distance=2)
        known = {"python"}
        text, changes = corrector.correct("xyzzxzywz", known)
        assert len(changes) == 0

    def test_correct_empty_text(self) -> None:
        corrector = SpellingCorrector()
        text, changes = corrector.correct("", set())
        assert text == ""

    def test_correct_short_word_unchanged(self) -> None:
        corrector = SpellingCorrector()
        known = {"go", "rust"}
        text, changes = corrector.correct("go", known)
        assert len(changes) == 0


# --- Synonym Resolver Tests ---


class TestSynonymResolver:
    def test_resolve_ml_to_machine_learning(self) -> None:
        resolver = SynonymResolver()
        text, changes = resolver.resolve("ml framework")
        assert any(c["resolved"] == "machine learning" for c in changes)

    def test_resolve_ai(self) -> None:
        resolver = SynonymResolver()
        text, changes = resolver.resolve("ai chatbot")
        assert any(c["resolved"] == "artificial intelligence" for c in changes)

    def test_resolve_abbreviation(self) -> None:
        resolver = SynonymResolver()
        text, changes = resolver.resolve("cli tool")
        assert any(c["resolved"] == "command line interface" for c in changes)

    def test_no_changes_for_plain_text(self) -> None:
        resolver = SynonymResolver()
        text, changes = resolver.resolve("hello world")
        assert len(changes) == 0

    def test_empty_text(self) -> None:
        resolver = SynonymResolver()
        text, changes = resolver.resolve("")
        assert text == ""


# --- Intent Extraction Tests ---


class TestIntentExtraction:
    def test_search_intent_default(self, engine) -> None:
        result = engine.understand("python web framework")
        assert result.intent == IntentType.SEARCH

    def test_compare_intent(self, engine) -> None:
        result = engine.understand("compare react vs vue")
        assert result.intent == IntentType.COMPARE

    def test_recommend_intent(self, engine) -> None:
        result = engine.understand("best python ide")
        assert result.intent == IntentType.RECOMMEND

    def test_explore_intent(self, engine) -> None:
        result = engine.understand("explore machine learning tools")
        assert result.intent in (IntentType.EXPLORE, IntentType.DISCOVER, IntentType.SEARCH)

    def test_spelling_mistake_still_detects_search(self, engine) -> None:
        result = engine.understand("find me a good pytnon web framwerk")
        assert result.confidence > 0


# --- Domain Extraction Tests ---


class TestDomainExtraction:
    def test_video_editor_domain(self, engine) -> None:
        result = engine.understand("best open source video editor")
        assert result.domain is not None

    def test_password_manager_domain(self, engine) -> None:
        result = engine.understand("password manager for teams")
        assert result.domain is not None

    def test_chatbot_domain(self, engine) -> None:
        result = engine.understand("build an ai chatbot")
        assert result.domain is not None

    def test_expense_tracker_domain(self, engine) -> None:
        result = engine.understand("expense tracker app")
        assert result.domain is not None

    def test_ocr_domain(self, engine) -> None:
        result = engine.understand("ocr tool for pdf")
        assert result.domain is not None


# --- Technology Extraction Tests ---


class TestTechnologyExtraction:
    def test_detects_python(self, engine) -> None:
        result = engine.understand("python machine learning library")
        assert "Python" in result.programming_languages

    def test_detects_react(self, engine) -> None:
        result = engine.understand("react dashboard template")
        assert "React" in result.frameworks or "React" in [t.name for t in result.technologies]

    def test_detects_django(self, engine) -> None:
        result = engine.understand("django rest api")
        assert "Django" in result.frameworks

    def test_detects_postgresql(self, engine) -> None:
        result = engine.understand("postgresql database tool")
        assert "PostgreSQL" in result.databases or "PostgreSQL" in [
            t.name for t in result.technologies
        ]

    def test_detects_docker(self, engine) -> None:
        result = engine.understand("docker deployment")
        assert "Docker" in result.platforms or "Docker" in [t.name for t in result.technologies]

    def test_multiple_technologies(self, engine) -> None:
        result = engine.understand("react python flask postgresql")
        assert len(result.programming_languages) > 0
        assert len(result.frameworks) > 0

    def test_detects_tensorflow(self, engine) -> None:
        result = engine.understand("tensorflow deep learning")
        assert "TensorFlow" in result.frameworks or "TensorFlow" in [
            t.name for t in result.technologies
        ]


# --- Filter Extraction Tests ---


class TestFilterExtraction:
    def test_free_filter(self, engine) -> None:
        result = engine.understand("free video editor")
        assert any(f.type == FilterType.COST for f in result.filters)

    def test_open_source_filter(self, engine) -> None:
        result = engine.understand("open source password manager")
        assert any(f.type == FilterType.COST for f in result.filters)

    def test_mobile_filter(self, engine) -> None:
        result = engine.understand("mobile expense tracker")
        assert any(f.type == FilterType.PLATFORM and f.value == "mobile" for f in result.filters)

    def test_cross_platform_filter(self, engine) -> None:
        result = engine.understand("cross platform music player")
        assert any(f.type == FilterType.PLATFORM and "cross" in f.value for f in result.filters)

    def test_license_filter(self, engine) -> None:
        result = engine.understand("mit license react components")
        assert any(f.type == FilterType.LICENSE for f in result.filters)

    def test_popularity_filter(self, engine) -> None:
        result = engine.understand("most popular python framework")
        assert any(f.type == FilterType.POPULARITY for f in result.filters)

    def test_maintained_filter(self, engine) -> None:
        result = engine.understand("actively maintained orm")
        assert any(f.type == FilterType.MAINTAINED for f in result.filters)


# --- Full Pipeline Integration Tests ---


class TestFullPipeline:
    def test_video_editing_pipeline(self, engine) -> None:
        result = engine.understand("best free video editing software for linux")
        assert result.intent == IntentType.RECOMMEND
        assert result.confidence > 0.3

    def test_ai_chatbot_pipeline(self, engine) -> None:
        result = engine.understand("build an ai chatbot with python")
        assert result.intent in (IntentType.SEARCH, IntentType.EXPLORE)
        assert "Python" in result.programming_languages

    def test_password_manager_pipeline(self, engine) -> None:
        result = engine.understand("open source password manager")
        assert result.confidence > 0
        assert any(f.value == "open-source" or f.value == "free" for f in result.filters)

    def test_ocr_pipeline(self, engine) -> None:
        result = engine.understand("ocr library for document scanning")
        assert result.confidence > 0

    def test_empty_query(self, engine) -> None:
        result = engine.understand("")
        assert result.confidence == 0.0

    def test_whitespace_query(self, engine) -> None:
        result = engine.understand("   ")
        assert result.confidence == 0.0

    def test_abbreviation_expansion(self, engine) -> None:
        result = engine.understand("ml framework")
        assert "machine learning" in result.expanded_query

    def test_query_normalization(self, engine) -> None:
        result = engine.understand("  Find   Me   a   TOOL!!  ")
        assert result.normalized_query == "Find Me a TOOL"

    def test_compare_vs(self, engine) -> None:
        result = engine.understand("react vs angular")
        assert result.intent == IntentType.COMPARE

    def test_hospital_management(self, engine) -> None:
        result = engine.understand("hospital management system")
        assert result.domain is not None

    def test_image_compression(self, engine) -> None:
        result = engine.understand("image compression library")
        assert result.confidence > 0

    def test_music_streaming(self, engine) -> None:
        result = engine.understand("music streaming app")
        assert result.confidence > 0

    def test_compiler_query(self, engine) -> None:
        result = engine.understand("c++ compiler")
        assert result.confidence > 0

    def test_synonym_k8s(self, engine) -> None:
        result = engine.understand("k8s deployment tool")
        assert "kubernetes" in result.expanded_query

    def test_multiple_filters(self, engine) -> None:
        result = engine.understand("free mobile open source note taking app")
        cost_filters = [f for f in result.filters if f.type == FilterType.COST]
        platform_filters = [f for f in result.filters if f.type == FilterType.PLATFORM]
        assert len(cost_filters) > 0
        assert len(platform_filters) > 0

    def test_explore_intent(self, engine) -> None:
        result = engine.understand("explore data visualization tools")
        assert result.intent in (IntentType.EXPLORE, IntentType.DISCOVER, IntentType.SEARCH)

    def test_no_crash_on_special_chars(self, engine) -> None:
        result = engine.understand("###  $$$  @@@")
        assert result.confidence == 0.0


# --- LLM Extractor Tests ---


class TestLLMExtractor:
    def test_llm_extractor_disabled_by_default(self, engine) -> None:
        assert engine._llm_extractor is None

    def test_llm_extractor_graceful_degradation(self) -> None:
        from ai.query_processor.llm_extractor import LLMExtractor
        extractor = LLMExtractor()
        from ai.query_processor.models import ExtractionContext
        ctx = ExtractionContext(original_query="test", normalized_query="test")
        result = extractor.extract(ctx)
        assert len(result.entities) == 0


# --- Edge Cases ---


class TestEdgeCases:
    def test_single_word_tool(self, engine) -> None:
        result = engine.understand("docker")
        assert result.confidence > 0
        assert "Docker" in result.platforms or "Docker" in [t.name for t in result.technologies]

    def test_abbreviation_only(self, engine) -> None:
        result = engine.understand("nlp")
        assert "natural language processing" in result.expanded_query

    def test_spelling_typo_python(self, engine) -> None:
        result = engine.understand("pythn web app")
        assert "Python" in result.programming_languages or result.confidence > 0

    def test_cross_platform_desktop(self, engine) -> None:
        result = engine.understand("cross platform desktop app framework")
        assert any(f.type == FilterType.PLATFORM for f in result.filters)
