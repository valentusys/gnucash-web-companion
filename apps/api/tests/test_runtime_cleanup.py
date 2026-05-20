"""Tests for stopped-runtime ignored data cleanup helper."""

from __future__ import annotations

import fcntl
import os
from pathlib import Path

import pytest

from app.runtime_cleanup import (
    STOPPED_RUNTIME_ACK,
    RuntimeCleanupError,
    cleanup_runtime,
    format_summary,
)


def _repo_with_data(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    data = repo / "data"
    for name in ("books", "app", "backups", "locks"):
        (data / name).mkdir(parents=True, exist_ok=True)
    return repo, data


def test_cleanup_requires_stopped_runtime_ack(tmp_path: Path) -> None:
    repo, data = _repo_with_data(tmp_path)
    (data / "locks" / "book.lock").write_text("", encoding="utf-8")

    with pytest.raises(RuntimeCleanupError, match="acknowledgement required"):
        cleanup_runtime(repo, data, ack=None)

    assert (data / "locks" / "book.lock").exists()


def test_cleanup_fails_closed_for_non_repo_data_root(tmp_path: Path) -> None:
    repo, _data = _repo_with_data(tmp_path)
    outside = tmp_path / "outside-data"
    outside.mkdir()

    with pytest.raises(RuntimeCleanupError, match="repository ignored data directory"):
        cleanup_runtime(repo, outside, ack=STOPPED_RUNTIME_ACK)


def test_dry_run_reports_only_classes_counts_and_statuses(tmp_path: Path) -> None:
    repo, data = _repo_with_data(tmp_path)
    private_name = "Private Accounts 123.45.gnucash.sqlite"
    (data / "books" / private_name).write_text("synthetic", encoding="utf-8")
    (data / "app" / "app.db").write_text("synthetic", encoding="utf-8")
    (data / "backups" / "backup-like-private-name").mkdir()
    (data / "locks" / "book-secret.lock").write_text("", encoding="utf-8")

    summary = cleanup_runtime(repo, data, ack=STOPPED_RUNTIME_ACK, execute=False)
    output = format_summary(summary)

    assert "books: count=1" in output
    assert "app: count=1" in output
    assert "backups: count=1" in output
    assert "locks: count=1" in output
    assert "cleanup_stale_lock" in output
    assert private_name not in output
    assert "book-secret" not in output
    assert str(data) not in output
    assert "123.45" not in output
    assert (data / "books" / private_name).exists()


def test_execute_removes_stale_lock_and_runtime_artifacts(tmp_path: Path) -> None:
    repo, data = _repo_with_data(tmp_path)
    (data / "books" / "synthetic.gnucash.sqlite").write_text("synthetic", encoding="utf-8")
    (data / "app" / "app.db").write_text("synthetic", encoding="utf-8")
    (data / "backups" / "book-id").mkdir()
    (data / "backups" / "book-id" / "backup.sqlite").write_text("synthetic", encoding="utf-8")
    stale_lock = data / "locks" / "book.lock"
    stale_lock.write_text("", encoding="utf-8")

    summary = cleanup_runtime(repo, data, ack=STOPPED_RUNTIME_ACK, execute=True)

    assert summary.statuses["removed"] == 4
    assert not (data / "books" / "synthetic.gnucash.sqlite").exists()
    assert not (data / "app" / "app.db").exists()
    assert not (data / "backups" / "book-id").exists()
    assert not stale_lock.exists()


def test_execute_preserves_active_lock(tmp_path: Path) -> None:
    repo, data = _repo_with_data(tmp_path)
    active_lock = data / "locks" / "book.lock"
    fd = os.open(active_lock, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

        summary = cleanup_runtime(repo, data, ack=STOPPED_RUNTIME_ACK, execute=True, classes=("locks",))

        assert summary.statuses["skip_active_lock"] == 1
        assert summary.statuses["lock_active"] == 1
        assert summary.statuses.get("removed", 0) == 0
        assert active_lock.exists()
        assert "active lock files were preserved" in summary.messages
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def test_execute_removes_unreadable_lock_after_ack_without_path_leak(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, data = _repo_with_data(tmp_path)
    lock_path = data / "locks" / "private-book.lock"
    lock_path.write_text("", encoding="utf-8")
    original_open = os.open

    def permission_denied(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        if str(path).endswith("private-book.lock"):
            raise PermissionError("permission denied")
        return original_open(path, flags, mode)

    monkeypatch.setattr(os, "open", permission_denied)

    summary = cleanup_runtime(repo, data, ack=STOPPED_RUNTIME_ACK, execute=True, classes=("locks",))
    output = format_summary(summary)

    assert summary.statuses["cleanup_unreadable_lock_with_stopped_ack"] == 1
    assert summary.statuses["lock_unreadable"] == 1
    assert summary.statuses["removed"] == 1
    assert not lock_path.exists()
    assert "private-book" not in output
    assert str(data) not in output


def test_unsupported_lock_child_is_not_removed(tmp_path: Path) -> None:
    repo, data = _repo_with_data(tmp_path)
    unexpected = data / "locks" / "unexpected.txt"
    unexpected.write_text("synthetic", encoding="utf-8")

    summary = cleanup_runtime(repo, data, ack=STOPPED_RUNTIME_ACK, execute=True, classes=("locks",))

    assert summary.statuses["skip_unsupported"] == 1
    assert summary.statuses.get("removed", 0) == 0
    assert unexpected.exists()
