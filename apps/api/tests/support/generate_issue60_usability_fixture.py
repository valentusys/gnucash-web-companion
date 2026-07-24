"""Fixed-seed generated GnuCash fixture for issue #60 backend usability tests.

The generator writes only under a caller-supplied temporary root.  It creates a
read-only source book and a separate disposable working copy so tests and browser
proofs never need a committed raw GnuCash database.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
from typing import Any

import piecash
from piecash import Account, Commodity, Split, Transaction

FIXTURE_SEED = 60060
BASE_CURRENCY = "RUB"
SECONDARY_CURRENCY = "USD"
SECURITY_MNEMONIC = "BTC"


def guid(label: str, *, seed: int = FIXTURE_SEED) -> str:
    return hashlib.sha256(f"issue60:{seed}:{label}".encode("utf-8")).hexdigest()[:32]


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class Issue60Fixture:
    root: Path
    source_path: Path
    target_path: Path
    source_hash: str
    target_hash_before: str
    seed: int
    accounts: dict[str, dict[str, str]] = field(default_factory=dict)
    transactions: dict[str, str] = field(default_factory=dict)
    expected: dict[str, Any] = field(default_factory=dict)

    def to_manifest(self) -> dict[str, Any]:
        return {
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


def generate_issue60_usability_fixture(root: Path | str, *, seed: int = FIXTURE_SEED) -> Issue60Fixture:
    """Create a source book plus disposable working copy under ``root``."""

    root_path = Path(root).resolve()
    source_root = root_path / "source"
    target_root = root_path / "working"
    source_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    source_path = source_root / "issue60-usability-source.gnucash.sqlite"
    target_path = target_root / "issue60-usability-working.gnucash.sqlite"
    for path in (source_path, target_path):
        if path.exists():
            path.chmod(0o600)
            path.unlink()

    accounts, transactions, default_ids = _create_source_book(source_path, seed=seed)
    _stabilize_default_identity(source_path, default_ids, seed=seed)
    source_hash = sha256_file(source_path)
    source_path.chmod(0o444)
    shutil.copy2(source_path, target_path)
    target_path.chmod(0o600)
    target_hash_before = sha256_file(target_path)

    return Issue60Fixture(
        root=root_path,
        source_path=source_path,
        target_path=target_path,
        source_hash=source_hash,
        target_hash_before=target_hash_before,
        seed=seed,
        accounts=accounts,
        transactions=transactions,
        expected={
            "reporting_currency": BASE_CURRENCY,
            "excluded_currencies": [SECONDARY_CURRENCY],
            "non_currency_commodities_excluded": True,
            "source_create_count": 1,
            "disposable_copy_count": 1,
            "synthetic_app_metadata_mutation_count": 0,
            "target_create_count": 0,
            "target_patch_count": 0,
            "target_delete_count": 0,
            "duplicate_confirm_count": 0,
            "owner_private_access_count": 0,
            "committed_raw_artifacts": 0,
        },
    )


def cleanup_issue60_usability_fixture(fixture: Issue60Fixture) -> None:
    if fixture.root.exists():
        shutil.rmtree(fixture.root)


def _assign_guid(obj: Any, value: str) -> Any:
    obj.guid = value
    return obj


def _make_commodity(book: Any, *, namespace: str, mnemonic: str, fullname: str, fraction: int, guid_value: str) -> Commodity:
    for commodity in book.commodities:
        if getattr(commodity, "namespace", None) == namespace and getattr(commodity, "mnemonic", None) == mnemonic:
            return commodity
    commodity = Commodity(namespace=namespace, mnemonic=mnemonic, fullname=fullname, fraction=fraction)
    return _assign_guid(commodity, guid_value)


def _account_record(account: Account) -> dict[str, str]:
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
    }


def _account(
    *,
    label: str,
    name: str,
    type: str,
    parent: Any,
    commodity: Commodity | None,
    placeholder: bool = False,
    hidden: bool = False,
    code: str = "",
) -> Account:
    return _assign_guid(
        Account(
            name=name,
            type=type,
            parent=parent,
            commodity=commodity,
            placeholder=placeholder,
            hidden=hidden,
            code=code,
        ),
        guid(label),
    )


def _transaction(
    *,
    label: str,
    currency: Commodity,
    description: str,
    post_date: date,
    splits: list[tuple[Account, str, str]],
) -> Transaction:
    tx = _assign_guid(
        Transaction(
            currency=currency,
            description=description,
            post_date=post_date,
            splits=[Split(account=account, value=Decimal(value), memo=memo) for account, value, memo in splits],
        ),
        guid(f"tx:{label}"),
    )
    for index, split in enumerate(tx.splits):
        _assign_guid(split, guid(f"split:{label}:{index}"))
    return tx


def _create_source_book(path: Path, *, seed: int) -> tuple[dict[str, dict[str, str]], dict[str, str], dict[str, str]]:
    book = piecash.create_book(currency=BASE_CURRENCY, sqlite_file=str(path), overwrite=True)
    try:
        root = book.root_account
        template_root = book.root_template
        rub = book.default_currency
        if root is None or template_root is None or rub is None:
            raise RuntimeError("piecash.create_book did not expose the required root/default identities")
        usd = _make_commodity(
            book,
            namespace="CURRENCY",
            mnemonic=SECONDARY_CURRENCY,
            fullname="US Dollar",
            fraction=100,
            guid_value=guid("commodity:usd", seed=seed),
        )
        btc = _make_commodity(
            book,
            namespace="CRYPTO",
            mnemonic=SECURITY_MNEMONIC,
            fullname="Bitcoin security placeholder",
            fraction=100000000,
            guid_value=guid("commodity:btc", seed=seed),
        )

        assets = _account(label="account:assets", name="Активы", type="ASSET", parent=root, commodity=rub, placeholder=True)
        banks = _account(label="account:assets:banks", name="Банки", type="ASSET", parent=assets, commodity=rub, placeholder=True)
        sber = _account(label="account:assets:banks:sber", name="Сбербанк", type="BANK", parent=banks, commodity=rub, code="1000")
        vtb = _account(label="account:assets:banks:vtb", name="ВТБ", type="BANK", parent=banks, commodity=rub)
        alfa = _account(label="account:assets:banks:alfa", name="Альфа", type="BANK", parent=banks, commodity=rub)
        business = _account(label="account:assets:business", name="Бизнес", type="ASSET", parent=assets, commodity=rub, placeholder=True)
        business_sber = _account(label="account:assets:business:sber", name="Сбербанк", type="BANK", parent=business, commodity=rub, code="2000")
        cash = _account(label="account:assets:cash", name="Наличные", type="CASH", parent=assets, commodity=rub)
        usd_cash = _account(label="account:assets:usd", name="Доллары", type="BANK", parent=assets, commodity=usd)
        investments = _account(label="account:assets:investments", name="Инвестиции", type="ASSET", parent=assets, commodity=rub, placeholder=True)
        btc_account = _account(label="account:assets:investments:btc", name="BTC", type="STOCK", parent=investments, commodity=btc)
        visible_template_named = _account(label="account:assets:template-visible", name="Template Root", type="BANK", parent=assets, commodity=rub)

        liabilities = _account(label="account:liabilities", name="Обязательства", type="LIABILITY", parent=root, commodity=rub, placeholder=True)
        card = _account(label="account:liabilities:card", name="Кредитная карта", type="CREDIT", parent=liabilities, commodity=rub)

        income = _account(label="account:income", name="Доходы", type="INCOME", parent=root, commodity=rub, placeholder=True)
        salary = _account(label="account:income:salary", name="Зарплата", type="INCOME", parent=income, commodity=rub)

        expenses = _account(label="account:expenses", name="Расходы", type="EXPENSE", parent=root, commodity=rub, placeholder=True)
        products = _account(label="account:expenses:products", name="Продукты", type="EXPENSE", parent=expenses, commodity=rub)
        building = _account(label="account:expenses:building", name="Строительство", type="EXPENSE", parent=expenses, commodity=rub)
        transport = _account(label="account:expenses:transport", name="Транспорт", type="EXPENSE", parent=expenses, commodity=rub)
        usd_travel = _account(label="account:expenses:usd-travel", name="USD Travel", type="EXPENSE", parent=expenses, commodity=usd)
        fees = _account(label="account:expenses:fees", name="Комиссии", type="EXPENSE", parent=expenses, commodity=rub)

        equity = _account(label="account:equity", name="Капитал", type="EQUITY", parent=root, commodity=rub, placeholder=True)
        opening = _account(label="account:equity:opening", name="Открытие", type="EQUITY", parent=equity, commodity=rub)
        opening_usd = _account(label="account:equity:opening-usd", name="Opening USD", type="EQUITY", parent=equity, commodity=usd)

        template_checking = _account(label="account:template:checking", name="Сбербанк", type="BANK", parent=template_root, commodity=rub)
        template_food = _account(label="account:template:food", name="Продукты", type="EXPENSE", parent=template_root, commodity=rub)

        tx_by_label = {
            "opening": _transaction(
                label="opening",
                currency=rub,
                description="Начальные остатки",
                post_date=date(2026, 1, 1),
                splits=[
                    (sber, "100000.00", "opening sber"),
                    (vtb, "50000.00", "opening vtb"),
                    (cash, "10000.00", "opening cash"),
                    (business_sber, "25000.00", "opening business"),
                    (card, "-10000.00", "opening card"),
                    (opening, "-175000.00", "opening equity"),
                ],
            ),
            "salary": _transaction(
                label="salary",
                currency=rub,
                description="Зарплата июль",
                post_date=date(2026, 7, 1),
                splits=[(salary, "-120000.00", "начисление"), (vtb, "120000.00", "поступление")],
            ),
            "building": _transaction(
                label="building",
                currency=rub,
                description="Покупка стройматериалов — юникод ✓",
                post_date=date(2026, 7, 2),
                splits=[(sber, "-1000.00", "оплата"), (building, "1000.00", "краска")],
            ),
            "transfer": _transaction(
                label="transfer",
                currency=rub,
                description="Перевод Сбербанк ВТБ",
                post_date=date(2026, 7, 3),
                splits=[(sber, "-5000.00", "исходящий"), (vtb, "5000.00", "входящий")],
            ),
            "three_split": _transaction(
                label="three-split",
                currency=rub,
                description="Покупка продукты и транспорт",
                post_date=date(2026, 7, 4),
                splits=[(vtb, "-3000.00", "карта"), (products, "2500.00", "еда"), (transport, "500.00", "такси")],
            ),
            "card": _transaction(
                label="card",
                currency=rub,
                description="Кредитная карта продукты",
                post_date=date(2026, 7, 5),
                splits=[(card, "-700.00", "card charge"), (products, "700.00", "food")],
            ),
            "repeated": _transaction(
                label="repeated",
                currency=rub,
                description="Две строки продуктов",
                post_date=date(2026, 7, 6),
                splits=[(sber, "-200.00", "total"), (products, "120.00", "part 1"), (products, "80.00", "part 2")],
            ),
            "zero": _transaction(
                label="zero",
                currency=rub,
                description="Нулевая техническая строка",
                post_date=date(2026, 7, 7),
                splits=[(sber, "-150.00", "paid"), (transport, "150.00", "ride"), (alfa, "0.00", "technical zero")],
            ),
            "empty_description": _transaction(
                label="empty-description",
                currency=rub,
                description="",
                post_date=date(2026, 7, 8),
                splits=[(cash, "-50.00", "cash out"), (sber, "50.00", "cash in")],
            ),
            "usd": _transaction(
                label="usd",
                currency=usd,
                description="USD hotel",
                post_date=date(2026, 7, 9),
                splits=[(usd_cash, "-120.00", "usd cash"), (usd_travel, "120.00", "hotel")],
            ),
            "security": _transaction(
                label="security",
                currency=rub,
                description="Покупка BTC без оценки валюты",
                post_date=date(2026, 7, 10),
                splits=[(sber, "-10000.00", "cash leg"), (btc_account, "10000.00", "security value")],
            ),
            "same_account_both_sides": _transaction(
                label="same-account-both-sides",
                currency=rub,
                description="Один счет с обеих сторон",
                post_date=date(2026, 7, 11),
                splits=[(sber, "-10.00", "negative"), (sber, "10.00", "positive")],
            ),
            "visible_template_named": _transaction(
                label="visible-template-named",
                currency=rub,
                description="Видимый счет с Template в имени",
                post_date=date(2026, 7, 12),
                splits=[(visible_template_named, "-42.00", "visible template name"), (fees, "42.00", "fee")],
            ),
            "template_hidden": _transaction(
                label="template-hidden",
                currency=rub,
                description="Template transaction must stay hidden",
                post_date=date(2026, 7, 13),
                splits=[(template_checking, "-1.00", "template"), (template_food, "1.00", "template")],
            ),
        }
        book.save()
        accounts = {
            "root": {"id": guid("default:root", seed=seed), "name": "Root Account", "type": "ROOT", "currency": BASE_CURRENCY, "namespace": "CURRENCY", "full_name": ""},
            "template_root": {"id": guid("default:template-root", seed=seed), "name": "Template Root", "type": "ROOT", "currency": "", "namespace": "", "full_name": ""},
        }
        for key, account in {
            "assets": assets,
            "banks": banks,
            "sber": sber,
            "vtb": vtb,
            "alfa": alfa,
            "business_sber": business_sber,
            "cash": cash,
            "usd_cash": usd_cash,
            "btc": btc_account,
            "visible_template_named": visible_template_named,
            "liabilities": liabilities,
            "card": card,
            "salary": salary,
            "products": products,
            "building": building,
            "transport": transport,
            "usd_travel": usd_travel,
            "fees": fees,
            "opening": opening,
            "opening_usd": opening_usd,
            "template_checking": template_checking,
            "template_food": template_food,
        }.items():
            accounts[key] = _account_record(account)
        transactions = {key: str(tx.guid) for key, tx in tx_by_label.items()}
        default_ids = {
            "old_book": str(book.guid),
            "old_root": str(root.guid),
            "old_template_root": str(template_root.guid),
            "old_rub": str(rub.guid),
            "new_book": guid("default:book", seed=seed),
            "new_root": accounts["root"]["id"],
            "new_template_root": accounts["template_root"]["id"],
            "new_rub": guid("commodity:rub", seed=seed),
        }
        return accounts, transactions, default_ids
    finally:
        book.close()


def _stabilize_default_identity(path: Path, default_ids: dict[str, str], *, seed: int) -> None:
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
        con.execute("update transactions set enter_date = '2026-07-24 00:00:00'")
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the issue #60 usability fixture under a temp root.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--manifest", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    fixture = generate_issue60_usability_fixture(args.root)
    manifest = fixture.to_manifest()
    if args.manifest is not None:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    else:
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
