"""Issue #56 additive app metadata migration tests."""

from __future__ import annotations

import shutil
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.database import Base
from app.models import Book, BookHealthSnapshot
from app.services.auth import seed_admin_user
from app.services.metadata_migrations import run_app_metadata_migrations
from app.services.seed import seed_admin_default_book_access, seed_default_book

FIXTURE_BOOK = Path(__file__).parent / "fixtures" / "test-book.gnucash.sqlite"


def _settings(tmp_path: Path, allowed_root: Path | None = None, default_path: str = "") -> Settings:
    return Settings(
        app_env="test",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_default_book_path=default_path,
        gnucash_book_allowed_roots=[str(allowed_root or tmp_path)],
        jwt_secret="test-secret-key-for-issue56-migration-32-bytes",
        app_admin_username="admin",
        app_admin_password="testpassword123",
    )


def _create_old_metadata_schema(engine) -> None:
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


def test_empty_first_run_default_settings_do_not_seed_phantom_missing_book(tmp_path, monkeypatch):
    settings = Settings(
        app_env="test",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        jwt_secret="test-secret-key-for-empty-first-run-32-bytes",
        app_admin_username="admin",
        app_admin_password="testpassword123",
    )
    assert settings.gnucash_default_book_path == ""

    engine = create_engine(settings.app_database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    run_app_metadata_migrations(engine, settings)
    SessionLocal = sessionmaker(bind=engine)
    monkeypatch.setattr("app.services.auth.get_settings", lambda: settings)

    with SessionLocal() as session:
        assert seed_default_book(session, settings.gnucash_default_book_path) is None
        seed_admin_user(session)
        assert seed_admin_default_book_access(session) is None
        assert session.query(Book).count() == 0
        assert session.query(BookHealthSnapshot).count() == 0


def test_additive_migration_preserves_legacy_rows_and_is_restart_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}", connect_args={"check_same_thread": False})
    _create_old_metadata_schema(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "insert into books "
                "(id, name, storage_type, uri_or_path, base_currency, is_default, is_archived, created_at) "
                "values (1, 'Legacy Missing', 'sqlite', '/private/missing.gnucash.sqlite', 'USD', 1, 0, '2026-01-01T00:00:00+00:00')"
            )
        )
        conn.execute(
            text(
                "insert into users (id, username, display_name, password_hash, is_admin, created_at) "
                "values (1, 'admin', 'Admin', 'hash', 1, '2026-01-01T00:00:00+00:00')"
            )
        )
        conn.execute(text("insert into user_book_access (user_id, book_id, role) values (1, 1, 'owner')"))

    settings = _settings(tmp_path, allowed_root=tmp_path / "books")
    run_app_metadata_migrations(engine, settings)
    run_app_metadata_migrations(engine, settings)

    inspector = inspect(engine)
    book_columns = {column["name"] for column in inspector.get_columns("books")}
    assert {"canonical_path", "canonical_path_hash", "is_enabled", "updated_at"}.issubset(book_columns)
    assert "book_health_snapshots" in inspector.get_table_names()

    with engine.connect() as conn:
        row = conn.execute(text("select * from books where id=1")).mappings().one()
        assert row["name"] == "Legacy Missing"
        assert row["uri_or_path"] == "/private/missing.gnucash.sqlite"
        assert row["canonical_path"] is None
        assert row["canonical_path_hash"] is None
        assert row["is_enabled"] == 0
        assert row["updated_at"] is not None
        assert conn.execute(text("select count(*) from user_book_access")).scalar_one() == 1
        snapshots = conn.execute(text("select * from book_health_snapshots where book_id=1")).mappings().all()
        assert len(snapshots) == 1
        assert snapshots[0]["source_status"] == "not_checked"
        assert snapshots[0]["open_status"] == "not_checked"
        assert snapshots[0]["safe_code"] == "not_checked"


def test_additive_migration_canonicalizes_safe_legacy_book_under_allowed_root(tmp_path):
    allowed_root = tmp_path / "books"
    allowed_root.mkdir()
    book_path = allowed_root / "legacy.gnucash.sqlite"
    shutil.copy2(FIXTURE_BOOK, book_path)
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy-valid.db'}", connect_args={"check_same_thread": False})
    _create_old_metadata_schema(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "insert into books "
                "(id, name, storage_type, uri_or_path, base_currency, is_default, is_archived, created_at) "
                "values (1, 'Legacy Valid', 'sqlite', :path, 'USD', 1, 0, '2026-01-01T00:00:00+00:00')"
            ),
            {"path": str(book_path)},
        )

    run_app_metadata_migrations(engine, _settings(tmp_path, allowed_root=allowed_root))

    with engine.connect() as conn:
        row = conn.execute(text("select * from books where id=1")).mappings().one()
        assert row["canonical_path"] == str(book_path.resolve(strict=True))
        assert isinstance(row["canonical_path_hash"], str)
        assert len(row["canonical_path_hash"]) == 64
        assert row["is_enabled"] == 1
        snapshot = conn.execute(text("select * from book_health_snapshots where book_id=1")).mappings().one()
        assert snapshot["source_status"] == "not_checked"
        assert snapshot["checked_at"] is None


def test_fresh_schema_contains_issue56_private_metadata_and_typed_health_snapshot(tmp_path):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        book = Book(name="Fresh", storage_type="sqlite", uri_or_path="/data/books/fresh.gnucash.sqlite")
        session.add(book)
        session.commit()
        assert book.is_enabled is True
        assert book.updated_at is not None
        assert book.canonical_path is None
        assert book.canonical_path_hash is None
        snapshot = BookHealthSnapshot(book_id=book.id)
        session.add(snapshot)
        session.commit()
        assert snapshot.source_status == "not_checked"
        assert snapshot.open_status == "not_checked"
        assert snapshot.accounts_status == "not_checked"
        assert snapshot.transactions_status == "not_checked"
        assert snapshot.reports_status == "not_checked"
        assert snapshot.safe_code == "not_checked"
