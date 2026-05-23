#!/usr/bin/env python3
"""Non-mutating DELETE planning dry-run helper.

This helper never calls the DELETE mutation route and never opens a book for
write. It performs read-only eligibility checks for a proposed future DELETE
against a synthetic/disposable target, verifies backup/restore readiness inputs,
counts delete audit rows before and after, and proves target checksums are stable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import redact_dogfood_evidence  # noqa: E402


class DeleteDryRunFailure(Exception):
    """Raised when the DELETE dry-run cannot prove a safe non-mutating check."""


@dataclass(frozen=True)
class DeleteDryRunEvidence:
    phase_number: int
    scenario_type: str
    classification: str
    mode: str
    target_label: str
    transaction_id_label: str
    target_eligibility_status: str
    transaction_present: bool
    split_count: int
    backup_readiness_status: str
    restore_readiness_status: str
    write_runtime_status: str
    delete_route_called: bool
    mutation_requested: bool
    mutation_performed: bool
    book_checksum_before: str
    book_checksum_after: str
    book_checksum_stable: bool
    app_db_checksum_before: str
    app_db_checksum_after: str
    app_db_checksum_stable: bool
    delete_audit_rows_before: int
    delete_audit_rows_after: int
    audit_rows_stable: bool
    redaction_status: str
    result: str
    commands_run: list[str]
    notes: list[str]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_digest_label(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _target_label(path: Path) -> str:
    suffixes = "".join(path.suffixes[-2:]) if len(path.suffixes) >= 2 else path.suffix
    return f"<redacted{suffixes or '<no-extension>'}>"


def _connect_readonly(path: Path) -> sqlite3.Connection:
    uri = f"file:{path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _count_rows(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> int:
    row = conn.execute(sql, params).fetchone()
    return int(row[0] if row else 0)


def _verify_runtime_is_not_write_enabled() -> str:
    writes = os.environ.get("GNUCASH_WRITES_ENABLED", "false").strip().lower()
    if writes == "true":
        raise DeleteDryRunFailure("GNUCASH_WRITES_ENABLED must not be true for DELETE dry-run planning")
    return "not-write-enabled"


def _verify_target_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise DeleteDryRunFailure("target file is missing")
    try:
        path.relative_to(REPO_ROOT)
    except ValueError:
        return
    raise DeleteDryRunFailure("target must be outside the git working tree")


def _verify_backup_readiness(backup_dir: Path) -> str:
    # Non-mutating check: the helper does not create backups or probe files.
    parent = backup_dir if backup_dir.exists() else backup_dir.parent
    if not parent.exists() or not parent.is_dir():
        raise DeleteDryRunFailure("backup destination parent is not ready")
    if not os.access(parent, os.W_OK | os.X_OK):
        raise DeleteDryRunFailure("backup destination parent is not writable")
    return "parent-ready-no-backup-created"


def _book_transaction_status(book_path: Path, transaction_id: str) -> tuple[bool, int]:
    with _connect_readonly(book_path) as conn:
        present = _count_rows(conn, "select count(*) from transactions where guid = ?", (transaction_id,)) > 0
        split_count = _count_rows(conn, "select count(*) from splits where tx_guid = ?", (transaction_id,))
    return present, split_count


def _app_db_status(app_db_path: Path, book_id: int, transaction_id: str) -> tuple[bool, int]:
    with _connect_readonly(app_db_path) as conn:
        owned = _count_rows(
            conn,
            """
            select count(*)
            from write_alpha_transaction_ownership
            where book_id = ? and transaction_id = ? and created_by_write_alpha = 1
            """,
            (book_id, transaction_id),
        ) > 0
        audit_rows = _count_rows(conn, "select count(*) from audit_logs where action = 'transaction.delete'")
    return owned, audit_rows


def _write_evidence(evidence: DeleteDryRunEvidence, evidence_file: Path) -> None:
    data = asdict(evidence)
    redact_dogfood_evidence.sanitize_evidence(data, mode="reject")
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a non-mutating DELETE planning dry-run on a synthetic/disposable book."
    )
    parser.add_argument("--target", required=True, help="Synthetic/disposable target book outside this git repo.")
    parser.add_argument("--transaction-id", required=True, help="Candidate write-alpha-created transaction GUID.")
    parser.add_argument("--app-db", required=True, help="App metadata DB used only for read-only ownership/audit checks.")
    parser.add_argument("--book-id", required=True, type=int, help="App metadata book id for ownership lookup.")
    parser.add_argument("--backup-dir", required=True, help="Future backup destination to inspect without writing.")
    parser.add_argument("--restore-source", help="Optional restore source; must exist if provided, but is not copied.")
    parser.add_argument("--evidence-file", required=True, help="Destination for redacted JSON evidence.")
    parser.add_argument("--confirm-synthetic-disposable", action="store_true")
    parser.add_argument("--confirm-no-delete-route", action="store_true")
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> DeleteDryRunEvidence:
    if not args.confirm_synthetic_disposable:
        raise DeleteDryRunFailure("missing --confirm-synthetic-disposable")
    if not args.confirm_no_delete_route:
        raise DeleteDryRunFailure("missing --confirm-no-delete-route")

    target = Path(args.target).expanduser().resolve()
    app_db = Path(args.app_db).expanduser().resolve()
    backup_dir = Path(args.backup_dir).expanduser().resolve()
    evidence_file = Path(args.evidence_file).expanduser().resolve()
    restore_source = Path(args.restore_source).expanduser().resolve() if args.restore_source else target

    runtime_status = _verify_runtime_is_not_write_enabled()
    _verify_target_file(target)
    if not app_db.exists() or not app_db.is_file():
        raise DeleteDryRunFailure("app metadata DB is missing")
    if not restore_source.exists() or not restore_source.is_file():
        raise DeleteDryRunFailure("restore source is missing")

    book_before = _sha256(target)
    app_before = _sha256(app_db)
    backup_status = _verify_backup_readiness(backup_dir)
    restore_status = "source-readable-no-restore-run" if restore_source.stat().st_size > 0 else "source-empty-no-restore-run"
    if restore_status.startswith("source-empty"):
        raise DeleteDryRunFailure("restore source is empty")

    present, split_count = _book_transaction_status(target, args.transaction_id)
    owned, audit_before = _app_db_status(app_db, args.book_id, args.transaction_id)
    if not present:
        raise DeleteDryRunFailure("candidate transaction is absent from target")
    if split_count < 2:
        raise DeleteDryRunFailure("candidate transaction does not have enough splits for safe planning")
    if not owned:
        raise DeleteDryRunFailure("candidate transaction is not app-metadata write-alpha owned")

    # No mutation route call is made. Re-read after all checks to prove stability.
    book_after = _sha256(target)
    app_after = _sha256(app_db)
    _owned_after, audit_after = _app_db_status(app_db, args.book_id, args.transaction_id)

    evidence = DeleteDryRunEvidence(
        phase_number=345,
        scenario_type="delete-planning-dry-run-helper",
        classification="synthetic-disposable-only",
        mode="delete-dry-run",
        target_label=_target_label(target),
        transaction_id_label=f"opaque-transaction-ref-{_safe_digest_label(args.transaction_id)}",
        target_eligibility_status="write-alpha-owned",
        transaction_present=present,
        split_count=split_count,
        backup_readiness_status=backup_status,
        restore_readiness_status=restore_status,
        write_runtime_status=runtime_status,
        delete_route_called=False,
        mutation_requested=False,
        mutation_performed=False,
        book_checksum_before=book_before[:12],
        book_checksum_after=book_after[:12],
        book_checksum_stable=(book_before == book_after),
        app_db_checksum_before=app_before[:12],
        app_db_checksum_after=app_after[:12],
        app_db_checksum_stable=(app_before == app_after),
        delete_audit_rows_before=audit_before,
        delete_audit_rows_after=audit_after,
        audit_rows_stable=(audit_before == audit_after),
        redaction_status="validated-before-write",
        result="pass" if book_before == book_after and app_before == app_after and audit_before == audit_after else "blocked",
        commands_run=["python3 scripts/write_alpha_delete_dry_run.py <redacted args>"],
        notes=[
            "no DELETE route called",
            "target opened read-only",
            "app metadata opened read-only",
            "paths redacted",
            "no backup created and no restore copied",
        ],
    )
    if evidence.result != "pass":
        raise DeleteDryRunFailure("post-check stability failed")
    _write_evidence(evidence, evidence_file)
    return evidence


def main(argv: list[str] | None = None) -> int:
    try:
        evidence = run(parse_args(argv))
    except (DeleteDryRunFailure, sqlite3.Error, OSError) as exc:
        print(f"FAIL: DELETE dry-run blocked; {exc.__class__.__name__}; paths=redacted", file=sys.stderr)
        return 2
    print(
        "PASS: DELETE dry-run completed; mutation_performed=false; "
        "delete_route_called=false; "
        f"eligibility={evidence.target_eligibility_status}; "
        f"checksum_stable={str(evidence.book_checksum_stable).lower()}; paths=redacted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
