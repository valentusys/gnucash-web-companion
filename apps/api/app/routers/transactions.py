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
import os
import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, NoReturn
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.models import Book, User, AuditLog, WriteAlphaTransactionOwnership
from app.routers.auth import get_current_user, get_db
from app.routers.accounts import resolve_default_viewable_book
from app.routers.books import (
    handle_gnucash_error,
    require_book_storage_configured_for_metadata_summary,
    require_book_view_access,
    transaction_service_for,
)
from app.schemas.gnucash import (
    PaginatedResponse,
    TransactionDetailDTO,
    TransactionListItemDTO,
)
from app.schemas.gnucash_writes import (
    TransactionCreatePreviewAccountDTO,
    TransactionCreatePreviewDTO,
    TransactionCreatePreviewRequestDTO,
    TransactionCreateRequestDTO,
    TransactionPatchRequestDTO,
    TransactionSplitWriteDTO,
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
from app.services.write_lock import WriteLockError, write_lock_service
from app.services.gnucash_book import GnuCashBookService, SUPPORTED_TRANSACTION_STATES
from app.services.transaction_explorer import (
    TransactionExplorerError,
    build_transaction_explorer_query,
)
from app.services.transaction_create_audit import serialize_transaction_create_audit_payload
from app.services.transaction_create_errors import TransactionCreateHTTPError, raise_transaction_create_error
from app.services.transaction_create_idempotency import TransactionCreateIdempotencyService
from app.services.transaction_create_policy import (
    TransactionCreatePinnedSource,
    evaluate_transaction_create_policy,
    inspect_transaction_create_source,
    open_transaction_create_source,
)
from app.services.transaction_create_tokens import (
    canonical_transaction_create_request_hash,
    hash_idempotency_key,
    hash_token_jti,
    issue_preview_token,
    source_fingerprint_for_book,
    verify_preview_token,
)

logger = logging.getLogger(__name__)


class GnuCashCreateReadbackVerificationError(GnuCashWriteError):
    """Raised when a CREATE write cannot be verified through the read-only path."""


CREATE_READBACK_FAILURE_DETAIL = (
    "GnuCash create read-back verification failed; check backup and operator evidence."
)

router = APIRouter(tags=["transactions"])

SOURCE_ROOT_LAYOUT_SUFFIXES = (
    ("apps", "api", "app", "routers", "transactions.py"),
    ("app", "routers", "transactions.py"),
)


def _source_root_for_module(source_file: str | Path) -> Path:
    """Return the source boundary for local checkouts and API Docker images.

    Local development imports this module from
    ``<repo>/apps/api/app/routers/transactions.py`` while the API Docker image
    imports it from ``/app/app/routers/transactions.py``. Unknown layouts fall
    back to the filesystem anchor so disposable write-alpha preflights fail
    closed instead of accepting a repository-contained target.
    """
    source = Path(source_file).expanduser().resolve()
    parts = source.parts
    for suffix in SOURCE_ROOT_LAYOUT_SUFFIXES:
        if len(parts) > len(suffix) and tuple(parts[-len(suffix) :]) == suffix:
            return Path(*parts[: -len(suffix)]).resolve()

    for ancestor in source.parents:
        if (ancestor / ".git").exists() or (ancestor / "docker-compose.yml").exists():
            return ancestor.resolve()

    return Path(source.anchor or os.sep).resolve()


REPO_ROOT = _source_root_for_module(__file__)
DISPOSABLE_CREATE_TARGET_HINTS = frozenset(
    {
        "copy",
        "copied",
        "disposable",
        "dogfood",
        "scratch",
        "synthetic",
        "test",
        "tmp",
    }
)
SQLITE_BOOK_SUFFIXES = frozenset({".sqlite", ".sqlite3", ".db"})
ISSUE51_EXPLICIT_TEST_MODE = "issue51"
ISSUE51_EXPLICIT_CREATE_QUERY = f"explicit_test_mode={ISSUE51_EXPLICIT_TEST_MODE}"
ISSUE51_EXPLICIT_CREATE_HEADER = "issue51-explicit-synthetic-create-harness"
ISSUE51_SYNTHETIC_DISPOSABLE_BOOK_ID = 1
ISSUE51_SYNTHETIC_DISPOSABLE_PROOF = f"synthetic-disposable-fixture-book-{ISSUE51_SYNTHETIC_DISPOSABLE_BOOK_ID}"
EXPLICIT_ISSUE51_CREATE_HARNESS_DETAIL = (
    "Explicit issue51 CREATE harness requires exact test-mode query, harness header, "
    "synthetic/disposable proof, APP_ENV=test, and GNUCASH_WRITES_ENABLED=true."
)
CREATE_ROUTE_QUERY_SMUGGLING_DETAIL = (
    "CREATE write route rejects query smuggling. Default product CREATE accepts no query "
    "parameters; explicit issue51 CREATE harness accepts only exact test-mode query, "
    "synthetic/disposable proof, APP_ENV=test, and GNUCASH_WRITES_ENABLED=true."
)
NON_CREATE_ISSUE51_HARNESS_SMUGGLING_DETAIL = (
    "Non-CREATE write route rejects query/header smuggling. Explicit issue51 CREATE harness "
    "markers are accepted only by POST /books/{book_id}/transactions with exact "
    "synthetic/disposable proof, APP_ENV=test, and GNUCASH_WRITES_ENABLED=true."
)
CREATE_PREVIEW_NON_FINITE_AMOUNT_DETAIL = "amount must be a finite decimal string"
GENERAL_CREATE_PREVIEW_DECIMAL_PATTERN = re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$")
GENERAL_CREATE_PREVIEW_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
GENERAL_CREATE_ALLOWED_ACCOUNT_TYPES = frozenset(
    {"ASSET", "BANK", "CASH", "CREDIT", "LIABILITY", "INCOME", "EXPENSE", "EQUITY"}
)
ReadbackAccountBalanceSnapshot = dict[str, tuple[Decimal, str]]


def _serialize_transaction_list_item(
    item: TransactionListItemDTO,
    *,
    is_write_alpha_owned: bool | None = None,
) -> dict[str, Any]:
    payload = item.model_dump()
    if is_write_alpha_owned is not None:
        payload["is_write_alpha_owned"] = is_write_alpha_owned
    return payload


def _write_alpha_owned_transaction_ids(
    session: Session,
    book_id: int,
    transaction_ids: list[str],
) -> set[str]:
    """Return write-alpha-created transaction ids for read-only history hints."""
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


def _serialize_transaction_list_items(
    items: list[TransactionListItemDTO],
    *,
    session: Session,
    book_id: int,
) -> list[dict[str, Any]]:
    owned_ids = _write_alpha_owned_transaction_ids(session, book_id, [item.id for item in items])
    return [
        _serialize_transaction_list_item(item, is_write_alpha_owned=item.id in owned_ids)
        for item in items
    ]


def _serialize_transaction_explorer_page(page: Any, *, session: Session, book_id: int) -> dict[str, Any]:
    """Add app-metadata ownership hints without involving any write path."""
    payload = page.model_dump()
    owned_ids = _write_alpha_owned_transaction_ids(
        session,
        book_id,
        [str(item.get("id", "")) for item in payload.get("items", [])],
    )
    for item in payload.get("items", []):
        item["is_write_alpha_owned"] = item.get("id") in owned_ids
    return payload


def _is_write_alpha_owned_transaction(session: Session, book_id: int, transaction_id: str) -> bool:
    """Return app-metadata ownership status for safe UI hints only.

    Backend write routes remain authoritative and re-check ownership before any
    PATCH/DELETE mutation path can construct the write service.
    """
    return (
        session.query(WriteAlphaTransactionOwnership.id)
        .filter(
            WriteAlphaTransactionOwnership.book_id == book_id,
            WriteAlphaTransactionOwnership.transaction_id == transaction_id,
            WriteAlphaTransactionOwnership.created_by_write_alpha == True,  # noqa: E712
        )
        .first()
        is not None
    )


def _serialize_transaction_detail(
    detail: TransactionDetailDTO,
    *,
    is_write_alpha_owned: bool = False,
) -> dict[str, Any]:
    payload = detail.model_dump()
    payload["is_write_alpha_owned"] = is_write_alpha_owned
    return payload


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
        items=_serialize_transaction_list_items(items, session=session, book_id=book.id),
        limit=limit,
        offset=offset,
        total=total,
    ).model_dump()


# ---------------------------------------------------------------------------
# CSV Export (read-only, book-aware)
# ---------------------------------------------------------------------------

CSV_EXPORT_LIMIT = 10_000
CSV_FORMULA_TEXT_PREFIXES = ("=", "+", "-", "@")
CSV_FORMULA_LEADING_WHITESPACE = " \t\r\n"


def _csv_safe_text_cell(value: Any) -> str:
    """Neutralize spreadsheet formula-like text while preserving raw CSV shape.

    The export keeps decimal amount strings untouched; all other text fields are
    prefixed only when their first non-whitespace character could be interpreted
    as a spreadsheet formula/operator.
    """
    text = "" if value is None else str(value)
    stripped = text.lstrip(CSV_FORMULA_LEADING_WHITESPACE)
    if stripped.startswith(CSV_FORMULA_TEXT_PREFIXES):
        return f"'{text}"
    return text


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
            _csv_safe_text_cell(item.id),
            _csv_safe_text_cell(item.date),
            _csv_safe_text_cell(item.description),
            item.amount,
            _csv_safe_text_cell(item.currency),
            _csv_safe_text_cell(item.account_id),
            _csv_safe_text_cell(item.account_name),
            _csv_safe_text_cell(item.counter_account_name),
        ])

    filename = f"transactions-book{book_id}.csv"
    truncated = total > CSV_EXPORT_LIMIT
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Content-Type-Options": "nosniff",
            "X-CSV-Export-Limit": str(CSV_EXPORT_LIMIT),
            "X-CSV-Export-Total": str(total),
            "X-CSV-Export-Truncated": "true" if truncated else "false",
            "X-CSV-Export-Timeout-Policy": "synchronous-request-timeout",
        },
    )


def _raise_transaction_explorer_error(exc: TransactionExplorerError) -> NoReturn:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


