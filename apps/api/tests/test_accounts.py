"""Tests for book-aware accounts API endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
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
def second_book(session_factory):
    with session_factory() as session:
        book = Book(
            name="Second Book",
            storage_type="sqlite",
            uri_or_path="/data/books/second.gnucash.sqlite",
            is_default=False,
        )
        session.add(book)
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
# Fake GnuCash book fixtures for monkeypatching piecash in route tests
# ---------------------------------------------------------------------------

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
    quantity: Decimal


class FakeBook:
    def __init__(self, accounts=None):
        self.accounts = accounts or []
        self.closed = False

    def close(self):
        self.closed = True


def _hex_guid(value: int) -> str:
    return f"{value:032x}"


def _amount(amount: str, *, namespace: str = "CURRENCY", mnemonic: str = "SEK") -> dict:
    return {"amount": amount, "commodity": {"namespace": namespace, "mnemonic": mnemonic}}


def _assert_identity_commodity(payload: dict, *, namespace: str = "CURRENCY", mnemonic: str = "SEK") -> None:
    assert payload["commodity"] == {"namespace": namespace, "mnemonic": mnemonic}
    assert "commodity_namespace" not in payload
    assert "commodity_mnemonic" not in payload


def _set_book_path(session_factory, book_id: int, path: Path) -> None:
    with session_factory() as session:
        book = session.query(Book).filter(Book.id == book_id).first()
        book.uri_or_path = str(path)
        session.commit()


@pytest.fixture
def install_explorer_fake_book(tmp_path, monkeypatch):
    opened: list[str] = []

    def install(accounts, *, book_cls=FakeBook):
        book_path = tmp_path / "explorer.gnucash"
        book_path.write_text("fake")

        def fake_open_book(path, readonly=False):
            assert readonly is True
            opened.append(str(path))
            return book_cls(accounts=accounts)

        import app.services.gnucash_book as gb_module

        monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
        return book_path, opened

    return install


def _explorer_accounts():
    root = FakeAccount(guid=_hex_guid(1), name="Root", type="ROOT")
    assets = FakeAccount(guid=_hex_guid(2), name="Assets", type="ASSET", parent=root)
    bank = FakeAccount(
        guid=_hex_guid(3),
        name="Bank",
        type="BANK",
        parent=assets,
        splits=[FakeSplit(Decimal("123.4567"))],
    )
    cafe = FakeAccount(
        guid=_hex_guid(4),
        name="Cafe\u0301",
        type="BANK",
        parent=assets,
        splits=[FakeSplit(Decimal("1.2345"))],
    )
    income = FakeAccount(
        guid=_hex_guid(5),
        name="Salary",
        type="INCOME",
        parent=root,
        splits=[FakeSplit(Decimal("-10.5"))],
    )
    hidden = FakeAccount(guid=_hex_guid(6), name="Hidden", type="BANK", parent=root, hidden=True)
    placeholder = FakeAccount(guid=_hex_guid(7), name="Placeholder", type="EXPENSE", parent=assets, placeholder=True)
    usd = FakeAccount(
        guid=_hex_guid(8),
        name="USD cash",
        type="CASH",
        commodity=FakeCommodity(mnemonic="USD"),
        parent=assets,
        splits=[FakeSplit(Decimal("2"))],
    )
    return [root, assets, bank, cafe, income, hidden, placeholder, usd]


@pytest.fixture
def fake_gnucash_accounts():
    root = FakeAccount(guid="root-guid", name="Assets", type="ROOT")
    bank = FakeAccount(guid="bank-guid", name="Bank", type="ASSET", parent=root)
    checking = FakeAccount(
        guid="checking-guid",
        name="Checking",
        type="BANK",
        parent=bank,
        balance=Decimal("12345.67"),
    )
    placeholder = FakeAccount(
        guid="placeholder-guid",
        name="Hidden placeholder",
        type="EXPENSE",
        placeholder=True,
        hidden=True,
    )
    return [root, bank, checking, placeholder]


@pytest.fixture
def fake_book_path(tmp_path, monkeypatch, fake_gnucash_accounts):
    book_path = tmp_path / "test.gnucash"
    book_path.write_text("fake")

    def fake_open_book(path, readonly=False):
        return FakeBook(accounts=fake_gnucash_accounts)

    def fake_open_book_uri(*, uri_conn, readonly=False):
        return FakeBook(accounts=fake_gnucash_accounts)

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path


# ---------------------------------------------------------------------------
# Tests: GET /books
# ---------------------------------------------------------------------------

class TestListBooks:
    def test_requires_auth(self, client):
        response = client.get("/books")
        assert response.status_code == 401

    def test_returns_books_for_user(self, client, auth_headers, sample_book):
        response = client.get("/books", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        ids = [b["id"] for b in data]
        assert sample_book in ids

        book = next(b for b in data if b["id"] == sample_book)
        assert book["access_role"] == "owner"
        assert book["read_only"] is True
        assert book["status"] == "not_checked"
        assert book["health"]["safe_code"] == "not_checked"
        assert book["management_actions"] == ["set_default", "remove_from_registry"]

    def test_excludes_books_without_access(
        self, client, auth_headers, second_book
    ):
        response = client.get("/books", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        ids = [b["id"] for b in data]
        assert second_book not in ids

    def test_excludes_archived_books_even_with_access(
        self, client, auth_headers, sample_book, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).one()
            book.is_archived = True
            session.commit()

        response = client.get("/books", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}
# ---------------------------------------------------------------------------

class TestGetBook:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}")
        assert response.status_code == 401

    def test_returns_book(self, client, auth_headers, sample_book):
        response = client.get(f"/books/{sample_book}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_book
        assert data["name"] == "Test Book"
        assert data["access_role"] == "owner"
        assert data["read_only"] is True
        assert data["status"] == "not_checked"
        assert data["health"]["safe_code"] == "not_checked"
        assert data["access_status"] == "accessible"
        assert "uri_or_path" not in data
        assert data["management_actions"] == ["set_default", "remove_from_registry"]

    def test_not_found(self, client, auth_headers):
        response = client.get("/books/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_access_denied_for_unauthorized_book(
        self, client, viewer_headers, sample_book, session_factory
    ):
        # viewer has no access to sample_book
        response = client.get(
            f"/books/{sample_book}", headers=viewer_headers
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/accounts
# ---------------------------------------------------------------------------

class TestListAccounts:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/accounts")
        assert response.status_code == 401

    def test_returns_accounts(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        # Update the book path to match our fake
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        names = [a["name"] for a in data]
        assert "Assets" not in names
        assert "Bank" in names
        assert "Checking" in names
        checking = next(a for a in data if a["name"] == "Checking")
        assert checking["display_name"] == "Checking"
        assert checking["full_name"] == "Assets:Bank:Checking"
        assert checking["currency"] == "SEK"
        assert "commodity" not in checking
        assert "commodity_namespace" not in checking
        assert "commodity_mnemonic" not in checking

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts", headers=viewer_headers
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/accounts/tree
# ---------------------------------------------------------------------------

class TestAccountTree:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/accounts/tree")
        assert response.status_code == 401

    def test_tree_shape(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/tree", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Structural ROOT is suppressed; visible children are promoted to ordinary roots.
        root_ids = [n["id"] for n in data]
        assert "root-guid" not in root_ids
        assert "bank-guid" in root_ids
        assert "placeholder-guid" in root_ids

        # Check promoted nesting: Bank -> Checking
        bank = next(n for n in data if n["id"] == "bank-guid")
        assert len(bank["children"]) == 1
        assert bank["children"][0]["id"] == "checking-guid"

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/tree", headers=viewer_headers
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/accounts/explorer
# ---------------------------------------------------------------------------

class TestAccountExplorer:
    def test_requires_auth(self, client, sample_book):
        response = client.get(f"/books/{sample_book}/accounts/explorer")
        assert response.status_code == 401

    def test_tree_preorder_exact_balances_and_metadata(
        self, client, auth_headers, sample_book, install_explorer_fake_book, session_factory
    ):
        book_path, opened = install_explorer_fake_book(_explorer_accounts())
        _set_book_path(session_factory, sample_book, book_path)

        response = client.get(f"/books/{sample_book}/accounts/explorer", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert opened == [str(book_path)]
        assert data["book_id"] == sample_book
        assert data["mode"] == "tree"
        assert data["normalized_filters"] == {
            "query": None,
            "types": [],
            "hidden": "exclude",
            "placeholder": "include",
        }
        assert data["balance_basis"] == "native_commodity_account_natural_sign"
        assert data["includes_currency_conversion"] is False
        assert any("currency conversion" in item for item in data["limitations"])
        assert data["root_ids"] == [_hex_guid(2), _hex_guid(5)]
        assert [node["id"] for node in data["nodes"]] == [
            _hex_guid(2),
            _hex_guid(3),
            _hex_guid(4),
            _hex_guid(7),
            _hex_guid(8),
            _hex_guid(5),
        ]
        assert data["returned_count"] == 6
        assert data["scan"]["candidate_accounts"] == 7
        assert data["scan"]["returned_nodes"] == 6
        assert data["scan"]["split_rows"] == 4
        assert data["scan"]["query_count"] <= 8
        assert data["scan"]["rollup_bucket_cells"] >= 0
        assert "rollup_cells" not in data["scan"]
        assert "rollup_bucket_cells" in data["scan"]["limits"]
        assert "rollup_cells" not in data["scan"]["limits"]

        by_id = {node["id"]: node for node in data["nodes"]}
        bank = by_id[_hex_guid(3)]
        assert bank["source_parent_id"] == _hex_guid(2)
        assert bank["parent_id"] == _hex_guid(2)
        assert bank["root_id"] == _hex_guid(2)
        assert bank["depth"] == 1
        assert bank["path"] == [
            {"id": _hex_guid(2), "name": "Assets", "display_name": "Assets"},
            {"id": _hex_guid(3), "name": "Bank", "display_name": "Bank"},
        ]
        assert bank["full_path"] == "Assets:Bank"
        assert bank["type"] == "BANK"
        _assert_identity_commodity(bank)
        assert bank["direct_balance"] == _amount("123.4567")
        assert bank["recursive_balances"] == [bank["direct_balance"]]
        assert bank["child_count"] == 0
        assert bank["match_state"] == "match"
        assert bank["structure_status"] == "normal"
        assert by_id[_hex_guid(2)]["structure_status"] == "orphan_promoted"

        cafe = by_id[_hex_guid(4)]
        assert cafe["name"] == "Café"
        assert cafe["full_path"] == "Assets:Café"
        assert cafe["direct_balance"]["amount"] == "1.2345"

        assets = by_id[_hex_guid(2)]
        assert assets["child_count"] == 4
        assert assets["recursive_balances"] == [
            _amount("124.6912"),
            _amount("2", mnemonic="USD"),
        ]
        income = by_id[_hex_guid(5)]
        assert income["direct_balance"]["amount"] == "10.5"
        assert _hex_guid(6) not in by_id

    def test_query_type_flat_tree_and_context_filters(
        self, client, auth_headers, sample_book, install_explorer_fake_book, session_factory
    ):
        book_path, _ = install_explorer_fake_book(_explorer_accounts())
        _set_book_path(session_factory, sample_book, book_path)

        tree = client.get(
            f"/books/{sample_book}/accounts/explorer",
            headers=auth_headers,
            params={"query": " cafe\u0301 "},
        )
        assert tree.status_code == 200
        tree_data = tree.json()
        assert tree_data["normalized_filters"]["query"] == "café"
        assert [node["id"] for node in tree_data["nodes"]] == [_hex_guid(2), _hex_guid(4)]
        assert [node["match_state"] for node in tree_data["nodes"]] == ["ancestor_context", "match"]

        flat = client.get(
            f"/books/{sample_book}/accounts/explorer",
            headers=auth_headers,
            params={"mode": "flat", "query": "CAFÉ"},
        )
        assert flat.status_code == 200
        flat_data = flat.json()
        assert flat_data["mode"] == "flat"
        assert [node["id"] for node in flat_data["nodes"]] == [_hex_guid(4)]
        assert flat_data["nodes"][0]["root_id"] == _hex_guid(2)

        typed = client.get(
            f"/books/{sample_book}/accounts/explorer",
            headers=auth_headers,
            params=[("type", "bank"), ("type", " asset ")],
        )
        assert typed.status_code == 200
        typed_data = typed.json()
        assert typed_data["normalized_filters"]["types"] == ["ASSET", "BANK"]
        assert [node["id"] for node in typed_data["nodes"]] == [
            _hex_guid(2),
            _hex_guid(3),
            _hex_guid(4),
        ]

    def test_hidden_placeholder_modes(
        self, client, auth_headers, sample_book, install_explorer_fake_book, session_factory
    ):
        book_path, _ = install_explorer_fake_book(_explorer_accounts())
        _set_book_path(session_factory, sample_book, book_path)

        hidden_only = client.get(
            f"/books/{sample_book}/accounts/explorer",
            headers=auth_headers,
            params={"hidden": "only"},
        )
        assert hidden_only.status_code == 200
        assert [node["id"] for node in hidden_only.json()["nodes"]] == [_hex_guid(6)]
        assert [node["match_state"] for node in hidden_only.json()["nodes"]] == ["match"]

        placeholder_excluded = client.get(
            f"/books/{sample_book}/accounts/explorer",
            headers=auth_headers,
            params={"placeholder": "exclude"},
        )
        assert placeholder_excluded.status_code == 200
        assert _hex_guid(7) not in {node["id"] for node in placeholder_excluded.json()["nodes"]}

    def test_invalid_filters_are_typed_and_redacted(
        self, client, auth_headers, sample_book, install_explorer_fake_book, session_factory
    ):
        book_path, _ = install_explorer_fake_book(_explorer_accounts())
        _set_book_path(session_factory, sample_book, book_path)

        duplicate = client.get(
            f"/books/{sample_book}/accounts/explorer",
            headers=auth_headers,
            params=[("type", "bank"), ("type", " BANK ")],
        )
        assert duplicate.status_code == 422
        assert duplicate.json()["detail"]["code"] == "duplicate_type"
        assert "bank" not in duplicate.text.lower()

        hidden = client.get(
            f"/books/{sample_book}/accounts/explorer",
            headers=auth_headers,
            params={"hidden": "private-account-name"},
        )
        assert hidden.status_code == 422
        assert hidden.json()["detail"]["code"] == "invalid_hidden"
        assert "private-account-name" not in hidden.text

    def test_orphans_and_cycles_are_promoted_without_losing_source_parent(
        self, client, auth_headers, sample_book, install_explorer_fake_book, session_factory
    ):
        external = FakeAccount(guid=_hex_guid(31), name="External")
        orphan = FakeAccount(guid=_hex_guid(30), name="Orphan", type="BANK", parent=external)
        cycle_a = FakeAccount(guid=_hex_guid(20), name="Cycle A", type="ASSET")
        cycle_b = FakeAccount(guid=_hex_guid(21), name="Cycle B", type="ASSET")
        cycle_c = FakeAccount(guid=_hex_guid(22), name="Cycle C", type="ASSET")
        cycle_a.parent = cycle_c
        cycle_b.parent = cycle_a
        cycle_c.parent = cycle_b
        book_path, _ = install_explorer_fake_book([orphan, cycle_c, cycle_b, cycle_a])
        _set_book_path(session_factory, sample_book, book_path)

        response = client.get(f"/books/{sample_book}/accounts/explorer", headers=auth_headers)

        assert response.status_code == 200
        by_id = {node["id"]: node for node in response.json()["nodes"]}
        assert by_id[_hex_guid(30)]["source_parent_id"] == _hex_guid(31)
        assert by_id[_hex_guid(30)]["parent_id"] is None
        assert by_id[_hex_guid(30)]["structure_status"] == "orphan_promoted"
        assert by_id[_hex_guid(20)]["parent_id"] is None
        assert by_id[_hex_guid(20)]["structure_status"] == "cycle_broken_root"
        assert by_id[_hex_guid(21)]["parent_id"] == _hex_guid(20)
        assert by_id[_hex_guid(21)]["structure_status"] == "cycle_member"
        assert by_id[_hex_guid(22)]["parent_id"] == _hex_guid(21)
        assert by_id[_hex_guid(22)]["structure_status"] == "cycle_member"

    def test_result_bounds_are_typed_and_safe(
        self, client, auth_headers, sample_book, install_explorer_fake_book, session_factory, monkeypatch
    ):
        import app.services.account_explorer as ae

        book_path, _ = install_explorer_fake_book(_explorer_accounts())
        _set_book_path(session_factory, sample_book, book_path)

        monkeypatch.setattr(ae, "MAX_CANDIDATE_ACCOUNTS", 1)
        too_many = client.get(f"/books/{sample_book}/accounts/explorer", headers=auth_headers)
        assert too_many.status_code == 422
        assert too_many.json()["detail"]["code"] == "result_too_large"
        assert "Assets" not in too_many.text

        monkeypatch.setattr(ae, "MAX_CANDIDATE_ACCOUNTS", 10_000)
        monkeypatch.setattr(ae, "MAX_COMMODITY_BUCKETS", 1)
        too_many_buckets = client.get(f"/books/{sample_book}/accounts/explorer", headers=auth_headers)
        assert too_many_buckets.status_code == 422
        assert too_many_buckets.json()["detail"]["code"] == "too_many_commodities"

    def test_depth_response_and_rollup_bounds_are_typed(
        self, client, auth_headers, sample_book, install_explorer_fake_book, session_factory, monkeypatch
    ):
        import app.services.account_explorer as ae

        root = FakeAccount(guid=_hex_guid(40), name="Top", type="ASSET", splits=[FakeSplit(Decimal("1"))])
        child = FakeAccount(
            guid=_hex_guid(41),
            name="Child",
            type="ASSET",
            parent=root,
            splits=[FakeSplit(Decimal("2"))],
        )
        grandchild = FakeAccount(guid=_hex_guid(42), name="Grandchild", type="BANK", parent=child)
        book_path, _ = install_explorer_fake_book([root, child, grandchild])
        _set_book_path(session_factory, sample_book, book_path)

        monkeypatch.setattr(ae, "MAX_DEPTH", 1)
        too_deep = client.get(f"/books/{sample_book}/accounts/explorer", headers=auth_headers)
        assert too_deep.status_code == 422
        assert too_deep.json()["detail"]["code"] == "result_too_deep"

        monkeypatch.setattr(ae, "MAX_DEPTH", 64)
        monkeypatch.setattr(ae, "MAX_ROLLUP_CELLS", 1)
        too_complex = client.get(f"/books/{sample_book}/accounts/explorer", headers=auth_headers)
        assert too_complex.status_code == 422
        assert too_complex.json()["detail"]["code"] == "result_too_complex"

        monkeypatch.setattr(ae, "MAX_ROLLUP_CELLS", 50_000)
        monkeypatch.setattr(ae, "MAX_SERIALIZED_RESPONSE_BYTES", 128)
        too_large = client.get(f"/books/{sample_book}/accounts/explorer", headers=auth_headers)
        assert too_large.status_code == 422
        assert too_large.json()["detail"]["code"] == "result_too_large"

    def test_does_not_use_legacy_balance_formatter_transactions_or_mutations(
        self, client, auth_headers, sample_book, install_explorer_fake_book, session_factory, monkeypatch
    ):
        import app.services.gnucash_book as gb_module

        class GuardAccount(FakeAccount):
            mutation_count = 0

            def get_balance(self):
                raise AssertionError("legacy get_balance must not be used by account explorer")

        class GuardBook(FakeBook):
            @property
            def transactions(self):
                raise AssertionError("account explorer must not materialize transactions")

        def forbidden_format_money(value):
            raise AssertionError("account explorer must not use cent formatter")

        monkeypatch.setattr(gb_module, "format_money", forbidden_format_money)

        root = GuardAccount(guid=_hex_guid(50), name="Root", type="ASSET")
        child = GuardAccount(
            guid=_hex_guid(51),
            name="Precise",
            type="BANK",
            parent=root,
            splits=[FakeSplit(Decimal("1.234567"))],
        )
        book_path, opened = install_explorer_fake_book([root, child], book_cls=GuardBook)
        _set_book_path(session_factory, sample_book, book_path)

        response = client.get(f"/books/{sample_book}/accounts/explorer", headers=auth_headers)

        assert response.status_code == 200
        assert opened == [str(book_path)]
        assert response.json()["nodes"][1]["direct_balance"]["amount"] == "1.234567"
        assert response.json()["scan"]["query_count"] <= 8
        assert root.mutation_count == 0
        assert child.mutation_count == 0


# ---------------------------------------------------------------------------
# Tests: GET /books/{book_id}/accounts/{account_id}
# ---------------------------------------------------------------------------

class TestGetAccount:
    def test_requires_auth(self, client, sample_book):
        response = client.get(
            f"/books/{sample_book}/accounts/some-id"
        )
        assert response.status_code == 401

    def test_returns_account(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/checking-guid",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "checking-guid"
        assert data["name"] == "Checking"
        assert data["type"] == "BANK"
        assert data["balance"] == "12345.67"
        assert data["currency"] == "SEK"
        assert data["parent_id"] == "bank-guid"
        assert data["display_name"] == "Checking"
        assert set(data) == {
            "id",
            "name",
            "display_name",
            "full_name",
            "type",
            "currency",
            "balance",
            "placeholder",
            "hidden",
            "parent_id",
        }

    def test_unknown_account_returns_404(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/nonexistent-guid",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_access_denied(
        self, client, viewer_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            f"/books/{sample_book}/accounts/checking-guid",
            headers=viewer_headers,
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Tests: MVP aliases  GET /accounts, /accounts/tree, /accounts/{id}
# ---------------------------------------------------------------------------

class TestMVPAliases:
    def test_list_requires_auth(self, client):
        response = client.get("/accounts")
        assert response.status_code == 401

    def test_list_returns_default_book_accounts(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get("/accounts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_tree_requires_auth(self, client):
        response = client.get("/accounts/tree")
        assert response.status_code == 401

    def test_tree_returns_default_book_tree(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get("/accounts/tree", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        root_ids = [n["id"] for n in data]
        assert "root-guid" not in root_ids
        assert "bank-guid" in root_ids

    def test_get_requires_auth(self, client):
        response = client.get("/accounts/some-id")
        assert response.status_code == 401

    def test_get_returns_default_book_account(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            "/accounts/checking-guid", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "checking-guid"
        assert data["name"] == "Checking"

    def test_get_unknown_account_returns_404(
        self, client, auth_headers, sample_book, fake_book_path, session_factory
    ):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == sample_book).first()
            book.uri_or_path = str(fake_book_path)
            session.commit()

        response = client.get(
            "/accounts/nonexistent-guid", headers=auth_headers
        )
        assert response.status_code == 404
