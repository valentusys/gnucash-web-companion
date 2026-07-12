"""Read-only service layer for GnuCash SQL books via piecash."""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Literal, cast

import piecash
from sqlalchemy.orm import joinedload

from app.schemas.gnucash import (
    AccountDTO,
    AccountTreeNodeDTO,
    BookSummaryDTO,
    CashflowDTO,
    CashflowPeriodDTO,
    ExpenseAccountComparisonDeltaDTO,
    ExpenseByAccountDTO,
    MoneyDTO,
    PeriodReportComparisonDTO,
    PeriodReportDTO,
    PeriodReportSectionStatusDTO,
    PeriodReportSummaryDTO,
    CashflowComparisonDeltaDTO,
    ReportComparisonDeltaDTO,
    ReportComparisonSectionStatusDTO,
    ReportMoneyDeltaDTO,
    ReportSummaryComparisonDeltaDTO,
    ReportSummaryDTO,
    ScheduledTransactionDTO,
    ScheduledTransactionRecurrenceDTO,
    TransactionDetailDTO,
    TransactionListItemDTO,
    TransactionSplitDTO,
)
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
)

MONEY_QUANT = Decimal("0.01")
SPLIT_TRANSACTION_LABEL = "Split transaction"
PERIOD_REPORT_SECTION_ERROR_DETAIL = "Report section could not be read safely from this runtime."
REPORT_SECTION_EXCEPTIONS = (BookNotConfiguredError, BookNotFoundError, EntityNotFoundError, GnuCashReadError, ValueError)
SUPPORTED_TRANSACTION_STATES = {
    "unreconciled": "n",
    "cleared": "c",
    "reconciled": "y",
    "voided": "v",
}


@dataclass
class _ReportReadContext:
    """Per-request report read cache scoped to one read-only piecash book open."""

    book: Any
    accounts: list[Any] | None = None
    transactions: list[Any] | None = None


def format_money(value: Any) -> str:
    """Format exact money values as a two-decimal string without using floats."""
    if value is None:
        value = Decimal("0")
    if isinstance(value, float):
        raise TypeError("Money values must not be floats")
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return str(value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP))


def _guid(value: Any) -> str:
    guid = getattr(value, "guid", value)
    return str(guid)


def _date_string(value: Any) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _coerce_date(value: date | str | None) -> date | None:
    if value is None or isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _commodity_code(value: Any, fallback: str = "XXX") -> str:
    if value is None:
        return fallback
    for attr in ("mnemonic", "currency", "code"):
        candidate = getattr(value, attr, None)
        if candidate:
            return str(candidate)
    return str(value) if value else fallback


def account_full_name(account: Any) -> str:
    """Return a colon-separated GnuCash account path."""
    names: list[str] = []
    current = account
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        name = getattr(current, "name", None)
        account_type = str(getattr(current, "type", "") or "").upper()
        is_root_account = account_type == "ROOT" and str(name or "") == "Root Account"
        if name and not is_root_account:
            names.append(str(name))
        current = getattr(current, "parent", None)
    return ":".join(reversed(names))