@router.get("/books/{book_id}/transactions/explorer")
async def list_book_transactions_explorer(
    book_id: int,
    request: Request,
    date_from: str | None = None,
    date_to: str | None = None,
    account_ids: list[str] | None = Query(None),
    direction: str | None = None,
    transaction_type: str | None = Query(None, alias="type"),
    min_amount: str | None = None,
    max_amount: str | None = None,
    query: str | None = None,
    transaction_state: str | None = None,
    sort: str | None = None,
    page_size: str | None = None,
    cursor: str | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Bounded read-only date/GUID keyset transaction explorer for a viewable book."""
    try:
        explorer_query = build_transaction_explorer_query(
            date_from=date_from,
            date_to=date_to,
            account_ids=account_ids,
            legacy_account_id_present="account_id" in request.query_params,
            direction=direction,
            transaction_type=transaction_type,
            min_amount=min_amount,
            max_amount=max_amount,
            query=query,
            transaction_state=transaction_state,
            sort=sort,
            page_size=page_size,
            cursor=cursor,
            secret=settings.jwt_secret,
        )
    except TransactionExplorerError as exc:
        _raise_transaction_explorer_error(exc)

    book = _resolve_readonly_data_book(book_id, user, session)
    try:
        page = transaction_service_for(book).explore_transactions(explorer_query)
    except TransactionExplorerError as exc:
        _raise_transaction_explorer_error(exc)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return _serialize_transaction_explorer_page(page, session=session, book_id=book.id)


@router.get("/books/{book_id}/transactions/create-readiness-status")
async def get_book_transaction_create_readiness_status(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Return redacted fail-closed readiness status for the future web UI CREATE flow.

    This endpoint is intentionally read-only: it resolves only app metadata/access,
    never opens the GnuCash book, and never calls write, backup, lock, audit,
    reset, or probe helpers.
    """
    book = _resolve_viewable_book(book_id, user, session)
    _require_book_owner_access(book, user, session)
    return _build_create_readiness_status(settings)


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
    return _serialize_transaction_detail(
        detail,
        is_write_alpha_owned=_is_write_alpha_owned_transaction(session, book.id, transaction_id),
    )


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
        items=_serialize_transaction_list_items(items, session=session, book_id=book.id),
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
        items=_serialize_transaction_list_items(items, session=session, book_id=book.id),
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
    return _serialize_transaction_detail(
        detail,
        is_write_alpha_owned=_is_write_alpha_owned_transaction(session, book.id, transaction_id),
    )


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
        items=_serialize_transaction_list_items(items, session=session, book_id=book.id),
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


def _require_book_owner_access(book: Book, user: User, session: Session) -> None:
    """Require owner access for controlled owner-only preview workflows."""
    role = BookAccessService(session).get_role(user, book)
    if role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Book owner access required",
        )


CREATE_READINESS_STATUS_CHECKS = (
    {
        "id": "writes_enabled_state",
        "label": "Writes-enabled state",
        "status": "pending",
        "note": "Pending: display-only status; enabled write gates alone do not arm web UI CREATE.",
        "redacted": True,
    },
    {
        "id": "write_session_armed",
        "label": "Write session armed",
        "status": "pending",
        "note": "Pending: no owner-approved web UI CREATE session is armed.",
        "redacted": True,
    },
    {
        "id": "allowed_create_count_zero",
        "label": "Allowed CREATE count",
        "status": "pending",
        "note": "Pending: allowed CREATE count is redacted to zero until a fresh bounded owner session exists.",
        "redacted": True,
    },
    {
        "id": "target_class_selected",
        "label": "Target class selected",
        "status": "pending",
        "note": "Pending: target class remains redacted and unset.",
        "redacted": True,
    },
    {
        "id": "target_preflight_not_checked",
        "label": "Target preflight",
        "status": "pending",
        "note": "Pending: no private target preflight or book/file probe runs in this read-only status endpoint.",
        "redacted": True,
    },
    {
        "id": "backup_readiness_not_checked",
        "label": "Backup readiness",
        "status": "pending",
        "note": "Pending: no backup helper, backup path lookup, or restore proof check runs in this endpoint.",
        "redacted": True,
    },
    {
        "id": "allowed_execution_blocked",
        "label": "Allowed execution",
        "status": "pending",
        "note": "Pending: CREATE execution remains blocked without fresh owner approval and an armed session.",
        "redacted": True,
    },
    {
        "id": "reviewed_non_stale_preview",
        "label": "Reviewed non-stale preview",
        "status": "pending",
        "note": "Pending: preview review is local UI state only and does not arm CREATE.",
        "redacted": True,
    },
    {
        "id": "backup_read_back_audit_reset_probes",
        "label": "Backup/read-back/audit/reset/probes",
        "status": "pending",
        "note": "Pending: no backup, read-back, audit, reset, or probe runs in this read-only status endpoint.",
        "redacted": True,
    },
)


def _build_create_readiness_status(settings: Settings) -> dict[str, Any]:
    writes_enabled = settings.gnucash_writes_enabled
    create_execution_reason = (
        "Write gates may be enabled, but no owner-approved web UI CREATE session is armed."
        if writes_enabled
        else "GNUCASH_WRITES_ENABLED=false; write session not armed."
    )
    readiness_state = {
        "writes_enabled": {
            "enabled": writes_enabled,
            "status": "enabled_but_blocked" if writes_enabled else "disabled",
            "redacted": True,
        },
        "session_armed": {
            "armed": False,
            "status": "not_armed",
            "redacted": True,
        },
        "allowed_create_count": {
            "count": 0,
            "status": "blocked",
            "redacted": True,
        },
        "target": {
            "target_class": None,
            "status": "not_selected",
            "private_target_probed": False,
            "redacted": True,
        },
        "preflight": {
            "required": True,
            "status": "not_checked",
            "private_target_probed": False,
            "redacted": True,
        },
        "backup": {
            "required": True,
            "status": "not_checked",
            "backup_helper_called": False,
            "redacted": True,
        },
        "allowed_execution": {
            "allowed": False,
            "status": "blocked",
            "reason": create_execution_reason,
            "redacted": True,
        },
    }
    return {
        "preview_only": True,
        "status": "disabled",
        "writes_enabled": writes_enabled,
        "session_armed": False,
        "create_execution_allowed": False,
        "create_execution_reason": create_execution_reason,
        "allowed_create_count": 0,
        "target_class": None,
        "readiness_required": True,
        "readiness_status": "not_checked",
        "readiness_state": readiness_state,
        "checks": [dict(check) for check in CREATE_READINESS_STATUS_CHECKS],
        "limitations": [
            "Read-only redacted status only; no CREATE/PATCH/DELETE/batch route is called.",
            "No private target probing, GnuCash book opening, backup, lock, audit, reset, or write service helper runs.",
            "Fresh same-context owner approval with exact target class and exact CREATE count is still required before any future mutation.",
        ],
    }


def _build_transaction_create_preview(
    request: TransactionCreatePreviewRequestDTO,
    accounts: list[Any],
) -> TransactionCreatePreviewDTO:
    """Build a normalized single-CREATE preview using read-only account data."""
    _parse_preview_date(request.date)
    amount = _parse_preview_amount(request.amount)
    currency = request.currency.upper()
    description = request.description.strip()
    memo = request.memo.strip()
    if not description:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="description is required",
        )
    if request.debit_account_id == request.credit_account_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="debit and credit accounts must be different",
        )

    if not any(
        not getattr(account, "placeholder", False) and not getattr(account, "hidden", False)
        for account in accounts
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="no selectable accounts are available for preview",
        )

    by_id = {account.id: account for account in accounts}
    debit_account = _preview_account_by_id(by_id, request.debit_account_id, "debit_account_id")
    credit_account = _preview_account_by_id(by_id, request.credit_account_id, "credit_account_id")
    _validate_preview_account_currency(debit_account, currency, "debit account")
    _validate_preview_account_currency(credit_account, currency, "credit account")

    amount_text = str(amount)
    debit_amount = f"-{amount_text}"
    credit_amount = amount_text
    return TransactionCreatePreviewDTO(
        preview_only=True,
        writes_enabled_required_for_create=True,
        create_count=1,
        date=request.date,
        amount=amount_text,
        currency=currency,
        description=description,
        memo=memo,
        debit_account=_preview_account_dto(debit_account),
        credit_account=_preview_account_dto(credit_account),
        splits=[
            TransactionSplitWriteDTO(
                account_id=debit_account.id,
                amount=debit_amount,
                currency=currency,
                memo=memo,
            ),
            TransactionSplitWriteDTO(
                account_id=credit_account.id,
                amount=credit_amount,
                currency=currency,
                memo=memo,
            ),
        ],
        warnings=["Preview only: no GnuCash write was executed."],
    )


def _is_general_create_preview_payload(payload: dict[str, Any]) -> bool:
    return isinstance(payload, dict) and "splits" in payload


def _general_text(payload: dict[str, Any], field_name: str, *, default: str | None = None) -> str:
    if field_name not in payload:
        if default is not None:
            return default
        _raise_general_preview_error(_field_error_code(field_name), field_name)
    value = payload[field_name]
    if not isinstance(value, str):
        _raise_general_preview_error(_field_error_code(field_name), field_name)
    stripped = value.strip()
    if GENERAL_CREATE_PREVIEW_CONTROL_CHARS.search(stripped):
        _raise_general_preview_error(_field_error_code(field_name), field_name)
    return stripped


def _field_error_code(field_name: str) -> str:
    return {
        "date": "INVALID_DATE",
        "description": "DESCRIPTION_REQUIRED",
        "currency": "UNSUPPORTED_COMMODITY",
        "account_id": "ACCOUNT_NOT_FOUND",
        "amount": "INVALID_DECIMAL",
        "memo": "INVALID_DECIMAL",
    }.get(field_name, "INVALID_DECIMAL")


def _raise_general_preview_error(code: str, field_path: str | None = None) -> None:
    raise_transaction_create_error(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        code,
        field_path=field_path,
    )


def _validate_general_decimal_string(value: Any, field_path: str) -> tuple[str, Decimal]:
    if not isinstance(value, str):
        _raise_general_preview_error("INVALID_DECIMAL", field_path)
    amount_text = value.strip()
    digits = [character for character in amount_text if character.isdigit()]
    if (
        len(amount_text) > 64
        or len(digits) > 18
        or not GENERAL_CREATE_PREVIEW_DECIMAL_PATTERN.fullmatch(amount_text)
    ):
        _raise_general_preview_error("INVALID_DECIMAL", field_path)
    try:
        amount = Decimal(amount_text)
    except Exception:
        _raise_general_preview_error("INVALID_DECIMAL", field_path)
    if not amount.is_finite():
        _raise_general_preview_error("INVALID_DECIMAL", field_path)
    if amount == Decimal("0"):
        _raise_general_preview_error("ZERO_SPLIT", field_path)
    return amount_text, amount


