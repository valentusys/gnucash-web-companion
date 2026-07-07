#!/usr/bin/env python3
"""Generate a disposable synthetic GnuCash SQLite fixture for write tests.

The fixture is intentionally boring and deterministic at the data-model level:
account paths, account types, transaction descriptions, split amounts, and
resulting balances are fixed.  GnuCash/piecash still allocate fresh GUIDs per
file, so tests should use account_lookup() instead of hard-coded IDs.

Safety posture:
- Generates synthetic data only.
- Refuses to write inside tracked repository paths.
- Default output is under apps/api/tests/generated-fixtures/, which is ignored.
- Does not read, copy, or mutate owner/private/original/only-copy books.
"""

import argparse
import hashlib
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from importlib import metadata as importlib_metadata
import json
import platform
import sqlite3
import sys
from pathlib import Path
from typing import Any

import piecash
from piecash import Account, Split, Transaction

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_CURRENCY = "SEK"
FIXTURE_ID = "synthetic-write-fixture-v1"
GENERATOR_VERSION = "synthetic-write-fixture-v1"
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT
    / "apps"
    / "api"
    / "tests"
    / "generated-fixtures"
    / "synthetic-write-fixture.gnucash.sqlite"
)
ALLOWED_REPO_OUTPUT_DIRS = (
    REPO_ROOT / "apps" / "api" / "tests" / "generated-fixtures",
)

MONEY_QUANT = Decimal("0.01")


@dataclass(frozen=True)
class AccountSpec:
    full_name: str
    type: str
    parent_full_name: str | None
    placeholder: bool = False

    @property
    def name(self) -> str:
        return self.full_name.rsplit(":", 1)[-1]


@dataclass(frozen=True)
class SplitSpec:
    account_full_name: str
    amount: Decimal
    memo: str = ""


@dataclass(frozen=True)
class TransactionSpec:
    description: str
    post_date: date
    splits: tuple[SplitSpec, ...]


ACCOUNT_SPECS: tuple[AccountSpec, ...] = (
    AccountSpec("Assets", "ASSET", None),
    AccountSpec("Assets:Checking", "BANK", "Assets"),
    AccountSpec("Assets:Savings", "BANK", "Assets"),
    AccountSpec("Liabilities", "LIABILITY", None),
    AccountSpec("Liabilities:Credit Card", "CREDIT", "Liabilities"),
    AccountSpec("Income", "INCOME", None),
    AccountSpec("Income:Salary", "INCOME", "Income"),
    AccountSpec("Income:Interest", "INCOME", "Income"),
    AccountSpec("Expenses", "EXPENSE", None),
    AccountSpec("Expenses:Groceries", "EXPENSE", "Expenses"),
    AccountSpec("Expenses:Utilities", "EXPENSE", "Expenses"),
    AccountSpec("Expenses:Transport", "EXPENSE", "Expenses"),
    AccountSpec("Expenses:Dining", "EXPENSE", "Expenses"),
    AccountSpec("Expenses:Future Placeholder", "EXPENSE", "Expenses", placeholder=True),
    AccountSpec("Equity", "EQUITY", None),
    AccountSpec("Equity:Opening Balances", "EQUITY", "Equity"),
)

