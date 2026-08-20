from __future__ import annotations

from typing import Literal

from pydantic import Field, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="forbid",
    )

    APP_ENV: Literal["development", "test", "production"] = "development"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = Field(default=8000, ge=1, le=65535)
    DATABASE_URL: str = Field(min_length=1)
    SESSION_HMAC_SECRET: SecretStr = Field(min_length=32)
    AI_BASE_URL: HttpUrl = HttpUrl("https://api.avalai.ir/v1")
    AVALAI_API_KEY: SecretStr = Field(min_length=16)
    AI_FAST_MODEL: str = "gpt-5.4-mini"
    AI_REASONING_MODEL: str = "gpt-5.5"
    AI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    KNOWLEDGE_SNAPSHOT_VERSION: str = "test-fixture"
    RETRIEVAL_SEMANTIC_THRESHOLD: float = Field(default=0.62, ge=0, le=1)
    CITATION_SEMANTIC_THRESHOLD: float = Field(default=0.72, ge=0, le=1)
    CITATION_LEXICAL_THRESHOLD: float = Field(default=0.25, ge=0, le=1)
    CPU_EXECUTOR_WORKERS: int = Field(default=2, ge=1, le=8)

    @field_validator("SESSION_HMAC_SECRET")
    @classmethod
    def reject_placeholder_session_secret(cls, value: SecretStr) -> SecretStr:
        normalized = value.get_secret_value().lower()
        forbidden_fragments = ("change-me", "placeholder", "example-secret")
        if any(fragment in normalized for fragment in forbidden_fragments):
            raise ValueError("SESSION_HMAC_SECRET must not be a placeholder")
        return value

    @field_validator("AI_BASE_URL")
    @classmethod
    def require_https_ai_endpoint(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme != "https":
            raise ValueError("AI_BASE_URL must use HTTPS")
        return value
