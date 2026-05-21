"""Book-aware and MVP transaction browsing router.

Read-only endpoints require auth.
Write endpoints (Phase 12) require editor/owner role and follow strict write flow.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import re
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.models import Book, User, AuditLog, WriteAlphaTransactionOwnership
from app.routers.auth import get_current_user, get_db
from app.routers.accounts import resolve_default_viewable_book
from app.routers.books import (
    handle_gnucash_error,
    require_book_view_access,
    transaction_service_for,
)
from app.schemas.gnucash import (
    PaginatedResponse,
    TransactionDetailDTO,
    TransactionListItemDTO,
)
from app.schemas.gnucash_writes import (
    TransactionCreateRequestDTO,
    TransactionPatchRequestDTO,
    TransactionValidationResultDTO,
    TransactionWriteResultDTO,
    WriteAlphaAuditSummaryDTO,
    WriteAlphaAuditSummaryItemDTO,
)
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
)
from app.services.gnucash_write import GnuCashWriteService, GnuCashWriteError
from app.services.book_access import AccessDenied, BookAccessService
from app.services.write_lock import WriteLockError
from app.services.gnucash_book import SUPPORTED_TRANSACTION_STATES

logger = logging.getLogger(__name__)

router = APIRouter(tags=["transactions"])


def _serialize_transaction_list_item(item: TransactionListItemDTO) -> dict[str, Any]:
    return item.model_dump()


def _serialize_transaction_detail(detail: TransactionDetailDTO) -> dict[str, Any]:
    return detail.model_dump()


# ---------------------------------------------------------------------------
# Book-aware endpoints
# ---------------------------------------------------------------------------


@router.get("/books/{book_id}/transactions")
async def list_book_transactions(
    book_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    account_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    query: str | None = None,
    transaction_state: str | None = None,
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """List transactions for a viewable book with pagination and filters."""
    _validate_transaction_filters(date_from, date_to, min_amount, max_amount, transaction_state)
    book = _resolve_readonly_data_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
        total = service.count_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        items = service.list_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=limit,
            offset=offset,
        )
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return PaginatedResponse(
        items=[_serialize_transaction_list_item(item) for item in items],
        limit=limit,
        offset=offset,
        total=total,
    ).model_dump()


# ---------------------------------------------------------------------------
# CSV Export (read-only, book-aware)
# ---------------------------------------------------------------------------

CSV_EXPORT_LIMIT = 10_000


@router.get("/books/{book_id}/transactions/export")
async def export_book_transactions_csv(
    book_id: int,
    account_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    query: str | None = None,
    transaction_state: str | None = None,
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> StreamingResponse:
    """Export transactions as a CSV file for a viewable book.

    Respects the same filters as the list endpoint. Row cap: 10,000.
    """
    _validate_transaction_filters(date_from, date_to, min_amount, max_amount, transaction_state)
    book = _resolve_readonly_data_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
        total = service.count_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        capped = min(total, CSV_EXPORT_LIMIT)
        items = service.list_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=capped,
            offset=0,
            max_limit=CSV_EXPORT_LIMIT,
        )
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)

    headers = [
        "id",
        "date",
        "description",
        "amount",
        "currency",
        "account_id",
        "account_name",
        "counter_account_name",
    ]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for item in items:
        writer.writerow([
            item.id,
            item.date,
            item.description,
            item.amount,
            item.currency,
            item.account_id,
            item.account_name,
            item.counter_account_name,
        ])

    filename = f"transactions-book{book_id}.csv"
    truncated = total > CSV_EXPORT_LIMIT
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-CSV-Export-Limit": str(CSV_EXPORT_LIMIT),
            "X-CSV-Export-Total": str(total),
            "X-CSV-Export-Truncated": "true" if truncated else "false",
            "X-CSV-Export-Timeout-Policy": "synchronous-request-timeout",
        },
    )


@router.get("/books/{book_id}/transactions/{transaction_id}")
async def get_book_transaction(
    book_id: int,
    transaction_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one transaction with all splits for a viewable book."""
    book = _resolve_readonly_data_book(book_id, user, session)
    try:
        detail = transaction_service_for(book).get_transaction(transaction_id)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return _serialize_transaction_detail(detail)


