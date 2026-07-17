"""Book-aware books and accounts API router."""

from __future__ import annotations

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.models import AuditLog, Book, BookHealthSnapshot, User, UserBookAccess, WriteAlphaTransactionOwnership
from app.routers.auth import get_current_user, get_db
from app.schemas.books import BookHealthDTO, BookPreflightRequest, BookPreflightResponse, BookPublicDTO
from app.services.book_access import AccessDenied, BookAccessService
from app.services.book_preflight import (
    BookPreflightError,
    BookPreflightService,
    BookHealthProbeResult,
    decode_preflight_token,
    run_book_health_probe,
)
from app.services.book_registry import BookRegistryService
from app.services.gnucash_book import GnuCashBookService
from app.services.account_explorer import (
    AccountExplorerError,
    build_account_activity_query,
    build_account_explorer_query,
    normalize_account_guid,
)
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
)
from app.services.transaction_create_audit import serialize_transaction_create_audit_payload
from app.services.transaction_create_errors import raise_transaction_create_error
from app.services.transaction_create_policy import validate_transaction_create_enablement_for_admin

router = APIRouter(prefix="/books", tags=["books"])

UNSUPPORTED_MVP_MANAGEMENT_ACTIONS = [
    "book_upload",
    "book_file_delete",
    "book_file_edit",
]

ADMIN_SAFE_MANAGEMENT_ACTIONS = [
    "set_default",
    "remove_from_registry",
]

SAFE_OPERATOR_NEXT_ACTIONS = {
    "available": [
        "Open a read-only view from this page.",
        "Use GnuCash Desktop for any edits.",
    ],
    "not_configured": [
        "Check the app metadata database and deployment configuration for this book entry.",
        "Do not upload or browse GnuCash files from the web UI; configure storage from the host side.",
    ],
    "missing_file": [
        "Verify the configured book is mounted on the host/container.",
        "Check the app metadata database and deployment volumes without uploading or browsing files from the web UI.",
    ],
    "invalid_gnucash_schema": [
        "Verify the configured file is a copied/test GnuCash SQLite book mounted from the host.",
        "Do not upload or browse private books from the web UI; fix the host-side metadata or mount.",
    ],
    "remote_or_unchecked": [
        "Validate the configured storage from the host before relying on this read-only view.",
        "Use GnuCash Desktop as the authoritative editor.",
    ],
    "disabled": [
        "Run source preflight again from an admin session before opening this book.",
        "Check allowed roots and mounted source files without exposing private paths in the UI.",
    ],
    "invalid_allowed_root_config": [
        "Fix the server-side allowed-root configuration before checking this book again.",
        "Do not expose or browse private file paths from the web UI.",
    ],
}

STATUS_SEVERITY = {
    "ready": "ok",
    "available": "ok",
    "not_checked": "warning",
    "remote_or_unchecked": "warning",
    "missing_file": "action_required",
    "not_configured": "action_required",
    "invalid_gnucash_schema": "action_required",
    "disabled": "action_required",
    "invalid_allowed_root_config": "action_required",
}

KNOWN_HEALTH_SAFE_CODES = frozenset(
    {
        "ready",
        "not_checked",
        "remote_or_unchecked",
        "missing_file",
        "not_configured",
        "invalid_path",
        "invalid_allowed_root_config",
        "unsupported_source",
        "outside_allowed_roots",
        "symlink_forbidden",
        "not_regular_file",
        "permission_denied",
        "unsupported_format",
        "invalid_gnucash_schema",
        "source_changed",
        "open_failed",
    }
)

READY_SECTION_STATUSES = frozenset({"ready", "empty"})

ACCESS_ROLE_COPY = {
    "owner": {
        "label": "Owner",
        "description": "Can open read-only views and review operator diagnostics for this independent book.",
    },
    "editor": {
        "label": "Editor",
        "description": "Can open read-only views; write-alpha remains disabled by default and separately gated.",
    },
    "viewer": {
        "label": "Viewer",
        "description": "Can open read-only views for this assigned independent book.",
    },
}


class BookRegistrationRequest(BaseModel):
    """Admin-only app metadata registration request.

    This registers an already-mounted local copied/test book in the app metadata
    database. It never uploads, copies, opens, or mutates GnuCash accounting data.
    """

    name: str = Field(min_length=1, max_length=256)
    storage_type: str = "sqlite"
    uri_or_path: str = Field(min_length=1, max_length=1024)
    base_currency: str | None = Field(default=None, max_length=16)
    make_default: bool = False
    preflight_token: str | None = Field(default=None, min_length=1, max_length=4096)

    @field_validator("name", "storage_type", "uri_or_path", mode="before")
    @classmethod
    def _strip_required_text(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("base_currency", mode="before")
    @classmethod
    def _normalize_base_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip().upper()
        return stripped or None


class BookPatchRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=256)
    base_currency: str | None = Field(default=None, min_length=1, max_length=16)

    @field_validator("name", mode="before")
    @classmethod
    def _strip_name(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("base_currency", mode="before")
    @classmethod
    def _normalize_base_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip().upper()
        return stripped or None


class BookEnableRequest(BaseModel):
    preflight_token: str = Field(min_length=1, max_length=4096)
    make_default: bool = False


class TransactionCreateSettingsPatchRequest(BaseModel):
    """Admin-only per-book transaction CREATE setting patch."""

    model_config = ConfigDict(extra="forbid")

    enabled: StrictBool


def require_admin_user(user: User) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required for book registry management.",
        )


