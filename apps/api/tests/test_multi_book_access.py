"""Tests for multi-book access filtering on GET /books and GET /books/{book_id}.

Validates that users can only see books they have explicit UserBookAccess to,
and that the book-aware data routes enforce the same access control.
"""

from __future__ import annotations

import sqlite3
import shutil
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import User, Book, BookHealthSnapshot, UserBookAccess
from app.routers.auth import get_db
from app.services.auth import hash_password

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password="testpassword123",
    gnucash_book_allowed_roots=[tempfile.gettempdir(), "/tmp", "/var/tmp", "/data/books"],
)

FIXTURE_BOOK = Path(__file__).parent / "fixtures" / "test-book.gnucash.sqlite"


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
        session.flush()
        _add_health_snapshot(session, book, "missing_file")
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
        session.flush()
        _add_health_snapshot(session, book, "missing_file")
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
        session.flush()
        _add_health_snapshot(session, book, "missing_file")
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


@pytest.fixture
def admin_headers(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "testpassword123"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}



def _create_minimal_gnucash_sqlite(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("create table versions (table_name text primary key, table_version integer not null)")
        conn.executemany(
            "insert into versions (table_name, table_version) values (?, ?)",
            [("Gnucash", 3_000_000), ("Gnucash-Resave", 19_920)],
        )
        conn.execute("create table accounts (guid text primary key, name text)")
        conn.execute("create table transactions (guid text primary key, description text)")
        conn.execute("create table splits (guid text primary key, memo text)")
        conn.execute("create table commodities (guid text primary key, fullname text)")
        conn.execute("create table books (guid text primary key, root_account_guid text)")


def _add_health_snapshot(session, book: Book, safe_code: str = "ready") -> None:
    session.add(
        BookHealthSnapshot(
            book_id=book.id,
            source_status="ready" if safe_code == "ready" else safe_code,
            open_status="ready" if safe_code == "ready" else "not_checked",
            accounts_status="ready" if safe_code == "ready" else "not_checked",
            transactions_status="ready" if safe_code == "ready" else "not_checked",
            reports_status="ready" if safe_code == "ready" else "not_checked",
            safe_code=safe_code,
        )
    )


def _preflight_register_payload(client: TestClient, headers: dict[str, str], book_path: Path, **overrides):
    payload = {
        "name": "Registered Copy",
        "storage_type": "sqlite",
        "uri_or_path": str(book_path),
        "base_currency": "USD",
        "make_default": False,
    }
    payload.update(overrides)
    preflight = client.post("/books/preflight", headers=headers, json=payload)
    assert preflight.status_code == 200
    payload["preflight_token"] = preflight.json()["preflight_token"]
    return payload

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
    (
        "/books/{book_id}/reports/comparison?date_from=2026-07-02&date_to=2026-12-30"
        "&comparison_mode=previous_equivalent"
        "&comparison_date_from=2026-01-01&comparison_date_to=2026-07-01"
    ),
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
                "book_file_delete",
                "book_file_edit",
            ],
            "message": (
                "This MVP lists configured accessible book metadata only. "
                "Upload, file delete, accounting-data edits, and direct file browsing are intentionally unavailable. "
                "Admin registry actions are metadata-only."
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

    def test_existing_local_book_reports_available_without_opening_accounting_values(
        self, client, session_factory, headers_a, book_a, tmp_path
    ):
        book_path = tmp_path / "synthetic.gnucash.sqlite"
        _create_minimal_gnucash_sqlite(book_path)
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_a).one()
            book.uri_or_path = str(book_path)
            book.health_snapshot.safe_code = "ready"
            book.health_snapshot.source_status = "ready"
            book.health_snapshot.open_status = "ready"
            book.health_snapshot.accounts_status = "ready"
            book.health_snapshot.transactions_status = "ready"
            book.health_snapshot.reports_status = "ready"
            session.commit()

        response = client.get(f"/books/{book_a}", headers=headers_a)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "available"
        assert data["storage_diagnostics"]["checked"] is True
        assert data["storage_diagnostics"]["configured"] is True
        assert data["can_open_read_only_views"] is True
        assert "uri_or_path" not in data

    def test_existing_local_non_gnucash_sqlite_reports_safe_unavailable_diagnostic(
        self, client, session_factory, headers_a, book_a, tmp_path
    ):
        private_path = tmp_path / "plain-private-copy.gnucash.sqlite"
        with sqlite3.connect(private_path) as conn:
            conn.execute("create table unrelated (id integer primary key)")
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_a).one()
            book.uri_or_path = str(private_path)
            book.health_snapshot.safe_code = "invalid_gnucash_schema"
            book.health_snapshot.source_status = "invalid_gnucash_schema"
            session.commit()

        response = client.get(f"/books/{book_a}", headers=headers_a)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "invalid_gnucash_schema"
        assert data["status_severity"] == "action_required"
        assert data["can_open_read_only_views"] is False
        assert str(private_path) not in str(data)
        assert data["storage_diagnostics"] == {
            "status": "invalid_gnucash_schema",
            "configured": True,
            "checked": True,
            "safe_summary": "A configured local SQLite book path is present, but it does not look like a readable GnuCash SQLite book.",
            "safe_next_actions": [
                "Verify the configured file is a copied/test GnuCash SQLite book mounted from the host.",
                "Do not upload or browse private books from the web UI; fix the host-side metadata or mount.",
            ],
        }

    def test_invalid_gnucash_schema_book_is_blocked_before_readonly_data_open(
        self, client, session_factory, headers_a, book_a, tmp_path
    ):
        private_path = tmp_path / "plain-private-copy.gnucash.sqlite"
        with sqlite3.connect(private_path) as conn:
            conn.execute("create table unrelated (id integer primary key)")
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_a).one()
            book.uri_or_path = str(private_path)
            book.health_snapshot.safe_code = "invalid_gnucash_schema"
            book.health_snapshot.source_status = "invalid_gnucash_schema"
            session.commit()

        response = client.get(f"/books/{book_a}/accounts", headers=headers_a)
        assert response.status_code == 503
        assert response.json()["detail"] == "Configured GnuCash book storage is not a readable SQLite GnuCash book."
        assert str(private_path) not in response.json()["detail"]

    def test_unconfigured_book_reports_not_configured_without_private_path(
        self, client, session_factory, headers_a, book_a
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_a).one()
            book.uri_or_path = ""
            book.health_snapshot.safe_code = "not_configured"
            book.health_snapshot.source_status = "not_configured"
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
            book.health_snapshot.safe_code = "remote_or_unchecked"
            book.health_snapshot.source_status = "not_checked"
            session.commit()

        response = client.get(f"/books/{book_a}", headers=headers_a)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "remote_or_unchecked"
        assert data["storage_diagnostics"]["configured"] is True
        assert data["storage_diagnostics"]["checked"] is False
        assert "uri_or_path" not in data

    def test_admin_can_register_existing_local_sqlite_book_metadata_only(
        self, client, session_factory, admin_headers, tmp_path
    ):
        book_path = tmp_path / "registered-copy.gnucash.sqlite"
        shutil.copy2(FIXTURE_BOOK, book_path)
        payload = _preflight_register_payload(
            client,
            admin_headers,
            book_path,
            name="Registered Copy",
            make_default=True,
        )

        response = client.post(
            "/books",
            headers=admin_headers,
            json=payload,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Registered Copy"
        assert data["base_currency"] == "USD"
        assert data["is_default"] is True
        assert data["status"] == "available"
        assert data["access_role"] == "owner"
        assert data["management_actions"] == ["set_default", "remove_from_registry"]
        assert "uri_or_path" not in data

        with session_factory() as session:
            book = session.query(Book).filter(Book.id == data["id"]).one()
            assert book.uri_or_path == str(book_path)
            assert book.is_default is True
            access = (
                session.query(UserBookAccess)
                .filter(UserBookAccess.book_id == book.id, UserBookAccess.role == "owner")
                .one()
            )
            admin = session.query(User).filter(User.username == "admin").one()
            assert access.user_id == admin.id

    def test_non_admin_cannot_register_book_metadata(self, client, headers_a, tmp_path):
        book_path = tmp_path / "viewer-copy.gnucash.sqlite"
        _create_minimal_gnucash_sqlite(book_path)

        response = client.post(
            "/books",
            headers=headers_a,
            json={
                "name": "Viewer Attempt",
                "storage_type": "sqlite",
                "uri_or_path": str(book_path),
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Admin privileges are required for book registry management."

    def test_register_book_rejects_non_sqlite_file_without_storing_private_path(
        self, client, session_factory, admin_headers, tmp_path
    ):
        private_path = tmp_path / "not-sqlite-private-copy.gnucash.sqlite"
        private_path.write_text("not sqlite")

        response = client.post(
            "/books",
            headers=admin_headers,
            json={
                "name": "Not SQLite",
                "storage_type": "sqlite",
                "uri_or_path": str(private_path),
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "missing_preflight_token"
        assert str(private_path) not in response.text
        with session_factory() as session:
            assert session.query(Book).filter(Book.name == "Not SQLite").first() is None

    def test_register_book_rejects_sqlite_without_gnucash_tables_without_private_path(
        self, client, session_factory, admin_headers, tmp_path
    ):
        private_path = tmp_path / "plain-private-copy.privatecopy"
        with sqlite3.connect(private_path) as conn:
            conn.execute("create table unrelated (id integer primary key)")

        response = client.post(
            "/books",
            headers=admin_headers,
            json={
                "name": "Plain SQLite",
                "storage_type": "sqlite",
                "uri_or_path": str(private_path),
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "missing_preflight_token"
        assert str(private_path) not in response.text
        with session_factory() as session:
            assert session.query(Book).filter(Book.name == "Plain SQLite").first() is None

    def test_register_book_rejects_missing_local_sqlite_without_storing_private_path(
        self, client, session_factory, admin_headers, tmp_path
    ):
        missing_path = tmp_path / "missing-private-copy.gnucash.sqlite"

        response = client.post(
            "/books",
            headers=admin_headers,
            json={
                "name": "Missing Copy",
                "storage_type": "sqlite",
                "uri_or_path": str(missing_path),
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "missing_preflight_token"
        assert str(missing_path) not in response.text
        with session_factory() as session:
            assert session.query(Book).filter(Book.name == "Missing Copy").first() is None

    def test_admin_can_set_default_book_without_exposing_private_path(
        self, client, session_factory, admin_headers, book_a, book_b
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_b).one()
            book.health_snapshot.safe_code = "ready"
            book.health_snapshot.source_status = "ready"
            book.health_snapshot.open_status = "ready"
            book.health_snapshot.accounts_status = "ready"
            book.health_snapshot.transactions_status = "ready"
            book.health_snapshot.reports_status = "ready"
            session.commit()

        response = client.post(f"/books/{book_b}/default", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book_b
        assert data["is_default"] is True
        assert "uri_or_path" not in data
        with session_factory() as session:
            assert session.query(Book).filter(Book.id == book_a).one().is_default is False
            assert session.query(Book).filter(Book.id == book_b).one().is_default is True

    def test_non_admin_cannot_set_default_book(self, client, headers_a, book_b):
        response = client.post(f"/books/{book_b}/default", headers=headers_a)

        assert response.status_code == 403
        assert response.json()["detail"] == "Admin privileges are required for book registry management."

    def test_admin_can_remove_book_from_registry_without_deleting_file(
        self, client, session_factory, admin_headers, tmp_path
    ):
        book_path = tmp_path / "remove-me.gnucash.sqlite"
        _create_minimal_gnucash_sqlite(book_path)
        with session_factory() as session:
            admin = session.query(User).filter(User.username == "admin").one()
            book = Book(
                name="Remove Me",
                storage_type="sqlite",
                uri_or_path=str(book_path),
                base_currency="USD",
                is_default=False,
            )
            session.add(book)
            session.flush()
            session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
            session.commit()
            book_id = book.id

        response = client.delete(f"/books/{book_id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data == {
            "id": book_id,
            "removed_from_registry": True,
            "underlying_file_deleted": False,
        }
        assert book_path.exists()
        with session_factory() as session:
            archived = session.query(Book).filter(Book.id == book_id).one()
            assert archived.is_archived is True

    def test_non_admin_cannot_remove_book_from_registry(self, client, headers_a, book_b):
        response = client.delete(f"/books/{book_b}", headers=headers_a)

        assert response.status_code == 403
        assert response.json()["detail"] == "Admin privileges are required for book registry management."

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