TRANSACTION_SPECS: tuple[TransactionSpec, ...] = (
    TransactionSpec(
        "Synthetic fixture opening checking",
        date(2026, 1, 1),
        (
            SplitSpec("Equity:Opening Balances", Decimal("-1000.00")),
            SplitSpec("Assets:Checking", Decimal("1000.00")),
        ),
    ),
    TransactionSpec(
        "Synthetic fixture opening savings",
        date(2026, 1, 1),
        (
            SplitSpec("Equity:Opening Balances", Decimal("-500.00")),
            SplitSpec("Assets:Savings", Decimal("500.00")),
        ),
    ),
    TransactionSpec(
        "Synthetic fixture salary",
        date(2026, 1, 5),
        (
            SplitSpec("Income:Salary", Decimal("-2500.00")),
            SplitSpec("Assets:Checking", Decimal("2500.00")),
        ),
    ),
    TransactionSpec(
        "Synthetic fixture interest",
        date(2026, 1, 10),
        (
            SplitSpec("Income:Interest", Decimal("-10.00")),
            SplitSpec("Assets:Savings", Decimal("10.00")),
        ),
    ),
    TransactionSpec(
        "Synthetic fixture groceries",
        date(2026, 1, 12),
        (
            SplitSpec("Assets:Checking", Decimal("-120.25")),
            SplitSpec("Expenses:Groceries", Decimal("120.25")),
        ),
    ),
    TransactionSpec(
        "Synthetic fixture utilities",
        date(2026, 1, 16),
        (
            SplitSpec("Assets:Checking", Decimal("-200.00")),
            SplitSpec("Expenses:Utilities", Decimal("200.00")),
        ),
    ),
    TransactionSpec(
        "Synthetic fixture monthly split",
        date(2026, 1, 20),
        (
            SplitSpec("Assets:Checking", Decimal("-350.00")),
            SplitSpec("Expenses:Groceries", Decimal("80.00")),
            SplitSpec("Expenses:Utilities", Decimal("170.00")),
            SplitSpec("Expenses:Transport", Decimal("100.00")),
        ),
    ),
    TransactionSpec(
        "Synthetic fixture transfer to savings",
        date(2026, 1, 22),
        (
            SplitSpec("Assets:Checking", Decimal("-300.00")),
            SplitSpec("Assets:Savings", Decimal("300.00")),
        ),
    ),
    TransactionSpec(
        "Synthetic fixture card dining",
        date(2026, 1, 24),
        (
            SplitSpec("Liabilities:Credit Card", Decimal("-75.00")),
            SplitSpec("Expenses:Dining", Decimal("75.00")),
        ),
    ),
    TransactionSpec(
        "Synthetic fixture card payment",
        date(2026, 1, 28),
        (
            SplitSpec("Assets:Checking", Decimal("-75.00")),
            SplitSpec("Liabilities:Credit Card", Decimal("75.00")),
        ),
    ),
)

EXPECTED_ACCOUNT_TYPES: dict[str, str] = {
    spec.full_name: spec.type for spec in sorted(ACCOUNT_SPECS, key=lambda item: item.full_name)
}
EXPECTED_BALANCES: dict[str, str] = {
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


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _validate_output_path(output_path: Path) -> None:
    resolved = output_path.resolve(strict=False)
    if _is_relative_to(resolved, REPO_ROOT):
        if not any(_is_relative_to(resolved, allowed) for allowed in ALLOWED_REPO_OUTPUT_DIRS):
            raise ValueError(
                "refusing to write generated SQLite fixture inside tracked repository paths; "
                "use apps/api/tests/generated-fixtures/ or an external temporary directory"
            )


def _format_money(value: Any) -> str:
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return str(value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP))


def _account_full_name(account: Any) -> str:
    names: list[str] = []
    current = account
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        name = getattr(current, "name", None)
        account_type = str(getattr(current, "type", "") or "").upper()
        is_root = account_type == "ROOT" and str(name or "") == "Root Account"
        if name and not is_root:
            names.append(str(name))
        current = getattr(current, "parent", None)
    return ":".join(reversed(names))


def _account_balance(account: Any) -> Decimal:
    get_balance = getattr(account, "get_balance", None)
    if callable(get_balance):
        return Decimal(str(get_balance()))
    total = Decimal("0")
    for split in getattr(account, "splits", []) or []:
        total += Decimal(str(getattr(split, "value", "0")))
    return total


def _open_book_readonly(path: str | Path) -> Any:
    return piecash.open_book(str(path), readonly=True)


def create_fixture(output_path: str | Path = DEFAULT_OUTPUT_PATH) -> Path:
    """Create the disposable synthetic GnuCash SQLite fixture and return its path."""

    output = Path(output_path)
    _validate_output_path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    book = piecash.create_book(currency=BASE_CURRENCY, sqlite_file=str(output))
    try:
        currency = book.commodities[0]
        root = book.root_account
        accounts: dict[str, Any] = {}

        for spec in ACCOUNT_SPECS:
            parent = root if spec.parent_full_name is None else accounts[spec.parent_full_name]
            accounts[spec.full_name] = Account(
                name=spec.name,
                type=spec.type,
                parent=parent,
                commodity=currency,
                placeholder=spec.placeholder,
            )

        for spec in TRANSACTION_SPECS:
            split_total = sum((split.amount for split in spec.splits), Decimal("0"))
            if split_total != Decimal("0.00"):
                raise ValueError(f"transaction does not balance: {spec.description}")
            Transaction(
                currency=currency,
                description=spec.description,
                post_date=spec.post_date,
                splits=[
                    Split(
                        account=accounts[split.account_full_name],
                        value=split.amount,
                        memo=split.memo,
                    )
                    for split in spec.splits
                ],
            )

        book.save()
    finally:
        book.close()

    return output


