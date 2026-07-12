"""Regression tests for independent multi-book read-only access boundaries."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import Book, User, UserBookAccess
from app.routers.auth import get_db
from app.schemas.accounts import AccountExplorerResponseDTO, AccountExplorerScanDTO
from app.schemas.gnucash import (
    AccountDTO,
    AccountTreeNodeDTO,
    CashflowDTO,
    ExpenseByAccountDTO,
    ReportSummaryDTO,
    ScheduledTransactionDTO,
    TransactionDetailDTO,
    TransactionListItemDTO,
)
from app.schemas.transaction_explorer import (
    TransactionExplorerPageDTO,
    TransactionExplorerScanMetadataDTO,
)
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
        session.add_all(
            [
                User(
                    username="admin",
                    display_name="Admin",
                    password_hash=hash_password("testpassword123"),
                    is_admin=True,
                ),
                User(
                    username="viewer",
                    display_name="Viewer",
                    password_hash=hash_password("viewerpass"),
                    is_admin=False,
                ),
            ]
        )
        session.commit()

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "testpassword123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def viewer_headers(client):
    response = client.post(
        "/auth/login",
        json={"username": "viewer", "password": "viewerpass"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_minimal_gnucash_sqlite(path):
    required_tables = ["versions", "books", "accounts", "transactions", "splits", "commodities"]
    with sqlite3.connect(path) as conn:
        for table in required_tables:
            conn.execute(f"create table {table} (guid text)")


@pytest.fixture
def multibook_registry(session_factory, tmp_path):
    present_one = tmp_path / "book-one.gnucash.sqlite"
    present_two = tmp_path / "book-two.gnucash.sqlite"
    _create_minimal_gnucash_sqlite(present_one)
    _create_minimal_gnucash_sqlite(present_two)

    with session_factory() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        viewer = session.query(User).filter(User.username == "viewer").one()
        books = {
            "default": Book(
                name="Synthetic Default",
                storage_type="sqlite",
                uri_or_path=str(present_one),
                base_currency="SEK",
                is_default=True,
            ),
            "second": Book(
                name="Synthetic Second",
                storage_type="sqlite",
                uri_or_path=str(present_two),
                base_currency="USD",
                is_default=False,
            ),
            "unauthorized": Book(
                name="Unauthorized Synthetic",
                storage_type="sqlite",
                uri_or_path=str(tmp_path / "unauthorized.gnucash.sqlite"),
                base_currency="EUR",
                is_default=False,
            ),
            "archived": Book(
                name="Archived Synthetic",
                storage_type="sqlite",
                uri_or_path=str(tmp_path / "archived.gnucash.sqlite"),
                base_currency="SEK",
                is_default=False,
                is_archived=True,
            ),
            "missing": Book(
                name="Missing Synthetic",
                storage_type="sqlite",
                uri_or_path=str(tmp_path / "missing.gnucash.sqlite"),
                base_currency="SEK",
                is_default=False,
            ),
            "not_configured": Book(
                name="Not Configured Synthetic",
                storage_type="sqlite",
                uri_or_path="",
                base_currency="SEK",
                is_default=False,
            ),
        }
        session.add_all(books.values())
        session.flush()
        session.add_all(
            [
                UserBookAccess(user_id=admin.id, book_id=books["default"].id, role="owner"),
                UserBookAccess(user_id=admin.id, book_id=books["second"].id, role="viewer"),
                UserBookAccess(user_id=admin.id, book_id=books["archived"].id, role="owner"),
                UserBookAccess(user_id=admin.id, book_id=books["missing"].id, role="owner"),
                UserBookAccess(user_id=admin.id, book_id=books["not_configured"].id, role="owner"),
                UserBookAccess(user_id=viewer.id, book_id=books["second"].id, role="viewer"),
            ]
        )
        session.commit()
        return {name: book.id for name, book in books.items()}


@dataclass
class ReadOnlyServiceProbe:
    book_id: int
    calls: list[int]

    def __post_init__(self):
        self.calls.append(self.book_id)

    def list_accounts(self):
        return [
            AccountDTO(
                id=f"acct-{self.book_id}",
                name=f"Account {self.book_id}",
                full_name=f"Assets:Account {self.book_id}",
                type="BANK",
                currency="SEK",
                balance="0.00",
            )
        ]

    def get_account_tree(self):
        return [
            AccountTreeNodeDTO(
                id=f"acct-{self.book_id}",
                name=f"Account {self.book_id}",
                full_name=f"Assets:Account {self.book_id}",
                type="BANK",
                currency="SEK",
                balance="0.00",
                children=[],
            )
        ]

    def explore_accounts(self, request, *, book_id: int | None = None):
        return AccountExplorerResponseDTO(
            book_id=book_id or self.book_id,
            mode=request.mode,
            normalized_filters=request.normalized_filters,
            root_ids=[],
            nodes=[],
            returned_count=0,
            scan=AccountExplorerScanDTO(query_count=0, exhausted=True, limits={}),
            limitations=[],
        )

    def get_account(self, account_id: str):
        return AccountDTO(
            id=account_id,
            name="Account detail",
            full_name="Assets:Account detail",
            type="BANK",
            currency="SEK",
            balance="0.00",
        )

    def count_transactions(self, **kwargs):
        return 1

    def list_transactions(self, **kwargs):
        return [
            TransactionListItemDTO(
                id=f"tx-{self.book_id}",
                date="2026-01-01",
                description=f"Synthetic tx {self.book_id}",
                amount="0.00",
                currency="SEK",
                account_id="acct",
                account_name="Assets:Account",
                counter_account_name="Equity:Opening Balances",
            )
        ]

    def explore_transactions(self, request):
        return TransactionExplorerPageDTO(
            items=[],
            normalized_filters=request.normalized_filters,
            sort=request.sort,
            page_size=request.page_size,
            returned_count=0,
            has_more=False,
            has_previous=False,
            scan=TransactionExplorerScanMetadataDTO(
                candidate_rows=0,
                split_rows=0,
                query_count=0,
                scan_limited=False,
                exhausted=True,
                limits={},
            ),
            limitations=[],
        )

    def get_transaction(self, transaction_id: str):
        return TransactionDetailDTO(
            id=transaction_id,
            date="2026-01-01",
            description="Synthetic detail",
            currency="SEK",
            splits=[],
        )

    def list_scheduled_transactions(self):
        return [ScheduledTransactionDTO(id=f"sched-{self.book_id}", name="Synthetic schedule")]

    def get_report_summary(self, as_of_date=None):
        return ReportSummaryDTO(
            currency="SEK",
            net_worth="0.00",
            assets="0.00",
            liabilities="0.00",
            income_this_month="0.00",
            expenses_this_month="0.00",
            as_of_date="2026-01-01",
        )

    def get_cashflow(self, date_from: str, date_to: str):
        return CashflowDTO(date_from=date_from, date_to=date_to, currency="SEK", inflow="0.00", outflow="0.00", net="0.00")

    def get_cashflow_by_month(self, date_from: str, date_to: str):
        return []

    def get_expenses_by_account(self, date_from: str, date_to: str):
        return [ExpenseByAccountDTO(account_id="acct", account_name="Expenses:Synthetic", total="0.00", currency="SEK")]

    def get_period_report_comparison(
        self,
        date_from: str,
        date_to: str,
        comparison_date_from: str,
        comparison_date_to: str,
        *,
        comparison_mode: str,
        book_id: int | None = None,
    ):
        period = {
            "book_id": book_id or self.book_id,
            "date_from": str(date_from),
            "date_to": str(date_to),
            "currency": "SEK",
            "reporting_basis": "base_currency_only",
            "includes_currency_conversion": False,
            "limitations": [],
            "partial_failure": False,
            "empty": True,
            "section_statuses": [
                {"section": "summary", "status": "empty", "detail": None},
                {"section": "cashflow", "status": "empty", "detail": None},
                {"section": "monthly_cashflow", "status": "empty", "detail": None},
                {"section": "expenses_by_account", "status": "empty", "detail": None},
            ],
            "summary": None,
            "cashflow": None,
            "monthly_cashflow": [],
            "expenses_by_account": [],
        }
        comparison = {**period, "date_from": str(comparison_date_from), "date_to": str(comparison_date_to)}
        return {
            "book_id": book_id or self.book_id,
            "comparison_mode": comparison_mode,
            "reporting_basis": "base_currency_only",
            "includes_currency_conversion": False,
            "primary": period,
            "comparison": comparison,
            "limitations": [],
            "comparable": True,
            "partial_failure": False,
            "empty": True,
            "delta_section_statuses": [
                {"section": "summary", "status": "empty", "detail": None},
                {"section": "cashflow", "status": "empty", "detail": None},
                {"section": "expenses_by_account", "status": "empty", "detail": None},
            ],
            "summary_delta": None,
            "cashflow_delta": None,
            "expense_changes": [],
        }


@pytest.fixture
def read_service_probe(monkeypatch):
    calls: list[int] = []

    def factory(book):
        return ReadOnlyServiceProbe(book.id, calls)

    monkeypatch.setattr("app.routers.books.account_service_for", factory)
    monkeypatch.setattr("app.routers.books.transaction_service_for", factory)
    monkeypatch.setattr("app.routers.books.scheduled_transaction_service_for", factory)
    monkeypatch.setattr("app.routers.transactions.transaction_service_for", factory)
    monkeypatch.setattr("app.routers.reports.transaction_service_for", factory)
    return calls


COMPARISON_REPORT_ROUTE = (
    "/books/{book_id}/reports/comparison?date_from=2026-07-02&date_to=2026-12-30"
    "&comparison_mode=previous_equivalent"
    "&comparison_date_from=2026-01-01&comparison_date_to=2026-07-01"
)


class TestMultiBookMetadataBoundaries:
    def test_books_listing_hides_archived_and_unauthorized_and_redacts_storage(
        self, client, auth_headers, multibook_registry
    ):
        response = client.get("/books", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        ids = {item["id"] for item in data}
        assert multibook_registry["default"] in ids
        assert multibook_registry["second"] in ids
        assert multibook_registry["missing"] in ids
        assert multibook_registry["not_configured"] in ids
        assert multibook_registry["archived"] not in ids
        assert multibook_registry["unauthorized"] not in ids
        for item in data:
            assert "uri_or_path" not in item
            assert item["access_status"] == "accessible"
            assert item["status_severity"] in {"ok", "warning", "action_required"}
            assert item["access_role_label"] in {"Owner", "Viewer"}
            assert "independent book" in item["access_role_description"] or "write-alpha" in item["access_role_description"]
            assert item["storage_diagnostics"]["safe_summary"]
            assert item["operator_guidance"]["private_path_redacted"] is True
            assert item["management_actions"] == ["set_default", "remove_from_registry"]
            assert str(item["id"]) not in item["storage_diagnostics"]["safe_summary"]
        statuses = {item["id"]: item["status"] for item in data}
        openable = {item["id"]: item["can_open_read_only_views"] for item in data}
        assert statuses[multibook_registry["default"]] == "available"
        assert statuses[multibook_registry["second"]] == "available"
        assert statuses[multibook_registry["missing"]] == "missing_file"
        assert statuses[multibook_registry["not_configured"]] == "not_configured"
        assert openable[multibook_registry["default"]] is True
        assert openable[multibook_registry["second"]] is True
        assert openable[multibook_registry["missing"]] is False
        assert openable[multibook_registry["not_configured"]] is False

    def test_get_book_blocks_archived_and_unauthorized(self, client, auth_headers, multibook_registry):
        archived = client.get(f"/books/{multibook_registry['archived']}", headers=auth_headers)
        unauthorized = client.get(f"/books/{multibook_registry['unauthorized']}", headers=auth_headers)
        assert archived.status_code == 404
        assert unauthorized.status_code == 403


class TestMultiBookReadOnlyRouteFamilies:
    @pytest.mark.parametrize(
        "path_template",
        [
            "/books/{book_id}/accounts",
            "/books/{book_id}/accounts/tree",
            "/books/{book_id}/accounts/explorer",
            "/books/{book_id}/accounts/acct-1",
            "/books/{book_id}/scheduled-transactions",
            "/books/{book_id}/transactions",
            "/books/{book_id}/transactions/explorer?date_from=2026-01-01&date_to=2026-01-31",
            "/books/{book_id}/transactions/export",
            "/books/{book_id}/transactions/tx-1",
            "/books/{book_id}/accounts/acct-1/transactions",
            "/books/{book_id}/reports/summary",
            "/books/{book_id}/reports/cashflow",
            "/books/{book_id}/reports/expenses-by-account",
            "/books/{book_id}/reports/recent-transactions",
            COMPARISON_REPORT_ROUTE,
        ],
    )
    def test_accessible_independent_books_route_to_the_selected_book_only(
        self, client, auth_headers, multibook_registry, read_service_probe, path_template
    ):
        response = client.get(path_template.format(book_id=multibook_registry["second"]), headers=auth_headers)
        assert response.status_code == 200
        assert read_service_probe == [multibook_registry["second"]]

    @pytest.mark.parametrize(
        "path_template",
        [
            "/books/{book_id}/accounts",
            "/books/{book_id}/accounts/tree",
            "/books/{book_id}/accounts/explorer",
            "/books/{book_id}/accounts/acct-1",
            "/books/{book_id}/scheduled-transactions",
            "/books/{book_id}/transactions",
            "/books/{book_id}/transactions/explorer?date_from=2026-01-01&date_to=2026-01-31",
            "/books/{book_id}/transactions/export",
            "/books/{book_id}/transactions/tx-1",
            "/books/{book_id}/accounts/acct-1/transactions",
            "/books/{book_id}/reports/summary",
            "/books/{book_id}/reports/cashflow",
            "/books/{book_id}/reports/expenses-by-account",
            "/books/{book_id}/reports/recent-transactions",
            COMPARISON_REPORT_ROUTE,
            "/books/{book_id}/write-alpha-audit-summary",
        ],
    )
    @pytest.mark.parametrize(
        ("book_key", "expected_status"),
        [("unauthorized", 403), ("archived", 404)],
    )
    def test_route_families_block_unauthorized_and_archived_before_opening_books(
        self, client, auth_headers, multibook_registry, read_service_probe, path_template, book_key, expected_status
    ):
        response = client.get(path_template.format(book_id=multibook_registry[book_key]), headers=auth_headers)
        assert response.status_code == expected_status
        assert read_service_probe == []

    @pytest.mark.parametrize(
        "path_template",
        [
            "/books/{book_id}/accounts",
            "/books/{book_id}/accounts/tree",
            "/books/{book_id}/accounts/explorer",
            "/books/{book_id}/accounts/acct-1",
            "/books/{book_id}/scheduled-transactions",
            "/books/{book_id}/transactions",
            "/books/{book_id}/transactions/explorer?date_from=2026-01-01&date_to=2026-01-31",
            "/books/{book_id}/transactions/export",
            "/books/{book_id}/transactions/tx-1",
            "/books/{book_id}/accounts/acct-1/transactions",
            "/books/{book_id}/reports/summary",
            "/books/{book_id}/reports/cashflow",
            "/books/{book_id}/reports/expenses-by-account",
            "/books/{book_id}/reports/recent-transactions",
            COMPARISON_REPORT_ROUTE,
            "/books/{book_id}/write-alpha-audit-summary",
        ],
    )
    @pytest.mark.parametrize(
        ("book_key", "expected_detail"),
        [
            ("missing", "Configured GnuCash book storage is unavailable from this runtime."),
            ("not_configured", "GnuCash book storage is not configured for this entry."),
        ],
    )
    def test_missing_and_not_configured_books_return_safe_503_before_opening_books(
        self, client, auth_headers, multibook_registry, read_service_probe, path_template, book_key, expected_detail
    ):
        response = client.get(path_template.format(book_id=multibook_registry[book_key]), headers=auth_headers)
        assert response.status_code == 503
        assert response.json() == {"detail": expected_detail}
        assert read_service_probe == []
        unsafe_fragments = [
            "/tmp/",
            "gnucash.sqlite",
            "uri_or_path",
            "backup",
            "Assets:Account",
            "Synthetic tx",
            "memo",
            "0.00",
            "private path",
        ]
        for fragment in unsafe_fragments:
            assert fragment not in response.text
