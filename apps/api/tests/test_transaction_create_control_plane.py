"""Issue #59 backend control-plane tests for product transaction CREATE."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import threading

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import (
    AuditLog,
    Book,
    BookHealthSnapshot,
    TransactionCreateIdempotency,
    User,
    UserBookAccess,
    WriteAlphaTransactionOwnership,
)
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.book_preflight import SourceIdentity, canonical_path_hash
from app.services.metadata_migrations import run_app_metadata_migrations
from app.services.transaction_create_audit import serialize_transaction_create_audit_payload
from app.services.transaction_create_idempotency import IN_PROGRESS_STALE_AFTER_SECONDS, TransactionCreateIdempotencyService
from app.services.transaction_create_policy import evaluate_transaction_create_policy
from app.services.transaction_create_tokens import (
    canonical_transaction_create_request_hash,
    hash_idempotency_key,
    hash_token_jti,
    issue_preview_token,
    source_fingerprint_for_book,
    verify_preview_token,
)
from app.schemas.gnucash_writes import TransactionValidationResultDTO
from app.services.write_lock import WriteLockError

JWT_SECRET = "".join(("issue", "59-", "ctrl-", "plane-", "x" * 32))
TEST_ADMIN_PASSWORD = "test" + "password123"
BASE_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret=JWT_SECRET,
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password=TEST_ADMIN_PASSWORD,
)


class FakeAccount:
    def __init__(
        self,
        guid: str,
        name: str,
        full_name: str,
        account_type: str,
        currency: str = "SEK",
        commodity_namespace: str = "CURRENCY",
        commodity_fraction: int = 100,
    ):
        self.id = guid
        self.name = name
        self.full_name = full_name
        self.type = account_type
        self.currency = currency
        self.commodity_namespace = commodity_namespace
        self.commodity_fraction = commodity_fraction
        self.placeholder = False
        self.hidden = False


class FakeReadService:
    def list_accounts(self):
        return [
            FakeAccount("bank-guid", "Checking", "Assets:Bank:Checking", "BANK"),
            FakeAccount("food-guid", "Food", "Expenses:Food", "EXPENSE"),
            FakeAccount("income-guid", "Salary", "Income:Salary", "INCOME"),
        ]

    def list_accounts_by_ids(self, account_ids):
        requested = set(account_ids)
        return [account for account in self.list_accounts() if account.id in requested]


class FakeLiveSourceEvidence:
    identity = SourceIdentity(
        canonical_path="/redacted/synthetic.gnucash.sqlite",
        canonical_path_hash="live-canonical-hash",
        st_dev=101,
        st_ino=202,
        st_size=303,
        st_mtime_ns=404,
    )
    versions = {"Gnucash": 2030000, "Gnucash-Resave": 19920}
    base_currency = "SEK"


class FakePinnedSource(FakeLiveSourceEvidence):
    fd_path = "/synthetic/not-opened-pinned-fd.gnucash.sqlite"
    roots = ()

    def verify_current(self):
        return None

    def verify_same_file_after_write(self):
        return None


class FakePinnedSourceContext:
    def __enter__(self):
        return FakePinnedSource()

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
def api_context(tmp_path: Path, monkeypatch):
    import app.routers.transactions as transactions_router
    import app.services.write_lock as write_lock_module

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    settings = BASE_SETTINGS

    def override_get_db():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(
        transactions_router,
        "inspect_transaction_create_source",
        lambda book, settings: FakeLiveSourceEvidence(),
    )
    monkeypatch.setattr(
        transactions_router,
        "open_transaction_create_source",
        lambda book, settings, **kwargs: FakePinnedSourceContext(),
    )
    monkeypatch.setattr(
        transactions_router,
        "write_lock_service",
        write_lock_module.WriteLockService(lock_dir=tmp_path / "locks"),
    )

    with SessionLocal() as session:
        admin = User(
            username="admin",
            display_name="Admin",
            password_hash=hash_password(TEST_ADMIN_PASSWORD),
            is_admin=True,
        )
        editor = User(
            username="editor",
            display_name="Editor",
            password_hash=hash_password("editorpass"),
            is_admin=False,
        )
        viewer = User(
            username="viewer",
            display_name="Viewer",
            password_hash=hash_password("viewerpass"),
            is_admin=False,
        )
        session.add_all([admin, editor, viewer])
        session.flush()
        book = Book(
            name="Synthetic Control Book",
            storage_type="sqlite",
            uri_or_path="/synthetic/not-opened.gnucash.sqlite",
            canonical_path_hash="synthetic-source-hash",
            base_currency="SEK",
            is_default=True,
            is_archived=False,
            is_enabled=True,
        )
        session.add(book)
        session.flush()
        session.add(
            BookHealthSnapshot(
                book_id=book.id,
                source_status="ready",
                open_status="ready",
                accounts_status="ready",
                transactions_status="ready",
                reports_status="ready",
                safe_code="ready",
                checked_at=datetime.now(timezone.utc),
                last_successful_at=datetime.now(timezone.utc),
            )
        )
        session.add(UserBookAccess(user_id=editor.id, book_id=book.id, role="editor"))
        session.add(UserBookAccess(user_id=viewer.id, book_id=book.id, role="viewer"))
        session.commit()
        ids = {"book": book.id, "admin": admin.id, "editor": editor.id, "viewer": viewer.id}

    client = TestClient(app)
    tokens = {}
    for username, password in {
        "admin": TEST_ADMIN_PASSWORD,
        "editor": "editorpass",
        "viewer": "viewerpass",
    }.items():
        response = client.post("/auth/login", json={"username": username, "password": password})
        assert response.status_code == 200
        tokens[username] = {"Authorization": f"Bearer {response.json()['access_token']}"}

    yield {
        "client": client,
        "engine": engine,
        "session_factory": SessionLocal,
        "settings": settings,
        "ids": ids,
        "headers": tokens,
    }

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    engine.dispose()


def _general_preview_payload(**overrides):
    payload = {
        "date": "2026-05-20",
        "description": "Unicode preview Покупка ☕",
        "currency": "SEK",
        "splits": [
            {"account_id": "bank-guid", "amount": "-123.4500", "memo": "card memo"},
            {"account_id": "food-guid", "amount": "123.4500", "memo": "расход"},
        ],
    }
    payload.update(overrides)
    return payload


def _fake_live_source_fingerprint(book: Book, settings: Settings) -> str:
    return source_fingerprint_for_book(
        book,
        settings,
        source_identity=FakeLiveSourceEvidence.identity,
        versions=FakeLiveSourceEvidence.versions,
        source_base_currency=FakeLiveSourceEvidence.base_currency,
    )


def _fixture_book_path() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "test-book.gnucash.sqlite"


def _copy_real_disposable_book(tmp_path: Path, name: str = "synthetic-disposable-product.gnucash.sqlite") -> Path:
    book_dir = tmp_path / "books"
    book_dir.mkdir(exist_ok=True)
    target = book_dir / name
    shutil.copy2(_fixture_book_path(), target)
    target.chmod(0o600)
    return target


def _file_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _create_valid_generated_book(output: Path) -> Path:
    import piecash

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    book = piecash.create_book(currency="SEK", sqlite_file=str(output))
    try:
        currency = book.commodities[0]
        root = book.root_account
        assets = piecash.Account(name="Assets", type="ASSET", parent=root, commodity=currency)
        piecash.Account(name="Checking", type="BANK", parent=assets, commodity=currency)
        expenses = piecash.Account(name="Expenses", type="EXPENSE", parent=root, commodity=currency)
        piecash.Account(name="Food", type="EXPENSE", parent=expenses, commodity=currency)
        book.save()
    finally:
        book.close()

    reopened = piecash.open_book(str(output), readonly=True)
    try:
        assert str(getattr(reopened.default_currency, "mnemonic", "")) == "SEK"
        assert len(reopened.transactions) == 0
    finally:
        reopened.close()
    output.chmod(0o600)
    return output


def _copy_valid_generated_disposable_book(tmp_path: Path) -> tuple[Path, Path, str]:
    template = _create_valid_generated_book(
        tmp_path / "template" / "valid-generated-template.gnucash.sqlite"
    )
    template_hash = _file_sha256(template)
    target = tmp_path / "books" / "valid-generated-product.gnucash.sqlite"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, target)
    target.chmod(0o600)
    return template, target, template_hash


def _transaction_storage_counts(book_path: Path, transaction_id: str) -> dict[str, object]:
    import sqlite3

    with sqlite3.connect(book_path) as connection:
        row = connection.execute(
            "select count(*), min(currency_guid), max(currency_guid) from transactions where guid=?",
            (transaction_id,),
        ).fetchone()
        split_count = connection.execute(
            "select count(*) from splits where tx_guid=?",
            (transaction_id,),
        ).fetchone()[0]
    return {
        "transaction_count": row[0],
        "currency_guid_min": row[1],
        "currency_guid_max": row[2],
        "split_count": split_count,
    }


def _transaction_snapshot(book_path: Path, transaction_id: str) -> dict[str, object]:
    import piecash

    book = piecash.open_book(str(book_path), readonly=True)
    try:
        matches = [transaction for transaction in book.transactions if transaction.guid == transaction_id]
        assert len(matches) == 1
        transaction = matches[0]
        return {
            "guid": transaction.guid,
            "date": transaction.post_date.isoformat(),
            "description": transaction.description,
            "currency": str(getattr(transaction.currency, "mnemonic", "")),
            "currency_guid": str(getattr(transaction.currency, "guid", "")),
            "default_currency_guid": str(getattr(book.default_currency, "guid", "")),
            "splits": sorted(
                [
                    {
                        "account_id": split.account.guid,
                        "account_name": split.account.name,
                        "amount": str(split.value),
                        "quantity": str(split.quantity),
                        "memo": split.memo,
                        "currency": str(getattr(split.account.commodity, "mnemonic", "")),
                    }
                    for split in transaction.splits
                ],
                key=lambda item: item["account_name"],
            ),
        }
    finally:
        book.close()


def _real_book_account_ids(book_path: Path) -> dict[str, str]:
    import piecash

    book = piecash.open_book(str(book_path), readonly=True)
    try:
        return {str(account.name): str(account.guid) for account in book.accounts}
    finally:
        book.close()


def _real_transaction_count(book_path: Path) -> int:
    import piecash

    book = piecash.open_book(str(book_path), readonly=True)
    try:
        return len(book.transactions)
    finally:
        book.close()


def _real_product_payload(book_path: Path, *, description: str = "Real product CREATE proof") -> dict:
    account_ids = _real_book_account_ids(book_path)
    return _general_preview_payload(
        description=description,
        splits=[
            {"account_id": account_ids["Checking"], "amount": "-12.34", "memo": "bounded debit"},
            {"account_id": account_ids["Food"], "amount": "12.34", "memo": "bounded credit"},
        ],
    )


def _use_real_product_source(api_context, monkeypatch, book_path: Path, *, allowed_root: Path | None = None) -> Settings:
    import app.routers.transactions as transactions_router
    import app.services.transaction_create_policy as policy_module

    root = allowed_root or book_path.parent
    root.mkdir(parents=True, exist_ok=True)
    enabled_settings = api_context["settings"].model_copy(
        update={
            "gnucash_writes_enabled": True,
            "gnucash_book_allowed_roots": [str(root)],
        }
    )
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    monkeypatch.setattr(
        transactions_router,
        "inspect_transaction_create_source",
        policy_module.inspect_transaction_create_source,
    )
    monkeypatch.setattr(
        transactions_router,
        "open_transaction_create_source",
        policy_module.open_transaction_create_source,
    )
    canonical_path = str(book_path.resolve(strict=False))
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        book.uri_or_path = str(book_path)
        book.canonical_path = canonical_path
        book.canonical_path_hash = canonical_path_hash(canonical_path)
        book.base_currency = "SEK"
        book.transaction_create_enabled = True
        book.transaction_create_recovery_required = False
        session.commit()
    return enabled_settings


def _post_product_preview(api_context, payload: dict):
    response = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=payload,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _post_product_confirm(api_context, preview_json: dict, payload: dict):
    return api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers={
            **api_context["headers"]["editor"],
            "Idempotency-Key": preview_json["idempotency_key"],
        },
        json={"preview_token": preview_json["preview_token"], "transaction": payload},
    )


def test_default_writes_setting_remains_false():
    assert Settings().gnucash_writes_enabled is False


def test_issue59_metadata_migration_adds_book_fields_idempotency_table_and_is_restart_idempotent(tmp_path: Path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy-control.db'}", connect_args={"check_same_thread": False})
    with engine.begin() as conn:
        conn.execute(text("create table users (id integer primary key autoincrement, username varchar(128) not null unique, username_normalized varchar(64) not null, display_name varchar(256) not null, password_hash varchar(512) not null, is_admin boolean not null, is_enabled boolean not null default 1, auth_version integer not null default 1, created_at datetime not null, updated_at datetime not null)"))
        conn.execute(text("create table books (id integer primary key autoincrement, name varchar(256) not null, storage_type varchar(64) not null, uri_or_path varchar(1024) not null, canonical_path varchar(1024), canonical_path_hash varchar(64), base_currency varchar(16), is_default boolean not null, is_archived boolean not null, is_enabled boolean not null default 1, created_at datetime not null, updated_at datetime not null)"))
        conn.execute(text("create table user_book_access (user_id integer not null, book_id integer not null, role varchar(16) not null, primary key (user_id, book_id))"))
        conn.execute(text("create table audit_logs (id integer primary key autoincrement, user_id integer, book_id integer, action varchar(128) not null, payload_json text, created_at datetime not null)"))
        conn.execute(text("insert into books (id, name, storage_type, uri_or_path, canonical_path_hash, base_currency, is_default, is_archived, is_enabled, created_at, updated_at) values (1, 'Legacy', 'sqlite', '/missing.gnucash.sqlite', 'hash', 'SEK', 1, 0, 1, '2026-01-01 00:00:00.000000', '2026-01-01 00:00:00.000000')"))

    settings = BASE_SETTINGS.model_copy(update={"app_database_url": f"sqlite:///{tmp_path / 'legacy-control.db'}", "gnucash_book_allowed_roots": [str(tmp_path)]})
    run_app_metadata_migrations(engine, settings)
    run_app_metadata_migrations(engine, settings)

    inspector = inspect(engine)
    book_columns = {column["name"] for column in inspector.get_columns("books")}
    assert {"transaction_create_enabled", "transaction_create_generation", "transaction_create_recovery_required"}.issubset(book_columns)
    assert "transaction_create_idempotency" in inspector.get_table_names()
    indexes = {tuple(index["column_names"]) for index in inspector.get_indexes("transaction_create_idempotency")}
    assert ("book_id", "user_id", "key_hash") in indexes
    with engine.connect() as conn:
        row = conn.execute(text("select transaction_create_enabled, transaction_create_generation, transaction_create_recovery_required from books where id=1")).one()
        assert tuple(row) == (0, 1, 0)
        assert conn.execute(text("select count(*) from transaction_create_idempotency")).scalar_one() == 0


def test_admin_settings_route_is_admin_only_default_off_and_generation_invalidates(api_context, monkeypatch):
    import app.services.transaction_create_policy as policy_module

    class LiveEvidence:
        base_currency = "SEK"
        versions = {"Gnucash": 2030000}

    monkeypatch.setattr(policy_module, "inspect_transaction_create_source", lambda book, settings: LiveEvidence())

    client = api_context["client"]
    book_id = api_context["ids"]["book"]

    viewer_patch = client.patch(
        f"/books/{book_id}/transaction-create-settings",
        headers=api_context["headers"]["viewer"],
        json={"enabled": True},
    )
    assert viewer_patch.status_code == 403

    default_get = client.get(
        f"/books/{book_id}/transaction-create-settings",
        headers=api_context["headers"]["admin"],
    )
    assert default_get.status_code == 200
    assert default_get.json()["enabled"] is False
    assert default_get.json()["generation"] == 1
    assert default_get.json()["recovery_required"] is False

    blocked = client.patch(
        f"/books/{book_id}/transaction-create-settings",
        headers=api_context["headers"]["admin"],
        json={"enabled": True},
    )
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "CREATE_DEPLOYMENT_DISABLED"

    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    enabled = client.patch(
        f"/books/{book_id}/transaction-create-settings",
        headers=api_context["headers"]["admin"],
        json={"enabled": True},
    )
    assert enabled.status_code == 200
    assert enabled.json()["enabled"] is True
    assert enabled.json()["generation"] == 2

    disabled = client.patch(
        f"/books/{book_id}/transaction-create-settings",
        headers=api_context["headers"]["admin"],
        json={"enabled": False},
    )
    assert disabled.status_code == 200
    assert disabled.json()["enabled"] is False
    assert disabled.json()["generation"] == 3

    with api_context["session_factory"]() as session:
        audit = session.query(AuditLog).filter(AuditLog.action == "book.transaction_create.setting_changed").order_by(AuditLog.id.desc()).first()
        payload = json.loads(audit.payload_json)
        assert payload["old_enabled"] is True
        assert payload["new_enabled"] is False
        assert payload["create_generation"] == 3
        assert "uri_or_path" not in audit.payload_json
        assert "not-opened" not in audit.payload_json


def test_effective_policy_requires_explicit_editor_owner_access_and_book_enablement(api_context):
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        admin = session.query(User).filter(User.username == "admin").one()
        editor = session.query(User).filter(User.username == "editor").one()
        viewer = session.query(User).filter(User.username == "viewer").one()
        enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})

        assert evaluate_transaction_create_policy(book, admin, session, enabled_settings).confirm_allowed is False
        assert "CREATE_PERMISSION_DENIED" in evaluate_transaction_create_policy(book, admin, session, enabled_settings).blocked_codes
        assert evaluate_transaction_create_policy(book, viewer, session, enabled_settings).confirm_allowed is False

        book.transaction_create_enabled = True
        session.commit()
        assert evaluate_transaction_create_policy(book, editor, session, enabled_settings).confirm_allowed is True

        book.transaction_create_recovery_required = True
        session.commit()
        blocked = evaluate_transaction_create_policy(book, editor, session, enabled_settings)
        assert blocked.confirm_allowed is False
        assert "CREATE_RECOVERY_REQUIRED" in blocked.blocked_codes


def test_general_preview_returns_signed_token_policy_and_no_write_helper_reachability(api_context, monkeypatch):
    import app.routers.transactions as transactions_router
    import app.services.gnucash_write as gnucash_write_module

    def fail_if_called(*args, **kwargs):
        raise AssertionError("product preview must not reach write, backup, or lock helpers")

    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadService())
    monkeypatch.setattr(transactions_router, "_write_service_for", fail_if_called)
    monkeypatch.setattr(transactions_router, "_audit_log", fail_if_called)
    monkeypatch.setattr(gnucash_write_module, "create_book_backup", fail_if_called)
    monkeypatch.setattr(gnucash_write_module.write_lock_service, "acquire", fail_if_called)

    client = api_context["client"]
    book_id = api_context["ids"]["book"]
    response = client.post(
        f"/books/{book_id}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=_general_preview_payload(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["preview_only"] is True
    assert data["confirm_allowed"] is False
    assert data["create_generation"] == 1
    assert data["preview_token"].startswith("pt1.")
    assert data["idempotency_key"]
    assert data["expires_at"]
    assert data["splits"][0]["index"] == 0
    assert data["splits"][0]["account"]["full_name"] == "Assets:Bank:Checking"
    for legacy_field in ("amount", "memo", "debit_account", "credit_account", "writes_enabled_required_for_create"):
        assert legacy_field not in data
    token_text = data["preview_token"]
    for forbidden in ("Unicode preview", "Покупка", "bank-guid", "food-guid", "123.4500", "card memo", "расход"):
        assert forbidden not in token_text

    viewer_response = client.post(
        f"/books/{book_id}/transactions/create-preview",
        headers=api_context["headers"]["viewer"],
        json=_general_preview_payload(),
    )
    assert viewer_response.status_code == 403
    assert viewer_response.json()["error"]["code"] == "CREATE_PERMISSION_DENIED"
    with api_context["session_factory"]() as session:
        assert session.query(AuditLog).filter(AuditLog.action == "transaction.create.preview").count() == 0
        assert session.query(TransactionCreateIdempotency).count() == 0


@pytest.mark.parametrize(
    ("account", "payload", "expected_code"),
    [
        (
            FakeAccount("bank-guid", "Checking", "Assets:Bank:Checking", "BANK", currency="XXX"),
            _general_preview_payload(),
            "UNSUPPORTED_COMMODITY",
        ),
        (
            FakeAccount(
                "bank-guid",
                "Checking",
                "Assets:Bank:Checking",
                "BANK",
                currency="SEK",
                commodity_namespace="NASDAQ",
            ),
            _general_preview_payload(),
            "UNSUPPORTED_COMMODITY",
        ),
        (
            FakeAccount(
                "bank-guid",
                "Checking",
                "Assets:Bank:Checking",
                "BANK",
                currency="SEK",
                commodity_fraction=100,
            ),
            _general_preview_payload(
                splits=[
                    {"account_id": "bank-guid", "amount": "-0.001", "memo": "too fine"},
                    {"account_id": "food-guid", "amount": "0.001", "memo": "too fine"},
                ]
            ),
            "INVALID_DECIMAL",
        ),
    ],
)
def test_general_preview_rejects_unknown_namespace_and_fraction_rounding(api_context, monkeypatch, account, payload, expected_code):
    import app.routers.transactions as transactions_router

    class CommodityReadService:
        def list_accounts(self):
            return [
                account,
                FakeAccount("food-guid", "Food", "Expenses:Food", "EXPENSE"),
            ]

        def list_accounts_by_ids(self, account_ids):
            requested = set(account_ids)
            return [account for account in self.list_accounts() if account.id in requested]

    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: CommodityReadService())

    response = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=payload,
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == expected_code


def test_preview_token_hashes_are_canonical_unicode_bound_and_tamper_expiry_safe(api_context):
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    request_a = _general_preview_payload(description="  Café Покупка  ")
    request_b = {
        "currency": "SEK",
        "description": "Café Покупка",
        "date": "2026-05-20",
        "splits": [
            {"memo": "card memo", "amount": "-123.4500", "account_id": "bank-guid"},
            {"memo": "расход", "account_id": "food-guid", "amount": "123.4500"},
        ],
    }
    hash_a = canonical_transaction_create_request_hash(request_a)
    hash_b = canonical_transaction_create_request_hash(request_b)
    assert hash_a == hash_b

    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        user = session.query(User).filter(User.username == "editor").one()
        key_hash = hash_idempotency_key("raw-idempotency-key", api_context["settings"])
        source_fp = source_fingerprint_for_book(book, api_context["settings"])
        token = issue_preview_token(
            settings=api_context["settings"],
            user=user,
            book=book,
            request_hash=hash_a,
            idempotency_key_hash=key_hash,
            source_fingerprint=source_fp,
            now=now,
            jti="0123456789abcdef0123456789abcdef",
        )

    verified = verify_preview_token(
        token,
        api_context["settings"],
        expected_user_id=api_context["ids"]["editor"],
        expected_auth_version=1,
        expected_book_id=api_context["ids"]["book"],
        expected_generation=1,
        expected_request_hash=hash_a,
        expected_idempotency_key_hash=key_hash,
        expected_source_fingerprint=source_fp,
        now=now + timedelta(seconds=30),
    )
    assert verified.valid is True
    assert verified.payload["request_hash"] == hash_a

    assert verify_preview_token(token + "x", api_context["settings"], now=now).code == "PREVIEW_TOKEN_INVALID"
    assert verify_preview_token(token, api_context["settings"], expected_request_hash="changed", now=now).code == "PREVIEW_PAYLOAD_MISMATCH"
    assert verify_preview_token(token, api_context["settings"], expected_idempotency_key_hash="changed", now=now).code == "IDEMPOTENCY_PAYLOAD_MISMATCH"
    assert verify_preview_token(token, api_context["settings"], expected_source_fingerprint="changed", now=now).code == "PREVIEW_STALE"
    assert verify_preview_token(token, api_context["settings"], expected_generation=2, now=now).code == "PREVIEW_STALE"
    assert verify_preview_token(token, api_context["settings"], now=now + timedelta(seconds=631)).code == "PREVIEW_TOKEN_EXPIRED"


def test_source_fingerprint_binds_live_identity_versions_and_registered_base_currency(api_context):
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        identity = SourceIdentity(
            canonical_path="/redacted/synthetic.gnucash.sqlite",
            canonical_path_hash="live-canonical-hash",
            st_dev=101,
            st_ino=202,
            st_size=303,
            st_mtime_ns=404,
        )
        fp_a = source_fingerprint_for_book(
            book,
            api_context["settings"],
            source_identity=identity,
            versions={"Gnucash": 2030000, "Gnucash-Resave": 19920},
            source_base_currency="SEK",
        )
        fp_b = source_fingerprint_for_book(
            book,
            api_context["settings"],
            source_identity=SourceIdentity(
                canonical_path=identity.canonical_path,
                canonical_path_hash=identity.canonical_path_hash,
                st_dev=identity.st_dev,
                st_ino=identity.st_ino,
                st_size=identity.st_size + 1,
                st_mtime_ns=identity.st_mtime_ns,
            ),
            versions={"Gnucash": 2030000, "Gnucash-Resave": 19920},
            source_base_currency="SEK",
        )
        fp_c = source_fingerprint_for_book(
            book,
            api_context["settings"],
            source_identity=identity,
            versions={"Gnucash": 2030001, "Gnucash-Resave": 19920},
            source_base_currency="SEK",
        )
        fp_d = source_fingerprint_for_book(
            book,
            api_context["settings"],
            source_identity=identity,
            versions={"Gnucash": 2030000, "Gnucash-Resave": 19920},
            source_base_currency="USD",
        )

    assert len({fp_a, fp_b, fp_c, fp_d}) == 4


def test_idempotency_state_machine_uniqueness_replay_mismatch_in_progress_indeterminate_and_pruning(api_context):
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    with api_context["session_factory"]() as session:
        service = TransactionCreateIdempotencyService(session, api_context["settings"])
        first = service.reserve(
            book_id=api_context["ids"]["book"],
            user_id=api_context["ids"]["editor"],
            raw_key="same-key",
            request_hash="request-a",
            token_jti_hash="token-a",
            now=now,
        )
        assert first.status == "reserved"
        assert len(first.record.planned_transaction_guid) == 32

        active = service.reserve(
            book_id=api_context["ids"]["book"],
            user_id=api_context["ids"]["editor"],
            raw_key="same-key",
            request_hash="request-a",
            token_jti_hash="token-a",
            now=now,
        )
        assert active.status == "in_progress"

        stale = service.reserve(
            book_id=api_context["ids"]["book"],
            user_id=api_context["ids"]["editor"],
            raw_key="same-key",
            request_hash="request-a",
            token_jti_hash="token-a",
            now=now + timedelta(seconds=IN_PROGRESS_STALE_AFTER_SECONDS + 1),
        )
        assert stale.status == "recovery_required"
        assert stale.record.state == "indeterminate"
        assert stale.record.safe_error_code == "CREATE_RECOVERY_REQUIRED"
        assert session.get(Book, api_context["ids"]["book"]).transaction_create_recovery_required is True

        session.get(Book, api_context["ids"]["book"]).transaction_create_recovery_required = False
        first.record.state = "in_progress"
        first.record.safe_error_code = None
        first.record.updated_at = now.replace(tzinfo=None)
        session.commit()

        mismatch = service.reserve(
            book_id=api_context["ids"]["book"],
            user_id=api_context["ids"]["editor"],
            raw_key="same-key",
            request_hash="request-b",
            token_jti_hash="token-a",
            now=now,
        )
        assert mismatch.status == "payload_mismatch"

        service.mark_succeeded(
            first.record,
            {
                "status": "created",
                "transaction_id": "a" * 32,
                "audit_ref": "aud_abcdef123456",
                "backup_ref": "bkp_abcdef123456",
                "readback": {
                    "verified": True,
                    "transaction_present": True,
                    "split_count": 2,
                    "balanced": True,
                    "currency_consistent": True,
                },
                "links": {
                    "transaction": "/books/1/transactions/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "explorer": "/books/1/transactions",
                },
            },
            now=now,
        )
        replay = service.reserve(
            book_id=api_context["ids"]["book"],
            user_id=api_context["ids"]["editor"],
            raw_key="same-key",
            request_hash="request-a",
            token_jti_hash="token-a",
            now=now,
        )
        assert replay.status == "already_succeeded"
        assert replay.safe_result["status"] == "created"

        unsafe = service.reserve(
            book_id=api_context["ids"]["book"],
            user_id=api_context["ids"]["editor"],
            raw_key="unsafe-key",
            request_hash="request-a",
            token_jti_hash="token-unsafe",
            now=now,
        )
        with pytest.raises(ValueError):
            service.mark_succeeded(unsafe.record, {"status": "created", "backup_path": "/private/book.gnucash"}, now=now)

        unknown = service.reserve(
            book_id=api_context["ids"]["book"],
            user_id=api_context["ids"]["editor"],
            raw_key="unknown-key",
            request_hash="request-a",
            token_jti_hash="token-b",
            now=now,
        )
        service.mark_indeterminate(unknown.record, "CREATE_RESULT_UNKNOWN", now=now)
        assert service.reserve(
            book_id=api_context["ids"]["book"],
            user_id=api_context["ids"]["editor"],
            raw_key="unknown-key",
            request_hash="request-a",
            token_jti_hash="token-b",
            now=now,
        ).status == "recovery_required"

        for index in range(105):
            row = TransactionCreateIdempotency(
                user_id=api_context["ids"]["editor"],
                book_id=api_context["ids"]["book"],
                key_hash=f"old-{index}",
                request_hash="request-old",
                token_jti_hash="token-old",
                planned_transaction_guid=f"{index:032x}",
                state="succeeded",
                safe_result_json="{}",
                created_at=now - timedelta(days=40, seconds=200 - index),
                updated_at=now - timedelta(days=40, seconds=200 - index),
                expires_at=now - timedelta(days=1),
            )
            session.add(row)
        session.commit()

        deleted = service.prune(book_id=api_context["ids"]["book"], now=now)
        assert deleted == 100
        remaining_old = session.query(TransactionCreateIdempotency).filter(TransactionCreateIdempotency.key_hash.like("old-%")).count()
        assert remaining_old == 5
        assert session.query(TransactionCreateIdempotency).filter(TransactionCreateIdempotency.state == "indeterminate").count() == 1


def test_control_plane_audit_serializer_allowlist_redacts_forbidden_values():
    payload = serialize_transaction_create_audit_payload(
        {
            "result": "failed",
            "error_code": "PREVIEW_STALE",
            "request_hash_prefix": "abcdef12",
            "split_count": 2,
            "currency": "SEK",
            "create_generation": 4,
            "old_enabled": False,
            "new_enabled": True,
            "backup_artifact_ref": "bkp_safe_ref",
            "transaction_ref": "tx_safe_ref",
            "recovery_ref": "rec/../../private",
            "event_ref": "evt/../../private",
            "backup_path": "/private/source/book.gnucash.sqlite",
            "account_id": "bank-guid",
            "amount": "123.45",
            "description": "Secret description",
            "memo": "Secret memo",
            "full_guid": "0123456789abcdef0123456789abcdef",
            "raw_exception": "Traceback with /private/source/book.gnucash.sqlite",
        }
    )
    assert set(payload).issubset(
        {
            "schema_version",
            "event_ref",
            "result",
            "error_code",
            "retryable",
            "request_hash_prefix",
            "token_jti_hash_prefix",
            "idempotency_key_hash_prefix",
            "split_count",
            "currency",
            "create_generation",
            "duplicate",
            "stale",
            "lock_acquired",
            "backup_present",
            "backup_artifact_ref",
            "transaction_ref",
            "readback_verified",
            "recovery_ref",
            "duration_bucket_ms",
            "old_enabled",
            "new_enabled",
        }
    )
    serialized = json.dumps(payload, ensure_ascii=False)
    for forbidden in ("/private", "book.gnucash", "bank-guid", "123.45", "Secret description", "Secret memo", "Traceback", "../../", "0123456789abcdef0123456789abcdef"):
        assert forbidden not in serialized


def test_admin_enablement_requires_live_source_base_currency_match(api_context, monkeypatch):
    import app.services.transaction_create_policy as policy_module

    class LiveEvidence:
        base_currency = "SEK"
        versions = {"Gnucash": 2030000}

    monkeypatch.setattr(policy_module, "inspect_transaction_create_source", lambda book, settings: LiveEvidence())
    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        book.base_currency = "USD"
        session.commit()

    response = api_context["client"].patch(
        f"/books/{api_context['ids']['book']}/transaction-create-settings",
        headers=api_context["headers"]["admin"],
        json={"enabled": True},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "COMMODITY_MISMATCH"


def test_product_confirm_endpoint_uses_preview_token_idempotency_and_safe_replay(api_context, monkeypatch):
    import app.routers.transactions as transactions_router

    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadService())
    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        book.transaction_create_enabled = True
        session.commit()

    preview = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=_general_preview_payload(),
    )
    assert preview.status_code == 200
    preview_json = preview.json()
    assert preview_json["confirm_allowed"] is True
    product_calls = []

    def fake_product_execute(**kwargs):
        product_calls.append(kwargs)
        guid = kwargs["planned_transaction_guid"]
        return {
            "status": "created",
            "transaction_id": guid,
            "audit_ref": "aud_abcdef123456",
            "backup_ref": "bkp_abcdef123456",
            "readback": {
                "verified": True,
                "transaction_present": True,
                "split_count": 2,
                "balanced": True,
                "currency_consistent": True,
            },
            "links": {
                "transaction": f"/books/{api_context['ids']['book']}/transactions/{guid}",
                "explorer": f"/books/{api_context['ids']['book']}/transactions",
            },
        }

    monkeypatch.setattr(transactions_router, "_execute_product_transaction_create", fake_product_execute, raising=False)

    confirm_body = {"preview_token": preview_json["preview_token"], "transaction": _general_preview_payload()}
    confirm_headers = {
        **api_context["headers"]["editor"],
        "Idempotency-Key": preview_json["idempotency_key"],
    }
    first = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers=confirm_headers,
        json=confirm_body,
    )
    replay = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers=confirm_headers,
        json=confirm_body,
    )

    assert first.status_code == 201
    assert first.json()["status"] == "created"
    assert replay.status_code == 200
    assert replay.json()["status"] == "already_created"
    assert replay.json()["transaction_id"] == first.json()["transaction_id"]
    assert len(product_calls) == 1
    with api_context["session_factory"]() as session:
        record = session.query(TransactionCreateIdempotency).one()
        assert record.state == "succeeded"
        assert record.safe_result_json is not None
        payloads = [json.loads(row.payload_json) for row in session.query(AuditLog).filter(AuditLog.action == "transaction.create.confirm").all()]
        assert {payload["result"] for payload in payloads} == {"started", "success", "already_created"}
        assert all("/" not in json.dumps(payload) for payload in payloads)


def test_product_confirm_allows_identical_succeeded_replay_after_preview_expiry(api_context, monkeypatch):
    import app.routers.transactions as transactions_router

    now = datetime.now(timezone.utc)
    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    payload = _general_preview_payload()
    idempotency_key = "expired-success-key"
    token_jti = "abcdefabcdefabcdefabcdefabcdefab"

    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        user = session.query(User).filter(User.username == "editor").one()
        book.transaction_create_enabled = True
        session.commit()
        request_hash = canonical_transaction_create_request_hash(payload)
        key_hash = hash_idempotency_key(idempotency_key, enabled_settings)
        token = issue_preview_token(
            settings=enabled_settings,
            user=user,
            book=book,
            request_hash=request_hash,
            idempotency_key_hash=key_hash,
            source_fingerprint=_fake_live_source_fingerprint(book, enabled_settings),
            now=now - timedelta(seconds=700),
            jti=token_jti,
        )
        idempotency = TransactionCreateIdempotencyService(session, enabled_settings)
        reservation = idempotency.reserve(
            book_id=book.id,
            user_id=user.id,
            raw_key=idempotency_key,
            request_hash=request_hash,
            token_jti_hash=hash_token_jti(token_jti, enabled_settings),
            now=now - timedelta(seconds=690),
        )
        idempotency.mark_succeeded(
            reservation.record,
            {
                "status": "created",
                "transaction_id": "b" * 32,
                "audit_ref": "aud_abcdef123456",
                "backup_ref": "bkp_abcdef123456",
                "readback": {
                    "verified": True,
                    "transaction_present": True,
                    "split_count": 2,
                    "balanced": True,
                    "currency_consistent": True,
                },
                "links": {
                    "transaction": f"/books/{book.id}/transactions/{'b' * 32}",
                    "explorer": f"/books/{book.id}/transactions",
                },
            },
            now=now - timedelta(seconds=680),
        )

    monkeypatch.setattr(transactions_router, "inspect_transaction_create_source", lambda book, settings: None)
    response = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers={
            **api_context["headers"]["editor"],
            "Idempotency-Key": idempotency_key,
        },
        json={"preview_token": token, "transaction": payload},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "already_created"
    assert response.json()["transaction_id"] == "b" * 32


def test_product_confirm_lock_busy_returns_book_write_busy_retry_after(api_context, monkeypatch):
    import app.routers.transactions as transactions_router

    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadService())
    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        book.transaction_create_enabled = True
        session.commit()

    preview = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=_general_preview_payload(),
    )
    assert preview.status_code == 200
    preview_json = preview.json()
    monkeypatch.setattr(
        transactions_router,
        "_execute_product_transaction_create",
        lambda **kwargs: (_ for _ in ()).throw(WriteLockError("book:1")),
        raising=False,
    )

    response = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers={
            **api_context["headers"]["editor"],
            "Idempotency-Key": preview_json["idempotency_key"],
        },
        json={"preview_token": preview_json["preview_token"], "transaction": _general_preview_payload()},
    )

    assert response.status_code == 409
    assert response.headers["Retry-After"] == "2"
    assert response.json()["error"]["code"] == "BOOK_WRITE_BUSY"


def test_product_create_error_status_and_backup_refs_are_contract_shaped():
    import app.routers.transactions as transactions_router

    backup_ref = transactions_router._product_backup_ref("/private/source/book.gnucash.sqlite")

    assert transactions_router._product_create_error_status("PREVIEW_PAYLOAD_MISMATCH") == 409
    assert backup_ref is not None
    assert backup_ref.startswith("bkp_")
    assert "/" not in backup_ref
    assert serialize_transaction_create_audit_payload({"backup_artifact_ref": backup_ref})[
        "backup_artifact_ref"
    ] == backup_ref


def test_product_confirm_recomputes_source_fingerprint_before_backup_or_write(api_context, monkeypatch):
    import app.routers.transactions as transactions_router

    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadService())
    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        book.transaction_create_enabled = True
        session.commit()

    preview = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=_general_preview_payload(),
    )
    assert preview.status_code == 200
    preview_json = preview.json()
    monkeypatch.setattr(
        transactions_router,
        "_live_source_fingerprint_for_book",
        lambda book, settings, **kwargs: "changed-live-source",
        raising=False,
    )

    def fail_if_write_reached(**kwargs):
        raise AssertionError("stale preview must stop before backup/write")

    monkeypatch.setattr(transactions_router, "_execute_product_transaction_create", fail_if_write_reached, raising=False)
    response = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers={
            **api_context["headers"]["editor"],
            "Idempotency-Key": preview_json["idempotency_key"],
        },
        json={"preview_token": preview_json["preview_token"], "transaction": _general_preview_payload()},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PREVIEW_STALE"


@pytest.mark.parametrize(
    "mode",
    [
        "missing_source",
        "replaced_inode",
        "symlink_change",
        "permission_error",
        "unsupported_file",
        "inspection_exception",
        "cached_metadata_only",
    ],
)
def test_live_source_fingerprint_required_for_confirm_fails_closed_without_cached_fallback(
    api_context,
    monkeypatch,
    mode,
):
    import app.routers.transactions as transactions_router

    def unavailable(book, settings):
        if mode == "inspection_exception":
            raise RuntimeError("raw /private/source exception must be redacted")
        return None

    monkeypatch.setattr(transactions_router, "inspect_transaction_create_source", unavailable)
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()

        cached_display_fingerprint = transactions_router._live_source_fingerprint_for_book(
            book,
            api_context["settings"],
            require_fresh=False,
        )
        assert cached_display_fingerprint == source_fingerprint_for_book(book, api_context["settings"])
        with pytest.raises(transactions_router.TransactionCreateHTTPError) as exc_info:
            transactions_router._live_source_fingerprint_for_book(
                book,
                api_context["settings"],
                require_fresh=True,
            )

    envelope = exc_info.value.envelope()
    encoded = json.dumps(envelope)
    assert exc_info.value.code == "PREVIEW_STALE"
    assert envelope["error"]["retryable"] is True
    assert "/private" not in encoded
    assert "raw" not in encoded.lower()


def test_product_confirm_missing_live_source_rejects_before_idempotency_backup_or_write(
    api_context,
    monkeypatch,
):
    import app.routers.transactions as transactions_router

    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadService())
    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        book.transaction_create_enabled = True
        session.commit()

    preview = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=_general_preview_payload(),
    )
    assert preview.status_code == 200
    preview_json = preview.json()

    monkeypatch.setattr(transactions_router, "inspect_transaction_create_source", lambda book, settings: None)
    monkeypatch.setattr(
        transactions_router,
        "_execute_product_transaction_create",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("write path must not run")),
        raising=False,
    )
    response = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers={
            **api_context["headers"]["editor"],
            "Idempotency-Key": preview_json["idempotency_key"],
        },
        json={"preview_token": preview_json["preview_token"], "transaction": _general_preview_payload()},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PREVIEW_STALE"
    assert response.json()["error"]["retryable"] is True
    encoded = json.dumps(response.json())
    assert "/synthetic" not in encoded
    with api_context["session_factory"]() as session:
        assert session.query(TransactionCreateIdempotency).count() == 0
        assert session.query(AuditLog).filter(AuditLog.action == "transaction.create.confirm").count() == 0


def test_product_confirm_holds_stable_book_lock_through_readback_idempotency_and_audit(
    api_context,
    monkeypatch,
):
    import app.routers.transactions as transactions_router

    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadService())
    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        book.transaction_create_enabled = True
        session.commit()

    preview = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=_general_preview_payload(),
    )
    assert preview.status_code == 200
    preview_json = preview.json()
    lock_key = f"book:{api_context['ids']['book']}"
    observed: list[str] = []

    def assert_lock_held(label: str) -> None:
        assert transactions_router.write_lock_service.inspect(lock_key).is_active is True
        observed.append(label)

    def fake_product_execute(**kwargs):
        assert_lock_held("execute_through_readback")
        guid = kwargs["planned_transaction_guid"]
        return {
            "status": "created",
            "transaction_id": guid,
            "backup_ref": "bkp_abcdef123456",
            "readback": {
                "verified": True,
                "transaction_present": True,
                "split_count": 2,
                "balanced": True,
                "currency_consistent": True,
                "account_balance_deltas_verified": True,
            },
            "links": {
                "transaction": f"/books/{api_context['ids']['book']}/transactions/{guid}",
                "explorer": f"/books/{api_context['ids']['book']}/transactions",
            },
        }

    original_mark_succeeded = TransactionCreateIdempotencyService.mark_succeeded

    def spy_mark_succeeded(self, record, safe_result, **kwargs):
        assert_lock_held("terminal_idempotency")
        return original_mark_succeeded(self, record, safe_result, **kwargs)

    original_audit = transactions_router._audit_product_transaction_create_confirm

    def spy_audit(session, **kwargs):
        if kwargs.get("result") in {"started", "success"}:
            assert_lock_held(f"audit_{kwargs['result']}")
        return original_audit(session, **kwargs)

    monkeypatch.setattr(transactions_router, "_execute_product_transaction_create", fake_product_execute, raising=False)
    monkeypatch.setattr(TransactionCreateIdempotencyService, "mark_succeeded", spy_mark_succeeded)
    monkeypatch.setattr(transactions_router, "_audit_product_transaction_create_confirm", spy_audit)

    response = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers={
            **api_context["headers"]["editor"],
            "Idempotency-Key": preview_json["idempotency_key"],
        },
        json={"preview_token": preview_json["preview_token"], "transaction": _general_preview_payload()},
    )

    assert response.status_code == 201
    assert observed == [
        "audit_started",
        "execute_through_readback",
        "terminal_idempotency",
        "audit_success",
    ]
    assert transactions_router.write_lock_service.inspect(lock_key).is_active is False


def test_backup_failed_is_terminal_non_retryable_and_requires_new_key(api_context, monkeypatch):
    import app.routers.transactions as transactions_router
    from app.services.gnucash_write import GnuCashWriteError

    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadService())
    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        book.transaction_create_enabled = True
        session.commit()

    preview = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=_general_preview_payload(),
    )
    assert preview.status_code == 200
    preview_json = preview.json()
    calls = []

    def fail_backup(**kwargs):
        calls.append(kwargs)
        raise GnuCashWriteError("Backup failed: /private/source/book.gnucash.sqlite")

    monkeypatch.setattr(transactions_router, "_execute_product_transaction_create", fail_backup, raising=False)
    headers = {
        **api_context["headers"]["editor"],
        "Idempotency-Key": preview_json["idempotency_key"],
    }
    body = {"preview_token": preview_json["preview_token"], "transaction": _general_preview_payload()}
    first = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers=headers,
        json=body,
    )
    second = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions",
        headers=headers,
        json=body,
    )

    assert first.status_code == 503
    assert first.json()["error"]["code"] == "BACKUP_FAILED"
    assert first.json()["error"]["retryable"] is False
    assert second.status_code == 503
    assert second.json()["error"]["code"] == "BACKUP_FAILED"
    assert second.json()["error"]["retryable"] is False
    assert len(calls) == 1
    encoded = json.dumps({"first": first.json(), "second": second.json()})
    assert "/private" not in encoded
    with api_context["session_factory"]() as session:
        record = session.query(TransactionCreateIdempotency).one()
        assert record.state == "rejected"
        assert record.safe_error_code == "BACKUP_FAILED"
        assert record.safe_result_json is None


def test_verified_backup_retention_prunes_only_successful_verified_candidates(tmp_path: Path):
    import hashlib
    import os

    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)

    def write_verified(name: str, age_days: int, order: int, *, corrupt: bool = False) -> Path:
        path = backup_dir / name
        payload = f"verified-{name}".encode("utf-8")
        path.write_bytes(payload)
        timestamp = (now - timedelta(days=age_days, seconds=order)).timestamp()
        created_at = now - timedelta(days=age_days, seconds=order)
        os.utime(path, (timestamp, timestamp))
        digest = hashlib.sha256(payload).hexdigest()
        marker = backup_module._verified_marker_path(path)
        marker.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "verified",
                    "backup_name": path.name,
                    "size_bytes": path.stat().st_size + (1 if corrupt else 0),
                    "sha256": digest,
                    "created_at": created_at.isoformat(),
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        os.utime(marker, (timestamp, timestamp))
        return path

    valid = [write_verified(f"valid_{index:02d}.gnucash.sqlite", 1, index) for index in range(51)]
    current = valid[-1]
    old = write_verified("old_31_days.gnucash.sqlite", 31, 0)
    corrupt = write_verified("corrupt.gnucash.sqlite", 31, 1, corrupt=True)
    unknown = backup_dir / "unknown-artifact.gnucash.sqlite"
    unknown.write_bytes(b"unknown")
    symlink_target = backup_dir / "symlink-target.gnucash.sqlite"
    symlink_target.write_bytes(b"target")
    symlink = backup_dir / "symlink-artifact.gnucash.sqlite"
    symlink.symlink_to(symlink_target)

    deleted = backup_module.prune_verified_book_backups(
        backup_dir,
        current_backup=current,
        now=now,
    )

    assert deleted >= 2
    assert current.exists()
    assert not old.exists()
    assert sum(path.exists() for path in valid) <= 50
    assert corrupt.exists()
    assert unknown.exists()
    assert symlink.is_symlink()
    assert symlink_target.exists()


def test_verified_backup_prune_failure_does_not_convert_successful_backup_to_failure(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module

    book_dir = tmp_path / "books"
    book_dir.mkdir()
    source = book_dir / "synthetic-disposable.gnucash.sqlite"
    source.write_bytes(b"SQLite format 3\x00synthetic backup payload")
    monkeypatch.setattr(
        backup_module,
        "prune_verified_book_backups",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("prune failed /private")),
    )

    backup_path = Path(backup_module.create_book_backup({"uri_or_path": str(source)}))

    assert backup_path.exists()
    assert backup_path.read_bytes() == source.read_bytes()
    assert backup_module._verified_marker_path(backup_path).exists()


def _write_test_verified_backup(backup_module, backup_dir: Path, name: str, payload: bytes, created_at: datetime) -> Path:
    import hashlib

    path = backup_dir / name
    path.write_bytes(payload)
    marker = backup_module._verified_marker_path(path)
    marker.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "status": "verified",
                "backup_name": path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "created_at": created_at.isoformat(),
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def _backup_tree_files(backup_dir: Path) -> list[Path]:
    return sorted(path for path in backup_dir.rglob("*") if path.is_file())


def _test_retention_record(backup_module, backup_dir: Path, name: str, payload: bytes):
    backup_path = _write_test_verified_backup(
        backup_module,
        backup_dir,
        name,
        payload,
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    inspection = backup_module._RetentionInspection()
    candidate = [item for item in backup_module._verified_backup_candidates(backup_dir.resolve(), inspection) if item.name == backup_path.name][0]
    marker_quarantine = backup_module._unique_quarantine_path(
        candidate.marker_path,
        backup_dir.resolve(),
        candidate.marker_st_dev,
        candidate.marker_st_ino,
    )
    backup_quarantine = backup_module._unique_quarantine_path(
        candidate.path,
        backup_dir.resolve(),
        candidate.st_dev,
        candidate.st_ino,
    )
    return backup_module._retention_record_for_candidate(candidate, backup_quarantine, marker_quarantine, "planned")


def test_verified_backup_retention_state_is_private_checksummed_and_tamper_fails_closed(tmp_path: Path):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    record = _test_retention_record(backup_module, backup_dir, "state-secure.gnucash.sqlite", b"state secure")

    backup_module._upsert_retention_state_record(backup_dir.resolve(), record)

    state_dir = backup_module._retention_state_dir(backup_dir.resolve())
    assert state_dir is not None
    state_file = state_dir / backup_module.VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME
    assert stat.S_IMODE(os.lstat(state_dir).st_mode) == 0o700
    assert stat.S_IMODE(os.lstat(state_file).st_mode) == 0o600
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    assert payload["checksum"] != "0" * 64
    assert len(payload["checksum"]) == 64

    payload["records"][0]["backup"]["st_size"] += 1
    state_file.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    tampered_bytes = state_file.read_bytes()
    inspection = backup_module._RetentionInspection()

    assert backup_module._load_retention_state_records(backup_dir.resolve(), inspection) == []
    assert inspection.skipped_reason == "retention_state_invalid"
    with pytest.raises(OSError):
        backup_module._upsert_retention_state_record(backup_dir.resolve(), record)
    assert state_file.read_bytes() == tampered_bytes


def test_verified_backup_retention_state_rejects_symlink_and_nonprivate_state_dir(tmp_path: Path):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir(mode=0o755)
    record = _test_retention_record(backup_module, backup_dir, "state-unsafe.gnucash.sqlite", b"state unsafe")
    state_dir = backup_dir / backup_module.VERIFIED_BACKUP_RETENTION_STATE_DIR_NAME
    state_dir.chmod(0o755)
    parent_mode_before = stat.S_IMODE(os.lstat(backup_dir).st_mode)

    with pytest.raises(OSError):
        backup_module._upsert_retention_state_record(backup_dir.resolve(), record)

    assert stat.S_IMODE(os.lstat(state_dir).st_mode) == 0o755
    assert stat.S_IMODE(os.lstat(backup_dir).st_mode) == parent_mode_before
    assert not (state_dir / backup_module.VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME).exists()

    state_dir.chmod(0o700)
    sentinel = tmp_path / "outside-sentinel"
    sentinel.write_bytes(b"outside unchanged")
    state_symlink = state_dir / backup_module.VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME
    state_symlink.symlink_to(sentinel)
    with pytest.raises(OSError):
        backup_module._upsert_retention_state_record(backup_dir.resolve(), record)
    assert state_symlink.is_symlink()
    assert sentinel.read_bytes() == b"outside unchanged"


def test_verified_backup_retention_state_preserves_unknown_replacement_at_cas_boundary(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    first = _test_retention_record(backup_module, backup_dir, "state-cas-a.gnucash.sqlite", b"state cas a")
    second = _test_retention_record(backup_module, backup_dir, "state-cas-b.gnucash.sqlite", b"state cas b")
    backup_module._upsert_retention_state_record(backup_dir.resolve(), first)
    state_dir = backup_module._retention_state_dir(backup_dir.resolve())
    assert state_dir is not None
    state_file = state_dir / backup_module.VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME
    unknown_bytes = backup_module._serialize_retention_state_records([])
    raced = {"done": False}
    real_matches_snapshot = backup_module._state_file_matches_snapshot

    def racing_matches_snapshot(path, snapshot):
        result = real_matches_snapshot(path, snapshot)
        if Path(path) == state_file and result and not raced["done"]:
            raced["done"] = True
            replacement = state_file.with_name("unknown-state-replacement.json")
            replacement.write_bytes(unknown_bytes)
            replacement.chmod(0o600)
            os.replace(replacement, state_file)
        return result

    monkeypatch.setattr(backup_module, "_state_file_matches_snapshot", racing_matches_snapshot)

    with pytest.raises(OSError):
        backup_module._upsert_retention_state_record(backup_dir.resolve(), second)

    assert raced["done"] is True
    assert state_file.read_bytes() == unknown_bytes


def test_verified_backup_retention_state_write_and_fsync_failures_preserve_existing(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    first = _test_retention_record(backup_module, backup_dir, "state-fsync-a.gnucash.sqlite", b"state fsync a")
    second = _test_retention_record(backup_module, backup_dir, "state-fsync-b.gnucash.sqlite", b"state fsync b")
    backup_module._upsert_retention_state_record(backup_dir.resolve(), first)
    state_dir = backup_module._retention_state_dir(backup_dir.resolve())
    assert state_dir is not None
    state_file = state_dir / backup_module.VERIFIED_BACKUP_RETENTION_STATE_FILE_NAME
    original_bytes = state_file.read_bytes()
    real_write = backup_module.os.write
    real_fsync = backup_module.os.fsync

    monkeypatch.setattr(backup_module.os, "write", lambda fd, data: 0)
    with pytest.raises(OSError):
        backup_module._upsert_retention_state_record(backup_dir.resolve(), second)
    assert state_file.read_bytes() == original_bytes

    monkeypatch.setattr(backup_module.os, "write", real_write)
    file_fsync_calls = {"count": 0}

    def fail_first_fsync(fd):
        file_fsync_calls["count"] += 1
        if file_fsync_calls["count"] == 1:
            raise OSError("file fsync failed")
        return real_fsync(fd)

    monkeypatch.setattr(backup_module.os, "fsync", fail_first_fsync)
    with pytest.raises(OSError):
        backup_module._upsert_retention_state_record(backup_dir.resolve(), second)
    assert state_file.read_bytes() == original_bytes

    monkeypatch.setattr(backup_module.os, "fsync", real_fsync)
    monkeypatch.setattr(backup_module, "_fsync_directory_fd", lambda fd: (_ for _ in ()).throw(OSError("dir fsync failed")))
    with pytest.raises(OSError):
        backup_module._upsert_retention_state_record(backup_dir.resolve(), second)
    assert state_file.read_bytes() == original_bytes


def test_verified_backup_retention_active_capacity_prune_failure_stops_before_mutation(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module
    from app.services.backup import BackupError

    book_dir = tmp_path / "books"
    book_dir.mkdir()
    source = book_dir / "synthetic-active-capacity.gnucash.sqlite"
    source.write_bytes(b"SQLite format 3\x00active cap payload")
    backup_dir = book_dir.parent / "backups" / source.stem
    backup_dir.mkdir(parents=True)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    for index in range(50):
        _write_test_verified_backup(
            backup_module,
            backup_dir,
            f"active-full-{index:03d}.gnucash.sqlite",
            f"active-full-payload-{index:03d}".encode("utf-8"),
            now - timedelta(minutes=50 - index),
        )
    before_files = sorted(path.relative_to(backup_dir) for path in _backup_tree_files(backup_dir))
    monkeypatch.setattr(backup_module, "_unlink_verified_backup_candidate", lambda *args, **kwargs: False)

    with pytest.raises(BackupError):
        backup_module.create_book_backup({"uri_or_path": str(source)})

    after_files = sorted(path.relative_to(backup_dir) for path in _backup_tree_files(backup_dir))
    assert after_files == before_files


def test_verified_backup_retention_quarantine_scan_stops_at_declared_entry_bound(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    state_dir = backup_module._retention_state_dir(backup_dir.resolve(), create=True)
    assert state_dir is not None
    for index in range(25):
        (state_dir / f"overflow-{index:03d}.retention-delete-1-{index}.tmp").write_bytes(b"x")
    monkeypatch.setattr(backup_module, "VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES", 2)
    real_scandir = backup_module.os.scandir
    seen = {"state_entries": 0}

    class CountingScandir:
        def __init__(self, path):
            self.path = Path(path)
            self._context = real_scandir(path)
            self._iterator = None

        def __enter__(self):
            self._iterator = self._context.__enter__()
            return self

        def __exit__(self, exc_type, exc, tb):
            return self._context.__exit__(exc_type, exc, tb)

        def __iter__(self):
            return self

        def __next__(self):
            assert self._iterator is not None
            entry = next(self._iterator)
            if self.path == state_dir:
                seen["state_entries"] += 1
            return entry

    monkeypatch.setattr(backup_module.os, "scandir", lambda path: CountingScandir(path))
    inspection = backup_module._RetentionInspection()

    usage = backup_module._retention_quarantine_usage(backup_dir.resolve(), inspection)

    assert usage[0] == 3
    assert inspection.skipped_reason == "retention_quarantine_entry_limit_exceeded"
    assert seen["state_entries"] <= 3


def test_verified_backup_retention_uses_verified_creation_time_not_source_mtime(tmp_path: Path):
    from app.services import backup as backup_module

    book_dir = tmp_path / "books"
    book_dir.mkdir()
    source = book_dir / "synthetic-old-source.gnucash.sqlite"
    source.write_bytes(b"SQLite format 3\x00old source timestamp payload")
    old_timestamp = (datetime.now(timezone.utc) - timedelta(days=40)).timestamp()
    source.chmod(0o640)
    source.touch()
    import os

    os.utime(source, (old_timestamp, old_timestamp))

    first = Path(backup_module.create_book_backup({"uri_or_path": str(source)}))
    second = Path(backup_module.create_book_backup({"uri_or_path": str(source)}))
    backup_dir = first.parent
    backup_files = sorted(path for path in backup_dir.iterdir() if not path.name.endswith(backup_module.VERIFIED_BACKUP_MARKER_SUFFIX))

    assert first in backup_files
    assert second in backup_files
    assert first.read_bytes() == source.read_bytes()
    assert second.read_bytes() == source.read_bytes()
    assert first.stat().st_mode & 0o777 == 0o640
    assert second.stat().st_mode & 0o777 == 0o640

    old_verified = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "genuinely-old.gnucash.sqlite",
        b"old verified backup",
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    deleted = backup_module.prune_verified_book_backups(backup_dir, current_backup=second)

    assert deleted == 1
    assert first.exists()
    assert second.exists()
    assert not old_verified.exists()


def test_verified_backup_retention_preserves_replacement_before_delete(tmp_path: Path):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    original_payload = b"original verified backup"
    replacement_payload = b"unknown replacement backup"
    original = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "race.gnucash.sqlite",
        original_payload,
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    inspection = backup_module._RetentionInspection()
    candidate = backup_module._verified_backup_candidates(backup_dir.resolve(), inspection)[0]

    original.write_bytes(replacement_payload)
    deleted = backup_module._unlink_verified_backup_candidate(candidate, backup_dir.resolve())

    assert deleted is False
    assert original.read_bytes() == replacement_payload
    assert backup_module._verified_marker_path(original).exists()


def test_verified_backup_retention_preserves_replacement_during_delete(tmp_path: Path, monkeypatch):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    original_payload = b"original verified backup"
    replacement_payload = b"unknown during rename"
    original = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "during.gnucash.sqlite",
        original_payload,
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    inspection = backup_module._RetentionInspection()
    candidate = backup_module._verified_backup_candidates(backup_dir.resolve(), inspection)[0]
    real_rename_no_replace = backup_module._rename_no_replace
    raced = {"done": False}

    def racing_rename_no_replace(src, dst):
        if Path(src) == original and not raced["done"]:
            raced["done"] = True
            original.write_bytes(replacement_payload)
        return real_rename_no_replace(src, dst)

    monkeypatch.setattr(backup_module, "_rename_no_replace", racing_rename_no_replace)
    deleted = backup_module._unlink_verified_backup_candidate(candidate, backup_dir.resolve())

    assert deleted is False
    assert raced["done"] is True
    preserved_paths = [path for path in _backup_tree_files(backup_dir) if path.read_bytes() == replacement_payload]
    assert preserved_paths
    assert all(path.parent == backup_dir for path in preserved_paths)


def test_verified_backup_retention_preserves_marker_replacement_before_quarantine(tmp_path: Path):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    original = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "marker-before.gnucash.sqlite",
        b"original marker pre-quarantine backup",
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    marker = backup_module._verified_marker_path(original)
    inspection = backup_module._RetentionInspection()
    candidate = backup_module._verified_backup_candidates(backup_dir.resolve(), inspection)[0]
    replacement_marker = b'{"status":"unknown replacement before quarantine"}'

    marker.write_bytes(replacement_marker)
    deleted = backup_module._unlink_verified_backup_candidate(candidate, backup_dir.resolve())

    assert deleted is False
    assert original.exists()
    assert marker.read_bytes() == replacement_marker


def test_verified_backup_retention_preserves_marker_replacement_at_rename_boundary(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    original = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "marker-rename.gnucash.sqlite",
        b"original marker rename-boundary backup",
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    marker = backup_module._verified_marker_path(original)
    inspection = backup_module._RetentionInspection()
    candidate = backup_module._verified_backup_candidates(backup_dir.resolve(), inspection)[0]
    real_rename_no_replace = backup_module._rename_no_replace
    replacement_marker = b'{"status":"unknown replacement at marker rename"}'
    raced = {"done": False}

    def racing_rename_no_replace(src, dst):
        if Path(src) == marker and not raced["done"]:
            raced["done"] = True
            marker.write_bytes(replacement_marker)
        return real_rename_no_replace(src, dst)

    monkeypatch.setattr(backup_module, "_rename_no_replace", racing_rename_no_replace)
    deleted = backup_module._unlink_verified_backup_candidate(candidate, backup_dir.resolve())

    assert raced["done"] is True
    assert deleted is False
    assert original.exists()
    assert marker.read_bytes() == replacement_marker


def test_verified_backup_retention_preserves_marker_replacement_at_reclamation_boundary(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    original = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "marker-unlink.gnucash.sqlite",
        b"original marker unlink-boundary backup",
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    marker = backup_module._verified_marker_path(original)
    inspection = backup_module._RetentionInspection()
    candidate = backup_module._verified_backup_candidates(backup_dir.resolve(), inspection)[0]
    replacement_marker = b'{"status":"unknown replacement at marker unlink"}'
    raced = {"done": False}

    real_preserve_pair = backup_module._preserve_quarantined_verified_pair

    def racing_preserve_pair(candidate_arg, backup_quarantine_path, marker_quarantine_path):
        if not raced["done"]:
            raced["done"] = True
            marker_quarantine_path.write_bytes(replacement_marker)
        return real_preserve_pair(candidate_arg, backup_quarantine_path, marker_quarantine_path)

    monkeypatch.setattr(backup_module, "_preserve_quarantined_verified_pair", racing_preserve_pair)
    deleted = backup_module._unlink_verified_backup_candidate(candidate, backup_dir.resolve())

    assert raced["done"] is True
    assert deleted is False
    assert original.exists()
    preserved_paths = [path for path in _backup_tree_files(backup_dir) if path.read_bytes() == replacement_marker]
    assert preserved_paths


def test_verified_backup_retention_reclaim_preserves_replacement_at_descriptor_boundary(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    now = datetime.now(timezone.utc)
    _write_test_verified_backup(
        backup_module,
        backup_dir,
        "reclaim-dirfd.gnucash.sqlite",
        b"original reclaim dirfd backup",
        now - timedelta(days=31),
    )
    assert backup_module.prune_verified_book_backups(backup_dir, now=now) == 1
    state_dir = backup_module._retention_state_dir(backup_dir.resolve())
    assert state_dir is not None
    replacement_payload = b"unknown replacement at reclaim descriptor boundary"
    real_ftruncate = backup_module.os.ftruncate
    raced = {"done": False, "name": ""}

    def racing_ftruncate(fd, length):
        if not raced["done"]:
            raced["done"] = True
            target = Path(os.readlink(f"/proc/self/fd/{fd}"))
            raced["name"] = target.name
            replacement = target.with_name(f"{target.name}.unknown-replacement")
            replacement.write_bytes(replacement_payload)
            os.replace(replacement, target)
        return real_ftruncate(fd, length)

    monkeypatch.setattr(backup_module.os, "ftruncate", racing_ftruncate)

    recovery_inspection = backup_module._RetentionInspection()
    backup_module._recover_verified_backup_retention_state(backup_dir.resolve(), recovery_inspection)

    assert ".retention-delete-" in raced["name"]
    assert recovery_inspection.skipped_reason is None
    assert recovery_inspection.reclaimed_entries == 0
    assert recovery_inspection.reclaimed_bytes > 0
    assert recovery_inspection.reclaimed_pairs == 0
    preserved_paths = [path for path in _backup_tree_files(backup_dir) if path.read_bytes() == replacement_payload]
    assert preserved_paths
    state_records = backup_module._load_retention_state_records(backup_dir.resolve())
    assert len(state_records) == 1
    assert state_records[0]["state"] == "pair_quarantined"


def test_verified_backup_retention_recovery_never_artifact_unlinks(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    now = datetime.now(timezone.utc)
    _write_test_verified_backup(
        backup_module,
        backup_dir,
        "no-artifact-unlink.gnucash.sqlite",
        b"original no artifact unlink backup",
        now - timedelta(days=31),
    )
    assert backup_module.prune_verified_book_backups(backup_dir, now=now) == 1
    real_unlink = backup_module.os.unlink

    def rejecting_artifact_unlink(path, *args, **kwargs):
        name = os.fsdecode(path) if isinstance(path, (str, bytes)) else str(path)
        if ".retention-delete-" in name or name.startswith(".reclaim-"):
            raise AssertionError(f"artifact unlink is not identity-safe: {name}")
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(backup_module.os, "unlink", rejecting_artifact_unlink)

    recovery_inspection = backup_module._RetentionInspection()
    backup_module._recover_verified_backup_retention_state(backup_dir.resolve(), recovery_inspection)

    assert recovery_inspection.skipped_reason is None
    assert recovery_inspection.reclaimed_entries == 0
    assert recovery_inspection.reclaimed_bytes > 0
    assert recovery_inspection.reclaimed_pairs == 0
    state_records = backup_module._load_retention_state_records(backup_dir.resolve())
    assert len(state_records) == 1
    assert state_records[0]["state"] == "pair_quarantined"


def test_verified_backup_retention_descriptor_partial_reclaim_restarts_without_false_pair_success(
    tmp_path: Path,
    monkeypatch,
):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    now = datetime.now(timezone.utc)
    _write_test_verified_backup(
        backup_module,
        backup_dir,
        "partial-descriptor-reclaim.gnucash.sqlite",
        b"original partial descriptor reclaim backup",
        now - timedelta(days=31),
    )
    assert backup_module.prune_verified_book_backups(backup_dir, now=now) == 1
    record = backup_module._load_retention_state_records(backup_dir.resolve())[0]
    state_dir = backup_module._retention_state_dir(backup_dir.resolve())
    assert state_dir is not None
    backup_quarantine = state_dir / record["backup_quarantine_name"]
    marker_quarantine = state_dir / record["marker_quarantine_name"]
    backup_size = backup_quarantine.stat().st_size
    marker_size = marker_quarantine.stat().st_size
    real_ftruncate = backup_module.os.ftruncate
    calls: list[str] = []

    def fail_second_ftruncate(fd, length):
        target = Path(os.readlink(f"/proc/self/fd/{fd}"))
        calls.append(target.name)
        if len(calls) == 2:
            raise OSError("marker descriptor reclaim failed")
        return real_ftruncate(fd, length)

    monkeypatch.setattr(backup_module.os, "ftruncate", fail_second_ftruncate)

    first_recovery = backup_module._RetentionInspection()
    backup_module._recover_verified_backup_retention_state(backup_dir.resolve(), first_recovery)

    assert calls == [record["backup_quarantine_name"], record["marker_quarantine_name"]]
    assert first_recovery.skipped_reason is None
    assert first_recovery.reclaimed_entries == 0
    assert first_recovery.reclaimed_bytes == backup_size
    assert first_recovery.reclaimed_pairs == 0
    assert backup_quarantine.exists()
    assert backup_quarantine.stat().st_size == 0
    assert marker_quarantine.exists()
    assert marker_quarantine.stat().st_size == marker_size
    assert len(backup_module._load_retention_state_records(backup_dir.resolve())) == 1

    monkeypatch.setattr(backup_module.os, "ftruncate", real_ftruncate)
    second_recovery = backup_module._RetentionInspection()
    backup_module._recover_verified_backup_retention_state(backup_dir.resolve(), second_recovery)

    assert second_recovery.skipped_reason is None
    assert second_recovery.reclaimed_entries == 0
    assert second_recovery.reclaimed_bytes == marker_size
    assert second_recovery.reclaimed_pairs == 0
    assert backup_quarantine.exists()
    assert marker_quarantine.exists()
    assert backup_module._retention_quarantine_usage(backup_dir.resolve()) == (2, 0)
    state_records = backup_module._load_retention_state_records(backup_dir.resolve())
    assert len(state_records) == 1
    assert state_records[0]["state"] == "pair_quarantined"


def test_verified_backup_retention_preserves_pair_on_marker_partial_race(tmp_path: Path, monkeypatch):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    original = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "marker-partial.gnucash.sqlite",
        b"original marker partial-race backup",
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    marker = backup_module._verified_marker_path(original)
    inspection = backup_module._RetentionInspection()
    candidate = backup_module._verified_backup_candidates(backup_dir.resolve(), inspection)[0]
    real_rename_no_replace = backup_module._rename_no_replace
    replacement_marker = b'{"status":"unknown replacement after marker quarantine"}'
    raced = {"done": False}

    def racing_rename_no_replace(src, dst):
        result = real_rename_no_replace(src, dst)
        if Path(src) == marker and not raced["done"]:
            raced["done"] = True
            marker.write_bytes(replacement_marker)
        return result

    monkeypatch.setattr(backup_module, "_rename_no_replace", racing_rename_no_replace)
    deleted = backup_module._unlink_verified_backup_candidate(candidate, backup_dir.resolve())

    assert raced["done"] is True
    assert deleted is True
    assert not original.exists()
    assert marker.read_bytes() == replacement_marker


def test_verified_backup_retention_preserves_quarantine_destination_replacement(tmp_path: Path, monkeypatch):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    original = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "marker-destination-race.gnucash.sqlite",
        b"original marker destination-race backup",
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    marker = backup_module._verified_marker_path(original)
    inspection = backup_module._RetentionInspection()
    candidate = backup_module._verified_backup_candidates(backup_dir.resolve(), inspection)[0]
    real_rename_no_replace = backup_module._rename_no_replace
    unknown_destination = b"unknown quarantine destination"
    raced = {"done": False}

    def racing_rename_no_replace(src, dst):
        if Path(src) == marker and not raced["done"]:
            raced["done"] = True
            Path(dst).write_bytes(unknown_destination)
        return real_rename_no_replace(src, dst)

    monkeypatch.setattr(backup_module, "_rename_no_replace", racing_rename_no_replace)
    deleted = backup_module._unlink_verified_backup_candidate(candidate, backup_dir.resolve())

    assert raced["done"] is True
    assert deleted is False
    assert original.exists()
    assert marker.exists()
    preserved_destinations = [path for path in _backup_tree_files(backup_dir) if path.read_bytes() == unknown_destination]
    assert preserved_destinations


def test_verified_backup_retention_skips_oversized_directory_before_hashing(tmp_path: Path, monkeypatch):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    for index in range(6):
        _write_test_verified_backup(
            backup_module,
            backup_dir,
            f"old-{index}.gnucash.sqlite",
            f"payload-{index}".encode("utf-8"),
            datetime.now(timezone.utc) - timedelta(days=31, seconds=index),
        )
    monkeypatch.setattr(backup_module, "VERIFIED_BACKUP_RETENTION_MAX_DIRECTORY_ENTRIES", 3)
    hash_calls = {"count": 0}
    real_sha = backup_module._sha256_file

    def spy_sha(path: Path) -> str:
        hash_calls["count"] += 1
        return real_sha(path)

    monkeypatch.setattr(backup_module, "_sha256_file", spy_sha)

    deleted = backup_module.prune_verified_book_backups(backup_dir)

    assert deleted == 0
    assert hash_calls["count"] == 0
    assert len([path for path in backup_dir.iterdir() if not path.name.endswith(backup_module.VERIFIED_BACKUP_MARKER_SUFFIX)]) == 6


def test_verified_backup_retention_tracks_repeated_cycles_with_separate_quarantine_budget(tmp_path: Path, monkeypatch):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    for index in range(55):
        _write_test_verified_backup(
            backup_module,
            backup_dir,
            f"cycle-{index:03d}.gnucash.sqlite",
            f"cycle-payload-{index:03d}".encode("utf-8"),
            now - timedelta(minutes=55 - index),
        )

    first_retired = backup_module.prune_verified_book_backups(backup_dir, now=now)
    state_records = backup_module._load_retention_state_records(backup_dir.resolve())
    quarantine_entries, quarantine_bytes = backup_module._retention_quarantine_usage(backup_dir.resolve())

    assert first_retired == 5
    assert len(state_records) == 5
    assert quarantine_entries == 10
    assert quarantine_bytes > 0
    assert len([path for path in backup_dir.iterdir() if path.is_file() and not path.name.endswith(backup_module.VERIFIED_BACKUP_MARKER_SUFFIX)]) == 50

    for cycle in range(1, 5):
        for index in range(5):
            _write_test_verified_backup(
                backup_module,
                backup_dir,
                f"cycle-{cycle}-{index}.gnucash.sqlite",
                f"cycle-payload-{cycle}-{index}".encode("utf-8"),
                now + timedelta(minutes=cycle, seconds=index),
            )
        assert backup_module.prune_verified_book_backups(backup_dir, now=now + timedelta(minutes=cycle)) == 5

    state_records = backup_module._load_retention_state_records(backup_dir.resolve())
    quarantine_entries, quarantine_bytes = backup_module._retention_quarantine_usage(backup_dir.resolve())
    assert len(state_records) == 25
    assert quarantine_entries == 50
    assert quarantine_entries <= backup_module.VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES
    assert quarantine_bytes <= backup_module.VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_BYTES

    recovery_inspection = backup_module._RetentionInspection()
    backup_module._recover_verified_backup_retention_state(backup_dir.resolve(), recovery_inspection)
    assert recovery_inspection.skipped_reason is None
    assert recovery_inspection.reclaimed_entries == 0
    assert recovery_inspection.reclaimed_bytes > 0
    assert recovery_inspection.reclaimed_pairs == 0
    assert len(backup_module._load_retention_state_records(backup_dir.resolve())) == 25
    assert backup_module._retention_quarantine_usage(backup_dir.resolve()) == (50, 0)

    monkeypatch.setattr(backup_module, "VERIFIED_BACKUP_RETENTION_MAX_DIRECTORY_ENTRIES", 100)
    inspection = backup_module._RetentionInspection()
    candidates = backup_module._verified_backup_candidates(backup_dir.resolve(), inspection)
    assert len(candidates) == 50
    assert inspection.skipped_reason is None
    assert inspection.entries_seen <= 100
    assert inspection.quarantine_entries_seen >= 1


def test_verified_backup_retention_recovers_marker_and_pair_interrupted_states(tmp_path: Path):
    from app.services import backup as backup_module

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    first = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "recover-marker.gnucash.sqlite",
        b"recover marker payload",
        datetime.now(timezone.utc),
    )
    inspection = backup_module._RetentionInspection()
    candidate = backup_module._verified_backup_candidates(backup_dir.resolve(), inspection)[0]
    marker_quarantine = backup_module._unique_quarantine_path(
        candidate.marker_path,
        backup_dir.resolve(),
        candidate.marker_st_dev,
        candidate.marker_st_ino,
    )
    backup_quarantine = backup_module._unique_quarantine_path(
        candidate.path,
        backup_dir.resolve(),
        candidate.st_dev,
        candidate.st_ino,
    )
    record = backup_module._retention_record_for_candidate(candidate, backup_quarantine, marker_quarantine, "planned")
    backup_module._upsert_retention_state_record(backup_dir.resolve(), record)
    assert backup_module._rename_no_replace(candidate.marker_path, marker_quarantine)
    record["state"] = "marker_quarantined"
    backup_module._upsert_retention_state_record(backup_dir.resolve(), record)

    recovery_inspection = backup_module._RetentionInspection()
    backup_module._recover_verified_backup_retention_state(backup_dir.resolve(), recovery_inspection)

    assert recovery_inspection.skipped_reason is None
    assert first.exists()
    assert backup_module._verified_marker_path(first).exists()

    second = _write_test_verified_backup(
        backup_module,
        backup_dir,
        "recover-pair.gnucash.sqlite",
        b"recover pair payload",
        datetime.now(timezone.utc) - timedelta(days=31),
    )
    inspection = backup_module._RetentionInspection()
    candidate = [item for item in backup_module._verified_backup_candidates(backup_dir.resolve(), inspection) if item.name == second.name][0]
    marker_quarantine = backup_module._unique_quarantine_path(
        candidate.marker_path,
        backup_dir.resolve(),
        candidate.marker_st_dev,
        candidate.marker_st_ino,
    )
    backup_quarantine = backup_module._unique_quarantine_path(
        candidate.path,
        backup_dir.resolve(),
        candidate.st_dev,
        candidate.st_ino,
    )
    record = backup_module._retention_record_for_candidate(candidate, backup_quarantine, marker_quarantine, "marker_quarantined")
    backup_module._upsert_retention_state_record(backup_dir.resolve(), record)
    assert backup_module._rename_no_replace(candidate.marker_path, marker_quarantine)
    assert backup_module._rename_no_replace(candidate.path, backup_quarantine)

    recovery_inspection = backup_module._RetentionInspection()
    backup_module._recover_verified_backup_retention_state(backup_dir.resolve(), recovery_inspection)
    assert recovery_inspection.skipped_reason is None
    assert recovery_inspection.reclaimed_entries == 0
    assert recovery_inspection.reclaimed_bytes > 0
    assert recovery_inspection.reclaimed_pairs == 0
    state_records = backup_module._load_retention_state_records(backup_dir.resolve())
    pair_records = [record for record in state_records if record["backup_name"] == second.name]
    assert len(pair_records) == 1
    assert pair_records[0]["state"] == "pair_quarantined"
    assert backup_module._retention_quarantine_usage(backup_dir.resolve()) == (2, 0)
    assert not second.exists()
    assert not backup_module._verified_marker_path(second).exists()


def test_verified_backup_retention_backpressure_happens_before_backup_mutation(tmp_path: Path, monkeypatch):
    from app.services import backup as backup_module
    from app.services.backup import BackupError

    book_dir = tmp_path / "books"
    book_dir.mkdir()
    source = book_dir / "synthetic-capacity.gnucash.sqlite"
    source.write_bytes(b"SQLite format 3\x00capacity payload")
    backup_dir = book_dir.parent / "backups" / source.stem
    backup_dir.mkdir(parents=True)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    for index in range(50):
        _write_test_verified_backup(
            backup_module,
            backup_dir,
            f"full-{index:03d}.gnucash.sqlite",
            f"full-payload-{index:03d}".encode("utf-8"),
            now - timedelta(minutes=50 - index),
        )
    state_dir = backup_module._retention_state_dir(backup_dir.resolve(), create=True)
    assert state_dir is not None
    monkeypatch.setattr(backup_module, "VERIFIED_BACKUP_RETENTION_MAX_QUARANTINE_ENTRIES", 2)
    (state_dir / "occupied-a.retention-delete-1-1.tmp").write_bytes(b"occupied-a")
    (state_dir / "occupied-b.retention-delete-1-2.tmp").write_bytes(b"occupied-b")
    before_files = sorted(path.relative_to(backup_dir) for path in _backup_tree_files(backup_dir))

    with pytest.raises(BackupError):
        backup_module.create_book_backup({"uri_or_path": str(source)})

    after_files = sorted(path.relative_to(backup_dir) for path in _backup_tree_files(backup_dir))
    assert after_files == before_files


def _copy_fixture_with_extra_accounts(tmp_path: Path, extra_count: int = 80) -> tuple[Path, dict[str, str]]:
    import piecash

    source = Path(__file__).resolve().parent / "fixtures" / "test-book.gnucash.sqlite"
    target = tmp_path / "generated-many-accounts.gnucash.sqlite"
    shutil.copy2(source, target)
    book = piecash.open_book(str(target), readonly=False, do_backup=False)
    try:
        commodity = book.default_currency
        root = book.root_account
        for index in range(extra_count):
            piecash.Account(
                name=f"GeneratedExtra{index:03d}",
                type="EXPENSE",
                commodity=commodity,
                parent=root,
            )
        book.save()
        account_ids = {account.name: str(account.guid) for account in book.accounts}
    finally:
        book.close()
    return target, {
        "bank": account_ids["Bank"],
        "food": account_ids["Food"],
    }


def _create_deep_hierarchy_account_lookup_book(
    tmp_path: Path,
    *,
    depth: int = 8,
    unrelated_count: int = 80,
) -> tuple[Path, dict[str, str], dict[str, str]]:
    from datetime import date
    from decimal import Decimal

    import piecash
    from piecash import Account, Split, Transaction

    path = tmp_path / "generated-deep-account-lookup.gnucash.sqlite"
    book = piecash.create_book(currency="SEK", sqlite_file=str(path), overwrite=True)
    try:
        sek = book.default_currency
        root = book.root_account
        assets = Account(name="Assets", type="ASSET", parent=root, commodity=sek)
        parent = assets
        path_parts = ["Assets"]
        for index in range(1, depth + 1):
            parent = Account(name=f"Level{index:02d}", type="ASSET", parent=parent, commodity=sek)
            path_parts.append(parent.name)
        requested_bank = Account(name="Requested Bank", type="BANK", parent=parent, commodity=sek)
        requested_food = Account(name="Requested Food", type="CASH", parent=parent, commodity=sek)
        equity = Account(name="Opening Balances", type="EQUITY", parent=root, commodity=sek)
        unrelated_parent = Account(name="Unrelated Parent", type="EXPENSE", parent=root, commodity=sek)
        unrelated_accounts = [
            Account(name=f"Unrelated{index:03d}", type="EXPENSE", parent=unrelated_parent, commodity=sek)
            for index in range(unrelated_count)
        ]

        Transaction(
            currency=sek,
            description="requested account balances",
            post_date=date(2026, 5, 20),
            splits=[
                Split(account=requested_bank, value=Decimal("123.45")),
                Split(account=requested_food, value=Decimal("67.89")),
                Split(account=equity, value=Decimal("-191.34")),
            ],
        )
        for index, account in enumerate(unrelated_accounts):
            Transaction(
                currency=sek,
                description=f"unrelated transaction {index:03d}",
                post_date=date(2026, 5, 20),
                splits=[
                    Split(account=account, value=Decimal("0.01")),
                    Split(account=equity, value=Decimal("-0.01")),
                ],
            )
        book.save()
        ids = {"bank": str(requested_bank.guid), "food": str(requested_food.guid)}
        full_names = {
            "bank": ":".join([*path_parts, requested_bank.name]),
            "food": ":".join([*path_parts, requested_food.name]),
        }
    finally:
        book.close()
    return path, ids, full_names


def _create_overlapping_account_lookup_book(
    tmp_path: Path,
    *,
    include_sibling: bool = False,
    unrelated_count: int = 80,
) -> tuple[Path, dict[str, str], dict[str, str]]:
    from datetime import date
    from decimal import Decimal

    import piecash
    from piecash import Account, Split, Transaction

    path = tmp_path / "generated-overlapping-account-lookup.gnucash.sqlite"
    book = piecash.create_book(currency="SEK", sqlite_file=str(path), overwrite=True)
    try:
        sek = book.default_currency
        root = book.root_account
        assets = Account(name="Assets", type="ASSET", parent=root, commodity=sek)
        parent = Account(name="Requested Parent", type="ASSET", parent=assets, commodity=sek)
        child = Account(name="Requested Child", type="ASSET", parent=parent, commodity=sek)
        grandchild = Account(name="Grandchild", type="ASSET", parent=child, commodity=sek)
        sibling = None
        if include_sibling:
            sibling = Account(name="Sibling Leaf", type="ASSET", parent=parent, commodity=sek)
        equity = Account(name="Opening Balances", type="EQUITY", parent=root, commodity=sek)
        unrelated_parent = Account(name="Unrelated Parent", type="EXPENSE", parent=root, commodity=sek)
        unrelated_accounts = [
            Account(name=f"UnrelatedOverlap{index:03d}", type="EXPENSE", parent=unrelated_parent, commodity=sek)
            for index in range(unrelated_count)
        ]

        splits = [
            Split(account=parent, value=Decimal("10.00")),
            Split(account=child, value=Decimal("20.00")),
            Split(account=grandchild, value=Decimal("30.00")),
        ]
        if sibling is not None:
            splits.append(Split(account=sibling, value=Decimal("40.00")))
        splits.append(Split(account=equity, value=-sum((split.value for split in splits), Decimal("0"))))
        Transaction(
            currency=sek,
            description="overlapping requested account balances",
            post_date=date(2026, 5, 20),
            splits=splits,
        )
        for index, account in enumerate(unrelated_accounts):
            Transaction(
                currency=sek,
                description=f"unrelated overlap transaction {index:03d}",
                post_date=date(2026, 5, 20),
                splits=[
                    Split(account=account, value=Decimal("0.01")),
                    Split(account=equity, value=Decimal("-0.01")),
                ],
            )
        book.save()
        ids = {
            "parent": str(parent.guid),
            "child": str(child.guid),
            "grandchild": str(grandchild.guid),
        }
        full_names = {
            "parent": "Assets:Requested Parent",
            "child": "Assets:Requested Parent:Requested Child",
            "grandchild": "Assets:Requested Parent:Requested Child:Grandchild",
        }
        if sibling is not None:
            ids["sibling"] = str(sibling.guid)
            full_names["sibling"] = "Assets:Requested Parent:Sibling Leaf"
    finally:
        book.close()
    return path, ids, full_names


def _list_accounts_with_sql_statement_capture(monkeypatch, book_path: Path, account_ids: list[str]):
    from contextlib import contextmanager

    import piecash
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    from app.services.gnucash_book import GnuCashBookService

    service = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"})
    opened_book = piecash.open_book(str(book_path), readonly=True)
    statements: list[str] = []
    counters: dict[str, int] = {}

    @contextmanager
    def existing_book_context():
        yield opened_book

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().lower().startswith("select"):
            statements.append(str(statement))

    monkeypatch.setattr(service, "_open_book", existing_book_context)
    event.listen(Engine, "before_cursor_execute", before_cursor_execute)
    try:
        accounts = service.list_accounts_by_ids(account_ids, counters=counters)
    finally:
        event.remove(Engine, "before_cursor_execute", before_cursor_execute)
        opened_book.close()
    return accounts, counters, statements


def test_bounded_account_lookup_overlapping_parent_child_balances_and_counters(tmp_path: Path, monkeypatch):
    book_path, account_ids, full_names = _create_overlapping_account_lookup_book(tmp_path)

    accounts, counters, statements = _list_accounts_with_sql_statement_capture(
        monkeypatch,
        book_path,
        [account_ids["parent"], account_ids["child"], account_ids["parent"]],
    )

    assert [account.id for account in accounts] == [account_ids["parent"], account_ids["child"]]
    assert [account.full_name for account in accounts] == [full_names["parent"], full_names["child"]]
    assert [account.balance for account in accounts] == ["60.00", "50.00"]
    assert counters["requested_account_distinct_count"] == 2
    assert counters["requested_account_row_count"] == 2
    assert counters["account_path_row_count"] == 2
    assert counters["account_descendant_query_count"] == 2
    assert counters["account_descendant_row_count"] == 2
    assert counters["account_balance_account_count"] == 3
    assert counters["account_balance_split_row_count"] == 3
    assert counters["account_materialized_unique_count"] == 5
    assert counters["account_materialized_count"] == 6
    assert counters["account_query_count"] == len(statements)
    assert counters["account_query_count"] == 6


def test_bounded_account_lookup_overlapping_parent_grandchild_and_sibling_leaves(
    tmp_path: Path,
    monkeypatch,
):
    book_path, account_ids, full_names = _create_overlapping_account_lookup_book(tmp_path, include_sibling=True)

    parent_accounts, parent_counters, parent_statements = _list_accounts_with_sql_statement_capture(
        monkeypatch,
        book_path,
        [account_ids["parent"], account_ids["grandchild"]],
    )
    sibling_accounts, sibling_counters, sibling_statements = _list_accounts_with_sql_statement_capture(
        monkeypatch,
        book_path,
        [account_ids["child"], account_ids["sibling"]],
    )

    assert [account.id for account in parent_accounts] == [account_ids["parent"], account_ids["grandchild"]]
    assert [account.full_name for account in parent_accounts] == [full_names["parent"], full_names["grandchild"]]
    assert [account.balance for account in parent_accounts] == ["100.00", "30.00"]
    assert parent_counters["account_descendant_row_count"] == 3
    assert parent_counters["account_balance_account_count"] == 4
    assert parent_counters["account_balance_split_row_count"] == 4
    assert parent_counters["account_query_count"] == len(parent_statements)

    assert [account.id for account in sibling_accounts] == [account_ids["child"], account_ids["sibling"]]
    assert [account.full_name for account in sibling_accounts] == [full_names["child"], full_names["sibling"]]
    assert [account.balance for account in sibling_accounts] == ["50.00", "40.00"]
    assert sibling_counters["account_balance_account_count"] == 3
    assert sibling_counters["account_balance_split_row_count"] == 3
    assert sibling_counters["account_query_count"] == len(sibling_statements)


def test_bounded_account_descendant_closure_handles_branch_convergence_without_double_count():
    from app.services.gnucash_book import GnuCashBookService, _BoundedAccountRow

    def row(guid: str, parent_guid: str | None) -> _BoundedAccountRow:
        return _BoundedAccountRow(
            guid=guid,
            name=guid,
            account_type="ASSET",
            parent_guid=parent_guid,
            hidden=False,
            placeholder=False,
            commodity_guid="sek",
            commodity_namespace="CURRENCY",
            commodity_mnemonic="SEK",
            commodity_fraction=100,
        )

    service = GnuCashBookService({"uri_or_path": "/synthetic", "base_currency": "SEK"})
    requested_rows = [row("a", None), row("b", None)]
    row_map = {item.guid: item for item in requested_rows}
    counters: dict[str, int] = {}

    def fake_rows_by_parent_guids(session, parent_ids, *, counters, query_counter, row_counter, remaining_limit):
        service._add_counter(counters, "account_query_count")
        service._add_counter(counters, query_counter)
        parent_set = set(parent_ids)
        if parent_set == {"a", "b"}:
            rows = [row("c", "a"), row("c", "b")]
        elif parent_set == {"c"}:
            rows = [row("d", "c")]
        else:
            rows = []
        service._add_counter(counters, row_counter, len(rows))
        return rows

    service._sql_account_rows_by_parent_guids = fake_rows_by_parent_guids  # type: ignore[method-assign]
    descendants = service._collect_sql_account_descendant_rows(object(), requested_rows, row_map, counters=counters)

    assert descendants == {"a": {"a", "c", "d"}, "b": {"b", "c", "d"}}
    assert counters["account_descendant_row_count"] == 3
    assert counters["account_descendant_tuple_row_count"] == 3
    assert counters["account_unique_descendant_row_count"] == 2


def test_bounded_account_lookup_reports_unique_tuple_and_query_limit_counters(tmp_path: Path, monkeypatch):
    book_path, account_ids, _full_names = _create_overlapping_account_lookup_book(tmp_path, include_sibling=True)

    accounts, counters, statements = _list_accounts_with_sql_statement_capture(
        monkeypatch,
        book_path,
        [account_ids["parent"], account_ids["grandchild"], account_ids["parent"]],
    )

    assert [account.id for account in accounts] == [account_ids["parent"], account_ids["grandchild"]]
    assert counters["requested_account_distinct_count"] == 2
    assert counters["requested_account_tuple_row_count"] == 2
    assert counters["requested_account_unique_row_count"] == 2
    assert counters["account_path_tuple_row_count"] == counters["account_path_row_count"]
    assert counters["account_descendant_tuple_row_count"] == 3
    assert counters["account_unique_descendant_row_count"] == 3
    assert counters["account_materialized_tuple_row_count"] == (
        counters["requested_account_tuple_row_count"]
        + counters["account_path_tuple_row_count"]
        + counters["account_descendant_tuple_row_count"]
    )
    assert counters["account_materialized_unique_row_count"] < counters["account_materialized_tuple_row_count"]
    assert counters["account_query_limit"] >= counters["account_query_count"] == len(statements)


def test_bounded_account_lookup_query_limit_overflow_fails_before_extra_select(tmp_path: Path, monkeypatch):
    from contextlib import contextmanager

    import piecash
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    from app.services import gnucash_book as gnucash_book_module
    from app.services.gnucash_book import GnuCashBookService
    from app.services.gnucash_exceptions import GnuCashReadError

    book_path, account_ids, _full_names = _create_deep_hierarchy_account_lookup_book(tmp_path, depth=8)
    service = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"})
    monkeypatch.setattr(gnucash_book_module, "REQUEST_ACCOUNT_QUERY_LIMIT", 3)
    opened_book = piecash.open_book(str(book_path), readonly=True)
    counters: dict[str, int] = {}
    statements: list[str] = []

    @contextmanager
    def existing_book_context():
        yield opened_book

    monkeypatch.setattr(service, "_open_book", existing_book_context)

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().lower().startswith("select"):
            statements.append(str(statement))

    event.listen(Engine, "before_cursor_execute", before_cursor_execute)
    try:
        with pytest.raises(GnuCashReadError):
            service.list_accounts_by_ids([account_ids["bank"], account_ids["food"]], counters=counters)
    finally:
        event.remove(Engine, "before_cursor_execute", before_cursor_execute)
        opened_book.close()

    assert counters["account_query_limit"] == 3
    assert counters["account_query_count"] == 3
    assert counters["account_query_overflow_count"] == 4
    assert len(statements) == 3


@pytest.mark.parametrize("limit_name", ["depth", "rows"])
def test_bounded_account_lookup_descendant_cycle_depth_and_row_limits_fail_closed(
    tmp_path: Path,
    monkeypatch,
    limit_name,
):
    from app.services import gnucash_book as gnucash_book_module
    from app.services.gnucash_book import GnuCashBookService
    from app.services.gnucash_exceptions import GnuCashReadError

    book_path, account_ids, _full_names = _create_overlapping_account_lookup_book(tmp_path)
    service = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"})
    if limit_name == "depth":
        monkeypatch.setattr(gnucash_book_module, "REQUEST_ACCOUNT_HIERARCHY_MAX_DEPTH", 1)
    else:
        monkeypatch.setattr(gnucash_book_module, "REQUEST_ACCOUNT_HIERARCHY_ROW_MAX", 1)

    with pytest.raises(GnuCashReadError):
        service.list_accounts_by_ids([account_ids["parent"]], counters={})


def test_bounded_account_lookup_detects_descendant_cycle(tmp_path: Path):
    from sqlalchemy import create_engine, text

    from app.services.gnucash_book import GnuCashBookService
    from app.services.gnucash_exceptions import GnuCashReadError

    book_path, account_ids, _full_names = _create_overlapping_account_lookup_book(tmp_path)
    engine = create_engine(f"sqlite:///{book_path}")
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE accounts SET parent_guid = :grandchild WHERE guid = :parent"),
            {"grandchild": account_ids["grandchild"], "parent": account_ids["parent"]},
        )
    engine.dispose()

    service = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"})
    with pytest.raises(GnuCashReadError):
        service.list_accounts_by_ids([account_ids["parent"]], counters={})


def test_bounded_account_lookup_materializes_only_requested_accounts_from_real_book(tmp_path: Path):
    from app.services.gnucash_book import GnuCashBookService

    book_path, account_ids = _copy_fixture_with_extra_accounts(tmp_path)
    service = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"})
    counters: dict[str, int] = {}

    accounts = service.list_accounts_by_ids(
        [account_ids["bank"], account_ids["food"], account_ids["bank"]],
        counters=counters,
    )

    assert [account.id for account in accounts] == [account_ids["bank"], account_ids["food"]]
    assert counters["requested_account_distinct_count"] == 2
    assert counters["requested_account_row_count"] == 2
    assert counters["account_query_count"] == 6
    assert counters["account_path_row_count"] == 3
    assert counters["account_descendant_row_count"] == 1
    assert counters["account_balance_split_row_count"] == 7
    assert counters["account_materialized_count"] == (
        counters["requested_account_row_count"]
        + counters["account_path_row_count"]
        + counters["account_descendant_row_count"]
    )


def test_bounded_account_lookup_deep_hierarchy_sql_counters_are_observed_and_bounded(
    tmp_path: Path,
    monkeypatch,
):
    from contextlib import contextmanager

    import piecash
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    from app.services.gnucash_book import GnuCashBookService

    book_path, account_ids, full_names = _create_deep_hierarchy_account_lookup_book(tmp_path)
    service = GnuCashBookService({"uri_or_path": str(book_path), "base_currency": "SEK"})
    opened_book = piecash.open_book(str(book_path), readonly=True)
    statements: list[str] = []
    counters: dict[str, int] = {}

    @contextmanager
    def existing_book_context():
        yield opened_book

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().lower().startswith("select"):
            statements.append(str(statement))

    monkeypatch.setattr(service, "_open_book", existing_book_context)
    event.listen(Engine, "before_cursor_execute", before_cursor_execute)
    try:
        accounts = service.list_accounts_by_ids(
            [account_ids["bank"], account_ids["food"], account_ids["bank"]],
            counters=counters,
        )
    finally:
        event.remove(Engine, "before_cursor_execute", before_cursor_execute)
        opened_book.close()

    assert [account.id for account in accounts] == [account_ids["bank"], account_ids["food"]]
    assert [account.full_name for account in accounts] == [full_names["bank"], full_names["food"]]
    assert [account.balance for account in accounts] == ["123.45", "67.89"]
    assert counters["requested_account_distinct_count"] == 2
    assert counters["requested_account_row_count"] == 2
    assert counters["account_query_count"] == len(statements)
    assert counters["account_query_count"] == 13
    assert counters["account_path_query_count"] == 10
    assert counters["account_descendant_query_count"] == 1
    assert counters["account_materialized_count"] == (
        counters["requested_account_row_count"]
        + counters["account_path_row_count"]
        + counters["account_descendant_row_count"]
    )
    assert counters["account_path_row_count"] == 10
    assert counters["account_descendant_row_count"] == 0
    assert counters["account_balance_account_count"] == 2
    assert counters["account_balance_split_row_count"] == 2
    assert counters["account_balance_query_count"] == 1
    assert "joinedload" not in "\n".join(statements).lower()


def test_product_preview_uses_bounded_account_lookup_with_many_unrelated_accounts(api_context, tmp_path: Path, monkeypatch):
    from app.services.gnucash_book import GnuCashBookService

    book_path, account_ids = _copy_fixture_with_extra_accounts(tmp_path)
    enabled_settings = api_context["settings"].model_copy(update={"gnucash_writes_enabled": True})
    app.dependency_overrides[get_settings] = lambda: enabled_settings
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == api_context["ids"]["book"]).one()
        book.uri_or_path = str(book_path)
        book.base_currency = "SEK"
        book.transaction_create_enabled = True
        session.commit()

    counters: dict[str, int] = {}
    original = GnuCashBookService.list_accounts_by_ids

    def spy_list_accounts_by_ids(self, account_ids_arg, **kwargs):
        kwargs["counters"] = counters
        return original(self, account_ids_arg, **kwargs)

    monkeypatch.setattr(GnuCashBookService, "list_accounts_by_ids", spy_list_accounts_by_ids)
    payload = _general_preview_payload(
        splits=[
            {"account_id": account_ids["bank"], "amount": "-12.34", "memo": "bounded"},
            {"account_id": account_ids["food"], "amount": "12.34", "memo": "bounded"},
        ]
    )

    response = api_context["client"].post(
        f"/books/{api_context['ids']['book']}/transactions/create-preview",
        headers=api_context["headers"]["editor"],
        json=payload,
    )

    assert response.status_code == 200
    assert counters["requested_account_distinct_count"] == 2
    assert counters["requested_account_row_count"] == 2
    assert counters["account_materialized_count"] == (
        counters["requested_account_row_count"]
        + counters["account_path_row_count"]
        + counters["account_descendant_row_count"]
    )
    assert counters["account_materialized_count"] == 6


def test_descriptor_pinned_product_account_lookup_rejects_unbounded_fallback():
    from app.services.gnucash_book import GnuCashBookService
    from app.services.gnucash_exceptions import GnuCashReadError

    class UnboundedPinnedBook:
        session = None

        @property
        def accounts(self):
            raise AssertionError("descriptor-pinned product CREATE must not full-scan accounts")

    service = GnuCashBookService(
        {
            "uri_or_path": "/synthetic/pinned-fd",
            "base_currency": "SEK",
            "backup_source_is_pinned_fd": True,
        }
    )

    with pytest.raises(GnuCashReadError):
        service._accounts_by_ids(UnboundedPinnedBook(), ["bank-guid", "food-guid"])


def test_route_account_lookup_rejects_product_service_full_scan_fallback():
    import app.routers.transactions as transactions_router
    from app.services.gnucash_book import GnuCashBookService
    from app.services.gnucash_exceptions import GnuCashReadError

    service = GnuCashBookService(
        {
            "uri_or_path": "/synthetic/product-service",
            "base_currency": "SEK",
        }
    )
    setattr(service, "list_accounts_by_ids", None)

    def forbidden_list_accounts():
        raise AssertionError("product CREATE must not call list_accounts fallback")

    setattr(service, "list_accounts", forbidden_list_accounts)

    with pytest.raises(GnuCashReadError):
        transactions_router._service_list_accounts_by_ids(service, ["bank-guid", "food-guid"])


@pytest.mark.parametrize(
    "mode",
    [
        "missing_source",
        "replaced_inode",
        "symlink_change",
        "permission_error",
        "unsupported_file",
        "inspection_exception",
        "cached_metadata_only",
    ],
)
def test_product_confirm_real_generated_source_modes_fail_closed_before_reservation(
    api_context,
    tmp_path: Path,
    monkeypatch,
    mode,
):
    import app.routers.transactions as transactions_router
    import app.services.transaction_create_policy as policy_module

    source = _copy_real_disposable_book(tmp_path, f"synthetic-disposable-source-{mode}.gnucash.sqlite")
    _use_real_product_source(api_context, monkeypatch, source)
    monkeypatch.setattr(transactions_router, "transaction_service_for", lambda book: FakeReadService())
    payload = _general_preview_payload()
    outside = None
    outside_count_before = None

    if mode == "missing_source":
        source.unlink()
    elif mode == "permission_error":
        os.chmod(source, 0)
    elif mode == "unsupported_file":
        source.write_bytes(b"not a sqlite gnucash file")
    elif mode == "inspection_exception":
        def raise_versions(_path):
            raise RuntimeError("raw /private/source versions failure")

        monkeypatch.setattr(policy_module, "_read_source_versions", raise_versions)
    elif mode == "cached_metadata_only":
        other_root = tmp_path / "other-root"
        other_root.mkdir()
        cached_only_settings = api_context["settings"].model_copy(
            update={
                "gnucash_writes_enabled": True,
                "gnucash_book_allowed_roots": [str(other_root)],
            }
        )
        app.dependency_overrides[get_settings] = lambda: cached_only_settings

    with api_context["session_factory"]() as session:
        audit_count_before = session.query(AuditLog).filter(AuditLog.action == "transaction.create.confirm").count()
        idempotency_count_before = session.query(TransactionCreateIdempotency).count()

    preview_json = _post_product_preview(api_context, payload)

    with api_context["session_factory"]() as session:
        assert session.query(AuditLog).filter(AuditLog.action == "transaction.create.confirm").count() == audit_count_before
        assert session.query(TransactionCreateIdempotency).count() == idempotency_count_before

    if mode == "replaced_inode":
        source.unlink()
        shutil.copy2(_fixture_book_path(), source)
        source.chmod(0o600)
    elif mode == "symlink_change":
        outside = tmp_path / "outside" / "outside-synthetic-disposable.gnucash.sqlite"
        outside.parent.mkdir()
        shutil.copy2(_fixture_book_path(), outside)
        outside_count_before = _real_transaction_count(outside)
        source.unlink()
        source.symlink_to(outside)

    response = _post_product_confirm(api_context, preview_json, payload)

    if mode == "permission_error" and source.exists():
        os.chmod(source, 0o600)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PREVIEW_STALE"
    encoded = json.dumps(response.json())
    assert "/private" not in encoded
    assert "Traceback" not in encoded
    with api_context["session_factory"]() as session:
        assert session.query(TransactionCreateIdempotency).count() == idempotency_count_before
        assert session.query(AuditLog).filter(AuditLog.action == "transaction.create.confirm").count() == audit_count_before
    if outside is not None and outside_count_before is not None:
        assert _real_transaction_count(outside) == outside_count_before


def test_product_actual_executor_success_duplicate_backup_readback_and_metadata(
    api_context,
    tmp_path: Path,
    monkeypatch,
):
    import app.routers.transactions as transactions_router
    from app.services import backup as backup_module

    book_path = _copy_real_disposable_book(tmp_path)
    _use_real_product_source(api_context, monkeypatch, book_path)
    payload = _real_product_payload(book_path)
    before_count = _real_transaction_count(book_path)

    preview_json = _post_product_preview(api_context, payload)
    first = _post_product_confirm(api_context, preview_json, payload)
    duplicate = _post_product_confirm(api_context, preview_json, payload)

    assert first.status_code == 201, first.text
    assert first.json()["status"] == "created"
    assert first.json()["readback"]["verified"] is True
    assert first.json()["readback"]["transaction_present"] is True
    assert first.json()["readback"]["account_balance_deltas_verified"] is True
    assert first.json()["backup_ref"].startswith("bkp_")
    assert duplicate.status_code == 200, duplicate.text
    assert duplicate.json()["status"] == "already_created"
    assert duplicate.json()["transaction_id"] == first.json()["transaction_id"]
    assert _real_transaction_count(book_path) == before_count + 1

    backup_dir = book_path.parent.parent / "backups" / book_path.stem
    markers = list(backup_dir.glob(f"*{backup_module.VERIFIED_BACKUP_MARKER_SUFFIX}"))
    assert markers
    with api_context["session_factory"]() as session:
        record = session.query(TransactionCreateIdempotency).one()
        assert record.state == "succeeded"
        assert record.safe_result_json is not None
        assert session.query(WriteAlphaTransactionOwnership).count() == 1
        payloads = [
            json.loads(row.payload_json)
            for row in session.query(AuditLog).filter(AuditLog.action == "transaction.create.confirm").all()
        ]
        assert {payload["result"] for payload in payloads} == {"started", "success", "already_created"}
        assert all("/" not in json.dumps(payload) for payload in payloads)
    assert transactions_router.write_lock_service.inspect(f"book:{api_context['ids']['book']}").is_active is False


def test_product_actual_executor_valid_generated_book_attaches_once_and_preserves_exact_graph(
    api_context,
    tmp_path: Path,
    monkeypatch,
):
    import app.routers.transactions as transactions_router
    import piecash
    from app.services.gnucash_write import GnuCashWriteService

    template_path, book_path, template_hash = _copy_valid_generated_disposable_book(tmp_path)
    account_ids = _real_book_account_ids(book_path)
    _use_real_product_source(api_context, monkeypatch, book_path)
    description = "Valid generated CREATE attachment proof"
    payload = _general_preview_payload(
        date="2026-05-21",
        description=description,
        splits=[
            {"account_id": account_ids["Checking"], "amount": "-45.67", "memo": "valid debit"},
            {"account_id": account_ids["Food"], "amount": "45.67", "memo": "valid credit"},
        ],
    )
    before_count = _real_transaction_count(book_path)
    assert before_count == 0
    assert _real_transaction_count(template_path) == 0

    attach_guids: list[str] = []
    original_do_create_transaction = GnuCashWriteService._do_create_transaction

    def spy_do_create_transaction(self, book, request, **kwargs):
        session = getattr(book, "session", None)
        original_add = getattr(session, "add", None)
        assert callable(original_add)

        def spy_add(instance, *args, **add_kwargs):
            if isinstance(instance, piecash.Transaction):
                attach_guids.append(str(getattr(instance, "guid", "")))
            return original_add(instance, *args, **add_kwargs)

        monkeypatch.setattr(session, "add", spy_add)
        return original_do_create_transaction(self, book, request, **kwargs)

    monkeypatch.setattr(
        GnuCashWriteService,
        "_do_create_transaction",
        spy_do_create_transaction,
    )

    preview_json = _post_product_preview(api_context, payload)
    first = _post_product_confirm(api_context, preview_json, payload)
    duplicate = _post_product_confirm(api_context, preview_json, payload)

    assert first.status_code == 201, first.text
    assert first.json()["status"] == "created"
    transaction_id = first.json()["transaction_id"]
    assert attach_guids == [transaction_id]
    assert first.json()["readback"]["verified"] is True
    assert first.json()["readback"]["split_count"] == 2
    assert first.json()["readback"]["currency_consistent"] is True
    assert first.json()["readback"]["account_balance_deltas_verified"] is True
    assert duplicate.status_code == 200, duplicate.text
    assert duplicate.json()["status"] == "already_created"
    assert duplicate.json()["transaction_id"] == transaction_id
    assert _real_transaction_count(book_path) == before_count + 1

    storage = _transaction_storage_counts(book_path, transaction_id)
    assert storage["transaction_count"] == 1
    assert storage["split_count"] == 2
    assert storage["currency_guid_min"]
    assert storage["currency_guid_min"] == storage["currency_guid_max"]

    snapshot = _transaction_snapshot(book_path, transaction_id)
    assert snapshot["guid"] == transaction_id
    assert snapshot["date"] == "2026-05-21"
    assert snapshot["description"] == description
    assert snapshot["currency"] == "SEK"
    assert snapshot["currency_guid"] == snapshot["default_currency_guid"]
    assert snapshot["splits"] == [
        {
            "account_id": account_ids["Checking"],
            "account_name": "Checking",
            "amount": "-45.67",
            "quantity": "-45.67",
            "memo": "valid debit",
            "currency": "SEK",
        },
        {
            "account_id": account_ids["Food"],
            "account_name": "Food",
            "amount": "45.67",
            "quantity": "45.67",
            "memo": "valid credit",
            "currency": "SEK",
        },
    ]
    assert _transaction_snapshot(book_path, transaction_id) == snapshot
    assert _file_sha256(template_path) == template_hash
    assert _real_transaction_count(template_path) == 0
    assert transactions_router.write_lock_service.inspect(f"book:{api_context['ids']['book']}").is_active is False


def test_product_actual_executor_concurrent_second_confirm_is_busy_without_second_transaction(
    api_context,
    tmp_path: Path,
    monkeypatch,
):
    from app.services.gnucash_write import GnuCashWriteService

    book_path = _copy_real_disposable_book(tmp_path, "synthetic-disposable-concurrent.gnucash.sqlite")
    _use_real_product_source(api_context, monkeypatch, book_path)
    payload = _real_product_payload(book_path, description="Concurrent product CREATE proof")
    preview_a = _post_product_preview(api_context, payload)
    preview_b = _post_product_preview(api_context, payload)
    before_count = _real_transaction_count(book_path)

    original_execute = GnuCashWriteService._execute_write_transaction
    entered = threading.Event()
    release = threading.Event()
    call_lock = threading.Lock()
    calls = {"count": 0}

    def slow_first_execute(self, *args, **kwargs):
        with call_lock:
            calls["count"] += 1
            is_first = calls["count"] == 1
        if is_first:
            entered.set()
            assert release.wait(10)
        return original_execute(self, *args, **kwargs)

    monkeypatch.setattr(GnuCashWriteService, "_execute_write_transaction", slow_first_execute)
    results = {}
    errors = {}

    def send(name: str, preview_json: dict) -> None:
        try:
            results[name] = _post_product_confirm(api_context, preview_json, payload)
        except BaseException as exc:  # pragma: no cover - reported by assertion below
            errors[name] = exc

    first_thread = threading.Thread(target=send, args=("first", preview_a))
    second_thread = threading.Thread(target=send, args=("second", preview_b))
    first_thread.start()
    assert entered.wait(10)
    second_thread.start()
    second_thread.join(timeout=5)
    if second_thread.is_alive():
        release.set()
        first_thread.join(timeout=10)
        second_thread.join(timeout=10)
        raise AssertionError("second confirm did not return while first product CREATE lock was held")
    release.set()
    first_thread.join(timeout=10)

    assert errors == {}
    assert results["first"].status_code == 201, results["first"].text
    assert results["second"].status_code == 409, results["second"].text
    assert results["second"].json()["error"]["code"] == "BOOK_WRITE_BUSY"
    assert _real_transaction_count(book_path) == before_count + 1
    with api_context["session_factory"]() as session:
        records = session.query(TransactionCreateIdempotency).order_by(TransactionCreateIdempotency.id).all()
        assert [record.state for record in records].count("succeeded") == 1
        assert [record.safe_error_code for record in records].count("BOOK_WRITE_BUSY") == 1


@pytest.mark.parametrize(
    ("phase", "expected_code", "expected_delta"),
    [
        ("revalidation", "WRITE_FAILED", 0),
        ("backup", "BACKUP_FAILED", 0),
        ("write", "WRITE_FAILED", 0),
        ("close", "CREATE_RESULT_UNKNOWN", 1),
        ("reopen_readback", "CREATE_RESULT_UNKNOWN", 1),
        ("deltas", "CREATE_RESULT_UNKNOWN", 1),
        ("ownership", "CREATE_RESULT_UNKNOWN", 1),
        ("idempotency", "CREATE_RESULT_UNKNOWN", 1),
        ("audit", "CREATE_RESULT_UNKNOWN", 1),
    ],
)
def test_product_actual_executor_phase_exceptions_are_typed_and_do_not_retry_mutation(
    api_context,
    tmp_path: Path,
    monkeypatch,
    phase,
    expected_code,
    expected_delta,
):
    import app.routers.transactions as transactions_router
    import app.services.gnucash_write as gnucash_write_module
    from app.services.backup import BackupError
    from app.services.gnucash_book import GnuCashBookService
    from app.services.gnucash_exceptions import GnuCashReadError
    from app.services.gnucash_write import GnuCashWriteError, GnuCashWriteService

    book_path = _copy_real_disposable_book(tmp_path, f"synthetic-disposable-phase-{phase}.gnucash.sqlite")
    _use_real_product_source(api_context, monkeypatch, book_path)
    payload = _real_product_payload(book_path, description=f"Phase failure {phase}")
    preview_json = _post_product_preview(api_context, payload)
    before_count = _real_transaction_count(book_path)

    if phase == "revalidation":
        def invalid_validate(self, request):
            return TransactionValidationResultDTO(
                valid=False,
                errors=["synthetic revalidation phase failure /private/source"],
                warnings=[],
                summary={"phase": "revalidation"},
            )

        monkeypatch.setattr(GnuCashWriteService, "validate_transaction_create", invalid_validate)
    elif phase == "backup":
        def fail_backup(_book_config):
            raise BackupError("/private/source/book.gnucash.sqlite", "synthetic backup phase")

        monkeypatch.setattr(gnucash_write_module, "create_book_backup", fail_backup)
    elif phase == "write":
        def fail_write(self, book, request):
            raise GnuCashWriteError("synthetic write phase /private/source")

        monkeypatch.setattr(GnuCashWriteService, "_do_create_transaction", fail_write)
    elif phase == "close":
        original_open = GnuCashWriteService._open_piecash_book_for_write

        class CloseFailureProxy:
            def __init__(self, wrapped):
                self._wrapped = wrapped

            def __getattr__(self, name):
                return getattr(self._wrapped, name)

            def close(self):
                self._wrapped.close()
                raise RuntimeError("synthetic close phase /private/source")

        def open_with_close_failure(self, uri_or_path):
            return CloseFailureProxy(original_open(self, uri_or_path))

        monkeypatch.setattr(GnuCashWriteService, "_open_piecash_book_for_write", open_with_close_failure)
    elif phase == "reopen_readback":
        def fail_get_transaction(self, transaction_id):
            raise GnuCashReadError("synthetic readback phase /private/source")

        monkeypatch.setattr(GnuCashBookService, "get_transaction", fail_get_transaction)
    elif phase == "deltas":
        def fail_deltas(book, request, result, before_account_balances, **kwargs):
            raise transactions_router.GnuCashCreateReadbackVerificationError(
                "synthetic delta phase /private/source",
                backup_path=result.backup_path,
            )

        monkeypatch.setattr(transactions_router, "_verify_account_balance_deltas", fail_deltas)
    elif phase == "ownership":
        def fail_ownership(*args, **kwargs):
            raise RuntimeError("synthetic ownership phase /private/source")

        monkeypatch.setattr(transactions_router, "_record_write_alpha_transaction_ownership", fail_ownership)
    elif phase == "idempotency":
        def fail_mark_succeeded(self, record, safe_result, **kwargs):
            raise RuntimeError("synthetic idempotency phase /private/source")

        monkeypatch.setattr(TransactionCreateIdempotencyService, "mark_succeeded", fail_mark_succeeded)
    elif phase == "audit":
        original_audit = transactions_router._audit_product_transaction_create_confirm

        def fail_success_audit(session, **kwargs):
            if kwargs.get("result") == "success":
                raise RuntimeError("synthetic audit phase /private/source")
            return original_audit(session, **kwargs)

        monkeypatch.setattr(transactions_router, "_audit_product_transaction_create_confirm", fail_success_audit)

    first = _post_product_confirm(api_context, preview_json, payload)
    retry = _post_product_confirm(api_context, preview_json, payload)

    assert first.status_code == 503, first.text
    assert first.json()["error"]["code"] == expected_code
    assert retry.status_code in {409, 503}
    assert _real_transaction_count(book_path) == before_count + expected_delta
    encoded = json.dumps({"first": first.json(), "retry": retry.json()})
    assert "/private" not in encoded
    assert "Traceback" not in encoded
    assert transactions_router.write_lock_service.inspect(f"book:{api_context['ids']['book']}").is_active is False
    with api_context["session_factory"]() as session:
        record = session.query(TransactionCreateIdempotency).one()
        assert record.state in {"rejected", "indeterminate"}
        assert record.safe_result_json is None
        assert record.safe_error_code in {expected_code, "CREATE_RECOVERY_REQUIRED"}
