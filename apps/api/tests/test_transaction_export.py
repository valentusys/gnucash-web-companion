"""Tests for CSV export endpoint GET /books/{book_id}/transactions/export."""

from __future__ import annotations

import csv
import io
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
# Fake GnuCash fixtures for export
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
    reconcile_state: str = "n"


@dataclass
class FakeTransaction:
    guid: str
    post_date: date
    description: str
    splits: list[FakeSplit]


class FakeBookForExport:
    def __init__(self, accounts=None, transactions=None):
        self.accounts = accounts or []
        self.transactions = transactions or []
        self.closed = False

    def close(self):
        self.closed = True


@pytest.fixture
def fake_export_data():
    root = FakeAccount(guid="root-guid", name="Assets", type="ROOT")
    bank = FakeAccount(guid="bank-guid", name="Bank", type="ASSET", parent=root)
    checking = FakeAccount(
        guid="checking-guid",
        name="Checking",
        type="BANK",
        parent=bank,
        balance=Decimal("12345.67"),
    )
    food = FakeAccount(guid="food-guid", name="Food", type="EXPENSE")
    tax = FakeAccount(guid="tax-guid", name="Tax", type="EXPENSE")

    tx1 = FakeTransaction(
        guid="tx-1",
        post_date=date(2026, 5, 16),
        description="ICA",
        splits=[
            FakeSplit(account=checking, value=Decimal("-320"), reconcile_state="c"),
            FakeSplit(account=food, value=Decimal("320"), memo="groceries", reconcile_state="c"),
        ],
    )

    tx2 = FakeTransaction(
        guid="tx-2",
        post_date=date(2026, 5, 17),
        description="Split transaction test",
        splits=[
            FakeSplit(account=checking, value=Decimal("-50")),
            FakeSplit(account=tax, value=Decimal("10")),
            FakeSplit(account=food, value=Decimal("40")),
        ],
    )

    tx3 = FakeTransaction(
        guid="tx-3",
        post_date=date(2026, 5, 18),
        description="Salary",
        splits=[
            FakeSplit(account=checking, value=Decimal("5000"), reconcile_state="y"),
            FakeSplit(account=food, value=Decimal("-5000"), reconcile_state="y"),
        ],
    )

    accounts = [root, bank, checking, food, tax]
    transactions = [tx1, tx2, tx3]
    return accounts, transactions


@pytest.fixture
def fake_book_for_export(tmp_path, monkeypatch, fake_export_data):
    book_path = tmp_path / "test.gnucash"
    book_path.write_text("fake")
    accounts, transactions = fake_export_data

    def fake_open_book(path, readonly=False):
        return FakeBookForExport(accounts=accounts, transactions=transactions)

    def fake_open_book_uri(*, uri_conn, readonly=False):
        return FakeBookForExport(accounts=accounts, transactions=transactions)

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path


