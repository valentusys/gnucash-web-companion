"""Book-aware and MVP transaction browsing router.

All endpoints are read-only and require auth.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models import Book, User
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
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
)

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
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """List transactions for a viewable book with pagination and filters."""
    book = _resolve_viewable_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
        total = service.count_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        items = service.list_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
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


@router.get("/books/{book_id}/transactions/{transaction_id}")
async def get_book_transaction(
    book_id: int,
    transaction_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one transaction with all splits for a viewable book."""
    book = _resolve_viewable_book(book_id, user, session)
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
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """List transactions for a specific account in a viewable book."""
    book = _resolve_viewable_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
        total = service.count_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        items = service.list_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
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
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """List transactions for the default book."""
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
        total = service.count_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        items = service.list_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
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
    min_amount: Decimal | None = Query(None),
    max_amount: Decimal | None = Query(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """List transactions for a specific account in the default book."""
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
        total = service.count_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        items = service.list_transactions(
            account_id=account_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
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
