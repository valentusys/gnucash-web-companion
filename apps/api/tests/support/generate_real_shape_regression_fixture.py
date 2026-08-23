"""Deterministic generated real-shape GnuCash fixture for read-only regression tests.

The fixture models only structural characteristics observed in large real books:
wide shallow hierarchies, many ordinary accounts, liability raw-negative splits,
as-of balance movement, Unicode labels, many transactions, templates, placeholders,
hidden accounts, and multi-currency edges. It never reads or copies any owner book.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
from typing import Any, Iterable

import piecash
from piecash import Account, Commodity, Split, Transaction

FIXTURE_SEED = 228810
BASE_CURRENCY = "RUB"
SECONDARY_CURRENCY = "USD"
SECURITY_MNEMONIC = "BTC"
FIXTURE_ID = "readonly-real-shape-regression-v1"
EARLY_AS_OF_DATE = date(2026, 3, 31)
LATE_AS_OF_DATE = date(2026, 12, 31)
WIDE_CHILD_COUNT = 80
EXPENSE_CHILD_COUNT = 120
INCOME_CHILD_COUNT = 20
ROUTE_TIMING_TRANSACTION_COUNT = 2_005
MONEY_QUANT = Decimal("0.01")
BALANCE_SHEET_ASSET_TYPES = frozenset({"ASSET", "BANK", "CASH", "RECEIVABLE"})
BALANCE_SHEET_LIABILITY_TYPES = frozenset({"LIABILITY", "CREDIT", "PAYABLE"})


def guid(label: str, *, seed: int = FIXTURE_SEED) -> str:
    """Return a stable 32-character GUID compatible with GnuCash SQLite."""

    return hashlib.sha256(f"real-shape:{seed}:{label}".encode("utf-8")).hexdigest()[:32]


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class RealShapeRegressionFixture:
    root: Path
    source_path: Path
    target_path: Path
    source_hash: str
    target_hash_before: str
    seed: int
    accounts: dict[str, dict[str, Any]] = field(default_factory=dict)
    transactions: dict[str, str] = field(default_factory=dict)
    expected: dict[str, Any] = field(default_factory=dict)

    def to_manifest(self) -> dict[str, Any]:
        return {
            "fixture_id": FIXTURE_ID,
            "seed": self.seed,
            "root": str(self.root),
            "source_path": str(self.source_path),
            "target_path": str(self.target_path),
            "source_hash": self.source_hash,
            "target_hash_before": self.target_hash_before,
            "accounts": self.accounts,
            "transactions": self.transactions,
            "expected": self.expected,
        }


@dataclass(frozen=True)
class _SplitSpec:
    account_key: str
    amount: Decimal
    memo: str
    currency: str


@dataclass(frozen=True)
class _TransactionSpec:
    label: str
    description: str
    post_date: date
    currency: str
    splits: tuple[_SplitSpec, ...]


def generate_real_shape_regression_fixture(root: Path | str, *, seed: int = FIXTURE_SEED) -> RealShapeRegressionFixture:
    """Create a read-only source book plus disposable working copy under ``root``."""

    root_path = Path(root).resolve()
    source_root = root_path / "source"
    target_root = root_path / "working"
    source_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    source_path = source_root / "readonly-real-shape-source.gnucash.sqlite"
    target_path = target_root / "readonly-real-shape-working.gnucash.sqlite"
    for path in (source_path, target_path):
        if path.exists():
            path.chmod(0o600)
            path.unlink()

    creation = _create_source_book(source_path, seed=seed)
    _stabilize_default_identity(source_path, creation["default_ids"])
    source_hash = sha256_file(source_path)
    source_path.chmod(0o444)
    shutil.copy2(source_path, target_path)
    target_path.chmod(0o600)
    target_hash_before = sha256_file(target_path)

    expected = _expected_contract(creation["accounts"], creation["transaction_specs"])
    expected.update(
        {
            "fixture_id": FIXTURE_ID,
            "contains_real_data": False,
            "account_count": len(creation["accounts"]),
            "transaction_count": len(creation["transaction_specs"]),
            "wide_child_count": WIDE_CHILD_COUNT,
            "expense_child_count": EXPENSE_CHILD_COUNT,
            "income_child_count": INCOME_CHILD_COUNT,
            "route_timing_transaction_count": ROUTE_TIMING_TRANSACTION_COUNT,
            "as_of_dates": [EARLY_AS_OF_DATE.isoformat(), LATE_AS_OF_DATE.isoformat()],
            "base_currency": BASE_CURRENCY,
            "secondary_currency": SECONDARY_CURRENCY,
            "security_mnemonic": SECURITY_MNEMONIC,
        }
    )

    return RealShapeRegressionFixture(
        root=root_path,
        source_path=source_path,
        target_path=target_path,
        source_hash=source_hash,
        target_hash_before=target_hash_before,
        seed=seed,
        accounts=creation["accounts"],
        transactions=creation["transactions"],
        expected=expected,
    )


def _create_source_book(path: Path, *, seed: int) -> dict[str, Any]:
    book = piecash.create_book(currency=BASE_CURRENCY, sqlite_file=str(path), overwrite=True)
    accounts: dict[str, Account] = {}
    transactions: dict[str, str] = {}
    transaction_specs = _build_transaction_specs(seed=seed)
    try:
        root = book.root_account
        template_root = book.root_template
        rub = book.default_currency
        if root is None or template_root is None or rub is None:
            raise RuntimeError("piecash.create_book did not expose root/template/default currency")

        usd = _make_commodity(
            book,
            namespace="CURRENCY",
            mnemonic=SECONDARY_CURRENCY,
            fullname="US Dollar synthetic edge",
            fraction=100,
            guid_value=guid("commodity:usd", seed=seed),
        )
        btc = _make_commodity(
            book,
            namespace="CRYPTO",
            mnemonic=SECURITY_MNEMONIC,
            fullname="Bitcoin synthetic security edge",
            fraction=100000000,
            guid_value=guid("commodity:btc", seed=seed),
        )

        accounts.update(
            {
                "assets": _account("account:assets", "Активы", "ASSET", root, rub, seed=seed, placeholder=True),
                "liabilities": _account(
                    "account:liabilities", "Обязательства", "LIABILITY", root, rub, seed=seed, placeholder=True
                ),
                "income": _account("account:income", "Доходы", "INCOME", root, rub, seed=seed, placeholder=True),
                "expenses": _account("account:expenses", "Расходы", "EXPENSE", root, rub, seed=seed, placeholder=True),
                "equity": _account("account:equity", "Капитал", "EQUITY", root, rub, seed=seed, placeholder=True),
            }
        )
        accounts["banks"] = _account(
            "account:assets:banks", "Банки", "ASSET", accounts["assets"], rub, seed=seed, placeholder=True
        )
        accounts["expense_wide_parent"] = _account(
            "account:expenses:wide", "Широкие расходы", "EXPENSE", accounts["expenses"], rub, seed=seed, placeholder=True
        )
        accounts.update(
            {
                "primary_bank": _account("account:assets:banks:primary", "Основной счёт", "BANK", accounts["banks"], rub, seed=seed),
                "reserve_bank": _account("account:assets:banks:reserve", "Резервный счёт", "BANK", accounts["banks"], rub, seed=seed),
                "cash": _account("account:assets:cash", "Наличные ₽", "CASH", accounts["assets"], rub, seed=seed),
                "wide_parent": _account("account:assets:wide", "Широкая группа", "ASSET", accounts["assets"], rub, seed=seed, placeholder=True),
                "visible_template_named": _account(
                    "account:assets:visible-template-named",
                    "Template в имени",
                    "BANK",
                    accounts["assets"],
                    rub,
                    seed=seed,
                ),
                "usd_bank": _account("account:assets:usd", "USD синтетика", "BANK", accounts["assets"], usd, seed=seed),
                "btc_wallet": _account("account:assets:btc", "BTC синтетика", "STOCK", accounts["assets"], btc, seed=seed),
                "credit_card": _account(
                    "account:liabilities:card", "Кредитная карта", "CREDIT", accounts["liabilities"], rub, seed=seed
                ),
                "loan": _account("account:liabilities:loan", "Займ", "LIABILITY", accounts["liabilities"], rub, seed=seed),
                "salary": _account("account:income:salary", "Зарплата", "INCOME", accounts["income"], rub, seed=seed),
                "interest": _account("account:income:interest", "Проценты", "INCOME", accounts["income"], rub, seed=seed),
                "groceries": _account("account:expenses:groceries", "Продукты", "EXPENSE", accounts["expenses"], rub, seed=seed),
                "utilities": _account("account:expenses:utilities", "Коммунальные", "EXPENSE", accounts["expenses"], rub, seed=seed),
                "fees": _account("account:expenses:fees", "Комиссии", "EXPENSE", accounts["expenses"], rub, seed=seed),
                "placeholder_leaf": _account(
                    "account:expenses:placeholder", "Будущий плейсхолдер", "EXPENSE", accounts["expenses"], rub, seed=seed, placeholder=True
                ),
                "hidden_expense": _account(
                    "account:expenses:hidden", "Скрытая синтетика", "EXPENSE", accounts["expenses"], rub, seed=seed, hidden=True
                ),
                "usd_travel": _account("account:expenses:usd", "USD Travel", "EXPENSE", accounts["expenses"], usd, seed=seed),
                "opening": _account("account:equity:opening", "Открытие", "EQUITY", accounts["equity"], rub, seed=seed),
                "opening_usd": _account("account:equity:opening-usd", "Opening USD", "EQUITY", accounts["equity"], usd, seed=seed),
                "template_checking": _account(
                    "account:template:checking", "Шаблон банк", "BANK", template_root, rub, seed=seed
                ),
                "template_food": _account(
                    "account:template:food", "Шаблон расход", "EXPENSE", template_root, rub, seed=seed
                ),
            }
        )

        for index in range(WIDE_CHILD_COUNT):
            accounts[f"wide_{index:03d}"] = _account(
                f"account:assets:wide:{index:03d}",
                f"Широкий счёт {index:03d}",
                "BANK",
                accounts["wide_parent"],
                rub,
                seed=seed,
            )
        for index in range(EXPENSE_CHILD_COUNT):
            accounts[f"expense_{index:03d}"] = _account(
                f"account:expenses:wide:{index:03d}",
                f"Категория расхода {index:03d}",
                "EXPENSE",
                accounts["expense_wide_parent"],
                rub,
                seed=seed,
            )
        for index in range(INCOME_CHILD_COUNT):
            accounts[f"income_{index:03d}"] = _account(
                f"account:income:wide:{index:03d}",
                f"Источник дохода {index:03d}",
                "INCOME",
                accounts["income"],
                rub,
                seed=seed,
            )

        for spec in transaction_specs:
            currency = rub if spec.currency == BASE_CURRENCY else usd
            tx = _transaction(
                spec.label,
                currency,
                spec.description,
                spec.post_date,
                [(accounts[split.account_key], split.amount, split.memo) for split in spec.splits],
                seed=seed,
            )
            transactions[spec.label] = str(tx.guid)

        book.save()
        default_ids = {
            "old_book": str(book.guid),
            "old_root": str(root.guid),
            "old_template_root": str(template_root.guid),
            "old_rub": str(rub.guid),
            "new_book": guid("default:book", seed=seed),
            "new_root": guid("default:root", seed=seed),
            "new_template_root": guid("default:template-root", seed=seed),
            "new_rub": guid("commodity:rub", seed=seed),
        }
        account_records = {
            "root": {
                "id": default_ids["new_root"],
                "name": "Root Account",
                "full_name": "",
                "type": "ROOT",
                "currency": BASE_CURRENCY,
                "namespace": "CURRENCY",
                "placeholder": False,
                "hidden": False,
                "ordinary_visible": False,
            },
            "template_root": {
                "id": default_ids["new_template_root"],
                "name": "Template Root",
                "full_name": "",
                "type": "ROOT",
                "currency": "",
                "namespace": "",
                "placeholder": False,
                "hidden": False,
                "ordinary_visible": False,
            },
        }
        template_keys = {"template_checking", "template_food"}
        for key, account in accounts.items():
            record = _account_record(account)
            record["ordinary_visible"] = key not in template_keys
            account_records[key] = record
        return {
            "accounts": account_records,
            "transactions": transactions,
            "transaction_specs": transaction_specs,
            "default_ids": default_ids,
        }
    finally:
        book.close()


def _build_transaction_specs(*, seed: int) -> list[_TransactionSpec]:
    specs: list[_TransactionSpec] = []

    def add(label: str, description: str, post_date: date, splits: Iterable[tuple[str, str, str]], currency: str = BASE_CURRENCY) -> None:
        split_specs = tuple(
            _SplitSpec(account_key=account_key, amount=Decimal(value), memo=memo, currency=currency)
            for account_key, value, memo in splits
        )
        split_total = sum((split.amount for split in split_specs), Decimal("0.00"))
        if split_total != Decimal("0.00"):
            raise ValueError(f"synthetic transaction is not balanced: {label} total={split_total}")
        specs.append(_TransactionSpec(label=label, description=description, post_date=post_date, currency=currency, splits=split_specs))

    add(
        "opening",
        "Синтетические начальные остатки",
        date(2026, 1, 1),
        [
            ("primary_bank", "100000.00", "opening primary"),
            ("reserve_bank", "50000.00", "opening reserve"),
            ("cash", "25000.00", "opening cash"),
            ("credit_card", "-10000.00", "opening card raw negative"),
            ("loan", "-40000.00", "opening loan raw negative"),
            ("opening", "-125000.00", "opening equity"),
        ],
    )
    add(
        "early_expense_marker",
        "Синтетическая ранняя трата",
        date(2026, 2, 15),
        [("primary_bank", "-3000.00", "early outflow"), ("groceries", "3000.00", "early expense")],
    )
    add(
        "liability_charge_marker",
        "Синтетическая операция по кредитке",
        date(2026, 3, 1),
        [("credit_card", "-5000.00", "card raw negative"), ("utilities", "5000.00", "card expense")],
    )
    add(
        "late_income_marker",
        "Синтетическое позднее поступление",
        date(2026, 8, 15),
        [("salary", "-20000.00", "late income"), ("primary_bank", "20000.00", "late inflow")],
    )
    add(
        "late_liability_payment_marker",
        "Синтетическое позднее погашение",
        date(2026, 9, 1),
        [("primary_bank", "-1000.00", "payment"), ("credit_card", "1000.00", "reduce raw liability")],
    )
    add(
        "usd_edge",
        "Synthetic USD edge without FX",
        date(2026, 4, 1),
        [("usd_bank", "-120.00", "usd cash"), ("usd_travel", "120.00", "usd travel")],
        currency=SECONDARY_CURRENCY,
    )
    add(
        "template_hidden_edge",
        "Template transaction must stay outside ordinary flows",
        date(2026, 4, 2),
        [("template_checking", "-1.00", "template"), ("template_food", "1.00", "template")],
    )
    add(
        "visible_template_name_edge",
        "Visible account whose name contains Template",
        date(2026, 4, 3),
        [("visible_template_named", "-42.00", "visible template name"), ("fees", "42.00", "fee")],
    )

    start = date(2026, 1, 2)
    for index in range(ROUTE_TIMING_TRANSACTION_COUNT):
        post_date = start + timedelta(days=index % 360)
        rubles = (index % 37) + 1
        kopecks = index % 100
        amount = Decimal(f"{rubles}.{kopecks:02d}")
        if index % 50 == 0:
            income_key = f"income_{index % INCOME_CHILD_COUNT:03d}"
            splits = [(income_key, str(-amount), "route income"), ("primary_bank", str(amount), "route inflow")]
        elif index % 25 == 0:
            expense_key = f"expense_{index % EXPENSE_CHILD_COUNT:03d}"
            splits = [("credit_card", str(-amount), "route card raw negative"), (expense_key, str(amount), "route expense")]
        else:
            expense_key = f"expense_{index % EXPENSE_CHILD_COUNT:03d}"
            splits = [("primary_bank", str(-amount), "route payment"), (expense_key, str(amount), "route expense")]
        add(
            f"route_timing_{index:04d}",
            f"Synthetic route timing row {index:04d}",
            post_date,
            splits,
        )
    return specs


def _expected_contract(accounts: dict[str, dict[str, Any]], specs: list[_TransactionSpec]) -> dict[str, Any]:
    as_of: dict[str, dict[str, str]] = {}
    for cutoff in (EARLY_AS_OF_DATE, LATE_AS_OF_DATE):
        assets_raw = Decimal("0.00")
        liabilities_raw = Decimal("0.00")
        for spec in specs:
            if spec.post_date > cutoff:
                continue
            for split in spec.splits:
                account = accounts[split.account_key]
                if split.currency != BASE_CURRENCY:
                    continue
                if not account.get("ordinary_visible", True):
                    continue
                if account.get("placeholder"):
                    continue
                account_type = str(account["type"]).upper()
                if account_type in BALANCE_SHEET_ASSET_TYPES:
                    assets_raw += split.amount
                elif account_type in BALANCE_SHEET_LIABILITY_TYPES:
                    liabilities_raw += split.amount
        liabilities = -liabilities_raw
        net_worth = assets_raw - liabilities
        as_of[cutoff.isoformat()] = {
            "assets": _format_money(assets_raw),
            "liabilities": _format_money(liabilities),
            "net_worth": _format_money(net_worth),
        }
    return {
        "as_of": as_of,
        "wide_parent_id": accounts["wide_parent"]["id"],
        "wide_child_ids": [accounts[f"wide_{index:03d}"]["id"] for index in range(WIDE_CHILD_COUNT)],
        "primary_bank_id": accounts["primary_bank"]["id"],
        "credit_card_id": accounts["credit_card"]["id"],
        "template_account_ids": [accounts["template_checking"]["id"], accounts["template_food"]["id"]],
        "placeholder_account_id": accounts["placeholder_leaf"]["id"],
        "hidden_account_id": accounts["hidden_expense"]["id"],
        "unicode_account_full_name": accounts["primary_bank"]["full_name"],
    }


def _assign_guid(obj: Any, guid_value: str) -> Any:
    obj.guid = guid_value
    return obj


def _make_commodity(
    book: Any,
    *,
    namespace: str,
    mnemonic: str,
    fullname: str,
    fraction: int,
    guid_value: str,
) -> Commodity:
    for commodity in book.commodities:
        if getattr(commodity, "namespace", None) == namespace and getattr(commodity, "mnemonic", None) == mnemonic:
            return _assign_guid(commodity, guid_value)
    return _assign_guid(Commodity(namespace=namespace, mnemonic=mnemonic, fullname=fullname, fraction=fraction), guid_value)


def _account(
    label: str,
    name: str,
    type: str,
    parent: Any,
    commodity: Commodity,
    *,
    seed: int,
    placeholder: bool = False,
    hidden: bool = False,
) -> Account:
    return _assign_guid(
        Account(name=name, type=type, parent=parent, commodity=commodity, placeholder=placeholder, hidden=hidden),
        guid(label, seed=seed),
    )


def _transaction(
    label: str,
    currency: Commodity,
    description: str,
    post_date: date,
    splits: Iterable[tuple[Account, Decimal, str]],
    *,
    seed: int,
) -> Transaction:
    tx = _assign_guid(
        Transaction(
            currency=currency,
            description=description,
            post_date=post_date,
            splits=[Split(account=account, value=amount, memo=memo) for account, amount, memo in splits],
        ),
        guid(f"tx:{label}", seed=seed),
    )
    for index, split in enumerate(tx.splits):
        _assign_guid(split, guid(f"split:{label}:{index}", seed=seed))
    return tx


def _account_record(account: Account) -> dict[str, Any]:
    names: list[str] = []
    current: Any = account
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        account_type = str(getattr(current, "type", "") or "").upper()
        name = str(getattr(current, "name", "") or "")
        if account_type != "ROOT" and name:
            names.append(name)
        current = getattr(current, "parent", None)
    commodity = getattr(account, "commodity", None)
    return {
        "id": str(account.guid),
        "name": str(account.name),
        "full_name": ":".join(reversed(names)),
        "type": str(account.type).upper(),
        "currency": str(getattr(commodity, "mnemonic", "") or "").upper(),
        "namespace": str(getattr(commodity, "namespace", "") or "").upper(),
        "placeholder": bool(getattr(account, "placeholder", False)),
        "hidden": bool(getattr(account, "hidden", False)),
    }


def _stabilize_default_identity(path: Path, default_ids: dict[str, str]) -> None:
    con = sqlite3.connect(path)
    try:
        old_book = default_ids["old_book"]
        old_root = default_ids["old_root"]
        old_template_root = default_ids["old_template_root"]
        old_rub = default_ids["old_rub"]
        new_book = default_ids["new_book"]
        new_root = default_ids["new_root"]
        new_template_root = default_ids["new_template_root"]
        new_rub = default_ids["new_rub"]
        con.execute(
            "update books set guid = ?, root_account_guid = ?, root_template_guid = ? where guid = ?",
            (new_book, new_root, new_template_root, old_book),
        )
        con.execute("update accounts set guid = ? where guid = ?", (new_root, old_root))
        con.execute("update accounts set guid = ? where guid = ?", (new_template_root, old_template_root))
        con.execute("update accounts set parent_guid = ? where parent_guid = ?", (new_root, old_root))
        con.execute("update accounts set parent_guid = ? where parent_guid = ?", (new_template_root, old_template_root))
        con.execute("update commodities set guid = ? where guid = ?", (new_rub, old_rub))
        con.execute("update accounts set commodity_guid = ? where commodity_guid = ?", (new_rub, old_rub))
        con.execute("update transactions set currency_guid = ? where currency_guid = ?", (new_rub, old_rub))
        con.execute("update transactions set enter_date = '2026-08-23 00:00:00'")
        con.execute("update splits set account_guid = ? where account_guid = ?", (new_root, old_root))
        con.execute("update splits set account_guid = ? where account_guid = ?", (new_template_root, old_template_root))
        con.execute("update slots set obj_guid = ? where obj_guid = ?", (new_book, old_book))
        con.execute("update slots set obj_guid = ? where obj_guid = ?", (new_root, old_root))
        con.execute("update slots set obj_guid = ? where obj_guid = ?", (new_template_root, old_template_root))
        con.execute("update slots set obj_guid = ? where obj_guid = ?", (new_rub, old_rub))
        con.execute("update slots set guid_val = ? where guid_val = ?", (new_book, old_book))
        con.execute("update slots set guid_val = ? where guid_val = ?", (new_root, old_root))
        con.execute("update slots set guid_val = ? where guid_val = ?", (new_template_root, old_template_root))
        con.execute("update slots set guid_val = ? where guid_val = ?", (new_rub, old_rub))
        con.execute("delete from prices")
        con.commit()
        con.execute("vacuum")
    finally:
        con.close()


def _format_money(value: Decimal) -> str:
    return str(value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the read-only real-shape regression fixture under a temp root.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--manifest", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    fixture = generate_real_shape_regression_fixture(args.root)
    manifest = fixture.to_manifest()
    if args.manifest is not None:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