_LIFECYCLE_PROBLEMS: dict[str, tuple[str, bool]] = {
    "missing_preflight_token": ("A fresh preflight token is required for this metadata lifecycle action.", False),
    "invalid_preflight_token": ("The supplied preflight token is invalid, expired, or tampered.", False),
    "preflight_request_mismatch": ("The request no longer matches the supplied preflight token.", False),
    "preflight_source_mismatch": ("The book source changed after preflight; repeat preflight before continuing.", True),
    "duplicate_canonical_path": ("A book with the same canonical source is already registered.", False),
    "book_not_enabled": ("Book metadata is disabled until a fresh successful preflight enables it.", True),
    "book_not_healthy": ("Book cached health is not ready; run a successful health recheck first.", True),
    "book_health_not_checked": ("Book cached health has not been verified yet.", True),
}


def _lifecycle_problem(code: str) -> dict[str, Any]:
    message, retryable = _LIFECYCLE_PROBLEMS[code]
    return {"code": code, "message": message, "retryable": retryable}


def _raise_lifecycle_problem(code: str, status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT) -> None:
    raise HTTPException(status_code=status_code, detail=_lifecycle_problem(code))


def _normalize_token_request_for_registration(body: BookRegistrationRequest) -> dict[str, Any]:
    return {
        "name": body.name.strip(),
        "storage_type": body.storage_type.strip().lower(),
        "base_currency": body.base_currency,
        "make_default": bool(body.make_default),
    }


def _normalize_token_request_for_book(book: Book, *, make_default: bool) -> dict[str, Any]:
    return {
        "name": str(book.name or "").strip(),
        "storage_type": str(book.storage_type or "").strip().lower(),
        "base_currency": str(book.base_currency).strip().upper() if book.base_currency else None,
        "make_default": bool(make_default),
    }


def _decode_required_preflight_token(token: str | None, settings: Settings) -> dict[str, Any]:
    if not token:
        _raise_lifecycle_problem("missing_preflight_token")
    token_value = str(token)
    payload = decode_preflight_token(token_value, settings)
    if payload is None:
        _raise_lifecycle_problem("invalid_preflight_token")
    assert payload is not None
    return payload


def _verify_preflight_bound_probe(
    *,
    raw_path: str,
    token: str | None,
    expected_request: dict[str, Any],
    settings: Settings,
) -> BookHealthProbeResult:
    payload = _decode_required_preflight_token(token, settings)
    if payload.get("request") != expected_request:
        _raise_lifecycle_problem("preflight_request_mismatch")
    try:
        probe = run_book_health_probe(raw_path, settings)
    except BookPreflightError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.problem.model_dump(),
        ) from exc
    if payload.get("source") != probe.identity.hmac_payload():
        _raise_lifecycle_problem("preflight_source_mismatch", status.HTTP_409_CONFLICT)
    return probe


def _reject_duplicate_canonical_registration(session: Session, canonical_hash: str) -> None:
    existing = (
        session.query(Book.id)
        .filter(Book.canonical_path_hash == canonical_hash, Book.is_archived.is_(False))
        .first()
    )
    if existing is not None:
        _raise_lifecycle_problem("duplicate_canonical_path", status.HTTP_409_CONFLICT)


def _safe_status_value(
    value: Any,
    default: str = "not_checked",
    *,
    allowed: frozenset[str] | None = None,
) -> str:
    if not isinstance(value, str):
        return default
    normalized = value.strip()
    if not normalized or len(normalized) > 64:
        return default
    if allowed is not None and normalized not in allowed:
        return default
    return normalized


def _ready_snapshot_is_well_formed(snapshot: BookHealthSnapshot) -> bool:
    return (
        _safe_status_value(getattr(snapshot, "source_status", None)) == "ready"
        and _safe_status_value(getattr(snapshot, "open_status", None)) == "ready"
        and _safe_status_value(
            getattr(snapshot, "accounts_status", None), allowed=READY_SECTION_STATUSES
        )
        in READY_SECTION_STATUSES
        and _safe_status_value(
            getattr(snapshot, "transactions_status", None), allowed=READY_SECTION_STATUSES
        )
        in READY_SECTION_STATUSES
        and _safe_status_value(
            getattr(snapshot, "reports_status", None), allowed=READY_SECTION_STATUSES
        )
        in READY_SECTION_STATUSES
    )


