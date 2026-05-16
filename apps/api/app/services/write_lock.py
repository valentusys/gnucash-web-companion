"""Per-book write lock service.

Provides in-process locking to prevent concurrent writes to the same GnuCash book.

Limitation: This is an in-process lock. In a multi-process deployment (e.g. multiple
gunicorn workers), this will not prevent concurrent writes across processes. For
production multi-process deployments, a file-based or distributed lock should be used.
"""

from __future__ import annotations

import threading
from collections.abc import Generator
from contextlib import contextmanager


class WriteLockError(Exception):
    """Raised when a write lock cannot be acquired."""

    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(f"Could not acquire write lock for book {book_id}")


class WriteLockService:
    """Thread-safe per-book write lock.

    Uses a dictionary of locks keyed by book identifier. Each book can have
    at most one writer at a time within this process.
    """

    def __init__(self) -> None:
        self._locks: dict[str, threading.Lock] = {}
        self._meta_lock = threading.Lock()

    def _get_lock(self, book_id: str) -> threading.Lock:
        """Get or create the lock for a given book_id."""
        with self._meta_lock:
            if book_id not in self._locks:
                self._locks[book_id] = threading.Lock()
            return self._locks[book_id]

    def acquire(self, book_id: str, blocking: bool = False) -> bool:
        """Attempt to acquire the write lock for a book.

        Args:
            book_id: Unique identifier for the book.
            blocking: If False (default), return immediately even if lock is held.

        Returns:
            True if the lock was acquired, False otherwise.
        """
        lock = self._get_lock(book_id)
        return lock.acquire(blocking=blocking)

    def release(self, book_id: str) -> None:
        """Release the write lock for a book.

        Safe to call even if the lock was not acquired (no-op).
        """
        with self._meta_lock:
            lock = self._locks.get(book_id)
        if lock is None:
            return
        try:
            lock.release()
        except RuntimeError:
            # Lock was not held
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
