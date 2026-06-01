"""Tests for safe compatibility report helper."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "safe_compatibility_report.py"


def test_safe_compatibility_report_redacts_sensitive_like_values():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--app-ref",
            "v0.5.2-public-readonly-beta",
            "--backend-type",
            "sqlite",
            "--fixture-scope",
            "synthetic",
            "--gnucash-version",
            "/private/book/path 5.10",
            "--browser-family",
            "Firefox",
            "--error-class",
            "SomeError at C:\\Users\\Owner\\Book.gnucash.sqlite amount 123.45",
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    output = proc.stdout
    assert "v0.5.2-public-readonly-beta" in output
    assert "[REDACTED_PATH]" in output
    assert "[REDACTED_AMOUNT]" in output
    assert "/private/book/path" not in output
    assert "C:\\Users" not in output
    assert "123.45" not in output
    assert "account" not in output.lower().replace("account names", "")


def test_safe_compatibility_report_classifies_evidence_without_broad_claim():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--app-ref",
            "v0.5.0-public-readonly-beta",
            "--backend-type",
            "sqlite",
            "--fixture-scope",
            "copied-restorable",
            "--gnucash-version",
            "GnuCash 5.10",
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )

    output = proc.stdout.lower()
    assert '"evidence_class": "copied-restorable-report"' in output
    assert '"support_claim": "redacted report only; not a compatibility guarantee"' in output
    assert "fully compatible" not in output
    assert "supports all gnucash" not in output


def test_safe_compatibility_report_marks_non_sqlite_as_unverified():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--backend-type",
            "postgres",
            "--fixture-scope",
            "synthetic",
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )

    assert '"evidence_class": "unverified"' in proc.stdout
