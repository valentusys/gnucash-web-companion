"""Regression coverage for safe copied-book dogfood preflight helpers."""

import subprocess
from pathlib import Path

from app.dogfood_preflight import (
    DogfoodPreflightResult,
    check_copied_book_candidate,
    check_write_alpha_dogfood_plan,
)


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


def test_missing_candidate_is_blocked_without_private_path_leak(tmp_path):
    private_path = tmp_path / "private-ledgers" / "main.gnucash.sqlite"

    result = check_copied_book_candidate(str(private_path), repo_root=tmp_path)

    assert result == DogfoodPreflightResult(
        status="blocked",
        category="release blocker",
        safe_label="main.gnucash.sqlite",
        reason="candidate book path does not exist",
    )
    assert str(private_path) not in result.safe_summary()
    assert "private-ledgers" not in result.safe_summary()
    assert "main.gnucash.sqlite" in result.safe_summary()


def test_candidate_inside_repo_is_blocked_to_prevent_private_book_commit(tmp_path):
    candidate = tmp_path / "data" / "books" / "real-personal.gnucash.sqlite"
    candidate.parent.mkdir(parents=True)
    candidate.write_bytes(b"SQLite format 3\x00")

    result = check_copied_book_candidate(candidate, repo_root=tmp_path)

    assert result.status == "blocked"
    assert result.category == "release blocker"
    assert result.reason == "candidate book is inside the git working tree"
    assert str(candidate) not in result.safe_summary()
    assert "data/books" not in result.safe_summary()


