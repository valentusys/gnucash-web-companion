"""Read-only service layer for GnuCash SQL books via piecash."""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

import piecash

from app.schemas.gnucash import (
    AccountDTO,
    AccountTreeNodeDTO,
    BookSummaryDTO,
    CashflowDTO,
    MoneyDTO,
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
        if name:
            names.append(str(name))
        current = getattr(current, "parent", None)
    return ":".join(reversed(names))


class GnuCashBookService:
    """Read-only data access service for one configured GnuCash book."""

    def __init__(self, book_config: Any):
        self.book_config = book_config
        self.uri_or_path = self._get_uri_or_path(book_config)
        self.base_currency = self._get_base_currency(book_config)

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
        min_amount: Decimal | str | None = None,
        max_amount: Decimal | str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TransactionListItemDTO]:
        limit = max(0, min(limit, 500))
        offset = max(0, offset)
        start = _coerce_date(date_from)
        end = _coerce_date(date_to)
        normalized_query = query.lower() if query else None
        min_decimal = self._optional_decimal(min_amount)
        max_decimal = self._optional_decimal(max_amount)
        with self._open_book() as book:
            items: list[TransactionListItemDTO] = []
            for transaction in self._transactions(book):
                if not self._transaction_matches(
                    transaction, account_id, start, end, normalized_query, min_decimal, max_decimal
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

    def count_transactions(
        self,
        account_id: str | None = None,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
        query: str | None = None,
        min_amount: Decimal | str | None = None,
        max_amount: Decimal | str | None = None,
    ) -> int:
        start = _coerce_date(date_from)
        end = _coerce_date(date_to)
        normalized_query = query.lower() if query else None
        min_decimal = self._optional_decimal(min_amount)
        max_decimal = self._optional_decimal(max_amount)
        with self._open_book() as book:
            return sum(
                1
                for transaction in self._transactions(book)
                if self._transaction_matches(
                    transaction, account_id, start, end, normalized_query, min_decimal, max_decimal
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
        with self._open_book() as book:
            for transaction in self._transactions(book):
                tx_date = _coerce_date(self._transaction_date(transaction))
                if tx_date is None or tx_date < start or tx_date > end:
                    continue
                for split in self._splits(transaction):
                    account = getattr(split, "account", None)
                    account_type = str(getattr(account, "type", "")).upper()
                    if account_type not in {"INCOME", "EXPENSE"}:
                        continue
                    amount = self._split_amount(split)
                    if account_type == "INCOME":
                        if amount >= 0:
                            inflow += amount
                        else:
                            outflow += abs(amount)
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

    def _accounts(self, book: Any) -> Iterable[Any]:
        return getattr(book, "accounts", []) or []

    def _transactions(self, book: Any) -> Iterable[Any]:
        return getattr(book, "transactions", []) or []

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

    def _transaction_matches(
        self,
        transaction: Any,
        account_id: str | None,
        date_from: date | None,
        date_to: date | None,
        query: str | None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
    ) -> bool:
        tx_date = _coerce_date(self._transaction_date(transaction))
        if date_from and (tx_date is None or tx_date < date_from):
            return False
        if date_to and (tx_date is None or tx_date > date_to):
            return False
        if query and query not in str(getattr(transaction, "description", "")).lower():
            return False
        if account_id and not any(self._account_id(getattr(split, "account", None)) == account_id for split in self._splits(transaction)):
            return False
        if min_amount is not None or max_amount is not None:
            amount = abs(self._split_amount(self._select_split(self._splits(transaction), account_id)))
            if min_amount is not None and amount < min_amount:
                return False
            if max_amount is not None and amount > max_amount:
                return False
        return True

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

    def _split_to_dto(self, split: Any) -> TransactionSplitDTO:
        account = getattr(split, "account", None)
        money = self._money(self._split_amount(split), self._account_currency(account))
        return TransactionSplitDTO(
            account_id=self._account_id(account),
            account_name=account_full_name(account),
            memo=str(getattr(split, "memo", "") or ""),
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
