"""Safe app metadata SQLite backup, verification, and restore rehearsal helpers."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import stat
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from app.services.app_metadata_schema import (
    APP_METADATA_REQUIRED_COLUMNS,
    APP_METADATA_REQUIRED_UNIQUE_INDEX_COLUMNS,
    APP_METADATA_TABLE_ALLOWLIST,
    CURRENT_APP_METADATA_SCHEMA_VERSION,
)

TOOL_VERSION = "1"
FORMAT_VERSION = "app-metadata-recovery-v1"
BACKUP_DB_FILENAME = "app.db"
MANIFEST_FILENAME = "manifest.json"
BACKUP_METHOD = "sqlite_backup_api"
RUNTIME_MODE_STOPPED = "offline_runtime_stopped_ack"

RUNTIME_ACK_MISSING = "runtime_ack_missing"
SOURCE_MISSING = "source_missing"
SOURCE_NOT_REGULAR = "source_not_regular"
DESTINATION_EXISTS = "destination_exists"
DESTINATION_INSIDE_REPO = "destination_inside_repo"
PERMISSION_DENIED = "permission_denied"
SQLITE_INTEGRITY_FAIL = "sqlite_integrity_fail"
CHECKSUM_MISMATCH = "checksum_mismatch"
UNSUPPORTED_SCHEMA = "unsupported_schema"
MANIFEST_INVALID = "manifest_invalid"
UNSAFE_RESTORE_DESTINATION = "unsafe_restore_destination"
PARTIAL_CLEANUP_FAILURE = "partial_cleanup_failure"
INTERNAL_ERROR = "internal_error"

ERROR_EXIT_CODES: dict[str, int] = {
    RUNTIME_ACK_MISSING: 10,
    SOURCE_MISSING: 11,
    SOURCE_NOT_REGULAR: 12,
    DESTINATION_EXISTS: 13,
    DESTINATION_INSIDE_REPO: 14,
    PERMISSION_DENIED: 15,
    SQLITE_INTEGRITY_FAIL: 16,
    CHECKSUM_MISMATCH: 17,
    UNSUPPORTED_SCHEMA: 18,
    MANIFEST_INVALID: 19,
    UNSAFE_RESTORE_DESTINATION: 20,
    PARTIAL_CLEANUP_FAILURE: 21,
    INTERNAL_ERROR: 1,
}

MANIFEST_KEYS: frozenset[str] = frozenset(
    {
        "utc_timestamp",
        "tool_version",
        "format_version",
        "app_schema_version",
        "file_size_bytes",
        "sha256",
        "sqlite_page_count",
        "integrity_check",
        "tables",
        "row_counts",
        "schema_signature",
        "backup_method",
        "runtime_mode",
        "verification_status",
    }
)


class AppMetadataRecoveryError(RuntimeError):
    """Controlled, redacted recovery error with a stable safe code."""

    def __init__(self, code: str, message: str | None = None) -> None:
        super().__init__(message or code)
        self.code = code
        self.exit_code = ERROR_EXIT_CODES.get(code, ERROR_EXIT_CODES[INTERNAL_ERROR])


@dataclass(frozen=True)
class DbInspection:
    file_size_bytes: int
    sha256: str
    sqlite_page_count: int
    integrity_check: str
    app_schema_version: int
    raw_user_version: int
    tables: tuple[str, ...]
    row_counts: dict[str, int]
    schema_signature: str


@dataclass(frozen=True)
class RecoveryResult:
    operation: str
    status: str
    manifest: dict[str, Any]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "status": self.status,
            "manifest": self.manifest,
        }


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def redacted_error_payload(exc: AppMetadataRecoveryError) -> dict[str, object]:
    return {"status": "error", "safe_code": exc.code, "exit_code": exc.exit_code}


def public_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def backup_app_metadata(
    *,
    source_db: Path | str,
    bundle_dir: Path | str,
    runtime_stopped: bool,
    repo_root: Path | str | None = None,
    timestamp: str | None = None,
) -> RecoveryResult:
    """Back up one offline app metadata SQLite DB into a redacted bundle."""

    if not runtime_stopped:
        raise AppMetadataRecoveryError(RUNTIME_ACK_MISSING)

    source = _validate_source_db(Path(source_db))
    root = _repo_root(repo_root)
    bundle = _validate_backup_destination(Path(bundle_dir), root)

    tmp_dir: Path | None = None
    try:
        tmp_dir = Path(
            tempfile.mkdtemp(prefix=f".{bundle.name}.tmp-", dir=str(bundle.parent))
        )
        _chmod(tmp_dir, 0o700)
        tmp_db = tmp_dir / BACKUP_DB_FILENAME
        _sqlite_backup(source, tmp_db)
        _chmod(tmp_db, 0o600)
        _fsync_file(tmp_db)
        inspection = inspect_app_metadata_db(tmp_db)
        manifest = _manifest_from_inspection(inspection, timestamp=timestamp)
        _write_json_file(tmp_dir / MANIFEST_FILENAME, manifest)
        _fsync_dir(tmp_dir)
        os.replace(tmp_dir, bundle)
        tmp_dir = None
        _fsync_dir(bundle.parent)
        return RecoveryResult(operation="backup", status="ok", manifest=manifest)
    except AppMetadataRecoveryError as exc:
        _cleanup_or_partial_failure(tmp_dir, exc)
        raise
    except PermissionError as exc:
        controlled = AppMetadataRecoveryError(PERMISSION_DENIED)
        _cleanup_or_partial_failure(tmp_dir, controlled)
        raise controlled from exc
    except OSError as exc:
        controlled = AppMetadataRecoveryError(PERMISSION_DENIED)
        _cleanup_or_partial_failure(tmp_dir, controlled)
        raise controlled from exc


def verify_bundle(
    *,
    bundle_dir: Path | str,
    repo_root: Path | str | None = None,
) -> RecoveryResult:
    """Verify a backup bundle without exposing private source values."""

    _ = _repo_root(repo_root)
    bundle = Path(bundle_dir).expanduser()
    if _has_parent_traversal(bundle) or _has_symlink_component(bundle, include_leaf=True):
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    try:
        bundle = bundle.resolve(strict=True)
    except FileNotFoundError as exc:
        raise AppMetadataRecoveryError(MANIFEST_INVALID) from exc
    except PermissionError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc
    if not bundle.is_dir():
        raise AppMetadataRecoveryError(MANIFEST_INVALID)

    files = {path.name for path in bundle.iterdir() if path.is_file()}
    if files != {BACKUP_DB_FILENAME, MANIFEST_FILENAME}:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)

    db_path = bundle / BACKUP_DB_FILENAME
    manifest = _read_manifest(bundle / MANIFEST_FILENAME)
    _validate_manifest_shape(manifest)

    file_size = db_path.stat().st_size
    if int(manifest["file_size_bytes"]) != file_size:
        raise AppMetadataRecoveryError(CHECKSUM_MISMATCH)
    if str(manifest["sha256"]) != _sha256(db_path):
        raise AppMetadataRecoveryError(CHECKSUM_MISMATCH)

    inspection = inspect_app_metadata_db(db_path)
    _assert_manifest_matches_inspection(manifest, inspection)
    verified_manifest = dict(manifest)
    verified_manifest["verification_status"] = "verified"
    return RecoveryResult(operation="verify", status="ok", manifest=verified_manifest)


def restore_rehearsal(
    *,
    bundle_dir: Path | str,
    destination_db: Path | str,
    repo_root: Path | str | None = None,
) -> RecoveryResult:
    """Restore a verified bundle into a new DB path for rehearsal only."""

    root = _repo_root(repo_root)
    verification = verify_bundle(bundle_dir=bundle_dir, repo_root=root)
    destination = _validate_restore_destination(Path(destination_db), root)
    bundle = Path(bundle_dir).expanduser().resolve(strict=True)
    source = bundle / BACKUP_DB_FILENAME
    tmp_db = destination.parent / f".{destination.name}.tmp-{os.getpid()}-{time.time_ns()}"
    try:
        _sqlite_backup(source, tmp_db)
        _chmod(tmp_db, 0o600)
        _fsync_file(tmp_db)
        tmp_inspection = inspect_app_metadata_db(tmp_db)
        _assert_manifest_matches_inspection(verification.manifest, tmp_inspection)
        os.replace(tmp_db, destination)
        _fsync_dir(destination.parent)
        final_inspection = inspect_app_metadata_db(destination)
        _assert_manifest_matches_inspection(verification.manifest, final_inspection)
        return RecoveryResult(
            operation="restore-rehearsal",
            status="ok",
            manifest=verification.manifest,
        )
    except AppMetadataRecoveryError as exc:
        _cleanup_file_or_partial_failure(tmp_db, exc)
        raise
    except PermissionError as exc:
        controlled = AppMetadataRecoveryError(PERMISSION_DENIED)
        _cleanup_file_or_partial_failure(tmp_db, controlled)
        raise controlled from exc
    except OSError as exc:
        controlled = AppMetadataRecoveryError(PERMISSION_DENIED)
        _cleanup_file_or_partial_failure(tmp_db, controlled)
        raise controlled from exc


def inspect_app_metadata_db(path: Path | str) -> DbInspection:
    db_path = Path(path)
    try:
        file_size = db_path.stat().st_size
    except PermissionError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc
    except FileNotFoundError as exc:
        raise AppMetadataRecoveryError(SOURCE_MISSING) from exc

    digest = _sha256(db_path)
    try:
        with _connect_readonly(db_path) as conn:
            integrity_rows = [str(row[0]) for row in conn.execute("pragma integrity_check").fetchall()]
            if integrity_rows != ["ok"]:
                raise AppMetadataRecoveryError(SQLITE_INTEGRITY_FAIL)
            page_count = int(conn.execute("pragma page_count").fetchone()[0])
            raw_user_version = int(conn.execute("pragma user_version").fetchone()[0])
            tables = tuple(
                str(row[0])
                for row in conn.execute(
                    "select name from sqlite_master "
                    "where type = 'table' and name not like 'sqlite_%' order by name"
                ).fetchall()
            )
            signature_payload = _schema_signature_payload(conn, tables)
            app_schema_version = _validate_schema_signature(raw_user_version, signature_payload)
            row_counts = {
                table_name: int(
                    conn.execute(f"select count(*) from {_quote_identifier(table_name)}").fetchone()[0]
                )
                for table_name in APP_METADATA_TABLE_ALLOWLIST
            }
    except AppMetadataRecoveryError:
        raise
    except sqlite3.DatabaseError as exc:
        raise AppMetadataRecoveryError(SQLITE_INTEGRITY_FAIL) from exc
    except PermissionError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc

    return DbInspection(
        file_size_bytes=file_size,
        sha256=digest,
        sqlite_page_count=page_count,
        integrity_check="ok",
        app_schema_version=app_schema_version,
        raw_user_version=raw_user_version,
        tables=APP_METADATA_TABLE_ALLOWLIST,
        row_counts=row_counts,
        schema_signature=_schema_signature_hash(signature_payload),
    )


def _manifest_from_inspection(
    inspection: DbInspection,
    *,
    timestamp: str | None = None,
) -> dict[str, Any]:
    return {
        "utc_timestamp": timestamp or _utc_timestamp(),
        "tool_version": TOOL_VERSION,
        "format_version": FORMAT_VERSION,
        "app_schema_version": inspection.app_schema_version,
        "file_size_bytes": inspection.file_size_bytes,
        "sha256": inspection.sha256,
        "sqlite_page_count": inspection.sqlite_page_count,
        "integrity_check": inspection.integrity_check,
        "tables": list(APP_METADATA_TABLE_ALLOWLIST),
        "row_counts": {table: inspection.row_counts[table] for table in APP_METADATA_TABLE_ALLOWLIST},
        "schema_signature": inspection.schema_signature,
        "backup_method": BACKUP_METHOD,
        "runtime_mode": RUNTIME_MODE_STOPPED,
        "verification_status": "verified",
    }


def _validate_manifest_shape(manifest: dict[str, Any]) -> None:
    if not isinstance(manifest, dict) or set(manifest) != MANIFEST_KEYS:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if manifest["tool_version"] != TOOL_VERSION:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if manifest["format_version"] != FORMAT_VERSION:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if manifest["backup_method"] != BACKUP_METHOD:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if manifest["runtime_mode"] != RUNTIME_MODE_STOPPED:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if manifest["verification_status"] != "verified":
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if manifest["integrity_check"] != "ok":
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if manifest["tables"] != list(APP_METADATA_TABLE_ALLOWLIST):
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if set(manifest["row_counts"]) != set(APP_METADATA_TABLE_ALLOWLIST):
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if not isinstance(manifest["sha256"], str) or len(manifest["sha256"]) != 64:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if not isinstance(manifest["schema_signature"], str) or len(manifest["schema_signature"]) != 64:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    for key in ("app_schema_version", "file_size_bytes", "sqlite_page_count"):
        if not isinstance(manifest[key], int) or manifest[key] < 0:
            raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if manifest["app_schema_version"] != CURRENT_APP_METADATA_SCHEMA_VERSION:
        raise AppMetadataRecoveryError(UNSUPPORTED_SCHEMA)
    for value in manifest["row_counts"].values():
        if not isinstance(value, int) or value < 0:
            raise AppMetadataRecoveryError(MANIFEST_INVALID)


def _assert_manifest_matches_inspection(
    manifest: dict[str, Any], inspection: DbInspection) -> None:
    if manifest["sha256"] != inspection.sha256:
        raise AppMetadataRecoveryError(CHECKSUM_MISMATCH)
    if manifest["file_size_bytes"] != inspection.file_size_bytes:
        raise AppMetadataRecoveryError(CHECKSUM_MISMATCH)
    if manifest["sqlite_page_count"] != inspection.sqlite_page_count:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if manifest["app_schema_version"] != inspection.app_schema_version:
        raise AppMetadataRecoveryError(UNSUPPORTED_SCHEMA)
    if manifest["schema_signature"] != inspection.schema_signature:
        raise AppMetadataRecoveryError(UNSUPPORTED_SCHEMA)
    if manifest["row_counts"] != inspection.row_counts:
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    if inspection.integrity_check != "ok":
        raise AppMetadataRecoveryError(SQLITE_INTEGRITY_FAIL)


def _schema_signature_payload(conn: sqlite3.Connection, tables: tuple[str, ...]) -> dict[str, Any]:
    columns: dict[str, tuple[str, ...]] = {}
    unique_indexes: dict[str, tuple[tuple[str, ...], ...]] = {}
    for table_name in tables:
        quoted_table = _quote_identifier(table_name)
        columns[table_name] = tuple(
            sorted(
                str(row[1])
                for row in conn.execute(f"pragma table_info({quoted_table})").fetchall()
            )
        )
        index_columns: list[tuple[str, ...]] = []
        for index_row in conn.execute(f"pragma index_list({quoted_table})").fetchall():
            is_unique = int(index_row[2]) == 1
            origin = str(index_row[3]) if len(index_row) > 3 else ""
            if not is_unique or origin == "pk":
                continue
            index_name = str(index_row[1])
            quoted_index = _quote_identifier(index_name)
            index_columns.append(
                tuple(
                    str(info_row[2])
                    for info_row in conn.execute(f"pragma index_info({quoted_index})").fetchall()
                )
            )
        unique_indexes[table_name] = tuple(sorted(index_columns))
    return {"tables": tuple(sorted(tables)), "columns": columns, "unique_indexes": unique_indexes}


def _validate_schema_signature(raw_user_version: int, payload: dict[str, Any]) -> int:
    expected_tables_sorted = tuple(sorted(APP_METADATA_TABLE_ALLOWLIST))
    if tuple(payload["tables"]) != expected_tables_sorted:
        raise AppMetadataRecoveryError(UNSUPPORTED_SCHEMA)
    for table_name, expected_columns in APP_METADATA_REQUIRED_COLUMNS.items():
        if set(payload["columns"].get(table_name, ())) != set(expected_columns):
            raise AppMetadataRecoveryError(UNSUPPORTED_SCHEMA)
        actual_indexes = set(payload["unique_indexes"].get(table_name, ()))
        expected_indexes = APP_METADATA_REQUIRED_UNIQUE_INDEX_COLUMNS.get(table_name, set())
        if actual_indexes != expected_indexes:
            raise AppMetadataRecoveryError(UNSUPPORTED_SCHEMA)
    if raw_user_version == 0:
        return CURRENT_APP_METADATA_SCHEMA_VERSION
    if raw_user_version == CURRENT_APP_METADATA_SCHEMA_VERSION:
        return CURRENT_APP_METADATA_SCHEMA_VERSION
    raise AppMetadataRecoveryError(UNSUPPORTED_SCHEMA)


def _schema_signature_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sqlite_backup(source: Path, destination: Path) -> None:
    try:
        with _connect_readonly(source) as source_conn:
            with sqlite3.connect(destination) as dest_conn:
                source_conn.backup(dest_conn)
                dest_conn.commit()
    except AppMetadataRecoveryError:
        raise
    except sqlite3.OperationalError as exc:
        message = str(exc).lower()
        if "unable to open" in message or "readonly" in message or "permission" in message:
            raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc
        raise AppMetadataRecoveryError(SQLITE_INTEGRITY_FAIL) from exc
    except sqlite3.DatabaseError as exc:
        raise AppMetadataRecoveryError(SQLITE_INTEGRITY_FAIL) from exc


def _connect_readonly(path: Path) -> sqlite3.Connection:
    uri_path = quote(str(path), safe="/")
    try:
        conn = sqlite3.connect(f"file:{uri_path}?mode=ro", uri=True)
    except sqlite3.OperationalError as exc:
        message = str(exc).lower()
        if "unable to open" in message or "permission" in message:
            raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc
        raise AppMetadataRecoveryError(SQLITE_INTEGRITY_FAIL) from exc
    conn.row_factory = sqlite3.Row
    return conn


def _validate_source_db(source: Path) -> Path:
    if _has_parent_traversal(source):
        raise AppMetadataRecoveryError(SOURCE_NOT_REGULAR)
    try:
        source_lstat = source.expanduser().lstat()
    except FileNotFoundError as exc:
        raise AppMetadataRecoveryError(SOURCE_MISSING) from exc
    except PermissionError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc
    if stat.S_ISLNK(source_lstat.st_mode) or not stat.S_ISREG(source_lstat.st_mode):
        raise AppMetadataRecoveryError(SOURCE_NOT_REGULAR)
    try:
        return source.expanduser().resolve(strict=True)
    except PermissionError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc


def _validate_backup_destination(bundle: Path, repo_root: Path) -> Path:
    if _has_parent_traversal(bundle):
        raise AppMetadataRecoveryError(DESTINATION_INSIDE_REPO)
    bundle = bundle.expanduser()
    if _has_symlink_component(bundle, include_leaf=True):
        raise AppMetadataRecoveryError(DESTINATION_INSIDE_REPO)
    resolved = bundle.resolve(strict=False)
    if _is_relative_to(resolved, repo_root):
        raise AppMetadataRecoveryError(DESTINATION_INSIDE_REPO)
    if bundle.exists() or bundle.is_symlink():
        raise AppMetadataRecoveryError(DESTINATION_EXISTS)
    _ensure_private_parent(resolved.parent)
    return resolved


def _validate_restore_destination(destination: Path, repo_root: Path) -> Path:
    if not destination.is_absolute() or _has_parent_traversal(destination):
        raise AppMetadataRecoveryError(UNSAFE_RESTORE_DESTINATION)
    destination = destination.expanduser()
    if _has_symlink_component(destination, include_leaf=True):
        raise AppMetadataRecoveryError(UNSAFE_RESTORE_DESTINATION)
    resolved = destination.resolve(strict=False)
    if _is_relative_to(resolved, repo_root):
        raise AppMetadataRecoveryError(DESTINATION_INSIDE_REPO)
    if destination.exists():
        raise AppMetadataRecoveryError(DESTINATION_EXISTS)
    _ensure_private_parent(resolved.parent)
    return resolved


def _ensure_private_parent(parent: Path) -> None:
    try:
        parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        _chmod(parent, 0o700)
    except PermissionError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc
    except OSError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc


def _repo_root(repo_root: Path | str | None) -> Path:
    return Path(repo_root).resolve() if repo_root is not None else default_repo_root().resolve()


def _has_parent_traversal(path: Path) -> bool:
    return any(part == ".." for part in path.parts)


def _has_symlink_component(path: Path, *, include_leaf: bool) -> bool:
    expanded = path.expanduser()
    candidates: list[Path] = []
    if include_leaf:
        candidates.append(expanded)
    candidates.extend(expanded.parents)
    for candidate in candidates:
        if candidate == candidate.parent:
            continue
        try:
            if candidate.is_symlink():
                return True
        except OSError:
            continue
    return False


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except PermissionError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc
    return digest.hexdigest()


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise AppMetadataRecoveryError(MANIFEST_INVALID) from exc
    if not isinstance(manifest, dict):
        raise AppMetadataRecoveryError(MANIFEST_INVALID)
    return manifest


def _write_json_file(path: Path, payload: dict[str, Any]) -> None:
    try:
        with path.open("w", encoding="utf-8") as handle:
            handle.write(public_json(payload))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        _chmod(path, 0o600)
    except PermissionError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc
    except OSError as exc:
        raise AppMetadataRecoveryError(PERMISSION_DENIED) from exc


def _chmod(path: Path, mode: int) -> None:
    if os.name == "posix":
        os.chmod(path, mode)


def _fsync_file(path: Path) -> None:
    if os.name != "posix":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_dir(path: Path) -> None:
    if os.name != "posix":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _cleanup_or_partial_failure(tmp_dir: Path | None, original: AppMetadataRecoveryError) -> None:
    if tmp_dir is None or not tmp_dir.exists():
        return
    try:
        shutil.rmtree(tmp_dir)
    except OSError as exc:
        raise AppMetadataRecoveryError(PARTIAL_CLEANUP_FAILURE) from exc
    raise original


def _cleanup_file_or_partial_failure(path: Path, original: AppMetadataRecoveryError) -> None:
    if not path.exists() and not path.is_symlink():
        return
    try:
        path.unlink()
    except OSError as exc:
        raise AppMetadataRecoveryError(PARTIAL_CLEANUP_FAILURE) from exc
    raise original


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
