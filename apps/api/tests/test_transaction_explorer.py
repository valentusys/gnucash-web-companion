"""Tests for GET /books/{book_id}/transactions/explorer."""

from __future__ import annotations

import base64
import inspect
import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
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
from app.models import AuditLog, Book, User, UserBookAccess, WriteAlphaTransactionOwnership
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.transaction_explorer import (
    CURSOR_TTL,
    build_transaction_explorer_query,
    encode_explorer_cursor,
)

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password="testpassword123",
)

CHECKING = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
FOOD = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
SALARY = "cccccccccccccccccccccccccccccccc"
TRANSPORT = "dddddddddddddddddddddddddddddddd"
EUR_ACCOUNT = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
TX1 = "00000000000000000000000000000001"
TX2 = "00000000000000000000000000000002"
TX3 = "00000000000000000000000000000003"
TX4 = "00000000000000000000000000000004"
TX5 = "00000000000000000000000000000005"
TX6 = "00000000000000000000000000000006"


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
def viewer_user(session_factory):
    with session_factory() as session:
        user = User(
            username="viewer",
            display_name="Viewer",
            password_hash=hash_password("viewerpass"),
        )
        session.add(user)
        session.commit()
        return user.id


@pytest.fixture
def viewer_headers(client, viewer_user):
    response = client.post(
        "/auth/login",
        json={"username": "viewer", "password": "viewerpass"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


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
    transaction: "FakeTransaction | None" = None


@dataclass
class FakeTransaction:
    guid: str
    post_date: date
    description: str
    splits: list[FakeSplit]
    notes: str = ""

    def __post_init__(self):
        for split in self.splits:
            split.transaction = self
            split.account.splits.append(split)


class FakeBookForExplorer:
    def __init__(self, accounts=None, transactions=None):
        self.accounts = accounts or []
        self.transactions = transactions or []
        self.closed = False

    def close(self):
        self.closed = True


@pytest.fixture
def fake_explorer_data():
    root = FakeAccount(guid="ffffffffffffffffffffffffffffffff", name="Root Account", type="ROOT")
    assets = FakeAccount(guid="11111111111111111111111111111111", name="Assets", type="ASSET", parent=root)
    expenses = FakeAccount(guid="22222222222222222222222222222222", name="Expenses", type="EXPENSE", parent=root)
    income = FakeAccount(guid="33333333333333333333333333333333", name="Income", type="INCOME", parent=root)
    checking = FakeAccount(guid=CHECKING, name="Checking", type="BANK", parent=assets)
    food = FakeAccount(guid=FOOD, name="Food", type="EXPENSE", parent=expenses)
    salary = FakeAccount(guid=SALARY, name="Salary", type="INCOME", parent=income)
    transport = FakeAccount(guid=TRANSPORT, name="Transport", type="EXPENSE", parent=expenses)
    eur = FakeAccount(
        guid=EUR_ACCOUNT,
        name="EUR Bank",
        type="BANK",
        parent=assets,
        commodity=FakeCommodity("EUR"),
    )

    transactions = [
        FakeTransaction(
            guid=TX1,
            post_date=date(2026, 5, 16),
            description="ICA ångström",
            splits=[
                FakeSplit(account=checking, value=Decimal("-320.10"), reconcile_state="c"),
                FakeSplit(account=food, value=Decimal("320.10"), memo="Fika İSTANBUL groceries", reconcile_state="c"),
            ],
        ),
        FakeTransaction(
            guid=TX2,
            post_date=date(2026, 5, 17),
            description="Split transaction test",
            splits=[
                FakeSplit(account=checking, value=Decimal("-50")),
                FakeSplit(account=food, value=Decimal("40"), memo="literal * wildcard"),
                FakeSplit(account=transport, value=Decimal("10")),
            ],
            notes="PRIVATE_NOTE_MAGIC",
        ),
        FakeTransaction(
            guid=TX3,
            post_date=date(2026, 5, 18),
            description="Salary",
            splits=[
                FakeSplit(account=checking, value=Decimal("5000"), reconcile_state="y"),
                FakeSplit(account=salary, value=Decimal("-5000"), reconcile_state="y"),
            ],
        ),
        FakeTransaction(
            guid=TX4,
            post_date=date(2026, 5, 18),
            description="Bonus",
            splits=[
                FakeSplit(account=checking, value=Decimal("1000"), reconcile_state="y"),
                FakeSplit(account=salary, value=Decimal("-1000"), reconcile_state="y"),
            ],
        ),
        FakeTransaction(
            guid=TX5,
            post_date=date(2026, 5, 15),
            description="Grocery refund",
            splits=[
                FakeSplit(account=checking, value=Decimal("12.34")),
                FakeSplit(account=food, value=Decimal("-12.34"), memo="refund"),
            ],
        ),
        FakeTransaction(
            guid=TX6,
            post_date=date(2026, 6, 1),
            description="Income reversal",
            splits=[
                FakeSplit(account=checking, value=Decimal("-25")),
                FakeSplit(account=salary, value=Decimal("25"), memo="chargeback"),
            ],
        ),
    ]
    accounts = [root, assets, expenses, income, checking, food, salary, transport, eur]
    return accounts, transactions


@pytest.fixture
def explorer_book_path(tmp_path, monkeypatch, fake_explorer_data):
    book_path = tmp_path / "synthetic-explorer.gnucash"
    book_path.write_text("fake", encoding="utf-8")
    accounts, transactions = fake_explorer_data

    def fake_open_book(path, readonly=False):
        assert readonly is True
        return FakeBookForExplorer(accounts=accounts, transactions=transactions)

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path


@pytest.fixture
def sample_book(session_factory, explorer_book_path):
    with session_factory() as session:
        book = Book(
            name="Synthetic Explorer Book",
            storage_type="sqlite",
            uri_or_path=str(explorer_book_path),
            base_currency="SEK",
            is_default=True,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


def explorer_url(book_id: int, **params) -> str:
    base = f"/books/{book_id}/transactions/explorer"
    if not params:
        return base
    from urllib.parse import urlencode

    pairs = []
    for key, value in params.items():
        if isinstance(value, list):
            pairs.extend((key, item) for item in value)
        else:
            pairs.append((key, value))
    return f"{base}?{urlencode(pairs)}"


BASE_PARAMS = {"date_from": "2026-05-01", "date_to": "2026-05-31"}


class TestTransactionExplorerAccessAndPaging:
    def test_requires_auth(self, client, sample_book):
        response = client.get(explorer_url(sample_book, **BASE_PARAMS))

        assert response.status_code == 401

    def test_first_next_previous_pages_preserve_date_guid_order(self, client, auth_headers, sample_book):
        first = client.get(explorer_url(sample_book, **BASE_PARAMS, page_size="2"), headers=auth_headers)

        assert first.status_code == 200
        page1 = first.json()
        assert [item["id"] for item in page1["items"]] == [TX4, TX3]
        assert page1["has_more"] is True
        assert page1["has_previous"] is False
        assert page1["next_cursor"]
        assert page1["previous_cursor"] is None
        assert page1["returned_count"] == 2
        assert page1["sort"] == "date_desc"
        assert page1["normalized_filters"]["date_from"] == BASE_PARAMS["date_from"]
        assert page1["scan"]["candidate_rows"] <= 3

        second = client.get(
            explorer_url(sample_book, **BASE_PARAMS, page_size="2", cursor=page1["next_cursor"]),
            headers=auth_headers,
        )
        assert second.status_code == 200
        page2 = second.json()
        assert [item["id"] for item in page2["items"]] == [TX2, TX1]
        assert page2["has_more"] is True
        assert page2["has_previous"] is True
        assert page2["previous_cursor"]

        previous = client.get(
            explorer_url(sample_book, **BASE_PARAMS, page_size="2", cursor=page2["previous_cursor"]),
            headers=auth_headers,
        )
        assert previous.status_code == 200
        assert [item["id"] for item in previous.json()["items"]] == [TX4, TX3]

    def test_date_asc_uses_guid_tie_break(self, client, auth_headers, sample_book):
        response = client.get(explorer_url(sample_book, **BASE_PARAMS, sort="date_asc"), headers=auth_headers)

        assert response.status_code == 200
        assert [item["id"] for item in response.json()["items"]] == [TX5, TX1, TX2, TX3, TX4]

    def test_viewer_without_book_access_is_blocked_before_opening_book(
        self, client, viewer_headers, sample_book, monkeypatch
    ):
        import app.routers.transactions as transactions_router

        def fail_if_called(_book):
            raise AssertionError("explorer must not open unauthorized books")

        monkeypatch.setattr(transactions_router, "transaction_service_for", fail_if_called)

        response = client.get(explorer_url(sample_book, **BASE_PARAMS), headers=viewer_headers)

        assert response.status_code == 403

    def test_explorer_does_not_call_write_helpers_or_create_app_mutation_rows(
        self, client, auth_headers, sample_book, session_factory, monkeypatch
    ):
        import app.routers.owner_writebeta as owner_writebeta_router
        import app.routers.transactions as transactions_router
        import app.services.gnucash_write as gnucash_write_module

        def fail_if_called(*args, **kwargs):
            raise AssertionError("transaction explorer must remain read-only")

        for guarded_name in (
            "_require_book_edit_access",
            "_ensure_writes_enabled",
            "_ensure_write_alpha_test_scope",
            "_write_service_for",
            "_audit_log",
            "_update_audit_log",
            "_record_write_alpha_transaction_ownership",
            "_require_write_alpha_transaction_ownership",
            "_mark_write_alpha_transaction_mutated",
            "_backup_audit_fields",
            "_write_lock_detail",
        ):
            monkeypatch.setattr(transactions_router, guarded_name, fail_if_called)

        monkeypatch.setattr(owner_writebeta_router, "require_owner_writebeta_if_active", fail_if_called)
        monkeypatch.setattr(gnucash_write_module, "create_book_backup", fail_if_called)
        monkeypatch.setattr(gnucash_write_module.write_lock_service, "lock", fail_if_called)
        monkeypatch.setattr(gnucash_write_module.write_lock_service, "acquire", fail_if_called)
        monkeypatch.setattr(
            gnucash_write_module.GnuCashWriteService,
            "_open_piecash_book_for_write",
            fail_if_called,
        )

        response = client.get(explorer_url(sample_book, **BASE_PARAMS), headers=auth_headers)

        assert response.status_code == 200
        with session_factory() as session:
            assert session.query(AuditLog).count() == 0
            assert session.query(WriteAlphaTransactionOwnership).count() == 0


class TestTransactionExplorerFilterSemantics:
    def test_account_direction_amount_state_uses_sum_of_selected_splits(self, client, auth_headers, sample_book):
        response = client.get(
            explorer_url(
                sample_book,
                **BASE_PARAMS,
                account_ids=[CHECKING],
                direction="decrease",
                min_amount="100",
                max_amount="400",
                transaction_state="cleared",
            ),
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert [item["id"] for item in data["items"]] == [TX1]
        row = data["items"][0]
        assert row["representative_amount"] == {"amount": "-320.10", "currency": "SEK"}
        assert row["matched_amount"] == {"amount": "-320.10", "currency": "SEK"}
        assert row["matched_account_ids"] == [CHECKING]
        assert row["amount_basis"] == "selected_accounts"
        assert row["representative_account"] == {"id": CHECKING, "name": "Assets:Checking"}

    def test_multiple_accounts_sum_to_one_row_per_transaction(self, client, auth_headers, sample_book):
        response = client.get(
            explorer_url(
                sample_book,
                **BASE_PARAMS,
                account_ids=[FOOD, TRANSPORT],
                direction="increase",
                min_amount="50",
                max_amount="50",
            ),
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert [item["id"] for item in data["items"]] == [TX2]
        assert data["items"][0]["matched_amount"] == {"amount": "50.00", "currency": "SEK"}
        assert data["items"][0]["matched_account_ids"] == [FOOD, TRANSPORT]

    def test_income_type_is_base_currency_perspective_and_incompatible_with_accounts(
        self, client, auth_headers, sample_book
    ):
        income = client.get(
            explorer_url(sample_book, **BASE_PARAMS, type="income", min_amount="5000", max_amount="5000"),
            headers=auth_headers,
        )

        assert income.status_code == 200
        assert [item["id"] for item in income.json()["items"]] == [TX3]
        assert income.json()["items"][0]["matched_amount"] == {"amount": "5000.00", "currency": "SEK"}
        assert income.json()["items"][0]["amount_basis"] == "income"

        incompatible = client.get(
            explorer_url(sample_book, **BASE_PARAMS, type="income", account_ids=[CHECKING]),
            headers=auth_headers,
        )
        assert incompatible.status_code == 422
        assert incompatible.json()["detail"]["code"] == "incompatible_filter_mode"

    def test_type_filters_use_only_matching_account_types_without_cross_sign_reclassification(
        self, client, auth_headers, sample_book
    ):
        income = client.get(explorer_url(sample_book, **BASE_PARAMS, type="income"), headers=auth_headers)
        expense = client.get(
            explorer_url(sample_book, date_from="2026-06-01", date_to="2026-06-30", type="expense"),
            headers=auth_headers,
        )

        assert income.status_code == 200
        assert [item["id"] for item in income.json()["items"]] == [TX4, TX3]
        assert TX5 not in [item["id"] for item in income.json()["items"]]
        assert expense.status_code == 200
        assert expense.json()["items"] == []

    def test_query_uses_unicode_casefold_description_and_memos_but_excludes_notes(
        self, client, auth_headers, sample_book
    ):
        description = client.get(explorer_url(sample_book, **BASE_PARAMS, query="ÅNG"), headers=auth_headers)
        memo = client.get(explorer_url(sample_book, **BASE_PARAMS, query="fika"), headers=auth_headers)
        literal = client.get(explorer_url(sample_book, **BASE_PARAMS, query="*"), headers=auth_headers)
        notes = client.get(explorer_url(sample_book, **BASE_PARAMS, query="PRIVATE_NOTE_MAGIC"), headers=auth_headers)

        assert description.status_code == 200
        assert [item["id"] for item in description.json()["items"]] == [TX1]
        assert memo.status_code == 200
        assert [item["id"] for item in memo.json()["items"]] == [TX1]
        assert literal.status_code == 200
        assert [item["id"] for item in literal.json()["items"]] == [TX2]
        assert notes.status_code == 200
        assert notes.json()["items"] == []


class TestTransactionExplorerValidationAndCursors:
    @pytest.mark.parametrize(
        ("params", "code"),
        [
            ({"date_from": "2026-05-01"}, "date_pair_required"),
            ({"date_from": "2026-05-32", "date_to": "2026-05-31"}, "invalid_date"),
            ({"date_from": "2026-05-31", "date_to": "2026-05-01"}, "invalid_date_range"),
            ({"date_from": "2025-01-01", "date_to": "2026-01-02"}, "date_range_too_wide"),
            ({**BASE_PARAMS, "page_size": "101"}, "invalid_page_size"),
            ({**BASE_PARAMS, "sort": "amount_desc"}, "invalid_sort"),
            ({**BASE_PARAMS, "account_ids": [CHECKING, CHECKING.upper()]}, "duplicate_account_id"),
            ({**BASE_PARAMS, "account_id": CHECKING}, "invalid_account_id"),
            ({**BASE_PARAMS, "direction": "increase"}, "account_scope_required"),
            ({**BASE_PARAMS, "min_amount": "1.00"}, "account_scope_required"),
            ({**BASE_PARAMS, "account_ids": [CHECKING], "min_amount": "01.00"}, "invalid_amount"),
            ({**BASE_PARAMS, "account_ids": [CHECKING], "min_amount": "2", "max_amount": "1"}, "invalid_amount"),
            ({**BASE_PARAMS, "query": "   "}, "invalid_query"),
        ],
    )
    def test_validation_errors_are_typed_and_redacted(self, client, auth_headers, sample_book, params, code):
        response = client.get(explorer_url(sample_book, **params), headers=auth_headers)

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == code
        serialized = json.dumps(response.json())
        assert "/data/books" not in serialized
        assert "synthetic-explorer" not in serialized

    def test_unknown_and_non_base_accounts_are_rejected(self, client, auth_headers, sample_book):
        unknown = client.get(
            explorer_url(sample_book, **BASE_PARAMS, account_ids=["99999999999999999999999999999999"]),
            headers=auth_headers,
        )
        non_base = client.get(
            explorer_url(sample_book, **BASE_PARAMS, account_ids=[EUR_ACCOUNT]),
            headers=auth_headers,
        )

        assert unknown.status_code == 422
        assert unknown.json()["detail"]["code"] == "unknown_account"
        assert non_base.status_code == 422
        assert non_base.json()["detail"]["code"] == "unsupported_currency_scope"

    def test_tampered_filter_mismatch_and_expired_cursors_are_typed(self, client, auth_headers, sample_book):
        first = client.get(explorer_url(sample_book, **BASE_PARAMS, page_size="1"), headers=auth_headers)
        assert first.status_code == 200
        cursor = first.json()["next_cursor"]
        assert cursor

        tampered = cursor[:-1] + ("A" if cursor[-1] != "A" else "B")
        tampered_response = client.get(
            explorer_url(sample_book, **BASE_PARAMS, page_size="1", cursor=tampered),
            headers=auth_headers,
        )
        assert tampered_response.status_code == 422
        assert tampered_response.json()["detail"]["code"] == "invalid_cursor"

        mismatch = client.get(
            explorer_url(sample_book, date_from="2026-05-01", date_to="2026-05-30", page_size="1", cursor=cursor),
            headers=auth_headers,
        )
        assert mismatch.status_code == 422
        assert mismatch.json()["detail"]["code"] == "cursor_filter_mismatch"

        parsed = build_transaction_explorer_query(
            **BASE_PARAMS,
            account_ids=None,
            legacy_account_id_present=False,
            direction=None,
            transaction_type=None,
            min_amount=None,
            max_amount=None,
            query=None,
            transaction_state=None,
            sort=None,
            page_size="1",
            cursor=None,
            secret=TEST_SETTINGS.jwt_secret,
        )
        expired = encode_explorer_cursor(
            mode="next",
            cursor_date=date(2026, 5, 18),
            cursor_guid=TX4,
            filter_hash=parsed.filter_hash,
            sort=parsed.sort,
            secret=TEST_SETTINGS.jwt_secret,
            now=datetime.now(timezone.utc) - CURSOR_TTL - timedelta(seconds=10),
        )
        expired_response = client.get(
            explorer_url(sample_book, **BASE_PARAMS, page_size="1", cursor=expired),
            headers=auth_headers,
        )
        assert expired_response.status_code == 422
        assert expired_response.json()["detail"]["code"] == "cursor_expired"

    def test_cursor_payload_is_filter_bound_without_private_query_text(self, client, auth_headers, sample_book):
        response = client.get(
            explorer_url(sample_book, **BASE_PARAMS, query="grocer", page_size="1"),
            headers=auth_headers,
        )

        assert response.status_code == 200
        token = response.json()["next_cursor"]
        assert token
        payload_part = token.split(".", 1)[0]
        decoded = base64.urlsafe_b64decode((payload_part + "=" * (-len(payload_part) % 4)).encode("ascii"))
        payload = json.loads(decoded.decode("utf-8"))
        serialized_payload = json.dumps(payload)
        assert "grocer" not in serialized_payload
        assert len(token) <= 1024


class TestTransactionExplorerBoundsAndStaticGuards:
    def test_candidate_scan_limit_returns_honest_continuation(
        self, client, auth_headers, session_factory, tmp_path, monkeypatch
    ):
        checking = FakeAccount(guid=CHECKING, name="Checking", type="BANK")
        food = FakeAccount(guid=FOOD, name="Food", type="EXPENSE")
        transactions = [
            FakeTransaction(
                guid=f"{idx:032x}",
                post_date=date(2026, 5, 1),
                description="unmatched",
                splits=[FakeSplit(account=checking, value=Decimal("-1")), FakeSplit(account=food, value=Decimal("1"))],
            )
            for idx in range(2105)
        ]
        path = tmp_path / "bounded-scan.gnucash"
        path.write_text("fake", encoding="utf-8")

        def fake_open_book(path_arg, readonly=False):
            return FakeBookForExplorer(accounts=[checking, food], transactions=transactions)

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        with session_factory() as session:
            book = Book(
                name="Bounded scan",
                storage_type="sqlite",
                uri_or_path=str(path),
                base_currency="SEK",
                is_default=False,
            )
            session.add(book)
            session.flush()
            admin = session.query(User).filter(User.username == "admin").one()
            session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
            session.commit()
            book_id = book.id

        response = client.get(
            explorer_url(book_id, date_from="2026-05-01", date_to="2026-05-01", query="does-not-match"),
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["has_more"] is True
        assert data["next_cursor"]
        assert data["scan"]["scan_limited"] is True
        assert data["scan"]["candidate_rows"] == 2000
        assert data["scan"]["query_count"] == 10
        assert data["scan"]["exhausted"] is False

    def test_split_guard_returns_result_too_complex_not_partial_rows(
        self, client, auth_headers, session_factory, tmp_path, monkeypatch
    ):
        checking = FakeAccount(guid=CHECKING, name="Checking", type="BANK")
        splits = [FakeSplit(account=checking, value=Decimal("1")) for _ in range(20001)]
        transaction = FakeTransaction(guid=TX1, post_date=date(2026, 5, 1), description="too complex", splits=splits)
        path = tmp_path / "split-guard.gnucash"
        path.write_text("fake", encoding="utf-8")

        def fake_open_book(path_arg, readonly=False):
            return FakeBookForExplorer(accounts=[checking], transactions=[transaction])

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        with session_factory() as session:
            book = Book(
                name="Split guard",
                storage_type="sqlite",
                uri_or_path=str(path),
                base_currency="SEK",
                is_default=False,
            )
            session.add(book)
            session.flush()
            admin = session.query(User).filter(User.username == "admin").one()
            session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
            session.commit()
            book_id = book.id

        response = client.get(
            explorer_url(book_id, date_from="2026-05-01", date_to="2026-05-01"),
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "result_too_complex"

    def test_explorer_source_avoids_legacy_count_and_route_order_is_before_dynamic_detail(self):
        import app.routers.transactions as transactions_router
        import app.services.gnucash_book as gnucash_book

        route_paths = [getattr(route, "path", "") for route in transactions_router.router.routes]
        assert route_paths.index("/books/{book_id}/transactions/explorer") < route_paths.index(
            "/books/{book_id}/transactions/{transaction_id}"
        )

        router_source = inspect.getsource(transactions_router.list_book_transactions_explorer)
        assert "count_transactions" not in router_source
        assert "list_transactions(" not in router_source
        assert "explore_transactions" in router_source

        service_source = inspect.getsource(gnucash_book.GnuCashBookService.explore_transactions)
        assert "count_transactions" not in service_source
        assert "list_transactions(" not in service_source
        sql_source = inspect.getsource(gnucash_book.GnuCashBookService._explorer_sql_candidate_chunk)
        assert "_transactions(book)" not in sql_source
        assert "join(piecash.Transaction.splits)" in sql_source
        assert "limit(limit)" in sql_source
