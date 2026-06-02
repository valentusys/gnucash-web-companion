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


def _check(env_example: Path, compose: Path, gate_doc: Path) -> list[str]:
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
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check committed/default write-safety posture.")
    parser.add_argument("--env-example", default=str(REPO_ROOT / ".env.example"))
    parser.add_argument("--compose", default=str(REPO_ROOT / "docker-compose.yml"))
    parser.add_argument(
        "--gate-doc",
        default=str(REPO_ROOT / "docs/write-alpha/owner-writebeta-operating-guide.md"),
    )
    args = parser.parse_args(argv)

    try:
        failures = _check(Path(args.env_example), Path(args.compose), Path(args.gate_doc))
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
