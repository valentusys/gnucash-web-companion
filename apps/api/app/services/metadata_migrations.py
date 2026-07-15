"""Idempotent additive app metadata migrations."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Engine, make_url

from app.config import Settings
from app.schemas.users import UsernameValidationError, normalize_username
from app.services.book_preflight import canonicalize_existing_book_path


class MetadataMigrationError(RuntimeError):
    """Raised for controlled, redacted app metadata migration blockers."""


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S.%f")


def _table_names(conn) -> set[str]:
    rows = conn.execute(text("select name from sqlite_master where type = 'table'")).fetchall()
    return {str(row[0]) for row in rows}


def _column_names(conn, table_name: str) -> set[str]:
    rows = conn.execute(text(f"pragma table_info({table_name})")).fetchall()
    return {str(row[1]) for row in rows}


def _add_column_if_missing(conn, table_name: str, column_name: str, ddl: str) -> None:
    if column_name not in _column_names(conn, table_name):
        conn.execute(text(f"alter table {table_name} add column {ddl}"))


def _create_health_snapshot_table(conn) -> None:
    conn.execute(
        text(
            "create table if not exists book_health_snapshots ("
            "book_id integer primary key, "
            "source_status varchar(64) not null default 'not_checked', "
            "open_status varchar(64) not null default 'not_checked', "
            "accounts_status varchar(64) not null default 'not_checked', "
            "transactions_status varchar(64) not null default 'not_checked', "
            "reports_status varchar(64) not null default 'not_checked', "
            "safe_code varchar(64) not null default 'not_checked', "
            "checked_at datetime null, "
            "last_successful_at datetime null, "
            "foreign key(book_id) references books(id) on delete cascade)"
        )
    )


def _create_canonical_unique_index(conn) -> None:
    conn.execute(
        text(
            "create unique index if not exists uq_books_canonical_path_hash_active "
            "on books(canonical_path_hash) "
            "where canonical_path_hash is not null and is_archived = 0"
        )
    )


def _create_user_normalized_unique_index(conn) -> None:
    conn.execute(
        text(
            "create unique index if not exists uq_users_username_normalized "
            "on users(username_normalized)"
        )
    )


def _legacy_user_normalized_keys(conn) -> dict[int, str]:
    rows = conn.execute(text("select id, username from users order by id")).mappings().all()
    keys_by_id: dict[int, str] = {}
    ids_by_key: dict[str, list[int]] = {}
    for row in rows:
        try:
            normalized = normalize_username(str(row["username"] or ""))
        except UsernameValidationError as exc:
            raise MetadataMigrationError(
                "Cannot migrate legacy users: invalid normalized usernames; "
                "resolve app metadata before startup."
            ) from exc
        user_id = int(row["id"])
        keys_by_id[user_id] = normalized
        ids_by_key.setdefault(normalized, []).append(user_id)
    if any(len(user_ids) > 1 for user_ids in ids_by_key.values()):
        raise MetadataMigrationError(
            "Cannot migrate legacy users: duplicate normalized usernames; "
            "resolve app metadata before startup."
        )
    return keys_by_id


def _migrate_users_issue57(conn) -> None:
    """Add #57 auth foundation columns while preserving legacy user rows."""

    normalized_by_id = _legacy_user_normalized_keys(conn)
    _add_column_if_missing(
        conn,
        "users",
        "username_normalized",
        "username_normalized varchar(64) not null default ''",
    )
    _add_column_if_missing(
        conn,
        "users",
        "is_enabled",
        "is_enabled boolean not null default 1",
    )
    _add_column_if_missing(
        conn,
        "users",
        "auth_version",
        "auth_version integer not null default 1",
    )
    _add_column_if_missing(
        conn,
        "users",
        "updated_at",
        "updated_at datetime not null default '1970-01-01 00:00:00.000000'",
    )
    now = _utc_now_text()
    for user_id, normalized in normalized_by_id.items():
        conn.execute(
            text(
                "update users set username_normalized = :username_normalized "
                "where id = :user_id"
            ),
            {"user_id": user_id, "username_normalized": normalized},
        )
    conn.execute(text("update users set is_enabled = 1 where is_enabled is null"))
    conn.execute(text("update users set auth_version = 1 where auth_version is null"))
    conn.execute(
        text(
            "update users set updated_at = :updated_at "
            "where updated_at is null or updated_at = '1970-01-01 00:00:00.000000'"
        ),
        {"updated_at": now},
    )
    _create_user_normalized_unique_index(conn)


