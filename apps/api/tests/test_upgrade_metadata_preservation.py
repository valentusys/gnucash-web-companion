"""Synthetic upgrade app-metadata preservation regression tests.

These tests pin the startup/seed behavior relied on by the Phase 214 Docker
upgrade smoke: an existing app metadata DB from a previous tag must remain
readable and must not be overwritten by current startup seeding.
"""

from __future__ import annotations

import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.database import Base
from app.models import AuditLog, Book, User, UserBookAccess
from app.services.auth import seed_admin_user, verify_password, hash_password
from app.services.app_metadata_schema import CURRENT_APP_METADATA_SCHEMA_VERSION
from app.services.metadata_migrations import run_app_metadata_migrations
from app.services.seed import seed_admin_default_book_access, seed_default_book


TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-upgrade-tests-32-bytes",
    app_admin_username="admin",
    app_admin_password="new-bootstrap-password-that-must-not-replace-existing",
    gnucash_default_book_path="/data/books/main.gnucash.sqlite",
    gnucash_writes_enabled=False,
)


def _session_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def test_upgrade_seed_functions_are_idempotent_for_existing_user_book_access(monkeypatch):
    monkeypatch.setattr("app.services.auth.get_settings", lambda: TEST_SETTINGS)
    session_factory = _session_factory()

    with session_factory() as session:
        admin = User(
            username="admin",
            display_name="Existing Admin",
            password_hash=hash_password("previous-dummy-password"),
            is_admin=True,
        )
        default_book = Book(
            name="Existing Synthetic Main",
            storage_type="sqlite",
            uri_or_path="/data/books/main.gnucash.sqlite",
            base_currency="USD",
            is_default=True,
        )
        session.add_all([admin, default_book])
        session.commit()
        session.refresh(admin)
        session.refresh(default_book)
        session.add(UserBookAccess(user_id=admin.id, book_id=default_book.id, role="editor"))
        session.add(
            AuditLog(
                user_id=admin.id,
                book_id=default_book.id,
                action="transaction.create",
                payload_json='{"result":"success","transaction_id":"phase-214-legacy-synthetic"}',
            )
        )
        session.commit()
        original_user_id = admin.id
        original_book_id = default_book.id

    with session_factory() as session:
        returned_book = seed_default_book(session, "/data/books/replacement-should-not-win.gnucash.sqlite")
        seeded_user = seed_admin_user(session)
        seeded_access = seed_admin_default_book_access(session)

        users = session.query(User).all()
        books = session.query(Book).all()
        access_rows = session.query(UserBookAccess).all()
        audit_rows = session.query(AuditLog).all()

        assert returned_book is not None
        assert returned_book.id == original_book_id
        assert seeded_user is None
        assert seeded_access is not None
        assert seeded_access.role == "editor"
        assert len(users) == 1
        assert users[0].id == original_user_id
        assert users[0].display_name == "Existing Admin"
        assert verify_password("previous-dummy-password", users[0].password_hash)
        assert not verify_password(TEST_SETTINGS.app_admin_password, users[0].password_hash)
        assert len(books) == 1
        assert books[0].id == original_book_id
        assert books[0].uri_or_path == "/data/books/main.gnucash.sqlite"
        assert books[0].is_default is True
        assert len(access_rows) == 1
        assert access_rows[0].role == "editor"
        assert len(audit_rows) == 1
        assert audit_rows[0].action == "transaction.create"


