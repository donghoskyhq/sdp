from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration supplied exclusively through environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Sky Dev Platform Core API"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", validation_alias="SDP_ENVIRONMENT")
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://sdp:sdp-local-only@localhost:5432/sdp"
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")
    queue_name: str = "default"
    cors_origins: list[AnyHttpUrl] = [AnyHttpUrl("http://localhost:3000")]

    github_token: str = ""
    github_owner: str = ""
    github_owner_type: Literal["organization", "user"] = "organization"
    github_api_url: str = "https://api.github.com"
    github_repository_private: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
