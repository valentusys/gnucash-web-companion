"""Backup service for GnuCash books.

Creates timestamped backups before any write operation.
"""

from __future__ import annotations

import ctypes
import errno
import fcntl
from dataclasses import dataclass
import hashlib
import hmac
import json
import logging
import os
import platform
import secrets
import shutil
import stat
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.services.gnucash_book import GnuCashBookService

logger = logging.getLogger(__name__)
_DATETIME_FROM_ISOFORMAT = datetime.fromisoformat

VERIFIED_BACKUP_MARKER_SUFFIX = ".verified.json"
VERIFIED_BACKUP_RETENTION_DAYS = 30
VERIFIED_BACKUP_MAX_COUNT = 50
VERIFIED_BACKUP_RETENTION_MAX_DIRECTORY_ENTRIES = 4096
VERIFIED_BACKUP_RETENTION_MAX_MARKERS = 1024
VERIFIED_BACKUP_RETENTION_MAX_MARKER_BYTES = 64 * 1024
VERIFIED_BACKUP_RETENTION_MAX_HASHES = 1024
VERIFIED_BACKUP_RETENTION_MAX_HASH_BYTES = 16 * 1024 * 1024 * 1024
VERIFIED_BACKUP_RETENTION_STATE_DIR_NAME = ".verified-backup-retention"
VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME = "state.json"
VERIFIED_BACKUP_RETENTION_STATE_SCHEMA_VERSION = 1
VERIFIED_BACKUP_RETENTION_MAX_STATE_BYTES = 256 * 1024
VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_PAIRS = 64
VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES = VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_PAIRS * 2
VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES = 64 * 1024 * 1024
_RETENTION_STATE_DIR_MODE = 0o700
_RETENTION_STATE_FILE_MODE = 0o600
_HASH_CHUNK_SIZE = 1024 * 1024
_AT_FDCWD = -100
_RENAME_NOREPLACE = 1
_RENAME_EXCHANGE = 2
_RENAMEAT2_SYSCALL_BY_MACHINE = {
    "x86_64": 316,
    "amd64": 316,
    "aarch64": 276,
    "arm64": 276,
}


@dataclass(frozen=True)
class _VerifiedBackupCandidate:
    path: Path
    marker_path: Path
    created_at: datetime
    name: str
    st_dev: int
    st_ino: int
    st_size: int
    sha256: str
    marker_st_dev: int
    marker_st_ino: int
    marker_st_size: int
    marker_sha256: str


@dataclass
class _RetentionInspection:
    entries_seen: int = 0
    markers_seen: int = 0
    hashes_seen: int = 0
    hash_bytes_seen: int = 0
    quarantine_entries_seen: int = 0
    quarantine_bytes_seen: int = 0
    state_records_seen: int = 0
    reclaimed_entries: int = 0
    reclaimed_bytes: int = 0
    reclaimed_pairs: int = 0
    skipped_reason: str | None = None


@dataclass(frozen=True)
class _RetentionStateSnapshot:
    records: list[dict[str, Any]]
    exists: bool
    st_dev: int | None = None
    st_ino: int | None = None
    st_size: int | None = None
    sha256: str | None = None


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
    source_text = str(_book_config_value(book_config, "backup_source_path", uri_or_path))
    basis_text = str(_book_config_value(book_config, "backup_path_basis", uri_or_path))
    allow_pinned_source = bool(_book_config_value(book_config, "backup_source_is_pinned_fd", False))

    source = Path(source_text)
    if not source.exists():
        raise BackupError(str(source), "Book file does not exist")
    if (source.is_symlink() and not allow_pinned_source) or not source.is_file():
        raise BackupError(str(source), "Book path is not a regular file")

    basis = Path(basis_text)
    backup_dir = _backup_dir(basis)
    try:
        source_stat = source.stat(follow_symlinks=allow_pinned_source)
        _ensure_verified_retention_capacity_before_backup(
            backup_dir,
            expected_backup_bytes=int(source_stat.st_size),
        )
    except Exception as exc:
        raise BackupError(str(source), "Verified backup retention capacity exhausted before backup mutation") from exc
    created_at = datetime.now(timezone.utc)
    timestamp = created_at.strftime("%Y%m%d_%H%M%S_%f")
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in basis.stem)
    try:
        backup_path = _copy_backup_without_overwrite(
            source,
            backup_dir,
            safe_stem,
            timestamp,
            basis.suffix,
            created_at=created_at,
        )
        _verify_and_mark_backup(
            source,
            backup_path,
            allow_pinned_source=allow_pinned_source,
            created_at=created_at,
        )
    except Exception as exc:
        raise BackupError(str(source), str(exc)) from exc

    try:
        prune_verified_book_backups(backup_dir, current_backup=backup_path)
    except Exception:
        logger.warning("Verified backup retention cleanup failed safely", exc_info=True)

    return str(backup_path)


def _book_config_value(book_config: Any, key: str, default: Any = None) -> Any:
    if isinstance(book_config, dict):
        return book_config.get(key, default)
    return getattr(book_config, key, default)


def prune_verified_book_backups(
    backup_dir: Path,
    *,
    current_backup: Path | None = None,
    now: datetime | None = None,
) -> int:
    """Prune only verified backup artifacts, preserving unknown/unsafe files.

    A backup is a prune candidate only when both the backup file and its marker are
    direct, non-symlink children of ``backup_dir`` and the marker hash/size still
    matches the file. Corrupt, unverified, unknown, and symlink artifacts are left
    untouched.
    """

    try:
        root = backup_dir.resolve(strict=True)
    except OSError:
        return 0
    current_name = current_backup.name if current_backup is not None else None
    inspection = _RetentionInspection()
    _recover_verified_backup_retention_state(root, inspection)
    if not _verified_retention_quarantine_has_capacity(root, 0, 0, inspection):
        logger.warning(
            "Verified backup retention cleanup skipped safely: quarantine budget exceeded (entries=%s bytes=%s records=%s)",
            inspection.quarantine_entries_seen,
            inspection.quarantine_bytes_seen,
            inspection.state_records_seen,
        )
        return 0
    candidates = _verified_backup_candidates(root, inspection)
    if inspection.skipped_reason:
        logger.warning(
            "Verified backup retention cleanup skipped safely: %s (entries=%s markers=%s hashes=%s bytes=%s quarantine_entries=%s quarantine_bytes=%s records=%s)",
            inspection.skipped_reason,
            inspection.entries_seen,
            inspection.markers_seen,
            inspection.hashes_seen,
            inspection.hash_bytes_seen,
            inspection.quarantine_entries_seen,
            inspection.quarantine_bytes_seen,
            inspection.state_records_seen,
        )
        return 0
    candidates.sort(key=lambda item: (item.created_at, item.name), reverse=True)
    victims = _verified_backup_retention_victims(candidates, current_name, now=now)

    deleted = 0
    for candidate in sorted(victims, key=lambda item: (item.created_at, item.name)):
        if _unlink_verified_backup_candidate(candidate, root):
            deleted += 1
    return deleted


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


