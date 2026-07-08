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
from collections.abc import Iterable, Mapping
import hashlib
from dataclasses import dataclass
from datetime import date, datetime
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

BALANCE_CREDIT_ACCOUNT_TYPES = frozenset({"CREDIT", "EQUITY", "INCOME", "LIABILITY"})
NEGATIVE_ZERO_ACCOUNT_TYPES = frozenset({"CREDIT", "LIABILITY"})


def _format_money(value: Any) -> str:
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return str(value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP))


def _validate_fixture_specs() -> None:
    account_paths = {spec.full_name for spec in ACCOUNT_SPECS}
    for spec in ACCOUNT_SPECS:
        if spec.parent_full_name is not None and spec.parent_full_name not in account_paths:
            raise ValueError(f"account parent is missing: {spec.full_name} -> {spec.parent_full_name}")

    for spec in TRANSACTION_SPECS:
        split_total = sum((split.amount for split in spec.splits), Decimal("0"))
        if split_total != Decimal("0.00"):
            raise ValueError(f"transaction does not balance: {spec.description}")
        for split in spec.splits:
            if split.account_full_name not in account_paths:
                raise ValueError(
                    f"transaction references unknown account: {spec.description} -> {split.account_full_name}"
                )


def _expected_display_balance(
    full_name: str,
    raw_amount: Decimal,
    account_types: Mapping[str, str],
) -> str:
    account_type = account_types[full_name].upper()
    display_amount = -raw_amount if account_type in BALANCE_CREDIT_ACCOUNT_TYPES else raw_amount
    if display_amount == Decimal("0") and account_type in NEGATIVE_ZERO_ACCOUNT_TYPES:
        display_amount = Decimal("-0.00")
    return _format_money(display_amount)


def _calculate_expected_balances() -> dict[str, str]:
    _validate_fixture_specs()
    account_types = {spec.full_name: spec.type for spec in ACCOUNT_SPECS}
    parents = {spec.full_name: spec.parent_full_name for spec in ACCOUNT_SPECS}
    balances = {spec.full_name: Decimal("0.00") for spec in ACCOUNT_SPECS}

    for spec in TRANSACTION_SPECS:
        for split in spec.splits:
            current: str | None = split.account_full_name
            while current is not None:
                balances[current] += split.amount
                current = parents[current]

    return {
        full_name: _expected_display_balance(full_name, balances[full_name], account_types)
        for full_name in sorted(balances)
    }


EXPECTED_ACCOUNT_TYPES: dict[str, str] = {
    spec.full_name: spec.type for spec in sorted(ACCOUNT_SPECS, key=lambda item: item.full_name)
}
EXPECTED_BALANCES: dict[str, str] = _calculate_expected_balances()


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


def _format_date(value: Any) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _split_currency(account: Any) -> str:
    return str(getattr(getattr(account, "commodity", None), "mnemonic", BASE_CURRENCY))


def _normalize_split_snapshot(split: Mapping[str, Any]) -> dict[str, str]:
    return {
        "account_path": str(split["account_path"]),
        "amount": _format_money(split["amount"]),
        "memo": str(split.get("memo", "") or ""),
        "currency": str(split.get("currency", BASE_CURRENCY) or BASE_CURRENCY),
    }


