"""Tests for multi-book access filtering on GET /books and GET /books/{book_id}.

Validates that users can only see books they have explicit UserBookAccess to,
and that the book-aware data routes enforce the same access control.
"""

from __future__ import annotations

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
def user_a(session_factory):
    with session_factory() as session:
        user = User(
            username="alice",
            display_name="Alice",
            password_hash=hash_password("alicepass"),
        )
        session.add(user)
        session.commit()
        user_id = user.id
    return user_id


@pytest.fixture
def user_b(session_factory):
    with session_factory() as session:
        user = User(
            username="bob",
            display_name="Bob",
            password_hash=hash_password("bobpass"),
        )
        session.add(user)
        session.commit()
        user_id = user.id
    return user_id


@pytest.fixture
def book_a(session_factory):
    with session_factory() as session:
        book = Book(
            name="Alice Book",
            storage_type="sqlite",
            uri_or_path="/data/books/alice.gnucash.sqlite",
            is_default=False,
        )
        session.add(book)
        session.commit()
        book_id = book.id
    return book_id


@pytest.fixture
def book_b(session_factory):
    with session_factory() as session:
        book = Book(
            name="Bob Book",
            storage_type="sqlite",
            uri_or_path="/data/books/bob.gnucash.sqlite",
            is_default=False,
        )
        session.add(book)
        session.commit()
        book_id = book.id
    return book_id


@pytest.fixture
def archived_book(session_factory):
    with session_factory() as session:
        book = Book(
            name="Archived Alice Book",
            storage_type="sqlite",
            uri_or_path="/data/books/archived-alice.gnucash.sqlite",
            is_default=False,
            is_archived=True,
        )
        session.add(book)
        session.commit()
        book_id = book.id
    return book_id


@pytest.fixture
def setup_access(session_factory, user_a, user_b, book_a, book_b, archived_book):
    with session_factory() as session:
        session.add(UserBookAccess(user_id=user_a, book_id=book_a, role="owner"))
        session.add(UserBookAccess(user_id=user_b, book_id=book_b, role="owner"))
        session.add(UserBookAccess(user_id=user_a, book_id=archived_book, role="owner"))
        session.commit()


@pytest.fixture
def token_a(client, user_a, setup_access):
    response = client.post(
        "/auth/login",
        json={"username": "alice", "password": "alicepass"},
    )
    return response.json()["access_token"]


@pytest.fixture
def token_b(client, user_b, setup_access):
    response = client.post(
        "/auth/login",
        json={"username": "bob", "password": "bobpass"},
    )
    return response.json()["access_token"]


@pytest.fixture
def headers_a(token_a):
    return {"Authorization": f"Bearer {token_a}"}


@pytest.fixture
def headers_b(token_b):
    return {"Authorization": f"Bearer {token_b}"}


BOOK_AWARE_READ_ONLY_ROUTES = [
    "/books/{book_id}/accounts",
    "/books/{book_id}/accounts/tree",
    "/books/{book_id}/accounts/checking",
    "/books/{book_id}/accounts/checking/transactions",
    "/books/{book_id}/transactions",
    "/books/{book_id}/transactions/export",
    "/books/{book_id}/transactions/tx-1",
    "/books/{book_id}/reports/summary",
    "/books/{book_id}/reports/cashflow",
    "/books/{book_id}/reports/expenses-by-account",
    "/books/{book_id}/reports/recent-transactions",
]