def _coerce_general_transaction_create_preview_request(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise_transaction_create_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "PREVIEW_PAYLOAD_MISMATCH",
        )
    date_text = _general_text(payload, "date")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text):
        _raise_general_preview_error("INVALID_DATE", "date")
    try:
        date.fromisoformat(date_text)
    except ValueError:
        _raise_general_preview_error("INVALID_DATE", "date")
    description = _general_text(payload, "description")
    if not description or len(description) > 256:
        _raise_general_preview_error("DESCRIPTION_REQUIRED", "description")
    currency = _general_text(payload, "currency").upper()
    if not re.fullmatch(r"[A-Z]{3}", currency):
        _raise_general_preview_error("UNSUPPORTED_COMMODITY", "currency")
    raw_splits = payload.get("splits")
    if not isinstance(raw_splits, list) or not 2 <= len(raw_splits) <= 50:
        _raise_general_preview_error("SPLIT_COUNT_OUT_OF_RANGE", "splits")

    normalized_splits: list[dict[str, str]] = []
    total = Decimal("0")
    account_ids: set[str] = set()
    for index, raw_split in enumerate(raw_splits):
        if not isinstance(raw_split, dict):
            _raise_general_preview_error("PREVIEW_PAYLOAD_MISMATCH", f"splits[{index}]")
        account_id = _general_text(raw_split, "account_id")
        if not account_id:
            _raise_general_preview_error("ACCOUNT_NOT_FOUND", f"splits[{index}].account_id")
        amount_text, amount = _validate_general_decimal_string(raw_split.get("amount"), f"splits[{index}].amount")
        memo = _general_text(raw_split, "memo", default="")
        if len(memo) > 512:
            _raise_general_preview_error("INVALID_DECIMAL", f"splits[{index}].memo")
        normalized_splits.append({"account_id": account_id, "amount": amount_text, "memo": memo})
        total += amount
        account_ids.add(account_id)

    if total != Decimal("0"):
        _raise_general_preview_error("UNBALANCED_SPLITS", "splits")
    if len(account_ids) < 2:
        _raise_general_preview_error("INSUFFICIENT_DISTINCT_ACCOUNTS", "splits")
    return {"date": date_text, "description": description, "currency": currency, "splits": normalized_splits}


def _general_preview_account_ids(normalized: dict[str, Any]) -> list[str]:
    account_ids: list[str] = []
    seen: set[str] = set()
    for split in normalized["splits"]:
        account_id = str(split["account_id"])
        if account_id not in seen:
            seen.add(account_id)
            account_ids.append(account_id)
    return account_ids


def _service_list_accounts_by_ids(service: Any, account_ids: set[str] | list[str]) -> list[Any]:
    fetch_by_ids = getattr(service, "list_accounts_by_ids", None)
    ordered_ids = list(account_ids)
    if callable(fetch_by_ids):
        result = fetch_by_ids(ordered_ids)
        if isinstance(result, list):
            return result
        if isinstance(result, tuple):
            return list(result)

    if isinstance(service, GnuCashBookService):
        raise GnuCashReadError("Bounded account lookup is not available for transaction CREATE")

    # Compatibility path for legacy synthetic read-service doubles only. Real
    # product GnuCash services are rejected above when bounded lookup is absent,
    # so product CREATE cannot fall back to list_accounts()/book.accounts.
    accounts = list(service.list_accounts())
    requested = set(ordered_ids)
    return [account for account in accounts if str(getattr(account, "id", "")) in requested]


def _general_account_dto(account: Any) -> dict[str, str]:
    return {
        "id": str(getattr(account, "id", "")),
        "name": str(getattr(account, "name", "")),
        "full_name": str(getattr(account, "full_name", "")),
        "type": str(getattr(account, "type", "") or "UNKNOWN").upper(),
        "currency": str(getattr(account, "currency", "") or "").upper(),
    }


def _general_account_commodity_namespace(account: Any) -> str:
    namespace = getattr(account, "commodity_namespace", None)
    if namespace is None:
        namespace = getattr(getattr(account, "commodity", None), "namespace", None)
    if namespace is None and str(getattr(account, "currency", "") or ""):
        namespace = "CURRENCY"
    return str(namespace or "").upper()


def _general_account_commodity_fraction(account: Any) -> int | None:
    fraction = getattr(account, "commodity_fraction", None)
    if fraction is None:
        fraction = getattr(getattr(account, "commodity", None), "fraction", None)
    if fraction is None:
        return None
    try:
        return int(fraction)
    except (TypeError, ValueError):
        return 0


def _validate_general_amount_fraction(amount_text: str, fraction: int | None, field_path: str) -> None:
    if fraction is None:
        return
    if fraction <= 0:
        _raise_general_preview_error("UNSUPPORTED_COMMODITY", field_path)
    amount = Decimal(amount_text)
    scaled = amount * Decimal(fraction)
    if scaled != scaled.to_integral_value():
        _raise_general_preview_error("INVALID_DECIMAL", field_path)


def _resolve_general_preview_accounts(
    normalized: dict[str, Any],
    accounts: list[Any],
) -> dict[str, dict[str, str]]:
    accounts_by_id = {str(getattr(account, "id", "")): account for account in accounts}
    resolved: dict[str, dict[str, str]] = {}
    currency = str(normalized["currency"])
    for index, split in enumerate(normalized["splits"]):
        account_id = split["account_id"]
        account = accounts_by_id.get(account_id)
        if account is None:
            _raise_general_preview_error("ACCOUNT_NOT_FOUND", f"splits[{index}].account_id")
        if getattr(account, "placeholder", False) or getattr(account, "hidden", False):
            _raise_general_preview_error("ACCOUNT_NOT_POSTABLE", f"splits[{index}].account_id")
        account_type = str(getattr(account, "type", "") or "").upper()
        if account_type not in GENERAL_CREATE_ALLOWED_ACCOUNT_TYPES:
            _raise_general_preview_error("UNSUPPORTED_ACCOUNT_TYPE", f"splits[{index}].account_id")
        if _general_account_commodity_namespace(account) != "CURRENCY":
            _raise_general_preview_error("UNSUPPORTED_COMMODITY", f"splits[{index}].account_id")
        account_currency = str(getattr(account, "currency", "") or "").upper()
        if not account_currency or account_currency == "XXX":
            _raise_general_preview_error("UNSUPPORTED_COMMODITY", f"splits[{index}].account_id")
        if account_currency != currency:
            _raise_general_preview_error("COMMODITY_MISMATCH", f"splits[{index}].account_id")
        _validate_general_amount_fraction(
            str(split["amount"]),
            _general_account_commodity_fraction(account),
            f"splits[{index}].amount",
        )
        resolved[account_id] = _general_account_dto(account)
    return resolved


def _live_source_fingerprint_for_book(
    book: Book,
    settings: Settings,
    *,
    require_fresh: bool = False,
) -> str:
    try:
        evidence = inspect_transaction_create_source(book, settings)
    except Exception:
        evidence = None
    if evidence is None:
        if require_fresh:
            _raise_product_create_error("PREVIEW_STALE", retryable=True)
        return source_fingerprint_for_book(book, settings)
    return source_fingerprint_for_book(
        book,
        settings,
        source_identity=evidence.identity,
        versions=evidence.versions,
        source_base_currency=evidence.base_currency,
    )


def _source_fingerprint_from_pinned_source(
    book: Book,
    settings: Settings,
    pinned_source: TransactionCreatePinnedSource,
) -> str:
    _require_pinned_source_current_for_authorization(pinned_source)
    return source_fingerprint_for_book(
        book,
        settings,
        source_identity=pinned_source.identity,
        versions=pinned_source.versions,
        source_base_currency=pinned_source.base_currency,
    )


def _require_pinned_source_current_for_authorization(pinned_source: TransactionCreatePinnedSource) -> None:
    try:
        pinned_source.verify_current()
    except Exception:
        _raise_product_create_error("PREVIEW_STALE", retryable=True)


def _require_pinned_source_current_after_write(
    pinned_source: TransactionCreatePinnedSource,
    backup_path: str | None,
) -> None:
    try:
        pinned_source.verify_same_file_after_write()
    except Exception as exc:
        _fail_create_readback_verification(backup_path, exc)


def _book_config_for_pinned_source(book: Book, pinned_source: TransactionCreatePinnedSource) -> dict[str, Any]:
    """Return a redirection-safe book config using only the pinned source fd path."""

    return {
        "id": int(book.id),
        "name": str(getattr(book, "name", "") or ""),
        "storage_type": str(getattr(book, "storage_type", "sqlite") or "sqlite"),
        "uri_or_path": pinned_source.fd_path,
        "base_currency": str(getattr(book, "base_currency", "") or "XXX"),
        "backup_source_path": pinned_source.fd_path,
        "backup_path_basis": pinned_source.identity.canonical_path,
        "backup_source_is_pinned_fd": True,
        "disable_piecash_internal_backup": True,
    }


def _enter_product_create_source_or_raise_stale(
    book: Book,
    settings: Settings,
) -> tuple[Any, TransactionCreatePinnedSource]:
    try:
        source_cm = open_transaction_create_source(book, settings, writable=True)
        pinned_source = source_cm.__enter__()
    except Exception:
        _raise_product_create_error("PREVIEW_STALE", retryable=True)
    return source_cm, pinned_source


def _build_general_transaction_create_preview(
    *,
    normalized: dict[str, Any],
    accounts: list[Any],
    book: Book,
    user: User,
    session: Session,
    settings: Settings,
) -> TransactionCreatePreviewDTO:
    policy = evaluate_transaction_create_policy(book, user, session, settings)
    if "CREATE_PERMISSION_DENIED" in policy.blocked_codes:
        raise_transaction_create_error(
            status.HTTP_403_FORBIDDEN,
            "CREATE_PERMISSION_DENIED",
        )
    if str(getattr(book, "base_currency", "") or "").upper() != str(normalized["currency"]).upper():
        raise_transaction_create_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "COMMODITY_MISMATCH",
            field_path="currency",
        )
    account_refs = _resolve_general_preview_accounts(normalized, accounts)
    idempotency_key = str(uuid4())
    idempotency_key_hash = hash_idempotency_key(idempotency_key, settings)
    request_hash = canonical_transaction_create_request_hash(normalized)
    source_fingerprint = _live_source_fingerprint_for_book(book, settings)
    issued_at = datetime.now(timezone.utc)
    token_jti = uuid4().hex
    preview_token = issue_preview_token(
        settings=settings,
        user=user,
        book=book,
        request_hash=request_hash,
        idempotency_key_hash=idempotency_key_hash,
        source_fingerprint=source_fingerprint,
        now=issued_at,
        jti=token_jti,
    )
    warnings = [] if policy.confirm_allowed else [
        {"code": code, "message_key": f"transaction_create.{code.lower()}"}
        for code in policy.blocked_codes
        if code != "CREATE_PERMISSION_DENIED"
    ]
    return TransactionCreatePreviewDTO(
        preview_only=True,
        confirm_allowed=policy.confirm_allowed,
        create_count=1,
        preview_token=preview_token,
        expires_at=(issued_at + timedelta(seconds=600)).isoformat(),
        idempotency_key=idempotency_key,
        create_generation=policy.create_generation,
        date=normalized["date"],
        currency=normalized["currency"],
        description=normalized["description"],
        splits=[
            {
                "index": index,
                "account": account_refs[split["account_id"]],
                "amount": split["amount"],
                "memo": split["memo"],
            }
            for index, split in enumerate(normalized["splits"])
        ],
        warnings=warnings,
    )


def _coerce_transaction_create_preview_request(
    payload: dict[str, Any],
) -> TransactionCreatePreviewRequestDTO:
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="create preview payload must be an object",
        )

    request = TransactionCreatePreviewRequestDTO.model_construct(
        date=_preview_request_text(payload, "date"),
        debit_account_id=_preview_request_text(payload, "debit_account_id"),
        credit_account_id=_preview_request_text(payload, "credit_account_id"),
        amount=_preview_request_text(payload, "amount"),
        currency=_preview_request_text(payload, "currency").upper(),
        description=_preview_request_text(payload, "description"),
        memo=_preview_request_text(payload, "memo", default=""),
    )
    _parse_preview_date(request.date)
    _parse_preview_amount(request.amount)
    return request


