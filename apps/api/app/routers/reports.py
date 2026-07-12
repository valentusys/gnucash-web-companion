"""Book-aware and MVP read-only reports router.

All endpoints are read-only and require auth.

Multi-currency limitation:
    Report endpoints only include accounts and splits whose commodity matches the
    book's base currency. Accounts/transactions in other currencies are silently
    excluded. No fake currency conversion is performed.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models import Book, User
from app.routers.accounts import resolve_default_viewable_book
from app.routers.auth import get_current_user, get_db
from app.routers.books import (
    handle_gnucash_error,
    resolve_readonly_data_book,
    transaction_service_for,
)
from app.schemas.gnucash import (
    CashflowDTO,
    CashflowPeriodDTO,
    ExpenseByAccountDTO,
    PeriodReportComparisonDTO,
    PeriodReportDTO,
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

COMPARISON_MODES = {"previous_equivalent", "same_period_last_year", "custom"}


def _serialize_transaction_list_item(item: TransactionListItemDTO) -> dict[str, Any]:
    return item.model_dump()


def _current_month_range() -> tuple[str, str]:
    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    return first_of_month.isoformat(), today.isoformat()


def _parse_report_date(value: str | None, field_name: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} must be a valid YYYY-MM-DD date",
        ) from exc


def _normalize_report_date_range(
    date_from: str | None,
    date_to: str | None,
) -> tuple[str, str]:
    if date_from is None and date_to is None:
        return _current_month_range()
    if date_from is None or date_to is None:
        raise HTTPException(
            status_code=422,
            detail="date_from and date_to must be provided together",
        )
    parsed_from = _parse_report_date(date_from, "date_from")
    parsed_to = _parse_report_date(date_to, "date_to")
    assert parsed_from is not None and parsed_to is not None
    if parsed_from > parsed_to:
        raise HTTPException(
            status_code=422,
            detail="date_from must be on or before date_to",
        )
    return parsed_from.isoformat(), parsed_to.isoformat()


def _normalize_required_report_date_range(date_from: str, date_to: str) -> tuple[date, date]:
    parsed_from = _parse_report_date(date_from, "date_from")
    parsed_to = _parse_report_date(date_to, "date_to")
    assert parsed_from is not None and parsed_to is not None
    if parsed_from > parsed_to:
        raise HTTPException(
            status_code=422,
            detail="date_from must be on or before date_to",
        )
    return parsed_from, parsed_to


def _previous_equivalent_range(date_from: date, date_to: date) -> tuple[date, date]:
    inclusive_days = (date_to - date_from).days + 1
    return date_from - timedelta(days=inclusive_days), date_from - timedelta(days=1)


def _one_year_back_clamped(value: date) -> date:
    target_year = value.year - 1
    target_day = min(value.day, monthrange(target_year, value.month)[1])
    return date(target_year, value.month, target_day)


def _same_period_last_year_range(date_from: date, date_to: date) -> tuple[date, date]:
    return _one_year_back_clamped(date_from), _one_year_back_clamped(date_to)


def _normalize_comparison_query(
    date_from: date,
    date_to: date,
    comparison_mode: str,
    comparison_date_from: str,
    comparison_date_to: str,
) -> tuple[str, date, date]:
    if comparison_mode not in COMPARISON_MODES:
        raise HTTPException(
            status_code=422,
            detail="comparison_mode must be previous_equivalent, same_period_last_year, or custom",
        )
    parsed_comparison_from = _parse_report_date(comparison_date_from, "comparison_date_from")
    parsed_comparison_to = _parse_report_date(comparison_date_to, "comparison_date_to")
    assert parsed_comparison_from is not None and parsed_comparison_to is not None
    if parsed_comparison_from > parsed_comparison_to:
        raise HTTPException(
            status_code=422,
            detail="comparison_date_from must be on or before comparison_date_to",
        )
    if comparison_mode == "custom":
        return comparison_mode, parsed_comparison_from, parsed_comparison_to

    expected_from, expected_to = (
        _previous_equivalent_range(date_from, date_to)
        if comparison_mode == "previous_equivalent"
        else _same_period_last_year_range(date_from, date_to)
    )
    if (parsed_comparison_from, parsed_comparison_to) != (expected_from, expected_to):
        raise HTTPException(
            status_code=422,
            detail=(
                "comparison_date_from and comparison_date_to must match "
                f"{comparison_mode} range {expected_from.isoformat()}..{expected_to.isoformat()}"
            ),
        )
    return comparison_mode, parsed_comparison_from, parsed_comparison_to


# ---------------------------------------------------------------------------
# Book-aware endpoints
# ---------------------------------------------------------------------------


@router.get("/books/{book_id}/reports/comparison", response_model=PeriodReportComparisonDTO)
async def get_book_period_report_comparison(
    book_id: int,
    date_from: str = Query(..., description="Inclusive primary period start as YYYY-MM-DD"),
    date_to: str = Query(..., description="Inclusive primary period end as YYYY-MM-DD"),
    comparison_mode: str = Query(..., description="previous_equivalent, same_period_last_year, or custom"),
    comparison_date_from: str = Query(..., description="Inclusive comparison period start as YYYY-MM-DD"),
    comparison_date_to: str = Query(..., description="Inclusive comparison period end as YYYY-MM-DD"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> PeriodReportComparisonDTO:
    """Return a read-only comparison between two explicit period reports for a viewable book."""
    parsed_from, parsed_to = _normalize_required_report_date_range(date_from, date_to)
    normalized_mode, parsed_comparison_from, parsed_comparison_to = _normalize_comparison_query(
        parsed_from,
        parsed_to,
        comparison_mode,
        comparison_date_from,
        comparison_date_to,
    )
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        return transaction_service_for(book).get_period_report_comparison(
            parsed_from,
            parsed_to,
            parsed_comparison_from,
            parsed_comparison_to,
            comparison_mode=normalized_mode,
            book_id=book.id,
        )
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
        raise


@router.get("/books/{book_id}/reports", response_model=PeriodReportDTO)
async def get_book_period_report(
    book_id: int,
    date_from: str = Query(..., description="Inclusive period start as YYYY-MM-DD"),
    date_to: str = Query(..., description="Inclusive period end as YYYY-MM-DD"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> PeriodReportDTO:
    """Return a combined read-only period report for a viewable book."""
    parsed_from, parsed_to = _normalize_required_report_date_range(date_from, date_to)
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        return transaction_service_for(book).get_period_report(
            parsed_from,
            parsed_to,
            book_id=book.id,
        )
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
        raise


@router.get("/books/{book_id}/reports/summary")
async def get_book_report_summary(
    book_id: int,
    as_of_date: str | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return dashboard summary for a viewable book."""
    parsed_date = _parse_report_date(as_of_date, "as_of_date")
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
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
    date_from, date_to = _normalize_report_date_range(date_from, date_to)
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
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
    date_from, date_to = _normalize_report_date_range(date_from, date_to)
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        service = transaction_service_for(book)
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
    book = resolve_readonly_data_book(book_id, user, session)
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
    parsed_date = _parse_report_date(as_of_date, "as_of_date")
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
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
    date_from, date_to = _normalize_report_date_range(date_from, date_to)
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
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
    date_from, date_to = _normalize_report_date_range(date_from, date_to)
    book = resolve_default_viewable_book(user, session)
    try:
        service = transaction_service_for(book)
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
