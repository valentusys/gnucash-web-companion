"""Tests for safe public compatibility report validation."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_compatibility_report.py"


def _write_report(tmp_path: Path, payload: dict[str, object]) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "report.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _valid_report() -> dict[str, object]:
    return {
        "report_schema": "gnucash-web-companion-safe-compatibility-v1",
        "app_tag_or_commit": "v0.5.0-public-readonly-beta",
        "os_family": "Linux",
        "os_release_major": "6",
        "python_version": "3.11.0",
        "node_version": "v20.0.0",
        "docker_version": "Docker version 27.0.0",
        "gnucash_version": "GnuCash 5.14",
        "browser_family": "Firefox",
        "book_backend_type": "sqlite",
        "fixture_scope": "synthetic",
        "evidence_class": "tested-synthetic-fixture",
        "support_claim": "redacted report only; not a compatibility guarantee",
        "error_class": "none",
        "privacy_notice": "No books, app DBs, backups, screenshots, CSV exports, private paths, account names, memos, descriptions, amounts, secrets, or tokens are included.",
    }


def test_validate_compatibility_report_accepts_safe_report(tmp_path: Path) -> None:
    report = _write_report(tmp_path, _valid_report())
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(report)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 0
    result = json.loads(proc.stdout)
    assert result == {
        "accepted": True,
        "report_schema": "gnucash-web-companion-safe-compatibility-v1",
        "evidence_class": "tested-synthetic-fixture",
        "support_claim": "redacted report only; not a compatibility guarantee",
    }
    assert proc.stderr == ""


def test_validate_compatibility_report_rejects_broad_claim_and_paths(tmp_path: Path) -> None:
    payload = _valid_report()
    payload["support_claim"] = "Fully compatible with all GnuCash books at /private/book.gnucash.sqlite"
    report = _write_report(tmp_path, payload)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(report)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert proc.stdout == ""
    assert "broad support phrase" in proc.stderr
    assert "/private/book" not in proc.stderr


def test_validate_compatibility_report_rejects_mismatched_evidence_class(tmp_path: Path) -> None:
    payload = _valid_report()
    payload["book_backend_type"] = "postgres"
    payload["evidence_class"] = "tested-synthetic-fixture"
    report = _write_report(tmp_path, payload)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(report)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert "evidence_class does not match backend/scope" in proc.stderr


def test_validate_compatibility_report_rejects_forbidden_extra_keys(tmp_path: Path) -> None:
    payload = _valid_report()
    payload["raw_account_name"] = "Checking"
    report = _write_report(tmp_path, payload)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(report)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert "unsafe key" in proc.stderr
    assert "Checking" not in proc.stderr


def test_validate_compatibility_report_rejects_account_memo_description_like_values(tmp_path: Path) -> None:
    payload = _valid_report()
    payload["error_class"] = "ParserError account Checking memo Grocery description Card purchase"
    report = _write_report(tmp_path, payload)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(report)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert "unsafe account-like, memo-like, or description-like value" in proc.stderr
    assert "Checking" not in proc.stderr
    assert "Grocery" not in proc.stderr


def test_validate_compatibility_report_rejects_unknown_fields_types_and_enums(tmp_path: Path) -> None:
    cases = [
        ("bad_backend", {"book_backend_type": "xml"}, "invalid compatibility report enum"),
        ("bad_scope", {"fixture_scope": "real-private"}, "invalid compatibility report enum"),
        ("bad_python_type", {"python_version": 3.11}, "invalid compatibility report field type"),
        ("too_long", {"error_class": "x" * 161}, "compatibility report field is too long"),
    ]

    for name, updates, expected_error in cases:
        payload = _valid_report()
        payload.update(updates)
        report = _write_report(tmp_path / name, payload)
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(report)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
        )

        assert proc.returncode == 2
        assert expected_error in proc.stderr
        assert proc.stdout == ""


def test_validate_compatibility_report_rejects_privacy_notice_with_raw_paths_or_amounts(
    tmp_path: Path,
) -> None:
    payload = _valid_report()
    payload["privacy_notice"] = "No books included, but operator checked /home/user/book.gnucash and amount 12.34"
    report = _write_report(tmp_path, payload)

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(report)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert "unsafe path-like or amount-like value" in proc.stderr
    assert "/home/user" not in proc.stderr
    assert "12.34" not in proc.stderr
