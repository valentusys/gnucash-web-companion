"""Issue #57 auth-foundation app metadata migration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.models import User
from app.services.auth import authenticate_user, hash_password
from app.services.metadata_migrations import MetadataMigrationError, run_app_metadata_migrations


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        app_env="test",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_book_allowed_roots=[str(tmp_path)],
        jwt_secret="test-secret-key-for-issue57-migration-32-bytes",
        app_admin_username="admin",
        app_admin_password="ValidPass123!",
    )


def _create_legacy_schema(engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "create table users ("
                "id integer primary key autoincrement, "
                "username varchar(128) not null unique, "
                "display_name varchar(256) not null, "
                "password_hash varchar(512) not null, "
                "is_admin boolean not null, "
                "created_at datetime not null)"
            )
        )
        conn.execute(
            text(
                "create table books ("
                "id integer primary key autoincrement, "
                "name varchar(256) not null, "
                "storage_type varchar(64) not null, "
                "uri_or_path varchar(1024) not null, "
                "base_currency varchar(16), "
                "is_default boolean not null, "
                "is_archived boolean not null, "
                "created_at datetime not null)"
            )
        )
        conn.execute(
            text(
                "create table user_book_access ("
                "user_id integer not null, "
                "book_id integer not null, "
                "role varchar(16) not null, "
                "primary key (user_id, book_id))"
            )
        )
        conn.execute(
            text(
                "create table audit_logs ("
                "id integer primary key autoincrement, "
                "user_id integer, "
                "book_id integer, "
                "action varchar(128) not null, "
                "payload_json text, "
                "created_at datetime not null)"
            )
        )


def test_issue57_user_migration_preserves_rows_and_is_restart_idempotent(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'legacy-users.db'}",
        connect_args={"check_same_thread": False},
    )
    _create_legacy_schema(engine)
    admin_hash = hash_password("ValidPass123!")
    with engine.begin() as conn:
        conn.execute(
            text(
                "insert into users "
                "(id, username, display_name, password_hash, is_admin, created_at) "
                "values (1, 'Admin', 'Legacy Admin', :hash, 1, '2026-01-01 00:00:00.000000')"
            ),
            {"hash": admin_hash},
        )
        conn.execute(
            text(
                "insert into users "
                "(id, username, display_name, password_hash, is_admin, created_at) "
                "values (2, 'viewer', 'Viewer', 'hash2', 0, '2026-01-02 00:00:00.000000')"
            )
        )
        conn.execute(
            text(
                "insert into books "
                "(id, name, storage_type, uri_or_path, base_currency, is_default, is_archived, created_at) "
                "values (10, 'Legacy Book', 'sqlite', '/missing.gnucash.sqlite', 'USD', 1, 0, '2026-01-01 00:00:00.000000')"
            )
        )
        conn.execute(
            text("insert into user_book_access (user_id, book_id, role) values (1, 10, 'owner')")
        )
        conn.execute(
            text(
                "insert into audit_logs (id, user_id, book_id, action, payload_json, created_at) "
                "values (100, 1, 10, 'legacy.event', :payload_json, '2026-01-03 00:00:00.000000')"
            ),
            {"payload_json": '{"ok":true}'},
        )

    run_app_metadata_migrations(engine, _settings(tmp_path))
    run_app_metadata_migrations(engine, _settings(tmp_path))

    inspector = inspect(engine)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    assert {"username_normalized", "is_enabled", "auth_version", "updated_at"}.issubset(
        user_columns
    )
    assert "uq_users_username_normalized" in {
        index["name"] for index in inspector.get_indexes("users")
    }
    with engine.connect() as conn:
        admin = conn.execute(text("select * from users where id=1")).mappings().one()
        viewer = conn.execute(text("select * from users where id=2")).mappings().one()
        assert admin["username"] == "Admin"
        assert admin["username_normalized"] == "admin"
        assert admin["is_enabled"] == 1
        assert admin["auth_version"] == 1
        assert admin["updated_at"] is not None
        assert viewer["username_normalized"] == "viewer"
        assert conn.execute(text("select count(*) from user_book_access")).scalar_one() == 1
        assert conn.execute(text("select count(*) from audit_logs")).scalar_one() == 1

    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        assert authenticate_user(session, " admin ", "ValidPass123!").id == 1
        session.add(User(username="ADMIN", display_name="Duplicate", password_hash="hash3"))
        with pytest.raises(IntegrityError):
            session.commit()


def test_issue57_normalized_collision_aborts_without_partial_user_migration(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'collision-users.db'}",
        connect_args={"check_same_thread": False},
    )
    _create_legacy_schema(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "insert into users "
                "(id, username, display_name, password_hash, is_admin, created_at) "
                "values (1, 'Alice', 'Alice', 'hash1', 1, '2026-01-01 00:00:00.000000')"
            )
        )
        conn.execute(
            text(
                "insert into users "
                "(id, username, display_name, password_hash, is_admin, created_at) "
                "values (2, 'alice', 'Alice 2', 'hash2', 0, '2026-01-02 00:00:00.000000')"
            )
        )
        conn.execute(
            text(
                "insert into books "
                "(id, name, storage_type, uri_or_path, base_currency, is_default, is_archived, created_at) "
                "values (10, 'Legacy Book', 'sqlite', '/missing.gnucash.sqlite', 'USD', 1, 0, '2026-01-01 00:00:00.000000')"
            )
        )

    with pytest.raises(MetadataMigrationError) as exc_info:
        run_app_metadata_migrations(engine, _settings(tmp_path))

    assert "duplicate normalized usernames" in str(exc_info.value)
    assert "Alice" not in str(exc_info.value)
    assert "alice" not in str(exc_info.value)
    inspector = inspect(engine)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    assert "username_normalized" not in user_columns
    assert "is_enabled" not in user_columns
    assert "auth_version" not in user_columns
    assert "updated_at" not in user_columns
    assert "uq_users_username_normalized" not in {
        index["name"] for index in inspector.get_indexes("users")
    }
    with engine.connect() as conn:
        assert conn.execute(text("select count(*) from users")).scalar_one() == 2