class TestMultiBookAccessFiltering:
    def test_user_a_sees_only_active_book_a(
        self, client, headers_a, book_a, book_b, archived_book
    ):
        response = client.get("/books", headers=headers_a)
        assert response.status_code == 200
        data = response.json()
        ids = [b["id"] for b in data]
        assert book_a in ids
        assert book_b not in ids
        assert archived_book not in ids

    def test_user_b_sees_only_book_b(self, client, headers_b, book_a, book_b):
        response = client.get("/books", headers=headers_b)
        assert response.status_code == 200
        data = response.json()
        ids = [b["id"] for b in data]
        assert book_b in ids
        assert book_a not in ids

    def test_user_a_cannot_access_book_b_detail(self, client, headers_b, book_a):
        # bob's token to access bob's book should work
        response = client.get(f"/books/{book_a}", headers=headers_b)
        assert response.status_code == 403

    def test_user_b_cannot_access_book_a_detail(self, client, headers_a, book_b):
        # alice's token to access alice's book should work
        response = client.get(f"/books/{book_b}", headers=headers_a)
        assert response.status_code == 403

    def test_user_a_can_access_own_book_detail(self, client, headers_a, book_a):
        response = client.get(f"/books/{book_a}", headers=headers_a)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book_a
        assert data["name"] == "Alice Book"

    def test_book_metadata_operator_guidance_is_app_metadata_only(self, client, headers_a, book_a):
        response = client.get(f"/books/{book_a}", headers=headers_a)
        assert response.status_code == 200
        data = response.json()

        assert data["management_actions"] == []
        assert data["operator_guidance"] == {
            "metadata_source": "app_metadata_db",
            "data_access": "gnucash_not_opened_for_listing",
            "read_only_default": True,
            "private_path_redacted": True,
            "storage_type_label": "Read-only sqlite GnuCash book metadata",
            "unsupported_management_actions": [
                "book_upload",
                "book_delete",
                "default_book_change",
                "registry_edit",
            ],
            "message": (
                "This MVP lists configured accessible book metadata only. "
                "Upload, delete, default-book changes, and registry editing are intentionally unavailable."
            ),
        }
        assert "uri_or_path" not in data
        assert data["access_status"] == "accessible"
        assert data["storage_diagnostics"] == {
            "status": "missing_file",
            "configured": True,
            "checked": True,
            "safe_summary": "A configured local SQLite book path is present, but the file was not found from this runtime.",
            "safe_next_actions": [
                "Verify the configured book is mounted on the host/container.",
                "Check the app metadata database and deployment volumes without uploading or browsing files from the web UI.",
            ],
        }

    def test_user_b_can_access_own_book_detail(self, client, headers_b, book_b):
        response = client.get(f"/books/{book_b}", headers=headers_b)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book_b
        assert data["name"] == "Bob Book"

    def test_default_book_marker_is_metadata_only(self, client, session_factory, headers_a, book_a):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_a).one()
            book.is_default = True
            session.commit()

        response = client.get(f"/books/{book_a}", headers=headers_a)
        assert response.status_code == 200
        data = response.json()
        assert data["is_default"] is True
        assert data["access_status"] == "accessible"
        assert data["status"] == "missing_file"
        assert "uri_or_path" not in data

    def test_existing_local_book_reports_available_without_opening_gnucash(
        self, client, session_factory, headers_a, book_a, tmp_path
    ):
        book_path = tmp_path / "synthetic.gnucash.sqlite"
        book_path.write_text("synthetic metadata probe only")
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_a).one()
            book.uri_or_path = str(book_path)
            session.commit()

        response = client.get(f"/books/{book_a}", headers=headers_a)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "available"
        assert data["storage_diagnostics"]["checked"] is True
        assert data["storage_diagnostics"]["configured"] is True
        assert "uri_or_path" not in data

    def test_unconfigured_book_reports_not_configured_without_private_path(
        self, client, session_factory, headers_a, book_a
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_a).one()
            book.uri_or_path = ""
            session.commit()

        response = client.get(f"/books/{book_a}", headers=headers_a)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_configured"
        assert data["storage_diagnostics"] == {
            "status": "not_configured",
            "configured": False,
            "checked": True,
            "safe_summary": "No book location is configured in app metadata.",
            "safe_next_actions": [
                "Check the app metadata database and deployment configuration for this book entry.",
                "Do not upload or browse GnuCash files from the web UI; configure storage from the host side.",
            ],
        }
        assert "uri_or_path" not in data

    def test_uri_book_reports_remote_or_unchecked_without_opening_gnucash(
        self, client, session_factory, headers_a, book_a
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_a).one()
            book.uri_or_path = "postgresql://example.invalid/book"
            session.commit()

        response = client.get(f"/books/{book_a}", headers=headers_a)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "remote_or_unchecked"
        assert data["storage_diagnostics"]["configured"] is True
        assert data["storage_diagnostics"]["checked"] is False
        assert "uri_or_path" not in data

    def test_archived_book_detail_is_not_viewable_even_with_access(
        self, client, headers_a, archived_book
    ):
        response = client.get(f"/books/{archived_book}", headers=headers_a)
        assert response.status_code == 404
        assert response.json()["detail"] == "Book not found"

    @pytest.mark.parametrize("route", BOOK_AWARE_READ_ONLY_ROUTES)
    def test_unauthorized_book_is_blocked_for_every_read_only_route_family(
        self, client, headers_a, book_b, route
    ):
        response = client.get(route.format(book_id=book_b), headers=headers_a)
        assert response.status_code == 403
        assert response.json()["detail"] == "Book access denied"

    @pytest.mark.parametrize("route", BOOK_AWARE_READ_ONLY_ROUTES)
    def test_archived_book_is_hidden_for_every_read_only_route_family(
        self, client, headers_a, archived_book, route
    ):
        response = client.get(route.format(book_id=archived_book), headers=headers_a)
        assert response.status_code == 404
        assert response.json()["detail"] == "Book not found"

    def test_user_with_no_access_sees_empty_list(self, client, session_factory, book_a, book_b):
        with session_factory() as session:
            user = User(
                username="carol",
                display_name="Carol",
                password_hash=hash_password("carolpass"),
            )
            session.add(user)
            session.commit()

        response = client.post(
            "/auth/login",
            json={"username": "carol", "password": "carolpass"},
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/books", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_shared_access_both_users_see_shared_book(
        self, client, session_factory, setup_access, user_a, user_b, book_a
    ):
        with session_factory() as session:
            session.add(UserBookAccess(user_id=user_b, book_id=book_a, role="viewer"))
            session.commit()

        # alice (owner) sees book_a
        response_a = client.post(
            "/auth/login",
            json={"username": "alice", "password": "alicepass"},
        )
        headers_a2 = {"Authorization": f"Bearer {response_a.json()['access_token']}"}

        response = client.get("/books", headers=headers_a2)
        ids = [b["id"] for b in response.json()]
        assert book_a in ids

        # bob (viewer) also sees book_a
        response_b = client.post(
            "/auth/login",
            json={"username": "bob", "password": "bobpass"},
        )
        headers_b2 = {"Authorization": f"Bearer {response_b.json()['access_token']}"}

        response = client.get("/books", headers=headers_b2)
        ids = [b["id"] for b in response.json()]
        assert book_a in ids