def _normalize_transaction_snapshot(
    transactions: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for transaction in transactions:
        splits = [_normalize_split_snapshot(split) for split in transaction["splits"]]
        normalized.append(
            {
                "date": _format_date(transaction["date"]),
                "description": str(transaction["description"]),
                "splits": sorted(
                    splits,
                    key=lambda split: (
                        split["account_path"],
                        split["amount"],
                        split["memo"],
                    ),
                ),
            }
        )
    return sorted(normalized, key=lambda item: (item["date"], item["description"]))


def create_fixture(output_path: str | Path = DEFAULT_OUTPUT_PATH) -> Path:
    """Create the disposable synthetic GnuCash SQLite fixture and return its path."""

    _validate_fixture_specs()
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


def account_rows_by_path(path: str | Path) -> dict[str, dict[str, Any]]:
    """Return account full-name to safe account metadata rows for generated test payloads."""

    rows_by_path: dict[str, dict[str, Any]] = {}
    duplicate_paths: set[str] = set()
    for item in account_snapshot(path):
        full_name = str(item["full_name"])
        if full_name in rows_by_path:
            duplicate_paths.add(full_name)
            continue
        rows_by_path[full_name] = dict(item)
    if duplicate_paths:
        raise ValueError(
            "generated fixture has duplicate synthetic account path(s): "
            + ", ".join(sorted(duplicate_paths))
        )
    return rows_by_path


def account_lookup(path: str | Path) -> dict[str, str]:
    """Return account full-name to GUID mapping for generated test payloads."""

    return {
        full_name: str(item["guid"])
        for full_name, item in account_rows_by_path(path).items()
    }


def account_balance_snapshot(path: str | Path) -> dict[str, str]:
    """Return account full-name to balance mapping for repeatability assertions."""

    return {item["full_name"]: item["balance"] for item in account_snapshot(path)}


def expected_transaction_snapshot() -> list[dict[str, Any]]:
    """Return deterministic transaction/split specs without generated GUIDs."""

    return _normalize_transaction_snapshot(
        {
            "date": spec.post_date,
            "description": spec.description,
            "splits": [
                {
                    "account_path": split.account_full_name,
                    "amount": split.amount,
                    "memo": split.memo,
                    "currency": BASE_CURRENCY,
                }
                for split in spec.splits
            ],
        }
        for spec in TRANSACTION_SPECS
    )


def transaction_snapshot(path: str | Path) -> list[dict[str, Any]]:
    """Return deterministic transaction/split rows from a generated fixture."""

    book = _open_book_readonly(path)
    try:
        rows: list[dict[str, Any]] = []
        for transaction in getattr(book, "transactions", []) or []:
            splits = []
            for split in getattr(transaction, "splits", []) or []:
                account = getattr(split, "account", None)
                splits.append(
                    {
                        "account_path": _account_full_name(account),
                        "amount": _format_money(getattr(split, "value", "0")),
                        "memo": str(getattr(split, "memo", "") or ""),
                        "currency": _split_currency(account),
                    }
                )
            rows.append(
                {
                    "date": _format_date(getattr(transaction, "post_date", "")),
                    "description": str(getattr(transaction, "description", "")),
                    "splits": splits,
                }
            )
        return _normalize_transaction_snapshot(rows)
    finally:
        book.close()


def expected_balance_snapshot() -> dict[str, str]:
    """Return expected balances derived from the deterministic fixture specs."""

    return dict(EXPECTED_BALANCES)


def _format_missing_account_paths_message(
    missing_paths: Iterable[str],
    available_paths: Iterable[str],
) -> str:
    return (
        "generated fixture missing synthetic account path(s): "
        f"{', '.join(missing_paths)}; available synthetic account paths: "
        f"{', '.join(sorted(available_paths))}"
    )


def require_account_rows(path: str | Path, account_paths: Iterable[str]) -> dict[str, dict[str, Any]]:
    """Return metadata rows for required synthetic account paths or fail with safe context."""

    rows_by_path = account_rows_by_path(path)
    requested_paths = list(account_paths)
    missing_paths = [account_path for account_path in requested_paths if account_path not in rows_by_path]
    if missing_paths:
        raise KeyError(_format_missing_account_paths_message(missing_paths, rows_by_path))
    return {account_path: dict(rows_by_path[account_path]) for account_path in requested_paths}


def require_account_guids(path: str | Path, account_paths: Iterable[str]) -> dict[str, str]:
    """Return GUIDs for required synthetic account paths or fail with safe context."""

    return {
        account_path: str(row["guid"])
        for account_path, row in require_account_rows(path, account_paths).items()
    }


def account_guid(path: str | Path, account_path: str) -> str:
    """Return one synthetic account GUID by deterministic full account path."""

    return require_account_guids(path, (account_path,))[account_path]


def assert_expected_balances(
    path: str | Path,
    expected: Mapping[str, str] | None = None,
) -> None:
    """Assert fixture balances match expected synthetic balances with path-level drift."""

    actual_balances = account_balance_snapshot(path)
    expected_balances = dict(EXPECTED_BALANCES if expected is None else expected)
    if actual_balances == expected_balances:
        return

    actual_paths = set(actual_balances)
    expected_paths = set(expected_balances)
    missing_paths = sorted(expected_paths - actual_paths)
    unexpected_paths = sorted(actual_paths - expected_paths)
    mismatched = [
        (
            account_path,
            expected_balances[account_path],
            actual_balances[account_path],
        )
        for account_path in sorted(actual_paths & expected_paths)
        if actual_balances[account_path] != expected_balances[account_path]
    ]

    details: list[str] = []
    if missing_paths:
        details.append(f"missing accounts: {', '.join(missing_paths)}")
    if unexpected_paths:
        details.append(f"unexpected accounts: {', '.join(unexpected_paths)}")
    if mismatched:
        details.append(
            "mismatched balances: "
            + "; ".join(
                f"{account_path} expected {expected_balance}, got {actual_balance}"
                for account_path, expected_balance, actual_balance in mismatched
            )
        )

    raise AssertionError(
        "generated fixture balances differ from expected synthetic balances: "
        + " | ".join(details)
    )


def _transaction_key(transaction: Mapping[str, Any]) -> tuple[str, str]:
    return (str(transaction["date"]), str(transaction["description"]))


def _format_transaction_key(key: tuple[str, str]) -> str:
    return f"{key[0]} {key[1]}"


def _transaction_map(
    transactions: Iterable[Mapping[str, Any]],
) -> dict[tuple[str, str], Mapping[str, Any]]:
    by_key: dict[tuple[str, str], Mapping[str, Any]] = {}
    duplicate_keys: set[tuple[str, str]] = set()
    for transaction in transactions:
        key = _transaction_key(transaction)
        if key in by_key:
            duplicate_keys.add(key)
            continue
        by_key[key] = transaction
    if duplicate_keys:
        raise AssertionError(
            "generated fixture has duplicate synthetic transaction key(s): "
            + ", ".join(_format_transaction_key(key) for key in sorted(duplicate_keys))
        )
    return by_key


def _transaction_snapshot_diff(
    expected: list[dict[str, Any]],
    actual: list[dict[str, Any]],
) -> list[str]:
    expected_by_key = _transaction_map(expected)
    actual_by_key = _transaction_map(actual)
    expected_keys = set(expected_by_key)
    actual_keys = set(actual_by_key)
    missing = sorted(expected_keys - actual_keys)
    unexpected = sorted(actual_keys - expected_keys)
    mismatched = [
        key
        for key in sorted(expected_keys & actual_keys)
        if expected_by_key[key]["splits"] != actual_by_key[key]["splits"]
    ]

    details: list[str] = []
    if missing:
        details.append(
            "missing transactions: "
            + ", ".join(_format_transaction_key(key) for key in missing)
        )
    if unexpected:
        details.append(
            "unexpected transactions: "
            + ", ".join(_format_transaction_key(key) for key in unexpected)
        )
    if mismatched:
        details.append(
            "mismatched transaction splits: "
            + "; ".join(
                f"{_format_transaction_key(key)} expected "
                f"{json.dumps(expected_by_key[key]['splits'], sort_keys=True)}, got "
                f"{json.dumps(actual_by_key[key]['splits'], sort_keys=True)}"
                for key in mismatched
            )
        )
    return details


def assert_transactions_balanced(path: str | Path) -> None:
    """Assert every generated transaction has a zero-sum split total."""

    unbalanced: list[str] = []
    for transaction in transaction_snapshot(path):
        total = sum(
            (Decimal(split["amount"]) for split in transaction["splits"]),
            Decimal("0.00"),
        )
        if total != Decimal("0.00"):
            unbalanced.append(
                f"{transaction['date']} {transaction['description']} total {_format_money(total)}"
            )
    if unbalanced:
        raise AssertionError(
            "generated fixture transaction splits are not zero-sum: " + "; ".join(unbalanced)
        )


def assert_expected_transactions(
    path: str | Path,
    expected: Iterable[Mapping[str, Any]] | None = None,
) -> None:
    """Assert fixture transactions match deterministic synthetic specs without GUIDs."""

    actual_snapshot = transaction_snapshot(path)
    expected_snapshot = expected_transaction_snapshot()
    if expected is not None:
        expected_snapshot = _normalize_transaction_snapshot(expected)
    if actual_snapshot == expected_snapshot:
        return
    details = _transaction_snapshot_diff(expected_snapshot, actual_snapshot)
    raise AssertionError(
        "generated fixture transactions differ from expected synthetic transaction specs: "
        + " | ".join(details)
    )


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
        "expected_transactions": expected_transaction_snapshot(),
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
    assert_expected_balances(output)
    assert_transactions_balanced(output)
    assert_expected_transactions(output)
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