def account_snapshot(path: str | Path) -> list[dict[str, Any]]:
    """Return deterministic account metadata from a generated fixture."""

    book = _open_book_readonly(path)
    try:
        rows = []
        for account in getattr(book, "accounts", []) or []:
            rows.append(
                {
                    "full_name": _account_full_name(account),
                    "name": str(getattr(account, "name", "")),
                    "guid": str(getattr(account, "guid", "")),
                    "type": str(getattr(account, "type", "")),
                    "currency": str(getattr(getattr(account, "commodity", None), "mnemonic", BASE_CURRENCY)),
                    "balance": _format_money(_account_balance(account)),
                    "placeholder": bool(getattr(account, "placeholder", False)),
                    "hidden": bool(getattr(account, "hidden", False)),
                }
            )
        rows.sort(key=lambda item: item["full_name"])
        return rows
    finally:
        book.close()


def account_lookup(path: str | Path) -> dict[str, str]:
    """Return account full-name to GUID mapping for generated test payloads."""

    return {item["full_name"]: item["guid"] for item in account_snapshot(path)}


def account_balance_snapshot(path: str | Path) -> dict[str, str]:
    """Return account full-name to balance mapping for repeatability assertions."""

    return {item["full_name"]: item["balance"] for item in account_snapshot(path)}


def transaction_descriptions(path: str | Path) -> list[str]:
    """Return generated transaction descriptions sorted by text."""

    book = _open_book_readonly(path)
    try:
        descriptions = [str(getattr(tx, "description", "")) for tx in getattr(book, "transactions", []) or []]
        return sorted(descriptions)
    finally:
        book.close()


def read_versions(path: str | Path) -> dict[str, int]:
    """Read SQLite versions-table markers without exposing row data."""

    with sqlite3.connect(str(path)) as conn:
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


def _package_version(package_name: str) -> str:
    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        return "not installed"


def runtime_context() -> dict[str, str]:
    """Return safe local toolchain metadata for generated-fixture provenance."""

    return {
        "generator_version": GENERATOR_VERSION,
        "os": platform.platform(),
        "python_version": sys.version.split()[0],
        "sqlite_version": sqlite3.sqlite_version,
        "piecash_version": _package_version("piecash"),
    }


def fixture_metadata(path: str | Path) -> dict[str, Any]:
    """Return non-sensitive metadata for a generated synthetic fixture."""

    return {
        "fixture_id": FIXTURE_ID,
        "generator": "scripts/create_synthetic_write_fixture.py",
        "format": "GnuCash SQLite",
        "base_currency": BASE_CURRENCY,
        "source": "synthetic disposable fixture generated with piecash",
        "contains_real_data": False,
        "account_count_expected": len(ACCOUNT_SPECS),
        "transaction_count_expected": len(TRANSACTION_SPECS),
        "account_paths": sorted(EXPECTED_ACCOUNT_TYPES),
        "account_types": EXPECTED_ACCOUNT_TYPES,
        "expected_balances": EXPECTED_BALANCES,
        "transaction_descriptions": sorted(spec.description for spec in TRANSACTION_SPECS),
        "runtime_context": runtime_context(),
        "versions": read_versions(path),
        "sha256": sha256_file(path),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a disposable synthetic GnuCash SQLite fixture for backend write tests."
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Output .gnucash.sqlite path. Defaults to ignored apps/api/tests/generated-fixtures/.",
    )
    parser.add_argument(
        "--metadata-json",
        action="store_true",
        help="Write redacted synthetic metadata next to the generated fixture.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output = create_fixture(args.output)
    metadata = fixture_metadata(output)
    if account_balance_snapshot(output) != EXPECTED_BALANCES:
        raise RuntimeError("generated fixture balances do not match EXPECTED_BALANCES")
    if args.metadata_json:
        metadata_path = output.with_suffix(output.suffix + ".metadata.json")
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"metadata_json={metadata_path}")
    print(f"fixture={output}")
    print(f"fixture_id={metadata['fixture_id']}")
    print(f"account_count={metadata['account_count_expected']}")
    print(f"transaction_count={metadata['transaction_count_expected']}")
    print(f"sha256={metadata['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
