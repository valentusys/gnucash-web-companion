"""Generated-fixture integration coverage for #59 product transaction CREATE."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import os
import shutil

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import (
    AuditLog,
    Book,
    BookHealthSnapshot,
    TransactionCreateIdempotency,
    User,
    UserBookAccess,
    WriteAlphaTransactionOwnership,
)
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.book_preflight import canonical_path_hash, run_book_health_probe
from app.services.metadata_migrations import run_app_metadata_migrations
from app.services.write_lock import WriteLockService
from tests.support.generate_transaction_create_fixtures import (
    GeneratedCreateCase,
    default_identity_snapshot,
    generate_transaction_create_fixture_set,
    sha256_file,
)

JWT_SECRET = "issue59-generated-fixtures-" + "x" * 32
ADMIN_PASSWORD = "generated-fixture-admin-pass"
ACCOUNT_TYPES_WITH_NATURAL_SIGN_REVERSED = {"LIABILITY", "PAYABLE", "CREDIT", "INCOME", "EQUITY"}


class ApiContext:
    def __init__(self, *, client: TestClient, session_factory, settings: Settings, token: str, lock_service: WriteLockService):
        self.client = client
        self.session_factory = session_factory
        self.settings = settings
        self.token = token
        self.lock_service = lock_service

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}


def _settings(tmp_path: Path, *, allowed_root: Path, writes_enabled: bool = True) -> Settings:
    return Settings(
        app_env="test",
        app_database_url="sqlite:///:memory:",
        gnucash_book_allowed_roots=[str(allowed_root)],
        jwt_secret=JWT_SECRET,
        jwt_token_expire_minutes=30,
        app_admin_username="admin",
        app_admin_password=ADMIN_PASSWORD,
        gnucash_writes_enabled=writes_enabled,
    )


def _create_context(tmp_path: Path, monkeypatch, *, allowed_root: Path, writes_enabled: bool = True) -> ApiContext:
    import app.routers.transactions as transactions_router
    import app.services.gnucash_write as gnucash_write_module

    settings = _settings(tmp_path, allowed_root=allowed_root, writes_enabled=writes_enabled)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    run_app_metadata_migrations(engine, settings)
    SessionLocal = sessionmaker(bind=engine)
    lock_service = WriteLockService(tmp_path / "locks")
    monkeypatch.setattr(transactions_router, "write_lock_service", lock_service)
    monkeypatch.setattr(gnucash_write_module, "write_lock_service", lock_service)

    def override_get_db():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db

    with SessionLocal() as session:
        admin = User(
            username="admin",
            display_name="Synthetic Admin",
            password_hash=hash_password(ADMIN_PASSWORD),
            is_admin=True,
        )
        session.add(admin)
        session.commit()

    client = TestClient(app)
    login = client.post("/auth/login", json={"username": "admin", "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text
    return ApiContext(
        client=client,
        session_factory=SessionLocal,
        settings=settings,
        token=login.json()["access_token"],
        lock_service=lock_service,
    )


@pytest.fixture(autouse=True)
def _clear_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def generated(tmp_path: Path):
    return generate_transaction_create_fixture_set(tmp_path / "generated-create-fixtures")


def _register_case(ctx: ApiContext, case: GeneratedCreateCase, *, create_enabled: bool = True, make_default: bool = True) -> int:
    probe = run_book_health_probe(str(case.target_path), ctx.settings)
    now = datetime.now(timezone.utc)
    with ctx.session_factory() as session:
        admin = session.query(User).filter_by(username="admin").one()
        if make_default:
            session.query(Book).update({Book.is_default: False}, synchronize_session=False)
        book = Book(
            name=f"Synthetic {case.name} CREATE",
            storage_type="sqlite",
            uri_or_path=str(case.target_path),
            canonical_path=probe.identity.canonical_path,
            canonical_path_hash=canonical_path_hash(probe.identity.canonical_path),
            base_currency=case.base_currency,
            is_default=make_default,
            is_archived=False,
            is_enabled=True,
            transaction_create_enabled=create_enabled,
            transaction_create_generation=1,
            transaction_create_recovery_required=False,
        )
        session.add(book)
        session.flush()
        session.add(
            BookHealthSnapshot(
                book_id=book.id,
                source_status=probe.source_status.status,
                open_status=probe.open_status.status,
                accounts_status=probe.accounts.status,
                transactions_status=probe.transactions.status,
                reports_status=probe.reports.status,
                safe_code="ready",
                checked_at=now,
                last_successful_at=now,
            )
        )
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return int(book.id)


def _preview(ctx: ApiContext, book_id: int, request: dict) -> dict:
    response = ctx.client.post(
        f"/books/{book_id}/transactions/create-preview",
        headers=ctx.headers,
        json=request,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["preview_only"] is True
    return payload


def _confirm(ctx: ApiContext, book_id: int, preview: dict, request: dict):
    return ctx.client.post(
        f"/books/{book_id}/transactions",
        headers={**ctx.headers, "Idempotency-Key": preview["idempotency_key"]},
        json={"preview_token": preview["preview_token"], "transaction": request},
    )


def _error_code(response) -> str:
    return response.json()["error"]["code"]


def _account_balances(ctx: ApiContext, book_id: int) -> dict[str, Decimal]:
    response = ctx.client.get(f"/books/{book_id}/accounts", headers=ctx.headers)
    assert response.status_code == 200, response.text
    return {item["id"]: Decimal(item["balance"]) for item in response.json()}


def _transaction_count(ctx: ApiContext, book_id: int) -> int:
    response = ctx.client.get(f"/books/{book_id}/transactions", headers=ctx.headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    if isinstance(payload, dict) and "total" in payload:
        return int(payload["total"])
    return len(payload)


def _expected_display_delta(case: GeneratedCreateCase, account_id: str, raw_amount: str) -> Decimal:
    account = next(record for record in case.accounts.values() if record["id"] == account_id)
    delta = Decimal(raw_amount)
    if account["type"].upper() in ACCOUNT_TYPES_WITH_NATURAL_SIGN_REVERSED:
        return -delta
    return delta


def _assert_no_patch_delete_audit(ctx: ApiContext, book_id: int) -> None:
    with ctx.session_factory() as session:
        forbidden = (
            session.query(AuditLog)
            .filter(AuditLog.book_id == book_id, AuditLog.action.in_(["transaction.patch", "transaction.delete"]))
            .all()
        )
        assert forbidden == []




def test_generated_fixture_default_currency_and_root_identity_survive_reopen(generated):
    for case in generated.cases.values():
        source_identity = default_identity_snapshot(case.source_path)
        target_identity = default_identity_snapshot(case.target_path)
        assert source_identity == target_identity
        assert source_identity["currency_guid"]
        assert source_identity["currency_mnemonic"] == case.base_currency
        assert source_identity["currency_namespace"] == "CURRENCY"
        assert source_identity["root_guid"]
        assert source_identity["root_type"].upper() == "ROOT"

@pytest.mark.parametrize("case_name", ["expense", "income", "three_split", "unicode"])
def test_generated_fixture_product_create_success_readback_idempotency_and_backup(tmp_path: Path, monkeypatch, generated, case_name: str):
    case = generated.cases[case_name]
    ctx = _create_context(tmp_path, monkeypatch, allowed_root=generated.root)
    book_id = _register_case(ctx, case)
    source_before = sha256_file(case.source_path)
    target_before = sha256_file(case.target_path)
    before_balances = _account_balances(ctx, book_id)
    before_count = _transaction_count(ctx, book_id)

    preview = _preview(ctx, book_id, case.request)
    assert preview["confirm_allowed"] is True
    assert preview["create_count"] == 1
    assert [split["amount"] for split in preview["splits"]] == [split["amount"] for split in case.request["splits"]]

    created = _confirm(ctx, book_id, preview, case.request)
    assert created.status_code == 201, created.text
    result = created.json()
    transaction_id = result["transaction_id"]
    assert result["status"] == "created"
    assert result["readback"] == {
        "verified": True,
        "transaction_present": True,
        "split_count": case.expected["split_count"],
        "balanced": True,
        "currency_consistent": True,
        "account_balance_deltas_verified": True,
    }
    assert result["backup_ref"].startswith("bkp_")

    duplicate = _confirm(ctx, book_id, preview, case.request)
    assert duplicate.status_code == 200, duplicate.text
    assert duplicate.json()["status"] == "already_created"
    assert duplicate.json()["transaction_id"] == transaction_id
    assert _transaction_count(ctx, book_id) == before_count + 1

    detail = ctx.client.get(f"/books/{book_id}/transactions/{transaction_id}", headers=ctx.headers)
    assert detail.status_code == 200, detail.text
    detail_payload = detail.json()
    assert detail_payload["id"] == transaction_id
    assert detail_payload["date"] == case.request["date"]
    assert detail_payload["description"] == case.request["description"]
    assert detail_payload["currency"] == case.request["currency"]
    assert detail_payload["is_write_alpha_owned"] is True
    assert len(detail_payload["splits"]) == case.expected["split_count"]
    actual_signatures = sorted((split["account_id"], split["amount"], split.get("memo", "")) for split in detail_payload["splits"])
    expected_signatures = sorted((split["account_id"], split["amount"], split["memo"]) for split in case.request["splits"])
    assert actual_signatures == expected_signatures

    after_balances = _account_balances(ctx, book_id)
    for split in case.request["splits"]:
        account_id = split["account_id"]
        assert after_balances[account_id] - before_balances[account_id] == _expected_display_delta(
            case,
            account_id,
            split["amount"],
        )

    with ctx.session_factory() as session:
        idempotency = session.query(TransactionCreateIdempotency).one()
        assert idempotency.state == "succeeded"
        assert idempotency.planned_transaction_guid == transaction_id
        assert session.query(WriteAlphaTransactionOwnership).filter_by(book_id=book_id, transaction_id=transaction_id).count() == 1
        success_audits = session.query(AuditLog).filter_by(book_id=book_id, action="transaction.create.confirm").all()
        assert len(success_audits) >= 3  # started, success, duplicate replay

    backup_root = case.target_path.parent.parent / "backups" / case.target_path.stem
    backups = sorted(path for path in backup_root.glob("*") if path.is_file() and not path.name.endswith(".verified.json"))
    markers = sorted(backup_root.glob("*.verified.json"))
    assert len(backups) == 1
    assert len(markers) == 1
    assert sha256_file(backups[0]) == target_before
    assert sha256_file(case.source_path) == source_before
    assert case.source_path.exists()
    assert case.target_path.exists()
    assert sha256_file(case.target_path) != target_before
    _assert_no_patch_delete_audit(ctx, book_id)


def test_generated_fixture_product_create_safety_failures_leave_targets_unchanged(tmp_path: Path, monkeypatch, generated):
    case = generated.cases["expense"]
    ctx = _create_context(tmp_path, monkeypatch, allowed_root=generated.root)
    book_id = _register_case(ctx, case)
    before_count = _transaction_count(ctx, book_id)

    preview = _preview(ctx, book_id, case.request)
    changed_request = {**case.request, "description": case.request["description"] + " changed"}
    changed = ctx.client.post(
        f"/books/{book_id}/transactions",
        headers={**ctx.headers, "Idempotency-Key": preview["idempotency_key"]},
        json={"preview_token": preview["preview_token"], "transaction": changed_request},
    )
    assert changed.status_code == 409
    assert _error_code(changed) in {"PREVIEW_PAYLOAD_MISMATCH", "IDEMPOTENCY_PAYLOAD_MISMATCH"}
    assert _transaction_count(ctx, book_id) == before_count

    stale_preview = _preview(ctx, book_id, case.request)
    stale_hash_before = sha256_file(case.target_path)
    os.utime(case.target_path, None)
    stale = _confirm(ctx, book_id, stale_preview, case.request)
    assert stale.status_code == 409, stale.text
    assert _error_code(stale) == "PREVIEW_STALE"
    assert sha256_file(case.target_path) == stale_hash_before
    assert _transaction_count(ctx, book_id) == before_count

    with ctx.session_factory() as session:
        book = session.query(Book).get(book_id)
        book.transaction_create_enabled = False
        book.transaction_create_generation += 1
        session.commit()
    disabled_preview = ctx.client.post(f"/books/{book_id}/transactions/create-preview", headers=ctx.headers, json=case.request)
    assert disabled_preview.status_code == 200
    assert disabled_preview.json()["confirm_allowed"] is False
    assert any(warning["code"] == "CREATE_BOOK_DISABLED" for warning in disabled_preview.json()["warnings"])

    disabled_confirm = ctx.client.post(
        f"/books/{book_id}/transactions",
        headers={**ctx.headers, "Idempotency-Key": preview["idempotency_key"] + "-disabled"},
        json={"preview_token": preview["preview_token"], "transaction": case.request},
    )
    assert disabled_confirm.status_code == 403
    assert _error_code(disabled_confirm) == "CREATE_BOOK_DISABLED"
    with ctx.session_factory() as session:
        book = session.query(Book).get(book_id)
        book.transaction_create_enabled = True
        book.transaction_create_generation += 1
        session.commit()

    locked_preview = _preview(ctx, book_id, case.request)
    with pytest.raises(Exception):
        with ctx.lock_service.lock(f"book:{book_id}"):
            locked = _confirm(ctx, book_id, locked_preview, case.request)
            assert locked.status_code == 409, locked.text
            assert _error_code(locked) == "BOOK_WRITE_BUSY"
            raise Exception("lock probe complete")
    assert _transaction_count(ctx, book_id) == before_count

    _assert_no_patch_delete_audit(ctx, book_id)


def test_generated_fixture_global_disabled_and_incompatible_commodity_reject_without_mutation(tmp_path: Path, monkeypatch, generated):
    disabled_case = generated.cases["income"]
    disabled_ctx = _create_context(tmp_path / "disabled", monkeypatch, allowed_root=generated.root, writes_enabled=False)
    disabled_book_id = _register_case(disabled_ctx, disabled_case)
    disabled_preview = disabled_ctx.client.post(
        f"/books/{disabled_book_id}/transactions/create-preview",
        headers=disabled_ctx.headers,
        json=disabled_case.request,
    )
    assert disabled_preview.status_code == 200, disabled_preview.text
    assert disabled_preview.json()["confirm_allowed"] is False
    assert any(warning["code"] == "CREATE_DEPLOYMENT_DISABLED" for warning in disabled_preview.json()["warnings"])

    incompatible = generated.cases["incompatible_commodity"]
    ctx = _create_context(tmp_path / "incompatible", monkeypatch, allowed_root=generated.root)
    book_id = _register_case(ctx, incompatible)
    target_before = sha256_file(incompatible.target_path)
    before_count = _transaction_count(ctx, book_id)
    rejected = ctx.client.post(
        f"/books/{book_id}/transactions/create-preview",
        headers=ctx.headers,
        json=incompatible.request,
    )
    assert rejected.status_code == 422, rejected.text
    assert _error_code(rejected) == "COMMODITY_MISMATCH"
    assert sha256_file(incompatible.source_path) == incompatible.source_hash
    assert sha256_file(incompatible.target_path) == target_before
    assert _transaction_count(ctx, book_id) == before_count


def test_generated_fixture_backup_failed_is_typed_non_retryable_and_can_retry_fresh(tmp_path: Path, monkeypatch, generated):
    import app.services.gnucash_write as gnucash_write_module
    from app.services.backup import BackupError

    case = generated.cases["three_split"]
    ctx = _create_context(tmp_path, monkeypatch, allowed_root=generated.root)
    book_id = _register_case(ctx, case)
    target_before = sha256_file(case.target_path)
    before_count = _transaction_count(ctx, book_id)
    preview = _preview(ctx, book_id, case.request)

    def fail_backup(_book_config):
        raise BackupError("synthetic", "forced generated-fixture backup failure")

    monkeypatch.setattr(gnucash_write_module, "create_book_backup", fail_backup)
    failed = _confirm(ctx, book_id, preview, case.request)
    assert failed.status_code == 503, failed.text
    payload = failed.json()["error"]
    assert payload["code"] == "BACKUP_FAILED"
    assert payload["retryable"] is False
    assert sha256_file(case.target_path) == target_before
    assert _transaction_count(ctx, book_id) == before_count

    monkeypatch.undo()
    # Reinstall app overrides and isolated locks after undoing the backup monkeypatch.
    ctx = _create_context(tmp_path / "retry", monkeypatch, allowed_root=tmp_path)
    retry_case_root = tmp_path / "retry-source"
    retry_case_root.mkdir()
    retry_target = retry_case_root / case.target_path.name
    shutil.copy2(case.source_path, retry_target)
    retry_case = GeneratedCreateCase(
        **{**case.__dict__, "target_path": retry_target, "target_hash_before": sha256_file(retry_target)}
    )
    retry_book_id = _register_case(ctx, retry_case)
    retry_before_count = _transaction_count(ctx, retry_book_id)
    retry_preview = _preview(ctx, retry_book_id, retry_case.request)
    retry = _confirm(ctx, retry_book_id, retry_preview, retry_case.request)
    assert retry.status_code == 201, retry.text
    assert _transaction_count(ctx, retry_book_id) == retry_before_count + 1