class GnuCashBookService:
    """Read-only data access service for one configured GnuCash book."""

    def __init__(self, book_config: Any):
        self.book_config = book_config
        self.uri_or_path = self._get_uri_or_path(book_config)
        self.base_currency = self._get_base_currency(book_config)
        self._active_report_context: _ReportReadContext | None = None

    @staticmethod
    def _get_uri_or_path(book_config: Any) -> str | None:
        if book_config is None:
            return None
        if isinstance(book_config, dict):
            return book_config.get("uri_or_path") or book_config.get("path") or book_config.get("uri")
        return getattr(book_config, "uri_or_path", None)

    @staticmethod
    def _get_base_currency(book_config: Any) -> str:
        if isinstance(book_config, dict):
            return str(book_config.get("base_currency") or "XXX")
        return str(getattr(book_config, "base_currency", None) or "XXX")

    @staticmethod
    def _get_book_id(book_config: Any) -> int | None:
        if book_config is None:
            return None
        if isinstance(book_config, dict):
            value = book_config.get("id") or book_config.get("book_id")
        else:
            value = getattr(book_config, "id", None)
        if value is None:
            return None
        return int(value)

    def _validate_configured_book(self) -> str:
        if not self.uri_or_path or not str(self.uri_or_path).strip():
            raise BookNotConfiguredError()
        uri_or_path = str(self.uri_or_path)
        if "://" not in uri_or_path and not Path(uri_or_path).exists():
            raise BookNotFoundError(uri_or_path)
        return uri_or_path

    def _open_piecash_book(self, uri_or_path: str):
        """Open a piecash book in read-only mode for paths and SQL connection URIs."""
        if "://" in uri_or_path:
            return piecash.open_book(uri_conn=uri_or_path, readonly=True)
        return piecash.open_book(uri_or_path, readonly=True)

    @contextmanager
    def _open_report_section_book(self):
        """Yield the active report book or open a short-lived read-only section book.

        Period report sections keep their historical error boundaries. The
        comparison endpoint installs a request-local context so repeated sections
        can reuse one read-only piecash handle and loaded account/transaction
        lists without caching private book data beyond this service call.
        """
        if self._active_report_context is not None:
            yield self._active_report_context.book
            return
        with self._open_book() as book:
            yield book

    @contextmanager
    def _use_report_read_context(self, book: Any):
        previous = self._active_report_context
        self._active_report_context = _ReportReadContext(book=book)
        try:
            yield
        finally:
            self._active_report_context = previous

    def _report_accounts(self, book: Any) -> Iterable[Any]:
        context = self._active_report_context
        if context is not None and context.book is book:
            if context.accounts is None:
                context.accounts = list(self._accounts(book))
            return context.accounts
        return self._accounts(book)

    def _report_transactions(self, book: Any) -> Iterable[Any]:
        context = self._active_report_context
        if context is not None and context.book is book:
            if context.transactions is None:
                context.transactions = list(self._transactions(book))
            return context.transactions
        return self._transactions(book)

    @contextmanager
    def _open_book(self):
        uri_or_path = self._validate_configured_book()
        book = None
        try:
            book = self._open_piecash_book(uri_or_path)
            yield book
        except (BookNotConfiguredError, BookNotFoundError, EntityNotFoundError):
            raise
        except Exception as exc:  # pragma: no cover - exact piecash exceptions vary by backend
            raise GnuCashReadError(str(exc)) from exc
        finally:
            if book is not None:
                close = getattr(book, "close", None)
                if callable(close):
                    close()

    def check_connection(self) -> bool:
        """Open and immediately close the configured book in read-only mode."""
        with self._open_book():
            return True

    def list_accounts(self) -> list[AccountDTO]:
        with self._open_book() as book:
            return [self._account_to_dto(account) for account in self._accounts(book)]

    def get_account(self, account_id: str) -> AccountDTO:
        with self._open_book() as book:
            account = self._find_account(book, account_id)
            if account is None:
                raise EntityNotFoundError("account", account_id)
            return self._account_to_dto(account)

    def get_account_tree(self) -> list[AccountTreeNodeDTO]:
        with self._open_book() as book:
            accounts = list(self._accounts(book))
            nodes = {self._account_id(account): self._account_to_tree_node(account) for account in accounts}
            roots: list[AccountTreeNodeDTO] = []
            for account in accounts:
                node = nodes[self._account_id(account)]
                parent = getattr(account, "parent", None)
                parent_id = self._account_id(parent) if parent is not None else None
                if parent_id and parent_id in nodes:
                    nodes[parent_id].children.append(node)
                else:
                    roots.append(node)
            return roots

    def list_transactions(
        self,
        account_id: str | None = None,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
        query: str | None = None,
        transaction_state: str | None = None,
        min_amount: Decimal | str | None = None,
        max_amount: Decimal | str | None = None,
        limit: int = 50,
        offset: int = 0,
        max_limit: int = 500,
    ) -> list[TransactionListItemDTO]:
        limit = max(0, min(limit, max_limit))
        offset = max(0, offset)
        start = _coerce_date(date_from)
        end = _coerce_date(date_to)
        normalized_query = query.lower() if query else None
        normalized_state = self._normalize_transaction_state(transaction_state)
        min_decimal = self._optional_decimal(min_amount)
        max_decimal = self._optional_decimal(max_amount)
        with self._open_book() as book:
            items: list[TransactionListItemDTO] = []
            for transaction in self._candidate_transactions(book, account_id):
                if not self._transaction_matches(
                    transaction,
                    account_id,
                    start,
                    end,
                    normalized_query,
                    normalized_state,
                    min_decimal,
                    max_decimal,
                ):
                    continue
                items.append(self._transaction_to_list_item(transaction, account_id))
            items.sort(key=lambda item: (item.date, item.id), reverse=True)
            return items[offset : offset + limit]

    def get_transaction(self, transaction_id: str) -> TransactionDetailDTO:
        with self._open_book() as book:
            transaction = self._find_transaction(book, transaction_id)
            if transaction is None:
                raise EntityNotFoundError("transaction", transaction_id)
            return self._transaction_to_detail(transaction)

    def list_scheduled_transactions(self) -> list[ScheduledTransactionDTO]:
        """Return safe read-only scheduled transaction metadata.

        This intentionally exposes only summary fields supported by piecash and does
        not compute or predict next-run dates.
        """
        with self._open_book() as book:
            items = [self._scheduled_transaction_to_dto(item) for item in self._scheduled_transactions(book)]
            items.sort(key=lambda item: ((item.start_date or "9999-99-99"), item.name.lower(), item.id))
            return items

    def count_transactions(
        self,
        account_id: str | None = None,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
        query: str | None = None,
        transaction_state: str | None = None,
        min_amount: Decimal | str | None = None,
        max_amount: Decimal | str | None = None,
    ) -> int:
        start = _coerce_date(date_from)
        end = _coerce_date(date_to)
        normalized_query = query.lower() if query else None
        normalized_state = self._normalize_transaction_state(transaction_state)
        min_decimal = self._optional_decimal(min_amount)
        max_decimal = self._optional_decimal(max_amount)
        with self._open_book() as book:
            return sum(
                1
                for transaction in self._candidate_transactions(book, account_id)
                if self._transaction_matches(
                    transaction,
                    account_id,
                    start,
                    end,
                    normalized_query,
                    normalized_state,
                    min_decimal,
                    max_decimal,
                )
            )

    def get_summary(self) -> BookSummaryDTO:
        with self._open_book() as book:
            accounts = list(self._accounts(book))
            transactions = list(self._transactions(book))
            return BookSummaryDTO(
                account_count=len(accounts),
                transaction_count=len(transactions),
                currency=self.base_currency,
            )

    def get_cashflow(self, date_from: date | str, date_to: date | str) -> CashflowDTO:
        start = _coerce_date(date_from)
        end = _coerce_date(date_to)
        if start is None or end is None:
            raise ValueError("date_from and date_to are required")
        inflow = Decimal("0")
        outflow = Decimal("0")
        with self._open_report_section_book() as book:
            for transaction in self._report_transactions(book):
                tx_date = _coerce_date(self._transaction_date(transaction))
                if tx_date is None or tx_date < start or tx_date > end:
                    continue
                for split in self._splits(transaction):
                    account = getattr(split, "account", None)
                    account_type = str(getattr(account, "type", "")).upper()
                    if account_type not in {"INCOME", "EXPENSE"}:
                        continue
                    currency = self._account_currency(account)
                    if currency != self.base_currency:
                        continue
                    amount = self._split_amount(split)
                    if account_type == "INCOME":
                        if amount <= 0:
                            inflow += abs(amount)
                        else:
                            outflow += amount
                    elif account_type == "EXPENSE":
                        if amount >= 0:
                            outflow += amount
                        else:
                            inflow += abs(amount)
        net = inflow - outflow
        return CashflowDTO(
            date_from=start.isoformat(),
            date_to=end.isoformat(),
            currency=self.base_currency,
            inflow=format_money(inflow),
            outflow=format_money(outflow),
            net=format_money(net),
        )

    def get_report_summary(self, as_of_date: date | str | None = None) -> ReportSummaryDTO:
        """Return dashboard summary: net worth, assets, liabilities, income/expenses this month.

        Multi-currency limitation: only accounts whose commodity matches the book's
        base currency are included. Accounts in other currencies are silently excluded
        from asset/liability totals.
        """
        as_of = _coerce_date(as_of_date) or date.today()
        today = as_of
        month_start = date(today.year, today.month, 1)
        asset_account_types = {"ASSET", "BANK", "CASH", "RECEIVABLE", "STOCK", "MUTUAL"}
        liability_account_types = {"LIABILITY", "CREDIT", "PAYABLE"}
        assets = Decimal("0")
        liabilities = Decimal("0")
        split_assets = Decimal("0")
        split_liabilities = Decimal("0")
        saw_base_currency_balance_split = False
        excluded_currencies: set[str] = set()
        base_currency_account_count = 0
        income_this_month = Decimal("0")
        expenses_this_month = Decimal("0")
        with self._open_report_section_book() as book:
            for account in self._report_accounts(book):
                account_type = str(getattr(account, "type", "")).upper()
                currency = self._account_currency(account)
                if currency != self.base_currency:
                    excluded_currencies.add(currency or "unknown")
                    continue
                base_currency_account_count += 1
                if account_type in asset_account_types:
                    assets += self._account_balance(account)
                elif account_type in liability_account_types:
                    liabilities += self._account_balance(account)
            for transaction in self._report_transactions(book):
                tx_date = _coerce_date(self._transaction_date(transaction))
                if tx_date is None or tx_date > today:
                    continue
                in_current_month = tx_date >= month_start
                for split in self._splits(transaction):
                    account = getattr(split, "account", None)
                    if account is None:
                        continue
                    account_type = str(getattr(account, "type", "")).upper()
                    currency = self._account_currency(account)
                    if currency != self.base_currency:
                        excluded_currencies.add(currency or "unknown")
                        continue
                    amount = self._split_amount(split)
                    if account_type in asset_account_types:
                        split_assets += amount
                        saw_base_currency_balance_split = True
                    elif account_type in liability_account_types:
                        split_liabilities += amount
                        saw_base_currency_balance_split = True
                    if not in_current_month:
                        continue
                    if account_type == "INCOME":
                        if amount < 0:
                            income_this_month += abs(amount)
                        else:
                            expenses_this_month += amount
                    elif account_type == "EXPENSE":
                        if amount >= 0:
                            expenses_this_month += amount
                        else:
                            income_this_month += abs(amount)
        if assets == 0 and liabilities == 0 and saw_base_currency_balance_split:
            assets = split_assets
            liabilities = split_liabilities
        net_worth = assets + liabilities  # liabilities are already negative
        limitations = self._report_summary_limitations(
            base_currency=self.base_currency,
            excluded_currencies=excluded_currencies,
            base_currency_account_count=base_currency_account_count,
        )
        return ReportSummaryDTO(
            currency=self.base_currency,
            net_worth=format_money(net_worth),
            assets=format_money(assets),
            liabilities=format_money(liabilities),
            income_this_month=format_money(income_this_month),
            expenses_this_month=format_money(-expenses_this_month),
            as_of_date=today.isoformat(),
            reporting_basis="base_currency_only",
            includes_currency_conversion=False,
            limitations=limitations,
        )

    @staticmethod
    def _report_summary_limitations(
        *,
        base_currency: str,
        excluded_currencies: set[str],
        base_currency_account_count: int,
    ) -> list[str]:
        """Return user-facing limitations for dashboard/reporting totals.

        Keep wording explicit so API consumers cannot mistake the summary for a
        converted multi-currency net worth. The money values remain Decimal/string
        formatted elsewhere; this helper only builds copy from currency codes.
        """
        limitations = [
            "Dashboard totals use reporting_basis=base_currency_only and include no currency conversion.",
            f"Only accounts and splits whose commodity is {base_currency} are included in reported totals.",
        ]
        if excluded_currencies:
            currencies = ", ".join(sorted(excluded_currencies))
            limitations.append(
                f"Other detected currencies ({currencies}) are excluded rather than converted or combined."
            )
        if base_currency == "XXX":
            limitations.append(
                "The configured base currency is unknown (XXX), so zero totals may mean no matching base-currency accounts rather than an empty book."
            )
        elif base_currency_account_count == 0:
            limitations.append(
                f"No accounts with base currency {base_currency} were detected; zero totals may reflect a currency-configuration mismatch."
            )
        return limitations

    def get_expenses_by_account(
        self,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
    ) -> list[ExpenseByAccountDTO]:
        """Return total expenses grouped by expense account within a date range.

        Multi-currency limitation: only splits whose account commodity matches the
        book's base currency are included.
        """
        start = _coerce_date(date_from)
        end = _coerce_date(date_to)
        totals: dict[str, Decimal] = {}
        account_names: dict[str, str] = {}
        account_currencies: dict[str, str] = {}
        with self._open_report_section_book() as book:
            for transaction in self._report_transactions(book):
                tx_date = _coerce_date(self._transaction_date(transaction))
                if tx_date is None:
                    continue
                if start is not None and tx_date < start:
                    continue
                if end is not None and tx_date > end:
                    continue
                for split in self._splits(transaction):
                    account = getattr(split, "account", None)
                    if account is None:
                        continue
                    account_type = str(getattr(account, "type", "")).upper()
                    if account_type != "EXPENSE":
                        continue
                    currency = self._account_currency(account)
                    if currency != self.base_currency:
                        continue
                    amount = self._split_amount(split)
                    account_id = self._account_id(account)
                    if account_id not in totals:
                        totals[account_id] = Decimal("0")
                        account_names[account_id] = account_full_name(account)
                        account_currencies[account_id] = currency
                    if amount >= 0:
                        totals[account_id] += amount
                    else:
                        totals[account_id] -= abs(amount)
        result = [
            ExpenseByAccountDTO(
                account_id=aid,
                account_name=account_names.get(aid, ""),
                total=format_money(totals[aid]),
                currency=account_currencies.get(aid, self.base_currency),
            )
            for aid in totals
        ]
        result.sort(key=lambda x: Decimal(x.total), reverse=True)
        return result

    def get_cashflow_by_month(
        self,
        date_from: date | str,
        date_to: date | str,
    ) -> list[CashflowPeriodDTO]:
        """Return cashflow totals broken down by month within a date range."""
        start = _coerce_date(date_from)
        end = _coerce_date(date_to)
        if start is None or end is None:
            raise ValueError("date_from and date_to are required")
        months: dict[str, dict[str, Decimal]] = {}
        with self._open_report_section_book() as book:
            for transaction in self._report_transactions(book):
                tx_date = _coerce_date(self._transaction_date(transaction))
                if tx_date is None or tx_date < start or tx_date > end:
                    continue
                month_key = f"{tx_date.year:04d}-{tx_date.month:02d}"
                if month_key not in months:
                    months[month_key] = {"inflow": Decimal("0"), "outflow": Decimal("0")}
                for split in self._splits(transaction):
                    account = getattr(split, "account", None)
                    if account is None:
                        continue
                    account_type = str(getattr(account, "type", "")).upper()
                    if account_type not in {"INCOME", "EXPENSE"}:
                        continue
                    currency = self._account_currency(account)
                    if currency != self.base_currency:
                        continue
                    amount = self._split_amount(split)
                    if account_type == "INCOME":
                        if amount <= 0:
                            months[month_key]["inflow"] += abs(amount)
                        else:
                            months[month_key]["outflow"] += amount
                    elif account_type == "EXPENSE":
                        if amount >= 0:
                            months[month_key]["outflow"] += amount
                        else:
                            months[month_key]["inflow"] += abs(amount)
        result = [
            CashflowPeriodDTO(
                month=key,
                inflow=format_money(values["inflow"]),
                outflow=format_money(values["outflow"]),
                net=format_money(values["inflow"] - values["outflow"]),
            )
            for key, values in sorted(months.items())
        ]
        return result

    def get_period_report(
        self,
        date_from: date | str,
        date_to: date | str,
        *,
        book_id: int | None = None,
    ) -> PeriodReportDTO:
        """Return a combined read-only period report with per-section status.

        Existing report helpers remain the source of truth for each section. This
        orchestration layer makes partial failures explicit instead of letting a
        failed section look like a genuine empty list or zero total.
        """
        start = _coerce_date(date_from)
        end = _coerce_date(date_to)
        if start is None or end is None:
            raise ValueError("date_from and date_to are required")
        if start > end:
            raise ValueError("date_from must be on or before date_to")

        resolved_book_id = book_id if book_id is not None else self._get_book_id(self.book_config)
        summary: PeriodReportSummaryDTO | None = None
        cashflow: CashflowDTO | None = None
        monthly_cashflow: list[CashflowPeriodDTO] = []
        expenses_by_account: list[ExpenseByAccountDTO] = []
        section_statuses: list[PeriodReportSectionStatusDTO] = []
        limitations = self._period_report_base_limitations(self.base_currency)

        try:
            dashboard_summary = self.get_report_summary(as_of_date=end)
            limitations = self._merge_limitations(limitations, dashboard_summary.limitations)
            summary = self._period_report_summary_from_report_summary(dashboard_summary)
            section_statuses.append(
                self._period_report_section_status(
                    "summary",
                    "empty" if self._period_report_summary_is_empty(summary) else "ok",
                )
            )
        except REPORT_SECTION_EXCEPTIONS:
            section_statuses.append(self._period_report_section_error("summary"))

        try:
            cashflow = self.get_cashflow(start, end)
            section_statuses.append(
                self._period_report_section_status(
                    "cashflow",
                    "empty" if self._cashflow_is_empty(cashflow) else "ok",
                )
            )
        except REPORT_SECTION_EXCEPTIONS:
            section_statuses.append(self._period_report_section_error("cashflow"))

        try:
            monthly_cashflow = self.get_cashflow_by_month(start, end)
            section_statuses.append(
                self._period_report_section_status(
                    "monthly_cashflow",
                    "empty" if not monthly_cashflow else "ok",
                )
            )
        except REPORT_SECTION_EXCEPTIONS:
            monthly_cashflow = []
            section_statuses.append(self._period_report_section_error("monthly_cashflow"))

        try:
            expenses_by_account = self.get_expenses_by_account(start, end)
            section_statuses.append(
                self._period_report_section_status(
                    "expenses_by_account",
                    "empty" if not expenses_by_account else "ok",
                )
            )
        except REPORT_SECTION_EXCEPTIONS:
            expenses_by_account = []
            section_statuses.append(self._period_report_section_error("expenses_by_account"))

        partial_failure = any(section.status == "error" for section in section_statuses)
        empty = not partial_failure and all(section.status == "empty" for section in section_statuses)
        currency = summary.currency if summary is not None else cashflow.currency if cashflow is not None else self.base_currency
        return PeriodReportDTO(
            book_id=resolved_book_id or 0,
            date_from=start.isoformat(),
            date_to=end.isoformat(),
            currency=currency,
            reporting_basis="base_currency_only",
            includes_currency_conversion=False,
            limitations=limitations,
            partial_failure=partial_failure,
            empty=empty,
            section_statuses=section_statuses,
            summary=summary,
            cashflow=cashflow,
            monthly_cashflow=monthly_cashflow,
            expenses_by_account=expenses_by_account,
        )

    def get_period_report_comparison(
        self,
        date_from: date | str,
        date_to: date | str,
        comparison_date_from: date | str,
        comparison_date_to: date | str,
        *,
        comparison_mode: str,
        book_id: int | None = None,
    ) -> PeriodReportComparisonDTO:
        """Return two read-only period reports plus Decimal-string comparison deltas."""
        try:
            with self._open_book() as book:
                with self._use_report_read_context(book):
                    primary = self.get_period_report(date_from, date_to, book_id=book_id)
                    comparison = self.get_period_report(comparison_date_from, comparison_date_to, book_id=book_id)
        except REPORT_SECTION_EXCEPTIONS:
            primary = self.get_period_report(date_from, date_to, book_id=book_id)
            comparison = self.get_period_report(comparison_date_from, comparison_date_to, book_id=book_id)
        delta = self._period_report_comparison_delta(primary, comparison)
        limitations = self._merge_limitations(
            [
                "Comparison deltas use exact Decimal arithmetic over base-currency-only period report values.",
                "Comparison deltas include no currency conversion; non-base currencies remain excluded from source reports.",
            ],
            primary.limitations,
            comparison.limitations,
            [
                "One or more comparison deltas are not comparable because a source section failed or currencies/account identities were unsafe to combine."
            ]
            if not delta.comparable
            else [],
        )
        return PeriodReportComparisonDTO(
            book_id=book_id if book_id is not None else primary.book_id,
            comparison_mode=cast(
                Literal["previous_equivalent", "same_period_last_year", "custom"],
                comparison_mode,
            ),
            reporting_basis=delta.reporting_basis,
            includes_currency_conversion=delta.includes_currency_conversion,
            primary=primary,
            comparison=comparison,
            limitations=limitations,
            comparable=delta.comparable,
            partial_failure=delta.partial_failure,
            empty=primary.empty and comparison.empty and not delta.partial_failure,
            delta_section_statuses=delta.section_statuses,
            summary_delta=delta.summary,
            cashflow_delta=delta.cashflow,
            expense_changes=delta.expenses_by_account,
        )

    def _period_report_comparison_delta(
        self,
        primary: PeriodReportDTO,
        comparison: PeriodReportDTO,
    ) -> ReportComparisonDeltaDTO:
        shared_currency, currency_detail = self._comparison_shared_currency(primary, comparison)
        currency = shared_currency or primary.currency or comparison.currency or self.base_currency
        section_statuses: list[ReportComparisonSectionStatusDTO] = []

        summary = self._summary_comparison_delta(
            primary,
            comparison,
            shared_currency=shared_currency,
            currency_detail=currency_detail,
            section_statuses=section_statuses,
        )
        cashflow = self._cashflow_comparison_delta(
            primary,
            comparison,
            shared_currency=shared_currency,
            currency_detail=currency_detail,
            section_statuses=section_statuses,
        )
        expenses = self._expenses_comparison_delta(
            primary,
            comparison,
            shared_currency=shared_currency,
            currency_detail=currency_detail,
            section_statuses=section_statuses,
        )

        partial_failure = primary.partial_failure or comparison.partial_failure or any(
            status.status == "error" for status in section_statuses
        )
        comparable = (
            shared_currency is not None
            and not partial_failure
            and all(status.status in {"ok", "empty"} for status in section_statuses)
            and all(row.status == "ok" for row in expenses)
        )
        return ReportComparisonDeltaDTO(
            currency=currency,
            reporting_basis="base_currency_only",
            includes_currency_conversion=False,
            comparable=comparable,
            partial_failure=partial_failure,
            section_statuses=section_statuses,
            summary=summary,
            cashflow=cashflow,
            expenses_by_account=expenses,
        )

    @staticmethod
    def _comparison_shared_currency(
        primary: PeriodReportDTO,
        comparison: PeriodReportDTO,
    ) -> tuple[str | None, str | None]:
        if primary.currency == "XXX" or comparison.currency == "XXX":
            return None, "Comparison deltas are not comparable when either period currency is unknown (XXX)."
        if primary.currency != comparison.currency:
            return None, "Comparison deltas are not comparable across different period currencies."
        return primary.currency, None

    def _summary_comparison_delta(
        self,
        primary: PeriodReportDTO,
        comparison: PeriodReportDTO,
        *,
        shared_currency: str | None,
        currency_detail: str | None,
        section_statuses: list[ReportComparisonSectionStatusDTO],
    ) -> ReportSummaryComparisonDeltaDTO | None:
        primary_status = self._period_report_section_status_value(primary, "summary")
        comparison_status = self._period_report_section_status_value(comparison, "summary")
        if primary_status == "error" or comparison_status == "error" or primary.summary is None or comparison.summary is None:
            section_statuses.append(self._comparison_section_status("summary", "error", PERIOD_REPORT_SECTION_ERROR_DETAIL))
            return None
        if shared_currency is None:
            section_statuses.append(self._comparison_section_status("summary", "not_comparable", currency_detail))
            return None
        section_statuses.append(
            self._comparison_section_status(
                "summary",
                "empty" if primary_status == "empty" and comparison_status == "empty" else "ok",
            )
        )
        return ReportSummaryComparisonDeltaDTO(
            currency=shared_currency,
            net_worth=self._money_delta(primary.summary.net_worth, comparison.summary.net_worth, shared_currency),
            assets=self._money_delta(primary.summary.assets, comparison.summary.assets, shared_currency),
            liabilities=self._money_delta(primary.summary.liabilities, comparison.summary.liabilities, shared_currency),
        )

    def _cashflow_comparison_delta(
        self,
        primary: PeriodReportDTO,
        comparison: PeriodReportDTO,
        *,
        shared_currency: str | None,
        currency_detail: str | None,
        section_statuses: list[ReportComparisonSectionStatusDTO],
    ) -> CashflowComparisonDeltaDTO | None:
        primary_status = self._period_report_section_status_value(primary, "cashflow")
        comparison_status = self._period_report_section_status_value(comparison, "cashflow")
        if primary_status == "error" or comparison_status == "error" or primary.cashflow is None or comparison.cashflow is None:
            section_statuses.append(self._comparison_section_status("cashflow", "error", PERIOD_REPORT_SECTION_ERROR_DETAIL))
            return None
        if shared_currency is None:
            section_statuses.append(self._comparison_section_status("cashflow", "not_comparable", currency_detail))
            return None
        if primary.cashflow.currency != shared_currency or comparison.cashflow.currency != shared_currency:
            section_statuses.append(
                self._comparison_section_status("cashflow", "not_comparable", "Cashflow currencies do not match the shared comparison currency.")
            )
            return None
        section_statuses.append(
            self._comparison_section_status(
                "cashflow",
                "empty" if primary_status == "empty" and comparison_status == "empty" else "ok",
            )
        )
        return CashflowComparisonDeltaDTO(
            currency=shared_currency,
            inflow=self._money_delta(primary.cashflow.inflow, comparison.cashflow.inflow, shared_currency),
            outflow=self._money_delta(primary.cashflow.outflow, comparison.cashflow.outflow, shared_currency),
            net=self._money_delta(primary.cashflow.net, comparison.cashflow.net, shared_currency),
        )

    def _expenses_comparison_delta(
        self,
        primary: PeriodReportDTO,
        comparison: PeriodReportDTO,
        *,
        shared_currency: str | None,
        currency_detail: str | None,
        section_statuses: list[ReportComparisonSectionStatusDTO],
    ) -> list[ExpenseAccountComparisonDeltaDTO]:
        primary_status = self._period_report_section_status_value(primary, "expenses_by_account")
        comparison_status = self._period_report_section_status_value(comparison, "expenses_by_account")
        if primary_status == "error" or comparison_status == "error":
            section_statuses.append(
                self._comparison_section_status("expenses_by_account", "error", PERIOD_REPORT_SECTION_ERROR_DETAIL)
            )
            return []
        if shared_currency is None:
            section_statuses.append(self._comparison_section_status("expenses_by_account", "not_comparable", currency_detail))
            return []

        primary_rows = {row.account_id: row for row in primary.expenses_by_account}
        comparison_rows = {row.account_id: row for row in comparison.expenses_by_account}
        result: list[ExpenseAccountComparisonDeltaDTO] = []
        for account_id in sorted(set(primary_rows) | set(comparison_rows)):
            primary_row = primary_rows.get(account_id)
            comparison_row = comparison_rows.get(account_id)
            account_name = (primary_row.account_name if primary_row is not None else comparison_row.account_name) if (primary_row or comparison_row) else ""
            currency = (primary_row.currency if primary_row is not None else comparison_row.currency) if (primary_row or comparison_row) else shared_currency
            primary_total = primary_row.total if primary_row is not None else "0.00"
            comparison_total = comparison_row.total if comparison_row is not None else "0.00"
            row_status: Literal["ok", "not_comparable"] = "ok"
            detail: str | None = None
            if primary_row is not None and comparison_row is not None and primary_row.account_name != comparison_row.account_name:
                row_status = "not_comparable"
                detail = "Expense account identity changed between periods for this account_id."
            row_currencies = {
                row.currency
                for row in (primary_row, comparison_row)
                if row is not None
            }
            if len(row_currencies) > 1 or (row_currencies and shared_currency not in row_currencies):
                row_status = "not_comparable"
                detail = "Expense account currency changed or does not match the shared comparison currency."
            if row_status == "ok":
                money_delta = self._money_delta(primary_total, comparison_total, shared_currency)
                result.append(
                    ExpenseAccountComparisonDeltaDTO(
                        account_id=account_id,
                        account_name=account_name,
                        currency=shared_currency,
                        primary_total=money_delta.primary,
                        comparison_total=money_delta.comparison,
                        delta=money_delta.delta,
                        absolute_delta=money_delta.absolute_delta,
                        status="ok",
                        detail=None,
                    )
                )
            else:
                result.append(
                    ExpenseAccountComparisonDeltaDTO(
                        account_id=account_id,
                        account_name=account_name,
                        currency=currency,
                        primary_total=format_money(Decimal(primary_total)),
                        comparison_total=format_money(Decimal(comparison_total)),
                        delta=None,
                        absolute_delta=None,
                        status="not_comparable",
                        detail=detail,
                    )
                )

        if not result and primary_status == "empty" and comparison_status == "empty":
            section_statuses.append(self._comparison_section_status("expenses_by_account", "empty"))
        elif result and all(row.status == "not_comparable" for row in result):
            section_statuses.append(
                self._comparison_section_status(
                    "expenses_by_account",
                    "not_comparable",
                    "No expense account delta rows were comparable between periods.",
                )
            )
        else:
            section_statuses.append(self._comparison_section_status("expenses_by_account", "ok"))
        result.sort(
            key=lambda row: (
                -(Decimal(row.absolute_delta) if row.absolute_delta is not None else Decimal("-1")),
                row.account_name.casefold(),
                row.account_name,
                row.account_id,
            )
        )
        return result

    @staticmethod
    def _money_delta(primary_value: str, comparison_value: str, currency: str) -> ReportMoneyDeltaDTO:
        primary_decimal = Decimal(primary_value)
        comparison_decimal = Decimal(comparison_value)
        delta = primary_decimal - comparison_decimal
        return ReportMoneyDeltaDTO(
            currency=currency,
            primary=format_money(primary_decimal),
            comparison=format_money(comparison_decimal),
            delta=format_money(delta),
            absolute_delta=format_money(abs(delta)),
        )

    @staticmethod
    def _period_report_section_status_value(
        report: PeriodReportDTO,
        section: Literal["summary", "cashflow", "monthly_cashflow", "expenses_by_account"],
    ) -> Literal["ok", "empty", "error"]:
        for item in report.section_statuses:
            if item.section == section:
                return item.status
        return "ok"

    @staticmethod
    def _comparison_section_status(
        section: Literal["summary", "cashflow", "expenses_by_account"],
        status: Literal["ok", "empty", "error", "not_comparable"],
        detail: str | None = None,
    ) -> ReportComparisonSectionStatusDTO:
        return ReportComparisonSectionStatusDTO(section=section, status=status, detail=detail)

    @staticmethod
    def _period_report_section_status(
        section: Literal["summary", "cashflow", "monthly_cashflow", "expenses_by_account"],
        status: Literal["ok", "empty", "error"],
        detail: str | None = None,
    ) -> PeriodReportSectionStatusDTO:
        return PeriodReportSectionStatusDTO(section=section, status=status, detail=detail)

    def _period_report_section_error(
        self,
        section: Literal["summary", "cashflow", "monthly_cashflow", "expenses_by_account"],
    ) -> PeriodReportSectionStatusDTO:
        return self._period_report_section_status(section, "error", PERIOD_REPORT_SECTION_ERROR_DETAIL)

    @staticmethod
    def _period_report_base_limitations(base_currency: str) -> list[str]:
        limitations = [
            "Period reports use reporting_basis=base_currency_only and include no currency conversion.",
            f"Only accounts and splits whose commodity is {base_currency} are included in reported totals.",
        ]
        if base_currency == "XXX":
            limitations.append(
                "The configured base currency is unknown (XXX), so zero totals may mean no matching base-currency accounts rather than an empty book."
            )
        return limitations

    @staticmethod
    def _merge_limitations(*groups: list[str]) -> list[str]:
        merged: list[str] = []
        seen: set[str] = set()
        for group in groups:
            for item in group:
                if item in seen:
                    continue
                seen.add(item)
                merged.append(item)
        return merged

    @staticmethod
    def _period_report_summary_from_report_summary(summary: ReportSummaryDTO) -> PeriodReportSummaryDTO:
        return PeriodReportSummaryDTO(
            currency=summary.currency,
            net_worth=summary.net_worth,
            assets=summary.assets,
            liabilities=summary.liabilities,
            as_of_date=summary.as_of_date,
            reporting_basis=summary.reporting_basis,
            includes_currency_conversion=summary.includes_currency_conversion,
            limitations=summary.limitations,
        )

    @staticmethod
    def _period_report_summary_is_empty(summary: PeriodReportSummaryDTO) -> bool:
        return all(
            Decimal(getattr(summary, field_name)) == Decimal("0")
            for field_name in (
                "net_worth",
                "assets",
                "liabilities",
            )
        )

    @staticmethod
    def _cashflow_is_empty(cashflow: CashflowDTO) -> bool:
        return all(
            Decimal(getattr(cashflow, field_name)) == Decimal("0")
            for field_name in ("inflow", "outflow", "net")
        )

    def _accounts(self, book: Any) -> Iterable[Any]:
        return getattr(book, "accounts", []) or []

    def _transactions(self, book: Any) -> Iterable[Any]:
        return getattr(book, "transactions", []) or []

    def _candidate_transactions(self, book: Any, account_id: str | None = None) -> Iterable[Any]:
        """Return the narrowest safe transaction iterable for list/count filters.

        Account detail/list/export paths can use the target account's split
        collection instead of scanning every transaction in the book. If the
        account does not exist, the historical API behavior is an empty result,
        not a 404. Test doubles that do not model split.transaction fall back to
        the full book iterable so existing behavior remains covered.
        """
        if not account_id:
            return self._transactions(book)

        session = getattr(book, "session", None)
        query = getattr(session, "query", None) if session is not None else None
        if callable(query):
            transactions = (
                query(piecash.Transaction)
                .join(piecash.Split, piecash.Transaction.guid == piecash.Split.transaction_guid)
                .options(joinedload(piecash.Transaction.splits).joinedload(piecash.Split.account))
                .filter(piecash.Split.account_guid == account_id)
                .all()
            )
            return list(transactions)

        account = self._find_account(book, account_id)
        if account is None:
            return []

        splits = list(getattr(account, "splits", []) or [])
        candidates: list[Any] = []
        seen: set[str] = set()
        for split in splits:
            transaction = getattr(split, "transaction", None)
            if transaction is None:
                continue
            transaction_id = _guid(transaction)
            if transaction_id in seen:
                continue
            seen.add(transaction_id)
            candidates.append(transaction)
        if candidates:
            return candidates
        return self._transactions(book)

    def _scheduled_transactions(self, book: Any) -> Iterable[Any]:
        scheduled = getattr(book, "scheduled_transactions", None)
        if scheduled is not None:
            return list(scheduled or [])
        session = getattr(book, "session", None)
        query = getattr(session, "query", None) if session is not None else None
        if not callable(query):
            return []
        result = query(piecash.ScheduledTransaction)
        all_items = getattr(result, "all", None)
        if not callable(all_items):
            return []
        raw_items: Any = all_items()
        return list(raw_items)

    def _account_id(self, account: Any) -> str:
        return _guid(account)

    def _account_currency(self, account: Any) -> str:
        return _commodity_code(getattr(account, "commodity", None), self.base_currency)

    def _money(self, value: Any, currency: str) -> MoneyDTO:
        return MoneyDTO(amount=format_money(value), currency=currency)

    def _account_balance(self, account: Any) -> Decimal:
        get_balance = getattr(account, "get_balance", None)
        if callable(get_balance):
            return self._decimal(get_balance())
        for attr in ("balance", "current_balance"):
            value = getattr(account, attr, None)
            if value is not None:
                return self._decimal(value)
        total = Decimal("0")
        for split in getattr(account, "splits", []) or []:
            total += self._split_amount(split)
        return total

    def _account_to_dto(self, account: Any) -> AccountDTO:
        parent = getattr(account, "parent", None)
        currency = self._account_currency(account)
        balance = self._money(self._account_balance(account), currency)
        return AccountDTO(
            id=self._account_id(account),
            name=str(getattr(account, "name", "")),
            full_name=account_full_name(account),
            type=str(getattr(account, "type", "")),
            currency=balance.currency,
            balance=balance.amount,
            placeholder=bool(getattr(account, "placeholder", False)),
            hidden=bool(getattr(account, "hidden", False)),
            parent_id=self._account_id(parent) if parent is not None else None,
        )

    def _account_to_tree_node(self, account: Any) -> AccountTreeNodeDTO:
        dto = self._account_to_dto(account)
        return AccountTreeNodeDTO(**dto.model_dump(), children=[])

    def _find_account(self, book: Any, account_id: str) -> Any | None:
        return next((account for account in self._accounts(book) if self._account_id(account) == account_id), None)

    def _find_transaction(self, book: Any, transaction_id: str) -> Any | None:
        return next((tx for tx in self._transactions(book) if _guid(tx) == transaction_id), None)

    def _transaction_date(self, transaction: Any) -> date | str | None:
        return getattr(transaction, "post_date", None) or getattr(transaction, "date", None) or getattr(transaction, "date_posted", None)

    def _splits(self, transaction: Any) -> list[Any]:
        return list(getattr(transaction, "splits", []) or [])

    def _split_amount(self, split: Any) -> Decimal:
        for attr in ("value", "quantity", "amount"):
            value = getattr(split, attr, None)
            if value is not None:
                return self._decimal(value)
        return Decimal("0")

    def _decimal(self, value: Any) -> Decimal:
        if isinstance(value, float):
            raise TypeError("Money values must not be floats")
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    def _optional_decimal(self, value: Decimal | str | None) -> Decimal | None:
        if value is None or value == "":
            return None
        return self._decimal(value)

    def _normalize_transaction_state(self, state: str | None) -> str | None:
        if state is None or state == "":
            return None
        return SUPPORTED_TRANSACTION_STATES[state]

    def _transaction_matches(
        self,
        transaction: Any,
        account_id: str | None,
        date_from: date | None,
        date_to: date | None,
        query: str | None,
        transaction_state: str | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
    ) -> bool:
        tx_date = _coerce_date(self._transaction_date(transaction))
        if date_from and (tx_date is None or tx_date < date_from):
            return False
        if date_to and (tx_date is None or tx_date > date_to):
            return False
        if query and not self._transaction_text_matches(transaction, query):
            return False
        if account_id and not any(self._account_id(getattr(split, "account", None)) == account_id for split in self._splits(transaction)):
            return False
        if transaction_state and not self._transaction_state_matches(transaction, account_id, transaction_state):
            return False
        if min_amount is not None or max_amount is not None:
            amount = abs(self._split_amount(self._select_split(self._splits(transaction), account_id)))
            if min_amount is not None and amount < min_amount:
                return False
            if max_amount is not None and amount > max_amount:
                return False
        return True

    def _transaction_text_matches(self, transaction: Any, query: str) -> bool:
        """Match the public query filter against safe transaction text fields.

        GnuCash exposes transaction descriptions, optional transaction notes, and
        split memos as distinct user-entered text fields. Keep the semantics as a
        simple case-insensitive substring match shared by list/count/export paths;
        do not introduce a separate full-text index or persistence layer here.
        """
        transaction_text = [
            getattr(transaction, "description", ""),
            getattr(transaction, "notes", ""),
        ]
        if any(query in str(value or "").lower() for value in transaction_text):
            return True
        return any(query in str(getattr(split, "memo", "") or "").lower() for split in self._splits(transaction))

    def _transaction_state_matches(self, transaction: Any, account_id: str | None, expected_state: str) -> bool:
        splits = self._splits(transaction)
        if account_id:
            splits = [split for split in splits if self._account_id(getattr(split, "account", None)) == account_id]
        return any(str(getattr(split, "reconcile_state", "") or "").lower() == expected_state for split in splits)

    def _transaction_to_list_item(self, transaction: Any, account_id: str | None = None) -> TransactionListItemDTO:
        splits = self._splits(transaction)
        selected = self._select_split(splits, account_id)
        account = getattr(selected, "account", None)
        money = self._money(self._split_amount(selected), self._account_currency(account))
        return TransactionListItemDTO(
            id=_guid(transaction),
            date=_date_string(self._transaction_date(transaction)),
            description=str(getattr(transaction, "description", "")),
            amount=money.amount,
            currency=money.currency,
            account_id=self._account_id(account),
            account_name=account_full_name(account),
            counter_account_name=self._counter_account_name(splits, account),
        )

    def _transaction_to_detail(self, transaction: Any) -> TransactionDetailDTO:
        split_dtos = [self._split_to_dto(split) for split in self._splits(transaction)]
        currency = split_dtos[0].currency if split_dtos else self.base_currency
        return TransactionDetailDTO(
            id=_guid(transaction),
            date=_date_string(self._transaction_date(transaction)),
            description=str(getattr(transaction, "description", "")),
            currency=currency,
            splits=split_dtos,
        )

    def _scheduled_transaction_to_dto(self, scheduled: Any) -> ScheduledTransactionDTO:
        has_template_account = bool(
            getattr(scheduled, "template_act_guid", None) or getattr(scheduled, "template_account", None)
        )
        template_reference_status = "present_redacted" if has_template_account else "not_present_redacted"
        limitations = [
            "Read-only summary metadata only; edit scheduled transactions in GnuCash Desktop.",
            "Next occurrence dates are not calculated by this pre-alpha view.",
            "Template split details are intentionally not exposed.",
            (
                "Template account reference is present, but template split amounts, accounts, memos, transaction descriptions, and raw SQL are redacted."
                if has_template_account
                else "No template account reference was reported; template split amounts, accounts, memos, transaction descriptions, and raw SQL are not queried or inferred."
            ),
        ]
        return ScheduledTransactionDTO(
            id=_guid(scheduled),
            name=str(getattr(scheduled, "name", "") or ""),
            enabled=bool(getattr(scheduled, "enabled", False)),
            start_date=self._optional_date_string(getattr(scheduled, "start_date", None)),
            end_date=self._optional_date_string(getattr(scheduled, "end_date", None)),
            last_occurred=self._optional_date_string(getattr(scheduled, "last_occur", None)),
            num_occurrences=self._optional_int(getattr(scheduled, "num_occur", None)),
            remaining_occurrences=self._optional_int(getattr(scheduled, "rem_occur", None)),
            auto_create=bool(getattr(scheduled, "auto_create", False)),
            auto_notify=bool(getattr(scheduled, "auto_notify", False)),
            advance_create_days=self._optional_int(getattr(scheduled, "adv_creation", None)),
            advance_notify_days=self._optional_int(getattr(scheduled, "adv_notify", None)),
            instance_count=self._optional_int(getattr(scheduled, "instance_count", None)),
            has_template_account=has_template_account,
            template_reference_status=template_reference_status,
            recurrence=[self._recurrence_to_dto(item) for item in self._recurrences(scheduled)],
            limitations=limitations,
        )

    def _recurrences(self, scheduled: Any) -> list[Any]:
        recurrence = getattr(scheduled, "recurrence", []) or []
        if isinstance(recurrence, list):
            return recurrence
        return [recurrence]

    def _recurrence_to_dto(self, recurrence: Any) -> ScheduledTransactionRecurrenceDTO:
        return ScheduledTransactionRecurrenceDTO(
            period_type=str(getattr(recurrence, "recurrence_period_type", "") or ""),
            multiplier=self._optional_int(getattr(recurrence, "recurrence_mult", None)),
            period_start=self._optional_date_string(getattr(recurrence, "recurrence_period_start", None)),
            weekend_adjust=str(getattr(recurrence, "recurrence_weekend_adjust", "") or ""),
        )

    def _optional_date_string(self, value: Any) -> str | None:
        if value is None or value == "":
            return None
        return _date_string(value)

    def _optional_int(self, value: Any) -> int | None:
        if value is None or value == "":
            return None
        return int(value)

    def _split_to_dto(self, split: Any) -> TransactionSplitDTO:
        account = getattr(split, "account", None)
        money = self._money(self._split_amount(split), self._account_currency(account))
        return TransactionSplitDTO(
            account_id=self._account_id(account),
            account_name=account_full_name(account),
            memo=str(getattr(split, "memo", "") or ""),
            reconcile_state=str(getattr(split, "reconcile_state", "") or ""),
            amount=money.amount,
            currency=money.currency,
        )

    def _select_split(self, splits: list[Any], account_id: str | None) -> Any:
        if not splits:
            raise GnuCashReadError("Transaction has no splits")
        if account_id is None:
            return splits[0]
        for split in splits:
            if self._account_id(getattr(split, "account", None)) == account_id:
                return split
        raise EntityNotFoundError("account", account_id)

    def _counter_account_name(self, splits: list[Any], selected_account: Any) -> str:
        if len(splits) > 2:
            return SPLIT_TRANSACTION_LABEL
        selected_id = self._account_id(selected_account)
        for split in splits:
            account = getattr(split, "account", None)
            if self._account_id(account) != selected_id:
                return account_full_name(account)
        return ""
