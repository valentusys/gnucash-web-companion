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
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in source.stem)
    try:
        backup_path = _copy_backup_without_overwrite(source, backup_dir, safe_stem, timestamp, source.suffix)
    except Exception as exc:
        raise BackupError(str(source), str(exc)) from exc

    return str(backup_path)


def _unique_backup_path(backup_dir: Path, safe_stem: str, timestamp: str, suffix: str) -> Path:
    """Return a backup path that does not already exist.

    Rapid route-family smokes can create multiple backups for the same source
    inside one second. Use microseconds for normal uniqueness and a deterministic
    numeric suffix if the clock is fixed or the candidate already exists, so a
    successful write never overwrites earlier backup evidence.
    """
    candidate = backup_dir / f"{safe_stem}_{timestamp}{suffix}"
    if not candidate.exists():
        return candidate

    index = 1
    while True:
        candidate = backup_dir / f"{safe_stem}_{timestamp}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _copy_backup_without_overwrite(source: Path, backup_dir: Path, safe_stem: str, timestamp: str, suffix: str) -> Path:
    """Copy source to a unique backup path without replacing existing artifacts."""
    while True:
        backup_path = _unique_backup_path(backup_dir, safe_stem, timestamp, suffix)
        try:
            with source.open("rb") as src, backup_path.open("xb") as dst:
                shutil.copyfileobj(src, dst)
            shutil.copystat(source, backup_path, follow_symlinks=True)
            return backup_path
        except FileExistsError:
            continue
        except Exception:
            try:
                if backup_path.exists():
                    backup_path.unlink()
            except OSError:
                pass
            raise
