"""Per-book write lock service.

Provides file-based locking to prevent concurrent writes to the same GnuCash
book across multiple workers/processes. Uses ``fcntl.flock()`` on per-book
lock files under ``/data/locks/``.

Replaces the previous in-process ``threading.Lock`` implementation to support
multi-worker deployments (e.g. multiple gunicorn workers).
"""

from __future__ import annotations

import fcntl
import os
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

DEFAULT_LOCK_DIR = Path("/data/locks")


class WriteLockError(Exception):
    """Raised when a write lock cannot be acquired."""

    def __init__(self, book_id: str, inspection: WriteLockProbeResult | None = None):
        self.book_id = book_id
        self.inspection = inspection
        super().__init__(f"Could not acquire write lock for book {book_id}")


@dataclass(frozen=True)
class WriteLockProbeResult:
    """Path-safe lock inspection result for operator evidence.

    The result intentionally does not expose the lock path or book path. It is
    for disposable write-alpha dogfood/recovery evidence and operator guidance,
    not for automatic production lock cleanup.
    """

    status: str
    is_active: bool
    operator_message: str


LOCK_NOT_PRESENT_MESSAGE = "No write lock file is present for this book."
LOCK_ACTIVE_MESSAGE = "A write lock is currently active. Wait for the active write to finish before retrying."
LOCK_STALE_MESSAGE = (
    "A write lock file is present but not actively held. With the app stopped, an operator may remove the "
    "book-specific stale lock file from ignored runtime storage before retrying on a disposable test copy."
)
LOCK_UNREADABLE_MESSAGE = (
    "A write lock file is present but cannot be inspected by this process. Inspect it from the API container "
    "or fix runtime ownership, then remove only the book-specific stale lock after confirming the app is stopped."
)


class WriteLockService:
    """File-based per-book write lock.

    Uses ``fcntl.flock()`` on a per-book lock file. Each book can have at most
    one writer at a time across all workers/processes sharing the same lock
    directory.

    Args:
        lock_dir: Directory for lock files. Defaults to ``/data/locks``.
    """

    def __init__(self, lock_dir: Path = DEFAULT_LOCK_DIR) -> None:
        self._lock_dir = lock_dir
        self._fds: dict[str, int] = {}

    def __del__(self) -> None:
        """Release all open lock fds on garbage collection (crash safety)."""
        fds = dict(self._fds)
        for book_id, fd in fds.items():
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                os.close(fd)
            except OSError:
                pass
        self._fds.clear()

    def _lock_path(self, book_id: str) -> Path:
        """Return the lock file path for a given book_id.

        The book_id is sanitized to replace path separators and other
        characters that are unsafe in filenames with underscores, so that
        even absolute paths or URIs produce a flat filename under the
        lock directory.
        """
        safe = book_id.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self._lock_dir / f"{safe}.lock"

    def acquire(self, book_id: str, blocking: bool = False) -> bool:
        """Attempt to acquire the write lock for a book.

        Args:
            book_id: Unique identifier for the book.
            blocking: If False (default), return immediately even if lock is held.

        Returns:
            True if the lock was acquired, False otherwise.
        """
        if book_id in self._fds:
            return False

        lock_path = self._lock_path(book_id)
        try:
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
            try:
                flags = fcntl.LOCK_EX
                if not blocking:
                    flags |= fcntl.LOCK_NB
                fcntl.flock(fd, flags)
                # If a previous fd exists for this book, close it (shouldn't
                # happen in normal usage, but prevents fd leaks).
                old_fd = self._fds.get(book_id)
                self._fds[book_id] = fd
                if old_fd is not None:
                    try:
                        os.close(old_fd)
                    except OSError:
                        pass
                return True
            except (BlockingIOError, OSError):
                os.close(fd)
                return False
        except OSError:
            return False

    def release(self, book_id: str) -> None:
        """Release the write lock for a book.

        Safe to call even if the lock was not acquired (no-op).
        """
        fd = self._fds.pop(book_id, None)
        if fd is None:
            return
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            try:
                os.close(fd)
            except OSError:
                pass

    def inspect(self, book_id: str) -> WriteLockProbeResult:
        """Inspect whether a book lock is active, stale, unreadable, or absent.

        This helper never deletes lock files and never returns filesystem paths.
        If the current service instance owns the lock, it reports active without
        attempting to re-lock the same file. Otherwise it opens the lock file and
        tries a non-blocking exclusive flock; success means the remaining file is
        stale/released, while ``BlockingIOError`` means another process holds it.
        """
        if book_id in self._fds:
            return WriteLockProbeResult(
                status="active",
                is_active=True,
                operator_message=LOCK_ACTIVE_MESSAGE,
            )

        lock_path = self._lock_path(book_id)
        if not lock_path.exists():
            return WriteLockProbeResult(
                status="not_present",
                is_active=False,
                operator_message=LOCK_NOT_PRESENT_MESSAGE,
            )

        try:
            fd = os.open(str(lock_path), os.O_RDWR)
        except (PermissionError, OSError):
            return WriteLockProbeResult(
                status="unreadable",
                is_active=False,
                operator_message=LOCK_UNREADABLE_MESSAGE,
            )

        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return WriteLockProbeResult(
                    status="active",
                    is_active=True,
                    operator_message=LOCK_ACTIVE_MESSAGE,
                )
            finally:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except OSError:
                    pass
        finally:
            os.close(fd)

        return WriteLockProbeResult(
            status="stale_released",
            is_active=False,
            operator_message=LOCK_STALE_MESSAGE,
        )

    @contextmanager
    def lock(self, book_id: str) -> Generator[None, None, None]:
        """Context manager that acquires and releases the lock.

        Raises:
            WriteLockError: If the lock cannot be acquired.
                The exception's ``inspection`` attribute carries a
                ``WriteLockProbeResult`` describing whether the lock is
                active or stale, for operator diagnostics.
        """
        acquired = self.acquire(book_id)
        if not acquired:
            probe = self.inspect(book_id)
            raise WriteLockError(book_id, inspection=probe)
        try:
            yield
        finally:
            self.release(book_id)


# Global singleton instance used by the write endpoints.
write_lock_service = WriteLockService()
