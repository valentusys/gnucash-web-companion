"""Tests for bounded per-account overview and activity endpoints."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import piecash
import pytest
from fastapi.testclient import TestClient
from piecash import Account, Commodity, Split, Transaction
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import Book, User, UserBookAccess, WriteAlphaTransactionOwnership
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.gnucash_book import GnuCashBookService

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password="testpassword123",
)

ROOT = "ffffffffffffffffffffffffffffffff"
ASSETS = "11111111111111111111111111111111"
EXPENSES = "22222222222222222222222222222222"
INCOME = "33333333333333333333333333333333"
CHECKING = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
CASH = "abababababababababababababababab"
SAVINGS = "acacacacacacacacacacacacacacacac"
FOOD = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
SALARY = "cccccccccccccccccccccccccccccccc"
EUR_ACCOUNT = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
TX1 = "00000000000000000000000000000001"
TX2 = "00000000000000000000000000000002"
TX3 = "00000000000000000000000000000003"


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(engine):
    return sessionmaker(bind=engine)


@pytest.fixture
def client(session_factory):
    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: TEST_SETTINGS
    app.dependency_overrides[get_db] = override_get_db

    with session_factory() as session:
        session.add(
            User(
                username="admin",
                display_name="Admin",
                password_hash=hash_password("testpassword123"),
                is_admin=True,
            )
        )
        session.add(
            User(
                username="viewer",
                display_name="Viewer",
                password_hash=hash_password("viewerpass"),
                is_admin=False,
            )
        )
        session.commit()

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def auth_headers(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "testpassword123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def viewer_headers(client):
    response = client.post("/auth/login", json={"username": "viewer", "password": "viewerpass"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


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
    balance: Decimal = Decimal("0")
    placeholder: bool = False
    hidden: bool = False
    splits: list = field(default_factory=list)


@dataclass
class FakeSplit:
    account: FakeAccount
    quantity: Decimal
    value: Decimal | None = None
    memo: str = ""
    reconcile_state: str = "n"
    transaction: "FakeTransaction | None" = None

    def __post_init__(self):
        if self.value is None:
            self.value = self.quantity


@dataclass
class FakeTransaction:
    guid: str
    post_date: date
    description: str
    splits: list[FakeSplit]

    def __post_init__(self):
        for split in self.splits:
            split.transaction = self
            split.account.splits.append(split)


class FakeBook:
    def __init__(self, accounts=None, transactions=None):
        self.accounts = accounts or []
        self.transactions = transactions or []
        self.closed = False

    def close(self):
        self.closed = True


def _fake_account_graph() -> tuple[list[FakeAccount], list[FakeTransaction]]:
    root = FakeAccount(guid=ROOT, name="Root Account", type="ROOT")
    assets = FakeAccount(guid=ASSETS, name="Assets", type="ASSET", parent=root)
    expenses = FakeAccount(guid=EXPENSES, name="Expenses", type="EXPENSE", parent=root)
    income = FakeAccount(guid=INCOME, name="Income", type="INCOME", parent=root)
    checking = FakeAccount(guid=CHECKING, name="Checking", type="BANK", parent=assets)
    cash = FakeAccount(guid=CASH, name="Cash", type="CASH", parent=assets)
    savings = FakeAccount(guid=SAVINGS, name="Savings", type="BANK", parent=assets)
    food = FakeAccount(guid=FOOD, name="Food", type="EXPENSE", parent=expenses)
    salary = FakeAccount(guid=SALARY, name="Salary", type="INCOME", parent=income)
    eur = FakeAccount(
        guid=EUR_ACCOUNT,
        name="EUR Bank",
        type="BANK",
        parent=assets,
        commodity=FakeCommodity(mnemonic="EUR"),
    )

    transactions = [
        FakeTransaction(
            guid=TX1,
            post_date=date(2026, 5, 1),
            description="Opening groceries",
            splits=[
                FakeSplit(account=checking, quantity=Decimal("-10.00")),
                FakeSplit(account=food, quantity=Decimal("10.00")),
            ],
        ),
        FakeTransaction(
            guid=TX2,
            post_date=date(2026, 5, 10),
            description="Salary",
            splits=[
                FakeSplit(account=checking, quantity=Decimal("1000.00")),
                FakeSplit(account=salary, quantity=Decimal("-1000.00")),
            ],
        ),
        FakeTransaction(
            guid=TX3,
            post_date=date(2026, 5, 10),
            description="Lunch",
            splits=[
                FakeSplit(account=checking, quantity=Decimal("-5.25")),
                FakeSplit(account=food, quantity=Decimal("5.25")),
            ],
        ),
        FakeTransaction(
            guid="00000000000000000000000000000004",
            post_date=date(2026, 6, 1),
            description="Outside range",
            splits=[
                FakeSplit(account=checking, quantity=Decimal("100.00")),
                FakeSplit(account=cash, quantity=Decimal("-100.00")),
            ],
        ),
    ]
    cash.splits.append(FakeSplit(account=cash, quantity=Decimal("3.00")))
    savings.splits.append(FakeSplit(account=savings, quantity=Decimal("25.50")))
    accounts = [root, assets, expenses, income, checking, cash, savings, food, salary, eur]
    return accounts, transactions


def _install_fake_book(tmp_path: Path, monkeypatch, accounts: list[FakeAccount], transactions: list[FakeTransaction]):
    path = tmp_path / "account-activity.gnucash"
    path.write_text("fake", encoding="utf-8")
    opened: list[str] = []

    def fake_open_book(path_arg, readonly=False):
        assert readonly is True
        opened.append(str(path_arg))
        return FakeBook(accounts=accounts, transactions=transactions)

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return path, opened


def _create_book(session_factory, path: Path | str, *, base_currency: str = "SEK") -> int:
    with session_factory() as session:
        book = Book(
            name="Synthetic Account Slice",
            storage_type="sqlite",
            uri_or_path=str(path),
            base_currency=base_currency,
            is_default=True,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


def _assign_guid(obj: Any, value: str):
    obj.guid = value
    return obj


class TestAccountOverviewEndpoint:
    def test_overview_normalizes_guid_and_returns_breadcrumbs_children_and_bounds(
        self, client, auth_headers, session_factory, tmp_path, monkeypatch
    ):
        import app.services.account_explorer as account_explorer

        accounts, transactions = _fake_account_graph()
        path, opened = _install_fake_book(tmp_path, monkeypatch, accounts, transactions)
        book_id = _create_book(session_factory, path)
        monkeypatch.setattr(account_explorer, "MAX_OVERVIEW_CHILDREN_RETURNED", 2)

        response = client.get(
            f"/books/{book_id}/accounts/%20{ASSETS.upper()}%20/overview",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert opened == [str(path)]
        assert data["book_id"] == book_id
        assert data["id"] == ASSETS
        assert data["source_parent_id"] == ROOT
        assert data["parent_id"] == ROOT
        assert data["root_id"] == ROOT
        assert data["full_path"] == "Root Account:Assets"
        assert data["breadcrumbs"] == [
            {"id": ROOT, "name": "Root Account"},
            {"id": ASSETS, "name": "Assets"},
        ]
        assert data["subtree_account_count"] == 5
        assert data["child_count"] == 4
        assert data["children_returned"] == 2
        assert data["children_truncated"] is True
        assert [child["id"] for child in data["children"]] == [CASH, CHECKING]
        assert data["children"][0]["direct_balance"] == {
            "amount": "-97",
            "commodity_namespace": "CURRENCY",
            "commodity_mnemonic": "SEK",
        }
        assert data["scan"]["candidate_accounts"] == 10
        assert data["scan"]["query_count"] <= 8
        assert data["scan"]["serialized_bytes"] <= data["scan"]["limits"]["serialized_bytes"]
        assert data["balance_basis"] == "native_commodity_account_natural_sign"
        assert data["includes_currency_conversion"] is False
        assert "total_count" not in data

    def test_invalid_guid_is_typed_redacted_and_does_not_open_book(
        self, client, auth_headers, session_factory, tmp_path, monkeypatch
    ):
        accounts, transactions = _fake_account_graph()
        path, opened = _install_fake_book(tmp_path, monkeypatch, accounts, transactions)
        book_id = _create_book(session_factory, path)

        response = client.get(
            f"/books/{book_id}/accounts/not-a-private-guid/overview",
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "invalid_account_id"
        assert "not-a-private-guid" not in response.text
        assert opened == []

    def test_missing_account_and_unauthorized_are_safe_before_open(
        self, client, auth_headers, viewer_headers, session_factory, tmp_path, monkeypatch
    ):
        accounts, transactions = _fake_account_graph()
        path, opened = _install_fake_book(tmp_path, monkeypatch, accounts, transactions)
        book_id = _create_book(session_factory, path)

        missing = client.get(
            f"/books/{book_id}/accounts/99999999999999999999999999999999/overview",
            headers=auth_headers,
        )
        denied = client.get(
            f"/books/{book_id}/accounts/{CHECKING}/overview",
            headers=viewer_headers,
        )

        assert missing.status_code == 404
        assert "99999999999999999999999999999999" not in missing.text
        assert denied.status_code == 403
        assert opened == [str(path)]

    def test_unavailable_storage_returns_safe_503_before_open(
        self, client, auth_headers, session_factory, tmp_path, monkeypatch
    ):
        missing_path = tmp_path / "missing.gnucash.sqlite"
        book_id = _create_book(session_factory, missing_path)

        import app.routers.books as books_router

        def fail_if_called(_book):
            raise AssertionError("storage diagnostics must run before any GnuCash open")

        monkeypatch.setattr(books_router, "account_service_for", fail_if_called)
        response = client.get(f"/books/{book_id}/accounts/{CHECKING}/overview", headers=auth_headers)

        assert response.status_code == 503
        assert str(missing_path) not in response.text

    def test_real_sqlite_overview_uses_bounded_aggregate_without_materializing_transactions_or_splits(
        self, tmp_path
    ):
        book_path = tmp_path / "overview-sql.gnucash.sqlite"
        book = piecash.create_book(currency="SEK", sqlite_file=str(book_path), overwrite=True)
        sek = _assign_guid(book.commodities[0], "99999999999999999999999999999999")
        usd = _assign_guid(
            Commodity(namespace="CURRENCY", mnemonic="USD", fullname="US Dollar", fraction=100),
            "99999999999999999999999999999998",
        )
        root = _assign_guid(book.root_account, ROOT)
        assets = _assign_guid(Account(name="Assets", type="ASSET", parent=root, commodity=sek), ASSETS)
        checking = _assign_guid(Account(name="Checking", type="BANK", parent=assets, commodity=sek), CHECKING)
        usd_cash = _assign_guid(Account(name="USD Cash", type="CASH", parent=assets, commodity=usd), EUR_ACCOUNT)
        equity = _assign_guid(Account(name="Equity", type="EQUITY", parent=root, commodity=sek), CASH)
        _assign_guid(
            Transaction(
                currency=sek,
                description="overview precise opening",
                post_date=date(2026, 5, 1),
                splits=[
                    Split(account=checking, value=Decimal("1.25")),
                    Split(account=equity, value=Decimal("-1.25")),
                ],
            ),
            TX1,
        )
        _assign_guid(
            Transaction(
                currency=sek,
                description="overview mixed native commodity",
                post_date=date(2026, 5, 2),
                splits=[
                    Split(account=usd_cash, value=Decimal("10.00"), quantity=Decimal("2.50")),
                    Split(account=equity, value=Decimal("-10.00")),
                ],
            ),
            TX2,
        )
        book.save()
        book.close()

        transaction_loads: list[str] = []
        split_loads: list[str] = []

        def on_transaction_load(target, context):
            transaction_loads.append(target.guid)

        def on_split_load(target, context):
            split_loads.append(target.guid)

        event.listen(piecash.Transaction, "load", on_transaction_load)
        event.listen(piecash.Split, "load", on_split_load)
        try:
            response = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"}).get_account_overview(
                ASSETS,
                book_id=42,
            )
        finally:
            event.remove(piecash.Transaction, "load", on_transaction_load)
            event.remove(piecash.Split, "load", on_split_load)

        assert response.id == ASSETS
        assert response.child_count == 2
        assert response.scan.query_count == 2
        assert response.scan.query_count <= 8
        assert response.scan.split_rows == 4
        assert transaction_loads == []
        assert split_loads == []
        assert response.scan.serialized_bytes <= response.scan.limits["serialized_bytes"]
        assert [bucket.model_dump() for bucket in response.recursive_balances] == [
            {"amount": "1.25", "commodity_namespace": "CURRENCY", "commodity_mnemonic": "SEK"},
            {"amount": "2.5", "commodity_namespace": "CURRENCY", "commodity_mnemonic": "USD"},
        ]


class TestAccountActivityEndpoint:
    @pytest.mark.parametrize(
        ("params", "code"),
        [
            ({"date_from": "2026-05-01"}, "date_pair_required"),
            ({"date_from": "2026-05-32", "date_to": "2026-05-31"}, "invalid_date"),
            ({"date_from": "2026-05-31", "date_to": "2026-05-01"}, "invalid_date_range"),
            ({"date_from": "2025-01-01", "date_to": "2026-01-02"}, "date_range_too_wide"),
            ({"date_from": "2026-05-01", "date_to": "2026-05-31", "limit": "21"}, "invalid_limit"),
        ],
    )
    def test_activity_validation_errors_are_typed_and_redacted(
        self, client, auth_headers, session_factory, tmp_path, monkeypatch, params, code
    ):
        accounts, transactions = _fake_account_graph()
        path, opened = _install_fake_book(tmp_path, monkeypatch, accounts, transactions)
        book_id = _create_book(session_factory, path)

        response = client.get(
            f"/books/{book_id}/accounts/{CHECKING}/activity",
            headers=auth_headers,
            params=params,
        )

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == code
        assert str(path) not in response.text
        assert opened == []

    def test_activity_returns_change_recent_limit_plus_one_and_write_alpha_hint(
        self, client, auth_headers, session_factory, tmp_path, monkeypatch
    ):
        accounts, transactions = _fake_account_graph()
        path, opened = _install_fake_book(tmp_path, monkeypatch, accounts, transactions)
        book_id = _create_book(session_factory, path)
        with session_factory() as session:
            session.add(
                WriteAlphaTransactionOwnership(
                    book_id=book_id,
                    transaction_id=TX3,
                    created_by_write_alpha=True,
                    created_by_user_id=None,
                )
            )
            session.commit()

        response = client.get(
            f"/books/{book_id}/accounts/{CHECKING}/activity",
            headers=auth_headers,
            params={"date_from": "2026-05-01", "date_to": "2026-05-31", "limit": "2"},
        )

        assert response.status_code == 200
        data = response.json()
        assert opened == [str(path)]
        assert data["book_id"] == book_id
        assert data["account_id"] == CHECKING
        assert data["date_from"] == "2026-05-01"
        assert data["date_to"] == "2026-05-31"
        assert data["scope"] == "direct_account"
        assert data["commodity_mnemonic"] == "SEK"
        assert data["change"] == {
            "amount": "984.75",
            "commodity_namespace": "CURRENCY",
            "commodity_mnemonic": "SEK",
        }
        assert data["inflow"] is None
        assert data["outflow"] is None
        assert data["flow_status"] == "not_applicable_for_generic_account"
        assert data["transaction_explorer_compatible"] is True
        assert [item["id"] for item in data["recent_transactions"]] == [TX3, TX2]
        assert data["recent_transactions"][0]["matched_quantity"]["amount"] == "-5.25"
        assert data["recent_transactions"][0]["counter_account_name"] == "Expenses:Food"
        assert data["recent_transactions"][0]["is_write_alpha_owned"] is True
        assert data["has_more"] is True
        assert data["partial_failure"] is False
        assert {item["section"]: item["status"] for item in data["section_statuses"]} == {
            "change": "ok",
            "recent_transactions": "ok",
        }
        assert data["scan"]["recent_transaction_objects"] == 3
        assert data["scan"]["recent_split_rows"] <= 20_000
        assert data["scan"]["query_count"] <= 10
        assert "total" not in data and "total_count" not in data

    def test_activity_for_empty_and_non_base_account_reports_honest_statuses_and_limitations(
        self, client, auth_headers, session_factory, tmp_path, monkeypatch
    ):
        accounts, transactions = _fake_account_graph()
        path, _ = _install_fake_book(tmp_path, monkeypatch, accounts, transactions)
        book_id = _create_book(session_factory, path)

        response = client.get(
            f"/books/{book_id}/accounts/{EUR_ACCOUNT}/activity",
            headers=auth_headers,
            params={"date_from": "2026-05-01", "date_to": "2026-05-31"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["commodity_mnemonic"] == "EUR"
        assert data["change"]["amount"] == "0"
        assert data["recent_transactions"] == []
        assert data["has_more"] is False
        assert data["transaction_explorer_compatible"] is False
        assert any("no FX" in item or "currency conversion" in item for item in data["limitations"])
        assert {item["section"]: item["status"] for item in data["section_statuses"]} == {
            "change": "empty",
            "recent_transactions": "empty",
        }

    def test_activity_section_failure_is_partial_and_redacted(
        self, client, auth_headers, session_factory, tmp_path, monkeypatch
    ):
        import app.services.account_explorer as account_explorer

        accounts, transactions = _fake_account_graph()
        path, _ = _install_fake_book(tmp_path, monkeypatch, accounts, transactions)
        book_id = _create_book(session_factory, path)

        def fail_change(*args, **kwargs):
            raise account_explorer.AccountExplorerError(
                "private_failure",
                "private /data/books/source.gnucash.sqlite account Salary amount 123",
            )

        monkeypatch.setattr(account_explorer, "_build_activity_change_section", fail_change)
        response = client.get(
            f"/books/{book_id}/accounts/{CHECKING}/activity",
            headers=auth_headers,
            params={"date_from": "2026-05-01", "date_to": "2026-05-31"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["partial_failure"] is True
        assert data["change"] is None
        assert data["recent_transactions"]
        statuses = {item["section"]: item for item in data["section_statuses"]}
        assert statuses["change"]["status"] == "error"
        assert statuses["change"]["detail"] == "Account activity change could not be read safely from this runtime."
        assert statuses["recent_transactions"]["status"] == "ok"
        assert "/data/books" not in statuses["change"]["detail"]
        assert "Salary" not in statuses["change"]["detail"]
        assert "123" not in statuses["change"]["detail"]


class TestAccountActivitySqlInstrumentation:
    def test_real_sqlite_activity_uses_bounded_queries_and_materializes_only_recent_probe(self, tmp_path):
        book_path = tmp_path / "activity-sql.gnucash.sqlite"
        book = piecash.create_book(currency="SEK", sqlite_file=str(book_path), overwrite=True)
        sek = _assign_guid(book.commodities[0], "99999999999999999999999999999999")
        usd = _assign_guid(
            Commodity(namespace="CURRENCY", mnemonic="USD", fullname="US Dollar", fraction=100),
            "99999999999999999999999999999998",
        )
        root = _assign_guid(book.root_account, ROOT)
        assets = _assign_guid(Account(name="Assets", type="ASSET", parent=root, commodity=sek), ASSETS)
        checking = _assign_guid(Account(name="Checking", type="BANK", parent=assets, commodity=sek), CHECKING)
        food = _assign_guid(Account(name="Food", type="EXPENSE", parent=root, commodity=sek), FOOD)
        usd_cash = _assign_guid(Account(name="USD Cash", type="CASH", parent=assets, commodity=usd), EUR_ACCOUNT)

        for index in range(30):
            tx = _assign_guid(
                Transaction(
                    currency=sek,
                    description=f"bounded activity {index:02d}",
                    post_date=date(2026, 5, (index % 28) + 1),
                    splits=[
                        Split(account=checking, value=Decimal("-1.00")),
                        Split(account=food, value=Decimal("1.00")),
                    ],
                ),
                f"{index + 1:032x}",
            )
            for split_index, split in enumerate(tx.splits, start=1):
                _assign_guid(split, f"{10_000 + index * 10 + split_index:032x}")
        _assign_guid(
            Transaction(
                currency=sek,
                description="other commodity ignored for selected account",
                post_date=date(2026, 5, 15),
                splits=[
                    Split(account=usd_cash, value=Decimal("10.00"), quantity=Decimal("2.50")),
                    Split(account=food, value=Decimal("-10.00")),
                ],
            ),
            "88888888888888888888888888888888",
        )
        book.save()
        book.close()

        transaction_loads: list[str] = []
        split_loads: list[str] = []

        def on_transaction_load(target, context):
            transaction_loads.append(target.guid)

        def on_split_load(target, context):
            split_loads.append(target.guid)

        event.listen(piecash.Transaction, "load", on_transaction_load)
        event.listen(piecash.Split, "load", on_split_load)
        try:
            response = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"}).get_account_activity(
                CHECKING,
                date_from=date(2026, 5, 1),
                date_to=date(2026, 5, 31),
                limit=5,
                book_id=42,
            )
        finally:
            event.remove(piecash.Transaction, "load", on_transaction_load)
            event.remove(piecash.Split, "load", on_split_load)

        assert response.account_id == CHECKING
        assert response.change is not None
        assert response.change.amount == "-30"
        assert response.has_more is True
        assert response.scan.query_count <= 10
        assert response.scan.recent_transaction_objects == 6
        assert len(transaction_loads) <= 6
        assert len(split_loads) <= 12
        assert response.scan.recent_split_rows <= 12
        assert response.scan.serialized_bytes <= response.scan.limits["serialized_bytes"]

    def test_source_guards_do_not_use_legacy_transaction_list_or_count_paths(self):
        import app.routers.books as books_router
        import app.services.gnucash_book as gnucash_book
        import app.services.account_explorer as account_explorer

        overview_source = inspect.getsource(gnucash_book.GnuCashBookService.get_account_overview)
        activity_source = inspect.getsource(gnucash_book.GnuCashBookService.get_account_activity)
        router_overview_source = inspect.getsource(books_router.get_book_account_overview)
        router_activity_source = inspect.getsource(books_router.get_book_account_activity)
        activity_builder_source = inspect.getsource(account_explorer.build_account_activity_response)

        for source in (overview_source, activity_source, router_overview_source, router_activity_source, activity_builder_source):
            assert "count_transactions" not in source
            assert "list_transactions(" not in source
            assert "get_balance(" not in source
            assert "format_money" not in source
        assert "book.transactions" not in activity_builder_source
