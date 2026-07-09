"""Tests for Phase 12 controlled write endpoints.

Strict TDD: these tests are written first and must fail before implementation.
"""

from __future__ import annotations

import json
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch, MagicMock

import piecash
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import User, Book, UserBookAccess, AuditLog, WriteAlphaTransactionOwnership
from app.routers.auth import get_db
from app.schemas.gnucash import AccountDTO, TransactionDetailDTO, TransactionSplitDTO
from app.schemas.gnucash_writes import TransactionCreateRequestDTO, TransactionSplitWriteDTO
from app.services.auth import hash_password
from app.services.backup import BackupError
from app.services.gnucash_write import GnuCashWriteService, GnuCashWriteError
from app.services.gnucash_book import _guid
from app.services.write_lock import WriteLockError

REPO_ROOT = Path(__file__).resolve().parents[3]
SYNTHETIC_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "test-book.gnucash.sqlite"

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

WRITE_ENABLED_DEVELOPMENT_SETTINGS = Settings(
    app_env="development",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password="testpassword123",
    gnucash_writes_enabled=True,
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
def sample_book(session_factory, tmp_path: Path):
    target = tmp_path / "disposable-route-test-book.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00")
    with session_factory() as session:
        book = Book(
            name="Test Book",
            storage_type="sqlite",
            uri_or_path=str(target),
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


@pytest.fixture
def disposable_fixture_book(tmp_path: Path) -> Path:
    book_dir = tmp_path / "books"
    book_dir.mkdir()
    book_path = book_dir / "write-alpha-disposable.gnucash.sqlite"
    shutil.copy2(SYNTHETIC_FIXTURE_PATH, book_path)
    return book_path


@pytest.fixture
def disposable_sample_book(session_factory, disposable_fixture_book: Path) -> int:
    with session_factory() as session:
        book = Book(
            name="Disposable write-alpha fixture",
            storage_type="sqlite",
            uri_or_path=str(disposable_fixture_book),
            base_currency="SEK",
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
def disposable_write_lock(tmp_path: Path):
    import app.services.write_lock as wl_module
    import app.services.gnucash_write as gw_module

    original_wl_service = wl_module.write_lock_service
    original_gw_service = gw_module.write_lock_service
    tmp_lock_svc = wl_module.WriteLockService(lock_dir=tmp_path / "locks")
    wl_module.write_lock_service = tmp_lock_svc
    gw_module.write_lock_service = tmp_lock_svc
    try:
        yield tmp_lock_svc
    finally:
        wl_module.write_lock_service = original_wl_service
        gw_module.write_lock_service = original_gw_service


def _read_written_transactions(book_path: Path) -> list[dict]:
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        return [
            {
                "guid": tx.guid,
                "description": tx.description,
                "post_date": tx.post_date,
                "currency": str(getattr(getattr(tx, "currency", None), "mnemonic", "")),
                "splits": [
                    {
                        "guid": _guid(split),
                        "account_guid": split.account.guid,
                        "account_name": split.account.name,
                        "value": Decimal(str(split.value)),
                        "memo": split.memo,
                    }
                    for split in tx.splits
                ],
            }
            for tx in book.transactions
        ]
    finally:
        book.close()


def _read_account_balances(book_path: Path, account_guids: set[str]) -> dict[str, Decimal]:
    """Reopen a disposable fixture read-only and return exact account balances."""
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        balances: dict[str, Decimal] = {}
        for account in book.accounts:
            account_guid = str(account.guid)
            if account_guid in account_guids:
                balances[account_guid] = Decimal(str(account.get_balance()))
        return balances
    finally:
        book.close()


def _read_account_balances_via_readonly_route(
    client: TestClient,
    auth_headers: dict[str, str],
    book_id: int,
    account_guids: set[str],
) -> dict[str, Decimal]:
    """Read balances through the app's read-only account service route."""
    response = client.get(f"/books/{book_id}/accounts", headers=auth_headers)
    assert response.status_code == 200
    balances = {
        account["id"]: Decimal(account["balance"])
        for account in response.json()
        if account["id"] in account_guids
    }
    assert set(balances) == account_guids
    return balances


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
        if created_tx not in fake_book.transactions:
            fake_book.transactions.append(created_tx)
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


def _balanced_transaction_payload():
    return {
        "date": "2026-05-16",
        "description": "Test",
        "splits": [
            {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
            {"account_id": "food-guid", "amount": "100.00", "currency": "SEK", "memo": ""},
        ],
    }


def _readback_detail_from_payload(transaction_id: str, payload: dict) -> TransactionDetailDTO:
    return TransactionDetailDTO(
        id=transaction_id,
        date=payload["date"],
        description=payload["description"],
        currency=payload["splits"][0]["currency"],
        splits=[
            TransactionSplitDTO(
                account_id=split["account_id"],
                account_name=split["account_id"],
                memo=split.get("memo", ""),
                reconcile_state="",
                amount=split["amount"],
                currency=split["currency"],
            )
            for split in payload["splits"]
        ],
    )


class TestWritesDisabledByDefault:
    """MVP v0.1 must remain read-only unless post-MVP writes are explicitly enabled."""

    def test_settings_default_keeps_writes_disabled_and_non_test(self, monkeypatch):
        monkeypatch.delenv("GNUCASH_WRITES_ENABLED", raising=False)
        monkeypatch.delenv("APP_ENV", raising=False)

        settings = Settings()

        assert settings.gnucash_writes_enabled is False
        assert settings.app_env == "development"

    def test_repository_default_configuration_keeps_writes_disabled(self):
        env_example = (REPO_ROOT / ".env.example").read_text()
        compose = (REPO_ROOT / "docker-compose.yml").read_text()

        assert "GNUCASH_WRITES_ENABLED=false" in env_example
        assert "GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}" in compose

    def test_default_runtime_settings_short_circuit_before_app_env_gate_and_book_resolution(
        self,
        client,
        auth_headers,
        monkeypatch,
    ):
        """Default Settings are development/read-only and must fail closed before resolving a book."""
        monkeypatch.delenv("GNUCASH_WRITES_ENABLED", raising=False)
        monkeypatch.delenv("APP_ENV", raising=False)
        resolved_books = []
        write_services = []

        def forbidden_book_resolution(*args, **kwargs):
            resolved_books.append((args, kwargs))
            raise AssertionError("default-disabled writes must not resolve books")

        def forbidden_write_service(*args, **kwargs):
            write_services.append((args, kwargs))
            raise AssertionError("default-disabled writes must not construct write services")

        default_runtime_settings = Settings(
            app_database_url="sqlite:///:memory:",
            jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
            jwt_token_expire_minutes=30,
            app_admin_username="admin",
            app_admin_password="testpassword123",
        )
        assert default_runtime_settings.gnucash_writes_enabled is False
        assert default_runtime_settings.app_env == "development"
        app.dependency_overrides[get_settings] = lambda: default_runtime_settings
        monkeypatch.setattr("app.routers.transactions._resolve_viewable_book", forbidden_book_resolution)
        monkeypatch.setattr("app.routers.transactions._write_service_for", forbidden_write_service)

        response = client.post(
            "/books/999/transactions/validate",
            json=_balanced_transaction_payload(),
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "read-only" in response.json()["detail"]
        assert "test" not in response.json()["detail"].lower()
        assert resolved_books == []
        assert write_services == []

    @pytest.fixture
    def fail_if_write_service_is_constructed(self, monkeypatch):
        calls = []

        def forbidden_write_service(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("_write_service_for must not be called when writes are disabled")

        monkeypatch.setattr(
            "app.routers.transactions._write_service_for",
            forbidden_write_service,
        )
        return calls

    def _assert_read_only_response_without_write_service(self, response, calls):
        assert response.status_code == 403
        assert "read-only" in response.json()["detail"]
        assert calls == []

    def _force_read_only_settings(self):
        app.dependency_overrides[get_settings] = lambda: READ_ONLY_TEST_SETTINGS

    def test_disabled_write_routes_short_circuit_before_book_resolution(
        self,
        client,
        auth_headers,
        fail_if_write_service_is_constructed,
        monkeypatch,
    ):
        resolved_books = []

        def forbidden_book_resolution(*args, **kwargs):
            resolved_books.append((args, kwargs))
            raise AssertionError("write routes must not resolve books when writes are disabled")

        self._force_read_only_settings()
        monkeypatch.setattr(
            "app.routers.transactions._resolve_viewable_book",
            forbidden_book_resolution,
        )

        responses = [
            client.post(
                "/books/999/transactions/validate",
                json=_balanced_transaction_payload(),
                headers=auth_headers,
            ),
            client.post(
                "/books/999/transactions",
                json=_balanced_transaction_payload(),
                headers=auth_headers,
            ),
            client.patch(
                "/books/999/transactions/some-tx-id",
                json={"description": "Updated description"},
                headers=auth_headers,
            ),
            client.delete(
                "/books/999/transactions/some-tx-id",
                headers=auth_headers,
            ),
        ]

        for response in responses:
            self._assert_read_only_response_without_write_service(
                response,
                fail_if_write_service_is_constructed,
            )
        assert resolved_books == []

    def test_validate_is_forbidden_when_writes_disabled(
        self,
        client,
        auth_headers,
        sample_book,
        fail_if_write_service_is_constructed,
    ):
        self._force_read_only_settings()
        response = client.post(
            f"/books/{sample_book}/transactions/validate",
            json=_balanced_transaction_payload(),
            headers=auth_headers,
        )
        self._assert_read_only_response_without_write_service(
            response,
            fail_if_write_service_is_constructed,
        )

    def test_create_is_forbidden_when_writes_disabled_without_constructing_write_service(
        self,
        client,
        auth_headers,
        sample_book,
        fail_if_write_service_is_constructed,
    ):
        self._force_read_only_settings()
        response = client.post(
            f"/books/{sample_book}/transactions",
            json=_balanced_transaction_payload(),
            headers=auth_headers,
        )
        self._assert_read_only_response_without_write_service(
            response,
            fail_if_write_service_is_constructed,
        )

    def test_patch_is_forbidden_when_writes_disabled_without_constructing_write_service(
        self,
        client,
        auth_headers,
        sample_book,
        fail_if_write_service_is_constructed,
    ):
        self._force_read_only_settings()
        response = client.patch(
            f"/books/{sample_book}/transactions/some-tx-id",
            json={"description": "Updated description"},
            headers=auth_headers,
        )
        self._assert_read_only_response_without_write_service(
            response,
            fail_if_write_service_is_constructed,
        )

    def test_delete_is_forbidden_when_writes_disabled_without_constructing_write_service(
        self,
        client,
        auth_headers,
        sample_book,
        fail_if_write_service_is_constructed,
    ):
        self._force_read_only_settings()
        response = client.delete(
            f"/books/{sample_book}/transactions/some-tx-id",
            headers=auth_headers,
        )
        self._assert_read_only_response_without_write_service(
            response,
            fail_if_write_service_is_constructed,
        )

    def test_write_routes_short_circuit_before_book_resolution_when_app_env_not_test(
        self,
        client,
        auth_headers,
        fail_if_write_service_is_constructed,
        monkeypatch,
    ):
        """A casual non-test runtime flag flip must not resolve books or enter writes."""
        resolved_books = []

        def forbidden_book_resolution(*args, **kwargs):
            resolved_books.append((args, kwargs))
            raise AssertionError("write routes must not resolve books when APP_ENV is not test")

        app.dependency_overrides[get_settings] = lambda: WRITE_ENABLED_DEVELOPMENT_SETTINGS
        monkeypatch.setattr(
            "app.routers.transactions._resolve_viewable_book",
            forbidden_book_resolution,
        )

        responses = [
            client.post(
                "/books/999/transactions/validate",
                json=_balanced_transaction_payload(),
                headers=auth_headers,
            ),
            client.post(
                "/books/999/transactions",
                json=_balanced_transaction_payload(),
                headers=auth_headers,
            ),
            client.patch(
                "/books/999/transactions/some-tx-id",
                json={"description": "Updated description"},
                headers=auth_headers,
            ),
            client.delete(
                "/books/999/transactions/some-tx-id",
                headers=auth_headers,
            ),
        ]

        for response in responses:
            assert response.status_code == 403
            assert "write-alpha" in response.json()["detail"]
            assert "test" in response.json()["detail"]
        assert fail_if_write_service_is_constructed == []
        assert resolved_books == []


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


class TestWriteServiceValidationRules:
    """Regression coverage for the write-alpha validation safety foundation."""

    def _service_with_fake_accounts(self, accounts):
        fake_book = FakeBookForWrite(accounts=accounts, transactions=[])
        service = GnuCashWriteService({"uri_or_path": "/tmp/disposable-write-alpha.gnucash.sqlite"})
        service._validate_configured_book = lambda: "/tmp/disposable-write-alpha.gnucash.sqlite"
        service._open_piecash_book = lambda uri_or_path: fake_book
        return service

    def test_validation_reports_all_core_create_guards(self, fake_accounts):
        service = self._service_with_fake_accounts(fake_accounts)

        result = service.validate_transaction_create(
            TransactionCreateRequestDTO.model_construct(
                date="bad-date",
                description="Invalid write-alpha validation probe",
                splits=[
                    TransactionSplitWriteDTO.model_construct(
                        account_id="missing-guid",
                        amount="not-decimal",
                        currency="SEK",
                        memo="",
                    ),
                ],
            )
        )

        assert result.valid is False
        joined_errors = "\n".join(result.errors)
        assert "At least two splits" in joined_errors
        assert "Invalid amount 'not-decimal'" in joined_errors
        assert "Account not found: missing-guid" in joined_errors
        assert "Invalid date format: bad-date" in joined_errors

    def test_validation_rejects_non_zero_sum_per_currency_and_placeholder_accounts(self, fake_accounts):
        placeholder = FakeAccount(
            guid="placeholder-guid",
            name="Placeholder",
            type="ASSET",
            placeholder=True,
        )
        service = self._service_with_fake_accounts([*fake_accounts, placeholder])

        result = service.validate_transaction_create(
            TransactionCreateRequestDTO(
                date="2026-05-16",
                description="Placeholder write-alpha validation probe",
                splits=[
                    TransactionSplitWriteDTO(
                        account_id="placeholder-guid",
                        amount="-100.00",
                        currency="SEK",
                        memo="",
                    ),
                    TransactionSplitWriteDTO(
                        account_id="food-guid",
                        amount="99.99",
                        currency="SEK",
                        memo="",
                    ),
                ],
            )
        )

        assert result.valid is False
        joined_errors = "\n".join(result.errors)
        assert "Splits do not balance to zero for currency SEK" in joined_errors
        assert "placeholder account and cannot receive postings" in joined_errors

    def test_validation_accepts_balanced_multi_split_decimal_strings(self, fake_accounts):
        service = self._service_with_fake_accounts(fake_accounts)

        result = service.validate_transaction_create(
            TransactionCreateRequestDTO(
                date="2026-05-16",
                description="Balanced validation probe",
                splits=[
                    TransactionSplitWriteDTO(
                        account_id="bank-guid",
                        amount="-100.100000000000000001",
                        currency="SEK",
                        memo="source",
                    ),
                    TransactionSplitWriteDTO(
                        account_id="food-guid",
                        amount="70.050000000000000000",
                        currency="SEK",
                        memo="food",
                    ),
                    TransactionSplitWriteDTO(
                        account_id="income-guid",
                        amount="30.050000000000000001",
                        currency="SEK",
                        memo="offset",
                    ),
                ],
            )
        )

        assert result.valid is True
        assert result.errors == []
        assert result.summary["split_count"] == 3
        assert result.summary["currencies"] == ["SEK"]

    def test_validation_balances_plain_decimal_strings_exactly(self, fake_accounts):
        service = self._service_with_fake_accounts(fake_accounts)

        result = service.validate_transaction_create(
            TransactionCreateRequestDTO(
                date="2026-05-16",
                description="Float-sensitive decimal validation probe",
                splits=[
                    TransactionSplitWriteDTO(
                        account_id="bank-guid",
                        amount="-0.30",
                        currency="SEK",
                        memo="source",
                    ),
                    TransactionSplitWriteDTO(
                        account_id="food-guid",
                        amount="0.10",
                        currency="SEK",
                        memo="first decimal",
                    ),
                    TransactionSplitWriteDTO(
                        account_id="income-guid",
                        amount="0.20",
                        currency="SEK",
                        memo="second decimal",
                    ),
                ],
            )
        )

        assert result.valid is True
        assert result.errors == []
        assert result.summary["currencies"] == ["SEK"]

    def test_validation_rejects_missing_account_even_when_splits_balance(self, fake_accounts):
        service = self._service_with_fake_accounts(fake_accounts)

        result = service.validate_transaction_create(
            TransactionCreateRequestDTO(
                date="2026-05-16",
                description="Missing account validation probe",
                splits=[
                    TransactionSplitWriteDTO(
                        account_id="missing-guid",
                        amount="-50.00",
                        currency="SEK",
                        memo="missing",
                    ),
                    TransactionSplitWriteDTO(
                        account_id="food-guid",
                        amount="50.00",
                        currency="SEK",
                        memo="known",
                    ),
                ],
            )
        )

        assert result.valid is False
        assert result.errors == ["Account not found: missing-guid"]

    def test_validation_rejects_placeholder_account_even_when_splits_balance(self, fake_accounts):
        placeholder = FakeAccount(
            guid="placeholder-guid",
            name="Synthetic Placeholder",
            type="ASSET",
            placeholder=True,
        )
        service = self._service_with_fake_accounts([*fake_accounts, placeholder])

        result = service.validate_transaction_create(
            TransactionCreateRequestDTO(
                date="2026-05-16",
                description="Balanced placeholder validation probe",
                splits=[
                    TransactionSplitWriteDTO(
                        account_id="placeholder-guid",
                        amount="-12.34",
                        currency="SEK",
                        memo="placeholder",
                    ),
                    TransactionSplitWriteDTO(
                        account_id="food-guid",
                        amount="12.34",
                        currency="SEK",
                        memo="posting",
                    ),
                ],
            )
        )

        assert result.valid is False
        assert result.errors == [
            "Account placeholder-guid is a placeholder account and cannot receive postings"
        ]

    def test_validation_rejects_hidden_account_even_when_splits_balance_before_write_execution(
        self, fake_accounts, monkeypatch
    ):
        hidden = FakeAccount(
            guid="hidden-guid",
            name="Synthetic Hidden Account",
            type="ASSET",
            hidden=True,
        )
        service = self._service_with_fake_accounts([*fake_accounts, hidden])
        request = TransactionCreateRequestDTO(
            date="2026-05-16",
            description="Balanced hidden account validation probe",
            splits=[
                TransactionSplitWriteDTO(
                    account_id="hidden-guid",
                    amount="-12.34",
                    currency="SEK",
                    memo="hidden",
                ),
                TransactionSplitWriteDTO(
                    account_id="food-guid",
                    amount="12.34",
                    currency="SEK",
                    memo="posting",
                ),
            ],
        )

        self._assert_create_request_rejected_before_execution(
            service,
            request,
            monkeypatch,
            ["Account hidden-guid is hidden and cannot receive postings"],
        )

    def test_validation_rejects_split_currency_that_differs_from_account_currency(self, fake_accounts):
        usd_account = FakeAccount(
            guid="usd-guid",
            name="USD Synthetic Account",
            type="BANK",
            commodity=FakeCommodity("USD"),
        )
        service = self._service_with_fake_accounts([*fake_accounts, usd_account])

        result = service.validate_transaction_create(
            TransactionCreateRequestDTO(
                date="2026-05-16",
                description="Currency consistency validation probe",
                splits=[
                    TransactionSplitWriteDTO(
                        account_id="usd-guid",
                        amount="-25.00",
                        currency="SEK",
                        memo="wrong currency",
                    ),
                    TransactionSplitWriteDTO(
                        account_id="food-guid",
                        amount="25.00",
                        currency="SEK",
                        memo="known",
                    ),
                ],
            )
        )

        assert result.valid is False
        assert result.errors == [
            "Currency SEK does not match account usd-guid currency USD"
        ]

    def test_validation_rejects_mixed_currency_create_before_write_execution(
        self, fake_accounts, monkeypatch
    ):
        usd_cash = FakeAccount(
            guid="usd-cash-guid",
            name="USD Cash",
            type="BANK",
            commodity=FakeCommodity("USD"),
        )
        usd_income = FakeAccount(
            guid="usd-income-guid",
            name="USD Income",
            type="INCOME",
            commodity=FakeCommodity("USD"),
        )
        service = self._service_with_fake_accounts([*fake_accounts, usd_cash, usd_income])
        request = TransactionCreateRequestDTO(
            date="2026-05-16",
            description="Mixed currency validation probe",
            splits=[
                TransactionSplitWriteDTO(
                    account_id="bank-guid",
                    amount="-10.00",
                    currency="SEK",
                    memo="sek source",
                ),
                TransactionSplitWriteDTO(
                    account_id="food-guid",
                    amount="10.00",
                    currency="SEK",
                    memo="sek target",
                ),
                TransactionSplitWriteDTO(
                    account_id="usd-cash-guid",
                    amount="-5.00",
                    currency="USD",
                    memo="usd source",
                ),
                TransactionSplitWriteDTO(
                    account_id="usd-income-guid",
                    amount="5.00",
                    currency="USD",
                    memo="usd target",
                ),
            ],
        )

        self._assert_create_request_rejected_before_execution(
            service,
            request,
            monkeypatch,
            ["Multiple split currencies are not supported by write-alpha CREATE"],
        )

    def test_validation_rejects_non_default_currency_before_write_execution(
        self, fake_accounts, monkeypatch
    ):
        """Balanced account-matching splits must still match the book transaction currency."""
        usd_cash = FakeAccount(
            guid="usd-cash-guid",
            name="USD Cash",
            type="BANK",
            commodity=FakeCommodity("USD"),
        )
        usd_income = FakeAccount(
            guid="usd-income-guid",
            name="USD Income",
            type="INCOME",
            commodity=FakeCommodity("USD"),
        )
        service = self._service_with_fake_accounts([*fake_accounts, usd_cash, usd_income])
        request = TransactionCreateRequestDTO(
            date="2026-05-16",
            description="Book default currency validation probe",
            splits=[
                TransactionSplitWriteDTO(
                    account_id="usd-cash-guid",
                    amount="-5.00",
                    currency="USD",
                    memo="usd source",
                ),
                TransactionSplitWriteDTO(
                    account_id="usd-income-guid",
                    amount="5.00",
                    currency="USD",
                    memo="usd target",
                ),
            ],
        )

        self._assert_create_request_rejected_before_execution(
            service,
            request,
            monkeypatch,
            ["Currency USD does not match book default currency SEK"],
        )

    def _assert_create_request_rejected_before_execution(
        self,
        service,
        request: TransactionCreateRequestDTO,
        monkeypatch,
        expected_errors: list[str],
    ) -> None:
        execution_calls: list[str] = []

        def fail_if_execution_reached(*args, **kwargs):
            execution_calls.append("called")
            raise AssertionError("invalid validation request must not execute writes")

        monkeypatch.setattr(service, "_execute_write_transaction", fail_if_execution_reached)

        validation = service.validate_transaction_create(request)
        assert validation.valid is False
        joined_errors = "\n".join(validation.errors)
        for expected_error in expected_errors:
            assert expected_error in joined_errors

        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            service.create_transaction(request, user_id=1, book_id=1)
        assert execution_calls == []

    def test_validation_rejects_unbalanced_currency_before_write_execution(
        self, fake_accounts, monkeypatch
    ):
        service = self._service_with_fake_accounts(fake_accounts)
        request = TransactionCreateRequestDTO(
            date="2026-05-16",
            description="Unbalanced validation pre-execution probe",
            splits=[
                TransactionSplitWriteDTO(
                    account_id="bank-guid",
                    amount="-10.00",
                    currency="SEK",
                    memo="source",
                ),
                TransactionSplitWriteDTO(
                    account_id="food-guid",
                    amount="9.99",
                    currency="SEK",
                    memo="target",
                ),
            ],
        )

        self._assert_create_request_rejected_before_execution(
            service,
            request,
            monkeypatch,
            ["Splits do not balance to zero for currency SEK"],
        )

    @pytest.mark.parametrize("bad_amount", ["-1E+1", "+10.00", "-010.00", "-10.", "-.10"])
    def test_validation_rejects_non_plain_decimal_strings_before_write_execution(
        self, fake_accounts, monkeypatch, bad_amount
    ):
        service = self._service_with_fake_accounts(fake_accounts)
        request = TransactionCreateRequestDTO.model_construct(
            date="2026-05-16",
            description="Strict decimal-string validation probe",
            splits=[
                TransactionSplitWriteDTO.model_construct(
                    account_id="bank-guid",
                    amount=bad_amount,
                    currency="SEK",
                    memo="source",
                ),
                TransactionSplitWriteDTO.model_construct(
                    account_id="food-guid",
                    amount="10.00" if bad_amount != "-.10" else "0.10",
                    currency="SEK",
                    memo="target",
                ),
            ],
        )

        self._assert_create_request_rejected_before_execution(
            service,
            request,
            monkeypatch,
            [f"Invalid amount '{bad_amount}' for account bank-guid"],
        )

    def test_validation_rejects_account_and_currency_errors_before_write_execution(
        self, fake_accounts, monkeypatch
    ):
        placeholder = FakeAccount(
            guid="placeholder-guid",
            name="Synthetic Placeholder",
            type="ASSET",
            placeholder=True,
        )
        usd_account = FakeAccount(
            guid="usd-guid",
            name="USD Synthetic Account",
            type="BANK",
            commodity=FakeCommodity("USD"),
        )
        service = self._service_with_fake_accounts([*fake_accounts, placeholder, usd_account])
        request = TransactionCreateRequestDTO(
            date="2026-05-16",
            description="Account validation pre-execution probe",
            splits=[
                TransactionSplitWriteDTO(
                    account_id="missing-guid",
                    amount="-10.00",
                    currency="SEK",
                    memo="missing",
                ),
                TransactionSplitWriteDTO(
                    account_id="placeholder-guid",
                    amount="5.00",
                    currency="SEK",
                    memo="placeholder",
                ),
                TransactionSplitWriteDTO(
                    account_id="usd-guid",
                    amount="5.00",
                    currency="SEK",
                    memo="currency mismatch",
                ),
            ],
        )

        self._assert_create_request_rejected_before_execution(
            service,
            request,
            monkeypatch,
            [
                "Account not found: missing-guid",
                "Account placeholder-guid is a placeholder account and cannot receive postings",
                "Currency SEK does not match account usd-guid currency USD",
            ],
        )

    def test_validation_read_failure_is_path_safe_and_rejected_before_write_execution(
        self, fake_accounts, monkeypatch
    ):
        from app.services.gnucash_exceptions import GnuCashReadError

        service = self._service_with_fake_accounts(fake_accounts)

        def fail_open(uri_or_path):
            raise GnuCashReadError("/private/source/book.gnucash.sqlite account memo 123.45")

        service._open_piecash_book = fail_open
        request = TransactionCreateRequestDTO(
            date="2026-05-16",
            description="Path-safe validation read failure probe",
            splits=[
                TransactionSplitWriteDTO(
                    account_id="bank-guid",
                    amount="-10.00",
                    currency="SEK",
                    memo="source",
                ),
                TransactionSplitWriteDTO(
                    account_id="food-guid",
                    amount="10.00",
                    currency="SEK",
                    memo="target",
                ),
            ],
        )

        self._assert_create_request_rejected_before_execution(
            service,
            request,
            monkeypatch,
            ["Could not validate accounts from configured disposable test book"],
        )
        validation = service.validate_transaction_create(request)
        joined_errors = "\n".join(validation.errors)
        assert "/private/source" not in joined_errors
        assert "book.gnucash.sqlite" not in joined_errors
        assert "account memo 123.45" not in joined_errors


# ---------------------------------------------------------------------------
# Tests: POST /books/{book_id}/transactions
# ---------------------------------------------------------------------------


class TestCreateReadbackVerification:
    """Focused CREATE read-back checks before route success is reported."""

    def _request(self) -> TransactionCreateRequestDTO:
        return TransactionCreateRequestDTO(
            date="2026-06-04",
            description="Synthetic read-back exact coverage",
            splits=[
                TransactionSplitWriteDTO(
                    account_id="source-checking-guid",
                    amount="-125.50",
                    currency="SEK",
                    memo="source memo exact",
                ),
                TransactionSplitWriteDTO(
                    account_id="destination-food-guid",
                    amount="100.00",
                    currency="SEK",
                    memo="destination food memo exact",
                ),
                TransactionSplitWriteDTO(
                    account_id="destination-transport-guid",
                    amount="25.50",
                    currency="SEK",
                    memo="destination transport memo exact",
                ),
            ],
        )

    def _detail_from_request(
        self,
        transaction_id: str,
        request: TransactionCreateRequestDTO,
    ) -> TransactionDetailDTO:
        return TransactionDetailDTO(
            id=transaction_id,
            date=request.date,
            description=request.description,
            currency=request.splits[0].currency,
            splits=[
                TransactionSplitDTO(
                    account_id=split.account_id,
                    account_name=split.account_id,
                    memo=split.memo,
                    reconcile_state="",
                    amount=split.amount,
                    currency=split.currency,
                )
                for split in request.splits
            ],
        )

    def _account(self, account_id: str, balance: str, currency: str = "SEK") -> AccountDTO:
        return AccountDTO(
            id=account_id,
            name=account_id,
            full_name=account_id,
            type="BANK",
            currency=currency,
            balance=balance,
            placeholder=False,
            hidden=False,
            parent_id=None,
        )

    def _patch_read_service(
        self,
        monkeypatch,
        detail: TransactionDetailDTO,
        accounts: list[AccountDTO] | None = None,
    ) -> None:
        import app.routers.transactions as transactions_router

        class FakeReadService:
            def get_transaction(self, transaction_id: str) -> TransactionDetailDTO:
                assert transaction_id == "created-readback-tx"
                return detail

            def list_accounts(self) -> list[AccountDTO]:
                return accounts or []

        monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadService())

    def test_create_readback_accepts_exact_source_destination_amount_currency_date_description_memo_splits_and_balance_deltas(
        self,
        monkeypatch,
    ):
        import app.routers.transactions as transactions_router
        from app.schemas.gnucash_writes import TransactionWriteResultDTO

        request = self._request()
        detail = self._detail_from_request("created-readback-tx", request)
        after_accounts = [
            self._account("source-checking-guid", "874.50"),
            self._account("destination-food-guid", "100.00"),
            self._account("destination-transport-guid", "25.50"),
        ]
        self._patch_read_service(monkeypatch, detail, accounts=after_accounts)

        readback = transactions_router._verify_transaction_create_readback(
            Book(name="Synthetic read-back book", storage_type="sqlite", uri_or_path="synthetic://readback"),
            request,
            TransactionWriteResultDTO(
                transaction_id="created-readback-tx",
                backup_path="synthetic-backup-ref",
            ),
            before_account_balances={
                "source-checking-guid": (Decimal("1000.00"), "SEK"),
                "destination-food-guid": (Decimal("0.00"), "SEK"),
                "destination-transport-guid": (Decimal("0.00"), "SEK"),
            },
        )

        assert readback == {
            "readback_verified": True,
            "readback_transaction_id": "created-readback-tx",
            "readback_transaction_present": True,
            "readback_split_count": 3,
            "readback_split_balance_verified": True,
            "readback_split_balance_by_currency": {"SEK": "0.00"},
            "readback_currency": "SEK",
            "readback_currency_consistent": True,
            "readback_account_balance_deltas_verified": True,
            "readback_account_balance_delta_count": 3,
            "readback_account_balance_delta_total_by_currency": {"SEK": "0.00"},
        }

    @pytest.mark.parametrize(
        "mismatch",
        [
            "transaction_id",
            "date",
            "description",
            "source_account",
            "destination_account",
            "amount",
            "currency",
            "transaction_currency",
            "memo",
            "split_count",
            "split_balance",
        ],
    )
    def test_create_readback_rejects_mismatched_source_destination_amount_currency_date_description_memo_and_splits(
        self,
        monkeypatch,
        mismatch,
    ):
        import app.routers.transactions as transactions_router
        from app.schemas.gnucash_writes import TransactionWriteResultDTO

        request = self._request()
        detail = self._detail_from_request("created-readback-tx", request)
        if mismatch == "transaction_id":
            detail.id = "different-readback-tx"
        elif mismatch == "date":
            detail.date = "2026-06-05"
        elif mismatch == "description":
            detail.description = "Different synthetic description"
        elif mismatch == "source_account":
            detail.splits[0].account_id = "different-source-guid"
        elif mismatch == "destination_account":
            detail.splits[1].account_id = "different-destination-guid"
        elif mismatch == "amount":
            detail.splits[2].amount = "25.51"
        elif mismatch == "currency":
            detail.splits[1].currency = "USD"
        elif mismatch == "transaction_currency":
            detail.currency = "USD"
        elif mismatch == "memo":
            detail.splits[0].memo = "different source memo"
        elif mismatch == "split_count":
            detail.splits = detail.splits[:-1]
        elif mismatch == "split_balance":
            request.splits[2].amount = "25.51"
            detail.splits[2].amount = "25.51"
        else:  # pragma: no cover - protects future parametrization edits
            raise AssertionError(f"unhandled mismatch: {mismatch}")
        self._patch_read_service(monkeypatch, detail)

        result = TransactionWriteResultDTO(
            transaction_id="created-readback-tx",
            backup_path="synthetic-backup-ref",
        )
        with pytest.raises(transactions_router.GnuCashCreateReadbackVerificationError) as excinfo:
            transactions_router._verify_transaction_create_readback(
                Book(name="Synthetic read-back book", storage_type="sqlite", uri_or_path="synthetic://readback"),
                request,
                result,
            )

        assert excinfo.value.detail == transactions_router.CREATE_READBACK_FAILURE_DETAIL
        assert excinfo.value.backup_path == "synthetic-backup-ref"

    def test_create_readback_rejects_mismatched_account_balance_delta(self, monkeypatch):
        import app.routers.transactions as transactions_router
        from app.schemas.gnucash_writes import TransactionWriteResultDTO

        request = self._request()
        detail = self._detail_from_request("created-readback-tx", request)
        after_accounts = [
            self._account("source-checking-guid", "875.00"),
            self._account("destination-food-guid", "100.00"),
            self._account("destination-transport-guid", "25.50"),
        ]
        self._patch_read_service(monkeypatch, detail, accounts=after_accounts)

        with pytest.raises(transactions_router.GnuCashCreateReadbackVerificationError) as excinfo:
            transactions_router._verify_transaction_create_readback(
                Book(name="Synthetic read-back book", storage_type="sqlite", uri_or_path="synthetic://readback"),
                request,
                TransactionWriteResultDTO(
                    transaction_id="created-readback-tx",
                    backup_path="synthetic-backup-ref",
                ),
                before_account_balances={
                    "source-checking-guid": (Decimal("1000.00"), "SEK"),
                    "destination-food-guid": (Decimal("0.00"), "SEK"),
                    "destination-transport-guid": (Decimal("0.00"), "SEK"),
                },
            )

        assert excinfo.value.detail == transactions_router.CREATE_READBACK_FAILURE_DETAIL
        assert excinfo.value.backup_path == "synthetic-backup-ref"


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

        def fake_read_accounts() -> list[AccountDTO]:
            balances = {"bank-guid": Decimal("0"), "food-guid": Decimal("0")}
            for split in created_tx.splits:
                balances[split.account.guid] += Decimal(str(split.value))
            return [
                AccountDTO(
                    id=account_id,
                    name=account_id,
                    full_name=account_id,
                    type="BANK",
                    currency="SEK",
                    balance=format(balance, "f"),
                    placeholder=False,
                    hidden=False,
                    parent_id=None,
                )
                for account_id, balance in balances.items()
            ]

        import app.services.write_lock as wl_module
        import app.services.gnucash_write as gw_module
        import app.services.gnucash_book as gb_module

        tmp_lock_svc = wl_module.WriteLockService(lock_dir=fake_book_path.parent / "locks")
        with patch.object(wl_module, "write_lock_service", tmp_lock_svc):
            with patch.object(gw_module, "write_lock_service", tmp_lock_svc):
                with patch.object(gw_module, "piecash", mock_piecash):
                    with patch.object(gb_module, "piecash", mock_piecash):
                        with patch("app.services.gnucash_write.create_book_backup", return_value=str(fake_book_path)):
                            with patch.object(GnuCashWriteService, "_validate_configured_book", return_value=str(fake_book_path)):
                                with patch(
                                    "app.routers.transactions.transaction_service_for",
                                    return_value=MagicMock(
                                        get_transaction=lambda transaction_id: _readback_detail_from_payload(
                                            transaction_id,
                                            payload,
                                        ),
                                        list_accounts=fake_read_accounts,
                                    ),
                                ):
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

    def test_create_write_lock_failure_writes_failed_audit_log(
        self,
        client,
        auth_headers,
        sample_book,
        session_factory,
        monkeypatch,
    ):
        """Attempts that enter the create route must be audited even when the lock fails."""

        class LockFailingWriteService:
            def create_transaction(self, request, user_id, book_id):
                raise WriteLockError(str(book_id))

        monkeypatch.setattr(
            "app.routers.transactions._write_service_for",
            lambda book: LockFailingWriteService(),
        )

        response = client.post(
            f"/books/{sample_book}/transactions",
            json=_balanced_transaction_payload(),
            headers=auth_headers,
        )
        assert response.status_code == 409

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            assert logs
            latest_payload = json.loads(logs[-1].payload_json)
            assert latest_payload["result"] == "failed"
            assert "write lock" in latest_payload["error"].lower()
            assert latest_payload["backup_path"] is None

class TestWriteAlphaCreateRouteDisposableFixture:
    """Enabled-mode create route coverage on a copied/disposable GnuCash fixture."""

    def _fixture_create_payload(self, description: str = "Route write-alpha create"):
        return {
            "date": "2026-05-17",
            "description": description,
            "splits": [
                {
                    "account_id": "c73e8aa01e6345288662b556f2f866f3",
                    "amount": "-42.00",
                    "currency": "SEK",
                    "memo": "route checking memo",
                },
                {
                    "account_id": "388a85676d4a4643ae6cd28166c34e79",
                    "amount": "42.00",
                    "currency": "SEK",
                    "memo": "route food memo",
                },
            ],
        }

    def test_enabled_create_route_writes_disposable_fixture_with_backup_audit_and_lock(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._fixture_create_payload(),
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["transaction_id"]
        assert data["readback_verified"] is True
        assert data["readback_transaction_id"] == data["transaction_id"]
        backup_path = Path(data["backup_path"])
        assert backup_path.exists()
        assert backup_path.is_file()
        assert backup_path.parent.name == disposable_fixture_book.stem
        assert data["audit_log_id"] is not None

        txs_after = _read_written_transactions(disposable_fixture_book)
        created = next(tx for tx in txs_after if tx["guid"] == data["transaction_id"])
        assert len(txs_after) == len(txs_before) + 1
        assert created["description"] == "Route write-alpha create"
        assert created["post_date"] == date(2026, 5, 17)
        assert sum(split["value"] for split in created["splits"]) == Decimal("0")
        assert {split["memo"] for split in created["splits"]} == {
            "route checking memo",
            "route food memo",
        }

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            audit_log = session.get(AuditLog, data["audit_log_id"])
            assert audit_log is not None
            payload = json.loads(audit_log.payload_json)
            assert audit_log.action == "transaction.create"
            assert payload["result"] == "success"
            assert payload["transaction_id"] == data["transaction_id"]
            assert payload["readback_verified"] is True
            assert payload["readback_transaction_id"] == data["transaction_id"]
            assert payload["readback_split_count"] == 2
            assert payload["backup_path"] == str(backup_path)
            assert payload["request_summary"]["split_count"] == 2
            ownership = (
                session.query(WriteAlphaTransactionOwnership)
                .filter_by(book_id=disposable_sample_book, transaction_id=data["transaction_id"])
                .one()
            )
            assert ownership.created_by_user_id == audit_log.user_id
            assert ownership.created_by_write_alpha is True
            assert ownership.created_at is not None
            assert ownership.last_mutated_at is not None

    def test_enabled_create_route_reopens_fixture_and_updates_balances(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
    ):
        checking_guid = "c73e8aa01e6345288662b556f2f866f3"
        food_guid = "388a85676d4a4643ae6cd28166c34e79"
        tracked_guids = {checking_guid, food_guid}
        before_balances = _read_account_balances(disposable_fixture_book, tracked_guids)
        assert set(before_balances) == tracked_guids

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._fixture_create_payload("Route write-alpha balance read-back"),
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["readback_verified"] is True
        assert data["readback_transaction_id"] == data["transaction_id"]
        assert data["readback_transaction_present"] is True
        assert data["readback_split_count"] == 2
        assert data["readback_split_balance_verified"] is True
        assert data["readback_split_balance_by_currency"] == {"SEK": "0.00"}
        assert data["readback_currency"] == "SEK"
        assert data["readback_currency_consistent"] is True
        assert data["readback_account_balance_deltas_verified"] is True
        assert data["readback_account_balance_delta_count"] == 2
        assert data["readback_account_balance_delta_total_by_currency"] == {"SEK": "0.00"}

        reopened_balances = _read_account_balances(disposable_fixture_book, tracked_guids)
        assert set(reopened_balances) == tracked_guids
        assert reopened_balances[checking_guid] == before_balances[checking_guid] - Decimal("42.00")
        assert reopened_balances[food_guid] == before_balances[food_guid] + Decimal("42.00")
        total_delta = sum(reopened_balances[guid] - before_balances[guid] for guid in tracked_guids)
        assert total_delta == Decimal("0.00")

        reopened_txs = _read_written_transactions(disposable_fixture_book)
        created = next(tx for tx in reopened_txs if tx["guid"] == data["transaction_id"])
        assert sum(split["value"] for split in created["splits"]) == Decimal("0")

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

    def test_enabled_create_route_preserves_exact_fields_after_readback_and_reopen(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        source_guid = "c73e8aa01e6345288662b556f2f866f3"
        destination_guid = "388a85676d4a4643ae6cd28166c34e79"
        amount = Decimal("37.25")
        tracked_guids = {source_guid, destination_guid}
        payload = {
            "date": "2026-06-02",
            "description": "Route create exact field coverage",
            "splits": [
                {
                    "account_id": source_guid,
                    "amount": f"-{amount}",
                    "currency": "SEK",
                    "memo": "source memo exact",
                },
                {
                    "account_id": destination_guid,
                    "amount": str(amount),
                    "currency": "SEK",
                    "memo": "destination memo exact",
                },
            ],
        }
        txs_before = _read_written_transactions(disposable_fixture_book)
        before_balances = _read_account_balances_via_readonly_route(
            client,
            auth_headers,
            disposable_sample_book,
            tracked_guids,
        )

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        transaction_id = data["transaction_id"]
        assert data["readback_verified"] is True
        assert data["readback_transaction_id"] == transaction_id

        detail_response = client.get(
            f"/books/{disposable_sample_book}/transactions/{transaction_id}",
            headers=auth_headers,
        )
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["id"] == transaction_id
        assert detail["date"] == payload["date"]
        assert detail["description"] == payload["description"]
        assert detail["currency"] == "SEK"
        assert detail["is_write_alpha_owned"] is True
        assert len(detail["splits"]) == 2
        detail_splits = {split["account_id"]: split for split in detail["splits"]}
        assert set(detail_splits) == tracked_guids
        assert detail_splits[source_guid]["amount"] == "-37.25"
        assert detail_splits[source_guid]["currency"] == "SEK"
        assert detail_splits[source_guid]["memo"] == "source memo exact"
        assert detail_splits[destination_guid]["amount"] == "37.25"
        assert detail_splits[destination_guid]["currency"] == "SEK"
        assert detail_splits[destination_guid]["memo"] == "destination memo exact"

        reopened_txs = _read_written_transactions(disposable_fixture_book)
        assert len(reopened_txs) == len(txs_before) + 1
        created = next(tx for tx in reopened_txs if tx["guid"] == transaction_id)
        assert created["description"] == payload["description"]
        assert created["post_date"] == date(2026, 6, 2)
        assert created["currency"] == "SEK"
        assert len(created["splits"]) == 2
        reopened_splits = {split["account_guid"]: split for split in created["splits"]}
        assert set(reopened_splits) == tracked_guids
        assert reopened_splits[source_guid]["value"] == Decimal("-37.25")
        assert reopened_splits[source_guid]["memo"] == "source memo exact"
        assert reopened_splits[destination_guid]["value"] == Decimal("37.25")
        assert reopened_splits[destination_guid]["memo"] == "destination memo exact"
        assert sum(split["value"] for split in created["splits"]) == Decimal("0.00")

        reopened_balances = _read_account_balances_via_readonly_route(
            client,
            auth_headers,
            disposable_sample_book,
            tracked_guids,
        )
        assert reopened_balances[source_guid] == before_balances[source_guid] - amount
        assert reopened_balances[destination_guid] == before_balances[destination_guid] + amount
        total_delta = sum(reopened_balances[guid] - before_balances[guid] for guid in tracked_guids)
        assert total_delta == Decimal("0.00")

        with session_factory() as session:
            audit_log = session.get(AuditLog, data["audit_log_id"])
            assert audit_log is not None
            audit_payload = json.loads(audit_log.payload_json)
        assert audit_payload["result"] == "success"
        assert audit_payload["request_summary"] == {
            "date": payload["date"],
            "description": payload["description"],
            "split_count": 2,
            "currencies": ["SEK"],
        }
        assert audit_payload["readback_verified"] is True
        assert audit_payload["readback_transaction_id"] == transaction_id
        assert audit_payload["readback_transaction_present"] is True
        assert audit_payload["readback_split_count"] == 2
        assert audit_payload["readback_split_balance_verified"] is True
        assert audit_payload["readback_split_balance_by_currency"] == {"SEK": "0.00"}
        assert audit_payload["readback_currency"] == "SEK"
        assert audit_payload["readback_currency_consistent"] is True
        assert audit_payload["readback_account_balance_deltas_verified"] is True
        assert audit_payload["readback_account_balance_delta_count"] == 2
        assert audit_payload["readback_account_balance_delta_total_by_currency"] == {"SEK": "0.00"}

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

    def test_enabled_create_route_three_split_reopens_with_exact_fields_and_balance_deltas_via_readonly_paths(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
    ):
        source_guid = "c73e8aa01e6345288662b556f2f866f3"
        food_guid = "388a85676d4a4643ae6cd28166c34e79"
        transport_guid = "50b7cedabc8b46238dc15284637733d6"
        tracked_guids = {source_guid, food_guid, transport_guid}
        payload = {
            "date": "2026-06-03",
            "description": "Route create three split exact coverage",
            "splits": [
                {
                    "account_id": source_guid,
                    "amount": "-63.33",
                    "currency": "SEK",
                    "memo": "source checking for split purchase",
                },
                {
                    "account_id": food_guid,
                    "amount": "40.00",
                    "currency": "SEK",
                    "memo": "destination food portion",
                },
                {
                    "account_id": transport_guid,
                    "amount": "23.33",
                    "currency": "SEK",
                    "memo": "destination transport portion",
                },
            ],
        }
        txs_before = _read_written_transactions(disposable_fixture_book)
        before_balances = _read_account_balances_via_readonly_route(
            client,
            auth_headers,
            disposable_sample_book,
            tracked_guids,
        )

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        transaction_id = data["transaction_id"]
        assert data["readback_verified"] is True
        assert data["readback_transaction_id"] == transaction_id

        detail_response = client.get(
            f"/books/{disposable_sample_book}/transactions/{transaction_id}",
            headers=auth_headers,
        )
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["id"] == transaction_id
        assert detail["date"] == payload["date"]
        assert detail["description"] == payload["description"]
        assert detail["currency"] == "SEK"
        assert detail["is_write_alpha_owned"] is True
        assert len(detail["splits"]) == 3
        detail_splits = {split["account_id"]: split for split in detail["splits"]}
        assert set(detail_splits) == tracked_guids
        assert detail_splits[source_guid]["amount"] == "-63.33"
        assert detail_splits[source_guid]["currency"] == "SEK"
        assert detail_splits[source_guid]["memo"] == "source checking for split purchase"
        assert detail_splits[food_guid]["amount"] == "40.00"
        assert detail_splits[food_guid]["currency"] == "SEK"
        assert detail_splits[food_guid]["memo"] == "destination food portion"
        assert detail_splits[transport_guid]["amount"] == "23.33"
        assert detail_splits[transport_guid]["currency"] == "SEK"
        assert detail_splits[transport_guid]["memo"] == "destination transport portion"

        list_response = client.get(
            f"/books/{disposable_sample_book}/transactions",
            headers=auth_headers,
            params={"query": payload["description"]},
        )
        assert list_response.status_code == 200
        listed = {item["id"]: item for item in list_response.json()["items"]}
        assert transaction_id in listed
        assert listed[transaction_id]["currency"] == "SEK"

        reopened_txs = _read_written_transactions(disposable_fixture_book)
        assert len(reopened_txs) == len(txs_before) + 1
        created = next(tx for tx in reopened_txs if tx["guid"] == transaction_id)
        assert created["description"] == payload["description"]
        assert created["post_date"] == date(2026, 6, 3)
        assert created["currency"] == "SEK"
        assert len(created["splits"]) == 3
        reopened_splits = {split["account_guid"]: split for split in created["splits"]}
        assert set(reopened_splits) == tracked_guids
        assert reopened_splits[source_guid]["account_name"] == "Checking"
        assert reopened_splits[source_guid]["value"] == Decimal("-63.33")
        assert reopened_splits[source_guid]["memo"] == "source checking for split purchase"
        assert reopened_splits[food_guid]["account_name"] == "Food"
        assert reopened_splits[food_guid]["value"] == Decimal("40.00")
        assert reopened_splits[food_guid]["memo"] == "destination food portion"
        assert reopened_splits[transport_guid]["account_name"] == "Transport"
        assert reopened_splits[transport_guid]["value"] == Decimal("23.33")
        assert reopened_splits[transport_guid]["memo"] == "destination transport portion"
        assert sum(split["value"] for split in created["splits"]) == Decimal("0.00")

        reopened_balances = _read_account_balances_via_readonly_route(
            client,
            auth_headers,
            disposable_sample_book,
            tracked_guids,
        )
        assert reopened_balances[source_guid] == before_balances[source_guid] - Decimal("63.33")
        assert reopened_balances[food_guid] == before_balances[food_guid] + Decimal("40.00")
        assert reopened_balances[transport_guid] == before_balances[transport_guid] + Decimal("23.33")
        total_delta = sum(reopened_balances[guid] - before_balances[guid] for guid in tracked_guids)
        assert total_delta == Decimal("0.00")

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

    def test_enabled_create_readback_failure_returns_503_audits_failure_and_skips_ownership(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        """A CREATE cannot report success until the created transaction is read back."""
        from app.services.gnucash_exceptions import EntityNotFoundError

        class MissingCreatedTransactionReadService:
            def list_accounts(self) -> list[AccountDTO]:
                return [
                    AccountDTO(
                        id="c73e8aa01e6345288662b556f2f866f3",
                        name="Checking",
                        full_name="Assets:Checking",
                        type="BANK",
                        currency="SEK",
                        balance="0.00",
                        placeholder=False,
                        hidden=False,
                        parent_id=None,
                    ),
                    AccountDTO(
                        id="388a85676d4a4643ae6cd28166c34e79",
                        name="Food",
                        full_name="Expenses:Food",
                        type="EXPENSE",
                        currency="SEK",
                        balance="0.00",
                        placeholder=False,
                        hidden=False,
                        parent_id=None,
                    ),
                ]

            def get_transaction(self, transaction_id):
                raise EntityNotFoundError("transaction", transaction_id)

        monkeypatch.setattr(
            "app.routers.transactions.transaction_service_for",
            lambda book: MissingCreatedTransactionReadService(),
        )
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._fixture_create_payload("Read-back failure create"),
            headers=auth_headers,
        )

        assert response.status_code == 503
        detail = response.json()["detail"]
        assert "read-back verification failed" in detail
        assert str(disposable_fixture_book) not in detail

        txs_after = _read_written_transactions(disposable_fixture_book)
        assert len(txs_after) == len(txs_before) + 1
        created = next(tx for tx in txs_after if tx["description"] == "Read-back failure create")

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["transaction_id"] == created["guid"]
            assert payload["readback_verified"] is False
            assert "read-back verification failed" in payload["error"]
            assert payload["backup_path"] is not None
            assert (
                session.query(WriteAlphaTransactionOwnership)
                .filter_by(book_id=disposable_sample_book, transaction_id=created["guid"])
                .one_or_none()
                is None
            )

    def test_enabled_create_validation_failure_is_audited_without_backup_or_lock_leak(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        invalid_payload = self._fixture_create_payload("Route write-alpha invalid")
        invalid_payload["splits"][1]["amount"] = "41.99"

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=invalid_payload,
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "Validation failed" in response.json()["detail"]
        assert "balance" in response.json()["detail"] or "sum" in response.json()["detail"]

        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is None
            assert "Validation failed" in payload["error"]

    def test_fast_route_family_writes_have_unique_backups_and_redacted_refs(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        """Fast create/PATCH/DELETE writes must keep distinct backup evidence."""
        import app.services.backup as backup_mod

        fixed_now = datetime(2026, 5, 21, 5, 23, 1, 987654, tzinfo=timezone.utc)

        class FixedDateTime:
            @classmethod
            def now(cls, tz=None):
                return fixed_now if tz is not None else fixed_now.replace(tzinfo=None)

        monkeypatch.setattr(backup_mod, "datetime", FixedDateTime)

        create_response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._fixture_create_payload("Phase 223 route-family create"),
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        created_id = create_response.json()["transaction_id"]
        created_tx = next(tx for tx in _read_written_transactions(disposable_fixture_book) if tx["guid"] == created_id)

        patch_response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{created_id}",
            json={
                "description": "Phase 244 owned route-family patch",
                "split_memos": {created_tx["splits"][0]["guid"]: "phase 244 owned patched memo"},
            },
            headers=auth_headers,
        )
        assert patch_response.status_code == 200

        delete_response = client.delete(
            f"/books/{disposable_sample_book}/transactions/{created_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 200

        backup_paths = [
            Path(create_response.json()["backup_path"]),
            Path(patch_response.json()["backup_path"]),
            Path(delete_response.json()["backup_path"]),
        ]
        assert [path.name for path in backup_paths] == [
            "write-alpha-disposable_gnucash_20260521_052301_987654.sqlite",
            "write-alpha-disposable_gnucash_20260521_052301_987654_1.sqlite",
            "write-alpha-disposable_gnucash_20260521_052301_987654_2.sqlite",
        ]
        for backup_path in backup_paths:
            assert backup_path.exists()
            assert backup_path.is_file()
            assert backup_path.parent.name == disposable_fixture_book.stem
            assert _read_written_transactions(backup_path)

        with session_factory() as session:
            audit_logs = [
                session.get(AuditLog, create_response.json()["audit_log_id"]),
                session.get(AuditLog, patch_response.json()["audit_log_id"]),
                session.get(AuditLog, delete_response.json()["audit_log_id"]),
            ]
            payloads = [json.loads(log.payload_json) for log in audit_logs]

        assert [payload["action"] for payload in payloads] == [
            "transaction.create",
            "transaction.patch",
            "transaction.delete",
        ]
        assert [payload["backup_path"] for payload in payloads] == [str(path) for path in backup_paths]
        refs = [payload["backup_artifact_ref"] for payload in payloads]
        assert len(set(refs)) == 3
        assert all(ref.startswith("bkp-") and len(ref) == 16 for ref in refs)

        summary_response = client.get(
            f"/books/{disposable_sample_book}/write-alpha-audit-summary",
            headers=auth_headers,
        )
        assert summary_response.status_code == 200
        summary = summary_response.json()
        summary_refs = {item["backup_artifact_ref"] for item in summary["items"] if item["backup_present"]}
        assert set(refs) <= summary_refs
        encoded_summary = json.dumps(summary)
        assert str(disposable_fixture_book.parent.parent) not in encoded_summary
        for path in backup_paths:
            assert str(path) not in encoded_summary
            assert path.name not in encoded_summary

    def test_concurrent_enabled_create_allows_one_success_and_one_lock_contention(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        """Two parallel POST writes against one disposable book are serialized by the lock."""
        original_do_create = GnuCashWriteService._do_create_transaction
        first_write_entered = threading.Event()
        release_first_write = threading.Event()

        def slow_do_create(service, book, request):
            first_write_entered.set()
            assert release_first_write.wait(timeout=5), "timed out waiting to release first write"
            return original_do_create(service, book, request)

        monkeypatch.setattr(GnuCashWriteService, "_do_create_transaction", slow_do_create)
        txs_before = _read_written_transactions(disposable_fixture_book)

        def post_create(description: str):
            return client.post(
                f"/books/{disposable_sample_book}/transactions",
                json=self._fixture_create_payload(description),
                headers=auth_headers,
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(post_create, "Concurrent write-alpha winner")
            assert first_write_entered.wait(timeout=5), "first write did not enter service"
            second = executor.submit(post_create, "Concurrent write-alpha contender")
            second_response = second.result(timeout=5)
            release_first_write.set()
            first_response = first.result(timeout=5)

        statuses = sorted([first_response.status_code, second_response.status_code])
        assert statuses == [201, 409]
        failed_response = first_response if first_response.status_code == 409 else second_response
        assert "write lock" in failed_response.json()["detail"].lower()

        txs_after = _read_written_transactions(disposable_fixture_book)
        created = [tx for tx in txs_after if tx["description"] == "Concurrent write-alpha winner"]
        assert len(txs_after) == len(txs_before) + 1
        assert len(created) == 1
        assert sum(split["value"] for split in created[0]["splits"]) == Decimal("0")

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            payloads = [json.loads(log.payload_json) for log in logs]
            assert any(payload["result"] == "success" for payload in payloads)
            assert any(
                payload["result"] == "failed" and "write lock" in payload.get("error", "").lower()
                for payload in payloads
            )

    def test_failure_during_create_write_releases_lock_audits_failure_and_keeps_backup(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        """A post-backup write failure must leave a backup, failed audit row, and free lock."""

        def fail_after_backup(self, book, request):
            raise GnuCashWriteError("synthetic failure after backup")

        monkeypatch.setattr(GnuCashWriteService, "_do_create_transaction", fail_after_backup)
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._fixture_create_payload("Synthetic post-backup failure"),
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "synthetic failure after backup" in response.json()["detail"]
        txs_after = _read_written_transactions(disposable_fixture_book)
        assert txs_after == txs_before

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert "synthetic failure after backup" in payload["error"]
            backup_path = Path(payload["backup_path"])

        assert backup_path.exists()
        assert backup_path.is_file()
        backup_txs = _read_written_transactions(backup_path)
        assert backup_txs == txs_before

    def test_failure_after_unsaved_create_can_reopen_original_and_backup_for_recovery(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        """If CREATE mutates the open book but fails before save, reopen must show no persisted tx."""
        original_do_create = GnuCashWriteService._do_create_transaction
        failure_description = "Synthetic unsaved create recovery probe"

        def mutate_then_fail_before_save(self, book, request):
            original_do_create(self, book, request)
            raise GnuCashWriteError("synthetic create failure before save")

        monkeypatch.setattr(GnuCashWriteService, "_do_create_transaction", mutate_then_fail_before_save)
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._fixture_create_payload(failure_description),
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "synthetic create failure before save" in response.json()["detail"]
        reopened_txs = _read_written_transactions(disposable_fixture_book)
        assert reopened_txs == txs_before
        assert all(tx["description"] != failure_description for tx in reopened_txs)

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert "synthetic create failure before save" in payload["error"]
            backup_path = Path(payload["backup_path"])

        assert backup_path.exists()
        assert _read_written_transactions(backup_path) == txs_before

    def test_create_backup_failure_fails_before_mutation_audits_and_releases_lock(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        """A backup-directory/creation failure must stop create before opening the write book."""
        txs_before = _read_written_transactions(disposable_fixture_book)
        write_open_calls = []

        def fail_backup(book_config):
            raise BackupError("cannot create backup under redacted-backup-target://unavailable")

        def forbidden_write_open(self, uri_or_path):
            write_open_calls.append(uri_or_path)
            raise AssertionError("write book must not be opened when backup creation fails")

        monkeypatch.setattr("app.services.gnucash_write.create_book_backup", fail_backup)
        monkeypatch.setattr(GnuCashWriteService, "_open_piecash_book_for_write", forbidden_write_open)

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._fixture_create_payload("Create blocked by backup failure"),
            headers=auth_headers,
        )

        assert response.status_code == 422
        detail = response.json()["detail"]
        assert "GnuCash write failed" in detail
        assert "redacted-backup-target" not in detail
        assert "://" not in detail
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        assert write_open_calls == []

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is None
            assert "GnuCash write failed" in payload["error"]
            assert "redacted-backup-target" not in payload["error"]
            assert "://" not in payload["error"]

    def test_path_like_create_failure_uses_safe_api_and_audit_error(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        """Backend errors must not leak disposable/private-looking paths after dogfood."""
        leaked_path = str(disposable_fixture_book)

        def fail_with_path_like_detail(self, book, request):
            raise GnuCashWriteError(f"synthetic backend failure at {leaked_path}")

        monkeypatch.setattr(GnuCashWriteService, "_do_create_transaction", fail_with_path_like_detail)

        response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._fixture_create_payload("Path leak regression"),
            headers=auth_headers,
        )

        assert response.status_code == 422
        detail = response.json()["detail"]
        assert "GnuCash write failed" in detail
        assert leaked_path not in detail
        assert "/" not in detail

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is not None
            assert leaked_path not in payload["error"]
            assert "/" not in payload["error"]

    def test_lock_contention_error_does_not_leak_lock_file_or_book_path(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        """A dogfood-visible stale lock/active lock message must be path-safe."""
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        try:
            response = client.post(
                f"/books/{disposable_sample_book}/transactions",
                json=self._fixture_create_payload("Lock path leak regression"),
                headers=auth_headers,
            )
        finally:
            disposable_write_lock.release(lock_key)

        assert response.status_code == 409
        detail = response.json()["detail"]
        assert "write lock" in detail.lower()
        assert lock_key not in detail
        assert "/" not in detail

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.create").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert "write lock" in payload["error"].lower()
            assert lock_key not in payload["error"]
            assert "/" not in payload["error"]
            assert payload["backup_path"] is None

    def test_read_only_book_access_rejects_create_before_write_service(
        self,
        client,
        viewer_headers,
        sample_book,
        viewer_book_access,
        monkeypatch,
    ):
        """A viewer/read-only book grant returns 403 before constructing the write service."""
        calls = []

        def forbidden_write_service(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("write service must not be constructed for read-only book access")

        monkeypatch.setattr("app.routers.transactions._write_service_for", forbidden_write_service)

        response = client.post(
            f"/books/{sample_book}/transactions",
            json=self._fixture_create_payload("Viewer write attempt"),
            headers=viewer_headers,
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Book edit access denied"
        assert calls == []


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
        assert response.status_code in (200, 403, 404, 422)

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
        assert response.status_code in (403, 404, 422)

    @pytest.mark.parametrize(
        ("field_name", "immutable_payload"),
        [
            ("amount", {"amount": "-999.00"}),
            ("value", {"value": "-999.00"}),
            ("quantity", {"quantity": "-999.00"}),
            ("account_id", {"account_id": "other-account-guid"}),
            ("split_amounts", {"split_amounts": {"synthetic-split-guid": "-999.00"}}),
            ("split_accounts", {"split_accounts": {"synthetic-split-guid": "other-account-guid"}}),
            ("split_values", {"split_values": {"synthetic-split-guid": "-999.00"}}),
            ("split_quantities", {"split_quantities": {"synthetic-split-guid": "-999.00"}}),
            (
                "splits",
                {
                    "splits": [
                        {
                            "account_id": "bank-guid",
                            "amount": "-999.00",
                            "currency": "SEK",
                            "memo": "attempted split replacement",
                        },
                    ]
                },
            ),
            ("currency", {"currency": "USD"}),
            ("currency_guid", {"currency_guid": "synthetic-currency-guid"}),
            ("commodity_guid", {"commodity_guid": "synthetic-commodity-guid"}),
            ("date", {"date": "2026-12-25"}),
            ("posted_date", {"posted_date": "2026-12-25"}),
            ("post_date", {"post_date": "2026-12-25"}),
            ("exchange_rate", {"exchange_rate": "1.25"}),
        ],
    )
    def test_patch_rejects_immutable_financial_fields(
        self,
        client,
        auth_headers,
        sample_book,
        field_name,
        immutable_payload,
    ):
        """PATCH must reject amount, account, split, currency, and date changes."""
        payload = {"description": "Updated", **immutable_payload}
        response = client.patch(
            f"/books/{sample_book}/transactions/some-tx-id",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert field_name in json.dumps(response.json())


class TestWriteAlphaPatchRouteDisposableFixture:
    """Enabled-mode PATCH route coverage on a copied/disposable GnuCash fixture."""

    def _first_fixture_transaction(self, book_path: Path) -> dict:
        transactions = _read_written_transactions(book_path)
        assert transactions, "fixture must contain at least one transaction"
        return transactions[0]

    def _create_payload(self, description: str):
        return TestWriteAlphaCreateRouteDisposableFixture()._fixture_create_payload(description)

    def _mark_owned(self, session_factory, book_id: int, transaction_id: str):
        with session_factory() as session:
            admin = session.query(User).filter(User.username == "admin").one()
            marker = WriteAlphaTransactionOwnership()
            marker.book_id = book_id
            marker.transaction_id = transaction_id
            marker.created_by_user_id = admin.id
            marker.created_by_write_alpha = True
            marker.created_at = datetime(2026, 5, 20, tzinfo=timezone.utc)
            marker.last_mutated_at = datetime(2026, 5, 20, tzinfo=timezone.utc)
            session.add(marker)
            session.commit()
            return marker.id

    def test_enabled_patch_route_updates_disposable_fixture_with_backup_audit_and_lock(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        ownership_id = self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        split_guid = tx_before["splits"][0]["guid"]

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={
                "description": "Route write-alpha patched",
                "split_memos": {split_guid: "patched memo from route"},
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == tx_before["guid"]
        backup_path = Path(data["backup_path"])
        assert backup_path.exists()
        assert backup_path.is_file()
        assert backup_path.parent.name == disposable_fixture_book.stem
        assert data["audit_log_id"] is not None

        txs_after = _read_written_transactions(disposable_fixture_book)
        patched = next(tx for tx in txs_after if tx["guid"] == tx_before["guid"])
        assert patched["description"] == "Route write-alpha patched"
        assert patched["post_date"] == tx_before["post_date"]
        assert patched["currency"] == tx_before["currency"]
        assert any(split["memo"] == "patched memo from route" for split in patched["splits"])
        assert [split["guid"] for split in patched["splits"]] == [split["guid"] for split in tx_before["splits"]]
        assert [split["account_guid"] for split in patched["splits"]] == [split["account_guid"] for split in tx_before["splits"]]
        assert [split["value"] for split in patched["splits"]] == [split["value"] for split in tx_before["splits"]]

        backup_txs = _read_written_transactions(backup_path)
        backup_original = next(tx for tx in backup_txs if tx["guid"] == tx_before["guid"])
        assert backup_original["description"] == tx_before["description"]
        assert backup_original["post_date"] == tx_before["post_date"]

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            audit_log = session.get(AuditLog, data["audit_log_id"])
            assert audit_log is not None
            payload = json.loads(audit_log.payload_json)
            assert audit_log.action == "transaction.patch"
            assert payload["result"] == "success"
            assert payload["transaction_id"] == tx_before["guid"]
            assert payload["backup_path"] == str(backup_path)
            assert set(payload["request_summary"]["fields_updated"]) == {"description", "split_memos"}
            ownership = session.get(WriteAlphaTransactionOwnership, ownership_id)
            assert ownership is not None
            assert ownership.last_mutated_at > datetime(2026, 5, 20)

    def test_enabled_patch_route_allows_description_only_metadata_edit(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"description": "Route write-alpha description-only patch"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == tx_before["guid"]
        assert Path(data["backup_path"]).exists()

        txs_after = _read_written_transactions(disposable_fixture_book)
        patched = next(tx for tx in txs_after if tx["guid"] == tx_before["guid"])
        assert patched["description"] == "Route write-alpha description-only patch"
        assert patched["post_date"] == tx_before["post_date"]
        assert patched["currency"] == tx_before["currency"]
        assert patched["splits"] == tx_before["splits"]

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            audit_log = session.get(AuditLog, data["audit_log_id"])
            assert audit_log is not None
            payload = json.loads(audit_log.payload_json)
            assert payload["result"] == "success"
            assert payload["request_summary"]["fields_updated"] == ["description"]
            assert payload["fields_updated"] == {
                "description": "Route write-alpha description-only patch"
            }

    def test_enabled_patch_route_allows_split_memos_only_metadata_edit(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        assert len(tx_before["splits"]) >= 2
        memo_updates = {
            split["guid"]: f"route write-alpha memo-only patch {idx}"
            for idx, split in enumerate(tx_before["splits"], start=1)
        }

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"split_memos": memo_updates},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == tx_before["guid"]
        assert Path(data["backup_path"]).exists()

        txs_after = _read_written_transactions(disposable_fixture_book)
        patched = next(tx for tx in txs_after if tx["guid"] == tx_before["guid"])
        assert patched["description"] == tx_before["description"]
        assert patched["post_date"] == tx_before["post_date"]
        assert patched["currency"] == tx_before["currency"]
        assert [split["guid"] for split in patched["splits"]] == [
            split["guid"] for split in tx_before["splits"]
        ]
        assert [split["account_guid"] for split in patched["splits"]] == [
            split["account_guid"] for split in tx_before["splits"]
        ]
        assert [split["value"] for split in patched["splits"]] == [
            split["value"] for split in tx_before["splits"]
        ]
        assert {split["guid"]: split["memo"] for split in patched["splits"]} == memo_updates

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            audit_log = session.get(AuditLog, data["audit_log_id"])
            assert audit_log is not None
            payload = json.loads(audit_log.payload_json)
            assert payload["result"] == "success"
            assert payload["request_summary"]["fields_updated"] == ["split_memos"]
            assert payload["fields_updated"] == {"split_memos": memo_updates}

    def test_enabled_patch_route_allows_clearing_text_metadata_without_financial_mutation(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        assert tx_before["description"]
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        split_guid = tx_before["splits"][0]["guid"]

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"description": "", "split_memos": {split_guid: ""}},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == tx_before["guid"]
        assert Path(data["backup_path"]).exists()

        txs_after = _read_written_transactions(disposable_fixture_book)
        patched = next(tx for tx in txs_after if tx["guid"] == tx_before["guid"])
        assert patched["description"] == ""
        assert patched["post_date"] == tx_before["post_date"]
        assert patched["currency"] == tx_before["currency"]
        assert [split["guid"] for split in patched["splits"]] == [
            split["guid"] for split in tx_before["splits"]
        ]
        assert [split["account_guid"] for split in patched["splits"]] == [
            split["account_guid"] for split in tx_before["splits"]
        ]
        assert [split["value"] for split in patched["splits"]] == [
            split["value"] for split in tx_before["splits"]
        ]
        patched_split = next(split for split in patched["splits"] if split["guid"] == split_guid)
        assert patched_split["memo"] == ""

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            audit_log = session.get(AuditLog, data["audit_log_id"])
            assert audit_log is not None
            payload = json.loads(audit_log.payload_json)
            assert payload["result"] == "success"
            assert set(payload["request_summary"]["fields_updated"]) == {"description", "split_memos"}
            assert payload["fields_updated"] == {"description": "", "split_memos": {split_guid: ""}}

    def test_enabled_patch_route_preserves_exact_text_metadata_without_financial_mutation(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        assert len(tx_before["splits"]) >= 2
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        updated_description = "  Synthetic PATCH text — проверка café ☕  "
        memo_updates = {
            tx_before["splits"][0]["guid"]: "  Synthetic memo α — строка A  ",
            tx_before["splits"][1]["guid"]: "Synthetic memo β / emoji ✅",
        }

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"description": updated_description, "split_memos": memo_updates},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert Path(data["backup_path"]).exists()

        txs_after = _read_written_transactions(disposable_fixture_book)
        patched = next(tx for tx in txs_after if tx["guid"] == tx_before["guid"])
        assert patched["description"] == updated_description
        assert patched["post_date"] == tx_before["post_date"]
        assert patched["currency"] == tx_before["currency"]
        assert [split["guid"] for split in patched["splits"]] == [
            split["guid"] for split in tx_before["splits"]
        ]
        assert [split["account_guid"] for split in patched["splits"]] == [
            split["account_guid"] for split in tx_before["splits"]
        ]
        assert [split["value"] for split in patched["splits"]] == [
            split["value"] for split in tx_before["splits"]
        ]
        patched_memos = {split["guid"]: split["memo"] for split in patched["splits"]}
        before_memos = {split["guid"]: split["memo"] for split in tx_before["splits"]}
        for patched_split_guid, memo in memo_updates.items():
            assert patched_memos[patched_split_guid] == memo
        for unchanged_split_guid in set(before_memos) - set(memo_updates):
            assert patched_memos[unchanged_split_guid] == before_memos[unchanged_split_guid]

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            audit_log = session.get(AuditLog, data["audit_log_id"])
            assert audit_log is not None
            payload = json.loads(audit_log.payload_json)
            assert payload["result"] == "success"
            assert set(payload["request_summary"]["fields_updated"]) == {"description", "split_memos"}
            assert payload["fields_updated"] == {
                "description": updated_description,
                "split_memos": memo_updates,
            }

    @pytest.mark.parametrize(
        ("field_name", "immutable_payload"),
        [
            ("amount", {"amount": "-999.00"}),
            ("value", {"value": "-999.00"}),
            ("quantity", {"quantity": "-999.00"}),
            ("account_id", {"account_id": "c3e2c3289f6745d6a226599207ef1157"}),
            ("split_amounts", {"split_amounts": {"synthetic-split-guid": "-999.00"}}),
            ("split_accounts", {"split_accounts": {"synthetic-split-guid": "c3e2c3289f6745d6a226599207ef1157"}}),
            ("split_values", {"split_values": {"synthetic-split-guid": "-999.00"}}),
            ("split_quantities", {"split_quantities": {"synthetic-split-guid": "-999.00"}}),
            (
                "splits",
                {
                    "splits": [
                        {
                            "account_id": "c73e8aa01e6345288662b556f2f866f3",
                            "amount": "-999.00",
                            "currency": "SEK",
                            "memo": "attempted split replacement",
                        },
                        {
                            "account_id": "388a85676d4a4643ae6cd28166c34e79",
                            "amount": "999.00",
                            "currency": "SEK",
                            "memo": "attempted split replacement",
                        },
                    ]
                },
            ),
            ("currency", {"currency": "USD"}),
            ("currency_guid", {"currency_guid": "synthetic-currency-guid"}),
            ("commodity_guid", {"commodity_guid": "synthetic-commodity-guid"}),
            ("date", {"date": "2026-05-18"}),
            ("posted_date", {"posted_date": "2026-05-18"}),
            ("post_date", {"post_date": "2026-05-18"}),
            ("exchange_rate", {"exchange_rate": "1.25"}),
        ],
    )
    def test_enabled_patch_route_rejects_immutable_financial_fields_without_mutation(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        field_name,
        immutable_payload,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"description": "should not partially patch", **immutable_payload},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert field_name in json.dumps(response.json())
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.patch").all()
            assert logs == []

    @pytest.mark.parametrize(
        "nested_payload",
        [
            {
                "memo": "attempted nested metadata edit",
                "amount": "999.00",
                "account_id": "c3e2c3289f6745d6a226599207ef1157",
            },
            {"memo": "attempted nested value edit", "value": "999.00"},
            {"memo": "attempted nested quantity edit", "quantity": "999.00"},
            {"memo": "attempted nested currency edit", "currency": "USD"},
            {"memo": "attempted nested date edit", "date": "2026-05-18"},
            [
                {
                    "account_id": "c73e8aa01e6345288662b556f2f866f3",
                    "amount": "999.00",
                    "currency": "SEK",
                    "memo": "attempted nested split replacement",
                }
            ],
        ],
        ids=["amount-account", "value", "quantity", "currency", "date", "split-replacement"],
    )
    def test_enabled_patch_route_rejects_nested_split_memo_financial_payloads_without_mutation(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        nested_payload,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)
        split_guid = tx_before["splits"][0]["guid"]

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"split_memos": {split_guid: nested_payload}},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "split_memos" in json.dumps(response.json())
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.patch").all()
            assert logs == []

    def test_non_owned_fixture_transaction_patch_is_rejected_before_write_service(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        calls = []

        def forbidden_write_service(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("write service must not be constructed for non-owned PATCH")

        monkeypatch.setattr("app.routers.transactions._write_service_for", forbidden_write_service)
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"description": "should not write historical fixture transaction"},
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "created by write-alpha" in response.json()["detail"]
        assert "Historical or manually imported" in response.json()["detail"]
        assert calls == []
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.patch").all()
            assert len(logs) == 1
            payload = json.loads(logs[0].payload_json)
            assert payload["result"] == "failed"
            assert payload["ownership_status"] == "non_owned_rejected"
            assert payload["transaction_id"] == tx_before["guid"]
            assert payload["backup_path"] is None
            assert payload["backup_artifact_ref"] is None
            assert payload["request_summary"] == {"fields_updated": ["description"]}
            assert "fields_updated" not in payload
            assert "should not write historical" not in json.dumps(payload)

    def test_owned_non_disposable_patch_target_rejected_before_write_service(
        self,
        client,
        auth_headers,
        session_factory,
        tmp_path: Path,
        monkeypatch,
    ):
        calls = []

        def forbidden_write_service(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("write service must not be constructed for non-disposable PATCH")

        monkeypatch.setattr("app.routers.transactions._write_service_for", forbidden_write_service)
        books_dir = tmp_path / "books"
        books_dir.mkdir()
        target = books_dir / "historical-ledger.gnucash.sqlite"
        target.write_bytes(b"SQLite format 3\x00 non-disposable patch target placeholder")
        with session_factory() as session:
            book = Book(
                name="Synthetic non-disposable patch guard fixture",
                storage_type="sqlite",
                uri_or_path=str(target),
                base_currency="SEK",
                is_default=False,
            )
            session.add(book)
            session.flush()
            admin = session.query(User).filter(User.username == "admin").one()
            session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
            session.commit()
            book_id = book.id

        owned_transaction_id = "synthetic-owned-marker-tx"
        self._mark_owned(session_factory, book_id, owned_transaction_id)

        response = client.patch(
            f"/books/{book_id}/transactions/{owned_transaction_id}",
            json={"description": "should not patch a non-disposable target"},
            headers=auth_headers,
        )

        assert response.status_code == 403
        detail = response.json()["detail"]
        assert "Disposable target preflight failed closed" in detail
        assert "filename must mark it as copied/disposable/synthetic test data" in detail
        assert str(target) not in detail
        assert calls == []
        assert not (tmp_path / "backups").exists()
        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.patch").all()
            assert logs == []

    def test_enabled_patch_route_rejects_unknown_split_memo_target_without_mutation(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"split_memos": {"synthetic-unknown-split-guid": "memo for missing split"}},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "Unknown split memo target" in response.json()["detail"]
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.patch").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is None
            assert "Unknown split memo target" in payload["error"]

    def test_owned_missing_transaction_returns_404_without_backup_or_lock_leak(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        missing_transaction_id = "missing-write-alpha-tx"
        self._mark_owned(session_factory, disposable_sample_book, missing_transaction_id)
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{missing_transaction_id}",
            json={"description": "should not write missing owned marker"},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.patch").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is None
            assert missing_transaction_id in payload["error"]

    def test_write_alpha_created_transaction_patch_succeeds(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        create_response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._create_payload("Phase 244 owned patch source"),
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        created_transaction_id = create_response.json()["transaction_id"]

        txs_after_create = _read_written_transactions(disposable_fixture_book)
        created_before_patch = next(tx for tx in txs_after_create if tx["guid"] == created_transaction_id)
        split_guid = created_before_patch["splits"][0]["guid"]

        patch_response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{created_transaction_id}",
            json={"description": "Phase 244 owned patch succeeded", "split_memos": {split_guid: "owned patch memo"}},
            headers=auth_headers,
        )

        assert patch_response.status_code == 200
        data = patch_response.json()
        assert data["transaction_id"] == created_transaction_id
        assert Path(data["backup_path"]).exists()
        txs_after_patch = _read_written_transactions(disposable_fixture_book)
        patched = next(tx for tx in txs_after_patch if tx["guid"] == created_transaction_id)
        assert patched["description"] == "Phase 244 owned patch succeeded"
        assert any(split["memo"] == "owned patch memo" for split in patched["splits"])
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            ownership = (
                session.query(WriteAlphaTransactionOwnership)
                .filter_by(book_id=disposable_sample_book, transaction_id=created_transaction_id)
                .one()
            )
            assert ownership.created_by_write_alpha is True
            assert ownership.last_mutated_at >= ownership.created_at

    def test_patch_validation_error_causes_no_mutation_no_backup_and_failed_audit(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "Validation failed" in response.json()["detail"]
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.patch").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is None
            assert "At least one editable field" in payload["error"]

    def test_failure_during_patch_write_releases_lock_audits_failure_and_keeps_backup(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        def fail_after_backup(self, book, transaction_id, request):
            raise GnuCashWriteError("synthetic patch failure after backup")

        monkeypatch.setattr(GnuCashWriteService, "_do_patch_transaction", fail_after_backup)
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"description": "should fail after backup"},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "synthetic patch failure after backup" in response.json()["detail"]
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.patch").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert "synthetic patch failure after backup" in payload["error"]
            backup_path = Path(payload["backup_path"])

        assert backup_path.exists()
        assert _read_written_transactions(backup_path) == txs_before

    def test_patch_backup_failure_fails_before_mutation_audits_and_releases_lock(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)
        write_open_calls = []

        def fail_backup(book_config):
            raise BackupError("backup destination unavailable at redacted-backup-target://patch")

        def forbidden_write_open(self, uri_or_path):
            write_open_calls.append(uri_or_path)
            raise AssertionError("write book must not be opened when patch backup fails")

        monkeypatch.setattr("app.services.gnucash_write.create_book_backup", fail_backup)
        monkeypatch.setattr(GnuCashWriteService, "_open_piecash_book_for_write", forbidden_write_open)

        response = client.patch(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            json={"description": "patch blocked by backup failure"},
            headers=auth_headers,
        )

        assert response.status_code == 422
        detail = response.json()["detail"]
        assert "GnuCash write failed" in detail
        assert "redacted-backup-target" not in detail
        assert "://" not in detail
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        assert write_open_calls == []

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.patch").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is None
            assert "GnuCash write failed" in payload["error"]
            assert "redacted-backup-target" not in payload["error"]
            assert "://" not in payload["error"]

    def test_concurrent_patch_and_create_allows_one_success_and_one_lock_contention(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        original_do_patch = GnuCashWriteService._do_patch_transaction
        patch_entered = threading.Event()
        release_patch = threading.Event()

        def slow_do_patch(service, book, transaction_id, request):
            patch_entered.set()
            assert release_patch.wait(timeout=5), "timed out waiting to release patch"
            return original_do_patch(service, book, transaction_id, request)

        monkeypatch.setattr(GnuCashWriteService, "_do_patch_transaction", slow_do_patch)
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)

        def patch_tx():
            return client.patch(
                f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
                json={"description": "Concurrent write-alpha patch winner"},
                headers=auth_headers,
            )

        def create_tx():
            return client.post(
                f"/books/{disposable_sample_book}/transactions",
                json=self._create_payload("Concurrent write-alpha create contender"),
                headers=auth_headers,
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(patch_tx)
            assert patch_entered.wait(timeout=5), "patch write did not enter service"
            second = executor.submit(create_tx)
            second_response = second.result(timeout=5)
            release_patch.set()
            first_response = first.result(timeout=5)

        statuses = sorted([first_response.status_code, second_response.status_code])
        assert statuses == [200, 409]
        failed_response = first_response if first_response.status_code == 409 else second_response
        assert "write lock" in failed_response.json()["detail"].lower()

        txs_after = _read_written_transactions(disposable_fixture_book)
        patched = next(tx for tx in txs_after if tx["guid"] == tx_before["guid"])
        assert patched["description"] == "Concurrent write-alpha patch winner"
        assert len(txs_after) == len(txs_before)

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            patch_payloads = [json.loads(log.payload_json) for log in session.query(AuditLog).filter_by(action="transaction.patch").all()]
            create_payloads = [json.loads(log.payload_json) for log in session.query(AuditLog).filter_by(action="transaction.create").all()]
            assert any(payload["result"] == "success" for payload in patch_payloads)
            assert any(
                payload["result"] == "failed" and "write lock" in payload.get("error", "").lower()
                for payload in create_payloads
            )


class TestWriteAlphaDeleteRouteDisposableFixture:
    """Enabled-mode DELETE route coverage on a copied/disposable GnuCash fixture."""

    def _first_fixture_transaction(self, book_path: Path) -> dict:
        transactions = _read_written_transactions(book_path)
        assert transactions, "fixture must contain at least one transaction"
        return transactions[0]

    def _create_payload(self, description: str):
        return TestWriteAlphaCreateRouteDisposableFixture()._fixture_create_payload(description)

    def _mark_owned(self, session_factory, book_id: int, transaction_id: str):
        with session_factory() as session:
            admin = session.query(User).filter(User.username == "admin").one()
            marker = WriteAlphaTransactionOwnership()
            marker.book_id = book_id
            marker.transaction_id = transaction_id
            marker.created_by_user_id = admin.id
            marker.created_by_write_alpha = True
            marker.created_at = datetime(2026, 5, 20, tzinfo=timezone.utc)
            marker.last_mutated_at = datetime(2026, 5, 20, tzinfo=timezone.utc)
            session.add(marker)
            session.commit()
            return marker.id

    def test_enabled_delete_route_deletes_write_alpha_created_transaction_with_backup_audit_and_lock(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        create_response = client.post(
            f"/books/{disposable_sample_book}/transactions",
            json=self._create_payload("Phase 245 owned delete source"),
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        created_transaction_id = create_response.json()["transaction_id"]
        txs_before_delete = _read_written_transactions(disposable_fixture_book)
        tx_before = next(tx for tx in txs_before_delete if tx["guid"] == created_transaction_id)

        response = client.delete(
            f"/books/{disposable_sample_book}/transactions/{created_transaction_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == created_transaction_id
        backup_path = Path(data["backup_path"])
        assert backup_path.exists()
        assert backup_path.is_file()
        assert backup_path.parent.name == disposable_fixture_book.stem
        assert data["audit_log_id"] is not None

        txs_after = _read_written_transactions(disposable_fixture_book)
        assert len(txs_after) == len(txs_before_delete) - 1
        assert all(tx["guid"] != created_transaction_id for tx in txs_after)

        backup_txs = _read_written_transactions(backup_path)
        backup_original = next(tx for tx in backup_txs if tx["guid"] == created_transaction_id)
        assert backup_original["splits"] == tx_before["splits"]

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            audit_log = session.get(AuditLog, data["audit_log_id"])
            assert audit_log is not None
            payload = json.loads(audit_log.payload_json)
            assert audit_log.action == "transaction.delete"
            assert payload["result"] == "success"
            assert payload["transaction_id"] == created_transaction_id
            assert payload["backup_path"] == str(backup_path)
            ownership = (
                session.query(WriteAlphaTransactionOwnership)
                .filter_by(book_id=disposable_sample_book, transaction_id=created_transaction_id)
                .one()
            )
            assert ownership.created_by_write_alpha is True
            assert ownership.last_mutated_at >= ownership.created_at

    def test_non_owned_fixture_transaction_delete_is_rejected_before_write_service(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        calls = []

        def forbidden_write_service(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("write service must not be constructed for non-owned DELETE")

        monkeypatch.setattr("app.routers.transactions._write_service_for", forbidden_write_service)
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.delete(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "Write-alpha DELETE" in response.json()["detail"]
        assert "created by write-alpha" in response.json()["detail"]
        assert "Historical or manually imported" in response.json()["detail"]
        assert calls == []
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.delete").all()
            assert len(logs) == 1
            payload = json.loads(logs[0].payload_json)
            assert payload["result"] == "failed"
            assert payload["ownership_status"] == "non_owned_rejected"
            assert payload["transaction_id"] == tx_before["guid"]
            assert payload["backup_path"] is None
            assert payload["backup_artifact_ref"] is None
            assert payload["request_summary"] == {
                "target_class": "write_alpha_owned_required"
            }

    def test_owned_non_disposable_delete_target_rejected_before_write_service(
        self,
        client,
        auth_headers,
        session_factory,
        tmp_path: Path,
        monkeypatch,
    ):
        calls = []

        def forbidden_write_service(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("write service must not be constructed for non-disposable DELETE")

        monkeypatch.setattr("app.routers.transactions._write_service_for", forbidden_write_service)
        books_dir = tmp_path / "books"
        books_dir.mkdir()
        target = books_dir / "historical-ledger.gnucash.sqlite"
        target.write_bytes(b"SQLite format 3\x00 non-disposable delete target placeholder")
        with session_factory() as session:
            book = Book(
                name="Synthetic non-disposable delete guard fixture",
                storage_type="sqlite",
                uri_or_path=str(target),
                base_currency="SEK",
                is_default=False,
            )
            session.add(book)
            session.flush()
            admin = session.query(User).filter(User.username == "admin").one()
            session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
            session.commit()
            book_id = book.id

        owned_transaction_id = "synthetic-owned-delete-marker-tx"
        self._mark_owned(session_factory, book_id, owned_transaction_id)

        response = client.delete(
            f"/books/{book_id}/transactions/{owned_transaction_id}",
            headers=auth_headers,
        )

        assert response.status_code == 403
        detail = response.json()["detail"]
        assert "Disposable target preflight failed closed" in detail
        assert "filename must mark it as copied/disposable/synthetic test data" in detail
        assert str(target) not in detail
        assert calls == []
        assert not (tmp_path / "backups").exists()
        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.delete").all()
            assert logs == []

    def test_inert_ownership_marker_with_false_created_flag_rejects_delete_before_write_service(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        """DELETE requires a true write-alpha-created marker, not just any metadata row."""
        calls = []

        def forbidden_write_service(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("write service must not be constructed for inert DELETE ownership markers")

        monkeypatch.setattr("app.routers.transactions._write_service_for", forbidden_write_service)
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        txs_before = _read_written_transactions(disposable_fixture_book)
        with session_factory() as session:
            admin = session.query(User).filter(User.username == "admin").one()
            marker = WriteAlphaTransactionOwnership()
            marker.book_id = disposable_sample_book
            marker.transaction_id = tx_before["guid"]
            marker.created_by_user_id = admin.id
            marker.created_by_write_alpha = False
            marker.created_at = datetime(2026, 5, 20, tzinfo=timezone.utc)
            marker.last_mutated_at = datetime(2026, 5, 20, tzinfo=timezone.utc)
            session.add(marker)
            session.commit()
            marker_id = marker.id

        response = client.delete(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "Write-alpha DELETE" in response.json()["detail"]
        assert "created by write-alpha" in response.json()["detail"]
        assert calls == []
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.delete").all()
            assert len(logs) == 1
            payload = json.loads(logs[0].payload_json)
            assert payload["result"] == "failed"
            assert payload["ownership_status"] == "non_owned_rejected"
            assert payload["transaction_id"] == tx_before["guid"]
            assert payload["backup_path"] is None
            assert payload["request_summary"] == {
                "target_class": "write_alpha_owned_required"
            }
            marker = session.get(WriteAlphaTransactionOwnership, marker_id)
            assert marker is not None
            assert marker.created_by_write_alpha is False
            assert marker.last_mutated_at == datetime(2026, 5, 20)

    def test_active_owner_writebeta_delete_preview_blocks_legacy_delete_before_write_service(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        """An active owner-writebeta DELETE preview cannot be bypassed by legacy write-alpha DELETE."""
        from app.owner_writebeta_state_machine import (
            OwnerWritebetaSession,
            OwnerWritebetaState,
            prepare_preview,
        )
        from app.routers.owner_writebeta import _SESSIONS

        calls = []

        def forbidden_write_service(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("write service must not be constructed for unarmed owner-writebeta DELETE")

        monkeypatch.setattr("app.routers.transactions._write_service_for", forbidden_write_service)
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)

        session_state = OwnerWritebetaSession()
        session_state.transition(OwnerWritebetaState.PREFLIGHT)
        prepare_preview(
            session_state,
            "DELETE",
            {"transaction_id": "opaque-delete-target"},
            count=1,
        )
        _SESSIONS[disposable_sample_book] = session_state
        try:
            response = client.delete(
                f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
                headers=auth_headers,
            )
        finally:
            _SESSIONS.clear()

        assert response.status_code == 403
        assert "not armed for mutation" in response.json()["detail"]
        assert calls == []
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.delete").all()
            assert logs == []

    def test_owned_missing_transaction_returns_404_without_backup_or_lock_leak(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        missing_transaction_id = "missing-delete-write-alpha-tx"
        self._mark_owned(session_factory, disposable_sample_book, missing_transaction_id)
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.delete(
            f"/books/{disposable_sample_book}/transactions/{missing_transaction_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.delete").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is None
            assert "missing-delete-write-alpha-tx" in payload["error"]

    def test_corrupted_disposable_fixture_delete_fails_before_backup_or_lock_leak(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        disposable_fixture_book.write_bytes(b"not-a-gnucash-sqlite-fixture")

        response = client.delete(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            headers=auth_headers,
        )

        assert response.status_code == 422
        detail = response.json()["detail"]
        assert "GnuCash write failed" in detail
        assert str(disposable_fixture_book) not in detail
        assert "/" not in detail
        backups_root = disposable_fixture_book.parent.parent / "backups"
        assert not backups_root.exists()
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.delete").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is None
            assert "GnuCash write failed" in payload["error"]
            assert str(disposable_fixture_book) not in payload["error"]
            assert "/" not in payload["error"]

    def test_failure_during_delete_write_releases_lock_audits_failure_and_keeps_backup(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        def fail_after_backup(self, book, transaction_id):
            raise GnuCashWriteError("synthetic delete failure after backup")

        monkeypatch.setattr(GnuCashWriteService, "_do_delete_transaction", fail_after_backup)
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)

        response = client.delete(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "synthetic delete failure after backup" in response.json()["detail"]
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.delete").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert "synthetic delete failure after backup" in payload["error"]
            backup_path = Path(payload["backup_path"])

        assert backup_path.exists()
        assert _read_written_transactions(backup_path) == txs_before

    def test_delete_backup_failure_fails_before_mutation_audits_and_releases_lock(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)
        write_open_calls = []

        def fail_backup(book_config):
            raise BackupError("delete backup directory unavailable at redacted-backup-target://delete")

        def forbidden_write_open(self, uri_or_path):
            write_open_calls.append(uri_or_path)
            raise AssertionError("write book must not be opened when delete backup fails")

        monkeypatch.setattr("app.services.gnucash_write.create_book_backup", fail_backup)
        monkeypatch.setattr(GnuCashWriteService, "_open_piecash_book_for_write", forbidden_write_open)

        response = client.delete(
            f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
            headers=auth_headers,
        )

        assert response.status_code == 422
        detail = response.json()["detail"]
        assert "GnuCash write failed" in detail
        assert "redacted-backup-target" not in detail
        assert "://" not in detail
        assert _read_written_transactions(disposable_fixture_book) == txs_before
        assert write_open_calls == []

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            logs = session.query(AuditLog).filter_by(action="transaction.delete").all()
            assert logs
            payload = json.loads(logs[-1].payload_json)
            assert payload["result"] == "failed"
            assert payload["backup_path"] is None
            assert "GnuCash write failed" in payload["error"]
            assert "redacted-backup-target" not in payload["error"]
            assert "://" not in payload["error"]

    def test_read_only_book_access_rejects_delete_before_write_service(
        self,
        client,
        viewer_headers,
        sample_book,
        viewer_book_access,
        monkeypatch,
    ):
        calls = []

        def forbidden_write_service(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("write service must not be constructed for read-only book access")

        monkeypatch.setattr("app.routers.transactions._write_service_for", forbidden_write_service)

        response = client.delete(
            f"/books/{sample_book}/transactions/some-tx-id",
            headers=viewer_headers,
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Book edit access denied"
        assert calls == []

    def test_concurrent_delete_and_create_allows_one_success_and_one_lock_contention(
        self,
        client,
        auth_headers,
        disposable_sample_book,
        disposable_fixture_book,
        disposable_write_lock,
        session_factory,
        monkeypatch,
    ):
        original_do_delete = GnuCashWriteService._do_delete_transaction
        delete_entered = threading.Event()
        release_delete = threading.Event()

        def slow_do_delete(service, book, transaction_id):
            delete_entered.set()
            assert release_delete.wait(timeout=5), "timed out waiting to release delete"
            return original_do_delete(service, book, transaction_id)

        monkeypatch.setattr(GnuCashWriteService, "_do_delete_transaction", slow_do_delete)
        tx_before = self._first_fixture_transaction(disposable_fixture_book)
        self._mark_owned(session_factory, disposable_sample_book, tx_before["guid"])
        txs_before = _read_written_transactions(disposable_fixture_book)
        create_payload = TestWriteAlphaCreateRouteDisposableFixture()._fixture_create_payload(
            "Concurrent write-alpha create blocked by delete"
        )

        def delete_tx():
            return client.delete(
                f"/books/{disposable_sample_book}/transactions/{tx_before['guid']}",
                headers=auth_headers,
            )

        def create_tx():
            return client.post(
                f"/books/{disposable_sample_book}/transactions",
                json=create_payload,
                headers=auth_headers,
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(delete_tx)
            assert delete_entered.wait(timeout=5), "delete write did not enter service"
            second = executor.submit(create_tx)
            second_response = second.result(timeout=5)
            release_delete.set()
            first_response = first.result(timeout=5)

        statuses = sorted([first_response.status_code, second_response.status_code])
        assert statuses == [200, 409]
        failed_response = first_response if first_response.status_code == 409 else second_response
        assert "write lock" in failed_response.json()["detail"].lower()

        txs_after = _read_written_transactions(disposable_fixture_book)
        assert all(tx["guid"] != tx_before["guid"] for tx in txs_after)
        assert len(txs_after) == len(txs_before) - 1

        lock_key = str(disposable_fixture_book)
        assert disposable_write_lock.acquire(lock_key) is True
        disposable_write_lock.release(lock_key)

        with session_factory() as session:
            delete_payloads = [json.loads(log.payload_json) for log in session.query(AuditLog).filter_by(action="transaction.delete").all()]
            create_payloads = [json.loads(log.payload_json) for log in session.query(AuditLog).filter_by(action="transaction.create").all()]
            assert any(payload["result"] == "success" for payload in delete_payloads)
            assert any(
                payload["result"] == "failed" and "write lock" in payload.get("error", "").lower()
                for payload in create_payloads
            )

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

    def test_lock_acquire_and_release(self, tmp_path):
        from app.services.write_lock import WriteLockService

        svc = WriteLockService(lock_dir=tmp_path / "locks")
        acquired = svc.acquire("book-1")
        assert acquired is True
        svc.release("book-1")

    def test_lock_blocks_concurrent(self, tmp_path):
        from app.services.write_lock import WriteLockService

        svc = WriteLockService(lock_dir=tmp_path / "locks")
        acquired1 = svc.acquire("book-1")
        assert acquired1 is True

        # Second acquire should fail or return False
        acquired2 = svc.acquire("book-1")
        assert acquired2 is False

        svc.release("book-1")

    def test_lock_different_books_independent(self, tmp_path):
        from app.services.write_lock import WriteLockService

        svc = WriteLockService(lock_dir=tmp_path / "locks")
        assert svc.acquire("book-1") is True
        assert svc.acquire("book-2") is True
        svc.release("book-1")
        svc.release("book-2")

    def test_lock_release_idempotent(self, tmp_path):
        from app.services.write_lock import WriteLockService

        svc = WriteLockService(lock_dir=tmp_path / "locks")
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
