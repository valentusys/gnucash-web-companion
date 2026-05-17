#!/usr/bin/env python3
"""Create a synthetic multi-currency GnuCash SQLite fixture for integration tests.

This script generates a disposable GnuCash book with:
- Base currency: SEK
- One EUR expense account with EUR-denominated transactions
- SEK-only accounts for comparison
- Generic descriptions only — no real financial data

The fixture is used to validate that report endpoints correctly exclude
non-base-currency accounts/splits.

Usage:
    python apps/api/scripts/create_multicurrency_fixture.py
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
    """Create a synthetic multi-currency GnuCash SQLite book at the given path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing file to ensure clean state
    if output_path.exists():
        output_path.unlink()

    book = piecash.create_book(currency="SEK", sqlite_file=str(output_path))
    sek = book.commodities[0]
    root = book.root_account

    # Create EUR commodity
    eur = piecash.Commodity(
        book=book,
        fullname="Euro",
        mnemonic="EUR",
        fraction=100,
        namespace="CURRENCY",
    )

    # SEK account tree (same as single-currency fixture)
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

    # EUR account tree
    eur_income = Account(
        name="EUR Income", type="INCOME", parent=root, commodity=eur
    )
    eur_expenses = Account(
        name="EUR Expenses", type="EXPENSE", parent=root, commodity=eur
    )
    eur_travel = Account(
        name="EUR Travel", type="EXPENSE", parent=eur_expenses, commodity=eur
    )

    # SEK-only transactions (same as single-currency fixture)
    transactions = [
        Transaction(
            currency=sek,
            description="January salary",
            post_date=date(2026, 1, 15),
            splits=[
                Split(account=salary, value=Decimal("-5000.00")),
                Split(account=checking, value=Decimal("5000.00")),
            ],
        ),
        Transaction(
            currency=sek,
            description="Grocery store",
            post_date=date(2026, 1, 20),
            splits=[
                Split(account=checking, value=Decimal("-320.50")),
                Split(account=food, value=Decimal("320.50")),
            ],
        ),
        Transaction(
            currency=sek,
            description="Bus pass",
            post_date=date(2026, 2, 1),
            splits=[
                Split(account=checking, value=Decimal("-150.00")),
                Split(account=transport, value=Decimal("150.00")),
            ],
        ),
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
        Transaction(
            currency=sek,
            description="Credit card payment",
            post_date=date(2026, 3, 1),
            splits=[
                Split(account=checking, value=Decimal("-1000.00")),
                Split(account=credit_card, value=Decimal("1000.00")),
            ],
        ),
        # EUR-denominated transaction (should be excluded from SEK reports)
        Transaction(
            currency=eur,
            description="Paris hotel",
            post_date=date(2026, 2, 10),
            splits=[
                Split(account=eur_travel, value=Decimal("120.00")),
                Split(account=eur_income, value=Decimal("-120.00")),
            ],
        ),
    ]

    book.save()
    book.close()

    return output_path


def main() -> None:
    """Entry point: create the fixture at the default path."""
    fixture_path = (
        Path(__file__).resolve().parent.parent
        / "tests"
        / "fixtures"
        / "test-book-multicurrency.gnucash.sqlite"
    )
    output = create_fixture(fixture_path)
    size_kb = output.stat().st_size / 1024
    print(f"Fixture created: {output} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
