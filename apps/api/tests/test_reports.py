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
from app.schemas.gnucash import PeriodReportDTO, PeriodReportSectionStatusDTO, PeriodReportSummaryDTO
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
        assert data["status"] == "setup_required"
        assert "net_worth" not in data
        assert "assets" not in data
        assert "liabilities" not in data
        assert "income_this_month" not in data
        assert "expenses_this_month" not in data
        assert data["reporting_currency"]["status"] == "setup_required"
        assert data["reporting_currency"]["source"] == "none"
        assert data["reporting_currency"]["reason"] == "no_eligible_currency"
        assert data["reporting_currency"]["configured_currency"] == "SEK"
        assert data["reporting_currency"]["configured_currency_status"] == "absent"
        assert data["reporting_currency"]["selected_currency"] is None
        assert data["reporting_currency"]["candidates"] == []
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
        # Liabilities expose a natural-sign display value while net worth uses
        # signed balance-sheet arithmetic: 200000 - 30000 = 170000.
        assert data["liabilities"] == "30000.00"
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
        assert data["liabilities"] == "200.00"
        assert data["net_worth"] == "1220.00"
        assert data["income_this_month"] == "500.00"
        assert data["expenses_this_month"] == "-50.00"
        for key in ("assets", "liabilities", "net_worth", "income_this_month", "expenses_this_month"):
            assert isinstance(data[key], str)

    def test_zero_liabilities_do_not_serialize_negative_zero(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        checking = FakeAccount(
            guid="checking",
            name="Checking",
            type="BANK",
            commodity=sek,
            parent=root,
            balance=Decimal("100.00"),
        )
        credit_card = FakeAccount(
            guid="cc",
            name="Credit Card",
            type="CREDIT",
            commodity=sek,
            parent=root,
            balance=Decimal("-0.00"),
        )
        equity = FakeAccount(guid="equity", name="Equity", type="EQUITY", commodity=sek, parent=root)
        accounts = [root, checking, credit_card, equity]
        transactions = [
            FakeTransaction(
                guid="opening-cash",
                post_date=date(2026, 5, 1),
                description="Opening checking balance",
                splits=[
                    FakeSplit(account=checking, value=Decimal("100.00")),
                    FakeSplit(account=equity, value=Decimal("-100.00")),
                ],
            )
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
        assert data["assets"] == "100.00"
        assert data["liabilities"] == "0.00"
        assert data["net_worth"] == "100.00"

    def test_mixed_currency_splits_are_excluded_and_disclosed_without_conversion(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        eur = FakeCommodity(mnemonic="EUR")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        checking = FakeAccount(guid="checking", name="Checking", type="BANK", commodity=sek, parent=root)
        sek_card = FakeAccount(guid="sek-card", name="SEK Credit Card", type="CREDIT", commodity=sek, parent=root)
        salary = FakeAccount(guid="salary", name="Salary", type="INCOME", commodity=sek, parent=root)
        food = FakeAccount(guid="food", name="Food", type="EXPENSE", commodity=sek, parent=root)
        eur_travel = FakeAccount(guid="eur-travel", name="EUR Travel", type="EXPENSE", commodity=eur, parent=root)
        eur_card = FakeAccount(guid="eur-card", name="EUR Credit Card", type="CREDIT", commodity=eur, parent=root)
        accounts = [root, checking, sek_card, salary, food, eur_travel, eur_card]
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
            FakeTransaction(
                guid="base-card-charge",
                post_date=date(2026, 5, 10),
                description="Base-currency card charge",
                splits=[
                    FakeSplit(account=sek_card, value=Decimal("-40.00")),
                    FakeSplit(account=food, value=Decimal("40.00")),
                ],
            ),
            FakeTransaction(
                guid="foreign-card-charge",
                post_date=date(2026, 5, 10),
                description="Foreign-currency card charge",
                splits=[
                    FakeSplit(account=eur_card, value=Decimal("-9999.99")),
                    FakeSplit(account=eur_travel, value=Decimal("9999.99")),
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
        assert data["expenses_this_month"] == "-65.00"
        assert data["assets"] == "-25.00"
        assert data["liabilities"] == "40.00"
        assert data["net_worth"] == "-65.00"
        limitations = " ".join(data["limitations"])
        assert "EUR" in limitations
        assert "excluded rather than converted or combined" in limitations
        assert "no currency conversion" in limitations

    def test_summary_contract_uses_signed_calculation_and_natural_liability_display(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        checking = FakeAccount(guid="checking", name="Checking", type="BANK", commodity=sek, parent=root, balance=Decimal("1000.00"))
        credit_card = FakeAccount(
            guid="credit-card",
            name="Credit Card",
            type="CREDIT",
            commodity=sek,
            parent=root,
            balance=Decimal("-200.00"),
        )
        payable = FakeAccount(
            guid="payable",
            name="Payable",
            type="PAYABLE",
            commodity=sek,
            parent=root,
            balance=Decimal("-30.25"),
        )
        loan = FakeAccount(
            guid="loan",
            name="Loan",
            type="LIABILITY",
            commodity=sek,
            parent=root,
            balance=Decimal("-69.75"),
        )
        zero_liability = FakeAccount(
            guid="zero-liability",
            name="Zero Liability",
            type="LIABILITY",
            commodity=sek,
            parent=root,
            balance=Decimal("0.00"),
        )
        contra_liability = FakeAccount(
            guid="contra-liability",
            name="Contra Liability",
            type="LIABILITY",
            commodity=sek,
            parent=root,
            balance=Decimal("25.00"),
        )
        salary = FakeAccount(guid="salary", name="Salary", type="INCOME", commodity=sek, parent=root)
        accounts = [root, checking, credit_card, payable, loan, zero_liability, contra_liability, salary]
        transactions = [
            FakeTransaction(
                guid="currency-activity",
                post_date=date(2026, 5, 16),
                description="Synthetic activity to make SEK reportable",
                splits=[
                    FakeSplit(account=checking, value=Decimal("1.00")),
                    FakeSplit(account=salary, value=Decimal("-1.00")),
                ],
            )
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
        assert data["assets"] == "1000.00"
        assert data["liabilities"] == "275.00"
        assert data["net_worth"] == "725.00"
        assert Decimal(data["net_worth"]) == Decimal(data["assets"]) - Decimal(data["liabilities"])

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
        assert data["status"] == "setup_required"
        assert data["reporting_currency"]["configured_currency"] == "SEK"
        assert data["reporting_currency"]["configured_currency_status"] == "inactive"
        assert data["reporting_currency"]["selected_currency"] is None
        assert "assets" not in data
        assert "liabilities" not in data
        assert "net_worth" not in data

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

        assert response.status_code == 409
        detail = response.json()["detail"]
        assert detail["code"] == "REPORTING_CURRENCY_SETUP_REQUIRED"
        assert detail["reporting_currency"]["status"] == "setup_required"
        assert detail["reporting_currency"]["selected_currency"] is None

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

        assert response.status_code == 409
        detail = response.json()["detail"]
        assert detail["code"] == "REPORTING_CURRENCY_SETUP_REQUIRED"
        assert detail["reporting_currency"]["status"] == "setup_required"
        assert detail["reporting_currency"]["selected_currency"] is None

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

        assert response.status_code == 409
        detail = response.json()["detail"]
        assert detail["code"] == "REPORTING_CURRENCY_SETUP_REQUIRED"
        assert detail["reporting_currency"]["status"] == "setup_required"
        assert detail["reporting_currency"]["selected_currency"] is None

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

    def test_period_report_auto_detects_only_active_currency_when_base_missing(
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
        assert data["currency"] == "EUR"
        limitations = " ".join(data["limitations"])
        assert "unknown (XXX)" not in limitations
        assert "commodity is EUR" in limitations
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

        assert response.status_code == 409
        detail = response.json()["detail"]
        assert detail["code"] == "REPORTING_CURRENCY_SETUP_REQUIRED"
        assert detail["reporting_currency"]["configured_currency"] == "SEK"
        assert detail["reporting_currency"]["configured_currency_status"] == "inactive"
        assert detail["reporting_currency"]["selected_currency"] is None

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


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/reports/comparison
# ---------------------------------------------------------------------------


class TestBookPeriodComparisonReport:
    previous_equivalent_query = (
        "date_from=2026-05-10&date_to=2026-05-15"
        "&comparison_mode=previous_equivalent"
        "&comparison_date_from=2026-05-04&comparison_date_to=2026-05-09"
    )

    @staticmethod
    def _point_book_at(session_factory, book_id: int, path: Path, *, base_currency: str | None = "SEK") -> None:
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == book_id).first()
            book.uri_or_path = str(path)
            book.base_currency = base_currency
            session.commit()

    def test_comparison_report_requires_auth_and_has_no_default_book_alias(self, client, auth_headers, sample_book):
        response = client.get(f"/books/{sample_book}/reports/comparison?{self.previous_equivalent_query}")
        alias = client.get(f"/reports/comparison?{self.previous_equivalent_query}", headers=auth_headers)

        assert response.status_code == 401
        assert alias.status_code == 404

    def test_previous_equivalent_returns_contract_shape_decimal_deltas_and_account_union(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        self._point_book_at(session_factory, sample_book, fake_book_for_reports)

        response = client.get(
            f"/books/{sample_book}/reports/comparison?{self.previous_equivalent_query}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["book_id"] == sample_book
        assert data["comparison_mode"] == "previous_equivalent"
        assert "date_from" not in data
        assert "date_to" not in data
        assert "comparison_date_from" not in data
        assert "comparison_date_to" not in data
        assert "delta" not in data
        assert data["primary"]["date_from"] == "2026-05-10"
        assert data["primary"]["date_to"] == "2026-05-15"
        assert data["comparison"]["date_from"] == "2026-05-04"
        assert data["comparison"]["date_to"] == "2026-05-09"
        assert data["primary"]["cashflow"]["outflow"] == "2150.00"
        assert data["comparison"]["cashflow"]["outflow"] == "850.00"
        assert data["primary"]["summary"]["liabilities"] == "30000.00"
        assert data["comparison"]["summary"]["liabilities"] == "30000.00"
        assert data["primary"]["summary"]["net_worth"] == "170000.00"
        assert data["summary_delta"]["liabilities"] == {
            "currency": "SEK",
            "primary": "30000.00",
            "comparison": "30000.00",
            "delta": "0.00",
            "absolute_delta": "0.00",
        }
        assert data["cashflow_delta"]["outflow"] == {
            "currency": "SEK",
            "primary": "2150.00",
            "comparison": "850.00",
            "delta": "1300.00",
            "absolute_delta": "1300.00",
        }
        assert data["cashflow_delta"]["net"]["delta"] == "-1300.00"
        assert data["cashflow_delta"]["net"]["absolute_delta"] == "1300.00"
        assert {status["section"]: status["status"] for status in data["delta_section_statuses"]} == {
            "summary": "ok",
            "cashflow": "ok",
            "expenses_by_account": "ok",
        }

        expense_rows = data["expense_changes"]
        assert [row["account_id"] for row in expense_rows] == ["utilities", "food"]
        assert expense_rows[0]["primary_total"] == "1530.00"
        assert expense_rows[0]["comparison_total"] == "0.00"
        assert expense_rows[0]["delta"] == "1530.00"
        assert expense_rows[0]["absolute_delta"] == "1530.00"
        assert expense_rows[1]["primary_total"] == "620.00"
        assert expense_rows[1]["comparison_total"] == "850.00"
        assert expense_rows[1]["delta"] == "-230.00"
        assert expense_rows[1]["absolute_delta"] == "230.00"
        assert all(isinstance(row["delta"], str) for row in expense_rows)

    def test_comparison_service_matches_independent_period_report_semantics(
        self, fake_book_for_reports
    ):
        service = GnuCashBookService(
            {"uri_or_path": str(fake_book_for_reports), "base_currency": "SEK", "id": 123}
        )

        primary = service.get_period_report(date(2026, 5, 10), date(2026, 5, 15), book_id=123)
        comparison = service.get_period_report(date(2026, 5, 4), date(2026, 5, 9), book_id=123)
        report = service.get_period_report_comparison(
            date(2026, 5, 10),
            date(2026, 5, 15),
            date(2026, 5, 4),
            date(2026, 5, 9),
            comparison_mode="previous_equivalent",
            book_id=123,
        )

        assert report.primary.model_dump() == primary.model_dump()
        assert report.comparison.model_dump() == comparison.model_dump()
        assert report.comparable is True
        assert report.cashflow_delta is not None
        assert report.cashflow_delta.net.delta == "-1300.00"
        assert [row.account_id for row in report.expense_changes] == ["utilities", "food"]

    def test_summary_delta_uses_natural_liability_values_with_non_zero_delta(self):
        service = GnuCashBookService({"uri_or_path": "synthetic://comparison", "base_currency": "SEK"})
        primary = PeriodReportDTO(
            book_id=123,
            date_from="2026-05-10",
            date_to="2026-05-15",
            currency="SEK",
            section_statuses=[PeriodReportSectionStatusDTO(section="summary", status="ok", detail=None)],
            summary=PeriodReportSummaryDTO(
                currency="SEK",
                assets="2000.00",
                liabilities="750.00",
                net_worth="1250.00",
                as_of_date="2026-05-15",
            ),
        )
        comparison = PeriodReportDTO(
            book_id=123,
            date_from="2026-05-04",
            date_to="2026-05-09",
            currency="SEK",
            section_statuses=[PeriodReportSectionStatusDTO(section="summary", status="ok", detail=None)],
            summary=PeriodReportSummaryDTO(
                currency="SEK",
                assets="1800.00",
                liabilities="500.00",
                net_worth="1300.00",
                as_of_date="2026-05-09",
            ),
        )
        statuses = []

        delta = service._summary_comparison_delta(
            primary,
            comparison,
            shared_currency="SEK",
            currency_detail=None,
            section_statuses=statuses,
        )

        assert delta is not None
        assert delta.liabilities.model_dump() == {
            "currency": "SEK",
            "primary": "750.00",
            "comparison": "500.00",
            "delta": "250.00",
            "absolute_delta": "250.00",
        }
        assert delta.net_worth.delta == "-50.00"
        assert [status.model_dump() for status in statuses] == [
            {"section": "summary", "status": "ok", "detail": None}
        ]

    def test_preset_modes_require_exact_server_derived_comparison_dates(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        self._point_book_at(session_factory, sample_book, fake_book_for_reports)

        previous_mismatch = client.get(
            f"/books/{sample_book}/reports/comparison?"
            "date_from=2026-05-10&date_to=2026-05-15"
            "&comparison_mode=previous_equivalent"
            "&comparison_date_from=2026-05-03&comparison_date_to=2026-05-08",
            headers=auth_headers,
        )
        leap_match = client.get(
            f"/books/{sample_book}/reports/comparison?"
            "date_from=2024-02-29&date_to=2024-03-31"
            "&comparison_mode=same_period_last_year"
            "&comparison_date_from=2023-02-28&comparison_date_to=2023-03-31",
            headers=auth_headers,
        )
        leap_mismatch = client.get(
            f"/books/{sample_book}/reports/comparison?"
            "date_from=2024-02-29&date_to=2024-03-31"
            "&comparison_mode=same_period_last_year"
            "&comparison_date_from=2023-03-01&comparison_date_to=2023-03-31",
            headers=auth_headers,
        )

        assert previous_mismatch.status_code == 422
        assert "previous_equivalent range 2026-05-04..2026-05-09" in previous_mismatch.json()["detail"]
        assert leap_match.status_code == 200
        assert leap_match.json()["comparison"]["date_from"] == "2023-02-28"
        assert leap_match.json()["comparison"]["date_to"] == "2023-03-31"
        assert leap_mismatch.status_code == 422
        assert "same_period_last_year range 2023-02-28..2023-03-31" in leap_mismatch.json()["detail"]

    def test_custom_comparison_accepts_any_ordered_pair_and_rejects_reversed_comparison_range(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        self._point_book_at(session_factory, sample_book, fake_book_for_reports)

        custom = client.get(
            f"/books/{sample_book}/reports/comparison?"
            "date_from=2026-05-10&date_to=2026-05-15"
            "&comparison_mode=custom"
            "&comparison_date_from=2026-05-01&comparison_date_to=2026-05-02",
            headers=auth_headers,
        )
        reversed_comparison = client.get(
            f"/books/{sample_book}/reports/comparison?"
            "date_from=2026-05-10&date_to=2026-05-15"
            "&comparison_mode=custom"
            "&comparison_date_from=2026-05-03&comparison_date_to=2026-05-02",
            headers=auth_headers,
        )

        assert custom.status_code == 200
        assert custom.json()["comparison_mode"] == "custom"
        assert custom.json()["comparison"]["date_from"] == "2026-05-01"
        assert custom.json()["comparison"]["date_to"] == "2026-05-02"
        assert reversed_comparison.status_code == 422
        assert reversed_comparison.json()["detail"] == "comparison_date_from must be on or before comparison_date_to"

    def test_account_union_preserves_zero_negative_one_sided_rows_and_tie_order(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        checking = FakeAccount(guid="checking", name="Checking", type="BANK", commodity=sek, parent=root)
        expense_accounts = {
            "comparison-only": FakeAccount(guid="comparison-only", name="Comparison Only", type="EXPENSE", commodity=sek, parent=root),
            "alpha": FakeAccount(guid="alpha", name="Alpha", type="EXPENSE", commodity=sek, parent=root),
            "tie-a": FakeAccount(guid="tie-a", name="alpha tie", type="EXPENSE", commodity=sek, parent=root),
            "tie-b": FakeAccount(guid="tie-b", name="Beta tie", type="EXPENSE", commodity=sek, parent=root),
            "primary-only": FakeAccount(guid="primary-only", name="Primary Only", type="EXPENSE", commodity=sek, parent=root),
            "refund": FakeAccount(guid="refund", name="Refunds", type="EXPENSE", commodity=sek, parent=root),
            "zero": FakeAccount(guid="zero", name="Zero", type="EXPENSE", commodity=sek, parent=root),
        }

        def expense_tx(guid: str, posted: date, account_key: str, amount: str) -> FakeTransaction:
            value = Decimal(amount)
            account = expense_accounts[account_key]
            return FakeTransaction(
                guid=guid,
                post_date=posted,
                description=guid,
                splits=[FakeSplit(account=checking, value=-value), FakeSplit(account=account, value=value)],
            )

        accounts = [root, checking, *expense_accounts.values()]
        transactions = [
            expense_tx("primary-alpha", date(2026, 6, 1), "alpha", "100.00"),
            expense_tx("comparison-alpha", date(2026, 5, 1), "alpha", "40.00"),
            expense_tx("primary-tie-a", date(2026, 6, 1), "tie-a", "30.00"),
            expense_tx("primary-tie-b", date(2026, 6, 1), "tie-b", "30.00"),
            expense_tx("primary-only", date(2026, 6, 1), "primary-only", "25.00"),
            expense_tx("comparison-only", date(2026, 5, 1), "comparison-only", "70.00"),
            expense_tx("primary-refund", date(2026, 6, 1), "refund", "-15.00"),
            expense_tx("comparison-refund", date(2026, 5, 1), "refund", "5.00"),
            expense_tx("primary-zero", date(2026, 6, 1), "zero", "10.00"),
            expense_tx("comparison-zero", date(2026, 5, 1), "zero", "10.00"),
        ]

        def fake_open_book(path, readonly=False):
            return FakeBookForReports(accounts=accounts, transactions=transactions)

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        self._point_book_at(session_factory, sample_book, fake_book_for_reports)

        response = client.get(
            f"/books/{sample_book}/reports/comparison?"
            "date_from=2026-06-01&date_to=2026-06-10"
            "&comparison_mode=custom"
            "&comparison_date_from=2026-05-01&comparison_date_to=2026-05-10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        rows = response.json()["expense_changes"]
        assert [row["account_id"] for row in rows] == [
            "comparison-only",
            "alpha",
            "tie-a",
            "tie-b",
            "primary-only",
            "refund",
            "zero",
        ]
        by_id = {row["account_id"]: row for row in rows}
        assert by_id["comparison-only"]["primary_total"] == "0.00"
        assert by_id["comparison-only"]["comparison_total"] == "70.00"
        assert by_id["comparison-only"]["delta"] == "-70.00"
        assert by_id["primary-only"]["comparison_total"] == "0.00"
        assert by_id["primary-only"]["delta"] == "25.00"
        assert by_id["refund"]["primary_total"] == "-15.00"
        assert by_id["refund"]["delta"] == "-20.00"
        assert by_id["zero"]["delta"] == "0.00"
        assert by_id["zero"]["absolute_delta"] == "0.00"

    def test_account_identity_conflicts_suppress_only_affected_row_delta(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        sek = FakeCommodity(mnemonic="SEK")
        root = FakeAccount(guid="root", name="Root Account", type="ROOT", commodity=sek)
        checking = FakeAccount(guid="checking", name="Checking", type="BANK", commodity=sek, parent=root)
        primary_name = FakeAccount(guid="shared-expense", name="Dining", type="EXPENSE", commodity=sek, parent=root)
        comparison_name = FakeAccount(guid="shared-expense", name="Food", type="EXPENSE", commodity=sek, parent=root)
        accounts = [root, checking, primary_name, comparison_name]
        transactions = [
            FakeTransaction(
                guid="primary-shared",
                post_date=date(2026, 6, 1),
                description="primary shared",
                splits=[FakeSplit(account=checking, value=Decimal("-100.00")), FakeSplit(account=primary_name, value=Decimal("100.00"))],
            ),
            FakeTransaction(
                guid="comparison-shared",
                post_date=date(2026, 5, 1),
                description="comparison shared",
                splits=[FakeSplit(account=checking, value=Decimal("-80.00")), FakeSplit(account=comparison_name, value=Decimal("80.00"))],
            ),
        ]

        def fake_open_book(path, readonly=False):
            return FakeBookForReports(accounts=accounts, transactions=transactions)

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        self._point_book_at(session_factory, sample_book, fake_book_for_reports)

        response = client.get(
            f"/books/{sample_book}/reports/comparison?"
            "date_from=2026-06-01&date_to=2026-06-01"
            "&comparison_mode=custom"
            "&comparison_date_from=2026-05-01&comparison_date_to=2026-05-01",
            headers=auth_headers,
        )

        assert response.status_code == 200
        [row] = response.json()["expense_changes"]
        assert row["account_id"] == "shared-expense"
        assert row["primary_total"] == "100.00"
        assert row["comparison_total"] == "80.00"
        assert row["status"] == "not_comparable"
        assert row["delta"] is None
        assert row["absolute_delta"] is None
        assert "changed between periods" in row["detail"]

    def test_missing_base_currency_can_still_auto_detect_comparable_currency(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory
    ):
        self._point_book_at(session_factory, sample_book, fake_book_for_reports, base_currency=None)

        response = client.get(
            f"/books/{sample_book}/reports/comparison?{self.previous_equivalent_query}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["comparable"] is True
        assert {status["section"]: status["status"] for status in data["delta_section_statuses"]} == {
            "summary": "ok",
            "cashflow": "ok",
            "expenses_by_account": "ok",
        }
        assert data["summary_delta"] is not None
        assert data["cashflow_delta"] is not None
        assert data["expense_changes"]
        assert "unknown (XXX)" not in " ".join(data["limitations"])

    def test_partial_section_errors_are_redacted_and_do_not_zero_failed_side(
        self, client, auth_headers, sample_book, fake_book_for_reports, session_factory, monkeypatch
    ):
        self._point_book_at(session_factory, sample_book, fake_book_for_reports)

        def fail_expenses(self, date_from=None, date_to=None):
            raise GnuCashReadError("cannot read /private/books/leaked.gnucash.sqlite")

        monkeypatch.setattr(GnuCashBookService, "get_expenses_by_account", fail_expenses)

        response = client.get(
            f"/books/{sample_book}/reports/comparison?{self.previous_equivalent_query}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        statuses = {status["section"]: status for status in data["delta_section_statuses"]}
        assert statuses["summary"]["status"] == "ok"
        assert statuses["cashflow"]["status"] == "ok"
        assert statuses["expenses_by_account"]["status"] == "error"
        assert statuses["expenses_by_account"]["detail"] == "Report section could not be read safely from this runtime."
        assert data["expense_changes"] == []
        assert "/private" not in response.text
        assert "leaked.gnucash" not in response.text

    def test_comparison_service_opens_books_readonly_without_mutation_helpers(
        self, fake_report_data, tmp_path, monkeypatch
    ):
        book_path = tmp_path / "readonly-comparison-report.gnucash"
        book_path.write_text("fake")
        accounts, transactions = fake_report_data
        readonly_flags: list[bool] = []
        opened_books: list["MutationGuardBook"] = []

        class MutationGuardBook(FakeBookForReports):
            def __init__(self, accounts=None, transactions=None):
                self.closed = False
                self._accounts = accounts or []
                self._transactions = transactions or []
                self.accounts_reads = 0
                self.transactions_reads = 0

            @property
            def accounts(self):
                self.accounts_reads += 1
                return self._accounts

            @property
            def transactions(self):
                self.transactions_reads += 1
                return self._transactions

            def save(self):  # pragma: no cover - failure path only
                raise AssertionError("comparison reports must not save GnuCash books")

            def flush(self):  # pragma: no cover - failure path only
                raise AssertionError("comparison reports must not flush GnuCash books")

        def fake_open_book(path, readonly=False):
            readonly_flags.append(readonly)
            book = MutationGuardBook(accounts=accounts, transactions=transactions)
            opened_books.append(book)
            return book

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)

        service = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"})
        report = service.get_period_report_comparison(
            date(2026, 5, 10),
            date(2026, 5, 15),
            date(2026, 5, 4),
            date(2026, 5, 9),
            comparison_mode="previous_equivalent",
            book_id=123,
        )

        assert report.book_id == 123
        assert report.partial_failure is False
        assert readonly_flags
        assert all(readonly_flags)
        assert len(readonly_flags) == 1
        assert opened_books[0].accounts_reads <= 2
        assert opened_books[0].transactions_reads <= 2
