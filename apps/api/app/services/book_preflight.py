"""Path-safe GnuCash SQLite source preflight service."""

from __future__ import annotations

import base64
import errno
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import stat
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterator
from urllib.parse import quote

import piecash
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Book
from app.schemas.books import (
    BookCapabilitiesDTO,
    BookPreflightReadCountersDTO,
    BookPreflightRequest,
    BookPreflightResponse,
    BookProblemDTO,
    BookSectionStatusDTO,
)

SQLITE_MAGIC = b"SQLite format 3\x00"
REQUIRED_GNUCASH_TABLES = frozenset(
    {"versions", "books", "accounts", "transactions", "splits", "commodities"}
)
REQUEST_PATH_MAX_LENGTH = 1024
TOKEN_VERSION = 1

_PROBLEM_MESSAGES: dict[str, tuple[str, bool]] = {
    "invalid_path": ("The supplied book path is not an accepted absolute POSIX path.", False),
    "invalid_allowed_root_config": ("Configured allowed book roots are not valid local directories.", False),
    "unsupported_source": ("Only an existing server-side local SQLite GnuCash file is supported.", False),
    "outside_allowed_roots": ("The supplied book path is outside configured allowed roots.", False),
    "symlink_forbidden": ("Symlinked book path components are not supported.", False),
    "missing_file": ("The configured book file was not found from this runtime.", True),
    "not_regular_file": ("The supplied book source is not a regular file.", False),
    "permission_denied": ("The book file could not be opened read-only by this runtime.", True),
    "unsupported_format": ("Only GnuCash SQL SQLite files are supported.", False),
    "invalid_gnucash_schema": ("The SQLite file does not contain required GnuCash SQL markers.", False),
    "source_changed": ("The book source changed while it was being checked; retry the preflight.", True),
    "open_failed": ("The book could not be opened read-only as a GnuCash SQL book.", False),
    "pinned_source_unavailable": (
        "A safe read-only source descriptor probe is not available on this runtime.",
        False,
    ),
}


class BookPreflightError(Exception):
    """Path-safe preflight failure."""

    def __init__(self, code: str):
        message, retryable = _PROBLEM_MESSAGES[code]
        self.problem = BookProblemDTO(code=code, message=message, retryable=retryable)
        super().__init__(code)


@dataclass(frozen=True)
class SourceIdentity:
    canonical_path: str
    canonical_path_hash: str
    st_dev: int
    st_ino: int
    st_size: int
    st_mtime_ns: int

    def hmac_payload(self) -> dict[str, Any]:
        return {
            "canonical_path_hash": self.canonical_path_hash,
            "st_dev": self.st_dev,
            "st_ino": self.st_ino,
            "st_size": self.st_size,
            "st_mtime_ns": self.st_mtime_ns,
        }


@dataclass(frozen=True)
class SourceInspection:
    identity: SourceIdentity
    magic: bytes


@dataclass(frozen=True)
class _PinnedSourceInspection:
    identity: SourceIdentity
    magic: bytes
    fd: int
    fd_path: str
    roots: tuple[Path, ...]


@dataclass
class _SQLiteProbeResult:
    accounts: BookSectionStatusDTO
    transactions: BookSectionStatusDTO
    reports: BookSectionStatusDTO
    sqlite_query_count: int


@dataclass(frozen=True)
class BookHealthProbeResult:
    """Path-safe successful read-only health probe result for one source."""

    identity: SourceIdentity
    source_status: BookSectionStatusDTO
    open_status: BookSectionStatusDTO
    accounts: BookSectionStatusDTO
    transactions: BookSectionStatusDTO
    reports: BookSectionStatusDTO
    checked_at: datetime
    read_counters: BookPreflightReadCountersDTO


def canonical_path_hash(canonical_path: str) -> str:
    """Return the private deterministic canonical-path hash stored in app metadata."""

    return hashlib.sha256(canonical_path.encode("utf-8")).hexdigest()


def _problem(code: str) -> BookPreflightError:
    return BookPreflightError(code)


def _stable_identity(canonical_path: str, file_stat: os.stat_result) -> SourceIdentity:
    return SourceIdentity(
        canonical_path=canonical_path,
        canonical_path_hash=canonical_path_hash(canonical_path),
        st_dev=int(file_stat.st_dev),
        st_ino=int(file_stat.st_ino),
        st_size=int(file_stat.st_size),
        st_mtime_ns=int(file_stat.st_mtime_ns),
    )


