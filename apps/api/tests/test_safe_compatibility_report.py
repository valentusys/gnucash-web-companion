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
