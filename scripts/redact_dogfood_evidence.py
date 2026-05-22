#!/usr/bin/env python3
"""Redact or reject dogfood evidence fields that could leak private data.

The helper is intentionally conservative. It is meant for local dogfood report
preparation, not for reading GnuCash books or validating accounting content.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Literal

Mode = Literal["reject", "redact"]

PATH_EXTENSIONS = (
    ".gnucash",
    ".gnucash.sqlite",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".backup",
    ".bak",
    ".csv",
)
SENSITIVE_KEY_HINTS = (
    "path",
    "uri",
    "filename",
    "file_name",
    "account",
    "account_name",
    "memo",
    "description",
    "amount",
    "value",
    "split",
    "payload",
)
ALLOWLIST_KEY_HINTS = (
    "backup_count",
    "audit_row_count",
    "phase",
    "phase_number",
    "status",
    "classification",
    "scenario_type",
    "lock_status",
    "restore_proof_status",
    "disabled_reset_status",
)
PLACEHOLDERS = {
    "path": "<redacted-path>",
    "amount": "<redacted-amount>",
    "sensitive": "<redacted-sensitive-field>",
}

ABSOLUTE_POSIX_RE = re.compile(r"(^|\s)/(?:[^\s'\"]+/)+[^\s'\"]*")
HOME_RE = re.compile(r"(^|\s)~/(?:[^\s'\"]+/)*[^\s'\"]*")
WINDOWS_PATH_RE = re.compile(r"\b[A-Za-z]:\\(?:[^\\\s'\"]+\\)*[^\\\s'\"]*")
DATA_PATH_RE = re.compile(r"\bdata/(?:books|backups|app)/[^\s'\"]+", re.I)
AMOUNT_RE = re.compile(r"(?<![\w-])[-+]?\d{1,12}(?:[.,]\d{2,8})(?![\w-])")
CURRENCY_AMOUNT_RE = re.compile(r"(?:[$€₽£]\s*[-+]?\d|[-+]?\d[\d.,]*\s*(?:USD|EUR|RUB|GBP|CNY|JPY)\b)", re.I)


@dataclass(frozen=True)
class SanitizationFinding:
    pointer: str
    reason: str


class EvidenceRejected(ValueError):
    def __init__(self, findings: list[SanitizationFinding]):
        self.findings = findings
        summary = "; ".join(f"{finding.pointer}: {finding.reason}" for finding in findings)
        super().__init__(summary)


def _json_pointer(parent: str, token: str) -> str:
    escaped = token.replace("~", "~0").replace("/", "~1")
    return f"{parent}/{escaped}" if parent else f"/{escaped}"


def _key_is_sensitive(key: str) -> bool:
    lowered = key.lower()
    if any(allowed == lowered for allowed in ALLOWLIST_KEY_HINTS):
        return False
    return any(hint in lowered for hint in SENSITIVE_KEY_HINTS)


def _looks_path_like(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    if any(regex.search(stripped) for regex in (ABSOLUTE_POSIX_RE, HOME_RE, WINDOWS_PATH_RE, DATA_PATH_RE)):
        return True
    lowered = stripped.lower()
    if any(lowered.endswith(extension) for extension in PATH_EXTENSIONS):
        return True
    if "/" in stripped and PurePosixPath(stripped).suffix.lower() in PATH_EXTENSIONS:
        return True
    if "\\" in stripped and PureWindowsPath(stripped).suffix.lower() in PATH_EXTENSIONS:
        return True
    return False


def _looks_amount_like(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    return bool(AMOUNT_RE.search(stripped) or CURRENCY_AMOUNT_RE.search(stripped))


def _classify_string(value: str, *, key: str | None) -> str | None:
    if _looks_path_like(value):
        return "path"
    if _looks_amount_like(value):
        return "amount"
    if key is not None and _key_is_sensitive(key):
        return "sensitive"
    return None


def sanitize_evidence(data: Any, *, mode: Mode = "reject") -> Any:
    """Return sanitized evidence or raise EvidenceRejected.

    `reject` mode fails if any path-like, amount-like, or sensitive-key value is
    found. `redact` mode replaces those values with bounded placeholders.
    """
    findings: list[SanitizationFinding] = []

    def walk(value: Any, pointer: str, key: str | None, inherited_sensitive: bool = False) -> Any:
        current_key_sensitive = key is not None and _key_is_sensitive(key)
        child_sensitive = inherited_sensitive or current_key_sensitive
        if isinstance(value, dict):
            return {
                str(k): walk(v, _json_pointer(pointer, str(k)), str(k), child_sensitive)
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [
                walk(item, _json_pointer(pointer, str(index)), key, child_sensitive)
                for index, item in enumerate(value)
            ]
        if isinstance(value, str):
            reason = _classify_string(value, key=key)
            if reason is None and inherited_sensitive:
                reason = "sensitive"
            if reason is None:
                return value
            findings.append(SanitizationFinding(pointer=pointer or "/", reason=reason))
            return PLACEHOLDERS[reason]
        if isinstance(value, bool) or value is None:
            return value
        if isinstance(value, int):
            if inherited_sensitive:
                findings.append(SanitizationFinding(pointer=pointer or "/", reason="sensitive"))
                return PLACEHOLDERS["sensitive"]
            return value
        if isinstance(value, float):
            findings.append(SanitizationFinding(pointer=pointer or "/", reason="amount"))
            return PLACEHOLDERS["amount"]
        return value

    sanitized = walk(data, "", None)
    if findings and mode == "reject":
        raise EvidenceRejected(findings)
    return sanitized


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reject or redact dogfood evidence JSON that contains raw paths, amounts, memos, account names, or payloads."
    )
    parser.add_argument("input", nargs="?", help="JSON evidence file. Reads stdin when omitted.")
    parser.add_argument("--mode", choices=("reject", "redact"), default="reject")
    args = parser.parse_args(argv)

    try:
        raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
        data = json.loads(raw)
        sanitized = sanitize_evidence(data, mode=args.mode)
    except EvidenceRejected as exc:
        print(f"dogfood evidence rejected: {exc}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print(f"dogfood evidence error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(sanitized, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