def _preview_request_text(payload: dict[str, Any], field_name: str, *, default: str | None = None) -> str:
    if field_name not in payload:
        if default is not None:
            return default
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_name} is required",
        )
    value = payload[field_name]
    if not isinstance(value, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_name} must be a string",
        )
    return value


def _parse_preview_date(value: str) -> date:
    if not value or not value.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="date is required",
        )
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="date must use YYYY-MM-DD format",
        ) from exc


def _parse_preview_amount(value: str) -> Decimal:
    if not value or not value.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="amount is required",
        )
    try:
        amount = Decimal(value)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="amount must be a decimal string",
        ) from exc
    if not amount.is_finite():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=CREATE_PREVIEW_NON_FINITE_AMOUNT_DETAIL,
        )
    if amount <= Decimal("0"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="amount must be greater than zero",
        )
    return amount


def _preview_account_by_id(accounts_by_id: dict[str, Any], account_id: str, field_name: str) -> Any:
    if not account_id or not account_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_name} is required",
        )
    account = accounts_by_id.get(account_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_name} was not found",
        )
    if getattr(account, "placeholder", False) or getattr(account, "hidden", False):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_name} must reference a selectable account",
        )
    return account


def _validate_preview_account_currency(account: Any, currency: str, label: str) -> None:
    account_currency = str(getattr(account, "currency", "") or "").upper()
    if account_currency and account_currency != "XXX" and account_currency != currency:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{label} currency does not match requested currency",
        )


def _preview_account_dto(account: Any) -> TransactionCreatePreviewAccountDTO:
    return TransactionCreatePreviewAccountDTO(
        id=account.id,
        name=account.name,
        full_name=account.full_name,
        type=getattr(account, "type", "UNKNOWN"),
        currency=account.currency,
    )


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


def _write_alpha_transaction_ownership_error_detail(mutation: str) -> str:
    return (
        f"Write-alpha {mutation} is allowed only for transactions created by write-alpha "
        "for this book. Historical or manually imported GnuCash transactions remain read-only."
    )


def _audit_write_alpha_ownership_rejection(
    session: Session,
    *,
    user_id: int,
    book_id: int,
    transaction_id: str,
    mutation: str,
    request_summary: dict[str, Any],
) -> AuditLog:
    """Record a redacted app-metadata audit row for non-owned PATCH/DELETE attempts."""
    detail = _write_alpha_transaction_ownership_error_detail(mutation)
    audit_payload = {
        "action": f"transaction.{mutation.lower()}",
        "transaction_id": transaction_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_summary": request_summary,
        "backup_path": None,
        "backup_artifact_ref": None,
        "ownership_status": "non_owned_rejected",
        "result": "failed",
        "error": detail,
    }
    return _audit_log(
        session,
        user_id,
        book_id,
        f"transaction.{mutation.lower()}",
        audit_payload,
    )


def _require_write_alpha_transaction_ownership(
    session: Session,
    *,
    book_id: int,
    transaction_id: str,
    mutation: str = "mutation",
    audit_user_id: int | None = None,
    audit_request_summary: dict[str, Any] | None = None,
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
        detail = _write_alpha_transaction_ownership_error_detail(mutation)
        if audit_user_id is not None:
            _audit_write_alpha_ownership_rejection(
                session,
                user_id=audit_user_id,
                book_id=book_id,
                transaction_id=transaction_id,
                mutation=mutation,
                request_summary=audit_request_summary or {},
            )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
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


def _mark_owner_writebeta_failure_if_active(book_id: int) -> None:
    """Hard-stop an active owner-writebeta session after routed write failure."""
    try:
        from app.routers.owner_writebeta import mark_owner_writebeta_failure_if_active

        mark_owner_writebeta_failure_if_active(book_id=book_id)
    except Exception:
        logger.warning("Could not mark owner-writebeta failure hard-stop", exc_info=True)


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


def _audit_summary_is_non_owned_rejection(payload: dict[str, Any]) -> bool:
    """Return true for audit rows that safely indicate an ownership guard rejection."""
    if payload.get("ownership_status") == "non_owned_rejected":
        return True
    safe_error = _safe_audit_error(payload.get("error")) or ""
    return "created by write-alpha" in safe_error and "Historical or manually imported" in safe_error


def _audit_summary_last_mutation_type(logs: list[AuditLog]) -> str | None:
    """Return the newest successful mutation action without exposing raw payload details."""
    for log in logs:
        if log.action in WRITE_ALPHA_AUDIT_ACTIONS and _audit_log_result(log) == "success":
            return log.action
    return None


def _parse_audit_window(value: str | None, label: str) -> datetime | None:
    """Parse an ISO datetime filter without accepting path-like/private values."""
    if value is None or not value.strip():
        return None
    text = value.strip()
    if len(text) > 40 or "/" in text or "\\" in text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid {label} filter. Use an ISO timestamp.",
        )
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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


def _fail_create_readback_verification(
    backup_path: str | None,
    exc: Exception | None = None,
) -> NoReturn:
    error = GnuCashCreateReadbackVerificationError(
        CREATE_READBACK_FAILURE_DETAIL,
        backup_path=backup_path,
    )
    if exc is not None:
        raise error from exc
    raise error


def _readback_decimal(value: Any, backup_path: str | None) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        _fail_create_readback_verification(backup_path, exc)
    if not amount.is_finite():
        _fail_create_readback_verification(backup_path)
    return amount


def _format_readback_decimal(value: Decimal) -> str:
    return format(value, "f")


def _request_account_delta_totals(
    request: TransactionCreateRequestDTO,
    backup_path: str | None,
) -> tuple[dict[str, Decimal], dict[str, str]]:
    deltas: dict[str, Decimal] = {}
    currencies: dict[str, str] = {}
    for split in request.splits:
        account_id = str(split.account_id)
        currency = split.currency.upper()
        if account_id in currencies and currencies[account_id] != currency:
            _fail_create_readback_verification(backup_path)
        currencies[account_id] = currency
        deltas[account_id] = deltas.get(account_id, Decimal("0")) + _readback_decimal(
            split.amount,
            backup_path,
        )
    return deltas, currencies


def _read_request_account_balance_snapshot(
    book: Book,
    request: TransactionCreateRequestDTO,
    *,
    backup_path: str | None = None,
    read_book_config: Any | None = None,
) -> ReadbackAccountBalanceSnapshot:
    """Read request account balances through the read-only service for delta checks."""
    account_ids = {str(split.account_id) for split in request.splits}
    try:
        read_service = GnuCashBookService(read_book_config) if read_book_config is not None else transaction_service_for(book)
        accounts = _service_list_accounts_by_ids(read_service, account_ids)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        _fail_create_readback_verification(backup_path, exc)

    snapshot: ReadbackAccountBalanceSnapshot = {}
    for account in accounts:
        account_id = str(getattr(account, "id", ""))
        if account_id not in account_ids:
            continue
        currency = str(getattr(account, "currency", "")).upper()
        balance = _readback_decimal(getattr(account, "balance", "0"), backup_path)
        snapshot[account_id] = (balance, currency)

    if set(snapshot) != account_ids:
        _fail_create_readback_verification(backup_path)
    for split in request.splits:
        account_currency = snapshot[str(split.account_id)][1]
        if account_currency != split.currency.upper():
            _fail_create_readback_verification(backup_path)
    return snapshot


def _readback_split_totals_by_currency(
    splits: list[Any],
    backup_path: str | None,
) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for split in splits:
        currency = str(getattr(split, "currency", "")).upper()
        if not currency:
            _fail_create_readback_verification(backup_path)
        totals[currency] = totals.get(currency, Decimal("0")) + _readback_decimal(
            getattr(split, "amount", "0"),
            backup_path,
        )
    return totals


def _verify_account_balance_deltas(
    book: Book,
    request: TransactionCreateRequestDTO,
    result: TransactionWriteResultDTO,
    before_account_balances: ReadbackAccountBalanceSnapshot,
    *,
    read_book_config: Any | None = None,
) -> tuple[int, dict[str, str]]:
    after_account_balances = _read_request_account_balance_snapshot(
        book,
        request,
        backup_path=result.backup_path,
        read_book_config=read_book_config,
    )
    expected_deltas, account_currencies = _request_account_delta_totals(
        request,
        result.backup_path,
    )
    delta_totals_by_currency: dict[str, Decimal] = {}
    for account_id, expected_delta in expected_deltas.items():
        before_balance, before_currency = before_account_balances[account_id]
        after_balance, after_currency = after_account_balances[account_id]
        expected_currency = account_currencies[account_id]
        if before_currency != expected_currency or after_currency != expected_currency:
            _fail_create_readback_verification(result.backup_path)
        observed_delta = after_balance - before_balance
        if observed_delta != expected_delta:
            _fail_create_readback_verification(result.backup_path)
        delta_totals_by_currency[expected_currency] = (
            delta_totals_by_currency.get(expected_currency, Decimal("0")) + observed_delta
        )

    for total in delta_totals_by_currency.values():
        if total != Decimal("0"):
            _fail_create_readback_verification(result.backup_path)

    return len(expected_deltas), {
        currency: _format_readback_decimal(total)
        for currency, total in sorted(delta_totals_by_currency.items())
    }


def _verify_transaction_create_readback(
    book: Book,
    request: TransactionCreateRequestDTO,
    result: TransactionWriteResultDTO,
    before_account_balances: ReadbackAccountBalanceSnapshot | None = None,
    *,
    read_book_config: Any | None = None,
) -> dict[str, Any]:
    """Read the created transaction and request-account deltas before reporting success."""
    try:
        read_service = GnuCashBookService(read_book_config) if read_book_config is not None else transaction_service_for(book)
        detail = read_service.get_transaction(result.transaction_id)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        _fail_create_readback_verification(result.backup_path, exc)

    request_currencies = sorted({split.currency.upper() for split in request.splits})
    if len(request_currencies) != 1:
        _fail_create_readback_verification(result.backup_path)
    request_currency = request_currencies[0]
    readback_currency = str(getattr(detail, "currency", "")).upper()

    if detail.id != result.transaction_id:
        _fail_create_readback_verification(result.backup_path)
    if detail.date != request.date:
        _fail_create_readback_verification(result.backup_path)
    if detail.description != request.description:
        _fail_create_readback_verification(result.backup_path)
    if readback_currency != request_currency:
        _fail_create_readback_verification(result.backup_path)
    if len(detail.splits) != len(request.splits):
        _fail_create_readback_verification(result.backup_path)
    if _readback_split_signatures(detail.splits, result.backup_path) != _request_split_signatures(
        request.splits,
        result.backup_path,
    ):
        _fail_create_readback_verification(result.backup_path)

    split_totals_by_currency = _readback_split_totals_by_currency(
        detail.splits,
        result.backup_path,
    )
    for total in split_totals_by_currency.values():
        if total != Decimal("0"):
            _fail_create_readback_verification(result.backup_path)

    account_delta_count = 0
    account_delta_totals: dict[str, str] = {}
    account_deltas_verified = False
    if before_account_balances is not None:
        account_delta_count, account_delta_totals = _verify_account_balance_deltas(
            book,
            request,
            result,
            before_account_balances,
            read_book_config=read_book_config,
        )
        account_deltas_verified = True

    return {
        "readback_verified": True,
        "readback_transaction_id": detail.id,
        "readback_transaction_present": True,
        "readback_split_count": len(detail.splits),
        "readback_split_balance_verified": True,
        "readback_split_balance_by_currency": {
            currency: _format_readback_decimal(total)
            for currency, total in sorted(split_totals_by_currency.items())
        },
        "readback_currency": readback_currency,
        "readback_currency_consistent": True,
        "readback_account_balance_deltas_verified": account_deltas_verified,
        "readback_account_balance_delta_count": account_delta_count,
        "readback_account_balance_delta_total_by_currency": account_delta_totals,
    }


