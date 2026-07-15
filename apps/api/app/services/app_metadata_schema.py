"""Shared app metadata SQLite schema constants."""

from __future__ import annotations

CURRENT_APP_METADATA_SCHEMA_VERSION = 58

APP_METADATA_TABLE_ALLOWLIST: tuple[str, ...] = (
    "users",
    "books",
    "user_book_access",
    "book_health_snapshots",
    "audit_logs",
    "write_alpha_transaction_ownership",
)

APP_METADATA_REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "users": (
        "id",
        "username",
        "username_normalized",
        "display_name",
        "password_hash",
        "is_admin",
        "is_enabled",
        "auth_version",
        "created_at",
        "updated_at",
    ),
    "books": (
        "id",
        "name",
        "storage_type",
        "uri_or_path",
        "canonical_path",
        "canonical_path_hash",
        "base_currency",
        "is_default",
        "is_archived",
        "is_enabled",
        "created_at",
        "updated_at",
    ),
    "user_book_access": (
        "user_id",
        "book_id",
        "role",
    ),
    "book_health_snapshots": (
        "book_id",
        "source_status",
        "open_status",
        "accounts_status",
        "transactions_status",
        "reports_status",
        "safe_code",
        "checked_at",
        "last_successful_at",
    ),
    "audit_logs": (
        "id",
        "user_id",
        "book_id",
        "action",
        "payload_json",
        "created_at",
    ),
    "write_alpha_transaction_ownership": (
        "id",
        "book_id",
        "transaction_id",
        "created_by_user_id",
        "created_by_write_alpha",
        "created_at",
        "last_mutated_at",
    ),
}

APP_METADATA_REQUIRED_UNIQUE_INDEX_COLUMNS: dict[str, set[tuple[str, ...]]] = {
    "users": {("username",), ("username_normalized",)},
    "books": {("canonical_path_hash",)},
    "write_alpha_transaction_ownership": {("book_id", "transaction_id")},
}
