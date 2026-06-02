#!/usr/bin/env python3
"""Validate redacted public compatibility feedback reports.

The validator accepts the JSON emitted by `scripts/safe_compatibility_report.py`
and rejects private/raw additions, broad compatibility claims, path-like values,
amount-like values, and mismatched evidence classifications.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "gnucash-web-companion-safe-compatibility-v1"
ALLOWED_BACKEND_TYPES = {"sqlite", "postgres", "mysql", "unknown"}
ALLOWED_FIXTURE_SCOPES = {"synthetic", "disposable", "copied-restorable", "unknown"}
MAX_TEXT_FIELD_LENGTH = 160
ALLOWED_KEYS = {
    "report_schema",
    "app_tag_or_commit",
    "os_family",
    "os_release_major",
    "python_version",
    "node_version",
    "docker_version",
    "gnucash_version",
    "browser_family",
    "book_backend_type",
    "fixture_scope",
    "evidence_class",
    "support_claim",
    "error_class",
    "privacy_notice",
}
FORBIDDEN_KEY_RE = re.compile(r"(path|file|dir|secret|token|password|key|account|memo|description|amount)", re.I)
PATH_RE = re.compile(r"([A-Za-z]:\\[^\s]*|/[^\s]+|\\\\[^\s]+)")
AMOUNT_RE = re.compile(r"(?i)(amount\s*)\d+[.,]\d{2}")
BROAD_SUPPORT_RE = re.compile(
    r"(?i)(fully compatible|supports all gnucash|compatible with all gnucash|guaranteed compatible|production-ready compatibility)"
)
PRIVATE_LABEL_RE = re.compile(r"(?i)\b(account|memo|description)\s+[^,;\n{}\[\]]+")


class ValidationError(ValueError):
    """Path-redacted report validation failure."""


def _expected_evidence_class(backend_type: object, fixture_scope: object) -> str:
    if backend_type != "sqlite":
        return "unverified"
    if fixture_scope == "synthetic":
        return "tested-synthetic-fixture"
    if fixture_scope == "disposable":
        return "tested-disposable-report"
    if fixture_scope == "copied-restorable":
        return "copied-restorable-report"
    return "unverified"


def _load_report(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError("report file could not be read or parsed") from exc
    if not isinstance(loaded, dict):
        raise ValidationError("report must be a JSON object")
    return loaded


def validate_report(report: dict[str, Any]) -> dict[str, str | bool]:
    for key in report:
        if key not in ALLOWED_KEYS or FORBIDDEN_KEY_RE.search(key):
            raise ValidationError("unsafe key in compatibility report")

    missing = sorted(ALLOWED_KEYS - set(report))
    if missing:
        raise ValidationError("missing required compatibility report field")
    if report.get("report_schema") != SCHEMA:
        raise ValidationError("unsupported compatibility report schema")

    for key in ALLOWED_KEYS:
        if not isinstance(report.get(key), str):
            raise ValidationError("invalid compatibility report field type")
        if len(str(report[key])) > MAX_TEXT_FIELD_LENGTH and key != "privacy_notice":
            raise ValidationError("compatibility report field is too long")
    if report.get("book_backend_type") not in ALLOWED_BACKEND_TYPES:
        raise ValidationError("invalid compatibility report enum")
    if report.get("fixture_scope") not in ALLOWED_FIXTURE_SCOPES:
        raise ValidationError("invalid compatibility report enum")

    serialized = json.dumps(report, ensure_ascii=False)
    if BROAD_SUPPORT_RE.search(serialized):
        raise ValidationError("broad support phrase is not allowed")

    for key, value in report.items():
        if key == "privacy_notice":
            continue
        value_text = json.dumps(value, ensure_ascii=False)
        if PATH_RE.search(value_text) or AMOUNT_RE.search(value_text):
            raise ValidationError("unsafe path-like or amount-like value in report")
        if PRIVATE_LABEL_RE.search(value_text):
            raise ValidationError("unsafe account-like, memo-like, or description-like value in report")

    expected = _expected_evidence_class(report.get("book_backend_type"), report.get("fixture_scope"))
    if report.get("evidence_class") != expected:
        raise ValidationError("evidence_class does not match backend/scope")
    if report.get("support_claim") != "redacted report only; not a compatibility guarantee":
        raise ValidationError("support_claim must remain the conservative non-guarantee text")

    return {
        "accepted": True,
        "report_schema": SCHEMA,
        "evidence_class": str(report["evidence_class"]),
        "support_claim": str(report["support_claim"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a redacted compatibility report JSON file.")
    parser.add_argument("report_json", help="Path to compatibility report JSON")
    args = parser.parse_args(argv)

    try:
        result = validate_report(_load_report(Path(args.report_json)))
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
