#!/usr/bin/env python3
"""Best-effort copied-book mutation compatibility check harness.

This local-only harness is intended to run after a synthetic/disposable or
maintainer-copied write-alpha mutation. It opens the target with piecash in
read-only mode, optionally probes GnuCash CLI/Desktop tooling when it is already
available on PATH, and writes redacted JSON evidence. It never claims broad
Desktop/version compatibility from one run and never prints raw filesystem paths.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import piecash

Result = Literal["pass", "blocked", "fail"]
MAX_VERSION_OUTPUT_CHARS = 500
PATH_RE = re.compile(r"([A-Za-z]:\\[^\s]*|/[^\s]+|\\\\[^\s]+)")
AMOUNT_RE = re.compile(r"(?i)(amount\s*)\d+[.,]\d{2}")
PRIVATE_LABEL_RE = re.compile(r"(?i)\b(account|memo|description)\s+[^,;\n{}\[\]]+")
GNUCASH_VERSION_RE = re.compile(r"(?i)\bGnuCash\s+\d+(?:\.\d+)+\b")


class CompatibilityCheckFailure(Exception):
    """Raised for deterministic harness failures."""


@dataclass(frozen=True)
class PiecashReadEvidence:
    status: Result
    account_count: int
    transaction_count: int
    commodity_count: int
    scheduled_transaction_count: int
    error: str | None = None


@dataclass(frozen=True)
class DesktopToolEvidence:
    status: Result
    command: str
    available: bool
    version: str
    reason: str | None = None


@dataclass(frozen=True)
class CompatibilityEvidence:
    phase_number: int
    scenario_type: str
    classification: str
    result: Result
    broad_compatibility_claimed: bool
    target_path: str
    location_redaction_status: str
    piecash_read: PiecashReadEvidence
    desktop_tooling: DesktopToolEvidence
    redaction_contract: dict[str, Any]
    notes: list[str]


def _safe_error(exc: BaseException) -> str:
    return f"{exc.__class__.__name__}: detail redacted"


def _open_piecash_readonly(target: Path) -> PiecashReadEvidence:
    book = None
    try:
        book = piecash.open_book(str(target), readonly=True)
        accounts = list(getattr(book, "accounts", []) or [])
        transactions = list(getattr(book, "transactions", []) or [])
        commodities = list(getattr(book, "commodities", []) or [])
        scheduled = list(getattr(book, "scheduled_transactions", []) or [])
        return PiecashReadEvidence(
            status="pass",
            account_count=len(accounts),
            transaction_count=len(transactions),
            commodity_count=len(commodities),
            scheduled_transaction_count=len(scheduled),
        )
    except Exception as exc:  # pragma: no cover - exact piecash errors vary
        return PiecashReadEvidence(
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


def _version_output(command: str) -> str:
    try:
        completed = subprocess.run(
            [command, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
    except Exception:
        return "unknown"
    output_text = "\n".join(part for part in ((completed.stdout or "").strip(), (completed.stderr or "").strip()) if part)
    if not output_text or len(output_text) > MAX_VERSION_OUTPUT_CHARS:
        return "unknown"
    if PATH_RE.search(output_text) or AMOUNT_RE.search(output_text) or PRIVATE_LABEL_RE.search(output_text):
        return "unknown"
    first_line = output_text.strip().splitlines()[0]
    if not GNUCASH_VERSION_RE.search(first_line):
        return "unknown"
    return first_line[:80]


def _run_desktop_tooling(target: Path, timeout_seconds: int) -> DesktopToolEvidence:
    command = "gnucash-cli"
    if shutil.which(command) is None:
        return DesktopToolEvidence(
            status="blocked",
            command="gnucash-cli --report show --name Balance Sheet <redacted-book>",
            available=False,
            version="not available",
            reason="gnucash-cli not found on PATH; Desktop/CLI compatibility remains blocked",
        )

    try:
        completed = subprocess.run(
            [command, "--report", "show", "--name", "Balance Sheet", str(target)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return DesktopToolEvidence(
            status="fail",
            command="gnucash-cli --report show --name Balance Sheet <redacted-book>",
            available=True,
            version=_version_output(command),
            reason="gnucash-cli timed out; output redacted",
        )
    except Exception as exc:  # pragma: no cover - defensive
        return DesktopToolEvidence(
            status="fail",
            command="gnucash-cli --report show --name Balance Sheet <redacted-book>",
            available=True,
            version=_version_output(command),
            reason=_safe_error(exc),
        )

    version = _version_output(command)
    if version == "unknown":
        return DesktopToolEvidence(
            status="fail",
            command="gnucash-cli --report show --name Balance Sheet <redacted-book>",
            available=True,
            version="unknown",
            reason="unsafe or ambiguous gnucash-cli version output; Desktop/CLI compatibility remains blocked",
        )

    if completed.returncode == 0:
        return DesktopToolEvidence(
            status="pass",
            command="gnucash-cli --report show --name Balance Sheet <redacted-book>",
            available=True,
            version=version,
            reason=None,
        )
    return DesktopToolEvidence(
        status="fail",
        command="gnucash-cli --report show --name Balance Sheet <redacted-book>",
        available=True,
        version=version,
        reason=f"gnucash-cli exited nonzero ({completed.returncode}); output redacted",
    )


def run_check(target: Path, timeout_seconds: int = 60) -> CompatibilityEvidence:
    target = target.expanduser().resolve()
    if not target.exists() or not target.is_file():
        raise CompatibilityCheckFailure("target is missing or not a regular file; path=redacted")

    piecash_evidence = _open_piecash_readonly(target)
    desktop_evidence = _run_desktop_tooling(target, timeout_seconds)

    if piecash_evidence.status == "fail" or desktop_evidence.status == "fail":
        result: Result = "fail"
    elif desktop_evidence.status == "blocked":
        result = "blocked"
    else:
        result = "pass"

    return CompatibilityEvidence(
        phase_number=256,
        scenario_type="post-mutation-copied-book-compatibility-check",
        classification="synthetic-or-copied-disposable-only",
        result=result,
        broad_compatibility_claimed=False,
        target_path="<redacted>",
        location_redaction_status="redacted",
        piecash_read=piecash_evidence,
        desktop_tooling=desktop_evidence,
        redaction_contract={
            "raw_paths": "excluded",
            "account_names": "excluded",
            "transaction_descriptions": "excluded",
            "split_memos": "excluded",
            "amounts": "excluded",
            "desktop_stdout_stderr": "excluded",
        },
        notes=[
            "one local run is not broad Desktop/version compatibility evidence",
            "original and only-copy books remain forbidden for write-alpha dogfood",
            "GnuCash Desktop remains the authoritative editor",
        ],
    )


def _write_evidence(evidence: CompatibilityEvidence, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(asdict(evidence), indent=2, sort_keys=True)
    forbidden_fragments = ("/home/", "/tmp/", "Private", "private", "Salary", "Checking")
    if any(fragment in payload for fragment in forbidden_fragments):
        raise CompatibilityCheckFailure("redaction validation failed; output withheld")
    output.write_text(payload + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a redacted best-effort compatibility check for a copied/disposable mutated GnuCash book."
    )
    parser.add_argument("target", help="Synthetic/disposable or copied/restorable GnuCash SQLite book path.")
    parser.add_argument("--output", required=True, help="Path for redacted JSON evidence.")
    parser.add_argument("--desktop-timeout-seconds", type=int, default=60)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        evidence = run_check(Path(args.target), timeout_seconds=args.desktop_timeout_seconds)
        _write_evidence(evidence, Path(args.output).expanduser().resolve())
    except CompatibilityCheckFailure as exc:
        print(f"FAIL: {exc}; paths=redacted", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"FAIL: filesystem operation failed; detail=redacted; {exc.__class__.__name__}", file=sys.stderr)
        return 1

    if evidence.result == "pass":
        print("PASS: compatibility check passed; piecash=pass; desktop=pass; paths=redacted")
        return 0
    if evidence.result == "blocked":
        print("BLOCKED: piecash read passed but Desktop/CLI tooling is unavailable; paths=redacted")
        return 3
    print("FAIL: compatibility check failed; output details redacted", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
