"""A1 generated real-shape fixture plus RED read-only correctness tests.

The remaining xfail tests are intentional RED evidence for later roadmap blocks.
Per the A0 PM clarification, the source-hash invariant is an always-green safety
guard. The A2 liabilities/net-worth contract now runs as a normal green test.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
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
from app.models import Book, User, UserBookAccess
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.gnucash_book import GnuCashBookService
from tests.support.generate_real_shape_regression_fixture import (
    BASE_CURRENCY,
    EARLY_AS_OF_DATE,
    LATE_AS_OF_DATE,
    RealShapeRegressionFixture,
    SOURCE_HASH_ALGORITHM,
    canonical_sqlite_hash,
    generate_real_shape_regression_fixture,
    sha256_file,
)

JWT_SECRET = "readonly-real-shape-regression-" + "x" * 32
ADMIN_PASSWORD = "real-shape-admin-pass"
RED_XFAIL = pytest.mark.xfail(strict=True, reason="A1 RED evidence only; later blocks implement product fixes")


@dataclass(frozen=True)
class _ApiContext:
    client: TestClient
    headers: dict[str, str]
    book_id: int
    session_factory: sessionmaker


@pytest.fixture(autouse=True)
def _clear_app_overrides():
    app.dependency_overrides.clear()
    get_settings.cache_clear()
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture(scope="module")
def real_shape_fixture(tmp_path_factory) -> RealShapeRegressionFixture:
    return generate_real_shape_regression_fixture(tmp_path_factory.mktemp("real-shape-regression"))


def _service(fixture: RealShapeRegressionFixture) -> GnuCashBookService:
    return GnuCashBookService({"uri_or_path": str(fixture.source_path), "base_currency": BASE_CURRENCY})


def _create_api_context(tmp_path: Path, fixture: RealShapeRegressionFixture) -> _ApiContext:
    settings = Settings(
        app_env="test",
        app_database_url="sqlite:///:memory:",
        gnucash_book_allowed_roots=[str(fixture.root)],
        jwt_secret=JWT_SECRET,
        jwt_token_expire_minutes=30,
        app_admin_username="admin",
        app_admin_password=ADMIN_PASSWORD,
    )
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db

    with SessionLocal() as session:
        admin = User(
            username="admin",
            display_name="Synthetic Admin",
            password_hash=hash_password(ADMIN_PASSWORD),
            is_admin=True,
        )
        session.add(admin)
        session.flush()
        book = Book(
            name="Synthetic real-shape regression",
            storage_type="sqlite",
            uri_or_path=str(fixture.source_path),
            base_currency=BASE_CURRENCY,
            is_default=True,
            is_archived=False,
            is_enabled=True,
        )
        session.add(book)
        session.flush()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        book_id = int(book.id)

    client = TestClient(app)
    login = client.post("/auth/login", json={"username": "admin", "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text
    return _ApiContext(
        client=client,
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
        book_id=book_id,
        session_factory=SessionLocal,
    )


def test_generated_real_shape_fixture_source_hash_is_stable_and_readonly(tmp_path: Path) -> None:
    first = generate_real_shape_regression_fixture(tmp_path / "first")
    second = generate_real_shape_regression_fixture(tmp_path / "second")

    assert first.source_hash == second.source_hash
    assert first.target_hash_before == first.source_hash
    assert second.target_hash_before == second.source_hash
    assert first.to_manifest()["source_hash_algorithm"] == SOURCE_HASH_ALGORITHM
    assert first.expected["source_hash_algorithm"] == SOURCE_HASH_ALGORITHM
    assert canonical_sqlite_hash(first.source_path) == first.source_hash
    assert canonical_sqlite_hash(first.target_path) == first.target_hash_before
    assert sha256_file(first.source_path) == sha256_file(first.target_path)
    assert not (first.source_path.stat().st_mode & 0o222)
    assert first.target_path.stat().st_mode & 0o200
    assert first.expected["contains_real_data"] is False
    assert first.expected["account_count"] >= 200
    assert first.expected["transaction_count"] >= 2_000
    assert first.expected["wide_child_count"] > 64
    assert "Активы" in first.expected["unicode_account_full_name"]
    assert Decimal(first.expected["as_of"][EARLY_AS_OF_DATE.isoformat()]["assets"]) != Decimal(
        first.expected["as_of"][LATE_AS_OF_DATE.isoformat()]["assets"]
    )


def test_generated_real_shape_fixture_cli_source_hash_is_stable(tmp_path: Path) -> None:
    script = Path(__file__).parent / "support" / "generate_real_shape_regression_fixture.py"
    first_manifest_path = tmp_path / "cli-first" / "manifest.json"
    second_manifest_path = tmp_path / "cli-second" / "manifest.json"

    for root, manifest_path in (
        (tmp_path / "cli-first", first_manifest_path),
        (tmp_path / "cli-second", second_manifest_path),
    ):
        result = subprocess.run(
            [sys.executable, str(script), str(root), "--manifest", str(manifest_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        assert result.stdout == ""

    first = json.loads(first_manifest_path.read_text(encoding="utf-8"))
    second = json.loads(second_manifest_path.read_text(encoding="utf-8"))

    assert first["source_hash_algorithm"] == SOURCE_HASH_ALGORITHM
    assert second["source_hash_algorithm"] == SOURCE_HASH_ALGORITHM
    assert first["source_hash"] == second["source_hash"]
    assert first["target_hash_before"] == first["source_hash"]
    assert second["target_hash_before"] == second["source_hash"]


def test_generated_real_shape_fixture_source_hash_survives_readonly_service_operations(
    real_shape_fixture: RealShapeRegressionFixture,
) -> None:
    before = canonical_sqlite_hash(real_shape_fixture.source_path)
    service = _service(real_shape_fixture)

    assert service.check_connection() is True
    service.get_report_summary(EARLY_AS_OF_DATE)
    service.get_report_summary(LATE_AS_OF_DATE)
    assert service.list_transactions(limit=25)

    after = canonical_sqlite_hash(real_shape_fixture.source_path)
    assert after == before == real_shape_fixture.source_hash


def test_generated_real_shape_fixture_has_mandatory_model_edges(real_shape_fixture: RealShapeRegressionFixture) -> None:
    accounts = real_shape_fixture.accounts
    expected = real_shape_fixture.expected

    assert len(expected["wide_child_ids"]) == expected["wide_child_count"]
    assert accounts["credit_card"]["type"] == "CREDIT"
    assert accounts["credit_card"]["currency"] == BASE_CURRENCY
    assert accounts["placeholder_leaf"]["placeholder"] is True
    assert accounts["hidden_expense"]["hidden"] is True
    assert accounts["usd_bank"]["currency"] == expected["secondary_currency"]
    assert accounts["btc_wallet"]["currency"] == expected["security_mnemonic"]
    assert accounts["template_checking"]["ordinary_visible"] is False
    assert accounts["visible_template_named"]["ordinary_visible"] is True


def test_a2_net_worth_uses_natural_liabilities_and_assets_minus_liabilities(
    real_shape_fixture: RealShapeRegressionFixture,
) -> None:
    service = _service(real_shape_fixture)
    report = service.get_report_summary(LATE_AS_OF_DATE)
    expected = real_shape_fixture.expected["as_of"][LATE_AS_OF_DATE.isoformat()]

    assert report.status == "ready"
    assert report.assets == expected["assets"]
    assert report.liabilities == expected["liabilities"]
    assert report.net_worth == expected["net_worth"]
    assert Decimal(report.net_worth) == Decimal(report.assets) - Decimal(report.liabilities)


@RED_XFAIL
def test_red_historical_as_of_balances_ignore_later_balance_sheet_splits(
    real_shape_fixture: RealShapeRegressionFixture,
) -> None:
    service = _service(real_shape_fixture)
    early = service.get_report_summary(EARLY_AS_OF_DATE)
    late = service.get_report_summary(LATE_AS_OF_DATE)
    early_expected = real_shape_fixture.expected["as_of"][EARLY_AS_OF_DATE.isoformat()]
    late_expected = real_shape_fixture.expected["as_of"][LATE_AS_OF_DATE.isoformat()]

    assert early.status == "ready"
    assert late.status == "ready"
    assert early.assets == early_expected["assets"]
    assert early.liabilities == early_expected["liabilities"]
    assert late.assets == late_expected["assets"]
    assert late.liabilities == late_expected["liabilities"]
    assert early.assets != late.assets
    assert early.net_worth != late.net_worth


@RED_XFAIL
def test_red_shallow_wide_account_tree_does_not_trip_depth_guard(real_shape_fixture: RealShapeRegressionFixture) -> None:
    service = _service(real_shape_fixture)

    tree = service.get_account_tree()
    by_id = {node.id: node for node in tree}
    frontier = list(tree)
    while frontier:
        node = frontier.pop()
        by_id[node.id] = node
        frontier.extend(node.children)
    wide = by_id[real_shape_fixture.expected["wide_parent_id"]]

    assert len(wide.children) == real_shape_fixture.expected["wide_child_count"]
    assert len(wide.children) > 64


@RED_XFAIL
def test_red_transactions_have_bounded_selectable_account_options_prerequisite(
    tmp_path: Path,
    real_shape_fixture: RealShapeRegressionFixture,
) -> None:
    ctx = _create_api_context(tmp_path, real_shape_fixture)

    response = ctx.client.get(
        f"/books/{ctx.book_id}/accounts/options?purpose=transactions_filter&limit=25",
        headers=ctx.headers,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["purpose"] == "transactions_filter"
    assert payload["items"]
    assert payload["limit"] == 25
    assert "next_cursor" in payload
    assert any(item["id"] == real_shape_fixture.expected["primary_bank_id"] for item in payload["items"])
    assert all("balance" not in item for item in payload["items"])
    assert all(item.get("selectable") is True for item in payload["items"])
