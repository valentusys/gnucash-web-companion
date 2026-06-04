#!/usr/bin/env python3
"""Guard committed write-safety defaults without opening runtime data.

This script reads only tracked configuration/docs. It verifies that committed
examples and rendered Compose defaults keep GnuCash writes disabled by default
and that public/default write-readiness docs still mention the APP_ENV=test gate.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WRITE_DEFAULT_TEXT = "GNUCASH_WRITES_ENABLED=false"
COMPOSE_WRITE_DEFAULT_TEXT = "GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}"
APP_ENV_GATE_TEXT = "APP_ENV=test"
EXPLICIT_WRITE_ENABLE_TEXT = "explicit write enablement"
RESET_TEXT = "reset"
DISABLED_PROBE_TEXT = "disabled-probe"
CHECKLIST_REQUIRED_TEXTS = (
    "#36",
    "keep #36 open",
    "no-release/no-public-write posture",
    "GNUCASH_WRITES_ENABLED=false",
    "APP_ENV=test",
    "owner-input/real-book/copy-book constraints",
    "next worker packages",
)
WRITE_COMPATIBILITY_DOCS = (
    Path("docs/write-alpha/evidence-matrix.md"),
    Path("docs/v0.2-controlled-writes.md"),
)
ISSUE_36_REMAINING_GATES_DOC = Path("docs/write-alpha/issue-36-remaining-gates.md")
ISSUE_36_DASHBOARD_DOC = Path("docs/write-alpha/controlled-write-readiness-dashboard.md")
RESTORE_BOUNDARY_DOC = Path("docs/write-alpha/restore-safety-boundary.md")
COPIED_DOGFOOD_PACKET_DOC = Path("docs/write-alpha/copied-book-dogfood-readiness-packet.md")
AFTER_W3_READINESS_BOUNDARY_DOC = Path("docs/write-alpha/after-w3-readiness-boundary.md")
BACKUP_RESTORE_READINESS_DOC = Path("docs/write-alpha/backup-restore-readiness-checklist.md")
WRITE_COMPATIBILITY_REQUIRED_TEXTS = (
    "supported-version write compatibility remains pending",
    "synthetic/disposable or copied/restorable evidence only",
    "not a real-book claim",
    "broad GnuCash compatibility",
    "public write beta",
    "production",
    "security-audited",
)
WRITE_COMPATIBILITY_FORBIDDEN_PATTERNS = (
    "broad GnuCash write compatibility is supported",
    "all GnuCash versions are write-compatible",
    "production-book write safety is proven",
    "real/private-book write-safety is proven",
    "public write beta is ready",
    "write mode is production-ready",
    "write mode is security-audited",
)


def _normalized(text: str) -> str:
    """Collapse Markdown wrapping so phrase guards do not depend on line breaks."""
    return " ".join(text.lower().split())


class GuardError(ValueError):
    """Path-redacted write-safety guard failure."""


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GuardError("required safety file could not be read") from exc


def _check_write_compatibility_docs(paths: tuple[Path, ...]) -> list[str]:
    failures: list[str] = []
    combined_text = ""
    for path in paths:
        doc_text = _read(REPO_ROOT / path if not path.is_absolute() else path)
        normalized = _normalized(doc_text)
        combined_text += " " + normalized
        for forbidden in WRITE_COMPATIBILITY_FORBIDDEN_PATTERNS:
            if _normalized(forbidden) in normalized:
                failures.append(f"write compatibility docs must not claim: {forbidden}")
    missing = [required for required in WRITE_COMPATIBILITY_REQUIRED_TEXTS if _normalized(required) not in combined_text]
    if missing:
        failures.append("write compatibility docs must preserve: " + ", ".join(missing))
    return failures


def _check_issue_36_remaining_gates(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "keep #36 open",
        "copied-book dogfood gate accepted",
        "W3 CREATE 2 / PATCH 1 / DELETE 1",
        "supported-version write compatibility evidence",
        "future copied/restorable mutation evidence packet",
        "same-context owner + PM authorization",
        "real/private/original/only-copy",
        "no public write beta",
        "NO_RELEASE",
        "CREATE 0 / PATCH 0 / DELETE 0",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["#36 remaining gates doc must preserve: " + ", ".join(missing)] if missing else []


def _check_issue_36_dashboard(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "keep #36 open",
        "state-machine evidence",
        "copied-book evidence",
        "restore evidence",
        "default-disabled probes",
        "compatibility gaps",
        "same-context owner + PM authorization",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "NO_RELEASE",
        "CREATE 0 / PATCH 0 / DELETE 0",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["#36 readiness dashboard must preserve: " + ", ".join(missing)] if missing else []


def _check_restore_boundary(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "restore-to-copy",
        "not destructive restore",
        "not real-book safety evidence",
        "independent backup",
        "redacted evidence only",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "CREATE 0 / PATCH 0 / DELETE 0",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["restore boundary doc must preserve: " + ", ".join(missing)] if missing else []


def _check_copied_dogfood_packet(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "non-mutating packet",
        "same-context owner + PM authorization",
        "route family and operation counts",
        "backup/read-back/audit/lock/restore/reset",
        "redacted evidence only",
        "no original/private/real-working/only-copy",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "CREATE 0 / PATCH 0 / DELETE 0",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["copied-book dogfood packet must preserve: " + ", ".join(missing)] if missing else []


def _check_after_w3_readiness_boundary(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "#36 remains open",
        "NO_RELEASE",
        "no public write beta",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "reset/default-disabled probes",
        "hard stop",
        "restore-to-copy",
        "supported-version write compatibility remains pending",
        "not a broad GnuCash compatibility claim",
        "not a real-book claim",
        "#22 closed only for narrow Desktop-generated synthetic SQLite fixture evidence",
        "PostgreSQL/MySQL/MariaDB GnuCash backends remain unclaimed",
        "same-context owner + PM authorization",
        "CREATE 0 / PATCH 0 / DELETE 0",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["after-W3 readiness boundary must preserve: " + ", ".join(missing)] if missing else []


def _check_backup_restore_readiness(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "non-mutating",
        "restore-to-copy",
        "copied/restorable or synthetic/disposable",
        "must not create backups",
        "must not restore into books",
        "must not run product dogfood",
        "real/original/private/working/only-copy book",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "public write beta readiness",
        "production safety",
        "security-audited status",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["backup/restore readiness checklist must preserve: " + ", ".join(missing)] if missing else []


def _check(env_example: Path, compose: Path, gate_doc: Path, checklist_doc: Path | None = None) -> list[str]:
    env_text = _read(env_example)
    compose_text = _read(compose)
    gate_text = _read(gate_doc)
    gate_text_normalized = _normalized(gate_text)
    failures: list[str] = []

    if WRITE_DEFAULT_TEXT not in env_text:
        failures.append(".env.example must set GNUCASH_WRITES_ENABLED=false")
    if "GNUCASH_WRITES_ENABLED=true" in env_text:
        failures.append(".env.example must not default or suggest GNUCASH_WRITES_ENABLED=true")
    if COMPOSE_WRITE_DEFAULT_TEXT not in compose_text:
        failures.append("Docker Compose must render GNUCASH_WRITES_ENABLED default false")
    if "GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-true}" in compose_text:
        failures.append("Docker Compose must not default GNUCASH_WRITES_ENABLED true")
    if APP_ENV_GATE_TEXT not in gate_text:
        failures.append("write-readiness documentation must preserve APP_ENV=test gate text")
    if EXPLICIT_WRITE_ENABLE_TEXT not in gate_text_normalized:
        failures.append("write-readiness documentation must require explicit write enablement")
    if RESET_TEXT not in gate_text_normalized or DISABLED_PROBE_TEXT not in gate_text_normalized:
        failures.append("write-readiness documentation must preserve reset/default-disabled probe wording")

    if checklist_doc is not None:
        checklist_text = _read(checklist_doc)
        checklist_text_normalized = _normalized(checklist_text)
        missing = [
            required
            for required in CHECKLIST_REQUIRED_TEXTS
            if _normalized(required) not in checklist_text_normalized
        ]
        if missing:
            failures.append("#36 audit checklist must preserve: " + ", ".join(missing))
    failures.extend(_check_write_compatibility_docs(WRITE_COMPATIBILITY_DOCS))
    failures.extend(_check_issue_36_remaining_gates(ISSUE_36_REMAINING_GATES_DOC))
    failures.extend(_check_issue_36_dashboard(ISSUE_36_DASHBOARD_DOC))
    failures.extend(_check_restore_boundary(RESTORE_BOUNDARY_DOC))
    failures.extend(_check_copied_dogfood_packet(COPIED_DOGFOOD_PACKET_DOC))
    failures.extend(_check_after_w3_readiness_boundary(AFTER_W3_READINESS_BOUNDARY_DOC))
    failures.extend(_check_backup_restore_readiness(BACKUP_RESTORE_READINESS_DOC))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check committed/default write-safety posture.")
    parser.add_argument("--env-example", default=str(REPO_ROOT / ".env.example"))
    parser.add_argument("--compose", default=str(REPO_ROOT / "docker-compose.yml"))
    parser.add_argument(
        "--gate-doc",
        default=str(REPO_ROOT / "docs/write-alpha/owner-writebeta-operating-guide.md"),
    )
    parser.add_argument(
        "--checklist-doc",
        default=str(REPO_ROOT / "docs/write-alpha-maintainer-checklist.md"),
    )
    args = parser.parse_args(argv)

    try:
        failures = _check(
            Path(args.env_example),
            Path(args.compose),
            Path(args.gate_doc),
            Path(args.checklist_doc),
        )
    except GuardError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if failures:
        print("unsafe write-safety defaults: " + "; ".join(failures), file=sys.stderr)
        return 2
    print(
        "write-safety defaults ok: GNUCASH_WRITES_ENABLED=false; "
        "APP_ENV=test gate text present; explicit write enablement present; "
        "reset/default-disabled probe wording present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
