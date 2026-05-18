"""Tests for transaction browsing API endpoints."""

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
# Fake GnuCash fixtures for transactions
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


class FakeBookWithTransactions:
    def __init__(self, accounts=None, transactions=None):
        self.accounts = accounts or []
        self.transactions = transactions or []
        self.closed = False

    def close(self):
        self.closed = True


@pytest.fixture
def fake_transaction_data():
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

    split1_checking = FakeSplit(account=checking, value=Decimal("-320"), reconcile_state="c")
    split1_food = FakeSplit(account=food, value=Decimal("320"), memo="groceries", reconcile_state="c")
    tx1 = FakeTransaction(
        guid="tx-1",
        post_date=date(2026, 5, 16),
        description="ICA",
        splits=[split1_checking, split1_food],
    )

    split2_checking = FakeSplit(account=checking, value=Decimal("-50"))
    split2_tax = FakeSplit(account=tax, value=Decimal("10"))
    split2_food = FakeSplit(account=food, value=Decimal("40"))
    tx2 = FakeTransaction(
        guid="tx-2",
        post_date=date(2026, 5, 17),
        description="Split transaction test",
        splits=[split2_checking, split2_tax, split2_food],
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
def fake_book_with_transactions(tmp_path, monkeypatch, fake_transaction_data):
    book_path = tmp_path / "test.gnucash"
    book_path.write_text("fake")
    accounts, transactions = fake_transaction_data

    def fake_open_book(path, readonly=False):
        return FakeBookWithTransactions(accounts=accounts, transactions=transactions)

    def fake_open_book_uri(*, uri_conn, readonly=False):
        return FakeBookWithTransactions(accounts=accounts, transactions=transactions)

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path


# ---------------------------------------------------------------------------
# Tests: GET /transactions (MVP alias)
# ---------------------------------------------------------------------------


class TestListTransactionsMVP:
    def test_requires_auth(self, client):
        response = client.get("/transactions")
        assert response.status_code == 401

    def test_returns_paginated_transactions(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "limit" in data
        assert "offset" in data
        assert "total" in data
        assert data["total"] == 3
        assert data["limit"] == 50
        assert data["offset"] == 0
        assert len(data["items"]) == 3

    def test_pagination(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?limit=2&offset=0", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2

        response2 = client.get("/transactions?limit=2&offset=2", headers=auth_headers)
        data2 = response2.json()
        assert data2["total"] == 3
        assert len(data2["items"]) == 1

    def test_filter_by_query(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?query=ica", headers=auth_headers)
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["description"] == "ICA"

    def test_filter_by_query_matches_split_memo_and_counts_consistently(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?query=GROCERIES", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == ["tx-1"]

    def test_filter_by_date_range(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?date_from=2026-05-17&date_to=2026-05-17",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == "tx-2"

    def test_rejects_inverted_date_range(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?date_from=2026-05-18&date_to=2026-05-16",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "date_from cannot be later than date_to"

    def test_filter_by_account_id(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?account_id=checking-guid",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 3

    def test_filter_by_amount_range(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?account_id=checking-guid&min_amount=100&max_amount=400",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == "tx-1"
        assert data["items"][0]["amount"] == "-320.00"

    def test_rejects_inverted_amount_range(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/transactions?min_amount=400&max_amount=100",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "min_amount cannot be greater than max_amount"

    def test_filter_by_transaction_state_matches_split_reconciliation_state(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?transaction_state=cleared", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == ["tx-1"]

    def test_filter_by_transaction_state_respects_account_scope(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/accounts/checking-guid/transactions?transaction_state=reconciled",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == ["tx-3"]

    def test_rejects_unknown_transaction_state(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions?transaction_state=maybe", headers=auth_headers)

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "transaction_state must be one of: cleared, reconciled, unreconciled, voided"
        )

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions", headers=viewer_headers)
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /transactions/{transaction_id} (MVP alias)
# ---------------------------------------------------------------------------


class TestGetTransactionMVP:
    def test_requires_auth(self, client):
        response = client.get("/transactions/some-id")
        assert response.status_code == 401

    def test_returns_transaction_detail(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions/tx-1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "tx-1"
        assert data["date"] == "2026-05-16"
        assert data["description"] == "ICA"
        assert data["currency"] == "SEK"
        assert len(data["splits"]) == 2
        assert data["splits"][0]["account_name"] == "Assets:Bank:Checking"
        assert data["splits"][0]["amount"] == "-320.00"
        assert data["splits"][1]["memo"] == "groceries"

    def test_unknown_transaction_returns_404(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_split_transaction_shows_all_splits(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions/tx-2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["splits"]) == 3

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get("/transactions/tx-1", headers=viewer_headers)
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /accounts/{account_id}/transactions (MVP alias)
# ---------------------------------------------------------------------------


class TestListAccountTransactionsMVP:
    def test_requires_auth(self, client):
        response = client.get("/accounts/some-id/transactions")
        assert response.status_code == 401

    def test_returns_account_transactions(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/accounts/checking-guid/transactions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for item in data["items"]:
            assert item["account_id"] == "checking-guid"

    def test_unknown_account_returns_empty(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            "/accounts/nonexistent-guid/transactions",
            headers=auth_headers,
        )
        # Unknown account_id used as filter returns empty list, not 404
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/transactions
# ---------------------------------------------------------------------------


class TestListBookTransactions:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/transactions")
        assert response.status_code == 401

    def test_returns_paginated_transactions(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions",
            headers=viewer_headers,
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/transactions/{transaction_id}
# ---------------------------------------------------------------------------


class TestGetBookTransaction:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/transactions/some-id")
        assert response.status_code == 401

    def test_returns_transaction_detail(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/tx-1",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "tx-1"
        assert len(data["splits"]) == 2

    def test_unknown_transaction_returns_404(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/transactions/nonexistent",
            headers=auth_headers,
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/accounts/{account_id}/transactions
# ---------------------------------------------------------------------------


class TestListBookAccountTransactions:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/accounts/some-id/transactions")
        assert response.status_code == 401

    def test_returns_account_transactions(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/checking-guid/transactions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3

    def test_filters_stay_account_scoped_and_counts_match_items(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/food-guid/transactions?"
            "query=salary&date_from=2026-05-18&date_to=2026-05-18&"
            "transaction_state=reconciled&min_amount=1000&max_amount=6000",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == ["tx-3"]
        assert all(item["account_id"] == "food-guid" for item in data["items"])

    def test_account_scope_filter_does_not_leak_other_account_matches(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/tax-guid/transactions?query=salary",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_unknown_account_returns_empty(
        self, client, auth_headers, sample_book, fake_book_with_transactions, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_with_transactions)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/nonexistent-guid/transactions",
            headers=auth_headers,
        )
        # Unknown account_id used as filter returns empty list, not 404
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
