"""Regression tests for the local-only write-alpha target preflight CLI."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_alpha_preflight.py"

spec = importlib.util.spec_from_file_location("write_alpha_preflight", SCRIPT_PATH)
assert spec is not None
preflight = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["write_alpha_preflight"] = preflight
spec.loader.exec_module(preflight)


def _init_repo_with_ignores(repo_root: Path, gitignore: str | None = None) -> None:
    repo_root.mkdir(parents=True, exist_ok=True)
    (repo_root / ".gitignore").write_text(
        gitignore
        or (
            "data/books/*.gnucash.sqlite\n"
            "data/books/*.sqlite\n"
            "data/books/*.sqlite3\n"
            "data/books/*.db\n"
            "data/app/*\n"
            "data/backups/*\n"
        )
    )
    subprocess.run(["git", "init"], cwd=repo_root, check=True, stdout=subprocess.DEVNULL)


def test_preflight_requires_explicit_existing_target_without_path_leak(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    private_missing = tmp_path / "private-ledgers" / "only-copy.gnucash.sqlite"
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "test")

    result = preflight.run_preflight(private_missing, repo_root=repo_root)

    summary = result.safe_summary()
    assert result.status == "blocked"
    assert result.reason == "target file does not exist"
    assert result.target_class == "missing"
    assert str(private_missing) not in summary
    assert "private-ledgers" not in summary
    assert "only-copy.gnucash.sqlite" not in summary
    assert "<redacted.gnucash.sqlite>" in summary


def test_preflight_blocks_inside_git_target_even_if_ignored(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    target = repo_root / "data" / "books" / "copy.gnucash.sqlite"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"SQLite format 3\x00")
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "test")

    result = preflight.run_preflight(target, repo_root=repo_root)

    summary = result.safe_summary()
    assert result.status == "blocked"
    assert result.reason == "target must be outside the git working tree"
    assert result.target_class == "inside repo"
    assert str(target) not in summary
    assert "data/books" not in summary
    assert "copy.gnucash.sqlite" not in summary


def test_preflight_blocks_unsafe_environment_without_raw_path(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    target = tmp_path / "copied-test-book.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00")
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "false")
    monkeypatch.setenv("APP_ENV", "production")

    result = preflight.run_preflight(target, repo_root=repo_root)

    summary = result.safe_summary()
    assert result.status == "blocked"
    assert result.reason == "GNUCASH_WRITES_ENABLED must be explicitly true for write-alpha dogfood"
    assert result.writes_env == "unexpected"
    assert result.app_env == "unexpected"
    assert str(target) not in summary
    assert "copied-test-book.gnucash.sqlite" not in summary


def test_preflight_blocks_backup_destination_inside_repo_when_not_ignored(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root, gitignore="data/books/*.gnucash.sqlite\n")
    target = tmp_path / "copied-test-book.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00")
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "test")

    result = preflight.run_preflight(target, repo_root=repo_root, backup_dir="docs/backups")

    assert result.status == "blocked"
    assert result.reason == "backup destination must be outside git or ignored by git"
    assert result.target_class == "external"
    assert result.backup_class == "unsafe"
    assert str(target) not in result.safe_summary()


def test_preflight_ready_output_is_redacted_and_warns_on_original_like_names(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    private_dir = tmp_path / "Documents"
    private_dir.mkdir()
    target = private_dir / "GnuCash-main.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00")
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "test")

    result = preflight.run_preflight(target, repo_root=repo_root)

    summary = result.safe_summary()
    assert result.status == "ready"
    assert result.target_class == "external"
    assert result.backup_class == "ignored"
    assert result.warnings == ("target-name-looks-original-or-production",)
    assert "GNUCASH_WRITES_ENABLED=true" in summary
    assert "APP_ENV=test" in summary
    assert "mutation=none" in summary
    assert "paths=redacted" in summary
    assert str(target) not in summary
    assert "Documents" not in summary
    assert "GnuCash-main.gnucash.sqlite" not in summary
    assert "<redacted.gnucash.sqlite>" in summary


def test_cli_exits_nonzero_for_missing_target_and_redacts_output(tmp_path):
    missing = tmp_path / "private" / "missing.gnucash.sqlite"

    result = subprocess.run(
        ["python3", str(SCRIPT_PATH), str(missing)],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 2
    assert "status=blocked" in result.stdout
    assert str(missing) not in result.stdout
    assert "private" not in result.stdout
    assert result.stderr == ""
