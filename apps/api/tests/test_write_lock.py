"""Tests for the file-based WriteLockService."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.services.write_lock import WriteLockError, WriteLockService


@pytest.fixture
def tmp_lock_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for lock files."""
    return tmp_path / "locks"


@pytest.fixture
def service(tmp_lock_dir: Path) -> WriteLockService:
    """Return a WriteLockService using a temporary lock directory."""
    return WriteLockService(lock_dir=tmp_lock_dir)


class TestWriteLockService:
    def test_acquire_returns_true_when_lock_is_free(self, service: WriteLockService) -> None:
        assert service.acquire("book-1") is True

    def test_acquire_returns_false_when_lock_is_held_non_blocking(
        self, service: WriteLockService
    ) -> None:
        assert service.acquire("book-1") is True
        assert service.acquire("book-1", blocking=False) is False

    def test_release_allows_reacquire(self, service: WriteLockService) -> None:
        assert service.acquire("book-1") is True
        service.release("book-1")
        assert service.acquire("book-1") is True

    def test_context_manager_acquires_and_releases(self, service: WriteLockService) -> None:
        with service.lock("book-1"):
            # Lock is held — non-blocking re-acquire must fail
            assert service.acquire("book-1", blocking=False) is False
        # After context exit lock is released
        assert service.acquire("book-1") is True

    def test_context_manager_releases_on_exception(self, service: WriteLockService) -> None:
        with pytest.raises(RuntimeError, match="boom"):
            with service.lock("book-1"):
                raise RuntimeError("boom")
        # Lock was released despite the exception
        assert service.acquire("book-1") is True

    def test_different_books_independent(self, service: WriteLockService) -> None:
        assert service.acquire("book-a") is True
        assert service.acquire("book-b") is True
        # Both locks are held simultaneously
        assert service.acquire("book-a", blocking=False) is False
        assert service.acquire("book-b", blocking=False) is False

    def test_lock_uses_expected_lock_file(
        self, service: WriteLockService, tmp_lock_dir: Path
    ) -> None:
        lock_file = tmp_lock_dir / "my-book.lock"
        assert not lock_file.exists()
        service.acquire("my-book")
        assert lock_file.exists()
        service.release("my-book")
        # File may remain on disk after release (that's fine)

    def test_release_is_noop_when_not_held(self, service: WriteLockService) -> None:
        # Must not raise
        service.release("never-locked")

    def test_blocking_acquire_succeeds_when_lock_is_free(
        self, service: WriteLockService
    ) -> None:
        assert service.acquire("book-1", blocking=True) is True

    def test_lock_file_parent_directory_created(
        self, tmp_path: Path
    ) -> None:
        """Lock service creates the lock directory if it doesn't exist."""
        nested = tmp_path / "deep" / "nested" / "locks"
        svc = WriteLockService(lock_dir=nested)
        assert svc.acquire("book-1") is True
        assert nested.is_dir()
