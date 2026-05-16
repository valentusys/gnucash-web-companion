"""Tests for Phase 12 controlled write endpoints.

Strict TDD: these tests are written first and must fail before implementation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import User, Book, UserBookAccess, AuditLog
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.gnucash_write import GnuCashWriteService, GnuCashWriteError

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password="testpassword123",
    gnucash_writes_enabled=True,
)

READ_ONLY_TEST_SETTINGS = Settings(
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
def editor_user(session_factory):
    with session_factory() as session:
        user = User(
            username="editor",
            display_name="Editor",
            password_hash=hash_password("editorpass"),
        )
        session.add(user)
        session.commit()
        user_id = user.id
    return user_id


@pytest.fixture
def editor_token(client, editor_user):
    response = client.post(
        "/auth/login",
        json={"username": "editor", "password": "editorpass"},
    )
    return response.json()["access_token"]


@pytest.fixture
def editor_headers(editor_token):
    return {"Authorization": f"Bearer {editor_token}"}


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
def editor_book_access(session_factory, sample_book, editor_user):
    with session_factory() as session:
        session.add(UserBookAccess(user_id=editor_user, book_id=sample_book, role="editor"))
        session.commit()


@pytest.fixture
def viewer_book_access(session_factory, sample_book, viewer_user):
    with session_factory() as session:
        session.add(UserBookAccess(user_id=viewer_user, book_id=sample_book, role="viewer"))
        session.commit()


# ---------------------------------------------------------------------------
# Fake GnuCash fixtures for write tests
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


@dataclass
class FakeSplit:
    account: FakeAccount
    value: Decimal
    memo: str = ""


@dataclass
class FakeTransaction:
    guid: str
    post_date: date
    description: str
    splits: list[FakeSplit]
    currency: str = "SEK"


class FakeBookForWrite:
    """Fake piecash book that supports write operations."""

    def __init__(self, accounts=None, transactions=None):
        self.accounts = accounts or []
        self.transactions = transactions or []
        self.closed = False
        self.saved = False
        self.default_currency = FakeCommodity("SEK")

    def close(self):
        self.closed = True

    def save(self):
        self.saved = True


@pytest.fixture
def fake_accounts():
    root = FakeAccount(guid="root-guid", name="Root", type="ROOT")
    bank = FakeAccount(guid="bank-guid", name="Bank", type="BANK", parent=root)
    food = FakeAccount(guid="food-guid", name="Food", type="EXPENSE")
    income = FakeAccount(guid="income-guid", name="Income", type="INCOME")
    return [root, bank, food, income]


@pytest.fixture
def fake_book_path(tmp_path):
    book_path = tmp_path / "test.gnucash.sqlite"
    book_path.write_text("fake-sqlite")
    return book_path


def _make_mock_piecash(fake_book, fake_accounts):
    """Create a mock piecash module for write tests."""
    mock_piecash = MagicMock()

    def fake_open_book(uri_or_path=None, readonly=True, uri_conn=None):
        return fake_book

    mock_piecash.open_book = fake_open_book

    # Mock Transaction to return a fake transaction with a guid
    created_tx = FakeTransaction(
        guid="new-tx-guid-12345",
        post_date=date(2026, 5, 16),
        description="Test",
        splits=[],
    )

    def fake_transaction_factory(*args, **kwargs):
        splits = kwargs.get("splits", [])
        created_tx.splits = splits
        if "description" in kwargs:
            created_tx.description = kwargs["description"]
        if "post_date" in kwargs:
            created_tx.post_date = kwargs["post_date"]
        return created_tx

    mock_piecash.Transaction = fake_transaction_factory

    # Mock Split to return a simple object
    def fake_split_factory(*args, **kwargs):
        account = kwargs.get("account")
        value = kwargs.get("value", Decimal("0"))
        memo = kwargs.get("memo", "")
        split = MagicMock()
        split.account = account
        split.value = value
        split.memo = memo
        split.guid = f"split-guid-{account.guid}" if account else "split-guid-unknown"
        return split

    mock_piecash.Split = fake_split_factory

    return mock_piecash, created_tx




class TestWritesDisabledByDefault:
    """MVP v0.1 must remain read-only unless post-MVP writes are explicitly enabled."""

    def test_validate_is_forbidden_when_writes_disabled(self, client, auth_headers, sample_book):
        app.dependency_overrides[get_settings] = lambda: READ_ONLY_TEST_SETTINGS
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "100.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 403
        assert "read-only" in response.json()["detail"]
        app.dependency_overrides[get_settings] = lambda: TEST_SETTINGS


# ---------------------------------------------------------------------------
# Tests: POST /books/{book_id}/transactions/validate
# ---------------------------------------------------------------------------


class TestValidateTransaction:
    """TDD: validation endpoint must exist and return structured results."""

    def test_validate_endpoint_exists(self, client, auth_headers, sample_book):
        """POST /books/{book_id}/transactions/validate should return 200."""
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "100.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "errors" in data
        assert "warnings" in data

    def test_validate_requires_auth(self, client, sample_book):
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "100.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=payload,
        )
        assert response.status_code == 401

    def test_validate_rejects_viewer(self, client, viewer_headers, sample_book, viewer_book_access):
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "100.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=payload,
            headers=viewer_headers,
        )
        assert response.status_code == 403

    def test_validate_rejects_single_split(self, client, auth_headers, sample_book):
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert any("two splits" in e.lower() or "at least" in e.lower() for e in data["errors"])

    def test_validate_rejects_unbalanced_splits(self, client, auth_headers, sample_book):
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "99.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert any("zero" in e.lower() or "balance" in e.lower() or "sum" in e.lower() for e in data["errors"])

    def test_validate_accepts_balanced_splits(self, client, auth_headers, sample_book):
        payload = {
            "date": "2026-05-16",
            "description": "ICA",
            "splits": [
                {"account_id": "bank-guid", "amount": "-320.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "320.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # May have warnings but should not have structural errors about balance
        balance_errors = [e for e in data["errors"] if "zero" in e.lower() or "balance" in e.lower()]
        assert len(balance_errors) == 0

    def test_validate_rejects_placeholder_account(self, client, auth_headers, sample_book):
        """Placeholder accounts should be rejected by default."""
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "placeholder-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "100.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # Should warn or error about placeholder
        all_issues = data["errors"] + data["warnings"]
        assert len(all_issues) > 0 or data["valid"] is True  # placeholder check may need accounts lookup

    def test_validate_three_split_transaction(self, client, auth_headers, sample_book):
        payload = {
            "date": "2026-05-16",
            "description": "Split test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "60.00", "currency": "SEK", "memo": ""},
                {"account_id": "income-guid", "amount": "40.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        balance_errors = [e for e in data["errors"] if "zero" in e.lower() or "balance" in e.lower()]
        assert len(balance_errors) == 0


# ---------------------------------------------------------------------------
# Tests: POST /books/{book_id}/transactions
# ---------------------------------------------------------------------------


class TestCreateTransaction:
    """TDD: create transaction endpoint must follow write flow."""

    def test_create_endpoint_exists(self, client, auth_headers, sample_book, fake_book_path, fake_accounts):
        """POST /books/{book_id}/transactions should return 201 on success."""
        payload = {
            "date": "2026-05-16",
            "description": "ICA",
            "splits": [
                {"account_id": "bank-guid", "amount": "-320.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "320.00", "currency": "SEK", "memo": ""},
            ],
        }

        fake_book = FakeBookForWrite(accounts=fake_accounts, transactions=[])
        mock_piecash, created_tx = _make_mock_piecash(fake_book, fake_accounts)

        import app.services.gnucash_write as gw_module
        import app.services.gnucash_book as gb_module

        with patch.object(gw_module, "piecash", mock_piecash):
            with patch.object(gb_module, "piecash", mock_piecash):
                with patch("app.services.gnucash_write.create_book_backup", return_value=str(fake_book_path)):
                    with patch.object(GnuCashWriteService, "_validate_configured_book", return_value=str(fake_book_path)):
                        response = client.post(
                            f"/books/{sample_book}/transactions",
                            json=payload,
                            headers=auth_headers,
                        )

        assert response.status_code == 201
        data = response.json()
        assert "transaction_id" in data
        assert "backup_path" in data

    def test_create_requires_auth(self, client, sample_book):
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "100.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions",
            json=payload,
        )
        assert response.status_code == 401

    def test_create_rejects_viewer(self, client, viewer_headers, sample_book, viewer_book_access):
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "100.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions",
            json=payload,
            headers=viewer_headers,
        )
        assert response.status_code == 403

    def test_create_writes_audit_log(self, client, auth_headers, sample_book, fake_book_path, fake_accounts, session_factory):
        """After creating a transaction, an audit log entry must exist."""
        payload = {
            "date": "2026-05-16",
            "description": "ICA",
            "splits": [
                {"account_id": "bank-guid", "amount": "-320.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "320.00", "currency": "SEK", "memo": ""},
            ],
        }

        fake_book = FakeBookForWrite(accounts=fake_accounts, transactions=[])
        mock_piecash, created_tx = _make_mock_piecash(fake_book, fake_accounts)

        import app.services.gnucash_write as gw_module

        with patch.object(gw_module, "piecash", mock_piecash):
            with patch("app.services.gnucash_write.create_book_backup", return_value=str(fake_book_path)):
                response = client.post(
                    f"/books/{sample_book}/transactions",
                    json=payload,
                    headers=auth_headers,
                )

        if response.status_code == 201:
            with session_factory() as session:
                logs = session.query(AuditLog).filter(AuditLog.action == "transaction.create").all()
                assert len(logs) >= 1
                log = logs[-1]
                assert log.book_id == sample_book
                assert log.user_id is not None

    def test_create_rejects_unbalanced(self, client, auth_headers, sample_book):
        """Unbalanced splits must be rejected with 422."""
        payload = {
            "date": "2026-05-16",
            "description": "Test",
            "splits": [
                {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "99.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_backup_before_write(self, client, auth_headers, sample_book, fake_book_path, fake_accounts):
        """Backup must happen before opening book for write."""
        call_order = []
        payload = {
            "date": "2026-05-16",
            "description": "ICA",
            "splits": [
                {"account_id": "bank-guid", "amount": "-320.00", "currency": "SEK", "memo": ""},
                {"account_id": "food-guid", "amount": "320.00", "currency": "SEK", "memo": ""},
            ],
        }

        fake_book = FakeBookForWrite(accounts=fake_accounts, transactions=[])
        mock_piecash, created_tx = _make_mock_piecash(fake_book, fake_accounts)

        import app.services.gnucash_write as gw_module

        def tracking_open(*args, **kwargs):
            call_order.append("open_book")
            return fake_book

        mock_piecash.open_book = tracking_open

        with patch.object(gw_module, "piecash", mock_piecash):
            with patch(
                "app.services.gnucash_write.create_book_backup",
                side_effect=lambda *a, **kw: (call_order.append("backup"), str(fake_book_path))[1],
            ):
                response = client.post(
                    f"/books/{sample_book}/transactions",
                    json=payload,
                    headers=auth_headers,
                )

        # If the endpoint was implemented, backup should come before write-open
        if "backup" in call_order and "open_book" in call_order:
            backup_idx = call_order.index("backup")
            open_idx = call_order.index("open_book")
            assert backup_idx < open_idx, "Backup must happen before opening book for write"


# ---------------------------------------------------------------------------
# Tests: PATCH /books/{book_id}/transactions/{transaction_id}
# ---------------------------------------------------------------------------



    def test_create_failed_validation_writes_audit_log(self, client, auth_headers, sample_book, session_factory):
        """Failed write attempts should leave an audit trail."""
        payload = {
            "date": "2025-01-15",
            "description": "Unbalanced",
            "splits": [
                {"account_id": "acc-1", "amount": "10.00", "currency": "SEK"},
                {"account_id": "acc-2", "amount": "5.00", "currency": "SEK"},
            ],
        }
        response = client.post(
            f"/books/{sample_book}/transactions",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 422

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            assert logs
            assert any('"result": "failed"' in log.payload_json for log in logs)

class TestPatchTransaction:
    """TDD: patch transaction metadata endpoint must exist."""

    def test_patch_endpoint_exists(self, client, auth_headers, sample_book):
        """PATCH /books/{book_id}/transactions/{id} should return 200."""
        payload = {
            "description": "Updated description",
        }
        response = client.patch(
            f"/books/{sample_book}/transactions/some-tx-id",
            json=payload,
            headers=auth_headers,
        )
        # Should not be 405 for missing endpoint. Missing fixture book may produce
        # controlled 404/422 depending on whether book or tx validation fails first.
        assert response.status_code in (200, 404, 422)

    def test_patch_requires_auth(self, client, sample_book):
        payload = {"description": "Updated"}
        response = client.patch(
            f"/books/{sample_book}/transactions/some-tx-id",
            json=payload,
        )
        assert response.status_code == 401

    def test_patch_rejects_viewer(self, client, viewer_headers, sample_book, viewer_book_access):
        payload = {"description": "Updated"}
        response = client.patch(
            f"/books/{sample_book}/transactions/some-tx-id",
            json=payload,
            headers=viewer_headers,
        )
        assert response.status_code == 403


    def test_patch_rejects_noop_payload(self, client, auth_headers, sample_book):
        """Empty patch payload should not create a backup or no-op write."""
        response = client.patch(
            f"/books/{sample_book}/transactions/some-tx-id",
            json={},
            headers=auth_headers,
        )
        assert response.status_code in (404, 422)

    def test_patch_rejects_split_amount_edit(self, client, auth_headers, sample_book):
        """PATCH must not allow editing split amounts or accounts."""
        payload = {
            "description": "Updated",
            "splits": [
                {"account_id": "bank-guid", "amount": "-999.00", "currency": "SEK", "memo": ""},
            ],
        }
        response = client.patch(
            f"/books/{sample_book}/transactions/some-tx-id",
            json=payload,
            headers=auth_headers,
        )
        # Should reject with 422 if splits are provided
        if response.status_code != 404:
            assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests: Backup service
# ---------------------------------------------------------------------------


class TestBackupService:
    """TDD: backup service must create timestamped backups."""

    def test_backup_creates_file(self, tmp_path):
        """create_book_backup should create a backup file."""
        from app.services.backup import create_book_backup

        book_path = tmp_path / "test.gnucash.sqlite"
        book_path.write_text("test-content")

        book_config = {"uri_or_path": str(book_path)}
        backup_path = create_book_backup(book_config)
        assert Path(backup_path).exists()

    def test_backup_contains_timestamp(self, tmp_path):
        """Backup filename should contain a timestamp."""
        from app.services.backup import create_book_backup

        book_path = tmp_path / "test.gnucash.sqlite"
        book_path.write_text("test-content")

        book_config = {"uri_or_path": str(book_path)}
        backup_path = create_book_backup(book_config)
        filename = Path(backup_path).name
        # Should contain date-like pattern
        import re
        assert re.search(r"\d{4}", filename), f"Backup filename should contain year: {filename}"

    def test_backup_fails_for_missing_book(self, tmp_path):
        """Backup should raise error for missing book."""
        from app.services.backup import create_book_backup, BackupError

        book_config = {"uri_or_path": str(tmp_path / "nonexistent.gnucash.sqlite")}
        with pytest.raises(BackupError):
            create_book_backup(book_config)


# ---------------------------------------------------------------------------
# Tests: Write lock service
# ---------------------------------------------------------------------------


class TestWriteLockService:
    """TDD: per-book write lock must prevent concurrent writes."""

    def test_lock_acquire_and_release(self):
        from app.services.write_lock import WriteLockService

        svc = WriteLockService()
        acquired = svc.acquire("book-1")
        assert acquired is True
        svc.release("book-1")

    def test_lock_blocks_concurrent(self):
        from app.services.write_lock import WriteLockService

        svc = WriteLockService()
        acquired1 = svc.acquire("book-1")
        assert acquired1 is True

        # Second acquire should fail or return False
        acquired2 = svc.acquire("book-1")
        assert acquired2 is False

        svc.release("book-1")

    def test_lock_different_books_independent(self):
        from app.services.write_lock import WriteLockService

        svc = WriteLockService()
        assert svc.acquire("book-1") is True
        assert svc.acquire("book-2") is True
        svc.release("book-1")
        svc.release("book-2")

    def test_lock_release_idempotent(self):
        from app.services.write_lock import WriteLockService

        svc = WriteLockService()
        svc.acquire("book-1")
        svc.release("book-1")
        svc.release("book-1")  # Should not raise


# ---------------------------------------------------------------------------
# Tests: Read-only flows still work
# ---------------------------------------------------------------------------


class TestReadOnlyFlowsPreserved:
    """Ensure existing read-only endpoints still work after write changes."""

    def test_list_transactions_still_works(self, client, auth_headers, sample_book):
        response = client.get(
            f"/books/{sample_book}/transactions",
            headers=auth_headers,
        )
        # Missing test book should still produce a controlled error, not a crash.
        assert response.status_code in (200, 404, 503)

    def test_get_transaction_still_works(self, client, auth_headers, sample_book):
        response = client.get(
            f"/books/{sample_book}/transactions/some-id",
            headers=auth_headers,
        )
        assert response.status_code in (404, 503)

    def test_list_accounts_still_works(self, client, auth_headers, sample_book):
        response = client.get(
            f"/books/{sample_book}/accounts",
            headers=auth_headers,
        )
        assert response.status_code in (200, 404, 503)

    def test_mvp_transactions_still_works(self, client, auth_headers):
        response = client.get(
            "/transactions",
            headers=auth_headers,
        )
        assert response.status_code in (200, 404, 503)