def _parse_csv_response(response):
    """Helper to parse CSV content from a StreamingResponse."""
    content = response.text
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    return rows


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestExportTransactionsCSV:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/transactions/export")
        assert response.status_code == 401

    def test_returns_csv_with_correct_headers(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert "Content-Disposition" in response.headers
        assert f"book{sample_book}" in response.headers["Content-Disposition"]

        rows = _parse_csv_response(response)
        assert len(rows) == 4  # header + 3 transactions
        assert rows[0] == [
            "id",
            "date",
            "description",
            "amount",
            "currency",
            "account_id",
            "account_name",
            "counter_account_name",
        ]

    def test_csv_contains_all_transactions(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export",
            headers=auth_headers,
        )
        rows = _parse_csv_response(response)
        # header + 3 data rows
        assert len(rows) == 4
        data_rows = rows[1:]
        ids = [row[0] for row in data_rows]
        assert "tx-1" in ids
        assert "tx-2" in ids
        assert "tx-3" in ids

    def test_export_respects_date_filter(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export?date_from=2026-05-17&date_to=2026-05-17",
            headers=auth_headers,
        )
        assert response.status_code == 200
        rows = _parse_csv_response(response)
        # header + 1 transaction on 2026-05-17
        assert len(rows) == 2
        assert rows[1][0] == "tx-2"

    def test_export_rejects_inverted_date_range(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export?date_from=2026-05-18&date_to=2026-05-16",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "date_from cannot be later than date_to"

    def test_export_respects_account_filter(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export?account_id=food-guid",
            headers=auth_headers,
        )
        assert response.status_code == 200
        rows = _parse_csv_response(response)
        # All 3 transactions have a split for food-guid
        assert len(rows) == 4

    def test_export_respects_query_filter(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export?query=ica",
            headers=auth_headers,
        )
        assert response.status_code == 200
        rows = _parse_csv_response(response)
        # header + 1 match
        assert len(rows) == 2
        assert rows[1][2] == "ICA"

    def test_export_query_filter_matches_split_memo(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export?query=GROCERIES",
            headers=auth_headers,
        )

        assert response.status_code == 200
        rows = _parse_csv_response(response)
        assert len(rows) == 2
        assert rows[1][0] == "tx-1"
        assert rows[1][2] == "ICA"
        assert response.headers["X-CSV-Export-Total"] == "1"

    def test_export_respects_amount_range_filter(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export?account_id=checking-guid&min_amount=100&max_amount=400",
            headers=auth_headers,
        )
        assert response.status_code == 200
        rows = _parse_csv_response(response)
        assert len(rows) == 2
        assert rows[1][0] == "tx-1"
        assert rows[1][3] == "-320.00"

    def test_export_respects_combined_list_filters(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export"
            "?query=split&date_from=2026-05-17&date_to=2026-05-18"
            "&account_id=checking-guid&min_amount=40&max_amount=60",
            headers=auth_headers,
        )
        assert response.status_code == 200
        rows = _parse_csv_response(response)
        assert len(rows) == 2
        assert rows[1][0] == "tx-2"
        assert rows[1][2] == "Split transaction test"
        assert rows[1][3] == "-50.00"

    def test_export_rejects_inverted_amount_range(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export?min_amount=500&max_amount=100",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "min_amount cannot be greater than max_amount"

    def test_export_respects_transaction_state_filter(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export?transaction_state=reconciled",
            headers=auth_headers,
        )

        assert response.status_code == 200
        rows = _parse_csv_response(response)
        assert len(rows) == 2
        assert rows[1][0] == "tx-3"
        assert response.headers["X-CSV-Export-Total"] == "1"

    def test_export_rejects_unknown_transaction_state(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export?transaction_state=posted",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "transaction_state must be one of: cleared, reconciled, unreconciled, voided"
        )

    def test_export_access_denied(
        self, client, viewer_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export",
            headers=viewer_headers,
        )
        assert response.status_code == 403

    def test_export_content_disposition_filename(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export",
            headers=auth_headers,
        )
        assert response.status_code == 200
        disposition = response.headers["Content-Disposition"]
        assert disposition.startswith("attachment;")
        assert f'transactions-book{sample_book}.csv' in disposition

    def test_export_reports_cap_and_truncation_headers(
        self,
        client,
        auth_headers,
        sample_book,
        fake_book_for_export,
        session_factory,
        monkeypatch,
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        import app.routers.transactions as transactions_router

        monkeypatch.setattr(transactions_router, "CSV_EXPORT_LIMIT", 2)

        response = client.get(
            f"/books/{sample_book}/transactions/export",
            headers=auth_headers,
        )

        assert response.status_code == 200
        rows = _parse_csv_response(response)
        assert len(rows) == 3  # header + capped 2 exported rows
        assert response.headers["X-CSV-Export-Limit"] == "2"
        assert response.headers["X-CSV-Export-Total"] == "3"
        assert response.headers["X-CSV-Export-Truncated"] == "true"
        assert response.headers["X-CSV-Export-Timeout-Policy"] == "synchronous-request-timeout"

    def test_export_reports_not_truncated_when_under_cap(
        self, client, auth_headers, sample_book, fake_book_for_export, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_for_export)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.headers["X-CSV-Export-Limit"] == "10000"
        assert response.headers["X-CSV-Export-Total"] == "3"
        assert response.headers["X-CSV-Export-Truncated"] == "false"
        assert response.headers["X-CSV-Export-Timeout-Policy"] == "synchronous-request-timeout"

    def test_export_above_service_page_clamp_returns_all_rows_and_consistent_headers(
        self,
        client,
        auth_headers,
        sample_book,
        tmp_path,
        session_factory,
        monkeypatch,
    ):
        root = FakeAccount(guid="root-guid", name="Assets", type="ROOT")
        checking = FakeAccount(guid="checking-guid", name="Checking", type="BANK", parent=root)
        food = FakeAccount(guid="food-guid", name="Food", type="EXPENSE", parent=root)
        transactions = [
            FakeTransaction(
                guid=f"tx-{index:03d}",
                post_date=date(2026, 5, (index % 28) + 1),
                description=f"Synthetic transaction {index:03d}",
                splits=[
                    FakeSplit(account=checking, value=Decimal("-1.00")),
                    FakeSplit(account=food, value=Decimal("1.00")),
                ],
            )
            for index in range(501)
        ]
        book_path = tmp_path / "large-export.gnucash"
        book_path.write_text("fake")

        def fake_open_book(path, readonly=False):
            return FakeBookForExport(accounts=[root, checking, food], transactions=transactions)

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)

        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/export",
            headers=auth_headers,
        )

        assert response.status_code == 200
        rows = _parse_csv_response(response)
        assert len(rows) == 502  # header + all 501 matching transactions
        assert response.headers["X-CSV-Export-Limit"] == "10000"
        assert response.headers["X-CSV-Export-Total"] == "501"
        assert response.headers["X-CSV-Export-Truncated"] == "false"
