import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.check_tracked_hygiene as guard


def test_path_violations_reject_private_artifact_classes(tmp_path):
    repo = guard.REPO_ROOT
    candidates = [
        repo / ".env",
        repo / ".hermes" / "cache" / "prompt.txt",
        repo / "data" / "books" / "book.gnucash.sqlite",
        repo / "data" / "app" / "app.db",
        repo / "secrets" / "api.key",
        repo / "docs" / "evidence.csv",
        repo / "docs" / "raw-ledger-export.sql",
        repo / "docs" / "book-backup.zip",
        repo / "docs" / "evidence-screenshot.png",
    ]

    problems = guard.path_violations(candidates)

    assert len(problems) >= len(candidates)


def test_path_violations_allow_safe_docs_and_code():
    repo = guard.REPO_ROOT
    candidates = [
        repo / "README.md",
        repo / "docs" / "community" / "public-readonly-beta-feedback-packet.md",
        repo / "docs" / "images" / "dashboard-desktop.png",
        repo / "apps" / "api" / "app" / "diagnostics.py",
    ]

    assert guard.path_violations(candidates) == []


def test_content_violations_reject_private_key_marker(tmp_path, monkeypatch):
    sample = tmp_path / "safe-name.txt"
    marker = "-----BEGIN " + "OPENSSH" + " PRIVATE KEY-----"
    sample.write_text(f"{marker}\nredacted\n", encoding="utf-8")
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == ["tracked private-key marker in: safe-name.txt"]


def test_content_violations_reject_raw_private_evidence_markers(tmp_path, monkeypatch):
    sample = tmp_path / "public-report.md"
    sample.write_text(
        "RAW_PRIVATE_EVIDENCE_BEGIN\nPRIVATE_BOOK_PATH=/redacted\nTRANSACTION_AMOUNT=0.00\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked raw private-evidence marker 'RAW_PRIVATE_EVIDENCE_BEGIN' in: public-report.md",
        "tracked raw private-evidence marker 'PRIVATE_BOOK_PATH=' in: public-report.md",
        "tracked raw private-evidence marker 'TRANSACTION_AMOUNT=' in: public-report.md",
    ]


def test_content_violations_reject_private_path_label_variants(tmp_path, monkeypatch):
    sample = tmp_path / "handoff.md"
    sample.write_text(
        "PRIVATE_PATH: /redacted\nORIGINAL_GNUCASH_PATH=/redacted\nONLY_COPY_GNUCASH_PATH=/redacted\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked raw private-evidence marker 'PRIVATE_PATH:' in: handoff.md",
        "tracked raw private-evidence marker 'ORIGINAL_GNUCASH_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'ONLY_COPY_GNUCASH_PATH=' in: handoff.md",
    ]


def test_content_violations_reject_unsafe_affirmative_wording(tmp_path, monkeypatch):
    sample = tmp_path / "release.md"
    sample.write_text(
        "Public write beta is ready.\n"
        "Broad GnuCash compatibility is supported.\n"
        "Only-copy books are safe for writes.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked unsafe affirmative wording in release.md:1: Public write beta is ready.",
        "tracked unsafe affirmative wording in release.md:2: Broad GnuCash compatibility is supported.",
        "tracked unsafe affirmative wording in release.md:3: Only-copy books are safe for writes.",
    ]


def test_content_violations_allow_negative_safety_wording(tmp_path, monkeypatch):
    sample = tmp_path / "limits.md"
    sample.write_text(
        "No public write beta is ready.\n"
        "Do not claim broad GnuCash compatibility is supported.\n"
        "Only-copy books are not safe for writes.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == []
