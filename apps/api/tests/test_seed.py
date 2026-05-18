"""Tests for default book seeding and config warning."""

import logging
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Book, User, UserBookAccess
from app.services.auth import hash_password
from app.services.seed import seed_admin_default_book_access, seed_default_book


@pytest.fixture
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


class TestSeedDefaultBook:
    def test_seeds_book_from_path(self, session):
        path = "/data/books/main.gnucash.sqlite"
        book = seed_default_book(session, path)
        assert book is not None
        assert book.name == "main"
        assert book.uri_or_path == path
        assert book.storage_type == "sqlite"
        assert book.is_default is True

    def test_seeds_idempotent(self, session):
        path = "/data/books/main.gnucash.sqlite"
        book1 = seed_default_book(session, path)
        book2 = seed_default_book(session, path)
        assert book1.id == book2.id
        count = session.query(Book).count()
        assert count == 1

    def test_seed_log_redacts_full_default_book_path(self, session, caplog):
        path = "/srv/private/customer-ledgers/main.gnucash.sqlite"

        with caplog.at_level(logging.INFO, logger="app.services.seed"):
            book = seed_default_book(session, path)

        assert book is not None
        assert "Seeded default book" in caplog.text
        assert "main.gnucash.sqlite" in caplog.text
        assert path not in caplog.text
        assert "/srv/private/customer-ledgers" not in caplog.text

    def test_seed_log_redacts_connection_uri_details(self, session, caplog):
        uri = "postgresql://ledger_user:credential-value@db.internal:5432/books/main?sslmode=require"

        with caplog.at_level(logging.INFO, logger="app.services.seed"):
            book = seed_default_book(session, uri)

        assert book is not None
        assert "Seeded default book" in caplog.text
        assert "main" in caplog.text
        assert uri not in caplog.text
        assert "credential-value" not in caplog.text
        assert "ledger_user" not in caplog.text
        assert "db.internal" not in caplog.text
        assert "sslmode" not in caplog.text

    def test_missing_path_returns_none_and_warns(self, session, caplog):
        with caplog.at_level(logging.WARNING):
            result = seed_default_book(session, None)
        assert result is None
        assert "GNUCASH_DEFAULT_BOOK_PATH" in caplog.text

    def test_empty_path_returns_none_and_warns(self, session, caplog):
        with caplog.at_level(logging.WARNING):
            result = seed_default_book(session, "")
        assert result is None
        assert "GNUCASH_DEFAULT_BOOK_PATH" in caplog.text

    def test_seeded_book_is_retrievable_as_default(self, session):
        path = "/data/books/finances.gnucash.sqlite"
        seed_default_book(session, path)
        from app.services.book_registry import BookRegistryService

        svc = BookRegistryService(session)
        default = svc.get_default_book()
        assert default is not None
        assert default.uri_or_path == path


class TestSeedAdminDefaultBookAccess:
    def test_grants_owner_access_to_first_admin_for_default_book(self, session):
        book = seed_default_book(session, "/data/books/main.gnucash.sqlite")
        admin = User(
            username="admin",
            display_name="Admin",
            password_hash=hash_password("secret"),
            is_admin=True,
        )
        session.add(admin)
        session.commit()

        access = seed_admin_default_book_access(session)

        assert access is not None
        assert access.user_id == admin.id
        assert access.book_id == book.id
        assert access.role == "owner"

    def test_admin_access_seed_is_idempotent(self, session):
        book = seed_default_book(session, "/data/books/main.gnucash.sqlite")
        admin = User(
            username="admin",
            display_name="Admin",
            password_hash=hash_password("secret"),
            is_admin=True,
        )
        session.add(admin)
        session.commit()

        access1 = seed_admin_default_book_access(session)
        access2 = seed_admin_default_book_access(session)

        assert access1.user_id == access2.user_id
        assert access1.book_id == access2.book_id
        assert session.query(UserBookAccess).count() == 1
        assert session.query(UserBookAccess).one().book_id == book.id

    def test_skips_without_default_book(self, session, caplog):
        admin = User(
            username="admin",
            display_name="Admin",
            password_hash=hash_password("secret"),
            is_admin=True,
        )
        session.add(admin)
        session.commit()

        with caplog.at_level(logging.WARNING):
            result = seed_admin_default_book_access(session)

        assert result is None
        assert "No default book configured" in caplog.text

    def test_skips_without_admin_user(self, session, caplog):
        seed_default_book(session, "/data/books/main.gnucash.sqlite")

        with caplog.at_level(logging.WARNING):
            result = seed_admin_default_book_access(session)

        assert result is None
        assert "No admin user configured" in caplog.text
