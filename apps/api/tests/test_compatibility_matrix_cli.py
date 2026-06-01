"""Tests for the redacted compatibility matrix row CLI."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "build_compatibility_matrix_row.py"


def _run_cli(payload: dict[str, object], *args: str) -> subprocess.CompletedProcess[str]:
    metadata = ROOT / ".pytest_cache" / "compatibility-metadata-input.json"
    metadata.parent.mkdir(exist_ok=True)
    metadata.write_text(json.dumps(payload), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(metadata), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )


def test_matrix_cli_builds_blocked_desktop_row_without_private_values() -> None:
    proc = _run_cli(
        {
            "backend": "SQLite",
            "fixture_origin": "desktop-generated-synthetic",
            "desktop_generated_synthetic_fixture": True,
            "gnucash_desktop_version": "GnuCash 5.14",
            "book_path": "/private/owner/Book.gnucash.sqlite",
            "versions": {"Gnucash": 3000000},
            "table_counts": {"accounts": 5, "transactions": 1},
        }
    )

    assert proc.returncode == 0
    row = json.loads(proc.stdout)
    assert row["category"] == "manual_fixture_blocked"
    assert row["status"] == "metadata captured; read-only validation still required"
    assert row["backend"] == "SQLite"
    assert row["fixture_origin"] == "desktop-generated-synthetic"
    assert row["desktop_version_evidence"] == "operator-supplied: GnuCash 5.14; not independently validated"
    assert "/private/owner" not in proc.stdout
    assert "Book.gnucash.sqlite" not in proc.stdout
    assert proc.stderr == ""


def test_matrix_cli_requires_explicit_validation_flag_for_tested_desktop_row() -> None:
    proc = _run_cli(
        {
            "backend": "SQLite",
            "fixture_origin": "desktop-generated-synthetic",
            "desktop_generated_synthetic_fixture": True,
            "gnucash_desktop_version": "GnuCash 5.14",
            "versions": {"Gnucash": 3000000},
            "table_counts": {"accounts": 5},
        },
        "--read-only-validation-passed",
    )

    assert proc.returncode == 0
    row = json.loads(proc.stdout)
    assert row["category"] == "tested_synthetic_fixture"
    assert row["desktop_version_evidence"] == "Desktop-generated synthetic fixture validated read-only"
    assert "no broad backend/version/real-book guarantee" in row["safe_copy"]


def test_matrix_cli_rejects_malformed_json_without_echoing_input_path() -> None:
    missing = ROOT / ".pytest_cache" / "missing-private-metadata.json"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(missing)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert proc.stdout == ""
    assert "metadata file could not be read" in proc.stderr
    assert str(missing) not in proc.stderr
