"""Application configuration loaded from environment variables."""

import json
from functools import lru_cache
from pathlib import PurePosixPath
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_database_url: str = "sqlite:////data/app/app.db"
    gnucash_default_book_path: str = ""
    gnucash_book_allowed_roots: list[str] = Field(default_factory=lambda: ["/data/books"])
    gnucash_preflight_token_ttl_seconds: int = 600
    jwt_secret: str = ""
    jwt_token_expire_minutes: int = 30
    app_admin_username: str = "admin"
    app_admin_password: str = ""
    app_admin_password_hash: str = ""
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    gnucash_writes_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("gnucash_book_allowed_roots", mode="before")
    @classmethod
    def _parse_allowed_roots(cls, value: Any) -> Any:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError("GNUCASH_BOOK_ALLOWED_ROOTS must be a JSON list of absolute POSIX directories") from exc
        return value

    @field_validator("gnucash_book_allowed_roots")
    @classmethod
    def _validate_allowed_roots(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for raw_root in value:
            root = str(raw_root).strip()
            if (
                not root
                or "\x00" in root
                or root.startswith("~")
                or "$" in root
                or "://" in root
                or "\\" in root
            ):
                raise ValueError("GNUCASH_BOOK_ALLOWED_ROOTS entries must be absolute POSIX directory paths")
            parsed = PurePosixPath(root)
            if not parsed.is_absolute() or any(part in {".", ".."} for part in parsed.parts):
                raise ValueError("GNUCASH_BOOK_ALLOWED_ROOTS entries must be absolute POSIX directory paths")
            cleaned = parsed.as_posix().rstrip("/") or "/"
            if cleaned not in seen:
                normalized.append(cleaned)
                seen.add(cleaned)
        if not normalized:
            raise ValueError("GNUCASH_BOOK_ALLOWED_ROOTS must contain at least one directory")
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()
