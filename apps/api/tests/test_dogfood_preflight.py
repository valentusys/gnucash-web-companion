"""Regression coverage for safe copied-book dogfood preflight helpers."""

from pathlib import Path

from app.dogfood_preflight import (
    DogfoodPreflightResult,
    check_copied_book_candidate,
    check_write_alpha_dogfood_plan,
)


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
    repo_root.mkdir()
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
    assert "copy-for-write-alpha.gnucash.sqlite" in result.safe_summary()


def test_write_alpha_plan_blocks_source_inside_repo(tmp_path):
    repo_root = tmp_path / "repo"
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
    repo_root.mkdir()
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


def test_write_alpha_plan_ready_summary_is_redacted_and_metadata_only(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
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
    assert str(candidate) not in summary
    assert "private-ledgers" not in summary
    assert "disposable-copy.gnucash.sqlite" in summary
    assert "size_bytes=" in summary
