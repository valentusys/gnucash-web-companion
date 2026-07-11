"""Tests for read-only reports API endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import User, Book, UserBookAccess
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.gnucash_book import GnuCashBookService
from app.services.gnucash_exceptions import GnuCashReadError

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password="testpassword123",
)


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
        session.commit()

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def auth_token(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "testpassword123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_book(session_factory):
    with session_factory() as session:
        book = Book(
            name="Test Book",
            storage_type="sqlite",
            uri_or_path="/data/books/test.gnucash.sqlite",
            base_currency="SEK",
            is_default=True,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        book_id = book.id
    return book_id


@pytest.fixture
def viewer_user(session_factory):
    with session_factory() as session:
        user = User(
            username="viewer",
            display_name="Viewer",
            password_hash=hash_password("viewerpass"),
        )
        session.add(user)
        session.commit()
        user_id = user.id
    return user_id


@pytest.fixture
def viewer_token(client, viewer_user):
    response = client.post(
        "/auth/login",
        json={"username": "viewer", "password": "viewerpass"},
    )
    return response.json()["access_token"]


@pytest.fixture
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}


# ---------------------------------------------------------------------------
# Fake GnuCash fixtures for reports
# ---------------------------------------------------------------------------


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
    splits: list = field(default_factory=list)


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


class FakeBookForReports:
    def __init__(self, accounts=None, transactions=None):
        self.accounts = accounts or []
        self.transactions = transactions or []
        self.closed = False

    def close(self):
        self.closed = True


@pytest.fixture
def fake_report_data():
    """Create a realistic set of accounts and transactions for report testing."""
    root = FakeAccount(guid="root-assets", name="Assets", type="ROOT")
    bank = FakeAccount(guid="bank", name="Bank", type="ASSET", parent=root)
    checking = FakeAccount(
        guid="checking",
        name="Checking",
        type="BANK",
        parent=bank,
        balance=Decimal("150000.00"),
    )
    savings = FakeAccount(
        guid="savings",
        name="Savings",
        type="ASSET",
        parent=bank,
        balance=Decimal("50000.00"),
    )

    root_liab = FakeAccount(guid="root-liab", name="Liabilities", type="ROOT")
    credit_card = FakeAccount(
        guid="cc",
        name="Credit Card",
        type="CREDIT",
        parent=root_liab,
        balance=Decimal("-30000.00"),
    )

    root_income = FakeAccount(guid="root-income", name="Income", type="ROOT")
    salary = FakeAccount(
        guid="salary",
        name="Salary",
        type="INCOME",
        parent=root_income,
        balance=Decimal("0"),
    )

    root_expense = FakeAccount(guid="root-expense", name="Expenses", type="ROOT")
    food = FakeAccount(
        guid="food",
        name="Food",
        type="EXPENSE",
        parent=root_expense,
        balance=Decimal("0"),
    )
    rent = FakeAccount(
        guid="rent",
        name="Rent",
        type="EXPENSE",
        parent=root_expense,
        balance=Decimal("0"),
    )
    utilities = FakeAccount(
        guid="utilities",
        name="Utilities",
        type="EXPENSE",
        parent=root_expense,
        balance=Decimal("0"),
    )

    # Transactions this month (May 2026)
    tx_salary = FakeTransaction(
        guid="tx-salary",
        post_date=date(2026, 5, 1),
        description="Monthly salary",
        splits=[
            FakeSplit(account=checking, value=Decimal("45000.00")),
            FakeSplit(account=salary, value=Decimal("-45000.00")),
        ],
    )

    tx_rent = FakeTransaction(
        guid="tx-rent",
        post_date=date(2026, 5, 2),
        description="Rent payment",
        splits=[
            FakeSplit(account=checking, value=Decimal("-12000.00")),
            FakeSplit(account=rent, value=Decimal("12000.00")),
        ],
    )

    tx_groceries1 = FakeTransaction(
        guid="tx-groceries1",
        post_date=date(2026, 5, 5),
        description="ICA Nara",
        splits=[
            FakeSplit(account=checking, value=Decimal("-850.00")),
            FakeSplit(account=food, value=Decimal("850.00")),
        ],
    )

    tx_groceries2 = FakeTransaction(
        guid="tx-groceries2",
        post_date=date(2026, 5, 10),
        description="Willys",
        splits=[
            FakeSplit(account=checking, value=Decimal("-620.00")),
            FakeSplit(account=food, value=Decimal("620.00")),
        ],
    )

    tx_utilities = FakeTransaction(
        guid="tx-utilities",
        post_date=date(2026, 5, 15),
        description="Electric bill",
        splits=[
            FakeSplit(account=checking, value=Decimal("-1530.00")),
            FakeSplit(account=utilities, value=Decimal("1530.00")),
        ],
    )

    accounts = [root, bank, checking, savings, root_liab, credit_card,
                root_income, salary, root_expense, food, rent, utilities]
    transactions = [tx_salary, tx_rent, tx_groceries1, tx_groceries2, tx_utilities]
    return accounts, transactions


@pytest.fixture
def fake_book_for_reports(tmp_path, monkeypatch, fake_report_data):
    book_path = tmp_path / "test-reports.gnucash"
    book_path.write_text("fake")
    accounts, transactions = fake_report_data

    def fake_open_book(path, readonly=False):
        return FakeBookForReports(accounts=accounts, transactions=transactions)

    def fake_open_book_uri(*, uri_conn, readonly=False):
        return FakeBookForReports(accounts=accounts, transactions=transactions)

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path


@pytest.fixture
def empty_fake_book_for_reports(tmp_path, monkeypatch):
    book_path = tmp_path / "empty-reports.gnucash"
    book_path.write_text("fake")

    def fake_open_book(path, readonly=False):
        return FakeBookForReports(accounts=[], transactions=[])

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path


# ---------------------------------------------------------------------------
# Tests: GET /reports/summary (MVP alias)
# ---------------------------------------------------------------------------


class TestReportSummaryMVP:
    def test_requires_auth(self, client):
        response = client.get("/reports/summary")
        assert response.status_code == 401

    def test_invalid_as_of_date_returns_clear_client_error(self, client, auth_headers, sample_book):
        response = client.get(
            "/reports/summary?as_of_date=not-a-date",
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "as_of_date must be a valid YYYY-MM-DD date"

    def test_empty_book_returns_conservative_zero_summary(
        self, client, auth_headers, sample_book, empty_fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(empty_fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/summary?as_of_date=2026-05-16",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["net_worth"] == "0.00"
        assert data["assets"] == "0.00"
        assert data["liabilities"] == "0.00"
        assert data["income_this_month"] == "0.00"
        assert data["expenses_this_month"] == "0.00"
        limitations = " ".join(data["limitations"])
        assert "reporting_basis=base_currency_only" in limitations
        assert "no currency conversion" in limitations
        assert "commodity is SEK" in limitations
        assert "No accounts with base currency SEK were detected" in limitations

    def test_returns_summary_shape(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/summary?as_of_date=2026-05-16",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "currency" in data
        assert "net_worth" in data
        assert "assets" in data
        assert "liabilities" in data
        assert "income_this_month" in data
        assert "expenses_this_month" in data
        assert "as_of_date" in data
        assert "reporting_basis" in data
        assert "includes_currency_conversion" in data
        assert "limitations" in data
        assert data["currency"] == "SEK"
        assert data["as_of_date"] == "2026-05-16"
        assert data["reporting_basis"] == "base_currency_only"
        assert data["includes_currency_conversion"] is False
        limitations = " ".join(data["limitations"])
        assert "reporting_basis=base_currency_only" in limitations
        assert "no currency conversion" in limitations
        assert "commodity is SEK" in limitations

    def test_summary_values(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/summary?as_of_date=2026-05-16",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # Assets: checking 150000 + savings 50000 = 200000
        assert data["assets"] == "200000.00"
        # Liabilities: credit card -30000
        assert data["liabilities"] == "-30000.00"
        # Net worth: 200000 + (-30000) = 170000
        assert data["net_worth"] == "170000.00"
        # Income this month: salary 45000
        assert data["income_this_month"] == "45000.00"
        # Expenses this month: rent 12000 + food 1470 + utilities 1530 = -15000
        assert data["expenses_this_month"] == "-15000.00"

    def test_summary_falls_back_to_current_base_currency_splits_when_balances_are_zero(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        checking = FakeAccount(guid="checking", name="Checking", type="BANK", commodity=sek, parent=root)
        credit_card = FakeAccount(guid="cc", name="Credit Card", type="CREDIT", commodity=sek, parent=root)
        salary = FakeAccount(guid="salary", name="Salary", type="INCOME", commodity=sek, parent=root)
        food = FakeAccount(guid="food", name="Food", type="EXPENSE", commodity=sek, parent=root)
        equity = FakeAccount(guid="equity", name="Equity", type="EQUITY", commodity=sek, parent=root)
        old_expense = FakeAccount(guid="old-food", name="Old Food", type="EXPENSE", commodity=sek, parent=root)
        eur = FakeCommodity(mnemonic="EUR")
        eur_bank = FakeAccount(guid="eur-bank", name="EUR Bank", type="BANK", commodity=eur, parent=root)
        accounts = [root, checking, credit_card, salary, food, equity, old_expense, eur_bank]
        transactions = [
            FakeTransaction(
                guid="opening-cash",
                post_date=date(2026, 5, 1),
                description="Opening checking balance",
                splits=[
                    FakeSplit(account=checking, value=Decimal("1000.00")),
                    FakeSplit(account=equity, value=Decimal("-1000.00")),
                ],
            ),
            FakeTransaction(
                guid="opening-card",
                post_date=date(2026, 5, 1),
                description="Opening credit card balance",
                splits=[
                    FakeSplit(account=credit_card, value=Decimal("-200.00")),
                    FakeSplit(account=equity, value=Decimal("200.00")),
                ],
            ),
            FakeTransaction(
                guid="salary-current",
                post_date=date(2026, 5, 10),
                description="Current salary",
                splits=[
                    FakeSplit(account=checking, value=Decimal("500.00")),
                    FakeSplit(account=salary, value=Decimal("-500.00")),
                ],
            ),
            FakeTransaction(
                guid="food-current",
                post_date=date(2026, 5, 11),
                description="Current groceries",
                splits=[
                    FakeSplit(account=checking, value=Decimal("-50.00")),
                    FakeSplit(account=food, value=Decimal("50.00")),
                ],
            ),
            FakeTransaction(
                guid="old-food",
                post_date=date(2026, 4, 30),
                description="Prior month groceries",
                splits=[
                    FakeSplit(account=checking, value=Decimal("-30.00")),
                    FakeSplit(account=old_expense, value=Decimal("30.00")),
                ],
            ),
            FakeTransaction(
                guid="future-salary",
                post_date=date(2026, 6, 1),
                description="Future salary",
                splits=[
                    FakeSplit(account=checking, value=Decimal("700.00")),
                    FakeSplit(account=salary, value=Decimal("-700.00")),
                ],
            ),
            FakeTransaction(
                guid="eur-transfer",
                post_date=date(2026, 5, 12),
                description="Foreign currency transfer",
                splits=[FakeSplit(account=eur_bank, value=Decimal("999.00"))],
            ),
        ]

        def fake_open_book(path, readonly=False):
            return FakeBookForReports(accounts=accounts, transactions=transactions)

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/summary?as_of_date=2026-05-16",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assets"] == "1420.00"
        assert data["liabilities"] == "-200.00"
        assert data["net_worth"] == "1220.00"
        assert data["income_this_month"] == "500.00"
        assert data["expenses_this_month"] == "-50.00"
        for key in ("assets", "liabilities", "net_worth", "income_this_month", "expenses_this_month"):
            assert isinstance(data[key], str)

    def test_mixed_currency_splits_are_excluded_and_disclosed_without_conversion(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        eur = FakeCommodity(mnemonic="EUR")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        checking = FakeAccount(guid="checking", name="Checking", type="BANK", commodity=sek, parent=root)
        salary = FakeAccount(guid="salary", name="Salary", type="INCOME", commodity=sek, parent=root)
        food = FakeAccount(guid="food", name="Food", type="EXPENSE", commodity=sek, parent=root)
        eur_travel = FakeAccount(guid="eur-travel", name="EUR Travel", type="EXPENSE", commodity=eur, parent=root)
        accounts = [root, checking, salary, food]
        transactions = [
            FakeTransaction(
                guid="mixed-income-eur-expense",
                post_date=date(2026, 5, 8),
                description="Mixed-currency synthetic transaction",
                splits=[
                    FakeSplit(account=salary, value=Decimal("-100.00")),
                    FakeSplit(account=eur_travel, value=Decimal("9999.99")),
                ],
            ),
            FakeTransaction(
                guid="base-expense",
                post_date=date(2026, 5, 9),
                description="Base-currency expense",
                splits=[
                    FakeSplit(account=checking, value=Decimal("-25.00")),
                    FakeSplit(account=food, value=Decimal("25.00")),
                ],
            ),
        ]

        def fake_open_book(path, readonly=False):
            return FakeBookForReports(accounts=accounts, transactions=transactions)

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/summary?as_of_date=2026-05-16",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["currency"] == "SEK"
        assert data["income_this_month"] == "100.00"
        assert data["expenses_this_month"] == "-25.00"
        assert data["assets"] == "-25.00"
        limitations = " ".join(data["limitations"])
        assert "EUR" in limitations
        assert "excluded rather than converted or combined" in limitations
        assert "no currency conversion" in limitations

    def test_negative_contra_balances_remain_signed_decimal_strings(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        contra_asset = FakeAccount(
            guid="contra-asset",
            name="Contra Asset",
            type="ASSET",
            commodity=sek,
            parent=root,
            balance=Decimal("-125.50"),
        )
        positive_liability = FakeAccount(
            guid="contra-liability",
            name="Contra Liability",
            type="LIABILITY",
            commodity=sek,
            parent=root,
            balance=Decimal("25.25"),
        )
        accounts = [root, contra_asset, positive_liability]

        def fake_open_book(path, readonly=False):
            return FakeBookForReports(accounts=accounts, transactions=[])

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/summary?as_of_date=2026-05-16",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assets"] == "-125.50"
        assert data["liabilities"] == "25.25"
        assert data["net_worth"] == "-100.25"
        assert isinstance(data["assets"], str)

    def test_multi_currency_accounts_are_excluded_from_base_currency_summary(
        self,
        client,
        auth_headers,
        sample_book,
        fake_report_data,
        fake_book_for_reports,
        session_factory,
    ):
        accounts, transactions = fake_report_data
        eur_commodity = FakeCommodity(mnemonic="EUR")
        eur_assets_root = FakeAccount(guid="root-eur-assets", name="EUR Assets", type="ROOT", commodity=eur_commodity)
        eur_bank = FakeAccount(
            guid="eur-bank",
            name="EUR Bank",
            type="BANK",
            commodity=eur_commodity,
            parent=eur_assets_root,
            balance=Decimal("999999.00"),
        )
        accounts.extend([eur_assets_root, eur_bank])

        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/summary?as_of_date=2026-05-16",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["currency"] == "SEK"
        # EUR account is intentionally ignored; reports do not do fake FX conversion.
        assert data["assets"] == "200000.00"
        assert data["net_worth"] == "170000.00"

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get("/reports/summary", headers=viewer_headers)
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /reports/recent-transactions (MVP alias)
# ---------------------------------------------------------------------------


class TestRecentTransactionsMVP:
    def test_requires_auth(self, client):
        response = client.get("/reports/recent-transactions")
        assert response.status_code == 401

    def test_returns_recent_transactions(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get("/reports/recent-transactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
        if len(data) > 0:
            item = data[0]
            assert "id" in item
            assert "date" in item
            assert "description" in item
            assert "amount" in item
            assert "currency" in item

    def test_limit_param(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/recent-transactions?limit=2",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_empty_book_returns_empty_recent_transactions(
        self, client, auth_headers, sample_book, empty_fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(empty_fake_book_for_reports)
            session.commit()

        response = client.get("/reports/recent-transactions", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get("/reports/recent-transactions", headers=viewer_headers)
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /reports/expenses-by-account (MVP alias)
# ---------------------------------------------------------------------------


class TestExpensesByAccountMVP:
    def test_requires_auth(self, client):
        response = client.get("/reports/expenses-by-account")
        assert response.status_code == 401

    def test_invalid_date_returns_clear_client_error(self, client, auth_headers, sample_book):
        response = client.get(
            "/reports/expenses-by-account?date_from=2026-05-01&date_to=bad-date",
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "date_to must be a valid YYYY-MM-DD date"

    def test_incomplete_date_range_returns_clear_client_error(self, client, auth_headers, sample_book):
        response = client.get(
            "/reports/expenses-by-account?date_from=2026-05-01",
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "date_from and date_to must be provided together"

    def test_returns_expenses_list(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/expenses-by-account?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for item in data:
            assert "account_id" in item
            assert "account_name" in item
            assert "total" in item
            assert "currency" in item

    def test_empty_book_returns_empty_expenses_list(
        self, client, auth_headers, sample_book, empty_fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(empty_fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/expenses-by-account?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_expenses_sorted_by_total_desc(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/expenses-by-account?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        totals = [Decimal(item["total"]) for item in data]
        assert totals == sorted(totals, reverse=True)


# ---------------------------------------------------------------------------
# Tests: GET /reports/cashflow (MVP alias)
# ---------------------------------------------------------------------------


class TestCashflowMVP:
    def test_requires_auth(self, client):
        response = client.get("/reports/cashflow")
        assert response.status_code == 401

    def test_invalid_date_returns_clear_client_error(self, client, auth_headers, sample_book):
        response = client.get(
            "/reports/cashflow?date_from=not-a-date&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "date_from must be a valid YYYY-MM-DD date"

    def test_incomplete_date_range_returns_clear_client_error(self, client, auth_headers, sample_book):
        response = client.get(
            "/reports/cashflow?date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "date_from and date_to must be provided together"

    def test_returns_cashflow(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/cashflow?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "date_from" in data
        assert "date_to" in data
        assert "currency" in data
        assert "inflow" in data
        assert "outflow" in data
        assert "net" in data

    def test_empty_book_returns_zero_cashflow(
        self, client, auth_headers, sample_book, empty_fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(empty_fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/cashflow?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["currency"] == "SEK"
        assert data["inflow"] == "0.00"
        assert data["outflow"] == "0.00"
        assert data["net"] == "0.00"

    def test_cashflow_excludes_non_base_currency_splits(
        self,
        client,
        auth_headers,
        sample_book,
        fake_report_data,
        fake_book_for_reports,
        session_factory,
    ):
        accounts, transactions = fake_report_data
        eur_commodity = FakeCommodity(mnemonic="EUR")
        eur_income = FakeAccount(guid="eur-income", name="EUR Income", type="INCOME", commodity=eur_commodity)
        eur_expense = FakeAccount(guid="eur-expense", name="EUR Expense", type="EXPENSE", commodity=eur_commodity)
        accounts.extend([eur_income, eur_expense])
        transactions.append(
            FakeTransaction(
                guid="tx-eur",
                post_date=date(2026, 5, 20),
                description="EUR transaction",
                splits=[
                    FakeSplit(account=eur_income, value=Decimal("-999999.00")),
                    FakeSplit(account=eur_expense, value=Decimal("999999.00")),
                ],
            )
        )

        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/cashflow?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["currency"] == "SEK"
        assert data["inflow"] == "45000.00"
        assert data["outflow"] == "15000.00"
        assert data["net"] == "30000.00"

    def test_by_month_returns_list(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            "/reports/cashflow?date_from=2026-05-01&date_to=2026-05-31&by_month=true",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for period in data:
            assert "month" in period
            assert "inflow" in period
            assert "outflow" in period
            assert "net" in period


# ---------------------------------------------------------------------------
# Tests: Book-aware endpoints
# ---------------------------------------------------------------------------


class TestBookAwareReports:
    def test_book_summary_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/reports/summary")
        assert response.status_code == 401

    def test_book_summary_returns_data(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports/summary?as_of_date=2026-05-16",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["currency"] == "SEK"
        assert data["as_of_date"] == "2026-05-16"

    def test_book_recent_transactions(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports/recent-transactions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_book_expenses_by_account(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports/expenses-by-account?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_book_cashflow(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports/cashflow?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "inflow" in data
        assert "outflow" in data
        assert "net" in data

    def test_book_access_denied(
        self, client, viewer_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports/summary",
            headers=viewer_headers,
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/reports (period vertical slice)
# ---------------------------------------------------------------------------


class TestBookPeriodReport:
    def test_period_report_requires_auth(self, client, sample_book):
        response = client.get(
            f"/books/{sample_book}/reports?date_from=2026-05-01&date_to=2026-05-31"
        )

        assert response.status_code == 401

    def test_period_report_returns_combined_readonly_sections(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["book_id"] == sample_book
        assert data["date_from"] == "2026-05-01"
        assert data["date_to"] == "2026-05-31"
        assert data["currency"] == "SEK"
        assert data["reporting_basis"] == "base_currency_only"
        assert data["includes_currency_conversion"] is False
        assert data["partial_failure"] is False
        assert data["empty"] is False
        assert data["summary"]["net_worth"] == "170000.00"
        assert data["cashflow"] == {
            "date_from": "2026-05-01",
            "date_to": "2026-05-31",
            "currency": "SEK",
            "inflow": "45000.00",
            "outflow": "15000.00",
            "net": "30000.00",
        }
        assert data["monthly_cashflow"] == [
            {"month": "2026-05", "inflow": "45000.00", "outflow": "15000.00", "net": "30000.00"}
        ]
        assert [item["account_id"] for item in data["expenses_by_account"]] == [
            "rent",
            "utilities",
            "food",
        ]
        assert {status["section"]: status["status"] for status in data["section_statuses"]} == {
            "summary": "ok",
            "cashflow": "ok",
            "monthly_cashflow": "ok",
            "expenses_by_account": "ok",
        }
        limitations = " ".join(data["limitations"])
        assert "base_currency_only" in limitations
        assert "no currency conversion" in limitations

    def test_period_report_summary_is_balance_only_for_arbitrary_period(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports?date_from=2026-05-10&date_to=2026-05-15",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["date_from"] == "2026-05-10"
        assert data["date_to"] == "2026-05-15"
        assert "income_this_month" not in data["summary"]
        assert "expenses_this_month" not in data["summary"]
        assert data["summary"]["as_of_date"] == "2026-05-15"
        assert data["cashflow"] == {
            "date_from": "2026-05-10",
            "date_to": "2026-05-15",
            "currency": "SEK",
            "inflow": "0.00",
            "outflow": "2150.00",
            "net": "-2150.00",
        }
        assert data["monthly_cashflow"] == [
            {"month": "2026-05", "inflow": "0.00", "outflow": "2150.00", "net": "-2150.00"}
        ]

    def test_period_report_empty_book_is_not_a_partial_failure(
        self, client, auth_headers, sample_book, empty_fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(empty_fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["partial_failure"] is False
        assert data["empty"] is True
        assert data["summary"]["net_worth"] == "0.00"
        assert data["cashflow"]["net"] == "0.00"
        assert data["monthly_cashflow"] == []
        assert data["expenses_by_account"] == []
        assert {status["section"]: status["status"] for status in data["section_statuses"]} == {
            "summary": "empty",
            "cashflow": "empty",
            "monthly_cashflow": "empty",
            "expenses_by_account": "empty",
        }

    def test_period_report_rejects_invalid_and_reversed_ranges(self, client, auth_headers, sample_book):
        invalid = client.get(
            f"/books/{sample_book}/reports?date_from=not-a-date&date_to=2026-05-31",
            headers=auth_headers,
        )
        reversed_range = client.get(
            f"/books/{sample_book}/reports?date_from=2026-06-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert invalid.status_code == 422
        assert invalid.json()["detail"] == "date_from must be a valid YYYY-MM-DD date"
        assert reversed_range.status_code == 422
        assert reversed_range.json()["detail"] == "date_from must be on or before date_to"

    def test_period_report_requires_book_view_access(
        self, client, viewer_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports?date_from=2026-05-01&date_to=2026-05-31",
            headers=viewer_headers,
        )

        assert response.status_code == 403

    def test_period_report_discloses_mixed_and_unknown_currency_limitations(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        eur = FakeCommodity(mnemonic="EUR")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        checking = FakeAccount(guid="checking", name="Checking", type="BANK", commodity=sek, parent=root)
        eur_travel = FakeAccount(guid="eur-travel", name="EUR Travel", type="EXPENSE", commodity=eur, parent=root)
        accounts = [root, checking, eur_travel]
        transactions = [
            FakeTransaction(
                guid="eur-only",
                post_date=date(2026, 5, 8),
                description="EUR-only synthetic expense",
                splits=[FakeSplit(account=eur_travel, value=Decimal("999.99"))],
            )
        ]

        def fake_open_book(path, readonly=False):
            return FakeBookForReports(accounts=accounts, transactions=transactions)

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            book.base_currency = None
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["currency"] == "XXX"
        limitations = " ".join(data["limitations"])
        assert "unknown (XXX)" in limitations
        assert "zero totals may mean no matching base-currency accounts" in limitations
        assert "EUR" in limitations
        assert "no currency conversion" in limitations

    def test_period_report_preserves_signed_decimal_strings(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        contra_asset = FakeAccount(
            guid="contra-asset",
            name="Contra Asset",
            type="ASSET",
            commodity=sek,
            parent=root,
            balance=Decimal("-125.50"),
        )
        positive_liability = FakeAccount(
            guid="positive-liability",
            name="Positive Liability",
            type="LIABILITY",
            commodity=sek,
            parent=root,
            balance=Decimal("25.25"),
        )
        accounts = [root, contra_asset, positive_liability]

        def fake_open_book(path, readonly=False):
            return FakeBookForReports(accounts=accounts, transactions=[])

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        summary = response.json()["summary"]
        assert summary["assets"] == "-125.50"
        assert summary["liabilities"] == "25.25"
        assert summary["net_worth"] == "-100.25"
        assert isinstance(summary["assets"], str)

    def test_period_report_partial_section_failure_is_user_safe(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        def fail_expenses(self, date_from=None, date_to=None):
            raise GnuCashReadError("cannot read /private/books/leaked.gnucash.sqlite")

        monkeypatch.setattr(GnuCashBookService, "get_expenses_by_account", fail_expenses)

        response = client.get(
            f"/books/{sample_book}/reports?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["partial_failure"] is True
        assert data["empty"] is False
        assert data["summary"]["net_worth"] == "170000.00"
        assert data["expenses_by_account"] == []
        statuses = {status["section"]: status for status in data["section_statuses"]}
        assert statuses["expenses_by_account"]["status"] == "error"
        assert statuses["expenses_by_account"]["detail"] == "Report section could not be read safely from this runtime."
        serialized = response.text
        assert "/private" not in serialized
        assert "leaked.gnucash" not in serialized

    def test_period_report_serializes_money_as_strings_not_floats(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_reports)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/reports?date_from=2026-05-01&date_to=2026-05-31",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        money_values = [
            data["summary"]["net_worth"],
            data["summary"]["assets"],
            data["summary"]["liabilities"],
            data["cashflow"]["inflow"],
            data["cashflow"]["outflow"],
            data["cashflow"]["net"],
            data["monthly_cashflow"][0]["inflow"],
            data["monthly_cashflow"][0]["outflow"],
            data["monthly_cashflow"][0]["net"],
            data["expenses_by_account"][0]["total"],
        ]
        assert all(isinstance(value, str) for value in money_values)

    def test_period_report_service_opens_books_readonly_without_mutation_helpers(
        self, fake_report_data, tmp_path, monkeypatch
    ):
        book_path = tmp_path / "readonly-period-report.gnucash"
        book_path.write_text("fake")
        accounts, transactions = fake_report_data
        readonly_flags: list[bool] = []

        class MutationGuardBook(FakeBookForReports):
            def save(self):  # pragma: no cover - failure path only
                raise AssertionError("period reports must not save GnuCash books")

            def flush(self):  # pragma: no cover - failure path only
                raise AssertionError("period reports must not flush GnuCash books")

        def fake_open_book(path, readonly=False):
            readonly_flags.append(readonly)
            return MutationGuardBook(accounts=accounts, transactions=transactions)

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)

        service = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"})
        report = service.get_period_report("2026-05-01", "2026-05-31", book_id=123)

        assert report.book_id == 123
        assert report.partial_failure is False
        assert readonly_flags
        assert all(readonly_flags)
