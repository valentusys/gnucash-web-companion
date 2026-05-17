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
from pathlib import Path

DEFAULT_LOCK_DIR = Path("/data/locks")


class WriteLockError(Exception):
    """Raised when a write lock cannot be acquired."""

    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(f"Could not acquire write lock for book {book_id}")


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

    @contextmanager
    def lock(self, book_id: str) -> Generator[None, None, None]:
        """Context manager that acquires and releases the lock.

        Raises:
            WriteLockError: If the lock cannot be acquired.
        """
        if not self.acquire(book_id):
            raise WriteLockError(book_id)
        try:
            yield
        finally:
            self.release(book_id)


# Global singleton instance used by the write endpoints.
write_lock_service = WriteLockService()