def _ensure_book_health_rows(conn) -> None:
    conn.execute(
        text(
            "insert or ignore into book_health_snapshots "
            "(book_id, source_status, open_status, accounts_status, transactions_status, reports_status, safe_code, checked_at, last_successful_at) "
            "select id, 'not_checked', 'not_checked', 'not_checked', 'not_checked', 'not_checked', 'not_checked', null, null "
            "from books"
        )
    )


def _canonicalize_legacy_rows(conn, settings: Settings) -> None:
    seen_hashes = {
        str(row[0])
        for row in conn.execute(
            text(
                "select canonical_path_hash from books "
                "where canonical_path_hash is not null and is_archived = 0"
            )
        ).fetchall()
    }
    rows = conn.execute(
        text(
            "select id, uri_or_path from books "
            "where canonical_path_hash is null and is_archived = 0"
        )
    ).mappings().all()
    for row in rows:
        identity = canonicalize_existing_book_path(str(row["uri_or_path"] or ""), settings)
        if identity is None or identity.canonical_path_hash in seen_hashes:
            conn.execute(
                text(
                    "update books set is_enabled = 0, updated_at = coalesce(updated_at, :updated_at) "
                    "where id = :book_id"
                ),
                {"book_id": row["id"], "updated_at": _utc_now_text()},
            )
            continue
        conn.execute(
            text(
                "update books set canonical_path = :canonical_path, "
                "canonical_path_hash = :canonical_path_hash, is_enabled = 1, "
                "updated_at = coalesce(updated_at, :updated_at) where id = :book_id"
            ),
            {
                "book_id": row["id"],
                "canonical_path": identity.canonical_path,
                "canonical_path_hash": identity.canonical_path_hash,
                "updated_at": _utc_now_text(),
            },
        )
        seen_hashes.add(identity.canonical_path_hash)


def run_app_metadata_migrations(engine: Engine, settings: Settings) -> None:
    """Run explicit additive migrations for SQLite app metadata databases.

    SQLAlchemy create_all creates missing tables but does not alter existing
    tables. This function is safe to run on every startup before seed/access use.
    It preserves rows and adds only explicit metadata columns/tables/indexes.
    """

    url = make_url(str(engine.url))
    if url.get_backend_name() != "sqlite":
        return

    with engine.begin() as conn:
        table_names = _table_names(conn)
        if "users" in table_names:
            _migrate_users_issue57(conn)
        if "books" not in table_names:
            return
        _add_column_if_missing(conn, "books", "canonical_path", "canonical_path varchar(1024)")
        _add_column_if_missing(conn, "books", "canonical_path_hash", "canonical_path_hash varchar(64)")
        _add_column_if_missing(conn, "books", "is_enabled", "is_enabled boolean not null default 1")
        _add_column_if_missing(conn, "books", "updated_at", "updated_at datetime")
        conn.execute(
            text("update books set updated_at = :updated_at where updated_at is null"),
            {"updated_at": _utc_now_text()},
        )
        _create_health_snapshot_table(conn)
        _add_column_if_missing(
            conn,
            "book_health_snapshots",
            "last_successful_at",
            "last_successful_at datetime",
        )
        _ensure_book_health_rows(conn)
        _canonicalize_legacy_rows(conn, settings)
        _create_canonical_unique_index(conn)
        _ensure_book_health_rows(conn)
