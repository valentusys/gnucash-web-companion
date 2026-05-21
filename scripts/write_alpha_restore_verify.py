#!/usr/bin/env python3
"""Restore verification harness for copied-book write-alpha dogfood.

This local-only harness restores a copied/disposable working book from a
pre-mutation backup, verifies checksum/read-back state, optionally executes an
operator-supplied read-only API/web probe command, writes redacted evidence, and
checks the committed default-disabled posture. It never prints raw filesystem
paths and never claims production disaster recovery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, Sequence

import piecash

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import redact_dogfood_evidence  # noqa: E402

Result = Literal["pass", "blocked", "fail"]


class RestoreVerifyFailure(Exception):
    """Raised when restore verification cannot proceed safely."""


@dataclass(frozen=True)
class ReadBackEvidence:
    status: Result
    account_count: int
    transaction_count: int
    commodity_count: int
    scheduled_transaction_count: int
    error: str | None = None


@dataclass(frozen=True)
class ApiReadEvidence:
    status: Result
    command: str
    required: bool
    reason: str | None = None


@dataclass(frozen=True)
class RestoreEvidence:
    phase_number: int
    scenario_type: str
    classification: str
    result: Result
    production_disaster_recovery_claimed: bool
    restore_status: str
    checksum_status: str
    backup_checksum_prefix: str
    restored_checksum_prefix: str
    expected_checksum_status: str
    read_back: ReadBackEvidence
    api_read: ApiReadEvidence
    backup_count: int
    audit_row_count: int
    lock_status: str
    restore_proof_status: str
    disabled_reset_status: str
    location_redaction_status: str
    redaction_status: str
    commands_run: list[str]
    artifact_refs: list[str]
    notes: list[str]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_error(exc: BaseException) -> str:
    return f"{exc.__class__.__name__}: detail redacted"


def _is_inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return False
    return True


def _require_safe_file(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.exists() or not resolved.is_file():
        raise RestoreVerifyFailure(f"{label} is missing or not a regular file; path=redacted")
    if _is_inside_repo(resolved):
        raise RestoreVerifyFailure(f"{label} must be outside this git checkout; path=redacted")
    return resolved


def _confirmations(args: argparse.Namespace) -> None:
    missing = []
    for flag in (
        "confirm_copied_disposable",
        "confirm_original_untouched",
        "confirm_restore_over_copy",
        "confirm_backup_pre_mutation",
    ):
        if not getattr(args, flag):
            missing.append("--" + flag.replace("_", "-"))
    if missing:
        raise RestoreVerifyFailure("required confirmation flag(s) missing: " + ", ".join(missing))


def _restore_backup(backup: Path, target: Path) -> tuple[str, str, str]:
    backup_checksum = _sha256(backup)
    shutil.copy2(backup, target)
    restored_checksum = _sha256(target)
    checksum_status = "verified-backup-matches-restored" if restored_checksum == backup_checksum else "failed-mismatch"
    return backup_checksum, restored_checksum, checksum_status


def _read_back_with_piecash(target: Path) -> ReadBackEvidence:
    book = None
    try:
        book = piecash.open_book(str(target), readonly=True)
        accounts = list(getattr(book, "accounts", []) or [])
        transactions = list(getattr(book, "transactions", []) or [])
        commodities = list(getattr(book, "commodities", []) or [])
        scheduled = list(getattr(book, "scheduled_transactions", []) or [])
        return ReadBackEvidence(
            status="pass",
            account_count=len(accounts),
            transaction_count=len(transactions),
            commodity_count=len(commodities),
            scheduled_transaction_count=len(scheduled),
        )
    except Exception as exc:  # pragma: no cover - piecash error classes vary
        return ReadBackEvidence(
            status="fail",
            account_count=0,
            transaction_count=0,
            commodity_count=0,
            scheduled_transaction_count=0,
            error=_safe_error(exc),
        )
    finally:
        close = getattr(book, "close", None)
        if callable(close):
            close()


def _run_api_read_command(command: Sequence[str] | None) -> ApiReadEvidence:
    if not command:
        return ApiReadEvidence(
            status="blocked",
            command="not-run; provide --api-read-command for local read-only web/API probe",
            required=False,
            reason="web/API read-back command not supplied; restore filesystem and piecash read-back can still be verified",
        )
    completed = subprocess.run(
        list(command),
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
        check=False,
    )
    if completed.returncode == 0:
        return ApiReadEvidence(
            status="pass",
            command="<operator-supplied-read-only-api-command>",
            required=True,
        )
    return ApiReadEvidence(
        status="fail",
        command="<operator-supplied-read-only-api-command>",
        required=True,
        reason=f"read-only API/web probe exited nonzero ({completed.returncode}); output redacted",
    )


def _default_disabled_status() -> str:
    env_example = REPO_ROOT / ".env.example"
    compose = REPO_ROOT / "docker-compose.yml"
    if "GNUCASH_WRITES_ENABLED=false" not in env_example.read_text(encoding="utf-8"):
        return "failed-env-example"
    if "GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}" not in compose.read_text(encoding="utf-8"):
        return "failed-compose-source"
    env = os.environ.copy()
    env.update(
        {
            "JWT_SECRET": "dummy-local-secret",
            "APP_ADMIN_PASSWORD": "dummy-local-password",
            "GNUCASH_WRITES_ENABLED": "false",
        }
    )
    result = subprocess.run(
        ["docker", "compose", "config"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return "blocked-compose-unavailable"
    if "GNUCASH_WRITES_ENABLED=false" not in result.stdout and 'GNUCASH_WRITES_ENABLED: "false"' not in result.stdout:
        return "failed-compose-rendered"
    return "verified-default-disabled"


def _expected_checksum_status(expected: str | None, restored_checksum: str) -> str:
    if expected is None:
        return "not-provided-backup-match-used"
    normalized = expected.strip().lower()
    if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
        raise RestoreVerifyFailure("expected checksum must be a full sha256 hex digest; value=redacted")
    return "verified-expected-checksum" if normalized == restored_checksum else "failed-expected-checksum-mismatch"


def _write_evidence(evidence: RestoreEvidence, output: Path) -> None:
    data = asdict(evidence)
    redact_dogfood_evidence.sanitize_evidence(data, mode="reject")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> RestoreEvidence:
    _confirmations(args)
    target = _require_safe_file(Path(args.target), "target")
    backup = _require_safe_file(Path(args.backup), "backup")
    output = Path(args.output).expanduser().resolve()

    backup_checksum, restored_checksum, checksum_status = _restore_backup(backup, target)
    expected_status = _expected_checksum_status(args.expected_restored_sha256, restored_checksum)
    read_back = _read_back_with_piecash(target)
    api_read = _run_api_read_command(args.api_read_command)
    disabled_status = _default_disabled_status()

    hard_fail = (
        checksum_status.startswith("failed")
        or expected_status.startswith("failed")
        or read_back.status == "fail"
        or api_read.status == "fail"
        or disabled_status.startswith("failed")
    )
    if hard_fail:
        result: Result = "fail"
    elif api_read.status == "blocked" or disabled_status.startswith("blocked"):
        result = "blocked"
    else:
        result = "pass"

    evidence = RestoreEvidence(
        phase_number=257,
        scenario_type="copied-book-restore-verification",
        classification="synthetic-or-copied-disposable-only",
        result=result,
        production_disaster_recovery_claimed=False,
        restore_status="restored-from-pre-mutation-backup" if checksum_status.startswith("verified") else "failed",
        checksum_status=checksum_status,
        backup_checksum_prefix=backup_checksum[:12],
        restored_checksum_prefix=restored_checksum[:12],
        expected_checksum_status=expected_status,
        read_back=read_back,
        api_read=api_read,
        backup_count=1,
        audit_row_count=0,
        lock_status="not-acquired-restore-harness-offline",
        restore_proof_status="verified" if checksum_status.startswith("verified") and read_back.status == "pass" else "failed",
        disabled_reset_status=disabled_status,
        location_redaction_status="redacted",
        redaction_status="validated-before-write",
        commands_run=[
            "python3 scripts/write_alpha_restore_verify.py --target <redacted-copy> --backup <redacted-pre-mutation-backup> --output <redacted-evidence-json>",
            "optional read-only web/API probe command" if args.api_read_command else "web/API probe not supplied",
            "JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> GNUCASH_WRITES_ENABLED=false docker compose config",
        ],
        artifact_refs=["<redacted-artifact-ref:phase-257-restore-evidence>"],
        notes=[
            "restore target and backup paths redacted",
            "restore applies only to copied/disposable working book, never original or only-copy books",
            "this is operator restore proof, not production disaster-recovery certification",
        ],
    )
    _write_evidence(evidence, output)
    return evidence


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Restore a copied/disposable book from a pre-mutation backup and write redacted verification evidence."
    )
    parser.add_argument("--target", required=True, help="Copied/disposable working book to restore; must be outside this git repo.")
    parser.add_argument("--backup", required=True, help="Pre-mutation backup to restore from; must be outside this git repo.")
    parser.add_argument("--output", required=True, help="Destination for redacted JSON evidence.")
    parser.add_argument("--expected-restored-sha256", help="Optional full sha256 expected after restore.")
    parser.add_argument("--api-read-command", nargs="+", help="Optional local read-only web/API probe command; output is redacted.")
    parser.add_argument("--confirm-copied-disposable", action="store_true")
    parser.add_argument("--confirm-original-untouched", action="store_true")
    parser.add_argument("--confirm-restore-over-copy", action="store_true")
    parser.add_argument("--confirm-backup-pre-mutation", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        evidence = run(parse_args(argv))
    except RestoreVerifyFailure as exc:
        print(f"FAIL: {exc}; paths=redacted", file=sys.stderr)
        return 2
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"FAIL: restore verification operation failed; detail=redacted; {exc.__class__.__name__}", file=sys.stderr)
        return 1

    if evidence.result == "pass":
        print("PASS: restore verification passed; checksum=verified; read_back=pass; api_read=pass; paths=redacted")
        return 0
    if evidence.result == "blocked":
        print(
            "BLOCKED: restore and read-back completed but optional web/API probe or compose reset proof is blocked; paths=redacted"
        )
        return 3
    print("FAIL: restore verification failed; output details redacted", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