def _cached_health_safe_code(book: Book) -> str:
    snapshot = getattr(book, "health_snapshot", None)
    if snapshot is None:
        # Unit tests and pre-#56 in-memory rows may construct Book objects
        # directly without running metadata migrations. Never infer healthy
        # from absence: serialize as unchecked while preserving legacy read-only
        # route compatibility through the bounded service-layer open.
        return "not_checked"
    safe_code = _safe_status_value(
        getattr(snapshot, "safe_code", None),
        allowed=KNOWN_HEALTH_SAFE_CODES,
    )
    if safe_code == "ready" and not _ready_snapshot_is_well_formed(snapshot):
        return "not_checked"
    return safe_code


def _is_uri(value: str) -> bool:
    return "://" in value


def _sqlite_gnucash_shape_error(path: Path) -> str | None:
    """Return a path-redacted schema problem, or None when the target looks usable."""
    required_tables = {"versions", "books", "accounts", "transactions", "splits", "commodities"}
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as conn:
            rows = conn.execute(
                "select name from sqlite_master where type = 'table'"
            ).fetchall()
    except sqlite3.DatabaseError:
        return "Configured local book path is not a readable SQLite GnuCash book."

    table_names = {str(row[0]) for row in rows}
    if not required_tables.issubset(table_names):
        return "Configured local SQLite file does not look like a GnuCash book."
    return None


def _local_sqlite_gnucash_shape_is_valid(path: Path) -> bool:
    """Check read-only schema markers for legacy diagnostics without exposing path details."""
    return _sqlite_gnucash_shape_error(path) is None


def _legacy_uncached_storage_status_for(book: Book) -> str:
    """Classify pre-health-snapshot rows without opening through piecash."""
    if not bool((book.uri_or_path or "").strip()):
        return "not_configured"

    storage_type = (book.storage_type or "").lower()
    if storage_type == "sqlite" and not _is_uri(book.uri_or_path):
        path = Path(book.uri_or_path)
        exists = path.exists()
        should_validate_shape = path.name.endswith((".sqlite", ".sqlite3", ".gnucash.sqlite"))
        if exists and (not should_validate_shape or _local_sqlite_gnucash_shape_is_valid(path)):
            return "available"
        if exists:
            return "invalid_gnucash_schema"
        return "missing_file"

    return "remote_or_unchecked"


def _storage_diagnostics_for(book: Book) -> dict[str, Any]:
    """Return path-redacted diagnostics without opening the GnuCash source via piecash."""
    configured = bool((book.uri_or_path or "").strip())

    if getattr(book, "is_enabled", True) is False:
        return {
            "status": "disabled",
            "configured": configured,
            "checked": False,
            "safe_summary": "This book metadata entry is disabled until its source is preflighted again.",
            "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["disabled"],
        }

    snapshot = getattr(book, "health_snapshot", None)
    safe_code = _cached_health_safe_code(book)
    if safe_code in {"ready", "available"}:
        safe_summary = (
            "Cached app metadata health is ready; listing did not touch the GnuCash source."
            if safe_code == "ready"
            else "A configured local SQLite book path is present and exists; the file is not opened by the metadata listing."
        )
        return {
            "status": "available",
            "configured": configured,
            "checked": True,
            "safe_summary": safe_summary,
            "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["available"],
        }

    if safe_code == "not_checked":
        return {
            "status": "not_checked",
            "configured": configured,
            "checked": False,
            "safe_summary": "Cached app metadata health has not been verified yet; run preflight/recheck from an admin session.",
            "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["remote_or_unchecked"],
        }
    if safe_code == "remote_or_unchecked":
        return {
            "status": "remote_or_unchecked",
            "configured": configured,
            "checked": False,
            "safe_summary": "This book source has not been checked by this runtime.",
            "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["remote_or_unchecked"],
        }
    if safe_code == "missing_file":
        return {
            "status": "missing_file",
            "configured": configured,
            "checked": True,
            "safe_summary": "A configured local SQLite book path is present, but the file was not found from this runtime.",
            "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["missing_file"],
        }
    if safe_code == "not_configured":
        return {
            "status": "not_configured",
            "configured": configured,
            "checked": True,
            "safe_summary": "No book location is configured in app metadata.",
            "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["not_configured"],
        }
    if safe_code == "invalid_gnucash_schema":
        return {
            "status": "invalid_gnucash_schema",
            "configured": configured,
            "checked": True,
            "safe_summary": "A configured local SQLite book path is present, but it does not look like a readable GnuCash SQLite book.",
            "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["invalid_gnucash_schema"],
        }

    return {
        "status": safe_code,
        "configured": configured,
        "checked": True,
        "safe_summary": "Cached app metadata health is not ready; no GnuCash source was opened for this listing.",
        "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS.get(safe_code, SAFE_OPERATOR_NEXT_ACTIONS["missing_file"]),
    }


