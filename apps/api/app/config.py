"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_database_url: str = "sqlite:////data/app/app.db"
    gnucash_default_book_path: str = "/data/books/main.gnucash.sqlite"
    jwt_secret: str = "change-me"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
