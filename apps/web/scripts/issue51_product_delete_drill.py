#!/usr/bin/env python3
"""Issue #51 explicit UI-harness product-route DELETE drill.

Creates exactly one app-owned disposable transaction as setup, proves non-owned
and non-disposable DELETE attempts are rejected without mutation, then runs
exactly one DELETE through the FastAPI product route. Output is a redacted result
panel only: no raw book paths, backup paths, account names, descriptions, memos,
amounts, transaction IDs, screenshots, tokens, or secrets.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.issue51_product_create_drill import (  # noqa: E402
    DESTINATION_ACCOUNT_ID,
    SOURCE_ACCOUNT_ID,
    SYNTHETIC_FIXTURE,
    DrillFailure,
    _bootstrap_metadata,
    _configured_app,
    _inside_repo,
    _login,
    _read_account_balances,
    _sha256_path,
    _validate_payload,
    default_product_create_payload,
)

import piecash  # noqa: E402
from app.models import AuditLog, Book, User, UserBookAccess, WriteAlphaTransactionOwnership  # noqa: E402
from app.services.gnucash_book import _guid  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

ISSUE51_DELETE_PANEL_ID = "issue51-redacted-delete-result"
EXPLICIT_DELETE_CREATE_REF = "create-ref-redacted-issue51-delete-setup"
EXPLICIT_DELETE_REF = "delete-ref-redacted-issue51"
EXPLICIT_DELETE_BACKUP_REF = "backup-ref-redacted-issue51-delete"
EXPLICIT_DELETE_AUDIT_REF = "audit-ref-redacted-issue51-delete"


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
                        "guid": _guid(split),
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


def _backup_file_count(work_dir: Path) -> int:
    backups_root = work_dir / "backups"
    if not backups_root.exists():
        return 0
    return sum(1 for path in backups_root.rglob("*") if path.is_file())


def _assert_transaction_matches_create_payload(
    *,
    created: dict[str, Any],
    payload: dict[str, Any],
    tracked_accounts: set[str],
) -> None:
    if created["description"] != payload["description"]:
        raise DrillFailure("setup CREATE reopened description mismatch")
    if created["post_date"] != date.fromisoformat(payload["date"]):
        raise DrillFailure("setup CREATE reopened date mismatch")
    if created["currency"] != "SEK":
        raise DrillFailure("setup CREATE reopened currency mismatch")
    if {split["account_guid"] for split in created["splits"]} != tracked_accounts:
        raise DrillFailure("setup CREATE reopened account set mismatch")
    expected_splits = {split["account_id"]: split for split in payload["splits"]}
    for split in created["splits"]:
        expected = expected_splits[split["account_guid"]]
        if split["value"] != Decimal(str(expected["amount"])):
            raise DrillFailure("setup CREATE reopened split amount mismatch")
        if split["memo"] != expected["memo"]:
            raise DrillFailure("setup CREATE reopened split memo mismatch")
    if sum(split["value"] for split in created["splits"]) != Decimal("0.00"):
        raise DrillFailure("setup CREATE reopened split balance mismatch")


def _create_non_disposable_owned_book(
    *,
    session_factory: Any,
    unsafe_book_path: Path,
    transaction_id: str,
) -> int:
    with session_factory() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        unsafe_book = Book(
            name="Issue 51 rejected non-disposable fixture",
            storage_type="sqlite",
            uri_or_path=str(unsafe_book_path),
            base_currency="SEK",
            is_default=False,
        )
        session.add(unsafe_book)
        session.flush()
        session.add(UserBookAccess(user_id=admin.id, book_id=unsafe_book.id, role="owner"))
        session.add(
            WriteAlphaTransactionOwnership(
                book_id=unsafe_book.id,
                transaction_id=transaction_id,
                created_by_user_id=admin.id,
                created_by_write_alpha=True,
            )
        )
        session.commit()
        return int(unsafe_book.id)


def _assert_delete_rejections(
    *,
    client: TestClient,
    headers: dict[str, str],
    book_id: int,
    transaction_id: str,
    book_path: Path,
    work_dir: Path,
    session_factory: Any,
    unsafe_book_path: Path,
) -> dict[str, Any]:
    txs_before = _read_transactions(book_path)
    backup_count_before = _backup_file_count(work_dir)

    non_owned_response = client.delete(
        f"/books/{book_id}/transactions/not-created-by-write-alpha",
        headers=headers,
    )
    if non_owned_response.status_code != 403:
        raise DrillFailure("non-owned DELETE probe did not fail closed")
    if "Write-alpha DELETE is allowed only" not in json.dumps(non_owned_response.json()):
        raise DrillFailure("non-owned DELETE probe did not return ownership rejection")
    if _read_transactions(book_path) != txs_before:
        raise DrillFailure("non-owned DELETE probe mutated the disposable fixture")
    if _backup_file_count(work_dir) != backup_count_before:
        raise DrillFailure("non-owned DELETE probe created backup evidence")

    shutil.copy2(SYNTHETIC_FIXTURE, unsafe_book_path)
    if _inside_repo(unsafe_book_path):
        raise DrillFailure("non-disposable rejection fixture copy is inside the git worktree")
    unsafe_book_id = _create_non_disposable_owned_book(
        session_factory=session_factory,
        unsafe_book_path=unsafe_book_path,
        transaction_id=transaction_id,
    )
    unsafe_txs_before = _read_transactions(unsafe_book_path)
    non_disposable_response = client.delete(
        f"/books/{unsafe_book_id}/transactions/{transaction_id}",
        headers=headers,
    )
    if non_disposable_response.status_code != 403:
        raise DrillFailure("non-disposable DELETE probe did not fail closed")
    detail = json.dumps(non_disposable_response.json())
    if "Disposable target preflight failed closed" not in detail:
        raise DrillFailure("non-disposable DELETE probe did not return target preflight rejection")
    if "owner-ledger" in detail:
        raise DrillFailure("non-disposable DELETE rejection leaked the raw target label")
    if _read_transactions(unsafe_book_path) != unsafe_txs_before:
        raise DrillFailure("non-disposable DELETE probe mutated the rejected fixture")
    if _read_transactions(book_path) != txs_before:
        raise DrillFailure("non-disposable DELETE probe mutated the disposable fixture")
    if _backup_file_count(work_dir) != backup_count_before:
        raise DrillFailure("non-disposable DELETE probe created backup evidence")

    return {
        "state": "verified",
        "non_owned_delete_rejected": True,
        "non_owned_http_status_class": non_owned_response.status_code,
        "non_disposable_delete_rejected": True,
        "non_disposable_http_status_class": non_disposable_response.status_code,
        "mutation_count": 0,
        "backup_created": False,
    }


def _run_disabled_delete_probe(
    *,
    app_db: Path,
    book_path: Path,
    lock_dir: Path,
    book_id: int,
    transaction_id: str,
    txs_after_delete: list[dict[str, Any]],
    backup_count_after_delete: int,
) -> tuple[dict[str, Any], bool]:
    with _configured_app(
        app_db=app_db,
        book_path=book_path,
        writes_enabled=False,
        app_env="test",
        lock_dir=lock_dir,
    ):
        client = TestClient(__import__("app.main", fromlist=["app"]).app)
        headers = _login(client)
        response = client.delete(
            f"/books/{book_id}/transactions/{transaction_id}",
            headers=headers,
        )
    blocked = response.status_code in {403, 404, 405}
    unchanged = _read_transactions(book_path) == txs_after_delete
    no_backup = _backup_file_count(app_db.parent) == backup_count_after_delete
    summary = {
        "state": "verified" if blocked and unchanged and no_backup else "failed",
        "app_env": "test",
        "gnucash_writes_enabled": False,
        "delete_execution_allowed_after_reset": False if blocked else True,
        "delete_execution_blocked_after_reset_verified": blocked,
        "probe": {
            "route_family": "delete",
            "status": "blocked_or_unavailable" if blocked else "unexpected",
            "http_status_class": response.status_code,
        },
    }
    return summary, blocked and unchanged and no_backup


def build_redacted_delete_result_panel(*, disabled_delete_probe_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "redacted_delete_result_panel": {
            "panel_id": ISSUE51_DELETE_PANEL_ID,
            "status": "success",
            "evidence_scope": "redacted_only",
            "target_class": "disposable_copied_like_fixture",
            "setup_create_count": 1,
            "delete_count": 1,
            "create_result_ref": EXPLICIT_DELETE_CREATE_REF,
            "delete_result_ref": EXPLICIT_DELETE_REF,
            "backend_route_write_boundary": {
                "setup_create_product_route_used": True,
                "delete_product_route_used": True,
                "route": "DELETE /books/{book_id}/transactions/{transaction_id}",
                "route_response_status": 200,
                "app_env": "test",
                "gnucash_writes_enabled_during_delete": True,
                "normal_ui_delete_activated": False,
                "direct_sql_write": False,
            },
            "fixture_scope": {
                "copied_like_fixture": True,
                "synthetic_fixture_source": True,
                "outside_git_worktree": True,
                "private_or_only_copy_target": False,
            },
            "ownership_state": {
                "state": "verified",
                "app_created_target": True,
                "created_by_write_alpha": True,
                "non_app_created_delete_allowed": False,
                "non_disposable_delete_allowed": False,
                "app_metadata_only": True,
            },
            "delete_scope": {
                "transaction_removed": True,
                "retained_non_target_transactions_unchanged": True,
                "account_balance_reverted": True,
                "split_rows_removed": True,
                "historical_or_manual_delete_allowed": False,
            },
            "read_back_verification": {
                "state": "verified",
                "transaction_ref": EXPLICIT_DELETE_REF,
                "transaction_present_after_delete": False,
                "transaction_count_delta_after_delete": -1,
                "account_balance_delta_reverted": True,
                "reopen_verified": True,
                "private_values_redacted": True,
            },
            "backup_state": {
                "state": "captured",
                "backup_ref": EXPLICIT_DELETE_BACKUP_REF,
                "exists_verified": True,
                "pre_delete_contents_verified": True,
                "raw_path_included": False,
            },
            "audit_state": {
                "state": "recorded",
                "audit_ref": EXPLICIT_DELETE_AUDIT_REF,
                "result": "success",
                "raw_payload_included": False,
            },
            "rejection_summary": {
                "state": "verified",
                "non_owned_delete_rejected": True,
                "non_owned_http_status_class": 403,
                "non_disposable_delete_rejected": True,
                "non_disposable_http_status_class": 403,
                "mutation_count": 0,
                "backup_created": False,
            },
            "reset_default_disabled_delete_probe_summary": disabled_delete_probe_summary,
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


def run_issue51_product_delete_drill(product_create_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = product_create_payload or default_product_create_payload()
    _validate_payload(payload)
    if not SYNTHETIC_FIXTURE.is_file():
        raise DrillFailure("synthetic fixture is unavailable")

    with tempfile.TemporaryDirectory(prefix="issue51-product-delete-drill-") as tmp:
        work_dir = Path(tmp)
        books_dir = work_dir / "books"
        books_dir.mkdir()
        book_path = books_dir / "issue51-disposable-copied-like.gnucash.sqlite"
        unsafe_book_path = books_dir / "owner-ledger.gnucash.sqlite"
        shutil.copy2(SYNTHETIC_FIXTURE, book_path)
        if _inside_repo(book_path):
            raise DrillFailure("disposable fixture copy is inside the git worktree")
        app_db = work_dir / "app-metadata.sqlite"
        lock_dir = work_dir / "locks"
        tracked_accounts = {SOURCE_ACCOUNT_ID, DESTINATION_ACCOUNT_ID}
        txs_before_create = _read_transactions(book_path)
        balances_before_create = _read_account_balances(book_path, tracked_accounts)
        if set(balances_before_create) != tracked_accounts:
            raise DrillFailure("fixture account balance precheck failed")

        with _configured_app(
            app_db=app_db,
            book_path=book_path,
            writes_enabled=True,
            app_env="test",
            lock_dir=lock_dir,
        ) as (_, session_factory, lock_service):
            book_id = _bootstrap_metadata(session_factory, book_path)
            client = TestClient(__import__("app.main", fromlist=["app"]).app)
            headers = _login(client)

            create_response = client.post(
                f"/books/{book_id}/transactions",
                json=payload,
                headers=headers,
            )
            if create_response.status_code != 201:
                raise DrillFailure(f"setup product CREATE route failed safely with status {create_response.status_code}")
            create_result = create_response.json()
            transaction_id = str(create_result.get("transaction_id") or "")
            if not transaction_id:
                raise DrillFailure("setup CREATE did not return a transaction reference")
            if create_result.get("readback_verified") is not True:
                raise DrillFailure("setup CREATE did not verify read-back before success")

            txs_after_create = _read_transactions(book_path)
            if len(txs_after_create) != len(txs_before_create) + 1:
                raise DrillFailure("setup CREATE count was not exactly one")
            created = next((tx for tx in txs_after_create if tx["guid"] == transaction_id), None)
            if created is None:
                raise DrillFailure("setup CREATE transaction missing after reopen")
            _assert_transaction_matches_create_payload(
                created=created,
                payload=payload,
                tracked_accounts=tracked_accounts,
            )
            balances_after_create = _read_account_balances(book_path, tracked_accounts)
            if balances_after_create == balances_before_create:
                raise DrillFailure("setup CREATE did not change disposable fixture balances")
            backup_count_after_create = _backup_file_count(work_dir)
            if backup_count_after_create < 1:
                raise DrillFailure("setup CREATE backup evidence missing")

            rejection_summary = _assert_delete_rejections(
                client=client,
                headers=headers,
                book_id=book_id,
                transaction_id=transaction_id,
                book_path=book_path,
                work_dir=work_dir,
                session_factory=session_factory,
                unsafe_book_path=unsafe_book_path,
            )
            if rejection_summary["state"] != "verified":
                raise DrillFailure("DELETE rejection summary was not verified")

            txs_before_delete = _read_transactions(book_path)
            fixture_sha_before_delete = _sha256_path(book_path)
            backup_count_before_delete = _backup_file_count(work_dir)
            delete_response = client.delete(
                f"/books/{book_id}/transactions/{transaction_id}",
                headers=headers,
            )
            if delete_response.status_code != 200:
                raise DrillFailure(f"product DELETE route failed safely with status {delete_response.status_code}")
            delete_result = delete_response.json()
            if delete_result.get("transaction_id") != transaction_id:
                raise DrillFailure("DELETE returned a mismatched transaction reference")
            delete_backup_path = Path(str(delete_result.get("backup_path") or ""))
            if not delete_backup_path.is_file() or _inside_repo(delete_backup_path):
                raise DrillFailure("DELETE backup evidence failed safe scope/existence checks")
            if _read_transactions(delete_backup_path) != txs_before_delete:
                raise DrillFailure("DELETE backup did not capture pre-DELETE fixture contents")
            if _sha256_path(delete_backup_path) != fixture_sha_before_delete:
                raise DrillFailure("DELETE backup checksum did not match pre-DELETE fixture")

            txs_after_delete = _read_transactions(book_path)
            if len(txs_after_delete) != len(txs_after_create) - 1:
                raise DrillFailure("DELETE count was not exactly one")
            if any(tx["guid"] == transaction_id for tx in txs_after_delete):
                raise DrillFailure("deleted transaction remained after reopen")
            retained_before = [tx for tx in txs_before_delete if tx["guid"] != transaction_id]
            if txs_after_delete != retained_before:
                raise DrillFailure("DELETE changed a retained transaction")
            balances_after_delete = _read_account_balances(book_path, tracked_accounts)
            if balances_after_delete != balances_before_create:
                raise DrillFailure("DELETE did not revert account balances to the pre-CREATE state")
            if _backup_file_count(work_dir) != backup_count_before_delete + 1:
                raise DrillFailure("DELETE did not add exactly one backup")

            detail_after_delete = client.get(
                f"/books/{book_id}/transactions/{transaction_id}",
                headers=headers,
            )
            if detail_after_delete.status_code != 404:
                raise DrillFailure("post-DELETE read-back did not prove the transaction is absent")

            lock_key = str(book_path)
            if not lock_service.acquire(lock_key):
                raise DrillFailure("write lock was not released after DELETE")
            lock_service.release(lock_key)

            with session_factory() as session:
                delete_audit = session.get(AuditLog, delete_result.get("audit_log_id"))
                if delete_audit is None:
                    raise DrillFailure("DELETE audit log missing")
                delete_payload = json.loads(delete_audit.payload_json)
                if delete_audit.action != "transaction.delete" or delete_payload.get("result") != "success":
                    raise DrillFailure("DELETE audit success row missing")
                if delete_payload.get("transaction_id") != transaction_id:
                    raise DrillFailure("DELETE audit transaction reference mismatch")
                if delete_payload.get("backup_path") != str(delete_backup_path):
                    raise DrillFailure("DELETE audit backup reference mismatch")
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
                    raise DrillFailure("DELETE target was not exactly one app-created transaction")

            backup_count_after_delete = _backup_file_count(work_dir)

        disabled_delete_probe_summary, disabled_ok = _run_disabled_delete_probe(
            app_db=app_db,
            book_path=book_path,
            lock_dir=lock_dir,
            book_id=book_id,
            transaction_id=transaction_id,
            txs_after_delete=txs_after_delete,
            backup_count_after_delete=backup_count_after_delete,
        )
        if not disabled_ok:
            raise DrillFailure("disabled/reset DELETE probe did not fail closed")

    return build_redacted_delete_result_panel(disabled_delete_probe_summary=disabled_delete_probe_summary)


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
    parser = argparse.ArgumentParser(description="Run issue #51 redacted product-route app-owned DELETE drill.")
    parser.add_argument("--json-only", action="store_true", help="print only the redacted JSON result panel")
    args = parser.parse_args()
    try:
        result = run_issue51_product_delete_drill(_payload_from_stdin())
    except Exception as exc:
        print(f"FAIL: {exc.__class__.__name__}: {exc}; paths redacted", file=sys.stderr)
        return 2

    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.json_only:
        print(payload)
    else:
        print("PASS: issue51 product-route app-owned DELETE drill completed; paths redacted")
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
