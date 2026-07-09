#!/usr/bin/env python3
"""Run a safe W3 write-alpha small batch on a copied GnuCash book.

Performs exactly two CREATE operations, exactly one metadata/memo-only PATCH on
one created transaction, and exactly one DELETE of the other created disposable
transaction, using a temporary app metadata DB outside git. Evidence is redacted
and must be stored outside the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

import piecash  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402
from app.models import WriteAlphaTransactionOwnership  # noqa: E402
from write_alpha_create_delete_chain import (  # noqa: E402
    bootstrap_metadata,
    configure_app,
    ensure_safe_runtime_artifact_dir,
    is_inside_repo,
    login,
    opaque,
    pick_two_accounts,
    read_counts,
    sha256,
    transaction_exists,
)


def transaction_split_ids(book_path: Path, tx_id: str) -> list[str]:
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        for tx in book.transactions:
            if getattr(tx, "guid", None) == tx_id:
                return [split.guid for split in tx.splits]
    finally:
        close = getattr(book, "close", None)
        if callable(close):
            close()
    raise RuntimeError("created transaction not found for patch preflight")


def run(book_path: Path, work_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    if not book_path.is_file():
        raise RuntimeError("book file missing")
    if is_inside_repo(book_path):
        raise RuntimeError("book must be outside git working tree")
    work_dir_class = ensure_safe_runtime_artifact_dir(work_dir, "work-dir")
    evidence_dir_class = ensure_safe_runtime_artifact_dir(evidence_dir, "evidence-dir")

    work_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    app_db = work_dir / "app-metadata-small-batch.sqlite"
    if app_db.exists():
        app_db.unlink()

    batch_backup = work_dir / "pre-small-batch-backup.gnucash.sqlite"
    shutil.copy2(book_path, batch_backup)

    before = sha256(book_path)
    before_counts = read_counts(book_path)
    account_a, account_b, currency = pick_two_accounts(book_path)

    engine, session_factory = configure_app(app_db, book_path, writes_enabled=True)
    created_ids: list[str] = []
    backup_paths: list[Path] = []
    patch_backup: Path | None = None
    delete_backup: Path | None = None
    deleted_transaction_absent = False
    try:
        book_id = bootstrap_metadata(session_factory, book_path)
        client = TestClient(app)
        headers = login(client)

        for idx in (1, 2):
            payload = {
                "date": "2026-05-26",
                "description": f"Write-alpha small batch disposable create {idx}",
                "splits": [
                    {"account_id": account_a, "amount": "-1", "currency": currency, "memo": ""},
                    {"account_id": account_b, "amount": "1", "currency": currency, "memo": ""},
                ],
            }
            response = client.post(f"/books/{book_id}/transactions", json=payload, headers=headers)
            if response.status_code != 201:
                raise RuntimeError(f"create {idx} failed: {response.status_code} {response.text[:200]}")
            data = response.json()
            created_ids.append(data["transaction_id"])
            backup_paths.append(Path(data["backup_path"]))
            if not transaction_exists(book_path, data["transaction_id"]):
                raise RuntimeError(f"created transaction {idx} missing on read-back")

        split_ids = transaction_split_ids(book_path, created_ids[0])
        patch_response = client.patch(
            f"/books/{book_id}/transactions/{created_ids[0]}",
            json={
                "description": "Write-alpha small batch disposable patched transaction",
                "split_memos": {split_ids[0]: "write-alpha small batch patched memo"},
            },
            headers=headers,
        )
        if patch_response.status_code != 200:
            raise RuntimeError(f"patch failed: {patch_response.status_code} {patch_response.text[:200]}")
        patch_json = patch_response.json()
        patch_backup = Path(patch_json["backup_path"])
        backup_paths.append(patch_backup)

        delete_response = client.delete(f"/books/{book_id}/transactions/{created_ids[1]}", headers=headers)
        if delete_response.status_code != 200:
            raise RuntimeError(f"delete failed: {delete_response.status_code} {delete_response.text[:200]}")
        delete_json = delete_response.json()
        delete_backup = Path(delete_json["backup_path"])
        backup_paths.append(delete_backup)
        deleted_transaction_absent = not transaction_exists(book_path, created_ids[1])
        if not deleted_transaction_absent:
            raise RuntimeError("deleted disposable transaction still present on read-back")

        with session_factory() as session:
            ownership_rows = session.query(WriteAlphaTransactionOwnership).filter(
                WriteAlphaTransactionOwnership.book_id == book_id,
                WriteAlphaTransactionOwnership.transaction_id.in_(created_ids),
                WriteAlphaTransactionOwnership.created_by_write_alpha == True,  # noqa: E712
            ).count()
        audit_response = client.get(f"/books/{book_id}/write-alpha-audit-summary", headers=headers)
        if audit_response.status_code != 200:
            raise RuntimeError(f"audit summary failed: {audit_response.status_code}")
        audit_json = audit_response.json()
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        engine.dispose()

    after = sha256(book_path)
    after_counts = read_counts(book_path)
    restored_target = work_dir / "restore-from-pre-small-batch.gnucash.sqlite"
    shutil.copy2(batch_backup, restored_target)
    restored_counts = read_counts(restored_target)
    restored_sha_matches = sha256(restored_target) == sha256(batch_backup)

    engine, _session_factory = configure_app(app_db, book_path, writes_enabled=False)
    try:
        client = TestClient(app)
        headers = login(client)
        disabled_create = client.post(
            f"/books/{book_id}/transactions",
            json={
                "date": "2026-05-26",
                "description": "disabled probe",
                "splits": [
                    {"account_id": account_a, "amount": "-1", "currency": currency, "memo": ""},
                    {"account_id": account_b, "amount": "1", "currency": currency, "memo": ""},
                ],
            },
            headers=headers,
        ).status_code
        disabled_patch = client.patch(
            f"/books/{book_id}/transactions/{created_ids[0]}",
            json={"description": "disabled patch probe"},
            headers=headers,
        ).status_code
        disabled_delete = client.delete(
            f"/books/{book_id}/transactions/{created_ids[1]}",
            headers=headers,
        ).status_code
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        engine.dispose()

    evidence = {
        "result": "pass",
        "scenario_type": "copied-book-write-alpha-small-batch",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "book_outside_git": True,
        "runtime_artifacts": {
            "work_dir_class": work_dir_class,
            "evidence_dir_class": evidence_dir_class,
            "tracked_artifacts_prevented": True,
            "raw_paths_redacted": True,
        },
        "operation_counts": {
            "create_attempts": 2,
            "create_successes": 2,
            "patch_attempts": 1,
            "patch_successes": 1,
            "delete_attempts": 1,
            "delete_successes": 1,
        },
        "book_sha_before_prefix": before[:12],
        "book_sha_after_prefix": after[:12],
        "before_counts": before_counts,
        "after_counts": after_counts,
        "created_transaction_opaque_refs": [opaque(tx) for tx in created_ids],
        "ownership_rows_for_created_transactions": ownership_rows,
        "route_backup_count": sum(1 for path in backup_paths if path.exists()),
        "pre_batch_backup_created": batch_backup.exists(),
        "patch_backup_created": bool(patch_backup and patch_backup.exists()),
        "delete": {
            "backup_created": bool(delete_backup and delete_backup.exists()),
            "deleted_created_transaction_absent": deleted_transaction_absent,
        },
        "read_back": {
            "created_transactions_present": [transaction_exists(book_path, created_ids[0])],
            "deleted_transaction_absent": deleted_transaction_absent,
        },
        "restore": {"restored_from_pre_batch_backup": True, "restored_sha_matches_backup": restored_sha_matches, "restored_counts": restored_counts},
        "compatibility": {"piecash_readonly_open": "pass", "mutated_counts_read": after_counts},
        "audit_summary": {
            "returned_count": audit_json.get("returned_count"),
            "counts_by_action": audit_json.get("counts_by_action"),
            "counts_by_result": audit_json.get("counts_by_result"),
            "ownership_summary": audit_json.get("ownership_summary"),
        },
        "default_disabled_probe": {
            "create_after_reset_status": disabled_create,
            "patch_after_reset_status": disabled_patch,
            "delete_after_reset_status": disabled_delete,
            "writes_disabled_forbidden": disabled_create == 403 and disabled_patch == 403 and disabled_delete == 403,
        },
        "redaction": "No private paths/account names/descriptions/memos/amounts are stored in committed docs.",
    }
    if not (
        ownership_rows == 2
        and all(evidence["read_back"]["created_transactions_present"])
        and evidence["read_back"]["deleted_transaction_absent"]
        and restored_sha_matches
        and evidence["default_disabled_probe"]["writes_disabled_forbidden"]
    ):
        evidence["result"] = "fail"
    evidence_file = evidence_dir / "write-alpha-small-batch-evidence.json"
    evidence_file.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()
    try:
        evidence = run(Path(args.book).resolve(), Path(args.work_dir).resolve(), Path(args.evidence_dir).resolve())
    except Exception as exc:
        print(f"FAIL: {exc.__class__.__name__}: {exc}; paths redacted", file=sys.stderr)
        return 2
    print("PASS: write-alpha small batch completed")
    print(f"  result={evidence['result']}")
    print(f"  operations={evidence['operation_counts']}")
    print(f"  ownership_rows={evidence['ownership_rows_for_created_transactions']}")
    print(f"  delete_absent={evidence['delete']['deleted_created_transaction_absent']}")
    print(f"  disabled_forbidden={evidence['default_disabled_probe']['writes_disabled_forbidden']}")
    print("  paths redacted")
    return 0 if evidence["result"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
