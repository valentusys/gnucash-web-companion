"""Regression tests for bounded SQL account explorer split aggregation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import piecash
import pytest
from piecash import Account, Commodity, Split, Transaction
from sqlalchemy import event

from app.services.account_explorer import build_account_explorer_query, build_account_explorer_response
from app.services.gnucash_book import GnuCashBookService


@dataclass
class FakeCommodity:
    namespace: str = "CURRENCY"
    mnemonic: str = "SEK"


@dataclass
class FakeAccount:
    guid: str
    name: str
    type: str = "BANK"
    commodity: FakeCommodity = field(default_factory=FakeCommodity)
    parent: "FakeAccount | None" = None
    hidden: bool = False
    placeholder: bool = False


def _hex_guid(value: int) -> str:
    return f"{value:032x}"


def _amount(amount: str, *, namespace: str = "CURRENCY", mnemonic: str = "SEK") -> dict:
    return {"amount": amount, "commodity": {"namespace": namespace, "mnemonic": mnemonic}}


def _assign_guid(obj: Any, value: str):
    obj.guid = value
    return obj


def _explorer_query():
    return build_account_explorer_query(mode=None, query=None, types=None, hidden=None, placeholder=None)


class _FakeRawConnection:
    def create_aggregate(self, *args):
        self.aggregate_args = args


class _FakeConnection:
    def __init__(self):
        self.connection = _FakeRawConnection()


class _FakeBind:
    dialect = SimpleNamespace(name="sqlite")


class _GuardQuery:
    def __init__(self, rows, session, kind: str):
        self.rows = rows
        self.session = session
        self.kind = kind

    def options(self, *args, **kwargs):
        return self

    def limit(self, value):
        self.session.limits.append(value)
        return self

    def select_from(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def group_by(self, *args, **kwargs):
        return self

    def all(self):
        self.session.all_calls.append(self.kind)
        return self.rows


class GuardSession:
    def __init__(self, accounts, aggregate_rows):
        self.accounts = accounts
        self.aggregate_rows = aggregate_rows
        self.queries: list[str] = []
        self.all_calls: list[str] = []
        self.limits: list[int] = []

    def get_bind(self):
        return _FakeBind()

    def connection(self):
        return _FakeConnection()

    def query(self, *entities):
        if len(entities) == 1 and entities[0] is piecash.Account:
            self.queries.append("accounts")
            return _GuardQuery(self.accounts, self, "accounts")
        if len(entities) == 1 and entities[0] is piecash.Split:  # pragma: no cover - proves old bug stays forbidden
            raise AssertionError("account explorer must not call query(piecash.Split).all()")
        self.queries.append("split_aggregate")
        return _GuardQuery(self.aggregate_rows, self, "split_aggregate")


class GuardBook:
    def __init__(self, session):
        self.session = session

    @property
    def transactions(self):
        raise AssertionError("account explorer must not traverse transactions")


def test_guard_session_blocks_split_all_and_transaction_traversal():
    root = FakeAccount(guid=_hex_guid(1), name="Root", type="ROOT")
    child = FakeAccount(guid=_hex_guid(2), name="Precise", parent=root)
    session = GuardSession(
        [root, child],
        [SimpleNamespace(account_guid=child.guid, quantity_rational="1234567/1000000", split_count=7)],
    )

    response = build_account_explorer_response(
        GuardBook(session),
        _explorer_query(),
        book_id=42,
        base_currency="SEK",
    )

    assert session.queries == ["accounts", "split_aggregate"]
    assert session.all_calls == ["accounts", "split_aggregate"]
    assert response.scan.query_count == 2
    assert response.scan.split_rows == 7
    assert response.scan.split_aggregate_rows == 1
    assert response.scan.serialized_bytes == len(response.model_dump_json().encode("utf-8"))
    by_name = {node.name: node for node in response.nodes}
    assert by_name["Precise"].direct_balance.amount == "1.234567"


@pytest.mark.parametrize("candidate_count", [1, 100, 1000])
def test_query_count_does_not_scale_per_candidate_account(candidate_count):
    root = FakeAccount(guid=_hex_guid(1), name="Root", type="ROOT")
    accounts = [root]
    for index in range(2, candidate_count + 1):
        accounts.append(FakeAccount(guid=_hex_guid(index), name=f"Account {index:04d}", parent=root))
    session = GuardSession(accounts, [])
    request = _explorer_query()
    if candidate_count == 1000:
        request = build_account_explorer_query(
            mode=None,
            query="Account 0999",
            types=None,
            hidden=None,
            placeholder=None,
        )

    response = build_account_explorer_response(
        GuardBook(session),
        request,
        book_id=42,
        base_currency="SEK",
    )

    assert response.scan.candidate_accounts == candidate_count
    if candidate_count == 1000:
        assert response.scan.returned_nodes == 2
    else:
        assert response.scan.returned_nodes == candidate_count
    assert response.scan.query_count == 2
    assert response.scan.query_count <= 8
    assert response.scan.split_aggregate_rows == 0
    assert session.queries == ["accounts", "split_aggregate"]
    assert session.all_calls == ["accounts", "split_aggregate"]


def _create_many_split_book(path: Path, *, many_split_count: int) -> int:
    book = piecash.create_book(currency="SEK", sqlite_file=str(path), overwrite=True)
    sek = _assign_guid(book.commodities[0], _hex_guid(10_001))
    usd = _assign_guid(
        Commodity(namespace="CURRENCY", mnemonic="USD", fullname="US Dollar", fraction=100),
        _hex_guid(10_002),
    )
    root = _assign_guid(book.root_account, _hex_guid(1))
    assets = _assign_guid(Account(name="Assets", type="ASSET", parent=root, commodity=sek), _hex_guid(2))
    checking = _assign_guid(Account(name="Checking", type="BANK", parent=assets, commodity=sek), _hex_guid(3))
    expenses = _assign_guid(Account(name="Expenses", type="EXPENSE", parent=root, commodity=sek), _hex_guid(4))
    food = _assign_guid(Account(name="Food", type="EXPENSE", parent=expenses, commodity=sek), _hex_guid(5))
    equity = _assign_guid(Account(name="Equity", type="EQUITY", parent=root, commodity=sek), _hex_guid(6))
    usd_cash = _assign_guid(Account(name="USD Cash", type="CASH", parent=assets, commodity=usd), _hex_guid(7))

    def tx(index: int, description: str, splits: list[Split]) -> None:
        _assign_guid(
            Transaction(currency=sek, description=description, post_date=date(2026, 1, 1), splits=splits),
            _hex_guid(20_000 + index),
        )
        for split_index, split in enumerate(splits, start=1):
            _assign_guid(split, _hex_guid(30_000 + index * 10 + split_index))

    tx(
        1,
        "precise opening",
        [
            Split(account=checking, value=Decimal("1.234567")),
            Split(account=equity, value=Decimal("-1.234567")),
        ],
    )
    tx(
        2,
        "mixed native commodity",
        [
            Split(account=usd_cash, value=Decimal("10.00"), quantity=Decimal("1.2345")),
            Split(account=equity, value=Decimal("-10.00")),
        ],
    )
    for index in range(many_split_count):
        tx(
            100 + index,
            f"many unrelated expense {index:04d}",
            [
                Split(account=checking, value=Decimal("-0.01")),
                Split(account=food, value=Decimal("0.01")),
            ],
        )
    book.save()
    book.close()
    return 4 + many_split_count * 2


def test_real_sqlite_book_aggregates_without_materializing_splits(tmp_path):
    many_split_count = 300
    book_path = tmp_path / "many-splits.gnucash.sqlite"
    expected_split_rows = _create_many_split_book(book_path, many_split_count=many_split_count)
    split_loads = []

    def on_split_load(target, context):
        split_loads.append(target.guid)

    event.listen(piecash.Split, "load", on_split_load)
    try:
        response = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"}).explore_accounts(
            _explorer_query(),
            book_id=42,
        )
    finally:
        event.remove(piecash.Split, "load", on_split_load)

    assert split_loads == []
    assert response.scan.query_count == 2
    assert response.scan.query_count <= 8
    assert response.scan.split_rows == expected_split_rows
    assert response.scan.split_aggregate_rows == 4
    assert response.scan.split_aggregate_rows <= response.scan.candidate_accounts
    assert response.scan.serialized_bytes == len(response.model_dump_json().encode("utf-8"))

    by_name = {node.name: node for node in response.nodes}
    assert by_name["Checking"].direct_balance.amount == str(Decimal("1.234567") - Decimal("0.01") * many_split_count)
    assert by_name["Food"].direct_balance.amount == "3"
    assert by_name["USD Cash"].direct_balance.amount == "1.2345"
    assert by_name["USD Cash"].direct_balance.commodity.mnemonic == "USD"
    assert [bucket.model_dump() for bucket in by_name["Assets"].recursive_balances] == [
        _amount("-1.765433"),
        _amount("1.2345", mnemonic="USD"),
    ]