def _same_file_stat(left: os.stat_result, right: os.stat_result) -> bool:
    return (
        int(left.st_dev) == int(right.st_dev)
        and int(left.st_ino) == int(right.st_ino)
        and int(left.st_size) == int(right.st_size)
        and int(left.st_mtime_ns) == int(right.st_mtime_ns)
    )


def _identity_matches_stat(identity: SourceIdentity, file_stat: os.stat_result) -> bool:
    return (
        int(identity.st_dev) == int(file_stat.st_dev)
        and int(identity.st_ino) == int(file_stat.st_ino)
        and int(identity.st_size) == int(file_stat.st_size)
        and int(identity.st_mtime_ns) == int(file_stat.st_mtime_ns)
    )


def _validate_absolute_request_path(raw_path: str) -> Path:
    value = str(raw_path or "")
    if (
        not value
        or len(value) > REQUEST_PATH_MAX_LENGTH
        or "\x00" in value
        or value.startswith("~")
        or "$" in value
        or "${" in value
        or "\\" in value
    ):
        raise _problem("invalid_path")
    if "://" in value or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        raise _problem("unsupported_source")
    if any(part in {".", ".."} for part in value.split("/")):
        raise _problem("invalid_path")
    parsed = PurePosixPath(value)
    if not parsed.is_absolute():
        raise _problem("invalid_path")
    if any(part in {".", ".."} for part in parsed.parts):
        raise _problem("invalid_path")
    return Path(value)


def _allowed_roots(settings: Settings) -> list[Path]:
    roots: list[Path] = []
    for root in settings.gnucash_book_allowed_roots:
        root_text = str(root or "")
        if (
            not root_text
            or "\x00" in root_text
            or root_text.startswith("~")
            or "$" in root_text
            or "${" in root_text
            or "\\" in root_text
            or "://" in root_text
            or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", root_text)
        ):
            raise _problem("invalid_allowed_root_config")
        parsed = PurePosixPath(root_text)
        if not parsed.is_absolute() or any(part in {".", ".."} for part in parsed.parts):
            raise _problem("invalid_allowed_root_config")
        root_path = Path(root_text)
        current = Path(root_path.anchor or "/")
        try:
            for part in root_path.parts[1:]:
                current = current / part
                if current.is_symlink():
                    raise _problem("invalid_allowed_root_config")
            resolved = root_path.resolve(strict=True)
            root_stat = os.stat(resolved, follow_symlinks=False)
        except BookPreflightError:
            raise
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise _problem("invalid_allowed_root_config") from exc
        if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
            raise _problem("invalid_allowed_root_config")
        roots.append(resolved)
    if not roots:
        raise _problem("invalid_allowed_root_config")
    return roots


def _is_under_allowed_root(candidate: Path, roots: list[Path]) -> bool:
    return _matching_allowed_root(candidate, roots) is not None


def _matching_allowed_root(candidate: Path, roots: list[Path]) -> Path | None:
    candidate_text = os.fspath(candidate)
    best_match: Path | None = None
    for root in roots:
        try:
            if os.path.commonpath([candidate_text, os.fspath(root)]) == os.fspath(root):
                if best_match is None or len(root.parts) > len(best_match.parts):
                    best_match = root
        except ValueError:
            continue
    return best_match


def _reject_symlink_components(path: Path) -> None:
    current = Path(path.anchor or "/")
    for part in path.parts[1:]:
        current = current / part
        try:
            if current.is_symlink():
                raise _problem("symlink_forbidden")
        except OSError as exc:
            if exc.errno in {errno.EACCES, errno.EPERM}:
                raise _problem("permission_denied") from exc
            raise


def _require_no_follow_support() -> None:
    if os.name != "posix" or getattr(os, "O_NOFOLLOW", 0) == 0:
        raise _problem("pinned_source_unavailable")


def _require_pinned_fd_primitives() -> None:
    _require_no_follow_support()
    if not Path("/proc/self/fd").is_dir():
        raise _problem("pinned_source_unavailable")


