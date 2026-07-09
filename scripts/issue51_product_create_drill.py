#!/usr/bin/env python3
"""Issue #51 explicit UI-harness product-route CREATE drill.

Runs exactly one FastAPI product CREATE route call against a temporary copied-like
synthetic SQLite fixture outside the git worktree. Output is a redacted result
panel only: no raw book paths, backup paths, account names, descriptions, memos,
amounts, transaction IDs, screenshots, tokens, or secrets.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import shutil
import sys
import tempfile
import warnings
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"
SYNTHETIC_FIXTURE = API_ROOT / "tests" / "fixtures" / "test-book.gnucash.sqlite"

sys.path.insert(0, str(API_ROOT))

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated.*")
warnings.filterwarnings("ignore", message="relationship .* will copy column .* conflicts.*")

import piecash  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.config import Settings, get_settings  # noqa: E402
from app.database import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.models import AuditLog, Book, User, UserBookAccess, WriteAlphaTransactionOwnership  # noqa: E402
from app.routers.auth import get_db  # noqa: E402
from app.services.auth import hash_password  # noqa: E402
from app.services.write_lock import WriteLockService  # noqa: E402

SOURCE_ACCOUNT_ID = "c73e8aa01e6345288662b556f2f866f3"
DESTINATION_ACCOUNT_ID = "388a85676d4a4643ae6cd28166c34e79"
ISSUE51_RESULT_PANEL_ID = "issue51-redacted-create-result"
EXPLICIT_CREATE_REF = "create-ref-redacted-issue51"
EXPLICIT_BACKUP_REF = "backup-ref-redacted-issue51"
EXPLICIT_AUDIT_REF = "audit-ref-redacted-issue51"
DISABLED_PROBE_FAMILIES = ("validate", "preflight", "create", "patch", "delete", "batch")


class DrillFailure(RuntimeError):
    """Path-safe drill failure."""


def default_product_create_payload() -> dict[str, Any]:
    return {
        "date": "2026-07-05",
        "description": "Synthetic browser smoke preview",
        "splits": [
            {
                "account_id": SOURCE_ACCOUNT_ID,
                "amount": "-12.34",
                "currency": "SEK",
                "memo": "Synthetic browser smoke memo",
            },
            {
                "account_id": DESTINATION_ACCOUNT_ID,
                "amount": "12.34",
                "currency": "SEK",
                "memo": "Synthetic browser smoke memo",
            },
        ],
    }


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return False
    return True


def _read_transactions(book_path: Path) -> list[dict[str, Any]]:
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
                        "account_guid": split.account.guid,
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


def _read_account_balances(book_path: Path, account_ids: set[str]) -> dict[str, Decimal]:
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        balances: dict[str, Decimal] = {}
        for account in book.accounts:
            account_id = str(account.guid)
            if account_id in account_ids:
                balances[account_id] = Decimal(str(account.get_balance()))
        return balances
    finally:
        book.close()


@contextlib.contextmanager
def _configured_app(
    *,
    app_db: Path,
    book_path: Path,
    writes_enabled: bool,
    app_env: str = "test",
    lock_dir: Path,
) -> Iterator[tuple[Any, Any, WriteLockService]]:
    import app.services.gnucash_write as gnucash_write_module
    import app.services.write_lock as write_lock_module

    engine = create_engine(f"sqlite:///{app_db}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    settings = Settings(
        app_env=app_env,
        app_database_url=f"sqlite:///{app_db}",
        gnucash_default_book_path=str(book_path),
        jwt_secret="test-secret-key-for-issue51-product-create-drill",
        jwt_token_expire_minutes=30,
        app_admin_username="admin",
        app_admin_password="testpassword123",
        gnucash_writes_enabled=writes_enabled,
    )

    def override_get_db():
        with session_factory() as session:
            yield session

    original_write_lock = write_lock_module.write_lock_service
    original_gnucash_write_lock = gnucash_write_module.write_lock_service
    lock_service = WriteLockService(lock_dir=lock_dir)
    write_lock_module.write_lock_service = lock_service
    gnucash_write_module.write_lock_service = lock_service
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db
    get_settings.cache_clear()
    try:
        yield engine, session_factory, lock_service
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        write_lock_module.write_lock_service = original_write_lock
        gnucash_write_module.write_lock_service = original_gnucash_write_lock
        engine.dispose()


def _bootstrap_metadata(session_factory: Any, book_path: Path) -> int:
    with session_factory() as session:
        user = session.query(User).filter(User.username == "admin").one_or_none()
        if user is None:
            user = User(
                username="admin",
                display_name="Admin",
                password_hash=hash_password("testpassword123"),
                is_admin=True,
            )
            session.add(user)
            session.flush()
        book = Book(
            name="Issue 51 disposable copied-like fixture",
            storage_type="sqlite",
            uri_or_path=str(book_path),
            base_currency="SEK",
            is_default=True,
        )
        session.add(book)
        session.flush()
        session.add(UserBookAccess(user_id=user.id, book_id=book.id, role="owner"))
        session.commit()
        return int(book.id)


def _login(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": "admin", "password": "testpassword123"})
    if response.status_code != 200:
        raise DrillFailure("login failed safely")
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _validate_payload(payload: dict[str, Any]) -> None:
    if sorted(payload) != ["date", "description", "splits"]:
        raise DrillFailure("payload shape is not the product CREATE shape")
    if not isinstance(payload.get("description"), str) or not payload["description"].strip():
        raise DrillFailure("payload description is missing")
    try:
        date.fromisoformat(str(payload["date"]))
    except ValueError as exc:
        raise DrillFailure("payload date is not ISO YYYY-MM-DD") from exc
    splits = payload.get("splits")
    if not isinstance(splits, list) or len(splits) != 2:
        raise DrillFailure("bounded CREATE drill requires exactly two splits")
    currencies = {str(split.get("currency", "")).upper() for split in splits if isinstance(split, dict)}
    if len(currencies) != 1 or next(iter(currencies)) != "SEK":
        raise DrillFailure("bounded CREATE drill requires one supported synthetic currency")
    total = Decimal("0")
    for split in splits:
        if not isinstance(split, dict):
            raise DrillFailure("split payload is invalid")
        if str(split.get("account_id")) not in {SOURCE_ACCOUNT_ID, DESTINATION_ACCOUNT_ID}:
            raise DrillFailure("payload account is not scoped to the disposable fixture")
        total += Decimal(str(split.get("amount")))
        if not isinstance(split.get("memo"), str):
            raise DrillFailure("payload memo is invalid")
    if total != Decimal("0.00"):
        raise DrillFailure("payload split total is not zero")


def _assert_detail_matches_payload(detail: dict[str, Any], payload: dict[str, Any], transaction_id: str) -> None:
    if detail.get("id") != transaction_id:
        raise DrillFailure("read-back transaction reference mismatch")
    if detail.get("date") != payload["date"]:
        raise DrillFailure("read-back date mismatch")
    if detail.get("description") != payload["description"]:
        raise DrillFailure("read-back description mismatch")
    if detail.get("currency") != "SEK":
        raise DrillFailure("read-back currency mismatch")
    if detail.get("is_write_alpha_owned") is not True:
        raise DrillFailure("read-back ownership marker missing")
    detail_splits = {split["account_id"]: split for split in detail.get("splits", [])}
    if set(detail_splits) != {SOURCE_ACCOUNT_ID, DESTINATION_ACCOUNT_ID}:
        raise DrillFailure("read-back split account set mismatch")
    expected_splits = {split["account_id"]: split for split in payload["splits"]}
    for account_id, expected in expected_splits.items():
        actual = detail_splits[account_id]
        if actual.get("amount") != expected["amount"]:
            raise DrillFailure("read-back split amount mismatch")
        if actual.get("currency") != expected["currency"]:
            raise DrillFailure("read-back split currency mismatch")
        if actual.get("memo") != expected["memo"]:
            raise DrillFailure("read-back split memo mismatch")


def _assert_reopened_matches_payload(
    *,
    created: dict[str, Any],
    payload: dict[str, Any],
    tracked_accounts: set[str],
) -> None:
    if created["description"] != payload["description"]:
        raise DrillFailure("reopened description mismatch")
    if created["post_date"] != date.fromisoformat(payload["date"]):
        raise DrillFailure("reopened date mismatch")
    if created["currency"] != "SEK":
        raise DrillFailure("reopened currency mismatch")
    reopened_splits = {split["account_guid"]: split for split in created["splits"]}
    if set(reopened_splits) != tracked_accounts:
        raise DrillFailure("reopened split account set mismatch")
    expected_splits = {split["account_id"]: split for split in payload["splits"]}
    for account_id, expected in expected_splits.items():
        actual = reopened_splits[account_id]
        if actual["value"] != Decimal(str(expected["amount"])):
            raise DrillFailure("reopened split amount mismatch")
        if actual["memo"] != expected["memo"]:
            raise DrillFailure("reopened split memo mismatch")
    if sum(split["value"] for split in created["splits"]) != Decimal("0.00"):
        raise DrillFailure("reopened split balance mismatch")


def _blocked_or_unavailable(response_status: int) -> bool:
    return response_status in {403, 404, 405}


def _run_disabled_probes(
    *,
    app_db: Path,
    book_path: Path,
    lock_dir: Path,
    book_id: int,
    transaction_id: str,
    payload: dict[str, Any],
    tx_count_after_create: int,
) -> tuple[dict[str, Any], bool]:
    with _configured_app(
        app_db=app_db,
        book_path=book_path,
        writes_enabled=False,
        app_env="test",
        lock_dir=lock_dir,
    ) as (_, __, ___):
        client = TestClient(app)
        headers = _login(client)
        readiness_response = client.get(
            f"/books/{book_id}/transactions/create-readiness-status",
            headers=headers,
        )
        if readiness_response.status_code != 200:
            raise DrillFailure("disabled readiness probe failed safely")
        readiness = readiness_response.json()
        probe_specs = {
            "validate": ("POST", f"/books/{book_id}/transactions/validate", payload),
            "preflight": ("POST", f"/books/{book_id}/transactions/preflight", payload),
            "create": ("POST", f"/books/{book_id}/transactions", payload),
            "patch": (
                "PATCH",
                f"/books/{book_id}/transactions/{transaction_id}",
                {"description": "disabled probe should not patch"},
            ),
            "delete": ("DELETE", f"/books/{book_id}/transactions/{transaction_id}", None),
            "batch": ("POST", f"/books/{book_id}/transactions/batch", {"items": [payload]}),
        }
        probes = []
        for route_family in DISABLED_PROBE_FAMILIES:
            method, path, body = probe_specs[route_family]
            if method == "POST":
                response = client.post(path, json=body, headers=headers)
            elif method == "PATCH":
                response = client.patch(path, json=body, headers=headers)
            elif method == "DELETE":
                response = client.delete(path, headers=headers)
            else:  # pragma: no cover - protects future probe edits
                raise AssertionError(method)
            probes.append(
                {
                    "route_family": route_family,
                    "status": "blocked_or_unavailable" if _blocked_or_unavailable(response.status_code) else "unexpected",
                    "http_status_class": response.status_code,
                }
            )

    tx_count_after_disabled_probes = len(_read_transactions(book_path))
    no_extra_create = tx_count_after_disabled_probes == tx_count_after_create
    create_execution_allowed_after_reset = bool(readiness.get("create_execution_allowed"))
    create_execution_blocked_after_reset_verified = create_execution_allowed_after_reset is False
    summary = {
        "state": "verified" if no_extra_create and create_execution_blocked_after_reset_verified else "failed",
        "app_env": "test",
        "gnucash_writes_enabled": False,
        "create_execution_allowed_after_reset": create_execution_allowed_after_reset,
        "create_execution_blocked_after_reset_verified": create_execution_blocked_after_reset_verified,
        "probes": probes,
    }
    return (
        summary,
        no_extra_create
        and create_execution_blocked_after_reset_verified
        and all(probe["status"] == "blocked_or_unavailable" for probe in probes),
    )


def build_redacted_result_panel(
    *,
    disabled_probe_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "redacted_result_panel": {
            "panel_id": ISSUE51_RESULT_PANEL_ID,
            "status": "success",
            "evidence_scope": "redacted_only",
            "target_class": "disposable_copied_like_fixture",
            "create_count": 1,
            "create_result_ref": EXPLICIT_CREATE_REF,
            "backend_route_write_boundary": {
                "product_route_used": True,
                "route": "POST /books/{book_id}/transactions",
                "route_response_status": 201,
                "app_env": "test",
                "gnucash_writes_enabled_during_create": True,
                "normal_ui_create_activated": False,
                "direct_sql_write": False,
            },
            "fixture_scope": {
                "copied_like_fixture": True,
                "synthetic_fixture_source": True,
                "outside_git_worktree": True,
                "private_or_only_copy_target": False,
            },
            "write_boundary_verification": {
                "backup_before_write_verified": True,
                "lock_released_verified": True,
                "audit_recorded": True,
                "write_route_called_once": True,
                "read_back_before_success": True,
            },
            "read_back_verification": {
                "state": "verified",
                "transaction_ref": EXPLICIT_CREATE_REF,
                "transaction_present": True,
                "split_count": 2,
                "split_balance_verified": True,
                "account_balance_delta_count": 2,
                "account_balance_deltas_verified": True,
                "reopen_verified": True,
                "currency_verified": True,
                "date_verified": True,
                "description_verified": True,
                "memo_verified": True,
                "private_values_redacted": True,
            },
            "backup_state": {
                "state": "captured",
                "backup_ref": EXPLICIT_BACKUP_REF,
                "exists_verified": True,
                "pre_create_contents_verified": True,
                "raw_path_included": False,
            },
            "audit_state": {
                "state": "recorded",
                "audit_ref": EXPLICIT_AUDIT_REF,
                "result": "success",
                "raw_payload_included": False,
            },
            "ownership_state": {
                "state": "recorded",
                "ownership_count": 1,
                "app_metadata_only": True,
            },
            "reset_default_disabled_probe_summary": disabled_probe_summary,
            "redaction": {
                "raw_book_paths": False,
                "raw_backup_paths": False,
                "private_account_names": False,
                "raw_descriptions": False,
                "raw_memos": False,
                "raw_amounts": False,
                "raw_guids": False,
                "screenshots": False,
                "tokens_or_secrets": False,
            },
        }
    }


def run_issue51_product_create_drill(product_create_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = product_create_payload or default_product_create_payload()
    _validate_payload(payload)
    if not SYNTHETIC_FIXTURE.is_file():
        raise DrillFailure("synthetic fixture is unavailable")

    with tempfile.TemporaryDirectory(prefix="issue51-product-create-drill-") as tmp:
        work_dir = Path(tmp)
        books_dir = work_dir / "books"
        books_dir.mkdir()
        book_path = books_dir / "issue51-disposable-copied-like.gnucash.sqlite"
        shutil.copy2(SYNTHETIC_FIXTURE, book_path)
        if _inside_repo(book_path):
            raise DrillFailure("disposable fixture copy is inside the git worktree")
        app_db = work_dir / "app-metadata.sqlite"
        lock_dir = work_dir / "locks"
        tracked_accounts = {SOURCE_ACCOUNT_ID, DESTINATION_ACCOUNT_ID}
        txs_before = _read_transactions(book_path)
        balances_before = _read_account_balances(book_path, tracked_accounts)
        if set(balances_before) != tracked_accounts:
            raise DrillFailure("fixture account balance precheck failed")
        fixture_sha_before = _sha256_path(book_path)

        with _configured_app(
            app_db=app_db,
            book_path=book_path,
            writes_enabled=True,
            app_env="test",
            lock_dir=lock_dir,
        ) as (_, session_factory, lock_service):
            book_id = _bootstrap_metadata(session_factory, book_path)
            client = TestClient(app)
            headers = _login(client)
            create_response = client.post(
                f"/books/{book_id}/transactions",
                json=payload,
                headers=headers,
            )
            if create_response.status_code != 201:
                raise DrillFailure(f"product CREATE route failed safely with status {create_response.status_code}")
            create_result = create_response.json()
            transaction_id = str(create_result.get("transaction_id") or "")
            if not transaction_id:
                raise DrillFailure("product CREATE route did not return a transaction reference")
            if create_result.get("readback_verified") is not True:
                raise DrillFailure("product CREATE route did not verify read-back before success")
            if create_result.get("readback_split_balance_verified") is not True:
                raise DrillFailure("product CREATE route did not verify split balance")
            if create_result.get("readback_currency_consistent") is not True:
                raise DrillFailure("product CREATE route did not verify currency consistency")
            if create_result.get("readback_account_balance_deltas_verified") is not True:
                raise DrillFailure("product CREATE route did not verify balance deltas")

            backup_path = Path(str(create_result.get("backup_path") or ""))
            if not backup_path.is_file() or _inside_repo(backup_path):
                raise DrillFailure("backup evidence failed safe scope/existence checks")
            if _read_transactions(backup_path) != txs_before:
                raise DrillFailure("backup did not capture pre-CREATE fixture contents")
            if _sha256_path(backup_path) != fixture_sha_before:
                raise DrillFailure("backup checksum did not match pre-CREATE fixture")

            detail_response = client.get(
                f"/books/{book_id}/transactions/{transaction_id}",
                headers=headers,
            )
            if detail_response.status_code != 200:
                raise DrillFailure("read-back detail route failed safely")
            _assert_detail_matches_payload(detail_response.json(), payload, transaction_id)

            txs_after = _read_transactions(book_path)
            if len(txs_after) != len(txs_before) + 1:
                raise DrillFailure("CREATE count was not exactly one")
            created = next((tx for tx in txs_after if tx["guid"] == transaction_id), None)
            if created is None:
                raise DrillFailure("created transaction missing after reopen")
            _assert_reopened_matches_payload(
                created=created,
                payload=payload,
                tracked_accounts=tracked_accounts,
            )
            balances_after = _read_account_balances(book_path, tracked_accounts)
            expected_deltas = {
                split["account_id"]: Decimal(str(split["amount"]))
                for split in payload["splits"]
            }
            for account_id, expected_delta in expected_deltas.items():
                if balances_after[account_id] - balances_before[account_id] != expected_delta:
                    raise DrillFailure("reopened account balance delta mismatch")
            if sum(balances_after[account_id] - balances_before[account_id] for account_id in tracked_accounts) != Decimal("0.00"):
                raise DrillFailure("reopened balance deltas do not net to zero")

            lock_key = str(book_path)
            if not lock_service.acquire(lock_key):
                raise DrillFailure("write lock was not released after CREATE")
            lock_service.release(lock_key)

            with session_factory() as session:
                audit_id = create_result.get("audit_log_id")
                audit_log = session.get(AuditLog, audit_id)
                if audit_log is None:
                    raise DrillFailure("audit log missing")
                audit_payload = json.loads(audit_log.payload_json)
                if audit_log.action != "transaction.create" or audit_payload.get("result") != "success":
                    raise DrillFailure("audit success row missing")
                if audit_payload.get("transaction_id") != transaction_id:
                    raise DrillFailure("audit transaction reference mismatch")
                if audit_payload.get("backup_path") != str(backup_path):
                    raise DrillFailure("audit backup reference mismatch")
                if audit_payload.get("readback_verified") is not True:
                    raise DrillFailure("audit read-back marker missing")
                ownership_count = (
                    session.query(WriteAlphaTransactionOwnership)
                    .filter(
                        WriteAlphaTransactionOwnership.book_id == book_id,
                        WriteAlphaTransactionOwnership.transaction_id == transaction_id,
                        WriteAlphaTransactionOwnership.created_by_write_alpha == True,  # noqa: E712
                    )
                    .count()
                )
                if ownership_count != 1:
                    raise DrillFailure("ownership metadata was not recorded exactly once")

        disabled_probe_summary, disabled_ok = _run_disabled_probes(
            app_db=app_db,
            book_path=book_path,
            lock_dir=lock_dir,
            book_id=book_id,
            transaction_id=transaction_id,
            payload=payload,
            tx_count_after_create=len(txs_after),
        )
        if not disabled_ok:
            raise DrillFailure("disabled/reset probes did not all fail closed")

    return build_redacted_result_panel(disabled_probe_summary=disabled_probe_summary)


def _payload_from_stdin() -> dict[str, Any] | None:
    if sys.stdin.isatty():
        return None
    raw = sys.stdin.read().strip()
    if not raw:
        return None
    parsed = json.loads(raw)
    if isinstance(parsed, dict) and "product_create_payload" in parsed:
        parsed = parsed["product_create_payload"]
    if not isinstance(parsed, dict):
        raise DrillFailure("stdin payload must be a JSON object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run issue #51 redacted product-route CREATE drill.")
    parser.add_argument("--json-only", action="store_true", help="print only the redacted JSON result panel")
    args = parser.parse_args()
    try:
        result = run_issue51_product_create_drill(_payload_from_stdin())
    except Exception as exc:
        print(f"FAIL: {exc.__class__.__name__}: {exc}; paths redacted", file=sys.stderr)
        return 2

    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.json_only:
        print(payload)
    else:
        print("PASS: issue51 product-route CREATE drill completed; paths redacted")
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
