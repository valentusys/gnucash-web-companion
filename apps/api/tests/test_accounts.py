"""Tests for book-aware accounts API endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import User, Book, UserBookAccess
from app.routers.auth import get_db
from app.services.auth import hash_password

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password="testpassword123",
)


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(engine):
    return sessionmaker(bind=engine)


@pytest.fixture
def client(session_factory):
    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: TEST_SETTINGS
    app.dependency_overrides[get_db] = override_get_db

    with session_factory() as session:
        session.add(
            User(
                username="admin",
                display_name="Admin",
                password_hash=hash_password("testpassword123"),
                is_admin=True,
            )
        )
        session.commit()

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def auth_token(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "testpassword123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_book(session_factory):
    with session_factory() as session:
        book = Book(
            name="Test Book",
            storage_type="sqlite",
            uri_or_path="/data/books/test.gnucash.sqlite",
            is_default=True,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        book_id = book.id
    return book_id


@pytest.fixture
def second_book(session_factory):
    with session_factory() as session:
        book = Book(
            name="Second Book",
            storage_type="sqlite",
            uri_or_path="/data/books/second.gnucash.sqlite",
            is_default=False,
        )
        session.add(book)
        session.commit()
        book_id = book.id
    return book_id


@pytest.fixture
def viewer_user(session_factory):
    with session_factory() as session:
        user = User(
            username="viewer",
            display_name="Viewer",
            password_hash=hash_password("viewerpass"),
        )
        session.add(user)
        session.commit()
        user_id = user.id
    return user_id


@pytest.fixture
def viewer_token(client, viewer_user):
    response = client.post(
        "/auth/login",
        json={"username": "viewer", "password": "viewerpass"},
    )
    return response.json()["access_token"]


@pytest.fixture
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}


# ---------------------------------------------------------------------------
# Fake GnuCash book fixtures for monkeypatching piecash in route tests
# ---------------------------------------------------------------------------

@dataclass
class FakeCommodity:
    mnemonic: str = "SEK"


@dataclass
class FakeAccount:
    guid: str
    name: str
    type: str = "BANK"
    commodity: FakeCommodity = field(default_factory=FakeCommodity)
    parent: "FakeAccount | None" = None
    balance: Decimal = Decimal("0")
    placeholder: bool = False
    hidden: bool = False
    splits: list = field(default_factory=list)


class FakeBook:
    def __init__(self, accounts=None):
        self.accounts = accounts or []
        self.closed = False

    def close(self):
        self.closed = True


@pytest.fixture
def fake_gnucash_accounts():
    root = FakeAccount(guid="root-guid", name="Assets", type="ROOT")
    bank = FakeAccount(guid="bank-guid", name="Bank", type="ASSET", parent=root)
    checking = FakeAccount(
        guid="checking-guid",
        name="Checking",
        type="BANK",
        parent=bank,
        balance=Decimal("12345.67"),
    )
    placeholder = FakeAccount(
        guid="placeholder-guid",
        name="Hidden placeholder",
        type="EXPENSE",
        placeholder=True,
        hidden=True,
    )
    return [root, bank, checking, placeholder]


@pytest.fixture
def fake_book_path(tmp_path, monkeypatch, fake_gnucash_accounts):
    book_path = tmp_path / "test.gnucash"
    book_path.write_text("fake")

    def fake_open_book(path, readonly=False):
        return FakeBook(accounts=fake_gnucash_accounts)

    def fake_open_book_uri(*, uri_conn, readonly=False):
        return FakeBook(accounts=fake_gnucash_accounts)

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path


# ---------------------------------------------------------------------------
# Tests: GET /books
# ---------------------------------------------------------------------------

class TestListBooks:
    def test_requires_auth(self, client):
        response = client.get("/books")
        assert response.status_code == 401

    def test_returns_books_for_user(self, client, auth_headers, sample_book):
        response = client.get("/books", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        ids = [b["id"] for b in data]
        assert sample_book in ids

    def test_excludes_books_without_access(
        self, client, auth_headers, second_book
    ):
        response = client.get("/books", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        ids = [b["id"] for b in data]
        assert second_book not in ids


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}
# ---------------------------------------------------------------------------

class TestGetBook:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}")
        assert response.status_code == 401

    def test_returns_book(self, client, auth_headers, sample_book):
        response = client.get(f"/books/{sample_book}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_book
        assert data["name"] == "Test Book"

    def test_not_found(self, client, auth_headers):
        response = client.get("/books/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_access_denied_for_unauthorized_book(
        self, client, viewer_headers, sample_book, session_factory
    ):
        # viewer has no access to sample_book
        response = client.get(
            f"/books/{sample_book}", headers=viewer_headers
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/accounts
# ---------------------------------------------------------------------------

class TestListAccounts:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/accounts")
        assert response.status_code == 401

    def test_returns_accounts(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        # Update the book path to match our fake
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4
        names = [a["name"] for a in data]
        assert "Assets" in names
        assert "Checking" in names

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts", headers=viewer_headers
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/accounts/tree
# ---------------------------------------------------------------------------

class TestAccountTree:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/accounts/tree")
        assert response.status_code == 401

    def test_tree_shape(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/tree", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Root-level nodes: Assets and Hidden placeholder
        root_ids = [n["id"] for n in data]
        assert "root-guid" in root_ids
        assert "placeholder-guid" in root_ids

        # Check nesting: Assets -> Bank -> Checking
        assets = next(n for n in data if n["id"] == "root-guid")
        assert len(assets["children"]) == 1
        assert assets["children"][0]["id"] == "bank-guid"
        assert len(assets["children"][0]["children"]) == 1
        assert assets["children"][0]["children"][0]["id"] == "checking-guid"

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/tree", headers=viewer_headers
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/accounts/{account_id}
# ---------------------------------------------------------------------------

class TestGetAccount:
    def test_requires_auth(self, client, sample_book):
        response = client.get(
            f"/books/{sample_book}/accounts/some-id"
        )
        assert response.status_code == 401

    def test_returns_account(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/checking-guid",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "checking-guid"
        assert data["name"] == "Checking"
        assert data["type"] == "BANK"
        assert data["balance"] == "12345.67"
        assert data["currency"] == "SEK"
        assert data["parent_id"] == "bank-guid"

    def test_unknown_account_returns_404(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/nonexistent-guid",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/checking-guid",
            headers=viewer_headers,
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: MVP aliases  GET /accounts, /accounts/tree, /accounts/{id}
# ---------------------------------------------------------------------------

class TestMVPAliases:
    def test_list_requires_auth(self, client):
        response = client.get("/accounts")
        assert response.status_code == 401

    def test_list_returns_default_book_accounts(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get("/accounts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4

    def test_tree_requires_auth(self, client):
        response = client.get("/accounts/tree")
        assert response.status_code == 401

    def test_tree_returns_default_book_tree(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get("/accounts/tree", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        root_ids = [n["id"] for n in data]
        assert "root-guid" in root_ids

    def test_get_requires_auth(self, client):
        response = client.get("/accounts/some-id")
        assert response.status_code == 401

    def test_get_returns_default_book_account(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            "/accounts/checking-guid", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "checking-guid"
        assert data["name"] == "Checking"

    def test_get_unknown_account_returns_404(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            "/accounts/nonexistent-guid", headers=auth_headers
        )
        assert response.status_code == 404
