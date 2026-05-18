"""Regression coverage for safe copied-book dogfood preflight helpers."""

from pathlib import Path

from app.dogfood_preflight import DogfoodPreflightResult, check_copied_book_candidate


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