def _open_allowed_root_fd(root: Path) -> int:
    _require_no_follow_support()
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        fd = os.open(root, flags)
    except OSError as exc:
        raise _problem("invalid_allowed_root_config") from exc
    try:
        root_stat = os.fstat(fd)
        if not stat.S_ISDIR(root_stat.st_mode):
            raise _problem("invalid_allowed_root_config")
    except Exception:
        os.close(fd)
        raise
    return fd


def _raise_component_open_error(exc: OSError, parent_fd: int, part: str) -> None:
    if exc.errno == errno.ELOOP:
        raise _problem("symlink_forbidden") from exc
    if exc.errno == errno.ENOTDIR:
        try:
            component_stat = os.stat(part, dir_fd=parent_fd, follow_symlinks=False)
        except OSError:
            raise _problem("missing_file") from exc
        if stat.S_ISLNK(component_stat.st_mode):
            raise _problem("symlink_forbidden") from exc
        raise _problem("missing_file") from exc
    if exc.errno in {errno.EACCES, errno.EPERM}:
        raise _problem("permission_denied") from exc
    if exc.errno == errno.ENOENT:
        raise _problem("missing_file") from exc
    raise _problem("permission_denied") from exc


def _open_parent_directory_no_follow(canonical_path: Path, root: Path) -> tuple[int, str]:
    try:
        relative = canonical_path.relative_to(root)
    except ValueError as exc:
        raise _problem("outside_allowed_roots") from exc
    if not relative.parts:
        raise _problem("not_regular_file")

    current_fd = _open_allowed_root_fd(root)
    dir_flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        for part in relative.parts[:-1]:
            try:
                next_fd = os.open(part, dir_flags, dir_fd=current_fd)
            except OSError as exc:
                _raise_component_open_error(exc, current_fd, part)
                raise AssertionError("unreachable component-open error path") from exc
            try:
                component_stat = os.fstat(next_fd)
                if not stat.S_ISDIR(component_stat.st_mode):
                    os.close(next_fd)
                    raise _problem("missing_file")
            except Exception:
                raise
            os.close(current_fd)
            current_fd = next_fd
        return current_fd, relative.parts[-1]
    except Exception:
        os.close(current_fd)
        raise