def _access_role_for(book: Book, user: User | None) -> str | None:
    if user is None:
        return None
    user_id = int(user.id)
    if getattr(book, "_current_user_access_user_id", None) == user_id:
        role = getattr(book, "_current_user_access_role", None)
        return role if isinstance(role, str) else None
    for entry in book.__dict__.get("access_entries", []):
        if entry.user_id == user.id:
            return entry.role
    return None


def _access_copy_for(role: str | None) -> dict[str, str]:
    if role in ACCESS_ROLE_COPY:
        return ACCESS_ROLE_COPY[role]
    return {
        "label": "Unknown access",
        "description": "This book is listed only when the server has already verified access for the signed-in user.",
    }


def _iso_datetime(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return str(value)


def _book_health_dto(book: Book, storage_status: str) -> BookHealthDTO:
    snapshot = getattr(book, "health_snapshot", None)
    if snapshot is not None:
        safe_code = _cached_health_safe_code(book)
        status_value = "ready" if safe_code == "ready" else safe_code
        return BookHealthDTO(
            status=status_value,
            source_status=_safe_status_value(getattr(snapshot, "source_status", None)),
            open_status=_safe_status_value(getattr(snapshot, "open_status", None)),
            accounts_status=_safe_status_value(getattr(snapshot, "accounts_status", None)),
            transactions_status=_safe_status_value(getattr(snapshot, "transactions_status", None)),
            reports_status=_safe_status_value(getattr(snapshot, "reports_status", None)),
            safe_code=safe_code,
            checked_at=_iso_datetime(snapshot.checked_at),
            last_successful_at=_iso_datetime(getattr(snapshot, "last_successful_at", None)),
        )
    if storage_status in {"ready", "available"} and _cached_health_safe_code(book) == "ready":
        return BookHealthDTO(
            status="ready",
            source_status="ready",
            open_status="ready",
            accounts_status="ready",
            transactions_status="ready",
            reports_status="ready",
            safe_code="ready",
            checked_at=None,
            last_successful_at=None,
        )
    if storage_status in {"ready", "available"}:
        return BookHealthDTO(
            status="not_checked",
            source_status="not_checked",
            open_status="not_checked",
            accounts_status="not_checked",
            transactions_status="not_checked",
            reports_status="not_checked",
            safe_code="not_checked",
            checked_at=None,
            last_successful_at=None,
        )
    return BookHealthDTO(
        status=storage_status,
        source_status=storage_status,
        open_status="not_checked",
        accounts_status="not_checked",
        transactions_status="not_checked",
        reports_status="not_checked",
        safe_code=storage_status,
        checked_at=None,
        last_successful_at=None,
    )


def _health_dto_for(book: Book) -> BookHealthDTO:
    return _book_health_dto(book, _storage_diagnostics_for(book)["status"])


def _ensure_health_snapshot(session: Session, book: Book) -> BookHealthSnapshot:
    snapshot = getattr(book, "health_snapshot", None)
    if snapshot is None:
        snapshot = BookHealthSnapshot()
        snapshot.book_id = book.id
        session.add(snapshot)
        book.health_snapshot = snapshot
    return snapshot


def _persist_successful_health(session: Session, book: Book, probe: BookHealthProbeResult) -> None:
    snapshot = _ensure_health_snapshot(session, book)
    snapshot.source_status = probe.source_status.status
    snapshot.open_status = probe.open_status.status
    snapshot.accounts_status = probe.accounts.status
    snapshot.transactions_status = probe.transactions.status
    snapshot.reports_status = probe.reports.status
    snapshot.safe_code = "ready"
    snapshot.checked_at = probe.checked_at
    snapshot.last_successful_at = probe.checked_at


def _persist_failed_health(session: Session, book: Book, exc: BookPreflightError) -> None:
    snapshot = _ensure_health_snapshot(session, book)
    code = exc.problem.code
    snapshot.source_status = "ready" if code == "open_failed" else "failed"
    snapshot.open_status = "failed" if code == "open_failed" else "not_checked"
    snapshot.accounts_status = "not_checked"
    snapshot.transactions_status = "not_checked"
    snapshot.reports_status = "not_checked"
    snapshot.safe_code = code
    snapshot.checked_at = datetime.now(timezone.utc)


def _require_enabled_and_healthy_for_default(book: Book) -> None:
    if not bool(getattr(book, "is_enabled", True)):
        _raise_lifecycle_problem("book_not_enabled", status.HTTP_409_CONFLICT)
    safe_code = _cached_health_safe_code(book)
    if safe_code == "not_checked":
        _raise_lifecycle_problem("book_health_not_checked", status.HTTP_409_CONFLICT)
    if safe_code != "ready":
        _raise_lifecycle_problem("book_not_healthy", status.HTTP_409_CONFLICT)


def serialize_book(book: Book, user: User | None = None) -> dict[str, Any]:
    """Serialize app metadata for a book without opening its GnuCash data."""
    storage_diagnostics = _storage_diagnostics_for(book)
    status_value = storage_diagnostics["status"]
    access_role = _access_role_for(book, user)
    access_copy = _access_copy_for(access_role)
    health = _book_health_dto(book, status_value)
    enabled = bool(getattr(book, "is_enabled", True))
    can_open_read_only_views = enabled and health.safe_code in {"ready", "not_checked"}
    return {
        "id": book.id,
        "name": book.name,
        "storage_type": book.storage_type,
        "base_currency": book.base_currency,
        "is_default": book.is_default,
        "is_archived": book.is_archived,
        "is_enabled": enabled,
        "enabled": enabled,
        "created_at": _iso_datetime(book.created_at),
        "updated_at": _iso_datetime(getattr(book, "updated_at", None)),
        "health": health.model_dump(mode="json"),
        "capabilities": {
            "read_only": True,
            "can_register_metadata": bool(user and user.is_admin),
            "can_open_accounts": can_open_read_only_views,
            "can_open_transactions": can_open_read_only_views,
            "can_open_reports": can_open_read_only_views,
            "can_upload": False,
            "can_edit": False,
            "can_delete": False,
            "can_edit_gnucash": False,
            "can_delete_source": False,
        },
        "access_role": access_role,
        "access_role_label": access_copy["label"],
        "access_role_description": access_copy["description"],
        "read_only": True,
        "status": status_value,
        "status_severity": STATUS_SEVERITY.get(status_value, "warning"),
        "access_status": "accessible",
        "can_open_read_only_views": can_open_read_only_views,
        "storage_diagnostics": storage_diagnostics,
        "management_actions": ADMIN_SAFE_MANAGEMENT_ACTIONS if user and user.is_admin else [],
        "operator_guidance": {
            "metadata_source": "app_metadata_db",
            "data_access": "gnucash_not_opened_for_listing",
            "read_only_default": True,
            "private_path_redacted": True,
            "storage_type_label": f"Read-only {book.storage_type} GnuCash book metadata",
            "unsupported_management_actions": UNSUPPORTED_MVP_MANAGEMENT_ACTIONS,
            "message": (
                "This MVP lists configured accessible book metadata only. "
                "Upload, file delete, accounting-data edits, and direct file browsing are intentionally unavailable. "
                "Admin registry actions are metadata-only."
            ),
        },
    }


def serialize_transaction_create_settings(book: Book, settings: Settings) -> dict[str, Any]:
    blockers = validate_transaction_create_enablement_for_admin(book, settings)
    enabled = bool(getattr(book, "transaction_create_enabled", False))
    return {
        "book_id": int(book.id),
        "enabled": enabled,
        "generation": int(getattr(book, "transaction_create_generation", 1) or 1),
        "recovery_required": bool(getattr(book, "transaction_create_recovery_required", False)),
        "deployment_writes_enabled": bool(settings.gnucash_writes_enabled),
        "can_enable": not blockers,
        "blocked_codes": list(blockers),
    }


def _transaction_create_setting_blocker_status(code: str) -> int:
    if code in {"PREVIEW_STALE", "CREATE_RECOVERY_REQUIRED"}:
        return status.HTTP_409_CONFLICT
    if code in {"UNSUPPORTED_COMMODITY", "COMMODITY_MISMATCH"}:
        return status.HTTP_422_UNPROCESSABLE_CONTENT
    return status.HTTP_403_FORBIDDEN


def _audit_transaction_create_setting_change(
    session: Session,
    *,
    user_id: int,
    book_id: int,
    old_enabled: bool,
    new_enabled: bool,
    generation: int,
) -> None:
    payload = serialize_transaction_create_audit_payload(
        {
            "result": "success",
            "old_enabled": old_enabled,
            "new_enabled": new_enabled,
            "create_generation": generation,
        }
    )
    session.add(
        AuditLog(
            user_id=user_id,
            book_id=book_id,
            action="book.transaction_create.setting_changed",
            payload_json=json.dumps(payload, sort_keys=True, separators=(",", ":")),
        )
    )


def resolve_viewable_book(book_id: int, user: User, session: Session) -> Book:
    """Resolve a book and require current user view access."""
    book = BookRegistryService(session).get_book_for_user(book_id, user)
    if book is None or book.is_archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    require_book_view_access(book, user, session)
    return book


def require_book_storage_available_for_readonly(book: Book) -> None:
    """Reject read-only data routes for disabled or explicitly unhealthy cached states."""
    safe_code = _cached_health_safe_code(book)
    if getattr(book, "health_snapshot", None) is None:
        safe_code = _legacy_uncached_storage_status_for(book)
    if getattr(book, "is_enabled", True) is False:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured GnuCash book metadata is disabled until source preflight is repeated.",
        )
    if safe_code in {"ready", "available", "not_checked"}:
        return
    if safe_code == "missing_file":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured GnuCash book storage is unavailable from this runtime.",
        )
    if safe_code == "not_configured":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GnuCash book storage is not configured for this entry.",
        )
    if safe_code == "invalid_gnucash_schema":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured GnuCash book storage is not a readable SQLite GnuCash book.",
        )
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Configured GnuCash book storage is unavailable from this runtime.",
    )