@router.get("/books/{book_id}/accounts/{account_id}/transactions")
async def list_book_account_transactions(
    book_id: int,
    account_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    date_from: str | None = None,
    date_to: str | None = None,
    query: str | None = None,
    transaction_state: str | None = None,
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """List transactions for a specific account in a viewable book."""
    _validate_transaction_filters(date_from, date_to, min_amount, max_amount, transaction_state)
    book = _resolve_readonly_data_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
        total = service.count_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        items = service.list_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=limit,
            offset=offset,
        )
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return PaginatedResponse(
        items=[_serialize_transaction_list_item(item) for item in items],
        limit=limit,
        offset=offset,
        total=total,
    ).model_dump()


# ---------------------------------------------------------------------------
# MVP aliases (default book)
# ---------------------------------------------------------------------------


@router.get("/transactions")
async def list_default_book_transactions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    account_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    query: str | None = None,
    transaction_state: str | None = None,
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """List transactions for the default book."""
    _validate_transaction_filters(date_from, date_to, min_amount, max_amount, transaction_state)
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
        total = service.count_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        items = service.list_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=limit,
            offset=offset,
        )
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return PaginatedResponse(
        items=[_serialize_transaction_list_item(item) for item in items],
        limit=limit,
        offset=offset,
        total=total,
    ).model_dump()