def _request_split_signatures(
    splits: list[TransactionSplitWriteDTO],
    backup_path: str | None,
) -> list[tuple[str, Decimal, str, str]]:
    return sorted(
        (
            split.account_id,
            _readback_decimal(split.amount, backup_path),
            split.currency.upper(),
            split.memo or "",
        )
        for split in splits
    )


def _readback_split_signatures(
    splits: list[Any],
    backup_path: str | None,
) -> list[tuple[str, Decimal, str, str]]:
    return sorted(
        (
            str(getattr(split, "account_id", "")),
            _readback_decimal(getattr(split, "amount", "0"), backup_path),
            str(getattr(split, "currency", "")).upper(),
            str(getattr(split, "memo", "") or ""),
        )
        for split in splits
    )


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


def _is_inside_path(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _looks_like_sqlite_book(path: Path) -> bool:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    return any(suffix in SQLITE_BOOK_SUFFIXES for suffix in suffixes)


def _has_disposable_target_marker(path: Path) -> bool:
    marker_text = path.name.lower()
    return any(marker in marker_text for marker in DISPOSABLE_CREATE_TARGET_HINTS)


def _disposable_create_target_blocker(book: Book) -> str | None:
    """Return a path-safe blocker unless this CREATE target is a disposable SQLite file.

    This is a metadata-only preflight. It never opens the GnuCash book, creates a
    backup, acquires a lock, writes an audit row, or calls the write service.
    """
    raw_target = str(getattr(book, "uri_or_path", "") or "").strip()
    if not raw_target:
        return "book target path is not configured"
    if "://" in raw_target:
        return "book target must be a local SQLite fixture file, not a connection URI"

    target = Path(raw_target).expanduser().resolve()
    if not target.exists() or not target.is_file():
        return "book target file is missing or not a regular file"
    if _is_inside_path(target, REPO_ROOT):
        return "book target must be outside the git working tree"
    if not _looks_like_sqlite_book(target):
        return "book target must be a SQLite fixture file"
    if not os.access(target, os.R_OK | os.W_OK):
        return "book target must be readable and writable"
    if not _has_disposable_target_marker(target):
        return (
            "book target filename must mark it as copied/disposable/synthetic test data"
        )
    return None


def _require_disposable_create_target(book: Book) -> None:
    blocker = _disposable_create_target_blocker(book)
    if blocker is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Disposable target preflight failed closed: {blocker}.",
        )


def _clean_harness_value(value: str | None) -> str:
    return "" if value is None else str(value)


def _explicit_issue51_create_harness_attempted(
    *,
    explicit_test_mode: str | None,
    x_issue51_explicit_test_create: str | None,
    x_issue51_synthetic_disposable_proof: str | None,
    x_app_env: str | None,
    x_gnucash_writes_enabled: str | None,
) -> bool:
    return any(
        _clean_harness_value(value)
        for value in (
            explicit_test_mode,
            x_issue51_explicit_test_create,
            x_issue51_synthetic_disposable_proof,
            x_app_env,
            x_gnucash_writes_enabled,
        )
    )


def _require_explicit_issue51_create_harness_scope(
    *,
    settings: Settings,
    book_id: int,
    raw_query: str,
    explicit_test_mode: str | None,
    x_issue51_explicit_test_create: str | None,
    x_issue51_synthetic_disposable_proof: str | None,
    x_app_env: str | None,
    x_gnucash_writes_enabled: str | None,
) -> None:
    """Fail closed for issue #51 explicit CREATE harness query/header smuggling.

    Normal write-alpha tests remain gated by Settings. When a caller advertises
    the issue #51 explicit CREATE harness, every harness marker must match the
    synthetic/disposable proof contract exactly. Header values are not trusted to
    enable writes; they only make incomplete or user-mode harness attempts fail
    before write service construction.
    """
    attempted = _explicit_issue51_create_harness_attempted(
        explicit_test_mode=explicit_test_mode,
        x_issue51_explicit_test_create=x_issue51_explicit_test_create,
        x_issue51_synthetic_disposable_proof=x_issue51_synthetic_disposable_proof,
        x_app_env=x_app_env,
        x_gnucash_writes_enabled=x_gnucash_writes_enabled,
    )
    if not attempted:
        if raw_query:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=CREATE_ROUTE_QUERY_SMUGGLING_DETAIL,
            )
        return

    if (
        raw_query != ISSUE51_EXPLICIT_CREATE_QUERY
        or book_id != ISSUE51_SYNTHETIC_DISPOSABLE_BOOK_ID
        or _clean_harness_value(explicit_test_mode) != ISSUE51_EXPLICIT_TEST_MODE
        or _clean_harness_value(x_issue51_explicit_test_create) != ISSUE51_EXPLICIT_CREATE_HEADER
        or _clean_harness_value(x_issue51_synthetic_disposable_proof)
        != ISSUE51_SYNTHETIC_DISPOSABLE_PROOF
        or _clean_harness_value(x_app_env).lower() != "test"
        or _clean_harness_value(x_gnucash_writes_enabled).lower() != "true"
        or settings.app_env.lower() != "test"
        or not settings.gnucash_writes_enabled
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=EXPLICIT_ISSUE51_CREATE_HARNESS_DETAIL,
        )


def _require_no_non_create_write_route_query_or_issue51_headers(
    *,
    raw_query: str,
    x_issue51_explicit_test_create: str | None,
    x_issue51_synthetic_disposable_proof: str | None,
    x_app_env: str | None,
    x_gnucash_writes_enabled: str | None,
) -> None:
    """Reject explicit CREATE harness/query material on non-CREATE write routes.

    Validate/PATCH/DELETE are part of the write route family but are not the
    issue #51 explicit CREATE harness. They accept no query parameters and never
    trust harness-like headers to select test mode or target safety; failing here
    prevents route/query/header smuggling before book lookup, audit, or service
    construction.
    """
    if raw_query or _explicit_issue51_create_harness_attempted(
        explicit_test_mode=None,
        x_issue51_explicit_test_create=x_issue51_explicit_test_create,
        x_issue51_synthetic_disposable_proof=x_issue51_synthetic_disposable_proof,
        x_app_env=x_app_env,
        x_gnucash_writes_enabled=x_gnucash_writes_enabled,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=NON_CREATE_ISSUE51_HARNESS_SMUGGLING_DETAIL,
        )


def _is_product_create_confirm_payload(payload: Any) -> bool:
    return isinstance(payload, dict) and "preview_token" in payload and "transaction" in payload


def _product_create_error_status(code: str) -> int:
    if code in {
        "PREVIEW_STALE",
        "CREATE_RECOVERY_REQUIRED",
        "CREATE_IN_PROGRESS",
        "IDEMPOTENCY_PAYLOAD_MISMATCH",
        "BOOK_WRITE_BUSY",
        "PREVIEW_TOKEN_EXPIRED",
        "PREVIEW_TOKEN_INVALID",
        "PREVIEW_PAYLOAD_MISMATCH",
    }:
        return status.HTTP_409_CONFLICT
    if code in {"UNSUPPORTED_COMMODITY", "COMMODITY_MISMATCH", "INVALID_DECIMAL"}:
        return status.HTTP_422_UNPROCESSABLE_CONTENT
    if code == "CREATE_PERMISSION_DENIED":
        return status.HTTP_403_FORBIDDEN
    if code == "CREATE_DEPLOYMENT_DISABLED" or code == "CREATE_BOOK_DISABLED":
        return status.HTTP_403_FORBIDDEN
    if code in {"BACKUP_FAILED", "WRITE_FAILED", "CREATE_RESULT_UNKNOWN"}:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_422_UNPROCESSABLE_CONTENT


def _raise_product_create_error(code: str, *, retryable: bool = False, recovery_ref: str | None = None) -> NoReturn:
    headers: dict[str, str] = {}
    if code == "CREATE_IN_PROGRESS":
        headers["Retry-After"] = "1"
    elif code == "BOOK_WRITE_BUSY":
        headers["Retry-After"] = "2"
    raise_transaction_create_error(
        _product_create_error_status(code),
        code,
        retryable=retryable,
        recovery_ref=recovery_ref,
        headers=headers or None,
    )


