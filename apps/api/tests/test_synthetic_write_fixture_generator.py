"""Synthetic write-fixture generator tests.

The generator must create disposable GnuCash SQLite books only in pytest tmp
paths or ignored generated-fixture paths.  No generated SQLite book is tracked by
git; tests validate the predictable synthetic account model through the same
read-only service used by API routes.
"""

from __future__ import annotations

import importlib.util
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest

from app.services.gnucash_book import GnuCashBookService

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "create_synthetic_write_fixture.py"

EXPECTED_ACCOUNT_TYPES = {
    "Assets": "ASSET",
    "Assets:Checking": "BANK",
    "Assets:Savings": "BANK",
    "Equity": "EQUITY",
    "Equity:Opening Balances": "EQUITY",
    "Expenses": "EXPENSE",
    "Expenses:Dining": "EXPENSE",
    "Expenses:Future Placeholder": "EXPENSE",
    "Expenses:Groceries": "EXPENSE",
    "Expenses:Transport": "EXPENSE",
    "Expenses:Utilities": "EXPENSE",
    "Income": "INCOME",
    "Income:Interest": "INCOME",
    "Income:Salary": "INCOME",
    "Liabilities": "LIABILITY",
    "Liabilities:Credit Card": "CREDIT",
}

EXPECTED_BALANCES = {
    "Assets": "3264.75",
    "Assets:Checking": "2454.75",
    "Assets:Savings": "810.00",
    "Equity": "1500.00",
    "Equity:Opening Balances": "1500.00",
    "Expenses": "745.25",
    "Expenses:Dining": "75.00",
    "Expenses:Future Placeholder": "0.00",
    "Expenses:Groceries": "200.25",
    "Expenses:Transport": "100.00",
    "Expenses:Utilities": "370.00",
    "Income": "2510.00",
    "Income:Interest": "10.00",
    "Income:Salary": "2500.00",
    "Liabilities": "-0.00",
    "Liabilities:Credit Card": "-0.00",
}

EXPECTED_DESCRIPTIONS = {
    "Synthetic fixture opening checking",
    "Synthetic fixture opening savings",
    "Synthetic fixture salary",
    "Synthetic fixture interest",
    "Synthetic fixture groceries",
    "Synthetic fixture utilities",
    "Synthetic fixture monthly split",
    "Synthetic fixture transfer to savings",
    "Synthetic fixture card dining",
    "Synthetic fixture card payment",
}


