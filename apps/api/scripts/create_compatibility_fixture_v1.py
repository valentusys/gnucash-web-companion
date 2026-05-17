#!/usr/bin/env python3
"""Create the Phase 46 disposable GnuCash compatibility fixture v1.

This generator is intentionally synthetic and safe:
- SQLite GnuCash book generated locally through piecash
- boring fake account/transaction names only
- no real financial data, screenshots, exports, secrets, or app DB data
- read-only compatibility validation target; not a write-scope expansion

The output path defaults to an ignored generated-fixtures directory so running this
script does not add a binary fixture to git by accident.

Usage:
    python apps/api/scripts/create_compatibility_fixture_v1.py
    python apps/api/scripts/create_compatibility_fixture_v1.py /tmp/compat-v1.gnucash.sqlite
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import piecash
from piecash import Account, Split, Transaction

FIXTURE_ID = "compatibility-v1-piecash-synthetic"
BASE_CURRENCY = "SEK"
DEFAULT_OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "tests"
    / "generated-fixtures"
    / "compatibility-v1.gnucash.sqlite"
)


def create_fixture(output_path: str | Path = DEFAULT_OUTPUT_PATH) -> Path:
    """Create a deterministic disposable SQLite fixture and return its path."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    book = piecash.create_book(currency=BASE_CURRENCY, sqlite_file=str(output))
    sek = book.commodities[0]
    root = book.root_account

    # Account model based on docs/gnucash-version-fixture-plan.md.
    assets = Account(name="Assets", type="ASSET", parent=root, commodity=sek)
    checking = Account(name="Checking", type="BANK", parent=assets, commodity=sek)
    savings = Account(name="Savings", type="BANK", parent=assets, commodity=sek)
    cash = Account(name="Cash", type="CASH", parent=assets, commodity=sek)

    liabilities = Account(name="Liabilities", type="LIABILITY", parent=root, commodity=sek)
    credit_card = Account(name="Credit Card", type="CREDIT", parent=liabilities, commodity=sek)

    income = Account(name="Income", type="INCOME", parent=root, commodity=sek)
    salary = Account(name="Salary", type="INCOME", parent=income, commodity=sek)
    interest = Account(name="Interest", type="INCOME", parent=income, commodity=sek)

    expenses = Account(name="Expenses", type="EXPENSE", parent=root, commodity=sek)
    groceries = Account(name="Groceries", type="EXPENSE", parent=expenses, commodity=sek)
    utilities = Account(name="Utilities", type="EXPENSE", parent=expenses, commodity=sek)
    travel = Account(name="Travel", type="EXPENSE", parent=expenses, commodity=sek)

    equity = Account(name="Equity", type="EQUITY", parent=root, commodity=sek)
    opening_balances = Account(
        name="Opening Balances", type="EQUITY", parent=equity, commodity=sek
    )

    # Nine synthetic transactions covering opening balances, income, interest,
    # expenses, split detail, transfers, credit-card usage, and payment.
    Transaction(
        currency=sek,
        description="Fixture opening checking",
        post_date=date(2024, 1, 1),
        splits=[
            Split(account=opening_balances, value=Decimal("-1000.00")),
            Split(account=checking, value=Decimal("1000.00")),
        ],
    )
    Transaction(
        currency=sek,
        description="Fixture opening savings",
        post_date=date(2024, 1, 1),
        splits=[
            Split(account=opening_balances, value=Decimal("-2000.00")),
            Split(account=savings, value=Decimal("2000.00")),
        ],
    )
    Transaction(
        currency=sek,
        description="Fixture salary",
        post_date=date(2024, 1, 5),
        splits=[
            Split(account=salary, value=Decimal("-3000.00")),
            Split(account=checking, value=Decimal("3000.00")),
        ],
    )
    Transaction(
        currency=sek,
        description="Fixture interest",
        post_date=date(2024, 1, 10),
        splits=[
            Split(account=interest, value=Decimal("-12.34")),
            Split(account=savings, value=Decimal("12.34")),
        ],
    )
    Transaction(
        currency=sek,
        description="Fixture grocery",
        post_date=date(2024, 1, 12),
        splits=[
            Split(account=checking, value=Decimal("-123.45")),
            Split(account=groceries, value=Decimal("123.45")),
        ],
    )
    Transaction(
        currency=sek,
        description="Fixture monthly split",
        post_date=date(2024, 1, 20),
        splits=[
            Split(account=checking, value=Decimal("-240.00")),
            Split(account=groceries, value=Decimal("80.00")),
            Split(account=utilities, value=Decimal("90.00")),
            Split(account=travel, value=Decimal("70.00")),
        ],
    )
    Transaction(
        currency=sek,
        description="Fixture transfer to cash",
        post_date=date(2024, 1, 22),
        splits=[
            Split(account=checking, value=Decimal("-50.00")),
            Split(account=cash, value=Decimal("50.00")),
        ],
    )
    Transaction(
        currency=sek,
        description="Fixture credit card cycle",
        post_date=date(2024, 1, 25),
        splits=[
            Split(account=credit_card, value=Decimal("-180.00")),
            Split(account=travel, value=Decimal("180.00")),
        ],
    )
    Transaction(
        currency=sek,
        description="Fixture credit card payment",
        post_date=date(2024, 1, 28),
        splits=[
            Split(account=checking, value=Decimal("-180.00")),
            Split(account=credit_card, value=Decimal("180.00")),
        ],
    )

    book.save()
    book.close()
    return output


def read_versions(output_path: str | Path) -> dict[str, int]:
    """Read SQLite versions-table markers without exposing fixture data rows."""
    with sqlite3.connect(str(output_path)) as conn:
        rows = conn.execute(
            "select table_name, table_version from versions order by table_name"
        ).fetchall()
    return {str(name): int(version) for name, version in rows}


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fixture_metadata(output_path: str | Path) -> dict[str, Any]:
    """Return non-sensitive provenance metadata for a generated fixture."""
    path = Path(output_path)
    return {
        "fixture_id": FIXTURE_ID,
        "generator": "apps/api/scripts/create_compatibility_fixture_v1.py",
        "format": "GnuCash SQLite",
        "base_currency": BASE_CURRENCY,
        "source": "synthetic disposable fixture generated with piecash",
        "desktop_version": "not desktop-generated in Phase 46 v1",
        "contains_real_data": False,
        "account_count_expected": 15,
        "transaction_count_expected": 9,
        "versions": read_versions(path),
        "sha256": sha256_file(path),
    }


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    output_path = Path(args[0]) if args else DEFAULT_OUTPUT_PATH
    fixture_path = create_fixture(output_path)
    metadata = fixture_metadata(fixture_path)
    metadata_path = fixture_path.with_suffix(fixture_path.suffix + ".metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    size_kb = fixture_path.stat().st_size / 1024
    print(f"Fixture created: {fixture_path} ({size_kb:.1f} KB)")
    print(f"Metadata created: {metadata_path}")
    print(f"SHA-256: {metadata['sha256']}")


if __name__ == "__main__":
    main()
