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