def _audit_product_transaction_create_confirm(
    session: Session,
    *,
    user_id: int,
    book_id: int,
    result: str,
    normalized: dict[str, Any] | None = None,
    request_hash: str | None = None,
    token_jti_hash: str | None = None,
    idempotency_key_hash: str | None = None,
    generation: int | None = None,
    error_code: str | None = None,
    retryable: bool = False,
    duplicate: bool = False,
    backup_ref: str | None = None,
    transaction_id: str | None = None,
    readback_verified: bool | None = None,
    event_ref: str | None = None,
) -> AuditLog:
    payload = serialize_transaction_create_audit_payload(
        {
            "result": result,
            "event_ref": event_ref,
            "error_code": error_code,
            "retryable": retryable,
            "request_hash_prefix": request_hash[:12] if request_hash else None,
            "token_jti_hash_prefix": token_jti_hash[:12] if token_jti_hash else None,
            "idempotency_key_hash_prefix": idempotency_key_hash[:12] if idempotency_key_hash else None,
            "split_count": len(normalized["splits"]) if normalized else None,
            "currency": normalized.get("currency") if normalized else None,
            "create_generation": generation,
            "duplicate": duplicate,
            "backup_present": bool(backup_ref),
            "backup_artifact_ref": backup_ref,
            "transaction_ref": f"tx_{transaction_id[:12]}" if transaction_id else None,
            "readback_verified": readback_verified,
        }
    )
    log = AuditLog(
        user_id=user_id,
        book_id=book_id,
        action="transaction.create.confirm",
        payload_json=json.dumps(payload, sort_keys=True, separators=(",", ":")),
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def _coerce_product_confirm_transaction(payload: dict[str, Any]) -> tuple[dict[str, Any], TransactionCreateRequestDTO]:
    transaction_payload = payload.get("transaction")
    normalized = _coerce_general_transaction_create_preview_request(transaction_payload)
    request = TransactionCreateRequestDTO(
        date=normalized["date"],
        description=normalized["description"],
        splits=[
            TransactionSplitWriteDTO(
                account_id=split["account_id"],
                amount=split["amount"],
                currency=normalized["currency"],
                memo=split["memo"],
            )
            for split in normalized["splits"]
        ],
    )
    return normalized, request


def _safe_created_result_for_replay(safe_result: dict[str, Any] | None) -> dict[str, Any]:
    result = dict(safe_result or {})
    result["status"] = "already_created"
    return result


def _handle_product_create_idempotency_reservation(
    reservation: Any,
    *,
    session: Session,
    http_response: Response,
    audit_common: dict[str, Any],
) -> dict[str, Any] | None:
    """Return/reject a non-new idempotency state without authorizing a new write."""

    if reservation.status == "already_succeeded":
        replay_result = _safe_created_result_for_replay(reservation.safe_result)
        _audit_product_transaction_create_confirm(
            session,
            result="already_created",
            duplicate=True,
            transaction_id=str(replay_result.get("transaction_id") or ""),
            readback_verified=True,
            **audit_common,
        )
        http_response.status_code = status.HTTP_200_OK
        return replay_result
    if reservation.status in {"payload_mismatch", "in_progress", "recovery_required", "rejected"}:
        code = {
            "payload_mismatch": "IDEMPOTENCY_PAYLOAD_MISMATCH",
            "in_progress": "CREATE_IN_PROGRESS",
            "recovery_required": "CREATE_RECOVERY_REQUIRED",
            "rejected": reservation.record.safe_error_code or "CREATE_REJECTED",
        }[reservation.status]
        _audit_product_transaction_create_confirm(
            session,
            result="indeterminate" if code == "CREATE_RECOVERY_REQUIRED" else "rejected",
            error_code=code,
            retryable=code == "CREATE_IN_PROGRESS",
            **audit_common,
        )
        _raise_product_create_error(
            code,
            retryable=code == "CREATE_IN_PROGRESS",
            recovery_ref=f"rec_{reservation.record.id}" if code == "CREATE_RECOVERY_REQUIRED" else None,
        )
    return None


def _mark_product_create_result_unknown(
    *,
    idempotency: TransactionCreateIdempotencyService,
    reservation: Any,
    session: Session,
    audit_common: dict[str, Any],
    backup_ref: str | None = None,
) -> None:
    """Best-effort terminal marking for post-write phase failures."""

    try:
        idempotency.mark_indeterminate(reservation.record, "CREATE_RESULT_UNKNOWN")
    except Exception:
        logger.warning("Product CREATE idempotency indeterminate marking failed safely", exc_info=True)
    try:
        _audit_product_transaction_create_confirm(
            session,
            result="indeterminate",
            error_code="CREATE_RESULT_UNKNOWN",
            retryable=False,
            backup_ref=backup_ref,
            **audit_common,
        )
    except Exception:
        logger.warning("Product CREATE indeterminate audit failed safely", exc_info=True)


def _product_backup_ref(value: Any) -> str | None:
    backup_ref = _safe_backup_artifact_ref(value)
    if backup_ref and backup_ref.startswith("bkp-"):
        return "bkp_" + backup_ref.removeprefix("bkp-")
    return backup_ref


def _planned_guid_presence(book: Book, planned_transaction_guid: str, *, read_book_config: Any | None = None) -> bool | None:
    try:
        read_service = GnuCashBookService(read_book_config) if read_book_config is not None else transaction_service_for(book)
        read_service.get_transaction(planned_transaction_guid)
    except EntityNotFoundError:
        return False
    except (BookNotFoundError, BookNotConfiguredError, GnuCashReadError):
        return None
    except Exception:
        return None
    return True


def _execute_product_transaction_create(
    *,
    book: Book,
    user: User,
    session: Session,
    request: TransactionCreateRequestDTO,
    planned_transaction_guid: str,
    settings: Settings,
    expected_source_fingerprint: str,
    pinned_source: TransactionCreatePinnedSource,
) -> dict[str, Any]:
    _require_pinned_source_current_for_authorization(pinned_source)
    pinned_book_config = _book_config_for_pinned_source(book, pinned_source)
    service = GnuCashWriteService(pinned_book_config)
    pre_write_evidence: dict[str, Any] = {}

    def revalidate_inside_lock_before_backup() -> None:
        session.refresh(book)
        session.refresh(user)
        policy = evaluate_transaction_create_policy(book, user, session, settings)
        if not policy.confirm_allowed:
            first = policy.blocked_codes[0] if policy.blocked_codes else "CREATE_BOOK_DISABLED"
            _raise_product_create_error(first, retryable=first == "PREVIEW_STALE")
        live_fingerprint = _source_fingerprint_from_pinned_source(
            book,
            settings,
            pinned_source,
        )
        if live_fingerprint != expected_source_fingerprint:
            _raise_product_create_error("PREVIEW_STALE", retryable=True)
        validation = service.validate_transaction_create(request)
        if not validation.valid:
            raise GnuCashWriteError(f"Validation failed: {'; '.join(validation.errors)}")
        pre_write_evidence["before_account_balances"] = _read_request_account_balance_snapshot(
            book,
            request,
            read_book_config=pinned_book_config,
        )
        _require_pinned_source_current_for_authorization(pinned_source)

    if isinstance(service, GnuCashWriteService):
        backup_path, transaction_id = service._execute_write_transaction(
            request,
            f"book:{book.id}",
            planned_transaction_guid=planned_transaction_guid,
            pre_backup_hook=revalidate_inside_lock_before_backup,
        )
        _require_pinned_source_current_after_write(pinned_source, backup_path)
        result = TransactionWriteResultDTO(
            transaction_id=transaction_id,
            backup_path=backup_path or "",
            audit_log_id=None,
        )
    else:
        revalidate_inside_lock_before_backup()
        result = service.create_transaction(request=request, user_id=user.id, book_id=book.id)
    _require_pinned_source_current_after_write(pinned_source, result.backup_path)

    readback_fields = _verify_transaction_create_readback(
        book,
        request,
        result,
        before_account_balances=pre_write_evidence.get("before_account_balances"),
        read_book_config=pinned_book_config,
    )
    _require_pinned_source_current_after_write(pinned_source, result.backup_path)
    _record_write_alpha_transaction_ownership(
        session,
        book_id=book.id,
        transaction_id=result.transaction_id,
        user_id=user.id,
    )
    backup_ref = _product_backup_ref(result.backup_path)
    return {
        "status": "created",
        "transaction_id": result.transaction_id,
        "backup_ref": backup_ref,
        "readback": {
            "verified": True,
            "transaction_present": readback_fields["readback_transaction_present"],
            "split_count": readback_fields["readback_split_count"],
            "balanced": readback_fields["readback_split_balance_verified"],
            "currency_consistent": readback_fields["readback_currency_consistent"],
            "account_balance_deltas_verified": readback_fields["readback_account_balance_deltas_verified"],
        },
        "links": {
            "transaction": f"/books/{book.id}/transactions/{result.transaction_id}",
            "explorer": f"/books/{book.id}/transactions",
        },
    }


def _confirm_product_transaction_create(
    *,
    book_id: int,
    payload: dict[str, Any],
    http_request: Request,
    http_response: Response,
    user: User,
    session: Session,
    settings: Settings,
    idempotency_key: str | None,
    x_issue51_explicit_test_create: str | None,
    x_issue51_synthetic_disposable_proof: str | None,
    x_app_env: str | None,
    x_gnucash_writes_enabled: str | None,
) -> dict[str, Any]:
    _require_no_non_create_write_route_query_or_issue51_headers(
        raw_query=http_request.url.query,
        x_issue51_explicit_test_create=x_issue51_explicit_test_create,
        x_issue51_synthetic_disposable_proof=x_issue51_synthetic_disposable_proof,
        x_app_env=x_app_env,
        x_gnucash_writes_enabled=x_gnucash_writes_enabled,
    )
    if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key) > 256:
        _raise_product_create_error("IDEMPOTENCY_KEY_REQUIRED")
    preview_token = payload.get("preview_token")
    if not isinstance(preview_token, str) or not preview_token:
        _raise_product_create_error("PREVIEW_TOKEN_INVALID")

    normalized, request = _coerce_product_confirm_transaction(payload)
    book = _resolve_viewable_book(book_id, user, session)
    policy = evaluate_transaction_create_policy(book, user, session, settings)
    if not policy.confirm_allowed:
        first = policy.blocked_codes[0] if policy.blocked_codes else "CREATE_BOOK_DISABLED"
        _raise_product_create_error(first, retryable=first == "PREVIEW_STALE")

    request_hash = canonical_transaction_create_request_hash(normalized)
    idempotency_key_hash = hash_idempotency_key(idempotency_key, settings)
    verification = verify_preview_token(
        preview_token,
        settings,
        expected_user_id=int(user.id),
        expected_auth_version=int(getattr(user, "auth_version", 1) or 1),
        expected_book_id=int(book.id),
        expected_generation=policy.create_generation,
        expected_request_hash=request_hash,
        expected_idempotency_key_hash=idempotency_key_hash,
    )
    token_expired = False
    if not verification.valid and verification.code == "PREVIEW_TOKEN_EXPIRED":
        expired_verification = verify_preview_token(
            preview_token,
            settings,
            expected_user_id=int(user.id),
            expected_auth_version=int(getattr(user, "auth_version", 1) or 1),
            expected_book_id=int(book.id),
            expected_generation=policy.create_generation,
            expected_request_hash=request_hash,
            expected_idempotency_key_hash=idempotency_key_hash,
            allow_expired=True,
        )
        if expired_verification.valid:
            verification = expired_verification
            token_expired = True
    if not verification.valid:
        _raise_product_create_error(
            verification.code or "PREVIEW_TOKEN_INVALID",
            retryable=verification.code in {"PREVIEW_STALE", "PREVIEW_TOKEN_EXPIRED"},
        )
    token_jti = str(verification.payload.get("jti", ""))
    token_jti_hash = hash_token_jti(token_jti, settings)

    idempotency = TransactionCreateIdempotencyService(session, settings)
    audit_common = {
        "user_id": int(user.id),
        "book_id": int(book.id),
        "normalized": normalized,
        "request_hash": request_hash,
        "token_jti_hash": token_jti_hash,
        "idempotency_key_hash": idempotency_key_hash,
        "generation": policy.create_generation,
    }

    existing_idempotency = idempotency.find_existing(
        book_id=int(book.id),
        user_id=int(user.id),
        raw_key=idempotency_key,
    )
    if existing_idempotency is not None:
        reservation = idempotency.reserve(
            book_id=int(book.id),
            user_id=int(user.id),
            raw_key=idempotency_key,
            request_hash=request_hash,
            token_jti_hash=token_jti_hash,
        )
        handled_reservation = _handle_product_create_idempotency_reservation(
            reservation,
            session=session,
            http_response=http_response,
            audit_common=audit_common,
        )
        if handled_reservation is not None:
            return handled_reservation

    source_fingerprint = _live_source_fingerprint_for_book(
        book,
        settings,
        require_fresh=True,
    )
    source_verification = verify_preview_token(
        preview_token,
        settings,
        expected_user_id=int(user.id),
        expected_auth_version=int(getattr(user, "auth_version", 1) or 1),
        expected_book_id=int(book.id),
        expected_generation=policy.create_generation,
        expected_request_hash=request_hash,
        expected_idempotency_key_hash=idempotency_key_hash,
        expected_source_fingerprint=source_fingerprint,
        allow_expired=token_expired,
    )
    if not source_verification.valid:
        _raise_product_create_error(
            source_verification.code or "PREVIEW_TOKEN_INVALID",
            retryable=source_verification.code in {"PREVIEW_STALE", "PREVIEW_TOKEN_EXPIRED"},
        )

    reservation = idempotency.reserve(
        book_id=int(book.id),
        user_id=int(user.id),
        raw_key=idempotency_key,
        request_hash=request_hash,
        token_jti_hash=token_jti_hash,
    )
    if token_expired and reservation.status == "reserved":
        idempotency.mark_rejected(reservation.record, "PREVIEW_TOKEN_EXPIRED")
        _audit_product_transaction_create_confirm(
            session,
            result="rejected",
            error_code="PREVIEW_TOKEN_EXPIRED",
            retryable=True,
            **audit_common,
        )
        _raise_product_create_error("PREVIEW_TOKEN_EXPIRED", retryable=True)
    handled_reservation = _handle_product_create_idempotency_reservation(
        reservation,
        session=session,
        http_response=http_response,
        audit_common=audit_common,
    )
    if handled_reservation is not None:
        return handled_reservation

    lock_key = f"book:{book.id}"
    try:
        with write_lock_service.lock(lock_key):
            source_cm = None
            pinned_source: TransactionCreatePinnedSource | None = None
            try:
                _audit_product_transaction_create_confirm(session, result="started", **audit_common)
                try:
                    source_cm, pinned_source = _enter_product_create_source_or_raise_stale(book, settings)
                    result = _execute_product_transaction_create(
                        book=book,
                        user=user,
                        session=session,
                        request=request,
                        planned_transaction_guid=reservation.record.planned_transaction_guid,
                        settings=settings,
                        expected_source_fingerprint=source_fingerprint,
                        pinned_source=pinned_source,
                    )
                except GnuCashCreateReadbackVerificationError as exc:
                    idempotency.mark_indeterminate(reservation.record, "CREATE_RESULT_UNKNOWN")
                    _audit_product_transaction_create_confirm(
                        session,
                        result="indeterminate",
                        error_code="CREATE_RESULT_UNKNOWN",
                        retryable=False,
                        backup_ref=_product_backup_ref(getattr(exc, "backup_path", None)),
                        **audit_common,
                    )
                    _raise_product_create_error(
                        "CREATE_RESULT_UNKNOWN",
                        recovery_ref=f"rec_{reservation.record.id}",
                    )
                except GnuCashWriteError as exc:
                    raw_detail = str(getattr(exc, "detail", "") or exc)
                    backup_path = getattr(exc, "backup_path", None)
                    if not backup_path and "backup failed" in raw_detail.lower():
                        error_code = "BACKUP_FAILED"
                    elif backup_path and pinned_source is not None:
                        planned_present = _planned_guid_presence(
                            book,
                            reservation.record.planned_transaction_guid,
                            read_book_config=_book_config_for_pinned_source(book, pinned_source),
                        )
                        error_code = "WRITE_FAILED" if planned_present is False else "CREATE_RESULT_UNKNOWN"
                    elif backup_path:
                        error_code = "CREATE_RESULT_UNKNOWN"
                    else:
                        error_code = "WRITE_FAILED"
                    if error_code == "CREATE_RESULT_UNKNOWN":
                        idempotency.mark_indeterminate(reservation.record, error_code)
                    else:
                        idempotency.mark_rejected(reservation.record, error_code)
                    _audit_product_transaction_create_confirm(
                        session,
                        result="indeterminate" if error_code == "CREATE_RESULT_UNKNOWN" else "failed",
                        error_code=error_code,
                        retryable=False,
                        backup_ref=_product_backup_ref(getattr(exc, "backup_path", None)),
                        **audit_common,
                    )
                    if error_code == "CREATE_RESULT_UNKNOWN":
                        _raise_product_create_error(
                            error_code,
                            recovery_ref=f"rec_{reservation.record.id}",
                        )
                    _raise_product_create_error(error_code, retryable=False)
                except TransactionCreateHTTPError as exc:
                    idempotency.mark_rejected(reservation.record, exc.code)
                    _audit_product_transaction_create_confirm(
                        session,
                        result="rejected",
                        error_code=exc.code,
                        retryable=exc.retryable,
                        **audit_common,
                    )
                    raise
                except WriteLockError:
                    raise
                except Exception as exc:
                    idempotency.mark_indeterminate(reservation.record, "CREATE_RESULT_UNKNOWN")
                    _audit_product_transaction_create_confirm(
                        session,
                        result="indeterminate",
                        error_code="CREATE_RESULT_UNKNOWN",
                        **audit_common,
                    )
                    _raise_product_create_error(
                        "CREATE_RESULT_UNKNOWN",
                        recovery_ref=f"rec_{reservation.record.id}",
                    )

                result["audit_ref"] = str(result.get("audit_ref") or f"aud_{uuid4().hex[:12]}")
                idempotency.mark_succeeded(reservation.record, result)
                _audit_product_transaction_create_confirm(
                    session,
                    result="success",
                    event_ref=result["audit_ref"].replace("aud_", "evt_", 1),
                    backup_ref=str(result.get("backup_ref") or "") or None,
                    transaction_id=str(result.get("transaction_id") or ""),
                    readback_verified=bool(result.get("readback", {}).get("verified")),
                    **audit_common,
                )
                http_response.status_code = status.HTTP_201_CREATED
                return result
            except WriteLockError:
                raise
            except TransactionCreateHTTPError:
                raise
            except Exception:
                _mark_product_create_result_unknown(
                    idempotency=idempotency,
                    reservation=reservation,
                    session=session,
                    audit_common=audit_common,
                )
                _raise_product_create_error(
                    "CREATE_RESULT_UNKNOWN",
                    recovery_ref=f"rec_{reservation.record.id}",
                )
            finally:
                if source_cm is not None:
                    source_cm.__exit__(None, None, None)
    except WriteLockError as exc:
        idempotency.mark_rejected(reservation.record, "BOOK_WRITE_BUSY")
        _audit_product_transaction_create_confirm(
            session,
            result="busy",
            error_code="BOOK_WRITE_BUSY",
            retryable=True,
            **audit_common,
        )
        _raise_product_create_error("BOOK_WRITE_BUSY", retryable=True)


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
    require_book_storage_configured_for_metadata_summary(book)
    if action is not None and action not in WRITE_ALPHA_AUDIT_ACTIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unsupported audit action filter.",
        )
    if result is not None and result not in WRITE_ALPHA_AUDIT_RESULTS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unsupported audit result filter.",
        )
    since_dt = _parse_audit_window(since, "since")
    until_dt = _parse_audit_window(until, "until")
    if since_dt and until_dt and since_dt > until_dt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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
    ownership_created_count = len(
        session.query(WriteAlphaTransactionOwnership.id)
        .filter(
            WriteAlphaTransactionOwnership.book_id == book.id,
            WriteAlphaTransactionOwnership.created_by_write_alpha == True,  # noqa: E712
        )
        .all()
    )
    non_owned_rejections_count = sum(
        1 for log in filtered_logs if _audit_summary_is_non_owned_rejection(_audit_summary_payload(log))
    )

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
        ownership_summary={
            "write_alpha_created_count": ownership_created_count,
            "non_owned_mutation_rejections_count": non_owned_rejections_count,
            "last_mutation_type": _audit_summary_last_mutation_type(filtered_logs),
        },
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
            f"Ownership evidence: {ownership_created_count} write-alpha-created transaction markers; {non_owned_rejections_count} non-owned mutation rejections in the filtered audit rows.",
            "Rows are redacted to action/result/timestamp/opaque transaction prefix/backup-present/opaque backup reference/safe-error only.",
        ],
        items=[_audit_summary_item(log) for log in logs],
        limitations=[
            "Read-only app metadata summary for synthetic/disposable write-alpha runs only.",
            "Backup paths, private file paths, raw filenames, raw payloads, account names, memos, and amounts are not exposed.",
        ],
    )


