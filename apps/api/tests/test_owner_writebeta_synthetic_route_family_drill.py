"""#36-W2-A synthetic CREATE/PATCH/DELETE route-family drill.

All mutations in this file use an in-memory app DB and a fake write service.
No GnuCash book is opened or mutated.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import json
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
from app.schemas.gnucash import AccountDTO, TransactionDetailDTO, TransactionSplitDTO
from app.schemas.gnucash_writes import TransactionValidationResultDTO, TransactionWriteResultDTO
from app.services.auth import hash_password

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    app_admin_username="admin",
    app_admin_password="testpassword123",
    gnucash_writes_enabled=True,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def _account_dto(account_id: str, balance: Decimal | str = "0.00", currency: str = "SEK") -> AccountDTO:
    return AccountDTO(
        id=account_id,
        name=account_id,
        full_name=account_id,
        type="BANK",
        currency=currency,
        balance=str(balance),
        placeholder=False,
        hidden=False,
        parent_id=None,
    )


READ_ONLY_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    app_admin_username="admin",
    app_admin_password="testpassword123",
    gnucash_writes_enabled=False,
)


@dataclass
class FakeWriteService:
    calls: list[tuple[str, object]]

    def validate_transaction_create(self, request):
        self.calls.append(("validate", request))
        return TransactionValidationResultDTO(valid=True, errors=[], warnings=[], summary={"synthetic": True})

    def create_transaction(self, *, request, user_id: int, book_id: int):
        self.calls.append(("create", request))
        return TransactionWriteResultDTO(transaction_id="synthetic-created-tx", backup_path="backup-create-ref")

    def patch_transaction_metadata(self, *, transaction_id: str, request, user_id: int, book_id: int):
        self.calls.append(("patch", request))
        return TransactionWriteResultDTO(transaction_id=transaction_id, backup_path="backup-patch-ref")

    def delete_transaction(self, *, transaction_id: str, user_id: int, book_id: int):
        self.calls.append(("delete", transaction_id))
        return TransactionWriteResultDTO(transaction_id=transaction_id, backup_path="backup-delete-ref")


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def fake_write_calls(monkeypatch):
    calls: list[tuple[str, object]] = []

    def fake_write_service_for(book):
        target = Path(str(book.uri_or_path)).resolve()
        assert target.is_file()
        assert "disposable" in target.name
        with pytest.raises(ValueError):
            target.relative_to(REPO_ROOT)
        return FakeWriteService(calls)

    class FakeReadService:
        def list_accounts(self) -> list[AccountDTO]:
            balances = {
                "synthetic-bank": Decimal("0.00"),
                "synthetic-expense": Decimal("0.00"),
            }
            create_requests = [payload for name, payload in calls if name == "create"]
            if create_requests:
                for split in getattr(create_requests[-1], "splits", []):
                    balances[split.account_id] += Decimal(split.amount)
            return [_account_dto(account_id, balance) for account_id, balance in balances.items()]

        def get_transaction(self, transaction_id: str) -> TransactionDetailDTO:
            create_requests = [payload for name, payload in calls if name == "create"]
            assert create_requests, "read-back verification must follow a synthetic CREATE call"
            request = create_requests[-1]
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

    monkeypatch.setattr("app.routers.transactions._write_service_for", fake_write_service_for)
    monkeypatch.setattr("app.routers.transactions.transaction_service_for", lambda book: FakeReadService())
    return calls


@pytest.fixture
def client(session_factory, fake_write_calls):
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
    from app.routers.owner_writebeta import _SESSIONS

    _SESSIONS.clear()
    test_client = TestClient(app)
    yield test_client
    _SESSIONS.clear()
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def auth_headers(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "testpassword123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def synthetic_book(session_factory, tmp_path: Path):
    target = tmp_path / "owner-writebeta-disposable-route-family.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00 synthetic route-family placeholder")
    with session_factory() as session:
        book = Book(
            name="Synthetic owner-writebeta route-family fixture",
            storage_type="sqlite",
            uri_or_path=str(target),
            is_default=True,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


@pytest.fixture
def external_unproven_book(session_factory, tmp_path: Path):
    target = tmp_path / "owner-ledger.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00 unproven route-family placeholder")
    with session_factory() as session:
        book = Book(
            name="Unproven external route-family target",
            storage_type="sqlite",
            uri_or_path=str(target),
            is_default=False,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


def _synthetic_create_payload():
    return {
        "date": "2026-06-03",
        "description": "Synthetic route-family fixture",
        "splits": [
            {"account_id": "synthetic-bank", "amount": "-10.00", "currency": "SEK", "memo": ""},
            {"account_id": "synthetic-expense", "amount": "10.00", "currency": "SEK", "memo": ""},
        ],
    }


def _preview_confirm_headers(client: TestClient, auth_headers: dict[str, str], book_id: int, operation: str, *, target_owned: bool = False):
    preflight = client.post(f"/books/{book_id}/owner-writebeta/preflight", headers=auth_headers)
    assert preflight.status_code == 200
    preview = client.post(
        f"/books/{book_id}/owner-writebeta/preview",
        headers=auth_headers,
        json={
            "operation": operation,
            "payload_shape": {"synthetic_route_family": "shape-only"},
            "target_is_write_alpha_owned": target_owned,
            "metadata_only_patch": True,
        },
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]
    confirm = client.post(
        f"/books/{book_id}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview_hash,
            "backup_ref": f"bkp-{operation.lower()}-ref",
            "restore_readiness_ref": f"rr-{operation.lower()}-ref",
        },
    )
    assert confirm.status_code == 200
    return {
        **auth_headers,
        "X-Owner-Writebeta-Preview-Hash": preview_hash,
        "X-Owner-Writebeta-Confirmation-Token": confirm.json()["confirmation_token"],
    }


def _verify_and_reset(
    client: TestClient,
    auth_headers: dict[str, str],
    book_id: int,
    suffix: str,
    fake_write_calls: list[tuple[str, object]],
    expected_write_call_names: list[str],
):
    verify = client.post(
        f"/books/{book_id}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={
            "audit_ref": f"audit-{suffix}-ref",
            "restore_ref": f"restore-{suffix}-ref",
            "lock_released": True,
            "defaults_reset": True,
        },
    )
    assert verify.status_code == 200
    verify_payload = verify.json()
    assert verify_payload["state"] == "reset_required"
    assert verify_payload["writes_blocked"] is True
    assert "state_reset_required" in verify_payload["blocked_reasons"]
    assert verify_payload["summary"]["audit_ref"] == f"audit-{suffix}-ref"
    assert verify_payload["summary"]["restore_ref"] == f"restore-{suffix}-ref"
    assert verify_payload["summary"]["lock_released"] is True
    assert verify_payload["summary"]["defaults_reset"] is True
    assert verify_payload["summary"]["preview_hash"] is None
    assert verify_payload["summary"]["confirmation_token_ref"] is None
    assert verify_payload["summary"]["restore_readiness_ref"] is None

    app.dependency_overrides[get_settings] = lambda: READ_ONLY_SETTINGS
    try:
        reset = client.post(f"/books/{book_id}/owner-writebeta/reset-disabled", headers=auth_headers)
        assert reset.status_code == 200
        reset_payload = reset.json()
        assert reset_payload["state"] == "disabled"
        assert reset_payload["writes_blocked"] is True
        assert "writes_disabled_default" in reset_payload["blocked_reasons"]
        assert "writes_explicitly_enabled_runtime" not in reset_payload["pass_reasons"]
        assert reset_payload["summary"]["audit_ref"] == f"audit-{suffix}-ref"
        assert reset_payload["summary"]["restore_ref"] == f"restore-{suffix}-ref"
        assert reset_payload["summary"]["lock_released"] is True
        assert reset_payload["summary"]["defaults_reset"] is True
        assert reset_payload["summary"]["preview_hash"] is None
        assert reset_payload["summary"]["confirmation_token_ref"] is None
        assert reset_payload["summary"]["restore_readiness_ref"] is None

        _assert_default_disabled_route_family_probes(
            client,
            auth_headers,
            book_id,
            fake_write_calls,
            expected_write_call_names,
        )
    finally:
        app.dependency_overrides[get_settings] = lambda: TEST_SETTINGS


def _assert_default_disabled_route_family_probes(
    client: TestClient,
    auth_headers: dict[str, str],
    book_id: int,
    fake_write_calls: list[tuple[str, object]],
    expected_write_call_names: list[str],
) -> None:
    baseline_calls = list(fake_write_calls)
    assert [name for name, _ in baseline_calls] == expected_write_call_names

    status_check = client.get(f"/books/{book_id}/owner-writebeta/status", headers=auth_headers)
    assert status_check.status_code == 200
    status_payload = status_check.json()
    assert status_payload["state"] == "disabled"
    assert status_payload["writes_blocked"] is True
    assert "writes_disabled_default" in status_payload["blocked_reasons"]
    assert "writes_explicitly_enabled_runtime" not in status_payload["pass_reasons"]
    assert status_payload["summary"]["preview_hash"] is None
    assert status_payload["summary"]["confirmation_token_ref"] is None
    assert status_payload["summary"]["restore_readiness_ref"] is None

    readiness = client.get(f"/books/{book_id}/transactions/create-readiness-status", headers=auth_headers)
    assert readiness.status_code == 200
    readiness_payload = readiness.json()
    assert readiness_payload["status"] == "disabled"
    assert readiness_payload["writes_enabled"] is False
    assert readiness_payload["session_armed"] is False
    assert readiness_payload["create_execution_allowed"] is False
    assert readiness_payload["allowed_create_count"] == 0
    assert readiness_payload["readiness_state"]["preflight"]["status"] == "not_checked"
    assert readiness_payload["readiness_state"]["preflight"]["private_target_probed"] is False
    assert readiness_payload["readiness_state"]["backup"]["backup_helper_called"] is False
    assert readiness_payload["readiness_state"]["allowed_execution"]["status"] == "blocked"
    assert readiness_payload["readiness_state"]["allowed_execution"]["allowed"] is False
    assert "GNUCASH_WRITES_ENABLED=false" in readiness_payload["readiness_state"]["allowed_execution"]["reason"]
    readiness_limitations = "\n".join(readiness_payload["limitations"])
    assert "no CREATE/PATCH/DELETE/batch route is called" in readiness_limitations
    assert "No private target probing" in readiness_limitations

    write_probes = [
        (
            "validate",
            client.post(
                f"/books/{book_id}/transactions/validate",
                headers=auth_headers,
                json=_synthetic_create_payload(),
            ),
        ),
        (
            "create",
            client.post(
                f"/books/{book_id}/transactions",
                headers=auth_headers,
                json=_synthetic_create_payload(),
            ),
        ),
        (
            "patch",
            client.patch(
                f"/books/{book_id}/transactions/synthetic-created-tx",
                headers=auth_headers,
                json={"description": "blocked"},
            ),
        ),
        (
            "delete",
            client.delete(
                f"/books/{book_id}/transactions/synthetic-created-tx",
                headers=auth_headers,
            ),
        ),
    ]
    assert [response.status_code for _, response in write_probes] == [403, 403, 403, 403]
    for name, response in write_probes:
        assert "read-only" in response.json()["detail"], f"{name} probe did not return read-only detail"

    batch = client.post(
        f"/books/{book_id}/transactions/batch",
        headers=auth_headers,
        json={"items": [_synthetic_create_payload()]},
    )
    assert batch.status_code in {404, 405}

    preflight = client.post(f"/books/{book_id}/owner-writebeta/preflight", headers=auth_headers)
    assert preflight.status_code == 200
    preflight_payload = preflight.json()
    assert preflight_payload["state"] == "disabled"
    assert preflight_payload["writes_blocked"] is True
    assert "writes_disabled_default" in preflight_payload["blocked_reasons"]
    assert "writes_explicitly_enabled_runtime" not in preflight_payload["pass_reasons"]
    assert preflight_payload["summary"]["preview_hash"] is None
    assert preflight_payload["summary"]["confirmation_token_ref"] is None
    assert preflight_payload["summary"]["restore_readiness_ref"] is None

    final_status = client.get(f"/books/{book_id}/owner-writebeta/status", headers=auth_headers)
    assert final_status.status_code == 200
    assert final_status.json()["state"] == "disabled"
    assert [name for name, _ in fake_write_calls] == expected_write_call_names
    assert fake_write_calls == baseline_calls


def _audit_payloads(session_factory, action: str) -> list[dict]:
    with session_factory() as session:
        logs = session.query(AuditLog).filter_by(action=action).order_by(AuditLog.id).all()
        return [json.loads(log.payload_json or "{}") for log in logs]


def _assert_failed_hard_stop_status(
    client: TestClient,
    auth_headers: dict[str, str],
    book_id: int,
) -> dict:
    status_response = client.get(f"/books/{book_id}/owner-writebeta/status", headers=auth_headers)
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["state"] == "failed_hard_stop"
    assert status_payload["writes_blocked"] is True
    assert "state_failed_hard_stop" in status_payload["blocked_reasons"]
    assert status_payload["summary"]["preview_hash"] is None
    assert status_payload["summary"]["confirmation_token_ref"] is None
    assert status_payload["summary"]["restore_readiness_ref"] is None
    warning_text = "\n".join(status_payload["warnings"])
    assert "rollback/restore decision" in warning_text
    assert "owner-approved rollback/restore decision before any retry" in warning_text
    assert "opaque audit/backup/restore refs" in warning_text
    for raw_private_marker in (
        "/data/books",
        "book.gnucash.sqlite",
        "owner-writebeta-disposable-route-family.gnucash.sqlite",
    ):
        assert raw_private_marker not in str(status_payload)
    _assert_failed_hard_stop_rejects_reuse(client, auth_headers, book_id)
    return status_payload


def _assert_failed_hard_stop_rejects_reuse(
    client: TestClient,
    auth_headers: dict[str, str],
    book_id: int,
) -> None:
    """A post-mutation hard stop must not allow stale preview/confirm reuse."""
    probes = [
        (
            "preflight",
            client.post(f"/books/{book_id}/owner-writebeta/preflight", headers=auth_headers),
            "blocked by current state",
        ),
        (
            "preview",
            client.post(
                f"/books/{book_id}/owner-writebeta/preview",
                headers=auth_headers,
                json={"operation": "CREATE", "payload_shape": {"synthetic": "reuse"}, "count": 1},
            ),
            "requires preflight state",
        ),
        (
            "confirm",
            client.post(
                f"/books/{book_id}/owner-writebeta/confirm",
                headers=auth_headers,
                json={"preview_hash": "owb-prev-reuse", "backup_ref": "bkp-reuse", "restore_readiness_ref": "rr-reuse"},
            ),
            "confirmation preview hash mismatch",
        ),
        (
            "reset-disabled",
            client.post(f"/books/{book_id}/owner-writebeta/reset-disabled", headers=auth_headers),
            "Reset-disabled requires reset_required state",
        ),
    ]
    for name, response, detail_fragment in probes:
        assert response.status_code == 409, f"{name} reuse probe must fail closed"
        assert detail_fragment in response.json()["detail"], f"{name} detail must stay explicit"


def _assert_preflight_failure_boundary_remains_non_mutating(
    client: TestClient,
    auth_headers: dict[str, str],
    book_id: int,
    fake_write_calls: list[tuple[str, object]],
    session_factory,
    raw_private_markers: tuple[str, ...] = (),
) -> None:
    """Target preflight failures happen before write/audit/rollback boundaries."""
    assert fake_write_calls == []
    assert _audit_payloads(session_factory, "transaction.create") == []

    owner_status = client.get(f"/books/{book_id}/owner-writebeta/status", headers=auth_headers)
    assert owner_status.status_code == 200
    owner_payload = owner_status.json()
    assert owner_payload["state"] == "confirmation"
    assert "preview_confirmed_armed" in owner_payload["pass_reasons"]
    assert "state_failed_hard_stop" not in owner_payload["blocked_reasons"]
    owner_warning_text = "\n".join(owner_payload["warnings"])
    assert "rollback/restore decision" not in owner_warning_text

    readiness = client.get(f"/books/{book_id}/transactions/create-readiness-status", headers=auth_headers)
    assert readiness.status_code == 200
    readiness_payload = readiness.json()
    assert readiness_payload["create_execution_allowed"] is False
    assert readiness_payload["allowed_create_count"] == 0
    assert readiness_payload["readiness_state"]["target"]["status"] == "not_selected"
    assert readiness_payload["readiness_state"]["preflight"]["status"] == "not_checked"
    assert readiness_payload["readiness_state"]["allowed_execution"]["status"] == "blocked"
    assert readiness_payload["readiness_state"]["allowed_execution"]["allowed"] is False
    for raw_private_marker in raw_private_markers:
        assert raw_private_marker not in str(owner_payload)
        assert raw_private_marker not in str(readiness_payload)


class InvalidAccountWriteService(FakeWriteService):
    def create_transaction(self, *, request, user_id: int, book_id: int):
        self.calls.append(("create-invalid-account", request))
        from app.services.gnucash_write import GnuCashWriteError

        raise GnuCashWriteError(
            "Validation failed: Account not found: synthetic-missing-account"
        )


class LockFailingWriteService(FakeWriteService):
    def create_transaction(self, *, request, user_id: int, book_id: int):
        self.calls.append(("create-lock-failed", request))
        from app.services.write_lock import WriteLockError

        raise WriteLockError("/private/original/book.gnucash.sqlite")


def _install_write_service(monkeypatch, service_factory):
    monkeypatch.setattr("app.routers.transactions._write_service_for", service_factory)


def _assert_no_failed_audit_raw_path(payloads: list[dict]) -> None:
    assert len(payloads) == 1
    assert payloads[0]["result"] == "failed"
    serialized = json.dumps(payloads[0], sort_keys=True)
    assert "/private/original" not in serialized
    assert "book.gnucash.sqlite" not in serialized


def test_issue50_routed_create_real_service_path_covers_backup_lock_audit_readback_exact_fields_and_redaction(
    client,
    auth_headers,
    synthetic_book,
    session_factory,
    fake_write_calls,
    monkeypatch,
    tmp_path: Path,
):
    """Exercise the routed CREATE path with real service orchestration on disposable fakes.

    The test keeps the GnuCash write itself fake, but leaves the route and
    GnuCashWriteService sequencing intact: audit start, lock, backup, write-open,
    save, lock release, route read-back, audit success, and response/audit-summary
    redaction all run through the HTTP route.
    """
    from contextlib import contextmanager
    from datetime import date
    from decimal import Decimal
    from types import SimpleNamespace
    from typing import Any, cast

    import app.routers.transactions as transactions_router
    import app.services.gnucash_write as gnucash_write_module
    from app.services.gnucash_write import GnuCashWriteService
    from app.services.write_lock import WriteLockService

    events: list[str] = []
    backup_paths: list[str] = []
    audit_start_snapshots: list[dict[str, Any]] = []
    audit_success_snapshots: list[dict[str, Any]] = []
    audit_row_ids: list[int] = []
    created: dict[str, Any] = {}
    currency = SimpleNamespace(mnemonic="SEK")
    accounts = [
        SimpleNamespace(
            guid="synthetic-bank",
            name="Synthetic Bank",
            type="BANK",
            commodity=currency,
            placeholder=False,
            hidden=False,
            parent=None,
        ),
        SimpleNamespace(
            guid="synthetic-expense",
            name="Synthetic Expense",
            type="EXPENSE",
            commodity=currency,
            placeholder=False,
            hidden=False,
            parent=None,
        ),
    ]

    class FakePiecashBook:
        def __init__(self, label: str) -> None:
            self.label = label
            self.default_currency = currency
            self.accounts = accounts

        def save(self) -> None:
            events.append("save")

        def close(self) -> None:
            events.append(f"close-{self.label}")

    class FakePiecashSplit:
        def __init__(self, *, account, value, memo) -> None:
            assert isinstance(value, Decimal)
            events.append(f"split:{account.guid}:{value}:{memo}")
            self.account = account
            self.value = value
            self.memo = memo
            self.reconcile_state = ""

    class FakePiecashTransaction:
        def __init__(self, *, currency, description, post_date, splits) -> None:
            assert post_date == date(2026, 6, 4)
            events.append(f"transaction:{description}:{currency.mnemonic}:{len(splits)}")
            self.guid = "synthetic-created-route-real"
            self.currency = currency
            self.description = description
            self.post_date = post_date
            self.splits = splits
            created["transaction"] = self

    def open_read_book(self, uri_or_path: str):
        events.append("open-read")
        return FakePiecashBook("read")

    def open_write_book(self, uri_or_path: str):
        events.append("open-write")
        return FakePiecashBook("write")

    real_backup = gnucash_write_module.create_book_backup

    def spy_backup(book_config) -> str:
        events.append("backup")
        backup_path = real_backup(book_config)
        backup_paths.append(backup_path)
        return backup_path

    real_lock = WriteLockService(lock_dir=tmp_path / "locks")

    class SpyWriteLockService:
        @contextmanager
        def lock(self, book_key: str):
            with real_lock.lock(book_key):
                events.append("lock-acquired")
                try:
                    yield
                finally:
                    events.append("lock-release")

    class FakeReadbackService:
        def list_accounts(self) -> list[AccountDTO]:
            events.append("accounts-read")
            balances = {
                "synthetic-bank": Decimal("0.00"),
                "synthetic-expense": Decimal("0.00"),
            }
            tx = created.get("transaction")
            if tx is not None:
                for split in cast(Any, tx).splits:
                    balances[split.account.guid] += Decimal(str(split.value))
            return [_account_dto(account_id, balance) for account_id, balance in balances.items()]

        def get_transaction(self, transaction_id: str) -> TransactionDetailDTO:
            events.append(f"readback:{transaction_id}")
            tx = cast(Any, created["transaction"])
            return TransactionDetailDTO(
                id=transaction_id,
                date=tx.post_date.isoformat(),
                description=tx.description,
                currency=tx.currency.mnemonic,
                splits=[
                    TransactionSplitDTO(
                        account_id=split.account.guid,
                        account_name=f"Synthetic:{split.account.guid}",
                        memo=split.memo,
                        reconcile_state="",
                        amount=str(split.value),
                        currency=split.account.commodity.mnemonic,
                    )
                    for split in tx.splits
                ],
            )

    real_audit_log = transactions_router._audit_log
    real_update_audit_log = transactions_router._update_audit_log

    def spy_audit_log(session, user_id: int, book_id: int, action: str, payload: dict):
        events.append(f"audit-start:{payload['result']}")
        log = real_audit_log(session, user_id, book_id, action, payload)
        audit_row_ids.append(log.id)
        audit_start_snapshots.append(json.loads(log.payload_json or "{}"))
        return log

    def spy_update_audit_log(session, log, payload: dict) -> None:
        events.append(f"audit-update:{payload['result']}")
        real_update_audit_log(session, log, payload)
        audit_success_snapshots.append(json.loads(log.payload_json or "{}"))

    monkeypatch.setattr(transactions_router, "_write_service_for", lambda book: GnuCashWriteService(book))
    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadbackService())
    monkeypatch.setattr(transactions_router, "_audit_log", spy_audit_log)
    monkeypatch.setattr(transactions_router, "_update_audit_log", spy_update_audit_log)
    monkeypatch.setattr(GnuCashWriteService, "_open_piecash_book", open_read_book)
    monkeypatch.setattr(GnuCashWriteService, "_open_piecash_book_for_write", open_write_book)
    monkeypatch.setattr(gnucash_write_module, "create_book_backup", spy_backup)
    monkeypatch.setattr(gnucash_write_module, "write_lock_service", SpyWriteLockService())
    monkeypatch.setattr(gnucash_write_module.piecash, "Split", FakePiecashSplit)
    monkeypatch.setattr(gnucash_write_module.piecash, "Transaction", FakePiecashTransaction)

    payload = {
        "date": "2026-06-04",
        "description": "Synthetic routed CREATE decimal preservation",
        "splits": [
            {
                "account_id": "synthetic-bank",
                "amount": "-123.4500",
                "currency": "SEK",
                "memo": "synthetic source memo exact trailing zeros",
            },
            {
                "account_id": "synthetic-expense",
                "amount": "123.4500",
                "currency": "SEK",
                "memo": "synthetic destination memo exact trailing zeros",
            },
        ],
    }
    headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")

    response = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["transaction_id"] == "synthetic-created-route-real"
    assert data["readback_verified"] is True
    assert data["readback_transaction_id"] == "synthetic-created-route-real"
    assert data["audit_log_id"] is not None
    assert backup_paths == [data["backup_path"]]
    assert Path(data["backup_path"]).exists()
    assert fake_write_calls == []

    assert events.index("audit-start:started") < events.index("lock-acquired")
    assert events.index("lock-acquired") < events.index("backup")
    assert events.index("backup") < events.index("open-write")
    assert events.index("open-write") < events.index("save")
    assert events.index("save") < events.index("lock-release")
    assert events.index("lock-release") < events.index("readback:synthetic-created-route-real")
    assert events.index("readback:synthetic-created-route-real") < events.index("audit-update:success")
    assert "split:synthetic-bank:-123.4500:synthetic source memo exact trailing zeros" in events
    assert "split:synthetic-expense:123.4500:synthetic destination memo exact trailing zeros" in events
    assert (
        "transaction:Synthetic routed CREATE decimal preservation:SEK:2"
        in events
    )
    tx = cast(Any, created["transaction"])
    assert tx.post_date == date(2026, 6, 4)
    assert tx.description == payload["description"]
    assert tx.currency.mnemonic == "SEK"
    assert len(tx.splits) == 2
    assert [split.account.guid for split in tx.splits] == ["synthetic-bank", "synthetic-expense"]
    assert [str(split.value) for split in tx.splits] == ["-123.4500", "123.4500"]
    assert [split.memo for split in tx.splits] == [
        "synthetic source memo exact trailing zeros",
        "synthetic destination memo exact trailing zeros",
    ]

    expected_request_summary = {
        "date": "2026-06-04",
        "description": "Synthetic routed CREATE decimal preservation",
        "split_count": 2,
        "currencies": ["SEK"],
    }
    assert audit_row_ids == [data["audit_log_id"]]
    assert len(audit_start_snapshots) == 1
    audit_start = audit_start_snapshots[0]
    assert audit_start["result"] == "started"
    assert audit_start["request_summary"] == expected_request_summary
    assert audit_start["transaction_id"] is None
    assert audit_start["backup_path"] is None
    assert audit_start["backup_artifact_ref"] is None
    assert audit_start["readback_verified"] is False
    assert audit_start["readback_transaction_id"] is None
    assert audit_start["readback_transaction_present"] is False
    assert audit_start["readback_split_count"] is None

    assert len(audit_success_snapshots) == 1
    audit_success = audit_success_snapshots[0]
    assert audit_success["result"] == "success"
    assert audit_success["request_summary"] == expected_request_summary
    assert audit_success["transaction_id"] == "synthetic-created-route-real"
    assert audit_success["backup_path"] == data["backup_path"]
    assert audit_success["backup_artifact_ref"].startswith("bkp-")
    assert audit_success["readback_verified"] is True
    assert audit_success["readback_transaction_id"] == "synthetic-created-route-real"
    assert audit_success["readback_transaction_present"] is True
    assert audit_success["readback_split_count"] == 2

    response_evidence = json.dumps(data, sort_keys=True)
    for raw_value in (
        payload["description"],
        "synthetic source memo exact trailing zeros",
        "synthetic destination memo exact trailing zeros",
        "synthetic-bank",
        "synthetic-expense",
        "123.4500",
    ):
        assert raw_value not in response_evidence

    payloads = _audit_payloads(session_factory, "transaction.create")
    assert len(payloads) == 1
    audit_payload = payloads[0]
    assert audit_payload["result"] == "success"
    assert audit_payload["request_summary"] == expected_request_summary
    assert audit_payload["transaction_id"] == "synthetic-created-route-real"
    assert audit_payload["readback_verified"] is True
    assert audit_payload["readback_transaction_id"] == "synthetic-created-route-real"
    assert audit_payload["readback_split_count"] == 2
    assert audit_payload["backup_path"] == data["backup_path"]
    assert audit_payload["backup_artifact_ref"].startswith("bkp-")

    summary = client.get(
        f"/books/{synthetic_book}/write-alpha-audit-summary",
        headers=auth_headers,
    )
    assert summary.status_code == 200
    summary_evidence = json.dumps(summary.json(), sort_keys=True)
    assert audit_payload["backup_artifact_ref"] in summary_evidence
    for raw_value in (
        data["backup_path"],
        Path(data["backup_path"]).name,
        payload["description"],
        "synthetic source memo exact trailing zeros",
        "synthetic destination memo exact trailing zeros",
        "synthetic-bank",
        "synthetic-expense",
        "123.4500",
    ):
        assert raw_value not in summary_evidence


def test_synthetic_create_patch_delete_route_family_requires_fresh_confirmed_gate_and_default_reset(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
):
    create_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")
    create = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=create_headers,
        json=_synthetic_create_payload(),
    )
    assert create.status_code == 201
    assert create.json()["transaction_id"] == "synthetic-created-tx"
    _verify_and_reset(client, auth_headers, synthetic_book, "create", fake_write_calls, ["create"])

    patch_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "PATCH", target_owned=True)
    patch = client.patch(
        f"/books/{synthetic_book}/transactions/synthetic-created-tx",
        headers=patch_headers,
        json={"description": "metadata-only", "split_memos": {"synthetic-split": "memo-only"}},
    )
    assert patch.status_code == 200
    patched_request = [payload for name, payload in fake_write_calls if name == "patch"][-1]
    assert patched_request.description == "metadata-only"
    assert patched_request.split_memos == {"synthetic-split": "memo-only"}
    for immutable_field in ("amount", "account_id", "splits", "currency", "date"):
        assert not hasattr(patched_request, immutable_field)
    _verify_and_reset(client, auth_headers, synthetic_book, "patch", fake_write_calls, ["create", "patch"])

    delete_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "DELETE", target_owned=True)
    non_owned_delete = client.delete(
        f"/books/{synthetic_book}/transactions/not-created-by-write-alpha",
        headers=delete_headers,
    )
    assert non_owned_delete.status_code == 403
    assert "Write-alpha DELETE is allowed only" in non_owned_delete.json()["detail"]
    delete = client.delete(
        f"/books/{synthetic_book}/transactions/synthetic-created-tx",
        headers=delete_headers,
    )
    assert delete.status_code == 200
    _verify_and_reset(client, auth_headers, synthetic_book, "delete", fake_write_calls, ["create", "patch", "delete"])

    app.dependency_overrides[get_settings] = lambda: READ_ONLY_SETTINGS
    _assert_default_disabled_route_family_probes(
        client,
        auth_headers,
        synthetic_book,
        fake_write_calls,
        ["create", "patch", "delete"],
    )


def test_synthetic_route_family_create_requires_disposable_target_preflight_before_write_service(
    client,
    auth_headers,
    external_unproven_book,
    fake_write_calls,
    session_factory,
):
    create_headers = _preview_confirm_headers(client, auth_headers, external_unproven_book, "CREATE")

    response = client.post(
        f"/books/{external_unproven_book}/transactions",
        headers=create_headers,
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "Disposable target preflight failed closed" in detail
    assert "filename must mark it as copied/disposable/synthetic test data" in detail
    assert "owner-ledger" not in detail
    assert fake_write_calls == []
    with session_factory() as session:
        assert session.query(AuditLog).filter_by(action="transaction.create").count() == 0
    from app.routers.owner_writebeta import _SESSIONS

    assert _SESSIONS[external_unproven_book].state.value == "confirmation"
    _assert_preflight_failure_boundary_remains_non_mutating(
        client,
        auth_headers,
        external_unproven_book,
        fake_write_calls,
        session_factory,
        raw_private_markers=("owner-ledger",),
    )


def test_synthetic_route_family_create_requires_target_outside_repo_before_write_service(
    client,
    auth_headers,
    fake_write_calls,
    session_factory,
    tmp_path: Path,
    monkeypatch,
):
    target = tmp_path / "inside-repo-disposable-route-family.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00 inside simulated repo placeholder")
    with session_factory() as session:
        book = Book(
            name="Repo-contained disposable-looking route-family target",
            storage_type="sqlite",
            uri_or_path=str(target),
            is_default=False,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        book_id = book.id

    create_headers = _preview_confirm_headers(client, auth_headers, book_id, "CREATE")
    import app.routers.transactions as transactions_router

    monkeypatch.setattr(transactions_router, "REPO_ROOT", tmp_path.parent)

    response = client.post(
        f"/books/{book_id}/transactions",
        headers=create_headers,
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "Disposable target preflight failed closed" in detail
    assert "outside the git working tree" in detail
    assert str(target) not in detail
    assert fake_write_calls == []
    with session_factory() as session:
        assert session.query(AuditLog).filter_by(action="transaction.create").count() == 0
    from app.routers.owner_writebeta import _SESSIONS

    assert _SESSIONS[book_id].state.value == "confirmation"
    _assert_preflight_failure_boundary_remains_non_mutating(
        client,
        auth_headers,
        book_id,
        fake_write_calls,
        session_factory,
        raw_private_markers=(str(target), target.name),
    )


@pytest.mark.parametrize(
    ("field_name", "immutable_payload"),
    [
        ("amount", {"amount": "999.99"}),
        ("account_id", {"account_id": "synthetic-other-account"}),
        (
            "splits",
            {
                "splits": [
                    {
                        "account_id": "synthetic-bank",
                        "amount": "-999.99",
                        "currency": "SEK",
                        "memo": "immutable split replacement",
                    },
                    {
                        "account_id": "synthetic-expense",
                        "amount": "999.99",
                        "currency": "SEK",
                        "memo": "immutable split replacement",
                    },
                ]
            },
        ),
        ("currency", {"currency": "USD"}),
        ("date", {"date": "2026-12-31"}),
    ],
)
def test_synthetic_patch_route_rejects_immutable_fields_without_calling_patch(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
    field_name,
    immutable_payload,
):
    create_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")
    create = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=create_headers,
        json=_synthetic_create_payload(),
    )
    assert create.status_code == 201
    _verify_and_reset(client, auth_headers, synthetic_book, "create-for-rejected-patch", fake_write_calls, ["create"])

    patch_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "PATCH", target_owned=True)
    baseline_calls = list(fake_write_calls)
    response = client.patch(
        f"/books/{synthetic_book}/transactions/synthetic-created-tx",
        headers=patch_headers,
        json={
            "description": "metadata-only regression patch",
            "split_memos": {"synthetic-split": "memo-only regression patch"},
            **immutable_payload,
        },
    )

    assert response.status_code == 422
    assert field_name in str(response.json()["detail"])
    assert fake_write_calls == baseline_calls


def test_synthetic_route_family_stale_owner_writebeta_headers_do_not_fall_through_to_write(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
):
    response = client.post(
        f"/books/{synthetic_book}/transactions",
        headers={
            **auth_headers,
            "X-Owner-Writebeta-Preview-Hash": "owb-prev-stale",
            "X-Owner-Writebeta-Confirmation-Token": "stale-token",
        },
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    assert "active armed owner-writebeta session" in response.json()["detail"]
    assert fake_write_calls == []


def test_synthetic_route_family_fails_closed_for_unowned_patch_delete_previews(client, auth_headers, synthetic_book):
    client.post(f"/books/{synthetic_book}/owner-writebeta/preflight", headers=auth_headers)
    patch_preview = client.post(
        f"/books/{synthetic_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "PATCH", "payload_shape": {}, "target_is_write_alpha_owned": False},
    )
    assert patch_preview.status_code == 403

    delete_preview = client.post(
        f"/books/{synthetic_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "DELETE", "payload_shape": {}, "target_is_write_alpha_owned": False},
    )
    assert delete_preview.status_code == 403


def test_synthetic_route_family_disabled_defaults_return_403_before_write_service(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
):
    app.dependency_overrides[get_settings] = lambda: READ_ONLY_SETTINGS

    _assert_default_disabled_route_family_probes(
        client,
        auth_headers,
        synthetic_book,
        fake_write_calls,
        [],
    )


def test_issue50_stale_confirmed_preview_rejects_before_audit_or_write_service(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
    session_factory,
):
    headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")

    response = client.post(
        f"/books/{synthetic_book}/transactions",
        headers={**headers, "X-Owner-Writebeta-Preview-Hash": "owb-prev-stale"},
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    assert "armed preview" in response.json()["detail"]
    assert fake_write_calls == []
    assert _audit_payloads(session_factory, "transaction.create") == []
    from app.routers.owner_writebeta import _SESSIONS

    assert _SESSIONS[synthetic_book].state.value == "confirmation"


def test_issue50_expired_confirmed_preview_rejects_before_audit_or_write_service(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
    session_factory,
):
    from datetime import datetime, timedelta, timezone

    from app.routers.owner_writebeta import _SESSIONS

    headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")
    assert _SESSIONS[synthetic_book].state.value == "confirmation"
    _SESSIONS[synthetic_book].expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    response = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=headers,
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    assert "confirmed owner-writebeta preview expired" in response.json()["detail"]
    assert fake_write_calls == []
    assert _audit_payloads(session_factory, "transaction.create") == []
    status = client.get(f"/books/{synthetic_book}/owner-writebeta/status", headers=auth_headers)
    assert status.status_code == 200
    status_payload = status.json()
    assert status_payload["state"] == "confirmation"
    assert status_payload["writes_blocked"] is True
    assert "confirmation_expired" in status_payload["blocked_reasons"]
    assert status_payload["summary"]["backup_ref"] == "bkp-create-ref"
    assert status_payload["summary"]["restore_readiness_ref"] == "rr-create-ref"


def test_issue50_writes_disabled_rejects_even_with_fresh_owner_writebeta_confirmation(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
    session_factory,
):
    headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")
    app.dependency_overrides[get_settings] = lambda: READ_ONLY_SETTINGS

    response = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=headers,
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    assert "read-only" in response.json()["detail"]
    assert fake_write_calls == []
    assert _audit_payloads(session_factory, "transaction.create") == []
    status = client.get(f"/books/{synthetic_book}/owner-writebeta/status", headers=auth_headers)
    assert status.status_code == 200
    status_payload = status.json()
    assert status_payload["state"] == "confirmation"
    assert status_payload["writes_blocked"] is True
    assert "writes_disabled_default" in status_payload["blocked_reasons"]


def test_issue50_missing_backup_or_recovery_boundary_rejects_before_write_service(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
    session_factory,
):
    preflight = client.post(f"/books/{synthetic_book}/owner-writebeta/preflight", headers=auth_headers)
    assert preflight.status_code == 200
    preview = client.post(
        f"/books/{synthetic_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"synthetic": "shape"}, "count": 1},
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]

    missing_backup = client.post(
        f"/books/{synthetic_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={"preview_hash": preview_hash, "restore_readiness_ref": "rr-no-backup"},
    )
    assert missing_backup.status_code == 422
    from app.routers.owner_writebeta import _SESSIONS

    assert _SESSIONS[synthetic_book].state.value == "preview"

    confirm_without_restore = client.post(
        f"/books/{synthetic_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={"preview_hash": preview_hash, "backup_ref": "bkp-no-restore"},
    )
    assert confirm_without_restore.status_code == 200
    response = client.post(
        f"/books/{synthetic_book}/transactions",
        headers={
            **auth_headers,
            "X-Owner-Writebeta-Preview-Hash": preview_hash,
            "X-Owner-Writebeta-Confirmation-Token": confirm_without_restore.json()["confirmation_token"],
        },
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    assert "restore_readiness_ref" in response.json()["detail"]
    assert fake_write_calls == []
    assert _audit_payloads(session_factory, "transaction.create") == []
    status = client.get(f"/books/{synthetic_book}/owner-writebeta/status", headers=auth_headers)
    assert "restore_not_ready" in status.json()["blocked_reasons"]


def test_issue50_invalid_account_rejection_hard_stops_with_safe_recovery_message(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
    session_factory,
    monkeypatch,
):
    _install_write_service(
        monkeypatch,
        lambda book: InvalidAccountWriteService(fake_write_calls),
    )
    headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")

    response = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=headers,
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Validation failed: Account not found: synthetic-missing-account"
    )
    assert [name for name, _ in fake_write_calls] == ["create-invalid-account"]
    _assert_failed_hard_stop_status(client, auth_headers, synthetic_book)
    payloads = _audit_payloads(session_factory, "transaction.create")
    assert payloads[0]["result"] == "failed"
    assert payloads[0]["backup_path"] is None


def test_issue50_lock_failure_hard_stops_and_does_not_leak_raw_lock_or_book_path(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
    session_factory,
    monkeypatch,
):
    _install_write_service(monkeypatch, lambda book: LockFailingWriteService(fake_write_calls))
    headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")

    response = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=headers,
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Could not acquire write lock for this book. Retry after the active write finishes."
    )
    assert "/private/original" not in response.text
    assert "book.gnucash.sqlite" not in response.text
    assert [name for name, _ in fake_write_calls] == ["create-lock-failed"]
    _assert_failed_hard_stop_status(client, auth_headers, synthetic_book)
    _assert_no_failed_audit_raw_path(
        _audit_payloads(session_factory, "transaction.create")
    )
