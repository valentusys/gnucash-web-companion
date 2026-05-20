"""Tests for redacted write-alpha audit summary endpoint."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import AuditLog, Book, User, UserBookAccess
from app.routers.auth import get_db
from app.services.auth import hash_password

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password="testpassword123",
    gnucash_writes_enabled=False,
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
        session.add_all(
            [
                User(
                    username="admin",
                    display_name="Admin",
                    password_hash=hash_password("testpassword123"),
                    is_admin=True,
                ),
                User(
                    username="viewer",
                    display_name="Viewer",
                    password_hash=hash_password("viewerpass"),
                    is_admin=False,
                ),
                User(
                    username="outsider",
                    display_name="Outsider",
                    password_hash=hash_password("outsiderpass"),
                    is_admin=False,
                ),
            ]
        )
        session.commit()

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def _login(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def auth_headers(client):
    return _login(client, "admin", "testpassword123")


@pytest.fixture
def viewer_headers(client):
    return _login(client, "viewer", "viewerpass")


@pytest.fixture
def outsider_headers(client):
    return _login(client, "outsider", "outsiderpass")


@pytest.fixture
def sample_book_with_audit(session_factory) -> int:
    with session_factory() as session:
        book = Book(
            name="Disposable audit fixture",
            storage_type="sqlite",
            uri_or_path="/data/books/disposable.gnucash.sqlite",
            base_currency="SEK",
            is_default=True,
        )
        session.add(book)
        session.flush()
        users = {user.username: user for user in session.query(User).all()}
        session.add_all(
            [
                UserBookAccess(user_id=users["admin"].id, book_id=book.id, role="owner"),
                UserBookAccess(user_id=users["viewer"].id, book_id=book.id, role="viewer"),
            ]
        )
        session.add_all(
            [
                AuditLog(
                    user_id=users["admin"].id,
                    book_id=book.id,
                    action="transaction.create",
                    payload_json=json.dumps(
                        {
                            "action": "transaction.create",
                            "result": "success",
                            "timestamp": "2026-05-20T10:00:00+00:00",
                            "transaction_id": "abcdef1234567890",
                            "backup_path": "/data/backups/private/book-backup.sqlite",
                            "request_summary": {
                                "description": "RAW PRIVATE DESCRIPTION",
                                "split_count": 2,
                                "amount": "12345.67",
                            },
                        }
                    ),
                    created_at=datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
                ),
                AuditLog(
                    user_id=users["admin"].id,
                    book_id=book.id,
                    action="transaction.patch",
                    payload_json=json.dumps(
                        {
                            "action": "transaction.patch",
                            "result": "failed",
                            "timestamp": "2026-05-20T10:05:00+00:00",
                            "transaction_id": "1234567890abcdef",
                            "backup_path": None,
                            "error": "failure under /private/path/book.sqlite",
                            "fields_updated": {"description": "SECRET", "split_memos": {"s": "MEMO"}},
                        }
                    ),
                    created_at=datetime(2026, 5, 20, 10, 5, tzinfo=timezone.utc),
                ),
                AuditLog(
                    user_id=users["admin"].id,
                    book_id=book.id,
                    action="auth.login",
                    payload_json=json.dumps({"secret": "not relevant"}),
                    created_at=datetime(2026, 5, 20, 10, 6, tzinfo=timezone.utc),
                ),
            ]
        )
        session.commit()
        return book.id


class TestWriteAlphaAuditSummary:
    def test_requires_authentication(self, client, sample_book_with_audit):
        response = client.get(f"/books/{sample_book_with_audit}/write-alpha-audit-summary")
        assert response.status_code == 401

    def test_blocks_viewer_and_unauthorized_access(self, client, sample_book_with_audit, viewer_headers, outsider_headers):
        viewer_response = client.get(
            f"/books/{sample_book_with_audit}/write-alpha-audit-summary", headers=viewer_headers
        )
        outsider_response = client.get(
            f"/books/{sample_book_with_audit}/write-alpha-audit-summary", headers=outsider_headers
        )
        assert viewer_response.status_code == 403
        assert outsider_response.status_code == 403

    def test_returns_redacted_write_alpha_summary_only(self, client, sample_book_with_audit, auth_headers):
        response = client.get(
            f"/books/{sample_book_with_audit}/write-alpha-audit-summary", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["book_id"] == sample_book_with_audit
        assert [item["action"] for item in data["items"]] == [
            "transaction.patch",
            "transaction.create",
        ]

        patch_item, create_item = data["items"]
        assert patch_item["transaction_id_prefix"] == "12345678"
        assert patch_item["backup_present"] is False
        assert patch_item["error"] == "Write-alpha request failed safely; check redacted operator evidence."
        assert create_item["transaction_id_prefix"] == "abcdef12"
        assert create_item["backup_present"] is True
        assert create_item["error"] is None

        encoded = json.dumps(data)
        for forbidden in [
            "/data/backups",
            "/private/path",
            "RAW PRIVATE DESCRIPTION",
            "12345.67",
            "SECRET",
            "MEMO",
            "book-backup.sqlite",
            "request_summary",
            "fields_updated",
        ]:
            assert forbidden not in encoded

        assert any("Read-only app metadata" in limitation for limitation in data["limitations"])
