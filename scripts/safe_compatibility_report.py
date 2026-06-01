#!/usr/bin/env python3
"""Print safe compatibility metadata for public read-only beta reports.

The helper intentionally avoids reading GnuCash books and redacts path-like,
secret-like, amount-like, account-like, memo-like, and description-like values.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

FORBIDDEN_KEY_RE = re.compile(r"(path|file|dir|secret|token|password|key|account|memo|description|amount)", re.I)
PATH_RE = re.compile(r"([A-Za-z]:\\[^\s]*|/[^\s]+|\\\\[^\s]+)")
AMOUNT_RE = re.compile(r"(?i)(amount\s*)\d+[.,]\d{2}")


def _evidence_class(backend_type: str, fixture_scope: str) -> str:
    """Classify public feedback as narrow report evidence, never support."""

    if backend_type != "sqlite":
        return "unverified"
    if fixture_scope == "synthetic":
        return "tested-synthetic-fixture"
    if fixture_scope == "disposable":
        return "tested-disposable-report"
    if fixture_scope == "copied-restorable":
        return "copied-restorable-report"
    return "unverified"


def _safe_text(value: str) -> str:
    value = PATH_RE.sub("[REDACTED_PATH]", value)
    value = AMOUNT_RE.sub("[REDACTED_AMOUNT]", value)
    return value[:160]


def _command_version(command: list[str]) -> str:
    try:
        proc = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return "not_detected"
    line = proc.stdout.splitlines()[0].strip() if proc.stdout else "not_detected"
    return _safe_text(line or "not_detected")


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "report_schema": "gnucash-web-companion-safe-compatibility-v1",
        "app_tag_or_commit": _safe_text(args.app_ref),
        "os_family": platform.system() or "unknown",
        "os_release_major": (platform.release().split(".")[0] if platform.release() else "unknown"),
        "python_version": platform.python_version(),
        "node_version": _command_version(["node", "--version"]),
        "docker_version": _command_version(["docker", "--version"]),
        "gnucash_version": _safe_text(args.gnucash_version or "not_provided"),
        "browser_family": _safe_text(args.browser_family or "not_provided"),
        "book_backend_type": args.backend_type,
        "fixture_scope": args.fixture_scope,
        "evidence_class": _evidence_class(args.backend_type, args.fixture_scope),
        "support_claim": "redacted report only; not a compatibility guarantee",
        "error_class": _safe_text(args.error_class or "none"),
        "privacy_notice": "No books, app DBs, backups, screenshots, CSV exports, private paths, account names, memos, descriptions, amounts, secrets, or tokens are included.",
    }


def validate_report(report: dict[str, Any]) -> None:
    for key, value in report.items():
        if FORBIDDEN_KEY_RE.search(key) and key not in {"privacy_notice"}:
            raise SystemExit(f"unsafe output key: {key}")
        text = json.dumps(value, ensure_ascii=False)
        if PATH_RE.search(text) or AMOUNT_RE.search(text):
            raise SystemExit(f"unsafe output value for {key}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit redacted compatibility metadata only.")
    parser.add_argument("--app-ref", default="unknown", help="Release tag or commit; no paths.")
    parser.add_argument("--backend-type", choices=["sqlite", "postgres", "mysql", "unknown"], default="unknown")
    parser.add_argument("--fixture-scope", choices=["synthetic", "disposable", "copied-restorable", "unknown"], default="unknown")
    parser.add_argument("--gnucash-version", default="")
    parser.add_argument("--browser-family", default="")
    parser.add_argument("--error-class", default="")
    args = parser.parse_args()
    report = build_report(args)
    validate_report(report)
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
