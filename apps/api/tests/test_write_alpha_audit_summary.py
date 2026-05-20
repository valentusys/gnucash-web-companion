"""Tests for redacted write-alpha audit summary endpoint."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

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
                    username="editor",
                    display_name="Editor",
                    password_hash=hash_password("editorpass"),
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
def editor_headers(client):
    return _login(client, "editor", "editorpass")


@pytest.fixture
def outsider_headers(client):
    return _login(client, "outsider", "outsiderpass")


@pytest.fixture
def sample_book_with_audit(session_factory, tmp_path: Path) -> int:
    synthetic_book = tmp_path / "disposable-audit-fixture.gnucash.sqlite"
    synthetic_book.touch()
    with session_factory() as session:
        book = Book(
            name="Disposable audit fixture",
            storage_type="sqlite",
            uri_or_path=str(synthetic_book),
            base_currency="SEK",
            is_default=True,
        )
        session.add(book)
        session.flush()
        users = {user.username: user for user in session.query(User).all()}
        session.add_all(
            [
                UserBookAccess(user_id=users["admin"].id, book_id=book.id, role="owner"),
                UserBookAccess(user_id=users["editor"].id, book_id=book.id, role="editor"),
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
                    action="transaction.delete",
                    payload_json=json.dumps(
                        {
                            "action": "transaction.delete",
                            "result": "success",
                            "timestamp": "2026-05-20T10:10:00+00:00",
                            "transaction_id": "deadbeef12345678",
                            "backup_path": "/data/backups/private/delete-backup.sqlite",
                            "deleted_summary": {
                                "description": "PRIVATE DELETED TX",
                                "account_name": "Assets:Private",
                                "amount": "999.01",
                            },
                        }
                    ),
                    created_at=datetime(2026, 5, 20, 10, 10, tzinfo=timezone.utc),
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
            "transaction.delete",
            "transaction.patch",
            "transaction.create",
        ]
        assert data["total_count"] == 3
        assert data["returned_count"] == 3
        assert data["counts_by_action"] == {
            "transaction.create": 1,
            "transaction.patch": 1,
            "transaction.delete": 1,
        }
        assert data["counts_by_result"] == {
            "started": 0,
            "success": 2,
            "failed": 1,
            "unknown": 0,
        }
        assert data["time_window"]["newest_returned"] == "2026-05-20T10:10:00+00:00"
        assert data["time_window"]["oldest_returned"] == "2026-05-20T10:00:00+00:00"
        assert data["status_summary"] == [
            "Filtered rows: 3",
            "Returned rows: 3 of at most 25 from offset 0",
            "Rows are redacted to action/result/timestamp/opaque transaction prefix/backup-present/safe-error only.",
        ]
        assert data["pagination"] == {
            "limit": 25,
            "offset": 0,
            "next_offset": None,
            "previous_offset": None,
            "has_next": False,
            "has_previous": False,
        }

        delete_item, patch_item, create_item = data["items"]
        assert delete_item["transaction_id_prefix"] == "deadbeef"
        assert delete_item["backup_present"] is True
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
            "delete-backup.sqlite",
            "PRIVATE DELETED TX",
            "Assets:Private",
            "999.01",
            "request_summary",
            "fields_updated",
            "deleted_summary",
        ]:
            assert forbidden not in encoded

        assert any("Read-only app metadata" in limitation for limitation in data["limitations"])

    def test_editor_can_filter_by_action_result_and_time_window(self, client, sample_book_with_audit, editor_headers):
        response = client.get(
            f"/books/{sample_book_with_audit}/write-alpha-audit-summary"
            "?action=transaction.delete&result=success"
            "&since=2026-05-20T10:09:00%2B00:00&until=2026-05-20T10:11:00%2B00:00",
            headers=editor_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 1
        assert data["returned_count"] == 1
        assert [item["action"] for item in data["items"]] == ["transaction.delete"]
        assert data["filters"]["action"] == "transaction.delete"
        assert data["filters"]["result"] == "success"
        assert data["counts_by_action"] == {
            "transaction.create": 0,
            "transaction.patch": 0,
            "transaction.delete": 1,
        }
        assert data["counts_by_result"]["success"] == 1

    def test_large_synthetic_audit_table_is_bounded_and_pageable(self, client, session_factory, sample_book_with_audit, auth_headers):
        with session_factory() as session:
            admin = session.query(User).filter(User.username == "admin").one()
            for index in range(150):
                session.add(
                    AuditLog(
                        user_id=admin.id,
                        book_id=sample_book_with_audit,
                        action="transaction.create",
                        payload_json=json.dumps(
                            {
                                "result": "success" if index % 2 == 0 else "failed",
                                "timestamp": f"2026-05-20T12:{index % 60:02d}:00+00:00",
                                "transaction_id": f"abcdef{index:010d}",
                                "backup_path": f"/data/backups/private/{index}.sqlite",
                                "request_summary": {
                                    "description": f"PRIVATE MEMO {index}",
                                    "account_name": "Assets:Private",
                                    "amount": "12345.67",
                                },
                            }
                        ),
                        created_at=datetime(2026, 5, 20, 12, index % 60, tzinfo=timezone.utc),
                    )
                )
            session.commit()

        first_response = client.get(
            f"/books/{sample_book_with_audit}/write-alpha-audit-summary?limit=10&offset=0",
            headers=auth_headers,
        )
        second_response = client.get(
            f"/books/{sample_book_with_audit}/write-alpha-audit-summary?limit=10&offset=10",
            headers=auth_headers,
        )

        assert first_response.status_code == 200
        assert second_response.status_code == 200
        first_page = first_response.json()
        second_page = second_response.json()
        assert first_page["total_count"] == 153
        assert first_page["returned_count"] == 10
        assert len(first_page["items"]) == 10
        assert first_page["pagination"] == {
            "limit": 10,
            "offset": 0,
            "next_offset": 10,
            "previous_offset": None,
            "has_next": True,
            "has_previous": False,
        }
        assert second_page["returned_count"] == 10
        assert second_page["pagination"]["offset"] == 10
        assert second_page["pagination"]["next_offset"] == 20
        assert second_page["pagination"]["previous_offset"] == 0
        assert {item["id"] for item in first_page["items"]}.isdisjoint(
            {item["id"] for item in second_page["items"]}
        )

        encoded = json.dumps({"first": first_page, "second": second_page})
        for forbidden in [
            "/data/backups",
            "PRIVATE MEMO",
            "Assets:Private",
            "12345.67",
            "request_summary",
            "account_name",
        ]:
            assert forbidden not in encoded

    def test_redacts_malicious_payload_status_timestamp_ids_and_error_text(self, client, session_factory, sample_book_with_audit, auth_headers):
        with session_factory() as session:
            admin = session.query(User).filter(User.username == "admin").one()
            session.add(
                AuditLog(
                    user_id=admin.id,
                    book_id=sample_book_with_audit,
                    action="transaction.patch",
                    payload_json=json.dumps(
                        {
                            "result": "success/../../private",
                            "timestamp": "/private/path/timestamp.sqlite",
                            "transaction_id": "/home/val/private-book.gnucash.sqlite",
                            "backup_path": "/data/backups/private/unsafe.sqlite",
                            "error": "Account Assets:Private memo SECRET amount 777.42",
                        }
                    ),
                    created_at=datetime(2026, 5, 20, 10, 20, tzinfo=timezone.utc),
                )
            )
            session.commit()

        response = client.get(
            f"/books/{sample_book_with_audit}/write-alpha-audit-summary?action=transaction.patch&limit=1",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert data["returned_count"] == 1
        assert data["counts_by_result"]["unknown"] == 1
        item = data["items"][0]
        assert item["result"] == "unknown"
        assert item["timestamp"] == "2026-05-20T10:20:00"
        assert item["transaction_id_prefix"] is None
        assert item["backup_present"] is True
        assert item["error"] == "Write-alpha request failed safely; check redacted operator evidence."

        encoded = json.dumps(data)
        for forbidden in [
            "/home/val",
            "/private/path",
            "/data/backups",
            "private-book",
            "Assets:Private",
            "SECRET",
            "777.42",
            "success/../../private",
            "timestamp.sqlite",
            "unsafe.sqlite",
        ]:
            assert forbidden not in encoded

    def test_filter_empty_state_and_invalid_filters_are_safe(self, client, sample_book_with_audit, auth_headers):
        empty_response = client.get(
            f"/books/{sample_book_with_audit}/write-alpha-audit-summary?action=transaction.create&result=failed",
            headers=auth_headers,
        )
        assert empty_response.status_code == 200
        empty_data = empty_response.json()
        assert empty_data["items"] == []
        assert empty_data["total_count"] == 0
        assert empty_data["counts_by_action"] == {
            "transaction.create": 0,
            "transaction.patch": 0,
            "transaction.delete": 0,
        }

        invalid_response = client.get(
            f"/books/{sample_book_with_audit}/write-alpha-audit-summary?since=/private/path/book.sqlite",
            headers=auth_headers,
        )
        assert invalid_response.status_code == 422
        encoded = json.dumps(invalid_response.json())
        assert "/private/path" not in encoded
        assert "Use an ISO timestamp" in encoded