def _load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("create_synthetic_write_fixture", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generator() -> ModuleType:
    return _load_generator()


@pytest.fixture
def generated_fixture_path(tmp_path: Path, generator: ModuleType) -> Path:
    return generator.create_fixture(tmp_path / "synthetic-write-fixture.gnucash.sqlite")


def test_generator_creates_predictable_account_tree_and_balances(
    generated_fixture_path: Path,
    generator: ModuleType,
) -> None:
    assert generated_fixture_path.exists()
    assert "tests/fixtures" not in generated_fixture_path.as_posix()

    snapshot = generator.account_snapshot(generated_fixture_path)

    assert [item["full_name"] for item in snapshot] == sorted(EXPECTED_ACCOUNT_TYPES)
    assert {item["full_name"]: item["type"] for item in snapshot} == EXPECTED_ACCOUNT_TYPES
    assert {item["full_name"]: item["balance"] for item in snapshot} == EXPECTED_BALANCES
    assert {item["currency"] for item in snapshot} == {"SEK"}
    assert {
        item["full_name"] for item in snapshot if item["placeholder"]
    } == {"Expenses:Future Placeholder"}


def test_read_only_service_loads_generated_fixture_without_mutating_it(
    generated_fixture_path: Path,
    generator: ModuleType,
) -> None:
    before = generator.sha256_file(generated_fixture_path)
    service = GnuCashBookService({"uri_or_path": str(generated_fixture_path), "base_currency": "SEK"})

    assert service.check_connection() is True
    accounts = service.list_accounts()
    assert {account.full_name: account.balance for account in accounts} == EXPECTED_BALANCES

    tree = service.get_account_tree()
    assert {node.name for node in tree} == {"Assets", "Equity", "Expenses", "Income", "Liabilities"}
    assets = next(node for node in tree if node.name == "Assets")
    assert {child.name for child in assets.children} == {"Checking", "Savings"}
    expenses = next(node for node in tree if node.name == "Expenses")
    assert {child.name for child in expenses.children} == {
        "Dining",
        "Future Placeholder",
        "Groceries",
        "Transport",
        "Utilities",
    }

    after = generator.sha256_file(generated_fixture_path)
    assert after == before


def test_generated_fixture_transactions_are_balanced_and_repeatable(
    tmp_path: Path,
    generator: ModuleType,
) -> None:
    first = generator.create_fixture(tmp_path / "first.gnucash.sqlite")
    second = generator.create_fixture(tmp_path / "second.gnucash.sqlite")

    assert generator.account_balance_snapshot(first) == EXPECTED_BALANCES
    assert generator.account_balance_snapshot(second) == EXPECTED_BALANCES
    assert set(generator.transaction_descriptions(first)) == EXPECTED_DESCRIPTIONS
    assert set(generator.transaction_descriptions(second)) == EXPECTED_DESCRIPTIONS

    service = GnuCashBookService({"uri_or_path": str(first), "base_currency": "SEK"})
    transactions = service.list_transactions(limit=100)
    assert len(transactions) == len(EXPECTED_DESCRIPTIONS)

    monthly_split = next(
        transaction for transaction in transactions if transaction.description == "Synthetic fixture monthly split"
    )
    detail = service.get_transaction(monthly_split.id)
    assert len(detail.splits) == 4
    assert {split.account_name for split in detail.splits} == {
        "Assets:Checking",
        "Expenses:Groceries",
        "Expenses:Transport",
        "Expenses:Utilities",
    }

    for transaction in transactions:
        detail = service.get_transaction(transaction.id)
        split_total = sum(Decimal(split.amount) for split in detail.splits)
        assert split_total == Decimal("0.00")


def test_metadata_and_account_lookup_are_safe_for_test_payloads(
    generated_fixture_path: Path,
    generator: ModuleType,
) -> None:
    lookup = generator.account_lookup(generated_fixture_path)
    metadata = generator.fixture_metadata(generated_fixture_path)

    assert set(lookup) == set(EXPECTED_ACCOUNT_TYPES)
    assert lookup["Assets:Checking"]
    assert lookup["Expenses:Groceries"]
    assert metadata["fixture_id"] == "synthetic-write-fixture-v1"
    assert metadata["format"] == "GnuCash SQLite"
    assert metadata["base_currency"] == "SEK"
    assert metadata["contains_real_data"] is False
    assert metadata["account_count_expected"] == len(EXPECTED_ACCOUNT_TYPES)
    assert metadata["transaction_count_expected"] == len(EXPECTED_DESCRIPTIONS)
    assert metadata["account_paths"] == sorted(EXPECTED_ACCOUNT_TYPES)
    assert metadata["expected_balances"] == EXPECTED_BALANCES
    assert metadata["versions"]["Gnucash"] >= 3000000
    assert len(metadata["sha256"]) == 64
    assert str(generated_fixture_path.parent) not in str(metadata)


def test_account_lookup_helpers_return_required_guids_and_clear_missing_paths(
    generated_fixture_path: Path,
    generator: ModuleType,
) -> None:
    required_paths = ("Assets:Checking", "Expenses:Groceries")

    required_lookup = generator.require_account_guids(generated_fixture_path, required_paths)

    assert list(required_lookup) == list(required_paths)
    assert required_lookup["Assets:Checking"] == generator.account_guid(
        generated_fixture_path, "Assets:Checking"
    )
    assert required_lookup["Expenses:Groceries"] == generator.account_guid(
        generated_fixture_path, "Expenses:Groceries"
    )

    with pytest.raises(KeyError, match="Expenses:Missing") as excinfo:
        generator.account_guid(generated_fixture_path, "Expenses:Missing")
    assert "Assets:Checking" in str(excinfo.value)
    assert str(generated_fixture_path.parent) not in str(excinfo.value)


def test_account_lookup_fails_closed_on_duplicate_account_paths(
    generated_fixture_path: Path,
    generator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    safe_rows = [
        {"full_name": "Assets:Checking", "guid": "guid-a"},
        {"full_name": "Assets:Checking", "guid": "guid-b"},
        {"full_name": "Expenses:Groceries", "guid": "guid-c"},
    ]
    monkeypatch.setattr(generator, "account_snapshot", lambda path: safe_rows)

    with pytest.raises(ValueError, match="duplicate synthetic account path") as excinfo:
        generator.account_lookup(generated_fixture_path)

    assert "Assets:Checking" in str(excinfo.value)
    assert "guid-a" not in str(excinfo.value)
    assert "guid-b" not in str(excinfo.value)
    assert str(generated_fixture_path.parent) not in str(excinfo.value)


def test_expected_balance_helpers_are_derived_and_report_drift(
    generated_fixture_path: Path,
    generator: ModuleType,
) -> None:
    assert generator.expected_balance_snapshot() == EXPECTED_BALANCES
    generator.assert_expected_balances(generated_fixture_path)

    drifted = dict(EXPECTED_BALANCES)
    drifted["Assets:Checking"] = "999.00"
    with pytest.raises(AssertionError, match="Assets:Checking") as excinfo:
        generator.assert_expected_balances(generated_fixture_path, expected=drifted)
    assert "expected 999.00, got 2454.75" in str(excinfo.value)


def test_generator_refuses_repo_tracked_fixture_paths(generator: ModuleType) -> None:
    tracked_fixture_dir = REPO_ROOT / "apps" / "api" / "tests" / "fixtures"

    with pytest.raises(ValueError, match="tracked repository paths"):
        generator.create_fixture(tracked_fixture_dir / "do-not-create.gnucash.sqlite")