def require_book_storage_configured_for_metadata_summary(book: Book) -> None:
    """Reject metadata summaries for absent storage without opening the GnuCash source."""
    if getattr(book, "is_enabled", True) is False:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured GnuCash book metadata is disabled until source preflight is repeated.",
        )
    snapshot = getattr(book, "health_snapshot", None)
    if snapshot is not None:
        safe_code = _cached_health_safe_code(book)
        if safe_code == "missing_file":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Configured GnuCash book storage is unavailable from this runtime.",
            )
        if safe_code == "not_configured":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GnuCash book storage is not configured for this entry.",
            )
        return

    configured_value = str(getattr(book, "uri_or_path", "") or "").strip()
    if not configured_value:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GnuCash book storage is not configured for this entry.",
        )
    if _is_uri(configured_value):
        return
    if not Path(configured_value).expanduser().exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured GnuCash book storage is unavailable from this runtime.",
        )


def resolve_readonly_data_book(book_id: int, user: User, session: Session) -> Book:
    """Resolve a viewable book and require it to be openable for read-only data routes."""
    book = resolve_viewable_book(book_id, user, session)
    require_book_storage_available_for_readonly(book)
    return book


def require_book_view_access(book: Book, user: User, session: Session) -> None:
    try:
        BookAccessService(session).assert_can_view(user, book)
    except AccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Book access denied",
        ) from exc


