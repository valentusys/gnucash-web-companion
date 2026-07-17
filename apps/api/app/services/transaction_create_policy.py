"""Effective policy checks for #59 product transaction CREATE."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
import re
import sqlite3
import stat
from typing import Any
from urllib.parse import quote

import piecash
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Book, User
from app.services.book_access import BookAccessService
from app.services.book_preflight import (
    BookPreflightError,
    SQLITE_MAGIC,
    SourceIdentity,
    _open_source_file_for_full_probe,
    _verify_pinned_source_identity_unchanged,
    _verify_source_identity_unchanged,
)

_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


@dataclass(frozen=True)
class TransactionCreatePolicy:
    confirm_allowed: bool
    blocked_codes: tuple[str, ...]
    role: str | None
    deployment_writes_enabled: bool
    book_enabled: bool
    recovery_required: bool
    create_generation: int


@dataclass(frozen=True)
class TransactionCreateSourceEvidence:
    identity: SourceIdentity
    versions: dict[str, int]
    base_currency: str | None


@dataclass(frozen=True)
class TransactionCreatePinnedSource:
    identity: SourceIdentity
    versions: dict[str, int]
    base_currency: str | None
    fd_path: str
    roots: tuple[Any, ...]
    _fd: int

    def verify_current(self) -> None:
        """Fail if either the pinned descriptor or configured path identity changed."""

        _verify_pinned_source_identity_unchanged(self.identity, self._fd)
        _verify_source_identity_unchanged(self.identity, list(self.roots))

    def verify_same_file_after_write(self) -> None:
        """Fail if the descriptor/path no longer reference the same regular file.

        Size and mtime are allowed to change after the authorized CREATE itself;
        device/inode and regular-file status must remain stable.
        """

        fd_stat = os.fstat(self._fd)
        path_stat = os.stat(self.identity.canonical_path, follow_symlinks=False)
        if (
            not stat.S_ISREG(fd_stat.st_mode)
            or not stat.S_ISREG(path_stat.st_mode)
            or int(fd_stat.st_dev) != int(path_stat.st_dev)
            or int(fd_stat.st_ino) != int(path_stat.st_ino)
        ):
            raise BookPreflightError("source_changed")


def _health_safe_code(book: Book) -> str:
    snapshot = getattr(book, "health_snapshot", None)
    if snapshot is None:
        return "not_checked"
    return str(getattr(snapshot, "safe_code", "not_checked") or "not_checked")


def _is_local_sqlite_book(book: Book) -> bool:
    storage_type = str(getattr(book, "storage_type", "") or "").lower()
    uri_or_path = str(getattr(book, "uri_or_path", "") or "")
    return storage_type == "sqlite" and "://" not in uri_or_path and bool(uri_or_path.strip())


def _base_currency_supported(book: Book) -> bool:
    currency = str(getattr(book, "base_currency", "") or "").upper()
    return bool(_CURRENCY_RE.fullmatch(currency))


def _sqlite_uri(path: str) -> str:
    return f"file:{quote(path, safe='/')}?mode=ro"


def _read_source_versions(canonical_path: str) -> dict[str, int]:
    versions: dict[str, int] = {}
    with sqlite3.connect(_sqlite_uri(canonical_path), uri=True) as conn:
        conn.execute("pragma query_only = on")
        for table_name, table_version in conn.execute(
            "select table_name, table_version from versions where table_name in ('Gnucash', 'Gnucash-Resave')"
        ).fetchall():
            try:
                versions[str(table_name)] = int(table_version)
            except (TypeError, ValueError):
                continue
    return versions


def _read_source_base_currency(canonical_path: str) -> str | None:
    book_handle: Any | None = None
    try:
        book_handle = piecash.open_book(canonical_path, readonly=True)
        commodity = getattr(book_handle, "default_currency", None)
        mnemonic = getattr(commodity, "mnemonic", None)
        return str(mnemonic).upper() if mnemonic else None
    finally:
        if book_handle is not None:
            close = getattr(book_handle, "close", None)
            if callable(close):
                close()


def inspect_transaction_create_source(book: Book, settings: Settings) -> TransactionCreateSourceEvidence | None:
    """Return live source identity/version/currency evidence when safely available.

    Synthetic tests and legacy metadata can point outside configured book roots;
    those cases return ``None`` so existing cached-health gates remain in charge.
    Real product CREATE flows with allowed local SQLite sources get fresh identity,
    schema-version, and default-currency material for token fingerprints.
    """

    try:
        with open_transaction_create_source(book, settings) as pinned_source:
            versions = dict(pinned_source.versions)
            base_currency = pinned_source.base_currency
            identity = pinned_source.identity
    except (BookPreflightError, OSError, sqlite3.DatabaseError, Exception):
        return None
    return TransactionCreateSourceEvidence(
        identity=identity,
        versions=versions,
        base_currency=base_currency,
    )


@contextmanager
def open_transaction_create_source(book: Book, settings: Settings, *, writable: bool = False):
    """Yield descriptor-pinned source evidence for the whole CREATE attempt.

    The yielded ``fd_path`` is the only path the write-authorizing flow should
    open. ``verify_current`` checks both the open descriptor and the registered
    beneath-root path, so replaced-inode/symlink races fail closed instead of
    falling back to cached metadata or reopening the configured path.
    """

    raw_path = str(getattr(book, "uri_or_path", "") or "").strip()
    if not raw_path or "://" in raw_path:
        raise BookPreflightError("unsupported_source")
    with _open_source_file_for_full_probe(raw_path, settings, writable=writable) as inspection:
        if inspection.magic != SQLITE_MAGIC:
            raise BookPreflightError("unsupported_format")
        _verify_pinned_source_identity_unchanged(inspection.identity, inspection.fd)
        versions = _read_source_versions(inspection.fd_path)
        _verify_pinned_source_identity_unchanged(inspection.identity, inspection.fd)
        base_currency = _read_source_base_currency(inspection.fd_path)
        pinned_source = TransactionCreatePinnedSource(
            identity=inspection.identity,
            versions=versions,
            base_currency=base_currency,
            fd_path=inspection.fd_path,
            roots=inspection.roots,
            _fd=inspection.fd,
        )
        pinned_source.verify_current()
        yield pinned_source


def validate_transaction_create_enablement_for_admin(book: Book, settings: Settings) -> tuple[str, ...]:
    """Return blocking codes for admin enabling of per-book CREATE.

    Enabling requires cached health plus a live descriptor-pinned compatible
    source/base-currency check when deployment writes are on.
    """

    blocked: list[str] = []
    if not settings.gnucash_writes_enabled:
        blocked.append("CREATE_DEPLOYMENT_DISABLED")
    if bool(getattr(book, "is_archived", False)) or not bool(getattr(book, "is_enabled", True)):
        blocked.append("CREATE_BOOK_DISABLED")
    if not _is_local_sqlite_book(book):
        blocked.append("UNSUPPORTED_COMMODITY")
    if _health_safe_code(book) != "ready":
        blocked.append("PREVIEW_STALE")
    if not _base_currency_supported(book):
        blocked.append("UNSUPPORTED_COMMODITY")
    source_evidence = inspect_transaction_create_source(book, settings)
    if settings.gnucash_writes_enabled and source_evidence is None:
        blocked.append("PREVIEW_STALE")
    if source_evidence is not None and source_evidence.base_currency:
        registered_currency = str(getattr(book, "base_currency", "") or "").upper()
        if source_evidence.base_currency.upper() != registered_currency:
            blocked.append("COMMODITY_MISMATCH")
    if bool(getattr(book, "transaction_create_recovery_required", False)):
        blocked.append("CREATE_RECOVERY_REQUIRED")
    return tuple(dict.fromkeys(blocked))


def evaluate_transaction_create_policy(
    book: Book,
    user: User,
    session: Session,
    settings: Settings,
) -> TransactionCreatePolicy:
    """Evaluate effective preview/confirm policy without touching GnuCash data."""

    role = BookAccessService(session).get_role(user, book)
    blocked: list[str] = []
    if not bool(getattr(user, "is_enabled", True)):
        blocked.append("CREATE_PERMISSION_DENIED")
    if role not in {"owner", "editor"}:
        blocked.append("CREATE_PERMISSION_DENIED")
    if not settings.gnucash_writes_enabled:
        blocked.append("CREATE_DEPLOYMENT_DISABLED")
    if not bool(getattr(book, "transaction_create_enabled", False)):
        blocked.append("CREATE_BOOK_DISABLED")
    if bool(getattr(book, "is_archived", False)) or not bool(getattr(book, "is_enabled", True)):
        blocked.append("CREATE_BOOK_DISABLED")
    if not _is_local_sqlite_book(book) or not _base_currency_supported(book):
        blocked.append("UNSUPPORTED_COMMODITY")
    if _health_safe_code(book) != "ready":
        blocked.append("PREVIEW_STALE")
    if bool(getattr(book, "transaction_create_recovery_required", False)):
        blocked.append("CREATE_RECOVERY_REQUIRED")

    ordered_unique = tuple(dict.fromkeys(blocked))
    return TransactionCreatePolicy(
        confirm_allowed=not ordered_unique,
        blocked_codes=ordered_unique,
        role=role,
        deployment_writes_enabled=bool(settings.gnucash_writes_enabled),
        book_enabled=bool(getattr(book, "transaction_create_enabled", False)),
        recovery_required=bool(getattr(book, "transaction_create_recovery_required", False)),
        create_generation=int(getattr(book, "transaction_create_generation", 1) or 1),
    )
