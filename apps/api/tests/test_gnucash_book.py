"""Tests for the read-only GnuCash book service layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.schemas.gnucash import TransactionListItemDTO
from app.services.gnucash_book import GnuCashBookService, account_full_name, format_money
from app.services.gnucash_exceptions import BookNotFoundError, BookNotConfiguredError, EntityNotFoundError


@dataclass
class FakeCommodity:
    mnemonic: str = "SEK"


@dataclass
class FakeAccount:
    guid: str
    name: str
    type: str = "BANK"
    commodity: FakeCommodity = field(default_factory=FakeCommodity)
    parent: "FakeAccount | None" = None
    balance: Decimal = Decimal("0")
    placeholder: bool = False
    hidden: bool = False
    splits: list["FakeSplit"] = field(default_factory=list)


@dataclass
class FakeSplit:
    account: FakeAccount
    value: Decimal
    memo: str = ""


@dataclass
class FakeTransaction:
    guid: str
    post_date: date
    description: str
    splits: list[FakeSplit]


class FakeBook:
    def __init__(self, accounts=None, transactions=None):
        self.accounts = accounts or []
        self.transactions = transactions or []
        self.closed = False

    def close(self):
        self.closed = True


@pytest.fixture
def fake_accounts():
    root = FakeAccount(guid="root", name="Assets", type="ASSET")
    bank = FakeAccount(guid="bank", name="Bank", type="ASSET", parent=root)
    checking = FakeAccount(guid="checking", name="Checking", type="BANK", parent=bank, balance=Decimal("12345.67"))
    food = FakeAccount(guid="food", name="Food", type="EXPENSE")
    tax = FakeAccount(guid="tax", name="Tax", type="EXPENSE")
    return root, bank, checking, food, tax


@pytest.fixture
def fake_book(fake_accounts):
    root, bank, checking, food, tax = fake_accounts
    split_checking = FakeSplit(account=checking, value=Decimal("-320"))
    split_food = FakeSplit(account=food, value=Decimal("320"), memo="groceries")
    tx = FakeTransaction(
        guid="tx-1",
        post_date=date(2026, 5, 16),
        description="ICA",
        splits=[split_checking, split_food],
    )
    split_tax = FakeSplit(account=tax, value=Decimal("10"))
    split_food_for_split_transaction = FakeSplit(account=food, value=Decimal("40"))
    split_transaction = FakeTransaction(
        guid="tx-2",
        post_date=date(2026, 5, 17),
        description="Split",
        splits=[split_checking, split_food_for_split_transaction, split_tax],
    )
    checking.splits = [split_checking]
    food.splits = [split_food]
    return FakeBook(accounts=[root, bank, checking, food, tax], transactions=[tx, split_transaction])


@pytest.fixture
def service(monkeypatch, tmp_path, fake_book):
    book_path = tmp_path / "book.gnucash"
    book_path.write_text("fixture")
    opened = {}

    def fake_open_book(path, readonly=False):
        opened["path"] = path
        opened["readonly"] = readonly
        return fake_book

    monkeypatch.setattr("app.services.gnucash_book.piecash.open_book", fake_open_book)
    service = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"})
    service.opened = opened
    return service


def test_money_formatting_uses_decimal_strings():
    assert format_money(Decimal("123.4")) == "123.40"
    assert format_money("-320") == "-320.00"
    with pytest.raises(TypeError):
        format_money(1.23)


def test_full_account_name_mapper(fake_accounts):
    root, bank, checking, *_ = fake_accounts
    assert account_full_name(root) == "Assets"
    assert account_full_name(bank) == "Assets:Bank"
    assert account_full_name(checking) == "Assets:Bank:Checking"


def test_full_account_name_skips_gnucash_root_account():
    root = FakeAccount(guid="root", name="Root Account", type="ROOT")
    assets = FakeAccount(guid="assets", name="Assets", type="ASSET", parent=root)
    bank = FakeAccount(guid="bank", name="Bank", type="ASSET", parent=assets)
    checking = FakeAccount(guid="checking", name="Checking", type="BANK", parent=bank)

    assert account_full_name(checking) == "Assets:Bank:Checking"
    assert account_full_name(root) == ""


def test_missing_book_path_raises_controlled_error():
    service = GnuCashBookService({"uri_or_path": ""})
    with pytest.raises(BookNotConfiguredError):
        service.check_connection()


def test_missing_book_file_raises_controlled_error(tmp_path):
    service = GnuCashBookService({"uri_or_path": str(tmp_path / "missing.gnucash")})
    with pytest.raises(BookNotFoundError):
        service.check_connection()


def test_check_connection_opens_book_readonly(service):
    assert service.check_connection() is True
    assert service.opened["readonly"] is True


def test_check_connection_supports_sql_connection_uri(monkeypatch):
    opened = {}

    def fake_open_book(*args, **kwargs):
        opened["args"] = args
        opened["kwargs"] = kwargs
        return FakeBook()

    monkeypatch.setattr("app.services.gnucash_book.piecash.open_book", fake_open_book)
    service = GnuCashBookService({"uri_or_path": "postgresql://user:pass@db/gnucash", "base_currency": "SEK"})

    assert service.check_connection() is True
    assert opened["args"] == ()
    assert opened["kwargs"] == {"uri_conn": "postgresql://user:pass@db/gnucash", "readonly": True}


def test_list_accounts_maps_accounts(service):
    accounts = service.list_accounts()
    checking = next(account for account in accounts if account.id == "checking")
    assert checking.name == "Checking"
    assert checking.full_name == "Assets:Bank:Checking"
    assert checking.type == "BANK"
    assert checking.currency == "SEK"
    assert checking.balance == "12345.67"
    assert checking.parent_id == "bank"


def test_get_account_raises_entity_not_found(service):
    with pytest.raises(EntityNotFoundError):
        service.get_account("missing")


def test_get_account_tree_nests_children(service):
    tree = service.get_account_tree()
    assets = next(node for node in tree if node.id == "root")
    assert assets.children[0].id == "bank"
    assert assets.children[0].children[0].id == "checking"


def test_mock_based_transaction_mapping(service):
    transactions = service.list_transactions(account_id="checking")
    assert isinstance(transactions[0], TransactionListItemDTO)
    tx = next(item for item in transactions if item.id == "tx-1")
    assert tx.date == "2026-05-16"
    assert tx.description == "ICA"
    assert tx.amount == "-320.00"
    assert tx.currency == "SEK"
    assert tx.account_id == "checking"
    assert tx.account_name == "Assets:Bank:Checking"
    assert tx.counter_account_name == "Food"


def test_split_transaction_counter_account_name(service):
    tx = next(item for item in service.list_transactions(account_id="checking") if item.id == "tx-2")
    assert tx.counter_account_name == "Split transaction"


def test_transaction_filters_pagination_and_query(service):
    results = service.list_transactions(query="ica", limit=1, offset=0)
    assert [item.id for item in results] == ["tx-1"]
    assert service.list_transactions(date_from="2026-05-17", date_to="2026-05-17")[0].id == "tx-2"


def test_transaction_query_matches_split_memo_case_insensitively(service):
    results = service.list_transactions(query="GROCERIES")

    assert [item.id for item in results] == ["tx-1"]
    assert service.count_transactions(query="GROCERIES") == 1


def test_transaction_query_without_description_or_memo_match_returns_empty(service):
    assert service.list_transactions(query="not-present") == []
    assert service.count_transactions(query="not-present") == 0


def test_get_transaction_detail_maps_splits(service):
    detail = service.get_transaction("tx-1")
    assert detail.id == "tx-1"
    assert detail.date == "2026-05-16"
    assert detail.currency == "SEK"
    assert len(detail.splits) == 2
    assert detail.splits[0].account_name == "Assets:Bank:Checking"
    assert detail.splits[0].amount == "-320.00"
    assert detail.splits[1].memo == "groceries"


def test_get_summary(service):
    summary = service.get_summary()
    assert summary.account_count == 5
    assert summary.transaction_count == 2
    assert summary.currency == "SEK"


def test_get_cashflow(service):
    cashflow = service.get_cashflow("2026-05-16", "2026-05-16")
    assert cashflow.inflow == "0.00"
    assert cashflow.outflow == "320.00"
    assert cashflow.net == "-320.00"


def test_fixture_based_integration_tests_exist():
    """Verify the synthetic fixture and integration test module are present."""
    fixture_path = Path("tests/fixtures/test-book.gnucash.sqlite")
    assert fixture_path.exists(), f"Synthetic fixture not found: {fixture_path}"
    integration_test = Path("tests/test_integration_fixture.py")
    assert integration_test.exists(), f"Integration test module not found: {integration_test}"
