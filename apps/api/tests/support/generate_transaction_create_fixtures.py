"""Deterministic synthetic GnuCash fixtures for product transaction CREATE tests.

The generator is intentionally source-only: generated books, disposable targets,
backups, logs, and app metadata DBs must be written under caller-owned temp roots.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import random
import shutil
from typing import Any

import piecash
from piecash import Account, Commodity, Split, Transaction

FIXTURE_SEED = 59017
BASE_CURRENCY = "SEK"
UNICODE_CURRENCY = "SEK"
USD_CURRENCY = "USD"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _guid(seed: int, label: str) -> str:
    return hashlib.sha256(f"{seed}:{label}".encode("utf-8")).hexdigest()[:32]


def default_identity_snapshot(path: Path | str) -> dict[str, str]:
    """Return reopened default commodity/root identity for fixture drift guards."""
    book = piecash.open_book(str(path), readonly=True)
    try:
        currency = book.default_currency
        root = book.root_account
        return {
            "currency_guid": str(getattr(currency, "guid", "") or ""),
            "currency_mnemonic": str(getattr(currency, "mnemonic", "") or ""),
            "currency_namespace": str(getattr(currency, "namespace", "") or ""),
            "root_guid": str(getattr(root, "guid", "") or ""),
            "root_type": str(getattr(root, "type", "") or ""),
        }
    finally:
        book.close()


def _assign_guid(obj: Any, guid: str):
    obj.guid = guid
    return obj


@dataclass(frozen=True)
class GeneratedCreateCase:
    name: str
    kind: str
    seed: int
    synthetic_only: bool
    source_path: Path
    target_path: Path
    source_hash: str
    target_hash_before: str
    base_currency: str
    accounts: dict[str, dict[str, str]]
    request: dict[str, Any]
    expected: dict[str, Any]

    def to_manifest(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "seed": self.seed,
            "synthetic_only": self.synthetic_only,
            "source_path": str(self.source_path),
            "target_path": str(self.target_path),
            "source_hash": self.source_hash,
            "target_hash_before": self.target_hash_before,
            "base_currency": self.base_currency,
            "accounts": self.accounts,
            "request": self.request,
            "expected": self.expected,
        }


@dataclass(frozen=True)
class GeneratedCreateFixtureSet:
    seed: int
    root: Path
    source_root: Path
    target_root: Path
    cases: dict[str, GeneratedCreateCase] = field(default_factory=dict)

    def to_manifest(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "root": str(self.root),
            "source_root": str(self.source_root),
            "target_root": str(self.target_root),
            "cases": {name: case.to_manifest() for name, case in self.cases.items()},
        }


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
        "currency": str(getattr(commodity, "mnemonic", BASE_CURRENCY)).upper(),
    }


def _make_commodity(book: Any, *, namespace: str, mnemonic: str, fullname: str, fraction: int, guid: str) -> Commodity:
    for commodity in book.commodities:
        if getattr(commodity, "namespace", None) == namespace and getattr(commodity, "mnemonic", None) == mnemonic:
            return _assign_guid(commodity, guid)
    return _assign_guid(
        Commodity(namespace=namespace, mnemonic=mnemonic, fullname=fullname, fraction=fraction),
        guid,
    )


def _opening_transaction(commodity: Commodity, asset: Account, equity: Account, amount: str, *, seed: int, label: str) -> None:
    tx = _assign_guid(
        Transaction(
            currency=commodity,
            description=f"Synthetic opening balance {label}",
            post_date=date(2026, 1, 1),
            splits=[
                Split(account=asset, value=Decimal(amount), memo="synthetic opening asset"),
                Split(account=equity, value=-Decimal(amount), memo="synthetic opening equity"),
            ],
        ),
        _guid(seed, f"{label}:opening-tx"),
    )
    for index, split in enumerate(tx.splits):
        _assign_guid(split, _guid(seed, f"{label}:opening-split:{index}"))


def _create_success_book(path: Path, *, seed: int, case_name: str, unicode_names: bool = False) -> dict[str, dict[str, str]]:
    book = piecash.create_book(currency=BASE_CURRENCY, sqlite_file=str(path), overwrite=True)
    try:
        # Keep piecash.create_book's default CURRENCY commodity and root identity intact.
        # Rewriting either GUID makes reopened default_currency/root identity drift and
        # invalidates the generated fixture as realistic GnuCash input.
        sek = book.default_currency
        root = book.root_account
        if not str(getattr(sek, "guid", "") or ""):
            raise RuntimeError("created book default currency must have a stable non-null GUID")
        if not str(getattr(root, "guid", "") or ""):
            raise RuntimeError("created book root account must have a stable non-null GUID")
        if unicode_names:
            assets_name, cash_name = "Активы", "Наличные"
            expenses_name, food_name = "Расходы", "Еда"
            income_name, salary_name = "Доходы", "Зарплата"
            transport_name = "Транспорт"
        else:
            assets_name, cash_name = "Assets", "Cash"
            expenses_name, food_name = "Expenses", "Food"
            income_name, salary_name = "Income", "Salary"
            transport_name = "Transport"
        assets = _assign_guid(Account(name=assets_name, type="ASSET", parent=root, commodity=sek), _guid(seed, f"{case_name}:assets"))
        cash = _assign_guid(Account(name=cash_name, type="CASH", parent=assets, commodity=sek), _guid(seed, f"{case_name}:cash"))
        bank = _assign_guid(Account(name="Bank" if not unicode_names else "Банк", type="BANK", parent=assets, commodity=sek), _guid(seed, f"{case_name}:bank"))
        expenses = _assign_guid(Account(name=expenses_name, type="EXPENSE", parent=root, commodity=sek), _guid(seed, f"{case_name}:expenses"))
        food = _assign_guid(Account(name=food_name, type="EXPENSE", parent=expenses, commodity=sek), _guid(seed, f"{case_name}:food"))
        transport = _assign_guid(Account(name=transport_name, type="EXPENSE", parent=expenses, commodity=sek), _guid(seed, f"{case_name}:transport"))
        income = _assign_guid(Account(name=income_name, type="INCOME", parent=root, commodity=sek), _guid(seed, f"{case_name}:income"))
        salary = _assign_guid(Account(name=salary_name, type="INCOME", parent=income, commodity=sek), _guid(seed, f"{case_name}:salary"))
        equity = _assign_guid(Account(name="Equity", type="EQUITY", parent=root, commodity=sek), _guid(seed, f"{case_name}:equity"))
        opening_asset = bank if case_name == "income" else cash
        _opening_transaction(sek, opening_asset, equity, "100.00", seed=seed, label=case_name)
        book.save()
        return {
            "cash": _account_record(cash),
            "bank": _account_record(bank),
            "food": _account_record(food),
            "transport": _account_record(transport),
            "salary": _account_record(salary),
            "equity": _account_record(equity),
        }
    finally:
        book.close()


def _create_incompatible_book(path: Path, *, seed: int) -> dict[str, dict[str, str]]:
    book = piecash.create_book(currency=BASE_CURRENCY, sqlite_file=str(path), overwrite=True)
    try:
        # Keep piecash.create_book's default CURRENCY commodity GUID intact.
        sek = book.default_currency
        if not str(getattr(sek, "guid", "") or ""):
            raise RuntimeError("created book default currency must have a stable non-null GUID")
        usd = _make_commodity(
            book,
            namespace="CURRENCY",
            mnemonic=USD_CURRENCY,
            fullname="US Dollar",
            fraction=100,
            guid=_guid(seed, "incompatible:commodity:usd"),
        )
        root = book.root_account
        if not str(getattr(root, "guid", "") or ""):
            raise RuntimeError("created book root account must have a stable non-null GUID")
        assets = _assign_guid(Account(name="Assets", type="ASSET", parent=root, commodity=sek), _guid(seed, "incompatible:assets"))
        cash = _assign_guid(Account(name="Cash", type="CASH", parent=assets, commodity=sek), _guid(seed, "incompatible:cash"))
        usd_wallet = _assign_guid(Account(name="USD Wallet", type="CASH", parent=assets, commodity=usd), _guid(seed, "incompatible:usd-wallet"))
        equity = _assign_guid(Account(name="Equity", type="EQUITY", parent=root, commodity=sek), _guid(seed, "incompatible:equity"))
        _opening_transaction(sek, cash, equity, "100.00", seed=seed, label="incompatible")
        book.save()
        return {
            "cash": _account_record(cash),
            "usd_wallet": _account_record(usd_wallet),
            "equity": _account_record(equity),
        }
    finally:
        book.close()


def _build_request(case_name: str, accounts: dict[str, dict[str, str]]) -> tuple[dict[str, Any], dict[str, Any]]:
    if case_name == "expense":
        splits = [
            {"account_id": accounts["cash"]["id"], "amount": "-12.34", "memo": "paid from synthetic cash"},
            {"account_id": accounts["food"]["id"], "amount": "12.34", "memo": "food expense"},
        ]
        return {
            "date": "2026-07-18",
            "description": "Synthetic expense CREATE seed 59017",
            "currency": BASE_CURRENCY,
            "splits": splits,
        }, {"split_count": 2, "delta_by_account_key": {"cash": "-12.34", "food": "12.34"}, "zero_sum": "0.00"}
    if case_name == "income":
        splits = [
            {"account_id": accounts["bank"]["id"], "amount": "2500.00", "memo": "salary received"},
            {"account_id": accounts["salary"]["id"], "amount": "-2500.00", "memo": "salary income"},
        ]
        return {
            "date": "2026-07-19",
            "description": "Synthetic income CREATE seed 59017",
            "currency": BASE_CURRENCY,
            "splits": splits,
        }, {"split_count": 2, "delta_by_account_key": {"bank": "2500.00", "salary": "-2500.00"}, "zero_sum": "0.00"}
    if case_name == "three_split":
        splits = [
            {"account_id": accounts["cash"]["id"], "amount": "-30.00", "memo": "source split"},
            {"account_id": accounts["food"]["id"], "amount": "12.50", "memo": "food part"},
            {"account_id": accounts["transport"]["id"], "amount": "17.50", "memo": "transport part"},
        ]
        return {
            "date": "2026-07-20",
            "description": "Synthetic three-split CREATE seed 59017",
            "currency": BASE_CURRENCY,
            "splits": splits,
        }, {"split_count": 3, "delta_by_account_key": {"cash": "-30.00", "food": "12.50", "transport": "17.50"}, "zero_sum": "0.00"}
    if case_name == "unicode":
        splits = [
            {"account_id": accounts["cash"]["id"], "amount": "-45.67", "memo": "наличные ☕"},
            {"account_id": accounts["food"]["id"], "amount": "45.67", "memo": "еда и кофе ☕"},
        ]
        return {
            "date": "2026-07-21",
            "description": "Синтетическая CREATE покупка ☕ seed 59017",
            "currency": UNICODE_CURRENCY,
            "splits": splits,
        }, {"split_count": 2, "delta_by_account_key": {"cash": "-45.67", "food": "45.67"}, "zero_sum": "0.00"}
    if case_name == "incompatible_commodity":
        splits = [
            {"account_id": accounts["cash"]["id"], "amount": "-10.00", "memo": "sek side"},
            {"account_id": accounts["usd_wallet"]["id"], "amount": "10.00", "memo": "usd side rejected"},
        ]
        return {
            "date": "2026-07-22",
            "description": "Synthetic incompatible commodity rejected seed 59017",
            "currency": BASE_CURRENCY,
            "splits": splits,
        }, {"rejected_code": "COMMODITY_MISMATCH", "target_delta": "0"}
    raise KeyError(case_name)


def generate_transaction_create_fixture_set(root: Path | str, *, seed: int = FIXTURE_SEED, clean: bool = True) -> GeneratedCreateFixtureSet:
    root_path = Path(root).resolve()
    if clean and root_path.exists():
        shutil.rmtree(root_path)
    source_root = root_path / "sources"
    target_root = root_path / "targets"
    source_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    case_names = ["expense", "income", "three_split", "unicode", "incompatible_commodity"]
    rng.shuffle(case_names)
    # Keep output ordering deterministic and readable while using the fixed seed
    # above as part of GUID/content generation and as a drift guard.
    case_names = ["expense", "income", "three_split", "unicode", "incompatible_commodity"]
    cases: dict[str, GeneratedCreateCase] = {}
    for index, case_name in enumerate(case_names, start=1):
        case_seed = seed + index * 101
        source_path = source_root / f"{case_name}-source.gnucash.sqlite"
        target_path = target_root / f"{case_name}-disposable-target.gnucash.sqlite"
        if case_name == "incompatible_commodity":
            accounts = _create_incompatible_book(source_path, seed=case_seed)
            kind = "incompatible_native_commodity"
        else:
            accounts = _create_success_book(source_path, seed=case_seed, case_name=case_name, unicode_names=case_name == "unicode")
            kind = case_name
        source_hash = sha256_file(source_path)
        shutil.copy2(source_path, target_path)
        request, expected = _build_request(case_name, accounts)
        cases[case_name] = GeneratedCreateCase(
            name=case_name,
            kind=kind,
            seed=case_seed,
            synthetic_only=True,
            source_path=source_path,
            target_path=target_path,
            source_hash=source_hash,
            target_hash_before=sha256_file(target_path),
            base_currency=BASE_CURRENCY,
            accounts=accounts,
            request=request,
            expected=expected,
        )
    return GeneratedCreateFixtureSet(
        seed=seed,
        root=root_path,
        source_root=source_root,
        target_root=target_root,
        cases=cases,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic transaction CREATE fixtures")
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--seed", type=int, default=FIXTURE_SEED)
    parser.add_argument("--no-clean", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    fixture_set = generate_transaction_create_fixture_set(args.output_root, seed=args.seed, clean=not args.no_clean)
    manifest = fixture_set.to_manifest()
    manifest["manifest_sha256"] = _sha256_bytes(json.dumps(manifest, sort_keys=True).encode("utf-8"))
    if args.json:
        print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