def test_upgrade_seed_adds_missing_access_without_replacing_preserved_metadata(monkeypatch):
    monkeypatch.setattr("app.services.auth.get_settings", lambda: TEST_SETTINGS)
    session_factory = _session_factory()

    with session_factory() as session:
        admin = User(
            username="admin",
            display_name="Existing Admin",
            password_hash=hash_password("previous-dummy-password"),
            is_admin=True,
        )
        default_book = Book(
            name="Existing Synthetic Main",
            storage_type="sqlite",
            uri_or_path="/data/books/main.gnucash.sqlite",
            is_default=True,
        )
        session.add_all([admin, default_book])
        session.commit()
        session.refresh(admin)
        session.refresh(default_book)
        original_user_id = admin.id
        original_book_id = default_book.id

    with session_factory() as session:
        assert seed_default_book(session, "/data/books/other.gnucash.sqlite").id == original_book_id
        assert seed_admin_user(session) is None
        access = seed_admin_default_book_access(session)

        assert access is not None
        assert access.user_id == original_user_id
        assert access.book_id == original_book_id
        assert access.role == "owner"
        assert session.query(User).count() == 1
        assert session.query(Book).count() == 1
        assert session.query(UserBookAccess).count() == 1


def test_public_readonly_upgrade_preserves_forward_synthetic_metadata(tmp_path):
    db_path = tmp_path / "public-readonly-upgrade-app.db"
    default_book = tmp_path / "main.gnucash.sqlite"
    assigned_book = tmp_path / "assigned.gnucash.sqlite"
    default_book.write_bytes(b"SQLite format 3\x00synthetic-default")
    assigned_book.write_bytes(b"SQLite format 3\x00synthetic-assigned")
    missing_book = tmp_path / "missing-private-sentinel.gnucash.sqlite"

    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            create table users (
                id integer primary key autoincrement,
                username varchar(128) unique not null,
                display_name varchar(256) not null,
                password_hash varchar(512) not null,
                is_admin boolean not null,
                created_at datetime not null,
                username_normalized varchar(64) not null default '',
                is_enabled boolean not null default 1,
                auth_version integer not null default 1,
                updated_at datetime not null default '1970-01-01 00:00:00.000000'
            );
            create table books (
                id integer primary key autoincrement,
                name varchar(256) not null,
                storage_type varchar(64) not null,
                uri_or_path varchar(1024) not null,
                base_currency varchar(16),
                is_default boolean not null,
                is_archived boolean not null,
                created_at datetime not null,
                canonical_path varchar(1024),
                canonical_path_hash varchar(64),
                is_enabled boolean not null default 1,
                updated_at datetime
            );
            create table user_book_access (
                user_id integer not null,
                book_id integer not null,
                role varchar(16) not null,
                primary key (user_id, book_id)
            );
            create table audit_logs (
                id integer primary key autoincrement,
                user_id integer,
                book_id integer,
                action varchar(128) not null,
                payload_json text,
                created_at datetime not null
            );
            create table book_health_snapshots (
                book_id integer primary key,
                source_status varchar(64) not null default 'not_checked',
                open_status varchar(64) not null default 'not_checked',
                accounts_status varchar(64) not null default 'not_checked',
                transactions_status varchar(64) not null default 'not_checked',
                reports_status varchar(64) not null default 'not_checked',
                safe_code varchar(64) not null default 'not_checked',
                checked_at datetime,
                last_successful_at datetime
            );
            create table write_alpha_transaction_ownership (
                id integer primary key autoincrement,
                book_id integer not null,
                transaction_id varchar(64) not null,
                created_by_user_id integer,
                created_by_write_alpha boolean not null,
                created_at datetime not null,
                last_mutated_at datetime not null,
                unique(book_id, transaction_id)
            );
            """
        )
        conn.executemany(
            "insert into users "
            "(id, username, username_normalized, display_name, password_hash, is_admin, is_enabled, auth_version, created_at, updated_at) "
            "values (?, ?, ?, ?, ?, ?, ?, ?, '2026-01-01 00:00:00.000000', '2026-01-01 00:00:00.000000')",
            [
                (1, "admin", "admin", "Synthetic Admin", "admin-hash-before", 1, 1, 7),
                (2, "analyst", "analyst", "Synthetic Analyst", "analyst-hash-before", 0, 1, 3),
                (3, "disabled-user", "disabled-user", "Synthetic Disabled", "disabled-hash-before", 0, 0, 5),
            ],
        )
        conn.executemany(
            "insert into books "
            "(id, name, storage_type, uri_or_path, base_currency, is_default, is_archived, is_enabled, created_at, updated_at) "
            "values (?, ?, 'sqlite', ?, 'USD', ?, 0, ?, '2026-01-01 00:00:00.000000', '2026-01-01 00:00:00.000000')",
            [
                (10, "Synthetic Main Book", str(default_book), 1, 1),
                (20, "Synthetic Assigned Book", str(assigned_book), 0, 1),
                (30, "Synthetic Unavailable Book", str(missing_book), 0, 0),
            ],
        )
        conn.executemany(
            "insert into user_book_access (user_id, book_id, role) values (?, ?, ?)",
            [
                (1, 10, "owner"),
                (1, 20, "owner"),
                (1, 30, "owner"),
                (2, 20, "viewer"),
                (3, 20, "viewer"),
            ],
        )
        conn.executemany(
            "insert into book_health_snapshots "
            "(book_id, source_status, open_status, accounts_status, transactions_status, reports_status, safe_code, checked_at, last_successful_at) "
            "values (?, ?, ?, ?, ?, ?, ?, '2026-01-01 00:00:00.000000', '2026-01-01 00:00:00.000000')",
            [
                (10, "ready", "ready", "ready", "ready", "ready", "ready"),
                (20, "ready", "ready", "ready", "ready", "ready", "ready"),
                (30, "missing_file", "blocked", "blocked", "blocked", "blocked", "missing_file"),
            ],
        )
        conn.execute(
            "insert into audit_logs (id, user_id, book_id, action, payload_json, created_at) "
            "values (1, 1, 10, 'transaction.create', '{\"result\":\"success\"}', '2026-01-01 00:00:00.000000')"
        )
        conn.commit()

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    settings = Settings(
        app_env="test",
        app_database_url=f"sqlite:///{db_path}",
        jwt_secret="test-secret-key-for-public-readonly-upgrade-32-bytes",
        app_admin_username="admin",
        app_admin_password="new-bootstrap-password-that-must-not-replace-existing",
        gnucash_default_book_path=str(default_book),
        gnucash_book_allowed_roots=[str(tmp_path)],
        gnucash_writes_enabled=False,
    )

    run_app_metadata_migrations(engine, settings)
    run_app_metadata_migrations(engine, settings)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        users = {row["username"]: row for row in conn.execute("select * from users")}
        assert users["admin"]["password_hash"] == "admin-hash-before"
        assert users["admin"]["auth_version"] == 7
        assert users["analyst"]["password_hash"] == "analyst-hash-before"
        assert users["analyst"]["auth_version"] == 3
        assert users["analyst"]["is_enabled"] == 1
        assert users["disabled-user"]["password_hash"] == "disabled-hash-before"
        assert users["disabled-user"]["auth_version"] == 5
        assert users["disabled-user"]["is_enabled"] == 0

        books = {row["id"]: row for row in conn.execute("select * from books")}
        assert books[10]["is_default"] == 1
        assert books[10]["is_enabled"] == 1
        assert books[10]["canonical_path_hash"]
        assert books[20]["is_enabled"] == 1
        assert books[20]["canonical_path_hash"]
        assert books[30]["is_enabled"] == 0
        assert books[30]["canonical_path_hash"] is None

        assert conn.execute("select count(*) from user_book_access").fetchone()[0] == 5
        assert conn.execute("select count(*) from audit_logs where action='transaction.create'").fetchone()[0] == 1
        health = {
            row["book_id"]: row["safe_code"]
            for row in conn.execute("select book_id, safe_code from book_health_snapshots")
        }
        assert health == {10: "ready", 20: "ready", 30: "missing_file"}
        assert conn.execute("pragma user_version").fetchone()[0] == CURRENT_APP_METADATA_SCHEMA_VERSION

    engine.dispose()
