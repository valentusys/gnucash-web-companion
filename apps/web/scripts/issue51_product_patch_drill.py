#!/usr/bin/env python3
"""Issue #51 explicit UI-harness product-route PATCH drill.

Creates exactly one app-owned disposable transaction as setup, then runs exactly
one metadata-only PATCH through the FastAPI product route. It verifies the PATCH
can change only description/split memo metadata and that amount, account, split,
date, and currency payloads are rejected without mutation. Output is a redacted
result panel only: no raw book paths, backup paths, account names, descriptions,
memos, amounts, transaction IDs, screenshots, tokens, or secrets.
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
from app.models import AuditLog, WriteAlphaTransactionOwnership  # noqa: E402
from app.services.gnucash_book import _guid  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

ISSUE51_PATCH_PANEL_ID = "issue51-redacted-patch-result"
EXPLICIT_CREATE_REF = "create-ref-redacted-issue51-patch-setup"
EXPLICIT_PATCH_REF = "patch-ref-redacted-issue51"
EXPLICIT_PATCH_BACKUP_REF = "backup-ref-redacted-issue51-patch"
EXPLICIT_PATCH_AUDIT_REF = "audit-ref-redacted-issue51-patch"
IMMUTABLE_REJECTED_FIELDS = ("amount", "account_id", "splits", "date", "currency")


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


def _assert_patch_preserved_financials(
    *,
    before: dict[str, Any],
    after: dict[str, Any],
    expected_description: str,
    expected_memos: dict[str, str],
) -> None:
    if after["description"] != expected_description:
        raise DrillFailure("metadata PATCH description mismatch")
    if after["post_date"] != before["post_date"]:
        raise DrillFailure("metadata PATCH changed the transaction date")
    if after["currency"] != before["currency"]:
        raise DrillFailure("metadata PATCH changed the transaction currency")
    if len(after["splits"]) != len(before["splits"]):
        raise DrillFailure("metadata PATCH changed the split count")
    before_by_guid = {split["guid"]: split for split in before["splits"]}
    after_by_guid = {split["guid"]: split for split in after["splits"]}
    if set(after_by_guid) != set(before_by_guid):
        raise DrillFailure("metadata PATCH changed split identity")
    for split_guid, before_split in before_by_guid.items():
        after_split = after_by_guid[split_guid]
        if after_split["account_guid"] != before_split["account_guid"]:
            raise DrillFailure("metadata PATCH changed a split account")
        if after_split["value"] != before_split["value"]:
            raise DrillFailure("metadata PATCH changed a split value")
        expected_memo = expected_memos.get(split_guid, before_split["memo"])
        if after_split["memo"] != expected_memo:
            raise DrillFailure("metadata PATCH split memo mismatch")


def _assert_immutable_rejections(
    *,
    client: TestClient,
    headers: dict[str, str],
    book_id: int,
    transaction_id: str,
    book_path: Path,
    work_dir: Path,
) -> list[dict[str, Any]]:
    txs_before = _read_transactions(book_path)
    backup_count_before = _backup_file_count(work_dir)
    probe_payloads: dict[str, dict[str, Any]] = {
        "amount": {"description": "immutable amount probe", "amount": "999.00"},
        "account_id": {"description": "immutable account probe", "account_id": DESTINATION_ACCOUNT_ID},
        "splits": {
            "description": "immutable split probe",
            "splits": [
                {"account_id": SOURCE_ACCOUNT_ID, "amount": "-999.00", "currency": "SEK", "memo": "immutable"},
                {"account_id": DESTINATION_ACCOUNT_ID, "amount": "999.00", "currency": "SEK", "memo": "immutable"},
            ],
        },
        "date": {"description": "immutable date probe", "date": "2026-07-06"},
        "currency": {"description": "immutable currency probe", "currency": "USD"},
    }
    probes = []
    for field_name in IMMUTABLE_REJECTED_FIELDS:
        response = client.patch(
            f"/books/{book_id}/transactions/{transaction_id}",
            json=probe_payloads[field_name],
            headers=headers,
        )
        if response.status_code != 422:
            raise DrillFailure(f"immutable {field_name} PATCH probe did not fail closed")
        if field_name not in json.dumps(response.json()):
            raise DrillFailure(f"immutable {field_name} PATCH probe did not identify the rejected field")
        if _read_transactions(book_path) != txs_before:
            raise DrillFailure(f"immutable {field_name} PATCH probe mutated the disposable fixture")
        if _backup_file_count(work_dir) != backup_count_before:
            raise DrillFailure(f"immutable {field_name} PATCH probe created backup evidence")
        probes.append(
            {
                "field": field_name,
                "status": "rejected_without_mutation",
                "http_status_class": response.status_code,
            }
        )
    return probes


def _run_disabled_patch_probe(
    *,
    app_db: Path,
    book_path: Path,
    lock_dir: Path,
    book_id: int,
    transaction_id: str,
    txs_after_patch: list[dict[str, Any]],
    backup_count_after_patch: int,
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
        response = client.patch(
            f"/books/{book_id}/transactions/{transaction_id}",
            json={"description": "disabled probe should not patch"},
            headers=headers,
        )
    blocked = response.status_code in {403, 404, 405}
    unchanged = _read_transactions(book_path) == txs_after_patch
    no_backup = _backup_file_count(app_db.parent) == backup_count_after_patch
    summary = {
        "state": "verified" if blocked and unchanged and no_backup else "failed",
        "app_env": "test",
        "gnucash_writes_enabled": False,
        "patch_execution_allowed_after_reset": False if blocked else True,
        "patch_execution_blocked_after_reset_verified": blocked,
        "probe": {
            "route_family": "patch",
            "status": "blocked_or_unavailable" if blocked else "unexpected",
            "http_status_class": response.status_code,
        },
    }
    return summary, blocked and unchanged and no_backup


def build_redacted_patch_result_panel(*, disabled_patch_probe_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "redacted_patch_result_panel": {
            "panel_id": ISSUE51_PATCH_PANEL_ID,
            "status": "success",
            "evidence_scope": "redacted_only",
            "target_class": "disposable_copied_like_fixture",
            "setup_create_count": 1,
            "patch_count": 1,
            "create_result_ref": EXPLICIT_CREATE_REF,
            "patch_result_ref": EXPLICIT_PATCH_REF,
            "backend_route_write_boundary": {
                "setup_create_product_route_used": True,
                "patch_product_route_used": True,
                "route": "PATCH /books/{book_id}/transactions/{transaction_id}",
                "route_response_status": 200,
                "app_env": "test",
                "gnucash_writes_enabled_during_patch": True,
                "normal_ui_patch_activated": False,
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
                "non_app_created_patch_allowed": False,
                "app_metadata_only": True,
            },
            "metadata_only_scope": {
                "description_updated": True,
                "split_memos_updated": True,
                "amount_changes_rejected": True,
                "account_changes_rejected": True,
                "split_changes_rejected": True,
                "date_changes_rejected": True,
                "currency_changes_rejected": True,
                "rejected_fields": list(IMMUTABLE_REJECTED_FIELDS),
                "split_structure_preserved": True,
                "financial_values_preserved": True,
                "post_date_preserved": True,
                "currency_preserved": True,
            },
            "read_back_verification": {
                "state": "verified",
                "transaction_ref": EXPLICIT_PATCH_REF,
                "transaction_present": True,
                "metadata_description_verified": True,
                "metadata_memo_verified": True,
                "split_count_unchanged": True,
                "split_accounts_unchanged": True,
                "split_values_unchanged": True,
                "post_date_unchanged": True,
                "currency_unchanged": True,
                "transaction_count_delta_after_patch": 0,
                "account_balance_delta_count": 0,
                "private_values_redacted": True,
            },
            "backup_state": {
                "state": "captured",
                "backup_ref": EXPLICIT_PATCH_BACKUP_REF,
                "exists_verified": True,
                "pre_patch_contents_verified": True,
                "raw_path_included": False,
            },
            "audit_state": {
                "state": "recorded",
                "audit_ref": EXPLICIT_PATCH_AUDIT_REF,
                "result": "success",
                "raw_payload_included": False,
            },
            "immutable_rejection_summary": {
                "state": "verified",
                "rejected_fields": list(IMMUTABLE_REJECTED_FIELDS),
                "http_status_class": 422,
                "mutation_count": 0,
                "backup_created": False,
            },
            "reset_default_disabled_patch_probe_summary": disabled_patch_probe_summary,
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


def run_issue51_product_patch_drill(product_create_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = product_create_payload or default_product_create_payload()
    _validate_payload(payload)
    if not SYNTHETIC_FIXTURE.is_file():
        raise DrillFailure("synthetic fixture is unavailable")

    with tempfile.TemporaryDirectory(prefix="issue51-product-patch-drill-") as tmp:
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
            created_before_patch = next((tx for tx in txs_after_create if tx["guid"] == transaction_id), None)
            if created_before_patch is None:
                raise DrillFailure("setup CREATE transaction missing after reopen")
            _assert_transaction_matches_create_payload(
                created=created_before_patch,
                payload=payload,
                tracked_accounts=tracked_accounts,
            )
            backup_count_after_create = _backup_file_count(work_dir)
            if backup_count_after_create < 1:
                raise DrillFailure("setup CREATE backup evidence missing")

            immutable_probe_results = _assert_immutable_rejections(
                client=client,
                headers=headers,
                book_id=book_id,
                transaction_id=transaction_id,
                book_path=book_path,
                work_dir=work_dir,
            )
            if [probe["field"] for probe in immutable_probe_results] != list(IMMUTABLE_REJECTED_FIELDS):
                raise DrillFailure("immutable rejection probe set mismatch")

            patch_description = "Synthetic PATCH metadata update"
            patch_memos = {created_before_patch["splits"][0]["guid"]: "Synthetic PATCH memo update"}
            txs_before_patch = _read_transactions(book_path)
            fixture_sha_before_patch = _sha256_path(book_path)
            balances_before_patch = _read_account_balances(book_path, tracked_accounts)
            patch_response = client.patch(
                f"/books/{book_id}/transactions/{transaction_id}",
                json={"description": patch_description, "split_memos": patch_memos},
                headers=headers,
            )
            if patch_response.status_code != 200:
                raise DrillFailure(f"metadata product PATCH route failed safely with status {patch_response.status_code}")
            patch_result = patch_response.json()
            if patch_result.get("transaction_id") != transaction_id:
                raise DrillFailure("metadata PATCH returned a mismatched transaction reference")
            patch_backup_path = Path(str(patch_result.get("backup_path") or ""))
            if not patch_backup_path.is_file() or _inside_repo(patch_backup_path):
                raise DrillFailure("PATCH backup evidence failed safe scope/existence checks")
            if _read_transactions(patch_backup_path) != txs_before_patch:
                raise DrillFailure("PATCH backup did not capture pre-PATCH fixture contents")
            if _sha256_path(patch_backup_path) != fixture_sha_before_patch:
                raise DrillFailure("PATCH backup checksum did not match pre-PATCH fixture")

            txs_after_patch = _read_transactions(book_path)
            if len(txs_after_patch) != len(txs_after_create):
                raise DrillFailure("metadata PATCH changed transaction count")
            patched = next((tx for tx in txs_after_patch if tx["guid"] == transaction_id), None)
            if patched is None:
                raise DrillFailure("metadata PATCH target missing after reopen")
            _assert_patch_preserved_financials(
                before=created_before_patch,
                after=patched,
                expected_description=patch_description,
                expected_memos=patch_memos,
            )
            balances_after_patch = _read_account_balances(book_path, tracked_accounts)
            if balances_after_patch != balances_before_patch:
                raise DrillFailure("metadata PATCH changed account balances")

            lock_key = str(book_path)
            if not lock_service.acquire(lock_key):
                raise DrillFailure("write lock was not released after PATCH")
            lock_service.release(lock_key)

            with session_factory() as session:
                patch_audit = session.get(AuditLog, patch_result.get("audit_log_id"))
                if patch_audit is None:
                    raise DrillFailure("PATCH audit log missing")
                patch_payload = json.loads(patch_audit.payload_json)
                if patch_audit.action != "transaction.patch" or patch_payload.get("result") != "success":
                    raise DrillFailure("PATCH audit success row missing")
                if patch_payload.get("transaction_id") != transaction_id:
                    raise DrillFailure("PATCH audit transaction reference mismatch")
                if patch_payload.get("backup_path") != str(patch_backup_path):
                    raise DrillFailure("PATCH audit backup reference mismatch")
                if set(patch_payload.get("request_summary", {}).get("fields_updated", [])) != {"description", "split_memos"}:
                    raise DrillFailure("PATCH audit fields-updated summary mismatch")
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
                    raise DrillFailure("PATCH target was not exactly one app-created transaction")

            backup_count_after_patch = _backup_file_count(work_dir)
            if backup_count_after_patch != backup_count_after_create + 1:
                raise DrillFailure("metadata PATCH did not add exactly one backup")

        disabled_patch_probe_summary, disabled_ok = _run_disabled_patch_probe(
            app_db=app_db,
            book_path=book_path,
            lock_dir=lock_dir,
            book_id=book_id,
            transaction_id=transaction_id,
            txs_after_patch=txs_after_patch,
            backup_count_after_patch=backup_count_after_patch,
        )
        if not disabled_ok:
            raise DrillFailure("disabled/reset PATCH probe did not fail closed")

    return build_redacted_patch_result_panel(disabled_patch_probe_summary=disabled_patch_probe_summary)


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
    parser = argparse.ArgumentParser(description="Run issue #51 redacted product-route metadata-only PATCH drill.")
    parser.add_argument("--json-only", action="store_true", help="print only the redacted JSON result panel")
    args = parser.parse_args()
    try:
        result = run_issue51_product_patch_drill(_payload_from_stdin())
    except Exception as exc:
        print(f"FAIL: {exc.__class__.__name__}: {exc}; paths redacted", file=sys.stderr)
        return 2

    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.json_only:
        print(payload)
    else:
        print("PASS: issue51 product-route metadata-only PATCH drill completed; paths redacted")
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
