#!/usr/bin/env python3
"""Non-mutating owner write-session preflight and manifest prototype.

This helper is intentionally conservative. It checks only metadata needed before
any future owner write session and emits redacted JSON. It never mutates or
copies the target book, never enables writes, and never prints raw paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

Status = Literal["PASS", "BLOCKED"]

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKUP_DIR = "/tmp/gnucash-web-companion-owner-writebeta-backups"


@dataclass(frozen=True)
class OwnerWriteSessionPreflight:
    status: Status
    target_ref: str
    target_outside_git: bool
    target_readable: bool
    target_fingerprint_prefix: str | None
    backup_ref: str
    backup_ready: bool
    backup_outside_git: bool
    write_gate_default_disabled: bool
    runtime_writes_enabled: bool
    app_env: str
    desktop_lock_hint: str
    restore_helper_available: bool
    redaction_status: str
    mutation_performed: bool
    blockers: list[str]


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _fingerprint_prefix(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def _redacted_ref(path: Path | None, label: str) -> str:
    if path is None:
        return f"{label}:not-configured"
    suffix = "".join(path.suffixes[-2:]) if len(path.suffixes) >= 2 else path.suffix
    return f"{label}:redacted{suffix or '-no-extension'}"


def _default_disabled() -> bool:
    env_example = REPO_ROOT / ".env.example"
    compose = REPO_ROOT / "docker-compose.yml"
    return (
        env_example.exists()
        and compose.exists()
        and "GNUCASH_WRITES_ENABLED=false" in env_example.read_text(encoding="utf-8")
        and "GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}" in compose.read_text(encoding="utf-8")
    )


def _desktop_lock_hint(target: Path | None) -> str:
    if target is None:
        return "not-checked"
    candidates = [
        target.with_name(target.name + ".LCK"),
        target.with_suffix(target.suffix + ".LCK"),
        target.with_name(".LCK" + target.name),
    ]
    return "lock-file-present-redacted" if any(path.exists() for path in candidates) else "no-lock-file-hint"


def _helper_available() -> bool:
    helper = REPO_ROOT / "scripts" / "write_alpha_restore_verify.py"
    return helper.exists() and os.access(helper, os.R_OK)


def run_preflight(target: str | None, backup_dir: str = DEFAULT_BACKUP_DIR) -> OwnerWriteSessionPreflight:
    blockers: list[str] = []
    target_path = Path(target).expanduser().resolve() if target else None
    backup_path = Path(backup_dir).expanduser().resolve()

    target_exists = bool(target_path is not None and target_path.exists() and target_path.is_file())
    target_readable = bool(target_path is not None and target_exists and os.access(target_path, os.R_OK))
    target_outside_git = bool(target_path is not None and not _is_inside(target_path, REPO_ROOT))
    backup_outside_git = not _is_inside(backup_path, REPO_ROOT)
    backup_ready = backup_outside_git and (backup_path.exists() or os.access(backup_path.parent, os.W_OK))
    write_gate_default_disabled = _default_disabled()
    runtime_writes_enabled = os.environ.get("GNUCASH_WRITES_ENABLED", "false").strip().lower() == "true"
    app_env = os.environ.get("APP_ENV", "unset")
    restore_helper_available = _helper_available()

    fingerprint = None
    if not target_path:
        blockers.append("target path required")
    elif not target_exists:
        blockers.append("target file missing or not regular")
    elif not target_readable:
        blockers.append("target file unreadable")
    else:
        fingerprint = _fingerprint_prefix(target_path)

    if target_path and not target_outside_git:
        blockers.append("target must be outside git checkout")
    if not backup_outside_git:
        blockers.append("backup directory must be outside git checkout")
    if not backup_ready:
        blockers.append("backup directory parent is not writable or unavailable")
    if not write_gate_default_disabled:
        blockers.append("default disabled write gate is not preserved")
    if runtime_writes_enabled:
        blockers.append("runtime writes are enabled during non-mutating preflight")
    if app_env != "test":
        blockers.append("APP_ENV is not test for future enabled-write session")
    if not restore_helper_available:
        blockers.append("restore verification helper is unavailable")

    return OwnerWriteSessionPreflight(
        status="BLOCKED" if blockers else "PASS",
        target_ref=_redacted_ref(target_path, "target"),
        target_outside_git=target_outside_git,
        target_readable=target_readable,
        target_fingerprint_prefix=fingerprint,
        backup_ref=_redacted_ref(backup_path, "backup_dir"),
        backup_ready=backup_ready,
        backup_outside_git=backup_outside_git,
        write_gate_default_disabled=write_gate_default_disabled,
        runtime_writes_enabled=runtime_writes_enabled,
        app_env=app_env,
        desktop_lock_hint=_desktop_lock_hint(target_path),
        restore_helper_available=restore_helper_available,
        redaction_status="raw-paths-redacted",
        mutation_performed=False,
        blockers=blockers,
    )


def build_manifest(preflight: OwnerWriteSessionPreflight, phase: int) -> dict[str, object]:
    return {
        "phase": phase,
        "session_ref": "owner-write-session-redacted",
        "status": preflight.status,
        "target_ref": preflight.target_ref,
        "target_fingerprint_prefix": preflight.target_fingerprint_prefix,
        "backup_ref": preflight.backup_ref,
        "backup_readiness_status": "ready" if preflight.backup_ready else "blocked",
        "restore_check_status": "helper-available" if preflight.restore_helper_available else "blocked",
        "write_gate_default_disabled": preflight.write_gate_default_disabled,
        "runtime_writes_enabled": preflight.runtime_writes_enabled,
        "redaction_status": preflight.redaction_status,
        "mutation_performed": False,
        "blockers": preflight.blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run non-mutating owner write-session preflight")
    parser.add_argument("--target", required=True, help="outside-git copied/restorable target book")
    parser.add_argument("--backup-dir", default=DEFAULT_BACKUP_DIR, help="outside-git backup directory")
    parser.add_argument("--manifest", help="optional redacted manifest output path")
    parser.add_argument("--phase", type=int, default=446)
    args = parser.parse_args()

    result = run_preflight(args.target, args.backup_dir)
    payload = asdict(result)
    if args.manifest:
        manifest_path = Path(args.manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(build_manifest(result, args.phase), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
