from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_prefix": "AI_", "extra": "ignore"}

    model_name: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    faiss_index_type: str = "Flat"
    top_k_default: int = 10
    rerank_top_k: int = 50
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # LLM
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Cache
    cache_ttl_seconds: int = 3600
    cache_max_size_mb: int = 512

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/ai.log"

    # Feature flags
    use_reranking: bool = True
    use_llm_summaries: bool = True
    summary_max_tokens: int = 150
    summary_temperature: float = 0.3
