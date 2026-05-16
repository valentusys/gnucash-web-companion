"""Book-aware and MVP read-only reports router.

All endpoints are read-only and require auth.

Multi-currency limitation:
    Report endpoints only include accounts and splits whose commodity matches the
    book's base currency. Accounts/transactions in other currencies are silently
    excluded. No fake currency conversion is performed.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models import Book, User
from app.routers.accounts import resolve_default_viewable_book
from app.routers.auth import get_current_user, get_db
from app.routers.books import (
    handle_gnucash_error,
    transaction_service_for,
)
from app.routers.transactions import _resolve_viewable_book
from app.schemas.gnucash import (
    CashflowDTO,
    CashflowPeriodDTO,
    ExpenseByAccountDTO,
    ReportSummaryDTO,
    TransactionListItemDTO,
)
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
)

router = APIRouter(tags=["reports"])


def _serialize_transaction_list_item(item: TransactionListItemDTO) -> dict[str, Any]:
    return item.model_dump()


def _current_month_range() -> tuple[str, str]:
    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    return first_of_month.isoformat(), today.isoformat()


# ---------------------------------------------------------------------------
# Book-aware endpoints
# ---------------------------------------------------------------------------


@router.get("/books/{book_id}/reports/summary")
async def get_book_report_summary(
    book_id: int,
    as_of_date: str | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return dashboard summary for a viewable book."""
    book = _resolve_viewable_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
        parsed_date = None
        if as_of_date:
            parsed_date = date.fromisoformat(as_of_date)
        summary = service.get_report_summary(as_of_date=parsed_date)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return summary.model_dump()


@router.get("/books/{book_id}/reports/cashflow")
async def get_book_cashflow(
    book_id: int,
    date_from: str | None = None,
    date_to: str | None = None,
    by_month: bool = Query(False, description="Group results by month"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any] | list[dict[str, Any]]:
    """Return cashflow for a viewable book over a date range.

    If date_from/date_to are omitted, defaults to current month to today.
    """
    book = _resolve_viewable_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
        if date_from is None or date_to is None:
            date_from, date_to = _current_month_range()
        if by_month:
            periods = service.get_cashflow_by_month(date_from, date_to)
            return [period.model_dump() for period in periods]
        cashflow = service.get_cashflow(date_from, date_to)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    if by_month:
        return []
    return cashflow.model_dump()


@router.get("/books/{book_id}/reports/expenses-by-account")
async def get_book_expenses_by_account(
    book_id: int,
    date_from: str | None = None,
    date_to: str | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return expenses grouped by account for a viewable book.

    If date_from/date_to are omitted, defaults to current month to today.
    """
    book = _resolve_viewable_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
        if date_from is None or date_to is None:
            date_from, date_to = _current_month_range()
        expenses = service.get_expenses_by_account(date_from, date_to)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [expense.model_dump() for expense in expenses]


@router.get("/books/{book_id}/reports/recent-transactions")
async def get_book_recent_transactions(
    book_id: int,
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return the most recent transactions for a viewable book."""
    book = _resolve_viewable_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
        items = service.list_transactions(limit=limit, offset=0)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [_serialize_transaction_list_item(item) for item in items]


# ---------------------------------------------------------------------------
# MVP aliases (default book)
# ---------------------------------------------------------------------------


@router.get("/reports/summary")
async def get_default_report_summary(
    as_of_date: str | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return dashboard summary for the default book."""
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
        parsed_date = None
        if as_of_date:
            parsed_date = date.fromisoformat(as_of_date)
        summary = service.get_report_summary(as_of_date=parsed_date)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return summary.model_dump()


@router.get("/reports/cashflow")
async def get_default_cashflow(
    date_from: str | None = None,
    date_to: str | None = None,
    by_month: bool = Query(False, description="Group results by month"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any] | list[dict[str, Any]]:
    """Return cashflow for the default book over a date range.

    If date_from/date_to are omitted, defaults to current month to today.
    """
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
        if date_from is None or date_to is None:
            date_from, date_to = _current_month_range()
        if by_month:
            periods = service.get_cashflow_by_month(date_from, date_to)
            return [period.model_dump() for period in periods]
        cashflow = service.get_cashflow(date_from, date_to)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    if by_month:
        return []
    return cashflow.model_dump()


@router.get("/reports/expenses-by-account")
async def get_default_expenses_by_account(
    date_from: str | None = None,
    date_to: str | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return expenses grouped by account for the default book.

    If date_from/date_to are omitted, defaults to current month to today.
    """
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
        if date_from is None or date_to is None:
            date_from, date_to = _current_month_range()
        expenses = service.get_expenses_by_account(date_from, date_to)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [expense.model_dump() for expense in expenses]


@router.get("/reports/recent-transactions")
async def get_default_recent_transactions(
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return the most recent transactions for the default book."""
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
        items = service.list_transactions(limit=limit, offset=0)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [_serialize_transaction_list_item(item) for item in items]
