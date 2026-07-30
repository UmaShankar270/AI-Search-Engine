from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    SEARCH = "search"
    COMPARE = "compare"
    RECOMMEND = "recommend"
    EXPLORE = "explore"
    DISCOVER = "discover"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    TOOL = "tool"
    DATABASE = "database"
    PLATFORM = "platform"
    DOMAIN = "domain"
    CATEGORY = "category"
    TECHNOLOGY = "technology"
    FILTER = "filter"


class TechnologyType(str, Enum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    TOOL = "tool"
    DATABASE = "database"
    PLATFORM = "platform"
    RUNTIME = "runtime"


class FilterType(str, Enum):
    LICENSE = "license"
    COST = "cost"
    PLATFORM = "platform"
    LANGUAGE = "language"
    FEATURE = "feature"
    POPULARITY = "popularity"
    MAINTAINED = "maintained"


class Technology(BaseModel):
    name: str
    type: TechnologyType
    aliases: list[str] = Field(default_factory=list)
    category: str = ""


class Filter(BaseModel):
    type: FilterType
    value: str
    original_text: str = ""


class ExtractedEntity(BaseModel):
    text: str
    entity_type: EntityType
    confidence: float = 1.0
    source: str = "rule_based"
    normalized: Optional[str] = None


class ExtractionContext(BaseModel):
    original_query: str
    normalized_query: str = ""
    corrected_query: str = ""
    expanded_query: str = ""
    tokens: list[str] = Field(default_factory=list)
    extracted_entities: list[ExtractedEntity] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    entities: list[ExtractedEntity] = Field(default_factory=list)
    confidence: float = 1.0


class QueryUnderstandingResult(BaseModel):
    original_query: str
    normalized_query: str
    corrected_query: str
    expanded_query: str
    intent: IntentType = IntentType.UNKNOWN
    domain: Optional[str] = None
    technologies: list[Technology] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    libraries: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    filters: list[Filter] = Field(default_factory=list)
    extracted_entities: list[ExtractedEntity] = Field(default_factory=list)
    confidence: float = 0.0
    processing_time_ms: float = 0.0
