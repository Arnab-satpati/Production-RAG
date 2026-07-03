from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")

    base_url: str = "http://localhost:11434"
    model: str = "llama3.1:8b"
    embedding_model: str = "nomic-embed-text"
    timeout: int = 120
    temperature: float = 0.1
    max_tokens: int = 4096


class QdrantSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="QDRANT_")

    host: str = "localhost"
    port: int = 6333
    grpc_port: int = 6334
    collection: str = "rag_documents"
    embedding_dim: int = 768


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    cache_ttl: int = 3600


class MLflowSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MLFLOW_")

    tracking_uri: str = "http://localhost:5000"
    experiment_name: str = "rag-production"


class ChunkingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CHUNKING_")

    chunk_size: int = 512
    chunk_overlap: int = 64
    min_chunk_size: int = 50


class RetrievalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RETRIEVAL_")

    top_k: int = 5
    similarity_threshold: float = 0.7
    rerank_top_k: int = 3


class GuardrailsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GUARDRAILS_")

    max_input_length: int = 10000
    rate_limit_per_minute: int = 60
    enable_output_filtering: bool = True
    blocked_patterns: list[str] = Field(default_factory=list)


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_")

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000
    workers: int = 4
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
    )
    enable_docs: bool = True


class MonitoringSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OTEL_")

    exporter_otlp_endpoint: str = "http://localhost:4317"
    service_name: str = "rag-production"
    enable_tracing: bool = True


class Settings(BaseSettings):
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    mlflow: MLflowSettings = Field(default_factory=MLflowSettings)
    chunking: ChunkingSettings = Field(default_factory=ChunkingSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    guardrails: GuardrailsSettings = Field(default_factory=GuardrailsSettings)
    api: APISettings = Field(default_factory=APISettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