def _copy_backup_without_overwrite(
    source: Path,
    backup_dir: Path,
    safe_stem: str,
    timestamp: str,
    suffix: str,
    *,
    created_at: datetime,
) -> Path:
    """Copy source to a unique backup path without replacing existing artifacts."""
    while True:
        backup_path = _unique_backup_path(backup_dir, safe_stem, timestamp, suffix)
        try:
            with source.open("rb") as src, backup_path.open("xb") as dst:
                shutil.copyfileobj(src, dst)
            source_mode = stat.S_IMODE(source.stat().st_mode)
            backup_path.chmod(source_mode)
            created_timestamp = _as_utc(created_at).timestamp()
            os.utime(backup_path, (created_timestamp, created_timestamp), follow_symlinks=False)
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


def _verify_and_mark_backup(
    source: Path,
    backup_path: Path,
    *,
    allow_pinned_source: bool = False,
    created_at: datetime | None = None,
) -> None:
    source_stat = source.stat(follow_symlinks=allow_pinned_source)
    backup_stat = backup_path.stat(follow_symlinks=False)
    if (
        not stat.S_ISREG(source_stat.st_mode)
        or not stat.S_ISREG(backup_stat.st_mode)
        or (source.is_symlink() and not allow_pinned_source)
        or backup_path.is_symlink()
        or source_stat.st_size != backup_stat.st_size
    ):
        raise BackupError(str(source), "Backup verification failed")
    backup_sha256 = _sha256_file(backup_path)
    if _sha256_file(source) != backup_sha256:
        raise BackupError(str(source), "Backup verification failed")

    marker_path = _verified_marker_path(backup_path)
    marker_payload = {
        "schema_version": 1,
        "status": "verified",
        "backup_name": backup_path.name,
        "size_bytes": backup_stat.st_size,
        "sha256": backup_sha256,
        "created_at": _as_utc(created_at or datetime.now(timezone.utc)).isoformat(),
    }
    marker_tmp = marker_path.with_name(f".{marker_path.name}.tmp")
    marker_tmp.write_text(
        json.dumps(marker_payload, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    marker_tmp.replace(marker_path)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(_HASH_CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _verified_marker_path(backup_path: Path) -> Path:
    return backup_path.with_name(backup_path.name + VERIFIED_BACKUP_MARKER_SUFFIX)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _is_direct_non_symlink_child(path: Path, root: Path) -> bool:
    try:
        if path.is_symlink() or path.parent.resolve(strict=True) != root:
            return False
        if not path.name or path.name in {".", ".."} or "/" in path.name or "\\" in path.name:
            return False
        return True
    except OSError:
        return False


def _verified_backup_candidates(root: Path, inspection: _RetentionInspection) -> list[_VerifiedBackupCandidate]:
    candidates: list[_VerifiedBackupCandidate] = []
    marker_paths = _bounded_verified_marker_paths(root, inspection)
    if inspection.skipped_reason:
        return []
    for marker_path in marker_paths:
        backup_name = marker_path.name[: -len(VERIFIED_BACKUP_MARKER_SUFFIX)]
        backup_path = root / backup_name
        candidate = _verified_backup_candidate(root, backup_path, marker_path, inspection)
        if inspection.skipped_reason:
            return []
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _bounded_verified_marker_paths(root: Path, inspection: _RetentionInspection) -> list[Path]:
    marker_paths: list[Path] = []
    try:
        with os.scandir(root) as entries:
            for entry in entries:
                if _is_verified_retention_private_name(entry.name):
                    inspection.quarantine_entries_seen += 1
                    continue
                inspection.entries_seen += 1
                if inspection.entries_seen > VERIFIED_BACKUP_RETENTION_MAX_DIRECTORY_ENTRIES:
                    inspection.skipped_reason = "directory_entry_limit_exceeded"
                    return []
                name = entry.name
                if not name.endswith(VERIFIED_BACKUP_MARKER_SUFFIX):
                    continue
                inspection.markers_seen += 1
                if inspection.markers_seen > VERIFIED_BACKUP_RETENTION_MAX_MARKERS:
                    inspection.skipped_reason = "marker_limit_exceeded"
                    return []
                marker_paths.append(root / name)
    except OSError:
        return []
    marker_paths.sort(key=lambda item: item.name)
    return marker_paths


def _verified_backup_candidate(
    root: Path,
    backup_path: Path,
    marker_path: Path,
    inspection: _RetentionInspection,
) -> _VerifiedBackupCandidate | None:
    if not _is_direct_non_symlink_child(backup_path, root) or not _is_direct_non_symlink_child(marker_path, root):
        return None
    try:
        backup_stat = backup_path.stat(follow_symlinks=False)
        marker_stat = marker_path.stat(follow_symlinks=False)
    except OSError:
        return None
    if not stat.S_ISREG(backup_stat.st_mode) or not stat.S_ISREG(marker_stat.st_mode):
        return None
    if marker_stat.st_size > VERIFIED_BACKUP_RETENTION_MAX_MARKER_BYTES:
        return None
    try:
        marker_sha256 = _sha256_file(marker_path)
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(marker, dict):
        return None
    marker_created_at = _marker_created_at(marker)
    if marker_created_at is None:
        return None
    marker_sha = _marker_expected_sha(marker, backup_path, backup_stat)
    if marker_sha is None:
        return None
    if not _within_retention_hash_budget(inspection, backup_stat.st_size):
        return None
    try:
        backup_sha = _sha256_file(backup_path)
    except OSError:
        return None
    if backup_sha != marker_sha:
        return None
    return _VerifiedBackupCandidate(
        path=backup_path,
        marker_path=marker_path,
        created_at=marker_created_at,
        name=backup_path.name,
        st_dev=int(backup_stat.st_dev),
        st_ino=int(backup_stat.st_ino),
        st_size=int(backup_stat.st_size),
        sha256=backup_sha,
        marker_st_dev=int(marker_stat.st_dev),
        marker_st_ino=int(marker_stat.st_ino),
        marker_st_size=int(marker_stat.st_size),
        marker_sha256=marker_sha256,
    )


def _within_retention_hash_budget(inspection: _RetentionInspection, size_bytes: int) -> bool:
    if inspection.hashes_seen + 1 > VERIFIED_BACKUP_RETENTION_MAX_HASHES:
        inspection.skipped_reason = "hash_count_limit_exceeded"
        return False
    if inspection.hash_bytes_seen + size_bytes > VERIFIED_BACKUP_RETENTION_MAX_HASH_BYTES:
        inspection.skipped_reason = "hash_byte_limit_exceeded"
        return False
    inspection.hashes_seen += 1
    inspection.hash_bytes_seen += size_bytes
    return True


def _marker_created_at(marker: dict[str, Any]) -> datetime | None:
    value = marker.get("created_at")
    if not isinstance(value, str) or not value.strip() or len(value) > 64:
        return None
    try:
        return _as_utc(_DATETIME_FROM_ISOFORMAT(value.replace("Z", "+00:00")))
    except ValueError:
        return None


def _marker_expected_sha(marker: dict[str, Any], backup_path: Path, backup_stat: os.stat_result) -> str | None:
    if marker.get("schema_version") != 1 or marker.get("status") != "verified":
        return None
    if marker.get("backup_name") != backup_path.name:
        return None
    if marker.get("size_bytes") != backup_stat.st_size:
        return None
    marker_sha = marker.get("sha256")
    if not isinstance(marker_sha, str) or not re_fullmatch_sha256(marker_sha):
        return None
    return marker_sha


def _current_file_matches_candidate(path: Path, candidate: _VerifiedBackupCandidate) -> bool:
    try:
        current_stat = path.stat(follow_symlinks=False)
    except OSError:
        return False
    if not stat.S_ISREG(current_stat.st_mode):
        return False
    if (
        int(current_stat.st_dev) != candidate.st_dev
        or int(current_stat.st_ino) != candidate.st_ino
        or int(current_stat.st_size) != candidate.st_size
    ):
        return False
    try:
        return _sha256_file(path) == candidate.sha256
    except OSError:
        return False


def _current_marker_matches_candidate(candidate: _VerifiedBackupCandidate) -> bool:
    return _marker_path_matches_candidate(candidate.marker_path, candidate)


def _marker_path_matches_candidate(path: Path, candidate: _VerifiedBackupCandidate) -> bool:
    try:
        marker_stat = path.stat(follow_symlinks=False)
    except OSError:
        return False
    if (
        not stat.S_ISREG(marker_stat.st_mode)
        or int(marker_stat.st_dev) != candidate.marker_st_dev
        or int(marker_stat.st_ino) != candidate.marker_st_ino
        or int(marker_stat.st_size) != candidate.marker_st_size
    ):
        return False
    try:
        return _sha256_file(path) == candidate.marker_sha256
    except OSError:
        return False


def re_fullmatch_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _verified_backup_retention_victims(
    candidates: list[_VerifiedBackupCandidate],
    current_name: str | None,
    *,
    now: datetime | None,
) -> list[_VerifiedBackupCandidate]:
    keep_limit = VERIFIED_BACKUP_MAX_COUNT
    if current_name and any(item.name == current_name for item in candidates):
        keep_limit = max(0, VERIFIED_BACKUP_MAX_COUNT - 1)

    cutoff = _as_utc(now or datetime.now(timezone.utc)) - timedelta(days=VERIFIED_BACKUP_RETENTION_DAYS)
    kept_non_current = 0
    victims: list[_VerifiedBackupCandidate] = []
    for candidate in candidates:
        if candidate.name == current_name:
            continue
        if candidate.created_at < cutoff or kept_non_current >= keep_limit:
            victims.append(candidate)
            continue
        kept_non_current += 1
    return victims


def _ensure_verified_retention_capacity_before_backup(backup_dir: Path, *, expected_backup_bytes: int) -> None:
    root = backup_dir.resolve(strict=True)
    inspection = _RetentionInspection()
    _recover_verified_backup_retention_state(root, inspection)
    if inspection.skipped_reason:
        raise BackupError(str(backup_dir), "Verified backup retention state is not recoverable")
    if not _verified_retention_quarantine_has_capacity(root, 0, 0, inspection):
        raise BackupError(str(backup_dir), "Verified backup retention quarantine budget exhausted")

    candidates = _verified_backup_candidates(root, inspection)
    if inspection.skipped_reason:
        raise BackupError(str(backup_dir), "Verified backup retention active scan budget exhausted")
    candidates.sort(key=lambda item: (item.created_at, item.name), reverse=True)
    victims = _verified_backup_retention_victims(candidates, None, now=None)
    if not victims and len(candidates) >= VERIFIED_BACKUP_MAX_COUNT:
        victims = [min(candidates, key=lambda item: (item.created_at, item.name))]
    if not victims:
        return
    required_entries = 2 * len(victims)
    required_bytes = sum(item.st_size + item.marker_st_size for item in victims)
    if required_bytes == 0:
        required_bytes = expected_backup_bytes + VERIFIED_BACKUP_RETENTION_MAX_MARKER_BYTES
    if not _verified_retention_quarantine_has_capacity(
        root,
        required_entries,
        required_bytes,
        inspection,
        additional_records=len(victims),
    ):
        raise BackupError(str(backup_dir), "Verified backup retention quarantine budget exhausted")
    retired = 0
    for victim in sorted(victims, key=lambda item: (item.created_at, item.name)):
        if _unlink_verified_backup_candidate(victim, root):
            retired += 1

    post_cleanup = _RetentionInspection()
    _recover_verified_backup_retention_state(root, post_cleanup)
    if post_cleanup.skipped_reason:
        raise BackupError(str(backup_dir), "Verified backup retention cleanup state is not recoverable")
    post_candidates = _verified_backup_candidates(root, post_cleanup)
    if post_cleanup.skipped_reason:
        raise BackupError(str(backup_dir), "Verified backup retention active scan budget exhausted")
    if len(candidates) >= VERIFIED_BACKUP_MAX_COUNT and (retired == 0 or len(post_candidates) >= VERIFIED_BACKUP_MAX_COUNT):
        raise BackupError(str(backup_dir), "Verified backup retention active capacity exhausted")


def _unlink_verified_backup_candidate(candidate: _VerifiedBackupCandidate, root: Path) -> bool:
    if not _is_direct_non_symlink_child(candidate.path, root) or not _is_direct_non_symlink_child(candidate.marker_path, root):
        return False
    if candidate.path.is_symlink() or candidate.marker_path.is_symlink():
        return False
    if not _current_file_matches_candidate(candidate.path, candidate) or not _current_marker_matches_candidate(candidate):
        logger.warning("Verified backup retention skipped changed candidate: %s", candidate.name)
        return False

    inspection = _RetentionInspection()
    if not _verified_retention_quarantine_has_capacity(
        root,
        2,
        candidate.st_size + candidate.marker_st_size,
        inspection,
        additional_records=1,
    ):
        logger.warning(
            "Verified backup retention skipped safely: quarantine budget exhausted (entries=%s bytes=%s records=%s)",
            inspection.quarantine_entries_seen,
            inspection.quarantine_bytes_seen,
            inspection.state_records_seen,
        )
        return False

    backup_quarantine_path = _unique_quarantine_path(candidate.path, root, candidate.st_dev, candidate.st_ino)
    marker_quarantine_path = _unique_quarantine_path(
        candidate.marker_path,
        root,
        candidate.marker_st_dev,
        candidate.marker_st_ino,
    )
    record = _retention_record_for_candidate(candidate, backup_quarantine_path, marker_quarantine_path, "planned")
    try:
        _upsert_retention_state_record(root, record)
    except OSError:
        logger.warning("Verified backup retention could not durably plan candidate: %s", candidate.name)
        return False

    if not _rename_no_replace(candidate.marker_path, marker_quarantine_path):
        _remove_retention_state_record(root, record)
        return False

    if not _marker_path_matches_candidate(marker_quarantine_path, candidate):
        logger.warning("Verified backup retention preserved changed marker quarantine: %s", marker_quarantine_path.name)
        _restore_quarantined_artifact(marker_quarantine_path, candidate.marker_path)
        _remove_retention_state_record(root, record)
        return False

    record["state"] = "marker_quarantined"
    try:
        _upsert_retention_state_record(root, record)
    except OSError:
        _restore_quarantined_artifact(marker_quarantine_path, candidate.marker_path)
        _remove_retention_state_record(root, record)
        return False

    if not _rename_no_replace(candidate.path, backup_quarantine_path):
        _restore_quarantined_artifact(marker_quarantine_path, candidate.marker_path)
        _remove_retention_state_record(root, record)
        return False

    if not _current_file_matches_candidate(backup_quarantine_path, candidate) or not _marker_path_matches_candidate(
        marker_quarantine_path,
        candidate,
    ):
        logger.warning("Verified backup retention preserved changed candidate quarantine: %s", backup_quarantine_path.name)
        _restore_quarantined_artifact(backup_quarantine_path, candidate.path)
        _restore_quarantined_artifact(marker_quarantine_path, candidate.marker_path)
        _remove_retention_state_record(root, record)
        return False

    if not _preserve_quarantined_verified_pair(candidate, backup_quarantine_path, marker_quarantine_path):
        _restore_quarantined_artifact(backup_quarantine_path, candidate.path)
        _restore_quarantined_artifact(marker_quarantine_path, candidate.marker_path)
        return False
    return True


def _rename_no_replace(source: Path, destination: Path) -> bool:
    """Rename source to destination only when destination does not exist.

    Retention must never clobber an unknown quarantine-path replacement. Linux
    renameat2(RENAME_NOREPLACE) gives the required single-step no-overwrite
    transition; unsupported platforms fail closed instead of falling back to a
    check-then-rename race.
    """

    try:
        _renameat2(source, destination, _RENAME_NOREPLACE)
        return True
    except OSError as exc:
        if exc.errno in {errno.EEXIST, errno.ENOSYS, errno.EINVAL, errno.EOPNOTSUPP}:
            return False
        return False


def _rename_exchange(source: Path, destination: Path) -> None:
    _renameat2(source, destination, _RENAME_EXCHANGE)


def _renameat2(source: Path, destination: Path, flags: int) -> None:
    source_bytes = os.fsencode(source)
    destination_bytes = os.fsencode(destination)
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    if renameat2 is not None:
        renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        renameat2.restype = ctypes.c_int
        result = renameat2(
            _AT_FDCWD,
            ctypes.c_char_p(source_bytes),
            _AT_FDCWD,
            ctypes.c_char_p(destination_bytes),
            ctypes.c_uint(flags),
        )
    else:
        syscall_number = _RENAMEAT2_SYSCALL_BY_MACHINE.get(platform.machine().lower())
        if syscall_number is None:
            raise OSError(errno.ENOSYS, "renameat2 unavailable", str(source))
        result = libc.syscall(
            ctypes.c_long(syscall_number),
            ctypes.c_int(_AT_FDCWD),
            ctypes.c_char_p(source_bytes),
            ctypes.c_int(_AT_FDCWD),
            ctypes.c_char_p(destination_bytes),
            ctypes.c_uint(flags),
        )
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number), str(source))


def _preserve_quarantined_verified_pair(
    candidate: _VerifiedBackupCandidate,
    backup_quarantine_path: Path,
    marker_quarantine_path: Path,
) -> bool:
    """Durably track the exact retired pair instead of path-unlinking it.

    Python/POSIX cannot unlink by a previously verified inode. A final
    path-unlink would therefore be another TOCTOU boundary where an unknown
    replacement at the quarantine path could be deleted. Active retention moves
    both active names to a private quarantine directory, records their exact
    identities, and relies on explicit quarantine budgets/backpressure instead
    of unsafe path deletion.
    """

    if not _current_file_matches_candidate(backup_quarantine_path, candidate) or not _marker_path_matches_candidate(
        marker_quarantine_path,
        candidate,
    ):
        logger.warning("Verified backup retention preserved changed quarantine pair for: %s", candidate.name)
        return False
    record = _retention_record_for_candidate(candidate, backup_quarantine_path, marker_quarantine_path, "pair_quarantined")
    try:
        _upsert_retention_state_record(candidate.path.parent, record)
    except OSError:
        logger.warning("Verified backup retention could not durably track quarantined pair: %s", candidate.name)
        return False
    return True


def _unique_quarantine_path(path: Path, root: Path, st_dev: int, st_ino: int) -> Path:
    safe_name = "".join(character if character.isalnum() or character in "-_." else "_" for character in path.name)
    quarantine_dir = _retention_state_dir(root, create=True)
    if quarantine_dir is None:
        raise OSError("retention quarantine directory unavailable")
    for _attempt in range(32):
        random_suffix = secrets.token_hex(8)
        candidate_path = quarantine_dir / f"{safe_name}.retention-delete-{st_dev}-{st_ino}-{random_suffix}.tmp"
        if not candidate_path.exists():
            return candidate_path
    raise OSError("retention quarantine name exhausted")


def _restore_quarantined_candidate(candidate: _VerifiedBackupCandidate, quarantine_path: Path) -> None:
    _restore_quarantined_artifact(quarantine_path, candidate.path)


def _restore_quarantined_artifact(quarantine_path: Path, original_path: Path) -> bool:
    try:
        if quarantine_path.exists() and not original_path.exists():
            return _rename_no_replace(quarantine_path, original_path)
    except OSError:
        logger.warning("Verified backup retention preserved unknown quarantine outside original name: %s", quarantine_path.name)
    return False


def _is_verified_retention_private_name(name: str) -> bool:
    return name == VERIFIED_BACKUP_RETENTION_STATE_DIR_NAME or ".retention-delete-" in name


def _set_retention_skip(inspection: _RetentionInspection | None, reason: str) -> None:
    if inspection is not None and inspection.skipped_reason is None:
        inspection.skipped_reason = reason


def _retention_state_dir(
    root: Path,
    *,
    create: bool = False,
    inspection: _RetentionInspection | None = None,
) -> Path | None:
    state_dir = root / VERIFIED_BACKUP_RETENTION_STATE_DIR_NAME
    try:
        root_stat = root.stat(follow_symlinks=False)
        if not stat.S_ISDIR(root_stat.st_mode):
            _set_retention_skip(inspection, "retention_root_not_directory")
            return None
    except OSError:
        _set_retention_skip(inspection, "retention_root_unavailable")
        return None
    try:
        state_stat = os.lstat(state_dir)
    except FileNotFoundError:
        if not create:
            return state_dir
        try:
            state_dir.mkdir(mode=_RETENTION_STATE_DIR_MODE, exist_ok=False)
            _fsync_directory_path(root)
            state_stat = os.lstat(state_dir)
        except OSError:
            _set_retention_skip(inspection, "retention_state_dir_create_failed")
            return None
    except OSError:
        _set_retention_skip(inspection, "retention_state_dir_unavailable")
        return None

    if stat.S_ISLNK(state_stat.st_mode) or not stat.S_ISDIR(state_stat.st_mode):
        _set_retention_skip(inspection, "retention_state_dir_not_directory")
        return None
    if stat.S_IMODE(state_stat.st_mode) != _RETENTION_STATE_DIR_MODE:
        _set_retention_skip(inspection, "retention_state_dir_not_private")
        return None
    return state_dir


def _retention_state_file(
    root: Path,
    *,
    create_dir: bool = False,
    inspection: _RetentionInspection | None = None,
) -> Path | None:
    state_dir = _retention_state_dir(root, create=create_dir, inspection=inspection)
    if state_dir is None:
        return None
    return state_dir / VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME


def _retention_record_for_candidate(
    candidate: _VerifiedBackupCandidate,
    backup_quarantine_path: Path,
    marker_quarantine_path: Path,
    state: str,
) -> dict[str, Any]:
    return {
        "schema_version": VERIFIED_BACKUP_RETENTION_STATE_SCHEMA_VERSION,
        "state": state,
        "backup_name": candidate.path.name,
        "marker_name": candidate.marker_path.name,
        "backup_quarantine_name": backup_quarantine_path.name,
        "marker_quarantine_name": marker_quarantine_path.name,
        "created_at": candidate.created_at.isoformat(),
        "backup": {
            "st_dev": candidate.st_dev,
            "st_ino": candidate.st_ino,
            "st_size": candidate.st_size,
            "sha256": candidate.sha256,
        },
        "marker": {
            "st_dev": candidate.marker_st_dev,
            "st_ino": candidate.marker_st_ino,
            "st_size": candidate.marker_st_size,
            "sha256": candidate.marker_sha256,
        },
    }


def _retention_record_key(record: dict[str, Any]) -> tuple[str, str]:
    return (str(record.get("backup_name", "")), str(record.get("marker_name", "")))


def _safe_retention_name(value: Any) -> str | None:
    if not isinstance(value, str) or not value or len(value) > 255:
        return None
    if value in {".", ".."} or "/" in value or "\\" in value:
        return None
    return value


def _load_retention_state_records(root: Path, inspection: _RetentionInspection | None = None) -> list[dict[str, Any]]:
    snapshot = _load_retention_state_snapshot(root, inspection)
    return snapshot.records


def _load_retention_state_snapshot(
    root: Path,
    inspection: _RetentionInspection | None = None,
) -> _RetentionStateSnapshot:
    state_file = _retention_state_file(root, inspection=inspection)
    if state_file is None:
        return _RetentionStateSnapshot(records=[], exists=False)
    state_dir = state_file.parent
    try:
        os.lstat(state_dir)
    except FileNotFoundError:
        return _RetentionStateSnapshot(records=[], exists=False)
    except OSError:
        _set_retention_skip(inspection, "retention_state_dir_unavailable")
        return _RetentionStateSnapshot(records=[], exists=False)

    try:
        state_stat = os.lstat(state_file)
    except FileNotFoundError:
        return _RetentionStateSnapshot(records=[], exists=False)
    except OSError:
        _set_retention_skip(inspection, "retention_state_unavailable")
        return _RetentionStateSnapshot(records=[], exists=False)

    if stat.S_ISLNK(state_stat.st_mode) or not stat.S_ISREG(state_stat.st_mode):
        _set_retention_skip(inspection, "retention_state_not_regular")
        return _RetentionStateSnapshot(records=[], exists=True)
    if stat.S_IMODE(state_stat.st_mode) != _RETENTION_STATE_FILE_MODE:
        _set_retention_skip(inspection, "retention_state_not_private")
        return _RetentionStateSnapshot(records=[], exists=True)
    if state_stat.st_size > VERIFIED_BACKUP_RETENTION_MAX_STATE_BYTES:
        _set_retention_skip(inspection, "retention_state_byte_limit_exceeded")
        return _RetentionStateSnapshot(records=[], exists=True)
    try:
        raw = _read_named_file_bytes_no_follow(
            state_dir,
            VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME,
            max_bytes=VERIFIED_BACKUP_RETENTION_MAX_STATE_BYTES,
        )
        records = _parse_retention_state_records(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        _set_retention_skip(inspection, "retention_state_invalid")
        return _RetentionStateSnapshot(records=[], exists=True)
    if inspection is not None:
        inspection.state_records_seen = len(records)
    return _RetentionStateSnapshot(
        records=records,
        exists=True,
        st_dev=int(state_stat.st_dev),
        st_ino=int(state_stat.st_ino),
        st_size=int(state_stat.st_size),
        sha256=hashlib.sha256(raw).hexdigest(),
    )


def _retention_record_is_well_formed(record: dict[str, Any]) -> bool:
    if record.get("schema_version") != VERIFIED_BACKUP_RETENTION_STATE_SCHEMA_VERSION:
        return False
    if record.get("state") not in {"planned", "marker_quarantined", "pair_quarantined"}:
        return False
    for key in ("backup_name", "marker_name", "backup_quarantine_name", "marker_quarantine_name"):
        if _safe_retention_name(record.get(key)) is None:
            return False
    backup = record.get("backup")
    marker = record.get("marker")
    if not isinstance(backup, dict) or not isinstance(marker, dict):
        return False
    for identity in (backup, marker):
        if not re_fullmatch_sha256(str(identity.get("sha256", ""))):
            return False
        for key in ("st_dev", "st_ino", "st_size"):
            value = identity.get(key)
            if not isinstance(value, int) or value < 0:
                return False
    return True


def _retention_state_body_bytes(records: list[dict[str, Any]]) -> bytes:
    body = {
        "schema_version": VERIFIED_BACKUP_RETENTION_STATE_SCHEMA_VERSION,
        "records": sorted(records, key=_retention_record_key),
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _retention_state_checksum(body: bytes) -> str:
    return hashlib.sha256(b"verified-backup-retention-state-v1\0" + body).hexdigest()


def _serialize_retention_state_records(records: list[dict[str, Any]]) -> bytes:
    for record in records:
        if not isinstance(record, dict) or not _retention_record_is_well_formed(record):
            raise OSError("retention state record invalid")
    body_bytes = _retention_state_body_bytes(records)
    if len(body_bytes) > VERIFIED_BACKUP_RETENTION_MAX_STATE_BYTES:
        raise OSError("retention state byte limit exceeded")
    payload = json.loads(body_bytes.decode("utf-8"))
    payload["checksum"] = _retention_state_checksum(body_bytes)
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(serialized) > VERIFIED_BACKUP_RETENTION_MAX_STATE_BYTES:
        raise OSError("retention state byte limit exceeded")
    return serialized


def _parse_retention_state_records(raw: bytes) -> list[dict[str, Any]]:
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "records", "checksum"}:
        raise ValueError("retention state schema invalid")
    if payload.get("schema_version") != VERIFIED_BACKUP_RETENTION_STATE_SCHEMA_VERSION:
        raise ValueError("retention state schema invalid")
    records = payload.get("records")
    checksum = payload.get("checksum")
    if not isinstance(records, list) or len(records) > VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_PAIRS:
        raise ValueError("retention state record limit exceeded")
    if not isinstance(checksum, str) or not re_fullmatch_sha256(checksum):
        raise ValueError("retention state checksum invalid")
    for record in records:
        if not isinstance(record, dict) or not _retention_record_is_well_formed(record):
            raise ValueError("retention state record invalid")
    body_bytes = _retention_state_body_bytes(records)
    if not hmac.compare_digest(checksum, _retention_state_checksum(body_bytes)):
        raise ValueError("retention state checksum mismatch")
    return sorted(records, key=_retention_record_key)


def _read_named_file_bytes_no_follow(directory: Path, name: str, *, max_bytes: int) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    dir_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    dir_fd = os.open(directory, dir_flags)
    try:
        fd = os.open(name, flags, dir_fd=dir_fd)
        try:
            file_stat = os.fstat(fd)
            if not stat.S_ISREG(file_stat.st_mode):
                raise OSError(errno.EINVAL, "retention state is not regular")
            chunks: list[bytes] = []
            bytes_read = 0
            while True:
                chunk = os.read(fd, min(8192, max_bytes + 1 - bytes_read))
                if not chunk:
                    break
                chunks.append(chunk)
                bytes_read += len(chunk)
                if bytes_read > max_bytes:
                    raise OSError(errno.EFBIG, "retention state byte limit exceeded")
            return b"".join(chunks)
        finally:
            os.close(fd)
    finally:
        os.close(dir_fd)


@contextmanager
def _locked_retention_state_dir(root: Path, *, create: bool):
    existed_before = (root / VERIFIED_BACKUP_RETENTION_STATE_DIR_NAME).exists()
    state_dir = _retention_state_dir(root, create=create)
    if state_dir is None:
        raise OSError("retention state directory unavailable")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    dir_fd = os.open(state_dir, flags)
    try:
        if not existed_before:
            _fsync_directory_path(root)
        fcntl.flock(dir_fd, fcntl.LOCK_EX)
        yield state_dir, dir_fd
    finally:
        try:
            fcntl.flock(dir_fd, fcntl.LOCK_UN)
        finally:
            os.close(dir_fd)


def _write_all_to_fd(fd: int, data: bytes) -> None:
    view = memoryview(data)
    offset = 0
    while offset < len(data):
        written = os.write(fd, view[offset:])
        if written <= 0:
            raise OSError(errno.EIO, "short retention state write")
        offset += written


def _create_retention_state_temp(dir_fd: int) -> tuple[str, int]:
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    for _attempt in range(32):
        name = f".{VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME}.{secrets.token_hex(16)}.tmp"
        try:
            return name, os.open(name, flags, _RETENTION_STATE_FILE_MODE, dir_fd=dir_fd)
        except FileExistsError:
            continue
    raise OSError(errno.EEXIST, "retention state temp name exhausted")


def _state_file_matches_snapshot(path: Path, snapshot: _RetentionStateSnapshot) -> bool:
    if not snapshot.exists:
        return not path.exists()
    try:
        current_stat = os.lstat(path)
    except OSError:
        return False
    if (
        stat.S_ISLNK(current_stat.st_mode)
        or not stat.S_ISREG(current_stat.st_mode)
        or stat.S_IMODE(current_stat.st_mode) != _RETENTION_STATE_FILE_MODE
        or int(current_stat.st_dev) != snapshot.st_dev
        or int(current_stat.st_ino) != snapshot.st_ino
        or int(current_stat.st_size) != snapshot.st_size
    ):
        return False
    try:
        raw = _read_named_file_bytes_no_follow(path.parent, path.name, max_bytes=VERIFIED_BACKUP_RETENTION_MAX_STATE_BYTES)
    except OSError:
        return False
    return hmac.compare_digest(hashlib.sha256(raw).hexdigest(), str(snapshot.sha256))


def _state_file_matches_bytes(path: Path, expected: bytes) -> bool:
    try:
        current_stat = os.lstat(path)
        if (
            stat.S_ISLNK(current_stat.st_mode)
            or not stat.S_ISREG(current_stat.st_mode)
            or stat.S_IMODE(current_stat.st_mode) != _RETENTION_STATE_FILE_MODE
            or int(current_stat.st_size) != len(expected)
        ):
            return False
        raw = _read_named_file_bytes_no_follow(path.parent, path.name, max_bytes=VERIFIED_BACKUP_RETENTION_MAX_STATE_BYTES)
    except OSError:
        return False
    return hmac.compare_digest(raw, expected)


def _best_effort_unlink_dir_entry(dir_fd: int, name: str) -> None:
    try:
        os.unlink(name, dir_fd=dir_fd)
    except FileNotFoundError:
        pass
    except OSError:
        logger.warning("Verified backup retention preserved temporary state entry: %s", name)


def _install_state_temp_when_absent(state_dir: Path, dir_fd: int, tmp_name: str, serialized: bytes) -> None:
    try:
        os.lstat(state_dir / VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME)
    except FileNotFoundError:
        pass
    except OSError as exc:
        raise OSError(exc.errno, "retention state changed before install") from exc
    else:
        raise OSError("retention state changed before install")
    try:
        os.link(
            tmp_name,
            VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME,
            src_dir_fd=dir_fd,
            dst_dir_fd=dir_fd,
            follow_symlinks=False,
        )
        _fsync_directory_fd(dir_fd)
    except OSError:
        state_path = state_dir / VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME
        if _state_file_matches_bytes(state_path, serialized):
            _best_effort_unlink_dir_entry(dir_fd, VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME)
            try:
                _fsync_directory_fd(dir_fd)
            except OSError:
                pass
        raise
    finally:
        _best_effort_unlink_dir_entry(dir_fd, tmp_name)


def _install_state_temp_over_existing(
    state_dir: Path,
    dir_fd: int,
    tmp_name: str,
    snapshot: _RetentionStateSnapshot,
    serialized: bytes,
) -> None:
    state_path = state_dir / VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME
    tmp_path = state_dir / tmp_name
    if not _state_file_matches_snapshot(state_path, snapshot):
        raise OSError("retention state changed before install")
    exchanged = False
    try:
        _rename_exchange(tmp_path, state_path)
        exchanged = True
        if not _state_file_matches_snapshot(tmp_path, snapshot):
            _rename_exchange(tmp_path, state_path)
            exchanged = False
            _fsync_directory_fd(dir_fd)
            raise OSError("retention state changed during install")
        if not _state_file_matches_bytes(state_path, serialized):
            _rename_exchange(tmp_path, state_path)
            exchanged = False
            _fsync_directory_fd(dir_fd)
            raise OSError("retention state install verification failed")
        try:
            _fsync_directory_fd(dir_fd)
        except OSError:
            _rename_exchange(tmp_path, state_path)
            exchanged = False
            try:
                _fsync_directory_fd(dir_fd)
            except OSError:
                pass
            raise
    except OSError:
        if exchanged and not _state_file_matches_snapshot(state_path, snapshot):
            try:
                _rename_exchange(tmp_path, state_path)
                _fsync_directory_fd(dir_fd)
            except OSError:
                logger.warning("Verified backup retention preserved state after failed rollback")
        raise
    finally:
        _best_effort_unlink_dir_entry(dir_fd, tmp_name)


def _write_retention_state_records(root: Path, records: list[dict[str, Any]]) -> None:
    if len(records) > VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_PAIRS:
        raise OSError("retention state record limit exceeded")
    serialized = _serialize_retention_state_records(records)
    with _locked_retention_state_dir(root, create=True) as (state_dir, dir_fd):
        inspection = _RetentionInspection()
        snapshot = _load_retention_state_snapshot(root, inspection)
        if inspection.skipped_reason:
            raise OSError("retention state invalid before update")
        tmp_name, tmp_fd = _create_retention_state_temp(dir_fd)
        try:
            _write_all_to_fd(tmp_fd, serialized)
            tmp_stat = os.fstat(tmp_fd)
            if stat.S_IMODE(tmp_stat.st_mode) != _RETENTION_STATE_FILE_MODE:
                raise OSError("retention state temp mode invalid")
            os.fsync(tmp_fd)
        finally:
            os.close(tmp_fd)
        try:
            if snapshot.exists:
                _install_state_temp_over_existing(state_dir, dir_fd, tmp_name, snapshot, serialized)
            else:
                _install_state_temp_when_absent(state_dir, dir_fd, tmp_name, serialized)
        except OSError:
            _best_effort_unlink_dir_entry(dir_fd, tmp_name)
            raise


def _upsert_retention_state_record(root: Path, record: dict[str, Any]) -> None:
    inspection = _RetentionInspection()
    records = _load_retention_state_records(root, inspection)
    if inspection.skipped_reason:
        raise OSError("retention state invalid before update")
    key = _retention_record_key(record)
    records = [existing for existing in records if _retention_record_key(existing) != key]
    records.append(record)
    _write_retention_state_records(root, records)


def _remove_retention_state_record(root: Path, record: dict[str, Any]) -> None:
    try:
        key = _retention_record_key(record)
        inspection = _RetentionInspection()
        records = [existing for existing in _load_retention_state_records(root, inspection) if _retention_record_key(existing) != key]
        if inspection.skipped_reason:
            raise OSError("retention state invalid before update")
        _write_retention_state_records(root, records)
    except OSError:
        logger.warning("Verified backup retention could not update state after restore: %s", record.get("backup_name", "unknown"))


def _candidate_from_retention_record(root: Path, record: dict[str, Any]) -> _VerifiedBackupCandidate | None:
    try:
        backup = record["backup"]
        marker = record["marker"]
        created_at = _as_utc(_DATETIME_FROM_ISOFORMAT(str(record.get("created_at", "")).replace("Z", "+00:00")))
        backup_name = _safe_retention_name(record.get("backup_name"))
        marker_name = _safe_retention_name(record.get("marker_name"))
        if backup_name is None or marker_name is None:
            return None
        return _VerifiedBackupCandidate(
            path=root / backup_name,
            marker_path=root / marker_name,
            created_at=created_at,
            name=backup_name,
            st_dev=int(backup["st_dev"]),
            st_ino=int(backup["st_ino"]),
            st_size=int(backup["st_size"]),
            sha256=str(backup["sha256"]),
            marker_st_dev=int(marker["st_dev"]),
            marker_st_ino=int(marker["st_ino"]),
            marker_st_size=int(marker["st_size"]),
            marker_sha256=str(marker["sha256"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _path_lstat_exists(path: Path) -> bool:
    try:
        os.lstat(path)
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return True


def _quarantine_artifact_matches(path: Path, candidate: _VerifiedBackupCandidate, kind: str) -> bool:
    if kind == "backup":
        return _current_file_matches_candidate(path, candidate)
    if kind == "marker":
        return _marker_path_matches_candidate(path, candidate)
    raise ValueError(f"unknown quarantine artifact kind {kind}")


def _quarantine_artifact_size(candidate: _VerifiedBackupCandidate, kind: str) -> int:
    if kind == "backup":
        return candidate.st_size
    if kind == "marker":
        return candidate.marker_st_size
    raise ValueError(f"unknown quarantine artifact kind {kind}")


def _fd_matches_quarantine_artifact(fd: int, candidate: _VerifiedBackupCandidate, kind: str) -> bool:
    try:
        file_stat = os.fstat(fd)
        if not stat.S_ISREG(file_stat.st_mode) or int(file_stat.st_nlink) != 1:
            return False
        if kind == "backup":
            expected_dev = candidate.st_dev
            expected_ino = candidate.st_ino
            expected_size = candidate.st_size
            expected_sha256 = candidate.sha256
        elif kind == "marker":
            expected_dev = candidate.marker_st_dev
            expected_ino = candidate.marker_st_ino
            expected_size = candidate.marker_st_size
            expected_sha256 = candidate.marker_sha256
        else:
            return False
        if (
            int(file_stat.st_dev) != expected_dev
            or int(file_stat.st_ino) != expected_ino
            or int(file_stat.st_size) != expected_size
        ):
            return False
        os.lseek(fd, 0, os.SEEK_SET)
        digest = hashlib.sha256()
        while True:
            chunk = os.read(fd, _HASH_CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
        os.lseek(fd, 0, os.SEEK_SET)
        return hmac.compare_digest(digest.hexdigest(), expected_sha256)
    except OSError:
        return False


def _reclaim_quarantined_artifact(
    path: Path,
    candidate: _VerifiedBackupCandidate,
    kind: str,
    state_dir: Path,
    inspection: _RetentionInspection,
) -> bool:
    """Reclaim verified bytes through an already-open descriptor.

    There is no portable path primitive that unlinks "this inode only" after a
    raceable final pathname boundary.  Keep the quarantine entry and durable
    state, but make safe byte progress by ftruncate() on a descriptor that was
    opened from the private state directory and verified by identity, size,
    hash, regular-file type, and nlink.  If the pathname is replaced after the
    descriptor is verified, ftruncate still affects only the original opened
    inode while the replacement remains untouched and tracked.
    """

    try:
        with _locked_retention_state_dir(candidate.path.parent, create=False) as (locked_state_dir, dir_fd):
            if locked_state_dir != state_dir:
                return False
            if path.parent != state_dir or _safe_retention_name(path.name) != path.name:
                return False
            flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
            try:
                fd = os.open(path.name, flags, dir_fd=dir_fd)
            except OSError:
                return False
            try:
                if not _fd_matches_quarantine_artifact(fd, candidate, kind):
                    return False
                os.ftruncate(fd, 0)
                os.fsync(fd)
            except OSError:
                return False
            finally:
                os.close(fd)
    except OSError:
        return False
    inspection.reclaimed_bytes += _quarantine_artifact_size(candidate, kind)
    return True


def _recover_retention_record(
    root: Path,
    state_dir: Path,
    record: dict[str, Any],
    inspection: _RetentionInspection,
) -> dict[str, Any] | None:
    candidate = _candidate_from_retention_record(root, record)
    if candidate is None:
        return None
    backup_quarantine_name = _safe_retention_name(record.get("backup_quarantine_name"))
    marker_quarantine_name = _safe_retention_name(record.get("marker_quarantine_name"))
    if backup_quarantine_name is None or marker_quarantine_name is None:
        return None
    backup_quarantine_path = state_dir / backup_quarantine_name
    marker_quarantine_path = state_dir / marker_quarantine_name
    active_backup = _current_file_matches_candidate(candidate.path, candidate)
    active_marker = _current_marker_matches_candidate(candidate)
    quarantined_backup = _current_file_matches_candidate(backup_quarantine_path, candidate)
    quarantined_marker = _marker_path_matches_candidate(marker_quarantine_path, candidate)

    if record.get("state") == "pair_quarantined" or (quarantined_backup and quarantined_marker):
        reclaimed_before = inspection.reclaimed_entries
        if quarantined_backup:
            _reclaim_quarantined_artifact(backup_quarantine_path, candidate, "backup", state_dir, inspection)
        if quarantined_marker:
            _reclaim_quarantined_artifact(marker_quarantine_path, candidate, "marker", state_dir, inspection)
        remaining_known_backup = _current_file_matches_candidate(backup_quarantine_path, candidate)
        remaining_known_marker = _marker_path_matches_candidate(marker_quarantine_path, candidate)
        remaining_unknown_backup = _path_lstat_exists(backup_quarantine_path) and not remaining_known_backup
        remaining_unknown_marker = _path_lstat_exists(marker_quarantine_path) and not remaining_known_marker
        if not (remaining_known_backup or remaining_known_marker or remaining_unknown_backup or remaining_unknown_marker):
            if inspection.reclaimed_entries - reclaimed_before == 2:
                inspection.reclaimed_pairs += 1
            return None
        record["state"] = "pair_quarantined"
        return record

    if active_backup and active_marker:
        return None
    if quarantined_marker and active_backup and not active_marker:
        if _restore_quarantined_artifact(marker_quarantine_path, candidate.marker_path):
            return None
    if quarantined_backup and active_marker and not active_backup:
        if _restore_quarantined_artifact(backup_quarantine_path, candidate.path):
            return None
    return record


def _recover_verified_backup_retention_state(root: Path, inspection: _RetentionInspection) -> None:
    records = _load_retention_state_records(root, inspection)
    if inspection.skipped_reason:
        return
    if not records:
        return
    state_dir = _retention_state_dir(root, inspection=inspection)
    if state_dir is None:
        inspection.skipped_reason = "retention_state_dir_unavailable"
        return
    recovered_records: list[dict[str, Any]] = []
    for record in records:
        recovered_record = _recover_retention_record(root, state_dir, record, inspection)
        if recovered_record is not None:
            recovered_records.append(recovered_record)
    try:
        _write_retention_state_records(root, recovered_records)
    except OSError:
        inspection.skipped_reason = "retention_state_write_failed"


def _verified_retention_quarantine_has_capacity(
    root: Path,
    additional_entries: int,
    additional_bytes: int,
    inspection: _RetentionInspection,
    *,
    additional_records: int = 0,
) -> bool:
    entry_count, byte_count = _retention_quarantine_usage(root, inspection)
    records = _load_retention_state_records(root, inspection)
    inspection.quarantine_entries_seen = max(inspection.quarantine_entries_seen, entry_count)
    inspection.quarantine_bytes_seen = byte_count
    inspection.state_records_seen = len(records)
    if inspection.skipped_reason:
        return False
    if len(records) + additional_records > VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_PAIRS:
        return False
    if entry_count + additional_entries > VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES:
        return False
    if byte_count + additional_bytes > VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES:
        inspection.skipped_reason = "retention_quarantine_byte_limit_exceeded"
        return False
    return True


def _retention_quarantine_usage(
    root: Path,
    inspection: _RetentionInspection | None = None,
) -> tuple[int, int]:
    entries = 0
    bytes_seen = 0
    state_dir = _retention_state_dir(root, inspection=inspection)
    if inspection is not None and inspection.skipped_reason:
        return (VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES + 1, VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES + 1)
    if state_dir is not None and _path_lstat_exists(state_dir):
        try:
            with os.scandir(state_dir) as children:
                for child in children:
                    if child.name == VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME or child.name.startswith(
                    f".{VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME}"
                    ):
                        continue
                    if entries >= VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES:
                        _set_retention_skip(inspection, "retention_quarantine_entry_limit_exceeded")
                        return (VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES + 1, bytes_seen)
                    entries += 1
                    try:
                        child_stat = child.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    if stat.S_ISREG(child_stat.st_mode):
                        size = int(child_stat.st_size)
                        if bytes_seen + size > VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES:
                            _set_retention_skip(inspection, "retention_quarantine_byte_limit_exceeded")
                            return (entries, VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES + 1)
                        bytes_seen += size
        except OSError:
            _set_retention_skip(inspection, "retention_quarantine_unreadable")
            return (VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES + 1, VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES + 1)
    try:
        with os.scandir(root) as children:
            for child in children:
                if ".retention-delete-" not in child.name:
                    continue
                if entries >= VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES:
                    _set_retention_skip(inspection, "retention_quarantine_entry_limit_exceeded")
                    return (VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES + 1, bytes_seen)
                entries += 1
                try:
                    child_stat = child.stat(follow_symlinks=False)
                except OSError:
                    continue
                if stat.S_ISREG(child_stat.st_mode):
                    size = int(child_stat.st_size)
                    if bytes_seen + size > VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES:
                        _set_retention_skip(inspection, "retention_quarantine_byte_limit_exceeded")
                        return (entries, VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES + 1)
                    bytes_seen += size
    except OSError:
        _set_retention_skip(inspection, "retention_quarantine_unreadable")
        return (VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES + 1, VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES + 1)
    if inspection is not None:
        inspection.quarantine_entries_seen = entries
        inspection.quarantine_bytes_seen = bytes_seen
    return entries, bytes_seen


def _fsync_directory_fd(directory_fd: int) -> None:
    os.fsync(directory_fd)


def _fsync_directory_path(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    directory_fd = os.open(path, flags)
    try:
        _fsync_directory_fd(directory_fd)
    finally:
        os.close(directory_fd)


def _fsync_parent(path: Path) -> None:
    _fsync_directory_path(path.parent)