def test_existing_candidate_outside_repo_is_ready_without_private_path_leak(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    candidate = tmp_path / "copied-real-book.gnucash.sqlite"
    candidate.write_bytes(b"SQLite format 3\x00")

    result = check_copied_book_candidate(candidate, repo_root=repo_root)

    assert result.status == "ready"
    assert result.category == "not reproducible"
    assert result.reason == "candidate book exists outside the git working tree"
    assert str(candidate) not in result.safe_summary()
    assert "copied-real-book.gnucash.sqlite" in result.safe_summary()


def test_write_alpha_plan_requires_disposable_acknowledgement_without_path_leak(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    private_dir = tmp_path / "private-source"
    private_dir.mkdir()
    candidate = private_dir / "copy-for-write-alpha.gnucash.sqlite"
    candidate.write_bytes(b"SQLite format 3\x00")

    result = check_write_alpha_dogfood_plan(
        candidate,
        repo_root=repo_root,
        disposable_copy_acknowledged=False,
    )

    assert result.status == "blocked"
    assert result.reason == "disposable copied-book acknowledgement is required"
    assert str(candidate) not in result.safe_summary()
    assert "private-source" not in result.safe_summary()
    assert "copy-for-write-alpha.gnucash.sqlite" not in result.safe_summary()
    assert "<redacted.gnucash.sqlite>" in result.safe_summary()


def test_write_alpha_plan_blocks_source_inside_repo(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    candidate = repo_root / "data" / "books" / "only-copy.gnucash.sqlite"
    candidate.parent.mkdir(parents=True)
    candidate.write_bytes(b"SQLite format 3\x00")

    result = check_write_alpha_dogfood_plan(
        candidate,
        repo_root=repo_root,
        disposable_copy_acknowledged=True,
    )

    assert result.status == "blocked"
    assert result.reason == "source copied/disposable book must stay outside the git working tree"
    assert result.source_class == "inside repo"
    assert str(candidate) not in result.safe_summary()
    assert "data/books" not in result.safe_summary()


def test_write_alpha_plan_blocks_unignored_runtime_or_backup_targets(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    candidate = tmp_path / "copied.gnucash.sqlite"
    candidate.write_bytes(b"SQLite format 3\x00")

    unsafe_runtime = check_write_alpha_dogfood_plan(
        candidate,
        repo_root=repo_root,
        disposable_copy_acknowledged=True,
        runtime_book_path="docs/copied.gnucash.sqlite",
    )
    unsafe_backup = check_write_alpha_dogfood_plan(
        candidate,
        repo_root=repo_root,
        disposable_copy_acknowledged=True,
        backup_dir_path="docs/backups",
    )

    assert unsafe_runtime.status == "blocked"
    assert unsafe_runtime.reason == "runtime copy target must be under ignored data/books/"
    assert unsafe_runtime.runtime_class == "unsafe"
    assert unsafe_backup.status == "blocked"
    assert unsafe_backup.reason == "backup directory must be under ignored data/backups/"
    assert unsafe_backup.backup_class == "unsafe"


def test_write_alpha_plan_fails_closed_for_non_ignored_artifacts(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root, gitignore="data/app/*\n")
    candidate = tmp_path / "copied.gnucash.sqlite"
    candidate.write_bytes(b"SQLite format 3\x00")

    runtime_result = check_write_alpha_dogfood_plan(
        candidate,
        repo_root=repo_root,
        disposable_copy_acknowledged=True,
    )
    backup_result = check_write_alpha_dogfood_plan(
        candidate,
        repo_root=repo_root,
        disposable_copy_acknowledged=True,
        runtime_book_path="data/books/write-alpha-dogfood.gnucash.sqlite",
        backup_dir_path="data/backups/write-alpha-dogfood",
    )

    assert runtime_result.status == "blocked"
    assert runtime_result.reason == "runtime copy target must be ignored by git"
    assert backup_result.status == "blocked"
    assert backup_result.reason == "runtime copy target must be ignored by git"


def test_write_alpha_plan_blocks_env_app_db_and_backup_sources(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    env_file = scratch / ".env"
    app_db = scratch / "app.db"
    backup_file = scratch / "preflight.backup"
    for candidate in (env_file, app_db, backup_file):
        candidate.write_bytes(b"not a disposable book")

    env_result = check_write_alpha_dogfood_plan(env_file, repo_root=repo_root, disposable_copy_acknowledged=True)
    app_db_result = check_write_alpha_dogfood_plan(app_db, repo_root=repo_root, disposable_copy_acknowledged=True)
    backup_result = check_write_alpha_dogfood_plan(backup_file, repo_root=repo_root, disposable_copy_acknowledged=True)

    assert env_result.status == "blocked"
    assert env_result.reason == "source must not be an environment file"
    assert app_db_result.status == "blocked"
    assert app_db_result.reason == "source must not be an app metadata DB"
    assert backup_result.status == "blocked"
    assert backup_result.reason == "source must not be a backup artifact or backup directory"


def test_write_alpha_plan_ready_summary_is_redacted_and_metadata_only(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    private_dir = tmp_path / "private-ledgers"
    private_dir.mkdir()
    candidate = private_dir / "disposable-copy.gnucash.sqlite"
    candidate.write_bytes(b"SQLite format 3\x00")

    result = check_write_alpha_dogfood_plan(
        candidate,
        repo_root=repo_root,
        disposable_copy_acknowledged=True,
    )

    summary = result.safe_summary()
    assert result.status == "ready"
    assert result.source_class == "external copied/disposable"
    assert result.runtime_class == "ignored data/books"
    assert result.backup_class == "ignored data/backups"
    assert result.size_bytes == len(b"SQLite format 3\x00")
    assert result.checksum_sha256_12 is not None
    assert str(candidate) not in summary
    assert "private-ledgers" not in summary
    assert "disposable-copy.gnucash.sqlite" not in summary
    assert "<redacted.gnucash.sqlite>" in summary
    assert "size_bytes=" in summary
    assert "sha256_12=" in summary
    assert "dry_run=true" in summary


def test_failed_write_alpha_checks_do_not_create_runtime_or_backup_artifacts(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo_with_ignores(repo_root)
    missing_candidate = tmp_path / "missing-copy.gnucash.sqlite"

    result = check_write_alpha_dogfood_plan(
        missing_candidate,
        repo_root=repo_root,
        disposable_copy_acknowledged=True,
    )

    assert result.status == "blocked"
    assert not (repo_root / "data" / "books" / "write-alpha-dogfood.gnucash.sqlite").exists()
    assert not (repo_root / "data" / "backups" / "write-alpha-dogfood").exists()
