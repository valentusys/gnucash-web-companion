#!/usr/bin/env python3
"""Create a synthetic GnuCash SQLite fixture for integration tests.

This script generates a disposable GnuCash book with:
- 1 ROOT account (auto-created by piecash) + 9 user accounts
- 5 transactions (including one multi-split)
- Single currency: SEK
- Generic descriptions only — no real financial data

Tested with piecash 1.2.1.

Usage:
    python apps/api/scripts/create_test_fixture.py
"""

from __future__ import annotations

import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import piecash
from piecash import Account, Split, Transaction


def create_fixture(output_path: str | Path) -> Path:
    """Create a synthetic GnuCash SQLite book at the given path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing file to ensure clean state
    if output_path.exists():
        output_path.unlink()

    book = piecash.create_book(currency="SEK", sqlite_file=str(output_path))
    sek = book.commodities[0]
    root = book.root_account

    # Create account tree
    # Root (auto-created by piecash, type=ROOT)
    # ├── Assets (ASSET)
    # │   └── Bank (BANK)
    # │       └── Checking (BANK)
    # ├── Expenses (EXPENSE)
    # │   ├── Food (EXPENSE)
    # │   └── Transport (EXPENSE)
    # ├── Income (INCOME)
    # │   └── Salary (INCOME)
    # └── Liabilities (LIABILITY)
    #     └── Credit Card (LIABILITY)

    assets = Account(name="Assets", type="ASSET", parent=root, commodity=sek)
    bank = Account(name="Bank", type="BANK", parent=assets, commodity=sek)
    checking = Account(name="Checking", type="BANK", parent=bank, commodity=sek)

    expenses = Account(name="Expenses", type="EXPENSE", parent=root, commodity=sek)
    food = Account(name="Food", type="EXPENSE", parent=expenses, commodity=sek)
    transport = Account(name="Transport", type="EXPENSE", parent=expenses, commodity=sek)

    income = Account(name="Income", type="INCOME", parent=root, commodity=sek)
    salary = Account(name="Salary", type="INCOME", parent=income, commodity=sek)

    liabilities = Account(name="Liabilities", type="LIABILITY", parent=root, commodity=sek)
    credit_card = Account(
        name="Credit Card", type="LIABILITY", parent=liabilities, commodity=sek
    )

    # Create 5 transactions
    transactions = [
        # 1. Salary -> Checking
        Transaction(
            currency=sek,
            description="January salary",
            post_date=date(2026, 1, 15),
            splits=[
                Split(account=salary, value=Decimal("-5000.00")),
                Split(account=checking, value=Decimal("5000.00")),
            ],
        ),
        # 2. Checking -> Food
        Transaction(
            currency=sek,
            description="Grocery store",
            post_date=date(2026, 1, 20),
            splits=[
                Split(account=checking, value=Decimal("-320.50")),
                Split(account=food, value=Decimal("320.50")),
            ],
        ),
        # 3. Checking -> Transport
        Transaction(
            currency=sek,
            description="Bus pass",
            post_date=date(2026, 2, 1),
            splits=[
                Split(account=checking, value=Decimal("-150.00")),
                Split(account=transport, value=Decimal("150.00")),
            ],
        ),
        # 4. Multi-split: Checking -> Food + Transport + Credit Card
        Transaction(
            currency=sek,
            description="Monthly expenses",
            post_date=date(2026, 2, 15),
            splits=[
                Split(account=checking, value=Decimal("-800.00")),
                Split(account=food, value=Decimal("350.00")),
                Split(account=transport, value=Decimal("200.00")),
                Split(account=credit_card, value=Decimal("250.00")),
            ],
        ),
        # 5. Checking -> Credit Card payment
        Transaction(
            currency=sek,
            description="Credit card payment",
            post_date=date(2026, 3, 1),
            splits=[
                Split(account=checking, value=Decimal("-1000.00")),
                Split(account=credit_card, value=Decimal("1000.00")),
            ],
        ),
    ]

    book.save()
    book.close()

    return output_path


def main() -> None:
    """Entry point: create the fixture at the default path."""
    fixture_path = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "test-book.gnucash.sqlite"
    output = create_fixture(fixture_path)
    size_kb = output.stat().st_size / 1024
    print(f"Fixture created: {output} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
