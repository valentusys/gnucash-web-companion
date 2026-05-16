"""Backup service for GnuCash books.

Creates timestamped backups before any write operation.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.services.gnucash_book import GnuCashBookService


class BackupError(Exception):
    """Raised when a backup operation fails."""

    def __init__(self, path: str, detail: str | None = None):
        self.path = path
        self.detail = detail
        msg = f"Backup failed for: {path}"
        if detail:
            msg += f" ({detail})"
        super().__init__(msg)


def _backup_dir(book_path: Path) -> Path:
    """Return the backup directory for a given book path.

    Backups live under <book_parent>/../backups/<book_stem>/ to keep them
    alongside the book but not inside the book directory itself.
    """
    book_dir = book_path.parent
    book_stem = book_path.stem
    backup_root = book_dir.parent / "backups" / book_stem
    backup_root.mkdir(parents=True, exist_ok=True)
    return backup_root


def create_book_backup(book_config) -> str:
    """Create a timestamped backup of a GnuCash book.

    Args:
        book_config: Book model instance or dict with uri_or_path.

    Returns:
        Absolute path to the backup file as a string.

    Raises:
        BackupError: If the book file does not exist or the copy fails.
    """
    uri_or_path = GnuCashBookService._get_uri_or_path(book_config)
    if not uri_or_path or not str(uri_or_path).strip():
        raise BackupError("", "No book path configured")

    source = Path(uri_or_path)
    if not source.exists():
        raise BackupError(str(source), "Book file does not exist")

    backup_dir = _backup_dir(source)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in source.stem)
    backup_name = f"{safe_stem}_{timestamp}{source.suffix}"
    backup_path = backup_dir / backup_name

    try:
        shutil.copy2(str(source), str(backup_path))
    except Exception as exc:
        raise BackupError(str(source), str(exc)) from exc

    return str(backup_path)
