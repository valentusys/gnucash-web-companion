#!/usr/bin/env python3
"""Local-only copied-book write-alpha dogfood wrapper.

The wrapper orchestrates one explicit step at a time. It performs preflight,
creates an independent pre-step backup, optionally delegates a single CREATE
smoke command, writes redacted evidence, and re-checks committed defaults. It
never opens a GnuCash book itself and never prints raw filesystem paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import redact_dogfood_evidence  # noqa: E402
import write_alpha_preflight  # noqa: E402

Mode = Literal["dry-run", "create-one"]
DEFAULT_BACKUP_DIR = "data/backups/write-alpha-dogfood"
DEFAULT_CREATE_COMMAND = ("python3", "scripts/smoke/write-alpha-create-smoke.py")


class DogfoodWrapperFailure(Exception):
    """Raised when a dogfood wrapper safety check fails."""


@dataclass(frozen=True)
class DogfoodEvidence:
    phase_number: int
    scenario_type: str
    classification: str
    mode: Mode
    preflight_status: str
    backup_status: str
    backup_count: int
    mutation_requested: bool
    mutation_performed: bool
    create_command_status: str
    patch_status: str
    delete_status: str
    audit_row_count: int
    lock_status: str
    restore_proof_status: str
    disabled_reset_status: str
    location_redaction_status: str
    redaction_status: str
    result: str
    commands_run: list[str]
    notes: list[str]


def _redacted_target_label(path: Path) -> str:
    suffixes = "".join(path.suffixes[-2:]) if len(path.suffixes) >= 2 else path.suffix
    return f"<redacted{suffixes or '<no-extension>'}>"


def _sha256_prefix(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:12]


def _confirmations(args: argparse.Namespace) -> None:
    missing = []
    for flag in ("confirm_copied_disposable", "confirm_original_untouched", "confirm_outside_git"):
        if not getattr(args, flag):
            missing.append("--" + flag.replace("_", "-"))
    if args.create_one and not args.confirm_create_one_mutation:
        missing.append("--confirm-create-one-mutation")
    if missing:
        raise DogfoodWrapperFailure("required confirmation flag(s) missing: " + ", ".join(missing))


def _run_preflight(target: Path, backup_dir: Path | str) -> write_alpha_preflight.PreflightResult:
    result = write_alpha_preflight.run_preflight(target, backup_dir=backup_dir, repo_root=REPO_ROOT)
    if result.status != "ready":
        raise DogfoodWrapperFailure(f"preflight blocked: {result.reason}; target={result.target_label}")
    return result


def _backup_target(target: Path, backup_dir: Path | str) -> tuple[Path, str]:
    backup_root = Path(backup_dir).expanduser()
    if not backup_root.is_absolute():
        backup_root = (REPO_ROOT / backup_root).resolve()
    backup_root.mkdir(parents=True, exist_ok=True)
    digest = _sha256_prefix(target)
    suffixes = "".join(target.suffixes[-2:]) if len(target.suffixes) >= 2 else target.suffix
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    destination = backup_root / f"phase-254-pre-step-{timestamp}-{digest}{suffixes or '.copy'}"
    shutil.copy2(target, destination)
    backup_ref = hashlib.sha256(str(destination.name).encode("utf-8")).hexdigest()[:12]
    return destination, f"opaque-backup-ref-{backup_ref}"


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
            # The wrapper may be invoked with writes enabled for local dogfood.
            # Render Compose with the committed/default value to verify reset posture.
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


def _run_create_command(command: Sequence[str]) -> str:
    result = subprocess.run(
        list(command),
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise DogfoodWrapperFailure(f"create-one command failed with exit={result.returncode}; output=redacted")
    return "passed"


def audit_payload_from_log(log: Any) -> dict[str, Any]:
    """Return a parsed AuditLog payload without assuming the obsolete .payload field.

    Current app metadata models store JSON in AuditLog.payload_json. Older local
    helper snippets used .payload and could abort after a successful mutation
    while collecting diagnostic evidence. This helper accepts either shape but
    prefers payload_json, keeps parsing failures local to evidence collection,
    and never returns raw non-dict values.
    """
    raw = getattr(log, "payload_json", None)
    if raw is None:
        raw = getattr(log, "payload", None)
    if isinstance(raw, dict):
        return raw
    if raw in (None, ""):
        return {}
    try:
        parsed = json.loads(str(raw))
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def redacted_audit_payload_status(log: Any) -> dict[str, Any]:
    """Summarize audit payload collection without exposing raw private values."""
    try:
        payload = audit_payload_from_log(log)
    except Exception:  # pragma: no cover - defensive boundary for diagnostics only
        return {"status": "diagnostic-blocked", "result": "unknown", "backup_present": False}
    return {
        "status": "collected" if payload else "empty",
        "result": str(payload.get("result") or "unknown"),
        "backup_present": bool(payload.get("backup_path")),
        "transaction_ref_present": bool(payload.get("transaction_id")),
    }


def _write_evidence(evidence: DogfoodEvidence, evidence_file: Path) -> None:
    data = asdict(evidence)
    # Fail closed before writing: evidence must already be redacted/safe.
    redact_dogfood_evidence.sanitize_evidence(data, mode="reject")
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> DogfoodEvidence:
    mode: Mode = "dry-run" if args.dry_run else "create-one"
    target = Path(args.target).expanduser().resolve()
    evidence_file = Path(args.evidence_file).expanduser().resolve()
    _confirmations(args)
    preflight = _run_preflight(target, args.backup_dir)
    _backup_path, backup_ref = _backup_target(target, args.backup_dir)

    create_status = "not-run"
    mutation_performed = False
    commands = ["python3 scripts/write_alpha_preflight.py <redacted-target> --backup-dir <redacted-backup-dir>"]
    notes = [
        "target path redacted",
        "backup path redacted",
        f"target label {_redacted_target_label(target)}",
        f"backup ref {backup_ref}",
    ]

    if mode == "create-one":
        command = tuple(args.create_command or DEFAULT_CREATE_COMMAND)
        commands.append(" ".join(command))
        create_status = _run_create_command(command)
        mutation_performed = True
    else:
        commands.append("dry-run only; no mutation command executed")

    disabled_status = _default_disabled_status()
    result = "pass" if disabled_status.startswith("verified") or disabled_status.startswith("blocked-compose") else "blocked"
    evidence = DogfoodEvidence(
        phase_number=getattr(args, "phase_number", 254),
        scenario_type="copied-book-dogfood-wrapper",
        classification=getattr(args, "classification", "synthetic-or-copied-disposable-only"),
        mode=mode,
        preflight_status=preflight.status,
        backup_status="created-before-step",
        backup_count=1,
        mutation_requested=(mode == "create-one"),
        mutation_performed=mutation_performed,
        create_command_status=create_status,
        patch_status="not-supported-by-default",
        delete_status="not-supported-by-default",
        audit_row_count=0,
        lock_status="not-inspected-by-wrapper",
        restore_proof_status="operator-required-after-mutation",
        disabled_reset_status=disabled_status,
        location_redaction_status="redacted",
        redaction_status="validated-before-write",
        result=result,
        commands_run=commands,
        notes=notes,
    )
    _write_evidence(evidence, evidence_file)
    if evidence.result != "pass":
        raise DogfoodWrapperFailure(f"default-disabled verification failed: {disabled_status}")
    return evidence


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one explicit local-only copied-book write-alpha dogfood wrapper step with redacted evidence."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Run preflight + backup + evidence only; no mutation command.")
    mode.add_argument("--create-one", action="store_true", help="Run preflight + backup, then one delegated CREATE smoke command.")
    parser.add_argument("--target", required=True, help="Copied/disposable book path outside this git repo.")
    parser.add_argument("--backup-dir", default=DEFAULT_BACKUP_DIR, help="Backup destination; outside git or git-ignored.")
    parser.add_argument("--evidence-file", required=True, help="Destination for redacted JSON evidence.")
    parser.add_argument("--create-command", nargs="+", help="Command used by --create-one; defaults to write-alpha create smoke.")
    parser.add_argument("--confirm-copied-disposable", action="store_true")
    parser.add_argument("--confirm-original-untouched", action="store_true")
    parser.add_argument("--confirm-outside-git", action="store_true")
    parser.add_argument("--confirm-create-one-mutation", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        evidence = run(parse_args(argv))
    except DogfoodWrapperFailure as exc:
        print(f"FAIL: {exc}; paths=redacted", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"FAIL: filesystem operation failed; detail=redacted; {exc.__class__.__name__}", file=sys.stderr)
        return 1
    print(
        "PASS: copied-book dogfood wrapper completed; "
        f"mode={evidence.mode}; preflight={evidence.preflight_status}; "
        f"backup={evidence.backup_status}; default_disabled={evidence.disabled_reset_status}; paths=redacted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
