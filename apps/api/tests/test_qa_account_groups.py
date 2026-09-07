"""Deterministic synthetic group totals: no private book is a fixture."""
from decimal import Decimal
from pathlib import Path
import hashlib
import sqlite3

from app.services.gnucash_book import GnuCashBookService
from tests.support.generate_qa_regression_fixture import SCENARIOS, generate_qa_regression_fixture


def test_group_fixture_and_full_recursive_totals(tmp_path):
    assert "account_groups" in SCENARIOS, "QA-05 requires deterministic nested/truncated groups"
    first = generate_qa_regression_fixture(tmp_path / "one", scenario="account_groups")
    second = generate_qa_regression_fixture(tmp_path / "two", scenario="account_groups")
    path = Path(first["book_path"])
    assert path.read_bytes() == Path(second["book_path"]).read_bytes()
    service = GnuCashBookService({"uri_or_path": str(path), "base_currency": "RUB"})
    group = service.get_account_overview(first["accounts"]["group"], book_id=1)
    assert group.placeholder is True
    assert group.child_count == 205
    assert group.children_returned == 200
    assert group.children_truncated is True
    assert first["accounts"]["last"] not in {child.id for child in group.children}
    totals = {bucket.commodity.mnemonic: Decimal(bucket.amount) for bucket in group.recursive_balances}
    assert totals == {"RUB": Decimal("100") - Decimal("25") + Decimal("7") + Decimal("11"), "USD": Decimal("5"), "EUR": Decimal("-2.5")}
    assert group.direct_balance.amount == "0"
    assert group.includes_currency_conversion is False
    assert not group.scan.limits.get("unbounded")
    for key, amount in [("negative", "-25"), ("zero", "0"), ("last", "7")]:
        leaf = service.get_account_overview(first["accounts"][key], book_id=1)
        assert Decimal(leaf.direct_balance.amount) == Decimal(amount)
    nested = service.get_account_overview(first["accounts"]["nested"], book_id=1)
    assert nested.placeholder is True
    assert nested.child_count == 3
    assert {bucket.commodity.mnemonic: Decimal(bucket.amount) for bucket in nested.recursive_balances} == {"RUB": Decimal("11"), "USD": Decimal("5"), "EUR": Decimal("-2.5")}
    assert hashlib.sha256(path.read_bytes()).hexdigest() == first["sha256"]
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        assert db.execute("pragma quick_check").fetchone() == ("ok",)