def handle_gnucash_error(exc: Exception) -> None:
    """Translate GnuCash service-layer errors to stable, path-safe HTTP responses."""
    if isinstance(exc, EntityNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, BookNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured GnuCash book storage is unavailable from this runtime.",
        ) from exc
    if isinstance(exc, BookNotConfiguredError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GnuCash book storage is not configured for this entry.",
        ) from exc
    if isinstance(exc, GnuCashReadError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GnuCash book cannot be read safely from this runtime.",
        ) from exc
    raise exc


def account_service_for(book: Book) -> GnuCashBookService:
    """Create the read-only GnuCash service for a book.

    Routes must use this adapter instead of importing or calling piecash directly.
    """
    return GnuCashBookService(book)


def transaction_service_for(book: Book) -> GnuCashBookService:
    """Alias for account_service_for; same service handles transactions."""
    return GnuCashBookService(book)


def scheduled_transaction_service_for(book: Book) -> GnuCashBookService:
    """Alias for account_service_for; same service handles scheduled transaction metadata."""
    return GnuCashBookService(book)


def _write_alpha_owned_transaction_ids(
    session: Session,
    book_id: int,
    transaction_ids: list[str],
) -> set[str]:
    """Return app-metadata ownership hints for read-only account activity rows."""
    candidate_ids = [transaction_id for transaction_id in transaction_ids if transaction_id]
    if not candidate_ids:
        return set()
    rows = (
        session.query(WriteAlphaTransactionOwnership.transaction_id)
        .filter(
            WriteAlphaTransactionOwnership.book_id == book_id,
            WriteAlphaTransactionOwnership.transaction_id.in_(candidate_ids),
            WriteAlphaTransactionOwnership.created_by_write_alpha == True,  # noqa: E712
        )
        .all()
    )
    return {str(row[0]) for row in rows}


def _serialize_account_activity(result: Any, *, session: Session, book_id: int) -> dict[str, Any]:
    """Attach write-alpha ownership hints without invoking any write path."""
    payload = result.model_dump()
    owned_ids = _write_alpha_owned_transaction_ids(
        session,
        book_id,
        [str(item.get("id", "")) for item in payload.get("recent_transactions", [])],
    )
    for item in payload.get("recent_transactions", []):
        item["is_write_alpha_owned"] = item.get("id") in owned_ids
    return payload


