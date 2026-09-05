"""QA-02 actual recent-report DTO; no explorer-shaped transport stub."""
from decimal import Decimal
import hashlib
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from app.services.gnucash_book import GnuCashBookService
from tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture
from tests.test_scheduled_transactions import point_sample_book_at
from tests.test_transactions import client, engine, session_factory, sample_book, auth_headers, auth_token


def test_recent_real_report_amount_contract(client, auth_headers, sample_book, session_factory, tmp_path):
    fixture = generate_qa_regression_fixture(tmp_path / "recent", scenario="money")
    path = Path(fixture["book_path"])
    point_sample_book_at(session_factory, sample_book, path)
    for prefix in ("", f"/books/{sample_book}"):
        response = client.get(f"{prefix}/reports/recent-transactions?limit=20", headers=auth_headers)
        assert response.status_code == 200, response.text
        rows = {item["id"]: item for item in response.json()}
        assert set(rows) == {item["id"] for item in fixture["transactions"].values()}
        for spec in fixture["transactions"].values():
            row = rows[spec["id"]]
            assert "representative_amount" not in row
            assert isinstance(row["amount"], str) and isinstance(row["currency"], str)
            assert row["amount_is_unambiguous"] == (spec["magnitude"] is not None)
            if spec["magnitude"] is not None:
                assert abs(Decimal(row["amount"])) == Decimal(spec["magnitude"])
                assert row["currency"] == spec["currency"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == fixture["sha256"]


@pytest.mark.parametrize("case,expected", [("valid", True), ("zero", True), ("one", False), ("same_account", False), ("missing_account", False), ("mixed", False), ("unbalanced", False), ("quantity_differs", False), ("missing_currency", False), ("security_currency", False), ("security_account", False), ("missing_value", False), ("missing_quantity", False)])
def test_simple_amount_classification_is_fail_closed(case, expected):
    rub = NS(mnemonic="RUB", namespace="CURRENCY")
    a = NS(guid="a", commodity=rub)
    b = NS(guid="b", commodity=rub)
    values = [Decimal("0"), Decimal("0")] if case == "zero" else [Decimal("-2.50"), Decimal("2.50")]
    splits = [NS(account=account, value=value, quantity=value) for account, value in zip([a,b], values)]
    tx = NS(splits=splits, currency=rub)
    if case == "one": tx.splits = splits[:1]
    if case == "same_account": splits[1].account = a
    if case == "missing_account": splits[1].account = None
    if case == "mixed": b.commodity = NS(mnemonic="USD", namespace="CURRENCY")
    if case == "unbalanced": splits[1].value = splits[1].quantity = Decimal("3")
    if case == "quantity_differs": splits[1].quantity = Decimal("3")
    if case == "missing_currency": tx.currency = None
    if case == "security_currency": tx.currency = NS(mnemonic="RUB", namespace="SECURITY")
    if case == "security_account": b.commodity = NS(mnemonic="RUB", namespace="SECURITY")
    if case == "missing_value": splits[1].value = None
    if case == "missing_quantity": splits[1].quantity = None
    service = GnuCashBookService({"uri_or_path": "unused-synthetic"})
    assert service._transaction_amount_is_unambiguous(tx) is expected
    tx.splits.reverse()
    assert service._transaction_amount_is_unambiguous(tx) is expected