@router.get("/transactions/{transaction_id}")
async def get_default_book_transaction(
    transaction_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one transaction with all splits from the default book."""
    book = resolve_default_viewable_book(user, session)
    try:
        detail = transaction_service_for(book).get_transaction(transaction_id)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return _serialize_transaction_detail(detail)


@router.get("/accounts/{account_id}/transactions")
async def list_default_book_account_transactions(
    account_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    date_from: str | None = None,
    date_to: str | None = None,
    query: str | None = None,
    transaction_state: str | None = None,
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """List transactions for a specific account in the default book."""
    _validate_transaction_filters(date_from, date_to, min_amount, max_amount, transaction_state)
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
        total = service.count_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        items = service.list_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            transaction_state=transaction_state,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=limit,
            offset=offset,
        )
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return PaginatedResponse(
        items=[_serialize_transaction_list_item(item) for item in items],
        limit=limit,
        offset=offset,
        total=total,
    ).model_dump()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_viewable_book(book_id: int, user: User, session: Session) -> Book:
    from app.routers.books import resolve_viewable_book

    return resolve_viewable_book(book_id, user, session)


def _resolve_readonly_data_book(book_id: int, user: User, session: Session) -> Book:
    from app.routers.books import resolve_readonly_data_book

    return resolve_readonly_data_book(book_id, user, session)


def _validate_transaction_filters(
    date_from: str | None,
    date_to: str | None,
    min_amount: Decimal | None,
    max_amount: Decimal | None,
    transaction_state: str | None,
) -> None:
    """Reject invalid or inverted transaction filters before querying GnuCash."""
    _validate_date_range(date_from, date_to)
    _validate_amount_range(min_amount, max_amount)
    _validate_transaction_state(transaction_state)


def _validate_date_range(date_from: str | None, date_to: str | None) -> None:
    """Reject invalid or inverted ISO date ranges before querying GnuCash."""
    if not date_from and not date_to:
        return

    parsed_from = _parse_filter_date("date_from", date_from) if date_from else None
    parsed_to = _parse_filter_date("date_to", date_to) if date_to else None
    if parsed_from is not None and parsed_to is not None and parsed_from > parsed_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from cannot be later than date_to",
        )


def _parse_filter_date(name: str, value: str | None) -> date:
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{name} must use YYYY-MM-DD format",
        )
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{name} must use YYYY-MM-DD format",
        ) from exc


def _validate_amount_range(min_amount: Decimal | None, max_amount: Decimal | None) -> None:
    """Reject inverted amount ranges before querying GnuCash."""
    if min_amount is not None and max_amount is not None and min_amount > max_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_amount cannot be greater than max_amount",
        )


def _validate_transaction_state(transaction_state: str | None) -> None:
    """Reject unsupported split reconciliation-state filters before querying GnuCash."""
    if not transaction_state:
        return
    if transaction_state not in SUPPORTED_TRANSACTION_STATES:
        allowed = ", ".join(sorted(SUPPORTED_TRANSACTION_STATES))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"transaction_state must be one of: {allowed}",
        )


def _require_book_edit_access(book: Book, user: User, session: Session) -> None:
    """Require current user editor or owner access to a book."""
    try:
        BookAccessService(session).assert_can_edit(user, book)
    except AccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Book edit access denied",
        ) from exc


def _write_service_for(book: Book) -> GnuCashWriteService:
    """Create the write-capable GnuCash service for a book."""
    return GnuCashWriteService(book)


def _audit_log(
    session: Session,
    user_id: int,
    book_id: int,
    action: str,
    payload: dict,
) -> AuditLog:
    """Write an audit log entry.

    The audit entry is created before invoking the GnuCash write. The route then
    updates it with success/failure details so a successful book mutation is not
    left completely unaudited if later response handling fails.
    """
    log = AuditLog(
        user_id=user_id,
        book_id=book_id,
        action=action,
        payload_json=json.dumps(payload, default=str),
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def _update_audit_log(session: Session, log: AuditLog, payload: dict) -> None:
    """Best-effort audit log update used after a write attempt completes."""
    log.payload_json = json.dumps(payload, default=str)
    session.add(log)
    session.commit()
    session.refresh(log)


def _record_write_alpha_transaction_ownership(
    session: Session,
    *,
    book_id: int,
    transaction_id: str,
    user_id: int | None,
) -> WriteAlphaTransactionOwnership:
    """Persist app-metadata-only ownership for a successful write-alpha CREATE."""
    now = datetime.now(timezone.utc)
    ownership = WriteAlphaTransactionOwnership(
        book_id=book_id,
        transaction_id=transaction_id,
        created_by_user_id=user_id,
        created_by_write_alpha=True,
        created_at=now,
        last_mutated_at=now,
    )
    session.add(ownership)
    session.commit()
    session.refresh(ownership)
    return ownership


def _require_write_alpha_transaction_ownership(
    session: Session,
    *,
    book_id: int,
    transaction_id: str,
    mutation: str = "mutation",
) -> WriteAlphaTransactionOwnership:
    """Require app metadata ownership before mutating an existing transaction."""
    ownership = (
        session.query(WriteAlphaTransactionOwnership)
        .filter(
            WriteAlphaTransactionOwnership.book_id == book_id,
            WriteAlphaTransactionOwnership.transaction_id == transaction_id,
            WriteAlphaTransactionOwnership.created_by_write_alpha == True,  # noqa: E712
        )
        .one_or_none()
    )
    if ownership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Write-alpha {mutation} is allowed only for transactions created by write-alpha "
                "for this book. Historical or manually imported GnuCash transactions remain read-only."
            ),
        )
    return ownership


def _mark_write_alpha_transaction_mutated(
    session: Session,
    ownership: WriteAlphaTransactionOwnership,
) -> None:
    """Refresh app-metadata-only mutation timestamp after an allowed write-alpha mutation."""
    ownership.last_mutated_at = datetime.now(timezone.utc)
    session.add(ownership)
    session.commit()


def _write_error_detail(exc: GnuCashWriteError) -> str:
    """Return a write-alpha error string safe for API responses and audit error fields.

    Dogfood showed frontend forms needed to defensively hide raw path-like backend
    details. Keep backend errors safe too: preserve validation/business wording, but
    collapse filesystem/URI-looking internals to a generic operator-safe message.
    Backup location, when relevant, stays in the explicit backup_path field.
    """
    detail = str(getattr(exc, "detail", "") or exc)
    if "://" in detail or "/" in detail or "\\" in detail:
        return "GnuCash write failed; check the configured disposable test book and backup evidence."
    return detail


def _write_lock_detail() -> str:
    """Return a lock-contention message without exposing the lock/book path."""
    return "Could not acquire write lock for this book. Retry after the active write finishes."


WRITE_ALPHA_AUDIT_ACTIONS = (
    "transaction.create",
    "transaction.patch",
    "transaction.delete",
)

WRITE_ALPHA_AUDIT_RESULTS = ("started", "success", "failed", "unknown")

SAFE_AUDIT_TRANSACTION_ID_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")
UNSAFE_AUDIT_TEXT_RE = re.compile(
    r"(://|/|\\\\|\b(amount|account|memo|description|private|assets?|liabilit(?:y|ies)|income|expense)\b|\d+\.\d{1,})",
    re.IGNORECASE,
)


def _safe_audit_error(value: object) -> str | None:
    """Return bounded operator-safe audit error text without filesystem/URI details."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if UNSAFE_AUDIT_TEXT_RE.search(text):
        return "Write-alpha request failed safely; check redacted operator evidence."
    return text[:160]


def _safe_audit_transaction_id_prefix(value: object) -> str | None:
    """Expose only an opaque bounded transaction ID prefix, never raw/path-like text."""
    if value is None:
        return None
    text = str(value).strip()
    if not SAFE_AUDIT_TRANSACTION_ID_RE.fullmatch(text):
        return None
    return text[:8]


def _safe_audit_timestamp(log: AuditLog, payload: dict[str, Any]) -> str:
    """Return an ISO timestamp from app metadata unless payload timestamp is safely parseable."""
    raw_timestamp = payload.get("timestamp")
    if (
        isinstance(raw_timestamp, str)
        and raw_timestamp
        and len(raw_timestamp) <= 40
        and "/" not in raw_timestamp
        and "\\" not in raw_timestamp
    ):
        try:
            datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
        except ValueError:
            pass
        else:
            return raw_timestamp
    return log.created_at.isoformat()


def _audit_summary_payload(log: AuditLog) -> dict[str, Any]:
    try:
        payload = json.loads(log.payload_json or "{}")
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_backup_artifact_ref(value: Any) -> str | None:
    """Return a bounded opaque backup reference without exposing raw paths or filenames."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if "\x00" in text or len(text) > 512:
        return None
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"bkp-{digest}"


def _backup_audit_fields(backup_path: str | None) -> dict[str, str | None]:
    return {
        "backup_path": backup_path,
        "backup_artifact_ref": _safe_backup_artifact_ref(backup_path),
    }


def _audit_summary_item(log: AuditLog) -> WriteAlphaAuditSummaryItemDTO:
    payload = _audit_summary_payload(log)
    return WriteAlphaAuditSummaryItemDTO(
        id=log.id,
        action=log.action,
        result=_audit_log_result(log),
        timestamp=_safe_audit_timestamp(log, payload),
        transaction_id_prefix=_safe_audit_transaction_id_prefix(payload.get("transaction_id")),
        backup_present=bool(payload.get("backup_path")),
        backup_artifact_ref=_safe_backup_artifact_ref(payload.get("backup_path")),
        error=_safe_audit_error(payload.get("error")),
    )


def _parse_audit_window(value: str | None, label: str) -> datetime | None:
    """Parse an ISO datetime filter without accepting path-like/private values."""
    if value is None or not value.strip():
        return None
    text = value.strip()
    if len(text) > 40 or "/" in text or "\\" in text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {label} filter. Use an ISO timestamp.",
        )
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {label} filter. Use an ISO timestamp.",
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _audit_log_result(log: AuditLog) -> str:
    payload = _audit_summary_payload(log)
    result = str(payload.get("result") or "unknown")
    return result if result in WRITE_ALPHA_AUDIT_RESULTS else "unknown"


def _request_summary(request: TransactionCreateRequestDTO) -> dict[str, Any]:
    return {
        "date": request.date,
        "description": request.description,
        "split_count": len(request.splits),
        "currencies": sorted({split.currency for split in request.splits}),
    }


def _ensure_writes_enabled(settings: Settings) -> None:
    """Keep the MVP read-only unless post-MVP writes are explicitly enabled."""
    if not settings.gnucash_writes_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="GnuCash writes are disabled. MVP v0.1 is read-only by default.",
        )


def _ensure_write_alpha_test_scope(settings: Settings) -> None:
    """Limit experimental write-alpha routes to automated test fixtures only."""
    if settings.app_env.lower() != "test":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Controlled write-alpha routes are limited to explicit test-environment "
                "copied/disposable fixtures. Keep GNUCASH_WRITES_ENABLED=false for normal runtime."
            ),
        )


# ---------------------------------------------------------------------------
# Phase 12: Controlled write endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/books/{book_id}/write-alpha-audit-summary",
    response_model=WriteAlphaAuditSummaryDTO,
)
async def get_write_alpha_audit_summary(
    book_id: int,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0, le=10000),
    action: str | None = Query(None, min_length=1, max_length=64),
    result: str | None = Query(None, min_length=1, max_length=32),
    since: str | None = Query(None, max_length=40),
    until: str | None = Query(None, max_length=40),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> WriteAlphaAuditSummaryDTO:
    """Return a redacted read-only summary of write-alpha audit rows from app metadata."""
    book = _resolve_viewable_book(book_id, user, session)
    _require_book_edit_access(book, user, session)
    from app.routers.books import require_book_storage_available_for_readonly

    require_book_storage_available_for_readonly(book)
    if action is not None and action not in WRITE_ALPHA_AUDIT_ACTIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported audit action filter.",
        )
    if result is not None and result not in WRITE_ALPHA_AUDIT_RESULTS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported audit result filter.",
        )
    since_dt = _parse_audit_window(since, "since")
    until_dt = _parse_audit_window(until, "until")
    if since_dt and until_dt and since_dt > until_dt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid audit time window: since must be before until.",
        )

    query = session.query(AuditLog).filter(
        AuditLog.book_id == book.id,
        AuditLog.action.in_(WRITE_ALPHA_AUDIT_ACTIONS),
    )
    if action is not None:
        query = query.filter(AuditLog.action == action)
    if since_dt is not None:
        query = query.filter(AuditLog.created_at >= since_dt)
    if until_dt is not None:
        query = query.filter(AuditLog.created_at <= until_dt)

    candidate_logs = query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).all()
    filtered_logs = [log for log in candidate_logs if result is None or _audit_log_result(log) == result]
    counts_by_action = {safe_action: 0 for safe_action in WRITE_ALPHA_AUDIT_ACTIONS}
    counts_by_result = {safe_result: 0 for safe_result in WRITE_ALPHA_AUDIT_RESULTS}
    for log in filtered_logs:
        counts_by_action[log.action] = counts_by_action.get(log.action, 0) + 1
        log_result = _audit_log_result(log)
        counts_by_result[log_result] = counts_by_result.get(log_result, 0) + 1

    logs = filtered_logs[offset : offset + limit]
    next_offset = offset + limit if offset + limit < len(filtered_logs) else None
    previous_offset = max(offset - limit, 0) if offset > 0 else None
    returned_timestamps = [
        _safe_audit_timestamp(log, _audit_summary_payload(log)) for log in logs
    ]
    return WriteAlphaAuditSummaryDTO(
        book_id=book.id,
        total_count=len(filtered_logs),
        returned_count=len(logs),
        counts_by_action=counts_by_action,
        counts_by_result=counts_by_result,
        filters={
            "action": action,
            "result": result,
            "since": since_dt.isoformat() if since_dt else None,
            "until": until_dt.isoformat() if until_dt else None,
            "limit": limit,
            "offset": offset,
        },
        pagination={
            "limit": limit,
            "offset": offset,
            "next_offset": next_offset,
            "previous_offset": previous_offset,
            "has_next": next_offset is not None,
            "has_previous": previous_offset is not None,
        },
        time_window={
            "requested_since": since_dt.isoformat() if since_dt else None,
            "requested_until": until_dt.isoformat() if until_dt else None,
            "newest_returned": max(returned_timestamps) if returned_timestamps else None,
            "oldest_returned": min(returned_timestamps) if returned_timestamps else None,
        },
        status_summary=[
            f"Filtered rows: {len(filtered_logs)}",
            f"Returned rows: {len(logs)} of at most {limit} from offset {offset}",
            "Rows are redacted to action/result/timestamp/opaque transaction prefix/backup-present/opaque backup reference/safe-error only.",
        ],
        items=[_audit_summary_item(log) for log in logs],
        limitations=[
            "Read-only app metadata summary for synthetic/disposable write-alpha runs only.",
            "Backup paths, private file paths, raw filenames, raw payloads, account names, memos, and amounts are not exposed.",
        ],
    )


@router.post(
    "/books/{book_id}/transactions/validate",
    response_model=TransactionValidationResultDTO,
)
async def validate_book_transaction(
    book_id: int,
    request: TransactionCreateRequestDTO,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TransactionValidationResultDTO:
    """Validate a transaction create request without writing."""
    _ensure_writes_enabled(settings)
    book = _resolve_viewable_book(book_id, user, session)
    _require_book_edit_access(book, user, session)
    _ensure_write_alpha_test_scope(settings)

    service = _write_service_for(book)
    return service.validate_transaction_create(request)


@router.post(
    "/books/{book_id}/transactions",
    response_model=TransactionWriteResultDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_book_transaction(
    book_id: int,
    request: TransactionCreateRequestDTO,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TransactionWriteResultDTO:
    """Create a new transaction with the given splits.

    Follows the strict write flow: validate, lock, backup, write, audit.
    """
    _ensure_writes_enabled(settings)
    book = _resolve_viewable_book(book_id, user, session)
    _require_book_edit_access(book, user, session)
    _ensure_write_alpha_test_scope(settings)

    service = _write_service_for(book)
    audit_payload = {
        "action": "transaction.create",
        "transaction_id": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_summary": _request_summary(request),
        "backup_path": None,
        "backup_artifact_ref": None,
        "result": "started",
    }
    log = _audit_log(session, user.id, book.id, "transaction.create", audit_payload)

    try:
        result = service.create_transaction(
            request=request,
            user_id=user.id,
            book_id=book.id,
        )
    except WriteLockError as exc:
        audit_payload.update({"result": "failed", "error": _write_lock_detail()})
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_write_lock_detail(),
        ) from exc
    except GnuCashWriteError as exc:
        safe_detail = _write_error_detail(exc)
        audit_payload.update(
            {
                "result": "failed",
                "error": safe_detail,
                **_backup_audit_fields(getattr(exc, "backup_path", None)),
            }
        )
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=safe_detail,
        ) from exc

    audit_payload.update(
        {
            "transaction_id": result.transaction_id,
            **_backup_audit_fields(result.backup_path),
            "result": "success",
        }
    )
    _update_audit_log(session, log, audit_payload)
    _record_write_alpha_transaction_ownership(
        session,
        book_id=book.id,
        transaction_id=result.transaction_id,
        user_id=user.id,
    )
    result.audit_log_id = log.id

    return result


@router.patch(
    "/books/{book_id}/transactions/{transaction_id}",
    response_model=TransactionWriteResultDTO,
)
async def patch_book_transaction(
    book_id: int,
    transaction_id: str,
    request: TransactionPatchRequestDTO,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TransactionWriteResultDTO:
    """Patch description, date, and/or split memos for an existing transaction.

    Does NOT allow editing split amounts or accounts.
    """
    _ensure_writes_enabled(settings)
    book = _resolve_viewable_book(book_id, user, session)
    _require_book_edit_access(book, user, session)
    _ensure_write_alpha_test_scope(settings)
    ownership = _require_write_alpha_transaction_ownership(
        session,
        book_id=book.id,
        transaction_id=transaction_id,
        mutation="PATCH",
    )

    service = _write_service_for(book)
    fields_updated = {
        k: v
        for k, v in {
            "description": request.description,
            "date": request.date,
            "split_memos": request.split_memos,
        }.items()
        if v is not None
    }
    audit_payload = {
        "action": "transaction.patch",
        "transaction_id": transaction_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_summary": {"fields_updated": list(fields_updated.keys())},
        "fields_updated": fields_updated,
        "backup_path": None,
        "backup_artifact_ref": None,
        "result": "started",
    }
    log = _audit_log(session, user.id, book.id, "transaction.patch", audit_payload)

    try:
        result = service.patch_transaction_metadata(
            transaction_id=transaction_id,
            request=request,
            user_id=user.id,
            book_id=book.id,
        )
    except WriteLockError as exc:
        audit_payload.update({"result": "failed", "error": _write_lock_detail()})
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_write_lock_detail(),
        ) from exc
    except GnuCashWriteError as exc:
        safe_detail = _write_error_detail(exc)
        audit_payload.update(
            {
                "result": "failed",
                "error": safe_detail,
                **_backup_audit_fields(getattr(exc, "backup_path", None)),
            }
        )
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=safe_detail,
        ) from exc
    except EntityNotFoundError as exc:
        audit_payload.update({"result": "failed", "error": str(exc)})
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    audit_payload.update(
        {
            **_backup_audit_fields(result.backup_path),
            "result": "success",
        }
    )
    _update_audit_log(session, log, audit_payload)
    _mark_write_alpha_transaction_mutated(session, ownership)
    result.audit_log_id = log.id

    return result


@router.delete(
    "/books/{book_id}/transactions/{transaction_id}",
    response_model=TransactionWriteResultDTO,
)
async def delete_book_transaction(
    book_id: int,
    transaction_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TransactionWriteResultDTO:
    """Delete one existing transaction through the experimental write-alpha path."""
    _ensure_writes_enabled(settings)
    book = _resolve_viewable_book(book_id, user, session)
    _require_book_edit_access(book, user, session)
    _ensure_write_alpha_test_scope(settings)
    ownership = _require_write_alpha_transaction_ownership(
        session,
        book_id=book.id,
        transaction_id=transaction_id,
        mutation="DELETE",
    )

    service = _write_service_for(book)
    audit_payload = {
        "action": "transaction.delete",
        "transaction_id": transaction_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_summary": {"transaction_id": transaction_id},
        "backup_path": None,
        "backup_artifact_ref": None,
        "result": "started",
    }
    log = _audit_log(session, user.id, book.id, "transaction.delete", audit_payload)

    try:
        result = service.delete_transaction(
            transaction_id=transaction_id,
            user_id=user.id,
            book_id=book.id,
        )
    except WriteLockError as exc:
        audit_payload.update({"result": "failed", "error": _write_lock_detail()})
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_write_lock_detail(),
        ) from exc
    except GnuCashWriteError as exc:
        safe_detail = _write_error_detail(exc)
        audit_payload.update(
            {
                "result": "failed",
                "error": safe_detail,
                **_backup_audit_fields(getattr(exc, "backup_path", None)),
            }
        )
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=safe_detail,
        ) from exc
    except EntityNotFoundError as exc:
        audit_payload.update({"result": "failed", "error": str(exc)})
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    audit_payload.update(
        {
            **_backup_audit_fields(result.backup_path),
            "result": "success",
        }
    )
    _update_audit_log(session, log, audit_payload)
    _mark_write_alpha_transaction_mutated(session, ownership)
    result.audit_log_id = log.id

    return result