@router.get("", response_model=list[BookPublicDTO])
async def list_books(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List books visible to the current user."""
    books = BookRegistryService(session).list_books_for_user(user)
    return [serialize_book(book, user) for book in books]


@router.get("/{book_id}/transaction-create-settings")
async def get_transaction_create_settings(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Admin-only per-book product CREATE setting state from app metadata."""

    require_admin_user(user)
    book = BookRegistryService(session).get_book(book_id)
    if book is None or book.is_archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return serialize_transaction_create_settings(book, settings)


@router.patch("/{book_id}/transaction-create-settings")
async def patch_transaction_create_settings(
    book_id: int,
    body: TransactionCreateSettingsPatchRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Admin-only exact `{enabled:boolean}` toggle for product transaction CREATE."""

    require_admin_user(user)
    book = BookRegistryService(session).get_book(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if body.enabled:
        blockers = validate_transaction_create_enablement_for_admin(book, settings)
        if blockers:
            first = blockers[0]
            raise_transaction_create_error(
                _transaction_create_setting_blocker_status(first),
                first,
                retryable=first == "PREVIEW_STALE",
            )

    old_enabled = bool(getattr(book, "transaction_create_enabled", False))
    if old_enabled != body.enabled:
        book.transaction_create_enabled = body.enabled
        book.transaction_create_generation = int(getattr(book, "transaction_create_generation", 1) or 1) + 1
        book.updated_at = datetime.now(timezone.utc)
        _audit_transaction_create_setting_change(
            session,
            user_id=int(user.id),
            book_id=int(book.id),
            old_enabled=old_enabled,
            new_enabled=body.enabled,
            generation=int(book.transaction_create_generation),
        )
        session.commit()
        session.refresh(book)
    return serialize_transaction_create_settings(book, settings)


@router.post("/preflight", response_model=BookPreflightResponse)
async def preflight_book(
    body: BookPreflightRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> BookPreflightResponse:
    """Preflight an already-mounted local SQLite book without metadata/source writes."""
    require_admin_user(user)
    try:
        return BookPreflightService(settings, session).run(body)
    except BookPreflightError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.problem.model_dump(),
        ) from exc


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BookPublicDTO)
async def register_book(
    body: BookRegistrationRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Register an already-mounted local SQLite book in app metadata only."""
    require_admin_user(user)
    probe = _verify_preflight_bound_probe(
        raw_path=body.uri_or_path,
        token=body.preflight_token,
        expected_request=_normalize_token_request_for_registration(body),
        settings=settings,
    )
    identity = probe.identity
    _reject_duplicate_canonical_registration(session, identity.canonical_path_hash)

    if body.make_default:
        active_defaults = session.query(Book).filter(
            Book.is_archived.is_(False),
            Book.is_enabled.is_(True),
        )
        active_defaults.update({Book.is_default: False}, synchronize_session=False)

    book = Book(
        name=body.name,
        storage_type=body.storage_type.lower(),
        uri_or_path=body.uri_or_path,
        canonical_path=identity.canonical_path,
        canonical_path_hash=identity.canonical_path_hash,
        base_currency=body.base_currency,
        is_default=body.make_default,
        is_archived=False,
        is_enabled=True,
    )
    session.add(book)
    try:
        session.flush()
        _persist_successful_health(session, book, probe)
        session.add(UserBookAccess(user_id=user.id, book_id=book.id, role="owner"))
        setattr(book, "_current_user_access_user_id", int(user.id))
        setattr(book, "_current_user_access_role", "owner")
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        _raise_lifecycle_problem("duplicate_canonical_path", status.HTTP_409_CONFLICT)
    session.refresh(book)
    return serialize_book(book, user)


@router.post("/{book_id}/default", response_model=BookPublicDTO)
async def set_default_book(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Set an existing app metadata book as default without opening GnuCash data."""
    require_admin_user(user)
    book = BookRegistryService(session).get_book_for_user(book_id, user)
    if book is None or book.is_archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    _require_enabled_and_healthy_for_default(book)

    session.query(Book).filter(
        Book.is_archived.is_(False),
        Book.is_enabled.is_(True),
    ).update({Book.is_default: False}, synchronize_session=False)
    book.is_default = True
    book.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(book)
    return serialize_book(book, user)


@router.delete("/{book_id}")
async def remove_book_from_registry(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Archive a book metadata entry; never delete the underlying GnuCash file."""
    require_admin_user(user)
    book = BookRegistryService(session).get_book(book_id)
    if book is None or book.is_archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    book.is_archived = True
    book.is_enabled = False
    if book.is_default:
        book.is_default = False
    book.updated_at = datetime.now(timezone.utc)
    session.commit()
    return {
        "id": book_id,
        "removed_from_registry": True,
        "underlying_file_deleted": False,
    }


@router.get("/{book_id}/health", response_model=BookHealthDTO)
async def get_book_health(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> BookHealthDTO:
    """Return cached path-safe health for an authorized viewer."""
    book = resolve_viewable_book(book_id, user, session)
    return _health_dto_for(book)


@router.post("/{book_id}/health/recheck", response_model=BookHealthDTO)
async def recheck_book_health(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> BookHealthDTO:
    """Admin-only bounded read-only source health recheck."""
    require_admin_user(user)
    book = BookRegistryService(session).get_book(book_id)
    if book is None or book.is_archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    try:
        probe = run_book_health_probe(book.uri_or_path, settings)
    except BookPreflightError as exc:
        _persist_failed_health(session, book, exc)
        book.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(book)
        return _health_dto_for(book)
    _persist_successful_health(session, book, probe)
    book.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(book)
    return _health_dto_for(book)


@router.patch("/{book_id}", response_model=BookPublicDTO)
async def patch_book_metadata(
    book_id: int,
    body: BookPatchRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Admin-only metadata edit for display name and base currency only."""
    require_admin_user(user)
    book = BookRegistryService(session).get_book_for_user(book_id, user)
    if book is None or book.is_archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if body.name is not None:
        book.name = body.name
    if body.base_currency is not None:
        book.base_currency = body.base_currency
    book.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(book)
    return serialize_book(book, user)


@router.post("/{book_id}/disable", response_model=BookPublicDTO)
async def disable_book(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Disable book metadata without opening the GnuCash source."""
    require_admin_user(user)
    book = BookRegistryService(session).get_book_for_user(book_id, user)
    if book is None or book.is_archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    book.is_enabled = False
    book.is_default = False
    book.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(book)
    return serialize_book(book, user)


@router.post("/{book_id}/enable", response_model=BookPublicDTO)
async def enable_book(
    book_id: int,
    body: BookEnableRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Enable disabled metadata only after a fresh matching successful preflight token."""
    require_admin_user(user)
    book = BookRegistryService(session).get_book_for_user(book_id, user)
    if book is None or book.is_archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    probe = _verify_preflight_bound_probe(
        raw_path=book.uri_or_path,
        token=body.preflight_token,
        expected_request=_normalize_token_request_for_book(book, make_default=body.make_default),
        settings=settings,
    )
    if book.canonical_path_hash and probe.identity.canonical_path_hash != book.canonical_path_hash:
        _raise_lifecycle_problem("preflight_source_mismatch", status.HTTP_409_CONFLICT)
    if body.make_default:
        session.query(Book).filter(
            Book.is_archived.is_(False),
            Book.is_enabled.is_(True),
        ).update({Book.is_default: False}, synchronize_session=False)
        book.is_default = True
    else:
        book.is_default = False
    book.canonical_path = probe.identity.canonical_path
    book.canonical_path_hash = probe.identity.canonical_path_hash
    book.is_enabled = True
    book.updated_at = datetime.now(timezone.utc)
    _persist_successful_health(session, book, probe)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        _raise_lifecycle_problem("duplicate_canonical_path", status.HTTP_409_CONFLICT)
    session.refresh(book)
    return serialize_book(book, user)


@router.get("/{book_id}", response_model=BookPublicDTO)
async def get_book(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one viewable book by id."""
    book = resolve_viewable_book(book_id, user, session)
    return serialize_book(book, user)


@router.get("/{book_id}/scheduled-transactions")
async def list_book_scheduled_transactions(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List safe read-only scheduled transaction metadata for an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    scheduled = []
    try:
        scheduled = scheduled_transaction_service_for(book).list_scheduled_transactions()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [item.model_dump() for item in scheduled]


@router.get("/{book_id}/accounts")
async def list_book_accounts(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List accounts for an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        accounts = account_service_for(book).list_accounts()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [account.model_dump() for account in accounts]


@router.get("/{book_id}/accounts/tree")
async def get_book_account_tree(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return nested account tree for an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        tree = account_service_for(book).get_account_tree()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [node.model_dump() for node in tree]


@router.get("/{book_id}/accounts/explorer")
async def explore_book_accounts(
    book_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return bounded flat preorder account hierarchy for an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        explorer_query = build_account_explorer_query(
            mode=request.query_params.get("mode"),
            query=request.query_params.get("query"),
            types=request.query_params.getlist("type"),
            hidden=request.query_params.get("hidden"),
            placeholder=request.query_params.get("placeholder"),
        )
        result = account_service_for(book).explore_accounts(explorer_query, book_id=book.id)
    except AccountExplorerError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
        raise
    return result.model_dump()


@router.get("/{book_id}/accounts/{account_id}/overview")
async def get_book_account_overview(
    book_id: int,
    account_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return a bounded read-only overview for one account in an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        normalized_account_id = normalize_account_guid(account_id)
        result = account_service_for(book).get_account_overview(normalized_account_id, book_id=book.id)
    except AccountExplorerError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
        raise
    return result.model_dump()


@router.get("/{book_id}/accounts/{account_id}/activity")
async def get_book_account_activity(
    book_id: int,
    account_id: str,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: str | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return bounded direct-account activity for one account in an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        normalized_account_id = normalize_account_guid(account_id)
        activity_query = build_account_activity_query(date_from=date_from, date_to=date_to, limit=limit)
        result = account_service_for(book).get_account_activity(
            normalized_account_id,
            activity_query,
            book_id=book.id,
        )
    except AccountExplorerError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
        raise
    return _serialize_account_activity(result, session=session, book_id=book.id)


@router.get("/{book_id}/accounts/{account_id}")
async def get_book_account(
    book_id: int,
    account_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one account in an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        account = account_service_for(book).get_account(account_id)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return account.model_dump()
