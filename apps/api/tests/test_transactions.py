"""Tests for transaction browsing API endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
import inspect
from pathlib import Path

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
# Fake GnuCash fixtures for transactions
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
    reconcile_state: str = "n"


@dataclass
class FakeTransaction:
    guid: str
    post_date: date
    description: str
    splits: list[FakeSplit]
    notes: str = ""


class FakeBookWithTransactions:
    def __init__(self, accounts=None, transactions=None):
        self.accounts = accounts or []
        self.transactions = transactions or []
        self.closed = False

    def close(self):
        self.closed = True


@pytest.fixture
def fake_transaction_data():
    root = FakeAccount(guid="root-guid", name="Assets", type="ROOT")
    bank = FakeAccount(guid="bank-guid", name="Bank", type="ASSET", parent=root)
    checking = FakeAccount(
        guid="checking-guid",
        name="Checking",
        type="BANK",
        parent=bank,
        balance=Decimal("12345.67"),
    )
    food = FakeAccount(guid="food-guid", name="Food", type="EXPENSE")
    tax = FakeAccount(guid="tax-guid", name="Tax", type="EXPENSE")

    split1_checking = FakeSplit(account=checking, value=Decimal("-320"), reconcile_state="c")
    split1_food = FakeSplit(account=food, value=Decimal("320"), memo="groceries", reconcile_state="c")
    tx1 = FakeTransaction(
        guid="tx-1",
        post_date=date(2026, 5, 16),
        description="ICA",
        splits=[split1_checking, split1_food],
    )

    split2_checking = FakeSplit(account=checking, value=Decimal("-50"))
    split2_tax = FakeSplit(account=tax, value=Decimal("10"))
    split2_food = FakeSplit(account=food, value=Decimal("40"))
    tx2 = FakeTransaction(
        guid="tx-2",
        post_date=date(2026, 5, 17),
        description="Split transaction test",
        splits=[split2_checking, split2_tax, split2_food],
        notes="Utility bill follow-up",
    )

    tx3 = FakeTransaction(
        guid="tx-3",
        post_date=date(2026, 5, 18),
        description="Salary",
        splits=[
            FakeSplit(account=checking, value=Decimal("5000"), reconcile_state="y"),
            FakeSplit(account=food, value=Decimal("-5000"), reconcile_state="y"),
        ],
    )

    accounts = [root, bank, checking, food, tax]
    transactions = [tx1, tx2, tx3]
    return accounts, transactions


@pytest.fixture
def fake_book_with_transactions(tmp_path, monkeypatch, fake_transaction_data):
    book_path = tmp_path / "test.gnucash"
    book_path.write_text("fake")
    accounts, transactions = fake_transaction_data

    def fake_open_book(path, readonly=False):
        return FakeBookWithTransactions(accounts=accounts, transactions=transactions)

    def fake_open_book_uri(*, uri_conn, readonly=False):
        return FakeBookWithTransactions(accounts=accounts, transactions=transactions)

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path




# ---------------------------------------------------------------------------
# Tests: POST /books/{book_id}/transactions/create-preview (non-mutating #48)
# ---------------------------------------------------------------------------


def _preview_payload(**overrides):
    payload = {
        "date": "2026-05-20",
        "debit_account_id": "checking-guid",
        "credit_account_id": "food-guid",
        "amount": "123.4500",
        "currency": "SEK",
        "description": "Preview only transaction",
        "memo": "optional memo",
    }
    payload.update(overrides)
    return payload


class TestTransactionCreateReadinessStatus:
    def guard_readiness_side_effect_helpers(self, monkeypatch):
        import app.routers.owner_writebeta as owner_writebeta_router
        import app.routers.transactions as transactions_router
        import app.services.gnucash_write as gnucash_write_module

        def fail_if_called(*args, **kwargs):
            raise AssertionError("readiness status must remain read-only and fail-closed")

        for guarded_name in (
            "transaction_service_for",
            "_resolve_readonly_data_book",
            "_require_book_edit_access",
            "_ensure_writes_enabled",
            "_ensure_write_alpha_test_scope",
            "_write_service_for",
            "_audit_log",
            "_update_audit_log",
            "_record_write_alpha_transaction_ownership",
            "_require_write_alpha_transaction_ownership",
            "_mark_write_alpha_transaction_mutated",
            "_backup_audit_fields",
            "_write_lock_detail",
        ):
            monkeypatch.setattr(transactions_router, guarded_name, fail_if_called)

        monkeypatch.setattr(owner_writebeta_router, "require_owner_writebeta_if_active", fail_if_called)
        monkeypatch.setattr(gnucash_write_module, "create_book_backup", fail_if_called)
        monkeypatch.setattr(gnucash_write_module.write_lock_service, "lock", fail_if_called)
        monkeypatch.setattr(gnucash_write_module.write_lock_service, "acquire", fail_if_called)
        monkeypatch.setattr(
            gnucash_write_module.GnuCashWriteService,
            "_open_piecash_book_for_write",
            fail_if_called,
        )

    def get_status(self, client, auth_headers, sample_book):
        return client.get(
            f"/books/{sample_book}/transactions/create-readiness-status",
            headers=auth_headers,
        )

    def test_default_status_is_redacted_disabled_and_does_not_probe_or_write(
        self, client, auth_headers, sample_book, session_factory, monkeypatch
    ):
        self.guard_readiness_side_effect_helpers(monkeypatch)

        response = self.get_status(client, auth_headers, sample_book)

        assert response.status_code == 200
        data = response.json()
        assert data["preview_only"] is True
        assert data["status"] == "disabled"
        assert data["writes_enabled"] is False
        assert data["session_armed"] is False
        assert data["create_execution_allowed"] is False
        assert data["create_execution_reason"] == "GNUCASH_WRITES_ENABLED=false; write session not armed."
        assert data["allowed_create_count"] == 0
        assert data["target_class"] is None
        assert data["readiness_required"] is True
        assert data["readiness_status"] == "not_checked"
        assert data["readiness_state"] == {
            "writes_enabled": {"enabled": False, "status": "disabled", "redacted": True},
            "session_armed": {"armed": False, "status": "not_armed", "redacted": True},
            "allowed_create_count": {"count": 0, "status": "blocked", "redacted": True},
            "target": {
                "target_class": None,
                "status": "not_selected",
                "private_target_probed": False,
                "redacted": True,
            },
            "preflight": {
                "required": True,
                "status": "not_checked",
                "private_target_probed": False,
                "redacted": True,
            },
            "backup": {
                "required": True,
                "status": "not_checked",
                "backup_helper_called": False,
                "redacted": True,
            },
            "allowed_execution": {
                "allowed": False,
                "status": "blocked",
                "reason": "GNUCASH_WRITES_ENABLED=false; write session not armed.",
                "redacted": True,
            },
        }
        assert [check["id"] for check in data["checks"]] == [
            "writes_enabled_state",
            "write_session_armed",
            "allowed_create_count_zero",
            "target_class_selected",
            "target_preflight_not_checked",
            "backup_readiness_not_checked",
            "allowed_execution_blocked",
            "reviewed_non_stale_preview",
            "backup_read_back_audit_reset_probes",
        ]
        assert {check["status"] for check in data["checks"]} == {"pending"}
        assert {check["redacted"] for check in data["checks"]} == {True}
        assert "No private target probing" in data["limitations"][1]
        serialized = str(data)
        assert "/data/books" not in serialized
        assert "test.gnucash" not in serialized
        with session_factory() as session:
            assert session.query(AuditLog).count() == 0
            assert session.query(WriteAlphaTransactionOwnership).count() == 0

    def test_status_remains_blocked_when_writes_enabled_setting_is_true(
        self, client, auth_headers, sample_book, monkeypatch
    ):
        enabled_settings = TEST_SETTINGS.model_copy(update={"gnucash_writes_enabled": True})
        app.dependency_overrides[get_settings] = lambda: enabled_settings
        self.guard_readiness_side_effect_helpers(monkeypatch)

        response = self.get_status(client, auth_headers, sample_book)

        assert response.status_code == 200
        data = response.json()
        assert data["writes_enabled"] is True
        assert data["session_armed"] is False
        assert data["create_execution_allowed"] is False
        assert data["allowed_create_count"] == 0
        assert data["target_class"] is None
        assert data["readiness_status"] == "not_checked"
        assert data["readiness_state"]["writes_enabled"] == {
            "enabled": True,
            "status": "enabled_but_blocked",
            "redacted": True,
        }
        assert data["readiness_state"]["allowed_execution"] == {
            "allowed": False,
            "status": "blocked",
            "reason": "Write gates may be enabled, but no owner-approved web UI CREATE session is armed.",
            "redacted": True,
        }

    def test_viewer_cannot_read_owner_create_readiness_status(
        self, client, viewer_headers, viewer_user, sample_book, session_factory
    ):
        with session_factory() as session:
            session.add(UserBookAccess(user_id=viewer_user, book_id=sample_book, role="viewer"))
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/create-readiness-status",
            headers=viewer_headers,
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Book owner access required"

    def test_create_readiness_source_shape_stays_read_only(self):
        import app.routers.transactions as transactions_router

        source = inspect.getsource(transactions_router.get_book_transaction_create_readiness_status)
        assert '"/books/{book_id}/transactions/create-readiness-status"' in source
        assert "_resolve_viewable_book" in source
        assert "_require_book_owner_access" in source
        assert "_build_create_readiness_status(settings)" in source
        for forbidden in (
            "transaction_service_for",
            "_resolve_readonly_data_book",
            "_require_book_edit_access",
            "_write_service_for",
            "GnuCashWriteService",
            "create_transaction",
            "validate_transaction_create",
            "patch_transaction",
            "delete_transaction",
            "_audit_log",
            "_update_audit_log",
            "create_book_backup",
            "write_lock_service",
            "_open_piecash_book_for_write",
            "require_owner_writebeta_if_active",
        ):
            assert forbidden not in source


class TestTransactionCreatePreview:
    def _set_fake_book(self, session_factory, sample_book, fake_book_with_transactions):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

    def post_preview(self, client, auth_headers, sample_book, payload):
        return client.post(
            f"/books/{sample_book}/transactions/create-preview",
            headers=auth_headers,
            json=payload,
        )

    def assert_no_preview_mutation_metadata(self, session_factory):
        with session_factory() as session:
            assert session.query(AuditLog).count() == 0
            assert session.query(WriteAlphaTransactionOwnership).count() == 0

    def guard_preview_mutation_helpers(
        self,
        monkeypatch,
        message="mutation/write path must not be reached for preview",
    ):
        import app.routers.transactions as transactions_router
        import app.services.gnucash_write as gnucash_write_module

        def fail_if_called(*args, **kwargs):
            raise AssertionError(message)

        for guarded_name in (
            "_ensure_writes_enabled",
            "_ensure_write_alpha_test_scope",
            "_write_service_for",
            "_audit_log",
            "_update_audit_log",
            "_record_write_alpha_transaction_ownership",
            "_require_write_alpha_transaction_ownership",
            "_mark_write_alpha_transaction_mutated",
            "_backup_audit_fields",
            "_write_lock_detail",
        ):
            monkeypatch.setattr(transactions_router, guarded_name, fail_if_called)

        monkeypatch.setattr(gnucash_write_module, "create_book_backup", fail_if_called)
        monkeypatch.setattr(gnucash_write_module.write_lock_service, "lock", fail_if_called)
        monkeypatch.setattr(gnucash_write_module.write_lock_service, "acquire", fail_if_called)
        monkeypatch.setattr(
            gnucash_write_module.GnuCashWriteService,
            "_open_piecash_book_for_write",
            fail_if_called,
        )

    def test_valid_preview_returns_normalized_private_preview_and_create_count_one(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)

        response = self.post_preview(client, auth_headers, sample_book, _preview_payload())

        assert response.status_code == 200
        data = response.json()
        assert data["preview_only"] is True
        assert data["create_count"] == 1
        assert data["date"] == "2026-05-20"
        assert data["amount"] == "123.4500"
        assert data["currency"] == "SEK"
        assert data["description"] == "Preview only transaction"
        assert data["memo"] == "optional memo"
        assert data["debit_account"]["id"] == "checking-guid"
        assert data["debit_account"]["full_name"] == "Assets:Bank:Checking"
        assert data["credit_account"]["id"] == "food-guid"
        assert data["splits"][0]["amount"] == "-123.4500"
        assert data["splits"][1]["amount"] == "123.4500"
        assert "no GnuCash write was executed" in data["warnings"][0]
        self.assert_no_preview_mutation_metadata(session_factory)

    def test_missing_book_rejected_before_preview_open_or_mutation(
        self, client, auth_headers, session_factory
    ):
        response = client.post(
            "/books/999999/transactions/create-preview",
            headers=auth_headers,
            json=_preview_payload(),
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Book not found"
        self.assert_no_preview_mutation_metadata(session_factory)

    def test_viewer_cannot_use_owner_preview_even_with_view_access(
        self, client, viewer_headers, viewer_user, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        with session_factory() as session:
            session.add(UserBookAccess(user_id=viewer_user, book_id=sample_book, role="viewer"))
            session.commit()

        response = self.post_preview(client, viewer_headers, sample_book, _preview_payload())

        assert response.status_code == 403
        assert response.json()["detail"] == "Book owner access required"
        self.assert_no_preview_mutation_metadata(session_factory)

    def test_missing_date_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(date=""))
        assert response.status_code == 422
        assert response.json()["detail"] == "date is required"

    def test_invalid_date_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(date="05/20/2026"))
        assert response.status_code == 422
        assert response.json()["detail"] == "date must use YYYY-MM-DD format"

    def test_missing_debit_account_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(debit_account_id=""))
        assert response.status_code == 422
        assert response.json()["detail"] == "debit_account_id is required"

    def test_missing_credit_account_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(credit_account_id=""))
        assert response.status_code == 422
        assert response.json()["detail"] == "credit_account_id is required"

    def test_unknown_debit_account_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(debit_account_id="unknown-debit-guid"))
        assert response.status_code == 422
        assert response.json()["detail"] == "debit_account_id was not found"
        self.assert_no_preview_mutation_metadata(session_factory)

    def test_unknown_credit_account_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(credit_account_id="unknown-credit-guid"))
        assert response.status_code == 422
        assert response.json()["detail"] == "credit_account_id was not found"
        self.assert_no_preview_mutation_metadata(session_factory)

    def test_same_debit_and_credit_account_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(
            client,
            auth_headers,
            sample_book,
            _preview_payload(credit_account_id="checking-guid"),
        )
        assert response.status_code == 422
        assert response.json()["detail"] == "debit and credit accounts must be different"

    def test_no_selectable_accounts_rejected_before_preview_values_are_built(
        self, client, auth_headers, sample_book, fake_book_with_transactions, fake_transaction_data, session_factory
    ):
        accounts, _transactions = fake_transaction_data
        for account in accounts:
            account.placeholder = True
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)

        response = self.post_preview(client, auth_headers, sample_book, _preview_payload())

        assert response.status_code == 422
        assert response.json()["detail"] == "no selectable accounts are available for preview"
        self.assert_no_preview_mutation_metadata(session_factory)

    def test_missing_amount_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(amount=""))
        assert response.status_code == 422

    def test_invalid_amount_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(amount="12.3.4"))
        assert response.status_code == 422

    def test_zero_amount_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(amount="0"))
        assert response.status_code == 422
        assert response.json()["detail"] == "amount must be greater than zero"

    def test_amount_is_not_converted_through_float(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(amount="0.100000000000000001"))
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "0.100000000000000001"
        assert data["splits"][0]["amount"] == "-0.100000000000000001"
        assert data["splits"][1]["amount"] == "0.100000000000000001"
        assert all(isinstance(split["amount"], str) for split in data["splits"])

    def test_amount_preserves_large_decimal_string_and_trailing_zeros(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        exact_amount = "999999999999999999.00000000000000000100"
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(amount=exact_amount))
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == exact_amount
        assert data["splits"][0]["amount"] == f"-{exact_amount}"
        assert data["splits"][1]["amount"] == exact_amount

    def test_missing_currency_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(currency=""))
        assert response.status_code == 422

    def test_unsupported_currency_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(currency="USD"))
        assert response.status_code == 422
        assert response.json()["detail"] == "debit account currency does not match requested currency"

    def test_credit_account_currency_mismatch_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, fake_transaction_data, session_factory
    ):
        accounts, _transactions = fake_transaction_data
        for account in accounts:
            if account.guid == "food-guid":
                account.commodity = FakeCommodity("USD")
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)

        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(currency="SEK"))

        assert response.status_code == 422
        assert response.json()["detail"] == "credit account currency does not match requested currency"
        self.assert_no_preview_mutation_metadata(session_factory)

    def test_missing_description_rejected(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload(description="   "))
        assert response.status_code == 422
        assert response.json()["detail"] == "description is required"

    def test_preview_endpoint_does_not_call_mutation_write_path(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory, monkeypatch
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        self.guard_preview_mutation_helpers(monkeypatch)

        response = self.post_preview(client, auth_headers, sample_book, _preview_payload())
        assert response.status_code == 200

    def test_preview_route_source_stays_readonly_create_preview_only(self):
        import app.routers.transactions as transactions_router

        source = inspect.getsource(transactions_router.preview_book_transaction_create)
        for required in (
            '"/books/{book_id}/transactions/create-preview"',
            "_resolve_readonly_data_book",
            "_require_book_owner_access",
            "transaction_service_for(book)",
            "service.list_accounts()",
            "_build_transaction_create_preview(request, accounts)",
        ):
            assert required in source

        for forbidden in (
            "_ensure_writes_enabled",
            "_ensure_write_alpha_test_scope",
            "_resolve_viewable_book",
            "_require_book_edit_access",
            "_write_service_for",
            "GnuCashWriteService",
            "create_transaction",
            "patch_transaction",
            "delete_transaction",
            "_audit_log",
            "_update_audit_log",
            "_record_write_alpha_transaction_ownership",
            "_require_write_alpha_transaction_ownership",
            "_mark_write_alpha_transaction_mutated",
            "_backup_audit_fields",
            "write_lock_service",
            "create_book_backup",
            "require_owner_writebeta_if_active",
        ):
            assert forbidden not in source

    def test_preview_works_with_writes_disabled_by_default(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        assert TEST_SETTINGS.gnucash_writes_enabled is False
        response = self.post_preview(client, auth_headers, sample_book, _preview_payload())
        assert response.status_code == 200

    def test_preview_read_error_returns_path_safe_503_without_mutation_helpers(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory, monkeypatch
    ):
        self._set_fake_book(session_factory, sample_book, fake_book_with_transactions)
        import app.routers.transactions as transactions_router
        from app.services.gnucash_exceptions import GnuCashReadError

        class FailingReadService:
            def list_accounts(self):
                raise GnuCashReadError("/synthetic/redacted/book/path account memo 123.45")

        monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FailingReadService())
        self.guard_preview_mutation_helpers(
            monkeypatch,
            message="mutation/write path must not be reached for preview read errors",
        )

        response = self.post_preview(client, auth_headers, sample_book, _preview_payload())

        assert response.status_code == 503
        assert response.json()["detail"] == "GnuCash book cannot be read safely from this runtime."
        assert "/synthetic/" not in str(response.json())
        self.assert_no_preview_mutation_metadata(session_factory)


# ---------------------------------------------------------------------------
# Tests: GET /transactions (MVP alias)
# ---------------------------------------------------------------------------


class TestListTransactionsMVP:
    def test_requires_auth(self, client):
        response = client.get("/transactions")
        assert response.status_code == 401

    def test_returns_paginated_transactions(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "limit" in data
        assert "offset" in data
        assert "total" in data
        assert data["total"] == 3
        assert data["limit"] == 50
        assert data["offset"] == 0
        assert len(data["items"]) == 3

    def test_pagination(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?limit=2&offset=0", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2

        response2 = client.get("/transactions?limit=2&offset=2", headers=auth_headers)
        data2 = response2.json()
        assert data2["total"] == 3
        assert len(data2["items"]) == 1

    def test_filter_by_query(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?query=ica", headers=auth_headers)
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["description"] == "ICA"

    def test_filter_by_query_matches_split_memo_and_counts_consistently(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?query=GROCERIES", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == ["tx-1"]

    def test_filter_by_query_matches_transaction_notes_and_counts_consistently(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?query=utility", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == ["tx-2"]

    def test_filter_by_date_range(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?date_from=2026-05-17&date_to=2026-05-17",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == "tx-2"

    def test_rejects_inverted_date_range(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?date_from=2026-05-18&date_to=2026-05-16",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "date_from cannot be later than date_to"

    def test_filter_by_account_id(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?account_id=checking-guid",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 3

    def test_filter_by_amount_range(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?account_id=checking-guid&min_amount=100&max_amount=400",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == "tx-1"
        assert data["items"][0]["amount"] == "-320.00"

    def test_rejects_inverted_amount_range(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?min_amount=400&max_amount=100",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "min_amount cannot be greater than max_amount"

    def test_filter_by_transaction_state_matches_split_reconciliation_state(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?transaction_state=cleared", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == ["tx-1"]

    def test_filter_by_transaction_state_respects_account_scope(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/accounts/checking-guid/transactions?transaction_state=reconciled",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == ["tx-3"]

    def test_rejects_unknown_transaction_state(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?transaction_state=maybe", headers=auth_headers)

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "transaction_state must be one of: cleared, reconciled, unreconciled, voided"
        )

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions", headers=viewer_headers)
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /transactions/{transaction_id} (MVP alias)
# ---------------------------------------------------------------------------


class TestGetTransactionMVP:
    def test_requires_auth(self, client):
        response = client.get("/transactions/some-id")
        assert response.status_code == 401

    def test_returns_transaction_detail(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions/tx-1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "tx-1"
        assert data["date"] == "2026-05-16"
        assert data["description"] == "ICA"
        assert data["currency"] == "SEK"
        assert data["is_write_alpha_owned"] is False
        assert len(data["splits"]) == 2
        assert data["splits"][0]["account_name"] == "Assets:Bank:Checking"
        assert data["splits"][0]["amount"] == "-320.00"
        assert data["splits"][0]["reconcile_state"] == "c"
        assert data["splits"][1]["memo"] == "groceries"
        assert data["splits"][1]["reconcile_state"] == "c"

    def test_unknown_transaction_returns_404(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_split_transaction_shows_all_splits(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions/tx-2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["splits"]) == 3

    def test_many_split_transaction_keeps_decimal_strings_and_reconciliation_states(
        self, client, auth_headers, sample_book, tmp_path, session_factory, monkeypatch
    ):
        root = FakeAccount(guid="root-guid", name="Root", type="ROOT")
        checking = FakeAccount(guid="checking-guid", name="Checking", type="BANK", parent=root)
        split_accounts = [
            FakeAccount(guid=f"expense-{index:02d}", name=f"Expense {index:02d}", type="EXPENSE", parent=root)
            for index in range(12)
        ]
        splits = [FakeSplit(account=checking, value=Decimal("-78.00"), reconcile_state="c")]
        splits.extend(
            FakeSplit(account=account, value=Decimal("6.50"), memo=f"line {index:02d}", reconcile_state="y")
            for index, account in enumerate(split_accounts)
        )
        transaction = FakeTransaction(
            guid="tx-many-splits",
            post_date=date(2026, 5, 19),
            description="Synthetic many split transaction",
            splits=splits,
        )
        book_path = tmp_path / "many-splits.gnucash"
        book_path.write_text("fake")

        def fake_open_book(path, readonly=False):
            assert readonly is True
            return FakeBookWithTransactions(accounts=[root, checking, *split_accounts], transactions=[transaction])

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(book_path)
            session.commit()

        response = client.get("/transactions/tx-many-splits", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["splits"]) == 13
        assert data["splits"][0]["amount"] == "-78.00"
        assert all(isinstance(split["amount"], str) for split in data["splits"])
        assert {split["reconcile_state"] for split in data["splits"]} == {"c", "y"}

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions/tx-1", headers=viewer_headers)
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /accounts/{account_id}/transactions (MVP alias)
# ---------------------------------------------------------------------------


class TestListAccountTransactionsMVP:
    def test_requires_auth(self, client):
        response = client.get("/accounts/some-id/transactions")
        assert response.status_code == 401

    def test_returns_account_transactions(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/accounts/checking-guid/transactions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for item in data["items"]:
            assert item["account_id"] == "checking-guid"

    def test_unknown_account_returns_empty(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/accounts/nonexistent-guid/transactions",
            headers=auth_headers,
        )
        # Unknown account_id used as filter returns empty list, not 404
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/transactions
# ---------------------------------------------------------------------------


class TestListBookTransactions:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/transactions")
        assert response.status_code == 401

    def test_returns_paginated_transactions(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions",
            headers=viewer_headers,
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/transactions/{transaction_id}
# ---------------------------------------------------------------------------


class TestGetBookTransaction:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/transactions/some-id")
        assert response.status_code == 401

    def test_returns_transaction_detail(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/tx-1",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "tx-1"
        assert data["is_write_alpha_owned"] is False
        assert len(data["splits"]) == 2

    def test_returns_write_alpha_owned_hint_for_app_metadata_owned_transaction(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            user = session.query(User).filter(User.username == "admin").one()
            session.add(
                WriteAlphaTransactionOwnership(
                    book_id=sample_book,
                    transaction_id="tx-1",
                    created_by_user_id=user.id,
                    created_by_write_alpha=True,
                )
            )
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/tx-1",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "tx-1"
        assert data["is_write_alpha_owned"] is True

    def test_unknown_transaction_returns_404(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/nonexistent",
            headers=auth_headers,
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/accounts/{account_id}/transactions
# ---------------------------------------------------------------------------


class TestListBookAccountTransactions:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/accounts/some-id/transactions")
        assert response.status_code == 401

    def test_returns_account_transactions(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/checking-guid/transactions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3

    def test_filters_stay_account_scoped_and_counts_match_items(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/food-guid/transactions?"
            "query=salary&date_from=2026-05-18&date_to=2026-05-18&"
            "transaction_state=reconciled&min_amount=1000&max_amount=6000",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == ["tx-3"]
        assert all(item["account_id"] == "food-guid" for item in data["items"])

    def test_account_scope_filter_does_not_leak_other_account_matches(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/tax-guid/transactions?query=salary",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_unknown_account_returns_empty(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/nonexistent-guid/transactions",
            headers=auth_headers,
        )
        # Unknown account_id used as filter returns empty list, not 404
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