@router.post(
    "/books/{book_id}/transactions/create-preview",
    response_model=TransactionCreatePreviewDTO,
    response_model_exclude_none=True,
)
async def preview_book_transaction_create(
    book_id: int,
    request: dict[str, Any],
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TransactionCreatePreviewDTO:
    """Validate and preview one owner web-UI transaction CREATE without writing.

    This endpoint intentionally works while GNUCASH_WRITES_ENABLED=false. It opens
    the selected book read-only to resolve exact account IDs for a private UI
    preview and never constructs the write service, lock, backup, audit, or
    mutation path.
    """
    if _is_general_create_preview_payload(request):
        preview_request = _coerce_general_transaction_create_preview_request(request)
        book = _resolve_readonly_data_book(book_id, user, session)
        policy = evaluate_transaction_create_policy(book, user, session, settings)
        if "CREATE_PERMISSION_DENIED" in policy.blocked_codes:
            raise_transaction_create_error(
                status.HTTP_403_FORBIDDEN,
                "CREATE_PERMISSION_DENIED",
            )
        try:
            service = transaction_service_for(book)
            accounts = _service_list_accounts_by_ids(service, _general_preview_account_ids(preview_request))
        except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
            handle_gnucash_error(exc)
        return _build_general_transaction_create_preview(
            normalized=preview_request,
            accounts=accounts,
            book=book,
            user=user,
            session=session,
            settings=settings,
        )

    preview_request = _coerce_transaction_create_preview_request(request)
    book = _resolve_readonly_data_book(book_id, user, session)
    _require_book_owner_access(book, user, session)
    try:
        service = transaction_service_for(book)
        accounts = service.list_accounts()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return _build_transaction_create_preview(preview_request, accounts)


@router.post(
    "/books/{book_id}/transactions/validate",
    response_model=TransactionValidationResultDTO,
)
async def validate_book_transaction(
    book_id: int,
    request: TransactionCreateRequestDTO,
    http_request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    x_issue51_explicit_test_create: str | None = Header(None),
    x_issue51_synthetic_disposable_proof: str | None = Header(None),
    x_app_env: str | None = Header(None),
    x_gnucash_writes_enabled: str | None = Header(None),
) -> TransactionValidationResultDTO:
    """Validate a transaction create request without writing."""
    _ensure_writes_enabled(settings)
    _ensure_write_alpha_test_scope(settings)
    _require_no_non_create_write_route_query_or_issue51_headers(
        raw_query=http_request.url.query,
        x_issue51_explicit_test_create=x_issue51_explicit_test_create,
        x_issue51_synthetic_disposable_proof=x_issue51_synthetic_disposable_proof,
        x_app_env=x_app_env,
        x_gnucash_writes_enabled=x_gnucash_writes_enabled,
    )
    book = _resolve_viewable_book(book_id, user, session)
    _require_book_edit_access(book, user, session)
    # Validation is part of the write route family: it may construct the
    # write service, so it must prove the target is synthetic/disposable first.
    _require_disposable_create_target(book)

    service = _write_service_for(book)
    return service.validate_transaction_create(request)


@router.post(
    "/books/{book_id}/transactions",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
)
async def create_book_transaction(
    book_id: int,
    request: dict[str, Any],
    http_request: Request,
    http_response: Response,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    explicit_test_mode: str | None = Query(None),
    idempotency_key: str | None = Header(None),
    x_issue51_explicit_test_create: str | None = Header(None),
    x_issue51_synthetic_disposable_proof: str | None = Header(None),
    x_app_env: str | None = Header(None),
    x_gnucash_writes_enabled: str | None = Header(None),
    x_owner_writebeta_preview_hash: str | None = Header(None),
    x_owner_writebeta_confirmation_token: str | None = Header(None),
) -> Any:
    """Create a new transaction with the given splits.

    Follows the strict write flow: validate, lock, backup, write, audit.
    """
    if _is_product_create_confirm_payload(request):
        return _confirm_product_transaction_create(
            book_id=book_id,
            payload=request,
            http_request=http_request,
            http_response=http_response,
            user=user,
            session=session,
            settings=settings,
            idempotency_key=idempotency_key,
            x_issue51_explicit_test_create=x_issue51_explicit_test_create,
            x_issue51_synthetic_disposable_proof=x_issue51_synthetic_disposable_proof,
            x_app_env=x_app_env,
            x_gnucash_writes_enabled=x_gnucash_writes_enabled,
        )

    _ensure_writes_enabled(settings)
    _ensure_write_alpha_test_scope(settings)
    _require_explicit_issue51_create_harness_scope(
        settings=settings,
        book_id=book_id,
        raw_query=http_request.url.query,
        explicit_test_mode=explicit_test_mode,
        x_issue51_explicit_test_create=x_issue51_explicit_test_create,
        x_issue51_synthetic_disposable_proof=x_issue51_synthetic_disposable_proof,
        x_app_env=x_app_env,
        x_gnucash_writes_enabled=x_gnucash_writes_enabled,
    )
    try:
        legacy_request = TransactionCreateRequestDTO.model_validate(request)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=exc.errors()) from exc
    request_dto = legacy_request

    book = _resolve_viewable_book(book_id, user, session)
    _require_book_edit_access(book, user, session)
    _require_disposable_create_target(book)
    from app.routers.owner_writebeta import require_owner_writebeta_if_active

    require_owner_writebeta_if_active(
        book_id=book.id,
        preview_hash=x_owner_writebeta_preview_hash,
        confirmation_token=x_owner_writebeta_confirmation_token,
        operation="CREATE",
        count=1,
    )

    service = _write_service_for(book)
    audit_payload = {
        "action": "transaction.create",
        "transaction_id": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_summary": _request_summary(request_dto),
        "backup_path": None,
        "backup_artifact_ref": None,
        "readback_verified": False,
        "readback_transaction_id": None,
        "readback_transaction_present": False,
        "readback_split_count": None,
        "readback_split_balance_verified": False,
        "readback_split_balance_by_currency": None,
        "readback_currency": None,
        "readback_currency_consistent": False,
        "readback_account_balance_deltas_verified": False,
        "readback_account_balance_delta_count": None,
        "readback_account_balance_delta_total_by_currency": None,
        "result": "started",
    }
    log = _audit_log(session, user.id, book.id, "transaction.create", audit_payload)

    result: TransactionWriteResultDTO | None = None
    readback_fields: dict[str, Any] = {}
    try:
        before_account_balances = None
        if isinstance(service, GnuCashWriteService):
            validation = service.validate_transaction_create(request_dto)
            if not validation.valid:
                raise GnuCashWriteError(
                    f"Validation failed: {'; '.join(validation.errors)}"
                )
            before_account_balances = _read_request_account_balance_snapshot(book, request_dto)
        result = service.create_transaction(
            request=request_dto,
            user_id=user.id,
            book_id=book.id,
        )
        readback_fields = _verify_transaction_create_readback(
            book,
            request_dto,
            result,
            before_account_balances=before_account_balances,
        )
    except WriteLockError as exc:
        _mark_owner_writebeta_failure_if_active(book.id)
        audit_payload.update({"result": "failed", "error": _write_lock_detail()})
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_write_lock_detail(),
        ) from exc
    except GnuCashCreateReadbackVerificationError as exc:
        _mark_owner_writebeta_failure_if_active(book.id)
        safe_detail = _write_error_detail(exc)
        audit_payload.update(
            {
                "result": "failed",
                "transaction_id": result.transaction_id if result is not None else None,
                "readback_verified": False,
                "readback_transaction_id": None,
                "readback_transaction_present": False,
                "readback_split_count": None,
                "readback_split_balance_verified": False,
                "readback_split_balance_by_currency": None,
                "readback_currency": None,
                "readback_currency_consistent": False,
                "readback_account_balance_deltas_verified": False,
                "readback_account_balance_delta_count": None,
                "readback_account_balance_delta_total_by_currency": None,
                "error": safe_detail,
                **_backup_audit_fields(getattr(exc, "backup_path", None)),
            }
        )
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=safe_detail,
        ) from exc
    except GnuCashWriteError as exc:
        _mark_owner_writebeta_failure_if_active(book.id)
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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=safe_detail,
        ) from exc

    audit_payload.update(
        {
            "transaction_id": result.transaction_id,
            **_backup_audit_fields(result.backup_path),
            **readback_fields,
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
    for key, value in readback_fields.items():
        if hasattr(result, key):
            setattr(result, key, value)

    return result


@router.patch(
    "/books/{book_id}/transactions/{transaction_id}",
    response_model=TransactionWriteResultDTO,
)
async def patch_book_transaction(
    book_id: int,
    transaction_id: str,
    request: TransactionPatchRequestDTO,
    http_request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    x_issue51_explicit_test_create: str | None = Header(None),
    x_issue51_synthetic_disposable_proof: str | None = Header(None),
    x_app_env: str | None = Header(None),
    x_gnucash_writes_enabled: str | None = Header(None),
    x_owner_writebeta_preview_hash: str | None = Header(None),
    x_owner_writebeta_confirmation_token: str | None = Header(None),
) -> TransactionWriteResultDTO:
    """Patch description and/or split memos for an existing transaction.

    Does NOT allow editing dates, split amounts, accounts, split structure, or currencies.
    """
    _ensure_writes_enabled(settings)
    _ensure_write_alpha_test_scope(settings)
    _require_no_non_create_write_route_query_or_issue51_headers(
        raw_query=http_request.url.query,
        x_issue51_explicit_test_create=x_issue51_explicit_test_create,
        x_issue51_synthetic_disposable_proof=x_issue51_synthetic_disposable_proof,
        x_app_env=x_app_env,
        x_gnucash_writes_enabled=x_gnucash_writes_enabled,
    )
    book = _resolve_viewable_book(book_id, user, session)
    _require_book_edit_access(book, user, session)
    _require_disposable_create_target(book)
    patch_field_names = [
        k
        for k, v in {
            "description": request.description,
            "split_memos": request.split_memos,
        }.items()
        if v is not None
    ]
    ownership = _require_write_alpha_transaction_ownership(
        session,
        book_id=book.id,
        transaction_id=transaction_id,
        mutation="PATCH",
        audit_user_id=user.id,
        audit_request_summary={"fields_updated": patch_field_names},
    )
    from app.routers.owner_writebeta import require_owner_writebeta_if_active

    require_owner_writebeta_if_active(
        book_id=book.id,
        preview_hash=x_owner_writebeta_preview_hash,
        confirmation_token=x_owner_writebeta_confirmation_token,
        operation="PATCH",
        count=1,
    )

    service = _write_service_for(book)
    fields_updated = {
        k: v
        for k, v in {
            "description": request.description,
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
        _mark_owner_writebeta_failure_if_active(book.id)
        audit_payload.update({"result": "failed", "error": _write_lock_detail()})
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_write_lock_detail(),
        ) from exc
    except GnuCashWriteError as exc:
        _mark_owner_writebeta_failure_if_active(book.id)
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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=safe_detail,
        ) from exc
    except EntityNotFoundError as exc:
        _mark_owner_writebeta_failure_if_active(book.id)
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
    http_request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    x_issue51_explicit_test_create: str | None = Header(None),
    x_issue51_synthetic_disposable_proof: str | None = Header(None),
    x_app_env: str | None = Header(None),
    x_gnucash_writes_enabled: str | None = Header(None),
    x_owner_writebeta_preview_hash: str | None = Header(None),
    x_owner_writebeta_confirmation_token: str | None = Header(None),
) -> TransactionWriteResultDTO:
    """Delete one existing transaction through the experimental write-alpha path."""
    _ensure_writes_enabled(settings)
    _ensure_write_alpha_test_scope(settings)
    _require_no_non_create_write_route_query_or_issue51_headers(
        raw_query=http_request.url.query,
        x_issue51_explicit_test_create=x_issue51_explicit_test_create,
        x_issue51_synthetic_disposable_proof=x_issue51_synthetic_disposable_proof,
        x_app_env=x_app_env,
        x_gnucash_writes_enabled=x_gnucash_writes_enabled,
    )
    book = _resolve_viewable_book(book_id, user, session)
    _require_book_edit_access(book, user, session)
    _require_disposable_create_target(book)
    ownership = _require_write_alpha_transaction_ownership(
        session,
        book_id=book.id,
        transaction_id=transaction_id,
        mutation="DELETE",
        audit_user_id=user.id,
        audit_request_summary={"target_class": "write_alpha_owned_required"},
    )
    from app.routers.owner_writebeta import require_owner_writebeta_if_active

    require_owner_writebeta_if_active(
        book_id=book.id,
        preview_hash=x_owner_writebeta_preview_hash,
        confirmation_token=x_owner_writebeta_confirmation_token,
        operation="DELETE",
        count=1,
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
        _mark_owner_writebeta_failure_if_active(book.id)
        audit_payload.update({"result": "failed", "error": _write_lock_detail()})
        _update_audit_log(session, log, audit_payload)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_write_lock_detail(),
        ) from exc
    except GnuCashWriteError as exc:
        _mark_owner_writebeta_failure_if_active(book.id)
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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=safe_detail,
        ) from exc
    except EntityNotFoundError as exc:
        _mark_owner_writebeta_failure_if_active(book.id)
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
