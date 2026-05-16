"""Tests for default book seeding and config warning."""

import logging
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Book
from app.services.seed import seed_default_book


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
