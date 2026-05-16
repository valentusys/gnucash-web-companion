"""Tests for BookRegistryService and BookAccessService."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User, Book, UserBookAccess
from app.services.book_registry import BookRegistryService
from app.services.book_access import BookAccessService, AccessDenied


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


@pytest.fixture
def sample_book(session):
    book = Book(
        name="Default Book",
        storage_type="sqlite",
        uri_or_path="/data/books/default.gnucash.sqlite",
        is_default=True,
    )
    session.add(book)
    session.commit()
    return book


@pytest.fixture
def second_book(session):
    book = Book(
        name="Archive Book",
        storage_type="sqlite",
        uri_or_path="/data/books/archive.gnucash.sqlite",
        is_default=False,
        is_archived=True,
    )
    session.add(book)
    session.commit()
    return book


@pytest.fixture
def sample_user(session):
    user = User(username="alice", display_name="Alice", password_hash="pw")
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def viewer_user(session):
    user = User(username="bob", display_name="Bob", password_hash="pw")
    session.add(user)
    session.commit()
    return user


class TestBookRegistryService:
    def test_get_default_book(self, session, sample_book):
        svc = BookRegistryService(session)
        result = svc.get_default_book()
        assert result is not None
        assert result.id == sample_book.id
        assert result.name == "Default Book"

    def test_get_default_book_none_when_no_default(self, session):
        svc = BookRegistryService(session)
        result = svc.get_default_book()
        assert result is None

    def test_list_books_for_user_owner(self, session, sample_book, sample_user):
        access = UserBookAccess(
            user_id=sample_user.id, book_id=sample_book.id, role="owner"
        )
        session.add(access)
        session.commit()

        svc = BookRegistryService(session)
        books = svc.list_books_for_user(sample_user)
        assert len(books) == 1
        assert books[0].id == sample_book.id

    def test_list_books_for_user_viewer(self, session, sample_book, viewer_user):
        access = UserBookAccess(
            user_id=viewer_user.id, book_id=sample_book.id, role="viewer"
        )
        session.add(access)
        session.commit()

        svc = BookRegistryService(session)
        books = svc.list_books_for_user(viewer_user)
        assert len(books) == 1

    def test_list_books_for_user_no_access(self, session, sample_book, sample_user):
        svc = BookRegistryService(session)
        books = svc.list_books_for_user(sample_user)
        assert books == []

    def test_list_books_excludes_archived(self, session, sample_book, second_book, sample_user):
        access1 = UserBookAccess(
            user_id=sample_user.id, book_id=sample_book.id, role="owner"
        )
        access2 = UserBookAccess(
            user_id=sample_user.id, book_id=second_book.id, role="owner"
        )
        session.add_all([access1, access2])
        session.commit()

        svc = BookRegistryService(session)
        books = svc.list_books_for_user(sample_user)
        assert len(books) == 1
        assert books[0].id == sample_book.id

    def test_get_book_by_id(self, session, sample_book):
        svc = BookRegistryService(session)
        result = svc.get_book(sample_book.id)
        assert result is not None
        assert result.name == "Default Book"

    def test_get_book_not_found(self, session):
        svc = BookRegistryService(session)
        result = svc.get_book(9999)
        assert result is None


class TestBookAccessService:
    def test_get_role(self, session, sample_book, sample_user):
        access = UserBookAccess(
            user_id=sample_user.id, book_id=sample_book.id, role="owner"
        )
        session.add(access)
        session.commit()

        svc = BookAccessService(session)
        role = svc.get_role(sample_user, sample_book)
        assert role == "owner"

    def test_get_role_none(self, session, sample_book, sample_user):
        svc = BookAccessService(session)
        role = svc.get_role(sample_user, sample_book)
        assert role is None

    def test_assert_can_view_owner(self, session, sample_book, sample_user):
        access = UserBookAccess(
            user_id=sample_user.id, book_id=sample_book.id, role="owner"
        )
        session.add(access)
        session.commit()

        svc = BookAccessService(session)
        svc.assert_can_view(sample_user, sample_book)  # should not raise

    def test_assert_can_view_viewer(self, session, sample_book, viewer_user):
        access = UserBookAccess(
            user_id=viewer_user.id, book_id=sample_book.id, role="viewer"
        )
        session.add(access)
        session.commit()

        svc = BookAccessService(session)
        svc.assert_can_view(viewer_user, sample_book)  # should not raise

    def test_assert_can_view_denied(self, session, sample_book, sample_user):
        svc = BookAccessService(session)
        with pytest.raises(AccessDenied):
            svc.assert_can_view(sample_user, sample_book)

    def test_assert_can_edit_owner(self, session, sample_book, sample_user):
        access = UserBookAccess(
            user_id=sample_user.id, book_id=sample_book.id, role="owner"
        )
        session.add(access)
        session.commit()

        svc = BookAccessService(session)
        svc.assert_can_edit(sample_user, sample_book)  # should not raise

    def test_assert_can_edit_editor(self, session, sample_book, sample_user):
        access = UserBookAccess(
            user_id=sample_user.id, book_id=sample_book.id, role="editor"
        )
        session.add(access)
        session.commit()

        svc = BookAccessService(session)
        svc.assert_can_edit(sample_user, sample_book)  # should not raise

    def test_assert_can_edit_viewer_denied(self, session, sample_book, viewer_user):
        access = UserBookAccess(
            user_id=viewer_user.id, book_id=sample_book.id, role="viewer"
        )
        session.add(access)
        session.commit()

        svc = BookAccessService(session)
        with pytest.raises(AccessDenied):
            svc.assert_can_edit(viewer_user, sample_book)

    def test_assert_can_edit_no_access_denied(self, session, sample_book, sample_user):
        svc = BookAccessService(session)
        with pytest.raises(AccessDenied):
            svc.assert_can_edit(sample_user, sample_book)
