"""Tests for the file-based WriteLockService."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.services.write_lock import (
    LOCK_ACTIVE_MESSAGE,
    LOCK_STALE_MESSAGE,
    LOCK_UNREADABLE_MESSAGE,
    WriteLockError,
    WriteLockService,
)


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

    def test_inspect_reports_active_lock_without_path_leak(self, service: WriteLockService) -> None:
        assert service.acquire("book-1") is True

        result = service.inspect("book-1")

        assert result.status == "active"
        assert result.is_active is True
        assert result.operator_message == LOCK_ACTIVE_MESSAGE
        assert "book-1" not in result.operator_message
        assert "/" not in result.operator_message

    def test_inspect_reports_released_lock_file_as_stale_guidance(
        self, service: WriteLockService, tmp_lock_dir: Path
    ) -> None:
        assert service.acquire("book-1") is True
        service.release("book-1")
        assert (tmp_lock_dir / "book-1.lock").exists()

        result = service.inspect("book-1")

        assert result.status == "stale_released"
        assert result.is_active is False
        assert result.operator_message == LOCK_STALE_MESSAGE
        assert "app stopped" in result.operator_message
        assert "disposable test copy" in result.operator_message
        assert "book-1" not in result.operator_message
        assert "/" not in result.operator_message

    def test_inspect_reports_missing_lock_without_cleanup_action(self, service: WriteLockService) -> None:
        result = service.inspect("book-1")

        assert result.status == "not_present"
        assert result.is_active is False
        assert "No write lock file" in result.operator_message
        assert "remove" not in result.operator_message.lower()
        assert "/" not in result.operator_message

    def test_inspect_reports_unreadable_lock_with_safe_operator_guidance(
        self, service: WriteLockService, tmp_lock_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert service.acquire("book-1") is True
        service.release("book-1")
        original_open = os.open

        def permission_denied(path: str, flags: int, mode: int = 0o777) -> int:
            if str(path).endswith("book-1.lock"):
                raise PermissionError("permission denied")
            return original_open(path, flags, mode)

        monkeypatch.setattr(os, "open", permission_denied)

        result = service.inspect("book-1")

        assert result.status == "unreadable"
        assert result.is_active is False
        assert result.operator_message == LOCK_UNREADABLE_MESSAGE
        assert "API container" in result.operator_message
        assert "book-specific stale lock" in result.operator_message
        assert str(tmp_lock_dir) not in result.operator_message
        assert "book-1" not in result.operator_message


class TestWriteLockServiceCrossInstance:
    """Cross-instance lock contention and stale recovery lifecycle tests."""

    def test_second_instance_non_blocking_acquire_fails_when_first_holds(
        self, tmp_lock_dir: Path
    ) -> None:
        """Two service instances sharing the same lock dir must serialize."""
        svc_a = WriteLockService(lock_dir=tmp_lock_dir)
        svc_b = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc_a.acquire("book-x") is True
        assert svc_b.acquire("book-x", blocking=False) is False

    def test_second_instance_inspect_reports_active_while_first_holds(
        self, tmp_lock_dir: Path
    ) -> None:
        """While instance A holds the lock, instance B must see it as active."""
        svc_a = WriteLockService(lock_dir=tmp_lock_dir)
        svc_b = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc_a.acquire("book-x") is True

        result = svc_b.inspect("book-x")
        assert result.status == "active"
        assert result.is_active is True

    def test_second_instance_acquires_after_first_releases(
        self, tmp_lock_dir: Path
    ) -> None:
        """After instance A releases, instance B must successfully acquire."""
        svc_a = WriteLockService(lock_dir=tmp_lock_dir)
        svc_b = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc_a.acquire("book-x") is True
        svc_a.release("book-x")

        result = svc_b.inspect("book-x")
        assert result.status == "stale_released"
        assert result.is_active is False

        assert svc_b.acquire("book-x") is True

    def test_second_instance_sees_stale_after_first_releases(
        self, tmp_lock_dir: Path
    ) -> None:
        """Stale lock file remains on disk but is detected as not active."""
        svc_a = WriteLockService(lock_dir=tmp_lock_dir)
        svc_b = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc_a.acquire("book-x") is True
        svc_a.release("book-x")

        assert (tmp_lock_dir / "book-x.lock").exists()
        result = svc_b.inspect("book-x")
        assert result.status == "stale_released"
        assert result.is_active is False

    def test_first_instance_non_blocking_reacquire_returns_false(
        self, tmp_lock_dir: Path
    ) -> None:
        """Re-acquiring a lock already held in the same instance must fail closed."""
        svc = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc.acquire("book-x") is True
        assert svc.acquire("book-x", blocking=False) is False

    def test_os_level_fd_cleanup_on_service_gc(
        self, tmp_lock_dir: Path
    ) -> None:
        """When a service instance is garbage collected without release(), fds are closed."""
        import gc
        svc = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc.acquire("book-x") is True
        # Simulate crash: service drops out of scope without release()
        del svc
        gc.collect()
        # Now a fresh instance must be able to acquire
        svc_new = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc_new.acquire("book-x") is True


class TestWriteLockInspection:
    """Tests for lock inspection details exposed on acquisition failures."""

    def test_reacquire_returns_false_without_inspection(
        self, tmp_lock_dir: Path
    ) -> None:
        """Same-instance non-blocking re-acquire returns False without inspection."""
        svc = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc.acquire("book-x") is True
        assert svc.acquire("book-x", blocking=False) is False

    def test_context_manager_succeeds_after_gc_releases_stale_lock(
        self, tmp_lock_dir: Path
    ) -> None:
        """A stale lock file can be inspected, then lock() reacquires safely.

        Setup: instance A acquires, then is GC'd without explicit release,
        leaving a stale lock file on disk. Instance B sees stale_released
        inspection info and can safely acquire the now-unheld OS flock.
        """
        import gc
        svc_a = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc_a.acquire("book-x") is True
        # Simulate crash: svc_a is GC'd; __del__ releases the flock
        del svc_a
        gc.collect()

        # Lock file exists on disk, but no one holds it
        assert (tmp_lock_dir / "book-x.lock").exists()

        svc_b = WriteLockService(lock_dir=tmp_lock_dir)
        # svc_b.lock(...) will succeed because __del__ released the flock,
        # but the lock file is stale. Let's verify that first with inspect:
        result = svc_b.inspect("book-x")
        assert result.status == "stale_released"
        # Now test that lock() succeeds (no WriteLockError after cleanup):
        with svc_b.lock("book-x"):
            pass  # succeeds because __del__ cleaned up
        svc_b.release("book-x")

    def test_context_manager_lock_error_carry_active_inspection(
        self, tmp_lock_dir: Path
    ) -> None:
        """When context manager fails while another holds lock, error carries active inspection."""
        svc_a = WriteLockService(lock_dir=tmp_lock_dir)
        svc_b = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc_a.acquire("book-x") is True

        with pytest.raises(WriteLockError) as exc_info:
            with svc_b.lock("book-x"):
                pass  # pragma: no cover

        err = exc_info.value
        assert err.inspection is not None
        assert err.inspection.status == "active"
        assert err.inspection.is_active is True

    def test_context_manager_lock_error_inspection_has_no_path_leak(
        self, tmp_lock_dir: Path
    ) -> None:
        """WriteLockError.inspection.operator_message must not leak paths."""
        svc_a = WriteLockService(lock_dir=tmp_lock_dir)
        svc_b = WriteLockService(lock_dir=tmp_lock_dir)
        assert svc_a.acquire("book-x") is True

        with pytest.raises(WriteLockError) as exc_info:
            with svc_b.lock("book-x"):
                pass  # pragma: no cover

        err = exc_info.value
        assert err.inspection is not None
        msg = err.inspection.operator_message
        assert "book-x" not in msg
        assert "/" not in msg
        assert str(tmp_lock_dir) not in msg