def _regular_file_stat_at(parent_fd: int, leaf_name: str) -> os.stat_result:
    try:
        file_stat = os.stat(leaf_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError as exc:
        raise _problem("missing_file") from exc
    except NotADirectoryError as exc:
        raise _problem("missing_file") from exc
    except PermissionError as exc:
        raise _problem("permission_denied") from exc

    if stat.S_ISLNK(file_stat.st_mode):
        raise _problem("symlink_forbidden")
    if not stat.S_ISREG(file_stat.st_mode):
        raise _problem("not_regular_file")
    return file_stat


def _open_regular_file_no_follow(
    canonical_path: Path,
    roots: list[Path],
) -> tuple[int, bytes, os.stat_result]:
    root = _matching_allowed_root(canonical_path, roots)
    if root is None:
        raise _problem("outside_allowed_roots")

    parent_fd, leaf_name = _open_parent_directory_no_follow(canonical_path, root)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd: int | None = None
    try:
        before = _regular_file_stat_at(parent_fd, leaf_name)
        fd = os.open(leaf_name, flags, dir_fd=parent_fd)
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            raise _problem("not_regular_file")
        if not _same_file_stat(before, opened):
            raise _problem("source_changed")
        magic = os.read(fd, len(SQLITE_MAGIC))
        os.lseek(fd, 0, os.SEEK_SET)
        after = _regular_file_stat_at(parent_fd, leaf_name)
        if not _same_file_stat(opened, after):
            raise _problem("source_changed")
        return fd, magic, opened
    except OSError as exc:
        if fd is not None:
            os.close(fd)
            fd = None
        if exc.errno == errno.ELOOP:
            raise _problem("symlink_forbidden") from exc
        if exc.errno in {errno.EACCES, errno.EPERM}:
            raise _problem("permission_denied") from exc
        if exc.errno in {errno.ENOENT, errno.ENOTDIR}:
            raise _problem("missing_file") from exc
        raise _problem("permission_denied") from exc
    except Exception:
        if fd is not None:
            os.close(fd)
            fd = None
        raise
    finally:
        os.close(parent_fd)


def _read_regular_file_magic_no_follow(
    canonical_path: Path,
    roots: list[Path],
) -> tuple[bytes, os.stat_result]:
    fd, magic, opened = _open_regular_file_no_follow(canonical_path, roots)
    try:
        return magic, opened
    finally:
        os.close(fd)


def _verify_pinned_source_identity_unchanged(identity: SourceIdentity, fd: int) -> None:
    try:
        current = os.fstat(fd)
    except OSError as exc:
        raise _problem("source_changed") from exc
    if not stat.S_ISREG(current.st_mode) or not _identity_matches_stat(identity, current):
        raise _problem("source_changed")


def _pinned_fd_path(fd: int, identity: SourceIdentity) -> str:
    _require_pinned_fd_primitives()
    fd_path = Path("/proc/self/fd") / str(fd)
    try:
        fd_stat = os.fstat(fd)
        proc_stat = os.stat(fd_path)
    except OSError as exc:
        raise _problem("pinned_source_unavailable") from exc
    if (
        not stat.S_ISREG(fd_stat.st_mode)
        or not _identity_matches_stat(identity, fd_stat)
        or not _same_file_stat(fd_stat, proc_stat)
    ):
        raise _problem("pinned_source_unavailable")
    return os.fspath(fd_path)


@contextmanager
def _open_source_file_for_full_probe(
    raw_path: str, settings: Settings
) -> Iterator[_PinnedSourceInspection]:
    request_path = _validate_absolute_request_path(raw_path)
    roots = _allowed_roots(settings)
    if not _is_under_allowed_root(request_path, roots):
        raise _problem("outside_allowed_roots")
    _reject_symlink_components(request_path)
    canonical_path = request_path.resolve(strict=False)
    if not _is_under_allowed_root(canonical_path, roots):
        raise _problem("outside_allowed_roots")

    fd: int | None = None
    try:
        fd, magic, file_stat = _open_regular_file_no_follow(canonical_path, roots)
        identity = _stable_identity(str(canonical_path), file_stat)
        fd_path = _pinned_fd_path(fd, identity)
        yield _PinnedSourceInspection(
            identity=identity,
            magic=magic,
            fd=fd,
            fd_path=fd_path,
            roots=tuple(roots),
        )
    finally:
        if fd is not None:
            os.close(fd)


def _verify_source_identity_unchanged(identity: SourceIdentity, roots: list[Path]) -> None:
    canonical_path = Path(identity.canonical_path)
    root = _matching_allowed_root(canonical_path, roots)
    if root is None:
        raise _problem("outside_allowed_roots")
    parent_fd, leaf_name = _open_parent_directory_no_follow(canonical_path, root)
    try:
        current = _regular_file_stat_at(parent_fd, leaf_name)
    finally:
        os.close(parent_fd)
    if not _identity_matches_stat(identity, current):
        raise _problem("source_changed")


def inspect_source_file(raw_path: str, settings: Settings) -> SourceInspection:
    """Inspect only path safety and file identity, without opening SQLite/piecash."""

    request_path = _validate_absolute_request_path(raw_path)
    roots = _allowed_roots(settings)
    if not _is_under_allowed_root(request_path, roots):
        raise _problem("outside_allowed_roots")
    _reject_symlink_components(request_path)
    canonical_path = request_path.resolve(strict=False)
    if not _is_under_allowed_root(canonical_path, roots):
        raise _problem("outside_allowed_roots")
    magic, file_stat = _read_regular_file_magic_no_follow(canonical_path, roots)
    identity = _stable_identity(str(canonical_path), file_stat)
    return SourceInspection(identity=identity, magic=magic)


def canonicalize_existing_book_path(raw_path: str, settings: Settings) -> SourceIdentity | None:
    """Best-effort migration helper: return safe canonical identity or None."""

    try:
        inspection = inspect_source_file(raw_path, settings)
    except BookPreflightError:
        return None
    if inspection.magic != SQLITE_MAGIC:
        return None
    return inspection.identity


def _sqlite_uri(path: str) -> str:
    return f"file:{quote(path, safe='/')}?mode=ro"


def _section_status(section: str, row: Any | None) -> BookSectionStatusDTO:
    if row is None:
        return BookSectionStatusDTO(
            status="empty",
            safe_code=f"{section}_empty",
            message=f"The {section} section is readable and currently empty.",
        )
    return BookSectionStatusDTO(
        status="ready",
        safe_code=f"{section}_ready",
        message=f"The {section} section is readable with a bounded probe.",
    )


def _verify_sqlite_gnucash_schema(canonical_path: str) -> _SQLiteProbeResult:
    query_count = 0
    try:
        with sqlite3.connect(_sqlite_uri(canonical_path), uri=True) as conn:
            conn.execute("pragma query_only = on")
            required = tuple(sorted(REQUIRED_GNUCASH_TABLES))
            placeholders = ", ".join("?" for _ in required)
            rows = conn.execute(
                f"select name from sqlite_master where type = 'table' and name in ({placeholders})",
                required,
            ).fetchall()
            query_count += 1
            table_names = {str(row[0]) for row in rows}
            if not REQUIRED_GNUCASH_TABLES.issubset(table_names):
                raise _problem("invalid_gnucash_schema")
            version_marker = conn.execute(
                "select 1 from versions where table_name in ('Gnucash', 'Gnucash-Resave') limit 1"
            ).fetchone()
            query_count += 1
            if version_marker is None:
                raise _problem("invalid_gnucash_schema")
            account_row = conn.execute("select 1 from accounts limit 1").fetchone()
            query_count += 1
            transaction_row = conn.execute("select 1 from transactions limit 1").fetchone()
            query_count += 1
            report_row = conn.execute("select 1 from books limit 1").fetchone()
            query_count += 1
    except BookPreflightError:
        raise
    except sqlite3.DatabaseError as exc:
        raise _problem("invalid_gnucash_schema") from exc

    return _SQLiteProbeResult(
        accounts=_section_status("accounts", account_row),
        transactions=_section_status("transactions", transaction_row),
        reports=BookSectionStatusDTO(
            status="ready" if report_row is not None else "empty",
            safe_code="reports_ready" if report_row is not None else "reports_empty",
            message="Report readiness metadata is readable with a bounded probe.",
        ),
        sqlite_query_count=query_count,
    )


def _open_piecash_readonly_once(canonical_path: str) -> None:
    book = None
    try:
        book = piecash.open_book(canonical_path, readonly=True)
    except Exception as exc:  # pragma: no cover - piecash exception classes vary
        raise _problem("open_failed") from exc
    finally:
        if book is not None:
            close = getattr(book, "close", None)
            if callable(close):
                close()


def _ready_status(code: str, message: str) -> BookSectionStatusDTO:
    return BookSectionStatusDTO(status="ready", safe_code=code, message=message)


def run_book_health_probe(raw_path: str, settings: Settings) -> BookHealthProbeResult:
    """Run the bounded read-only source/schema/piecash probe used by lifecycle routes.

    The probe never writes app metadata and never copies/modifies/deletes the
    source. It performs bounded SQLite schema reads and exactly one piecash
    read-only open on success.
    """

    with _open_source_file_for_full_probe(raw_path, settings) as inspection:
        if inspection.magic != SQLITE_MAGIC:
            raise _problem("unsupported_format")
        _verify_pinned_source_identity_unchanged(inspection.identity, inspection.fd)
        sqlite_probe = _verify_sqlite_gnucash_schema(inspection.fd_path)
        _verify_pinned_source_identity_unchanged(inspection.identity, inspection.fd)
        _open_piecash_readonly_once(inspection.fd_path)
        _verify_pinned_source_identity_unchanged(inspection.identity, inspection.fd)
        _verify_source_identity_unchanged(inspection.identity, list(inspection.roots))
        return BookHealthProbeResult(
            identity=inspection.identity,
            source_status=_ready_status(
                "source_ready",
                "The source is an allowed local regular file and was opened read-only without following symlinks.",
            ),
            open_status=_ready_status(
                "piecash_readonly_open_ready",
                "The book opened once with piecash in read-only mode.",
            ),
            accounts=sqlite_probe.accounts,
            transactions=sqlite_probe.transactions,
            reports=sqlite_probe.reports,
            checked_at=datetime.now(timezone.utc),
            read_counters=BookPreflightReadCountersDTO(
                sqlite_query_count=sqlite_probe.sqlite_query_count,
                piecash_open_count=1,
                account_materialization_count=0,
                transaction_materialization_count=0,
            ),
        )


def _registration_status(session: Session | None, identity: SourceIdentity) -> BookSectionStatusDTO:
    if session is None:
        return BookSectionStatusDTO(
            status="available",
            safe_code="registration_not_checked",
            message="Registration availability was not checked in app metadata.",
        )
    existing = (
        session.query(Book.id)
        .filter(
            Book.canonical_path_hash == identity.canonical_path_hash,
            Book.is_archived.is_(False),
        )
        .first()
    )
    if existing is not None:
        return BookSectionStatusDTO(
            status="already_registered",
            safe_code="duplicate_canonical_path",
            message="A book with the same canonical source is already registered.",
        )
    return BookSectionStatusDTO(
        status="available",
        safe_code="registration_available",
        message="No active app metadata book uses this canonical source.",
    )


def _base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _preflight_token(
    *,
    settings: Settings,
    request: BookPreflightRequest,
    identity: SourceIdentity,
    checked_at_epoch: int,
) -> str:
    ttl = max(60, min(int(settings.gnucash_preflight_token_ttl_seconds), 3600))
    expires_at = checked_at_epoch + ttl
    nonce = secrets.token_urlsafe(18)
    signed_payload = {
        "v": TOKEN_VERSION,
        "exp": expires_at,
        "nonce": nonce,
        "request": {
            "name": request.name,
            "storage_type": request.storage_type,
            "base_currency": request.base_currency,
            "make_default": request.make_default,
        },
        "source": identity.hmac_payload(),
    }
    message = json.dumps(signed_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    secret = settings.jwt_secret.encode("utf-8")
    signature = hmac.new(secret, message, hashlib.sha256).digest()
    return f"{_base64url(message)}.{_base64url(signature)}"


def decode_preflight_token(
    token: str,
    settings: Settings,
    *,
    now_epoch: int | None = None,
) -> dict[str, Any] | None:
    """Verify and decode an opaque preflight token for future registration.

    The signed payload excludes raw source paths and source filenames. It binds
    normalized request fields to canonical source hash/identity and expiry.
    """

    try:
        parts = str(token).split(".")
        if len(parts) != 2:
            return None
        payload_part, signature_part = parts
        if not payload_part or not signature_part:
            return None
        payload_bytes = _base64url_decode(payload_part)
        supplied_signature = _base64url_decode(signature_part)
    except Exception:
        return None
    if _base64url(payload_bytes) != payload_part or _base64url(supplied_signature) != signature_part:
        return None

    expected_signature = hmac.new(
        settings.jwt_secret.encode("utf-8"), payload_bytes, hashlib.sha256
    ).digest()
    if not hmac.compare_digest(supplied_signature, expected_signature):
        return None

    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("v") != TOKEN_VERSION:
        return None
    expires_at = payload.get("exp")
    if not isinstance(expires_at, int):
        return None
    if (int(time.time()) if now_epoch is None else int(now_epoch)) >= expires_at:
        return None
    if not isinstance(payload.get("request"), dict) or not isinstance(payload.get("source"), dict):
        return None
    return payload


class BookPreflightService:
    """Run idempotent preflight checks without writing app metadata or source files."""

    def __init__(self, settings: Settings, session: Session | None = None):
        self.settings = settings
        self.session = session

    def run(self, request: BookPreflightRequest) -> BookPreflightResponse:
        probe = run_book_health_probe(request.uri_or_path, self.settings)
        checked_at_epoch = int(time.time())
        registration_status = _registration_status(self.session, probe.identity)
        can_register = registration_status.status == "available"
        token = _preflight_token(
            settings=self.settings,
            request=request,
            identity=probe.identity,
            checked_at_epoch=checked_at_epoch,
        )
        return BookPreflightResponse(
            status="ready",
            format="gnucash_sqlite",
            preflight_token=token,
            registration_status=registration_status,
            source_status=probe.source_status,
            open_status=probe.open_status,
            accounts=probe.accounts,
            transactions=probe.transactions,
            reports=probe.reports,
            capabilities=BookCapabilitiesDTO(
                read_only=True,
                can_register_metadata=can_register,
                can_open_accounts=probe.accounts.status in {"ready", "empty"},
                can_open_transactions=probe.transactions.status in {"ready", "empty"},
                can_open_reports=probe.reports.status in {"ready", "empty"},
                can_upload=False,
                can_edit=False,
                can_delete=False,
                can_edit_gnucash=False,
                can_delete_source=False,
            ),
            checked_at=probe.checked_at.isoformat(),
            message="GnuCash SQLite source preflight completed without source or metadata writes.",
            read_counters=probe.read_counters,
        )
