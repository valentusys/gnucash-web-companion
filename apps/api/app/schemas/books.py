"""Typed book registry and preflight DTOs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BookProblemDTO(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=240)
    retryable: bool = False


class BookSectionStatusDTO(BaseModel):
    status: Literal[
        "ready",
        "available",
        "already_registered",
        "empty",
        "blocked",
        "not_checked",
        "unsupported",
        "failed",
    ]
    safe_code: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=240)
    retryable: bool = False


class BookHealthDTO(BaseModel):
    status: str = Field(min_length=1, max_length=64)
    source_status: str = Field(min_length=1, max_length=64)
    open_status: str = Field(min_length=1, max_length=64)
    accounts_status: str = Field(min_length=1, max_length=64)
    transactions_status: str = Field(min_length=1, max_length=64)
    reports_status: str = Field(min_length=1, max_length=64)
    safe_code: str = Field(min_length=1, max_length=64)
    checked_at: str | None = None


class BookCapabilitiesDTO(BaseModel):
    read_only: bool = True
    can_register_metadata: bool = False
    can_open_accounts: bool = False
    can_open_transactions: bool = False
    can_open_reports: bool = False
    can_upload: bool = False
    can_edit: bool = False
    can_delete: bool = False
    can_edit_gnucash: bool = False
    can_delete_source: bool = False


class BookPreflightReadCountersDTO(BaseModel):
    sqlite_query_count: int = 0
    piecash_open_count: int = 0
    account_materialization_count: int = 0
    transaction_materialization_count: int = 0


class BookPreflightRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    uri_or_path: str = Field(min_length=1, max_length=1024)
    storage_type: Literal["sqlite"] = "sqlite"
    base_currency: str = Field(min_length=1, max_length=16)
    make_default: bool = False

    @field_validator("name", "uri_or_path", mode="before")
    @classmethod
    def _strip_required_text(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("base_currency", mode="before")
    @classmethod
    def _normalize_base_currency(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().upper()
        return value


class BookPreflightResponse(BaseModel):
    status: Literal["ready"]
    format: Literal["gnucash_sqlite"]
    preflight_token: str
    registration_status: BookSectionStatusDTO
    source_status: BookSectionStatusDTO
    open_status: BookSectionStatusDTO
    accounts: BookSectionStatusDTO
    transactions: BookSectionStatusDTO
    reports: BookSectionStatusDTO
    capabilities: BookCapabilitiesDTO
    checked_at: str
    safe_code: str = "ready"
    message: str
    read_counters: BookPreflightReadCountersDTO


class BookPublicDTO(BaseModel):
    """Typed public book foundation.

    Existing routes still include legacy compatibility fields, so this DTO allows
    extra safe fields while explicitly documenting the path-free public contract.
    """

    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    storage_type: Literal["sqlite"] | str
    base_currency: str | None = None
    is_default: bool
    is_archived: bool
    is_enabled: bool
    enabled: bool
    created_at: str | None = None
    updated_at: str | None = None
    health: BookHealthDTO
    capabilities: dict[str, Any]
    management_actions: list[str]
