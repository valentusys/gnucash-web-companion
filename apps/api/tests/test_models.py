"""Tests for app metadata DB models."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User, Book, UserBookAccess, AuditLog, WriteAlphaTransactionOwnership


@pytest.fixture
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestUserModel:
    def test_create_user(self, session):
        user = User(
            username="alice",
            display_name="Alice",
            password_hash="hashed_pw",
            is_admin=True,
        )
        session.add(user)
        session.commit()
        assert user.id is not None
        assert user.username == "alice"
        assert user.is_admin is True

    def test_user_default_is_admin_false(self, session):
        user = User(
            username="bob",
            display_name="Bob",
            password_hash="hashed_pw",
        )
        session.add(user)
        session.commit()
        assert user.is_admin is False

    def test_user_created_at_auto(self, session):
        user = User(
            username="carol",
            display_name="Carol",
            password_hash="hashed_pw",
        )
        session.add(user)
        session.commit()
        assert user.created_at is not None


class TestBookModel:
    def test_create_book(self, session):
        book = Book(
            name="My Finances",
            storage_type="sqlite",
            uri_or_path="/data/books/main.gnucash.sqlite",
            base_currency="USD",
            is_default=True,
        )
        session.add(book)
        session.commit()
        assert book.id is not None
        assert book.name == "My Finances"
        assert book.is_default is True
        assert book.is_archived is False

    def test_book_defaults(self, session):
        book = Book(
            name="Test Book",
            storage_type="sqlite",
            uri_or_path="/data/books/test.gnucash.sqlite",
        )
        session.add(book)
        session.commit()
        assert book.is_default is False
        assert book.is_archived is False
        assert book.base_currency is None

    def test_book_created_at_auto(self, session):
        book = Book(
            name="Timed Book",
            storage_type="sqlite",
            uri_or_path="/data/books/timed.gnucash.sqlite",
        )
        session.add(book)
        session.commit()
        assert book.created_at is not None


class TestUserBookAccessModel:
    def test_create_access(self, session):
        user = User(username="alice", display_name="Alice", password_hash="pw")
        book = Book(name="B", storage_type="sqlite", uri_or_path="/b.gnucash.sqlite")
        session.add_all([user, book])
        session.commit()

        access = UserBookAccess(user_id=user.id, book_id=book.id, role="owner")
        session.add(access)
        session.commit()
        assert access.user_id == user.id
        assert access.book_id == book.id
        assert access.role == "owner"

    def test_viewer_role(self, session):
        user = User(username="viewer", display_name="Viewer", password_hash="pw")
        book = Book(name="B", storage_type="sqlite", uri_or_path="/b.gnucash.sqlite")
        session.add_all([user, book])
        session.commit()

        access = UserBookAccess(user_id=user.id, book_id=book.id, role="viewer")
        session.add(access)
        session.commit()
        assert access.role == "viewer"

    def test_editor_role(self, session):
        user = User(username="editor", display_name="Editor", password_hash="pw")
        book = Book(name="B", storage_type="sqlite", uri_or_path="/b.gnucash.sqlite")
        session.add_all([user, book])
        session.commit()

        access = UserBookAccess(user_id=user.id, book_id=book.id, role="editor")
        session.add(access)
        session.commit()
        assert access.role == "editor"

    def test_rejects_invalid_role(self, session):
        user = User(username="invalid", display_name="Invalid", password_hash="pw")
        book = Book(name="B", storage_type="sqlite", uri_or_path="/b.gnucash.sqlite")
        session.add_all([user, book])
        session.commit()

        session.add(UserBookAccess(user_id=user.id, book_id=book.id, role="admin"))
        with pytest.raises(IntegrityError):
            session.commit()


class TestAuditLogModel:
    def test_create_audit_log(self, session):
        user = User(username="alice", display_name="Alice", password_hash="pw")
        book = Book(name="B", storage_type="sqlite", uri_or_path="/b.gnucash.sqlite")
        session.add_all([user, book])
        session.commit()

        log = AuditLog(
            user_id=user.id,
            book_id=book.id,
            action="view_accounts",
            payload_json='{"filter": "all"}',
        )
        session.add(log)
        session.commit()
        assert log.id is not None
        assert log.action == "view_accounts"
        assert log.created_at is not None


class TestWriteAlphaTransactionOwnershipModel:
    def test_create_write_alpha_ownership_marker(self, session):
        user = User(username="writer", display_name="Writer", password_hash="pw")
        book = Book(name="B", storage_type="sqlite", uri_or_path="/b.gnucash.sqlite")
        session.add_all([user, book])
        session.commit()

        marker = WriteAlphaTransactionOwnership(
            book_id=book.id,
            transaction_id="phase-243-synthetic-guid",
            created_by_user_id=user.id,
            created_by_write_alpha=True,
        )
        session.add(marker)
        session.commit()

        assert marker.id is not None
        assert marker.book_id == book.id
        assert marker.transaction_id == "phase-243-synthetic-guid"
        assert marker.created_by_user_id == user.id
        assert marker.created_by_write_alpha is True
        assert marker.created_at is not None
        assert marker.last_mutated_at is not None

    def test_write_alpha_ownership_marker_is_book_transaction_unique(self, session):
        user = User(username="writer2", display_name="Writer", password_hash="pw")
        book = Book(name="B", storage_type="sqlite", uri_or_path="/b.gnucash.sqlite")
        session.add_all([user, book])
        session.commit()

        session.add(
            WriteAlphaTransactionOwnership(
                book_id=book.id,
                transaction_id="duplicate-synthetic-guid",
                created_by_user_id=user.id,
            )
        )
        session.commit()
        session.add(
            WriteAlphaTransactionOwnership(
                book_id=book.id,
                transaction_id="duplicate-synthetic-guid",
                created_by_user_id=user.id,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
