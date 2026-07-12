"""Phase 87/88 large-book, many-splits, and synthetic write-path benchmark helper.

The helper intentionally generates only synthetic/disposable GnuCash SQLite books
and exercises non-mutating read, write-preview, validation, and read-back paths.
It must never require or commit private books, CSV exports, screenshots, app DBs,
`.env`, or secrets, and it does not make production performance claims.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import statistics
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

import piecash
from fastapi.testclient import TestClient
from piecash import Account, Split, Transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import Book, User, UserBookAccess
from app.routers.auth import get_db
from app.schemas.gnucash import TransactionDetailDTO
from app.schemas.gnucash_writes import (
    TransactionCreateRequestDTO,
    TransactionSplitWriteDTO,
    TransactionWriteResultDTO,
)
from app.services.auth import hash_password
from app.services.gnucash_book import GnuCashBookService
from app.services.gnucash_write import GnuCashWriteService

BASE_CURRENCY = "SEK"
CSV_EXPORT_LIMIT = 10_000
DEFAULT_OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "generated-fixtures"
    / "phase-87-large-book.gnucash.sqlite"
)


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    method: str
    path_template: str
    read_only: bool = True
    request_json: str | None = None


BENCHMARK_CASES: list[BenchmarkCase] = [
    BenchmarkCase("accounts_tree_load", "GET", "/books/{book_id}/accounts/tree"),
    BenchmarkCase(
        "accounts_tree_large_hierarchy_filter_seed",
        "GET",
        "/books/{book_id}/accounts/tree",
    ),
    BenchmarkCase("transactions_list_first_page", "GET", "/books/{book_id}/transactions?limit=50&offset=0"),
    BenchmarkCase(
        "transaction_filters",
        "GET",
        "/books/{book_id}/transactions?limit=50&offset=0&query=synthetic&date_from=2026-01-01&date_to=2026-12-31",
    ),
    BenchmarkCase(
        "account_detail_transactions",
        "GET",
        "/books/{book_id}/accounts/{account_id}/transactions?limit=50&offset=0",
    ),
    BenchmarkCase(
        "account_detail_transactions_page_2",
        "GET",
        "/books/{book_id}/accounts/{account_id}/transactions?limit=50&offset=50",
    ),
    BenchmarkCase(
        "account_detail_transactions_filtered",
        "GET",
        "/books/{book_id}/accounts/{account_id}/transactions?limit=50&offset=0&query=synthetic&date_from=2026-01-01&date_to=2026-12-31&min_amount=1&max_amount=1500",
    ),
    BenchmarkCase(
        "account_detail_csv_export",
        "GET",
        "/books/{book_id}/transactions/export?account_id={account_id}&query=synthetic&date_from=2026-01-01&date_to=2026-12-31&min_amount=1&max_amount=1500",
    ),
    BenchmarkCase(
        "many_splits_transaction_detail",
        "GET",
        "/books/{book_id}/transactions/{many_split_transaction_id}",
    ),
    BenchmarkCase(
        "transaction_create_preview_validation",
        "POST",
        "/books/{book_id}/transactions/create-preview",
        request_json="synthetic_create_preview",
    ),
    BenchmarkCase(
        "transaction_create_validation_service",
        "SERVICE",
        "GnuCashWriteService.validate_transaction_create",
        request_json="synthetic_transaction_validation",
    ),
    BenchmarkCase(
        "transaction_create_readback_existing_synthetic",
        "SERVICE",
        "transactions._verify_transaction_create_readback",
        request_json="synthetic_existing_transaction_readback",
    ),
    BenchmarkCase("dashboard_summary", "GET", "/books/{book_id}/reports/summary?as_of_date=2026-12-31"),
    BenchmarkCase(
        "dashboard_cashflow_monthly",
        "GET",
        "/books/{book_id}/reports/cashflow?date_from=2026-01-01&date_to=2026-12-31&by_month=true",
    ),
    BenchmarkCase(
        "dashboard_expenses_by_account_month",
        "GET",
        "/books/{book_id}/reports/expenses-by-account?date_from=2026-12-01&date_to=2026-12-31",
    ),
    BenchmarkCase(
        "dashboard_recent_transactions",
        "GET",
        "/books/{book_id}/reports/recent-transactions?limit=10",
    ),
    BenchmarkCase(
        "period_comparison_previous_equivalent",
        "GET",
        "/books/{book_id}/reports/comparison?date_from=2026-07-02&date_to=2026-12-30"
        "&comparison_mode=previous_equivalent"
        "&comparison_date_from=2026-01-01&comparison_date_to=2026-07-01",
    ),
    BenchmarkCase("csv_export_up_to_cap", "GET", "/books/{book_id}/transactions/export"),
]


@dataclass(frozen=True)
class BenchmarkConfig:
    transaction_count: int = 1_000
    expense_account_count: int = 12
    account_branch_count: int = 8
    account_depth: int = 4
    many_split_count: int = 60
    repeats: int = 3


@dataclass(frozen=True)
class FixtureMetadata:
    path: Path
    transaction_count: int
    expense_account_count: int
    account_branch_count: int
    account_depth: int
    synthetic_account_count: int
    many_split_count: int
    synthetic: bool
    contains_real_data: bool


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    method: str
    path: str
    status_code: int
    duration_ms_min: float
    duration_ms_median: float
    duration_ms_max: float
    response_bytes: int
    item_count: int | None = None
    csv_limit: int | None = None
    csv_total: int | None = None
    csv_truncated: bool | None = None
    csv_expected_body_rows: int | None = None
    csv_body_matches_expected: bool | None = None

    def __post_init__(self) -> None:
        if self.name not in {"csv_export_up_to_cap", "account_detail_csv_export"}:
            return
        if self.csv_total is None or self.csv_limit is None or self.item_count is None:
            return
        expected_body_rows = min(self.csv_total, self.csv_limit)
        object.__setattr__(self, "csv_expected_body_rows", expected_body_rows)
        object.__setattr__(self, "csv_body_matches_expected", self.item_count == expected_body_rows)


def benchmark_plan(case_names: set[str] | None = None) -> list[BenchmarkCase]:
    """Return the conservative synthetic benchmark plan, optionally filtered by case name."""
    if case_names is None:
        return BENCHMARK_CASES
    unknown = case_names - {case.name for case in BENCHMARK_CASES}
    if unknown:
        raise ValueError(f"unknown benchmark case(s): {', '.join(sorted(unknown))}")
    return [case for case in BENCHMARK_CASES if case.name in case_names]


def create_large_synthetic_book(
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    *,
    transaction_count: int = 1_000,
    expense_account_count: int = 12,
    account_branch_count: int = 8,
    account_depth: int = 4,
    many_split_count: int = 60,
) -> FixtureMetadata:
    """Create a deterministic synthetic GnuCash SQLite book for benchmarks."""
    if transaction_count < 2:
        raise ValueError("transaction_count must be at least 2 for the opening and many-splits transactions")
    if expense_account_count < 1:
        raise ValueError("expense_account_count must be at least 1")
    if account_branch_count < 1:
        raise ValueError("account_branch_count must be at least 1")
    if account_depth < 1:
        raise ValueError("account_depth must be at least 1")
    if many_split_count < 2:
        raise ValueError("many_split_count must be at least 2")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    book = piecash.create_book(currency=BASE_CURRENCY, sqlite_file=str(output))
    currency = book.commodities[0]
    root = book.root_account

    assets = Account(name="Synthetic Assets", type="ASSET", parent=root, commodity=currency)
    checking = Account(name="Synthetic Checking", type="BANK", parent=assets, commodity=currency)
    savings = Account(name="Synthetic Savings", type="BANK", parent=assets, commodity=currency)

    liabilities = Account(name="Synthetic Liabilities", type="LIABILITY", parent=root, commodity=currency)
    credit_card = Account(name="Synthetic Credit Card", type="CREDIT", parent=liabilities, commodity=currency)

    income = Account(name="Synthetic Income", type="INCOME", parent=root, commodity=currency)
    salary = Account(name="Synthetic Salary", type="INCOME", parent=income, commodity=currency)

    expenses = Account(name="Synthetic Expenses", type="EXPENSE", parent=root, commodity=currency)
    expense_accounts = [
        Account(
            name=f"Synthetic Expense {idx:02d}",
            type="EXPENSE",
            parent=expenses,
            commodity=currency,
        )
        for idx in range(1, expense_account_count + 1)
    ]

    synthetic_hierarchy_accounts: list[Account] = []
    for branch_idx in range(1, account_branch_count + 1):
        parent = Account(
            name=f"Synthetic Hierarchy Branch {branch_idx:02d}",
            type="ASSET",
            parent=assets,
            commodity=currency,
        )
        synthetic_hierarchy_accounts.append(parent)
        for depth_idx in range(1, account_depth + 1):
            parent = Account(
                name=f"Synthetic Hierarchy Branch {branch_idx:02d} Level {depth_idx:02d}",
                type="ASSET",
                parent=parent,
                commodity=currency,
            )
            synthetic_hierarchy_accounts.append(parent)

    equity = Account(name="Synthetic Equity", type="EQUITY", parent=root, commodity=currency)
    opening = Account(name="Synthetic Opening Balances", type="EQUITY", parent=equity, commodity=currency)

    Transaction(
        currency=currency,
        description="Synthetic benchmark transaction opening checking",
        post_date=date(2026, 1, 1),
        splits=[
            Split(account=opening, value=Decimal("-10000.00")),
            Split(account=checking, value=Decimal("10000.00")),
        ],
    )

    per_split_amount = Decimal("1.00")
    Transaction(
        currency=currency,
        description="Synthetic benchmark transaction many splits",
        post_date=date(2026, 1, 2),
        splits=[
            Split(account=checking, value=-(per_split_amount * (many_split_count - 1))),
            *[
                Split(account=expense_accounts[idx % expense_account_count], value=per_split_amount)
                for idx in range(many_split_count - 1)
            ],
        ],
    )

    start = date(2026, 1, 2)
    for idx in range(2, transaction_count):
        tx_date = start + timedelta(days=idx % 365)
        amount = Decimal((idx % 500) + 1).quantize(Decimal("0.01"))
        if idx % 10 == 0:
            Transaction(
                currency=currency,
                description=f"Synthetic benchmark transaction salary {idx:05d}",
                post_date=tx_date,
                splits=[
                    Split(account=salary, value=-(amount + Decimal("1000.00"))),
                    Split(account=checking, value=amount + Decimal("1000.00")),
                ],
            )
        elif idx % 15 == 0:
            Transaction(
                currency=currency,
                description=f"Synthetic benchmark transaction transfer {idx:05d}",
                post_date=tx_date,
                splits=[
                    Split(account=checking, value=-amount),
                    Split(account=savings, value=amount),
                ],
            )
        elif idx % 22 == 0:
            expense = expense_accounts[idx % expense_account_count]
            Transaction(
                currency=currency,
                description=f"Synthetic benchmark transaction credit {idx:05d}",
                post_date=tx_date,
                splits=[
                    Split(account=credit_card, value=-amount),
                    Split(account=expense, value=amount),
                ],
            )
        else:
            expense = expense_accounts[idx % expense_account_count]
            Transaction(
                currency=currency,
                description=f"Synthetic benchmark transaction expense {idx:05d}",
                post_date=tx_date,
                splits=[
                    Split(account=checking, value=-amount),
                    Split(account=expense, value=amount),
                ],
            )

    book.save()
    book.close()
    return FixtureMetadata(
        path=output,
        transaction_count=transaction_count,
        expense_account_count=expense_account_count,
        account_branch_count=account_branch_count,
        account_depth=account_depth,
        synthetic_account_count=10
        + expense_account_count
        + (account_branch_count * (account_depth + 1)),
        many_split_count=many_split_count,
        synthetic=True,
        contains_real_data=False,
    )


def _test_settings() -> Settings:
    return Settings(
        app_env="benchmark",
        app_database_url="sqlite:///:memory:",
        jwt_secret="benchmark-secret-key-for-local-phase-87-only",
        jwt_token_expire_minutes=30,
        app_admin_username="admin",
        app_admin_password="benchmark-password",
    )


def _build_client(book_path: Path) -> tuple[TestClient, int, dict[str, str], Callable[[], None]]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_settings] = _test_settings
    app.dependency_overrides[get_db] = override_get_db

    with session_factory() as session:
        user = User(
            username="admin",
            display_name="Benchmark Admin",
            password_hash=hash_password("benchmark-password"),
            is_admin=True,
        )
        session.add(user)
        session.flush()
        book = Book(
            name="Phase 87 Synthetic Large Book",
            storage_type="sqlite",
            uri_or_path=str(book_path),
            base_currency=BASE_CURRENCY,
            is_default=True,
        )
        session.add(book)
        session.flush()
        session.add(UserBookAccess(user_id=user.id, book_id=book.id, role="owner"))
        session.commit()
        book_id = int(book.id)

    client = TestClient(app)
    login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "benchmark-password"},
    )
    login.raise_for_status()
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    def cleanup() -> None:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        engine.dispose()

    return client, book_id, headers, cleanup


def _load_account_tree(client: TestClient, book_id: int, headers: dict[str, str]) -> list[dict[str, Any]]:
    response = client.get(f"/books/{book_id}/accounts/tree", headers=headers)
    response.raise_for_status()
    return response.json()


def _iter_account_tree(nodes: list[dict[str, Any]]):
    for node in nodes:
        yield node
        children = node.get("children") or []
        if isinstance(children, list):
            yield from _iter_account_tree(children)


def _select_account_id_from_tree(tree: list[dict[str, Any]]) -> str:
    for preferred_types in ({"BANK"}, {"ASSET"}):
        for node in _iter_account_tree(tree):
            if (
                node.get("type") in preferred_types
                and node.get("id")
                and not node.get("placeholder", False)
                and not node.get("hidden", False)
            ):
                return str(node["id"])
    raise RuntimeError("benchmark fixture did not expose a usable account id")


def _select_account_id(client: TestClient, book_id: int, headers: dict[str, str]) -> str:
    return _select_account_id_from_tree(_load_account_tree(client, book_id, headers))


def _select_preview_account_ids(client: TestClient, book_id: int, headers: dict[str, str]) -> tuple[str, str]:
    tree = _load_account_tree(client, book_id, headers)
    candidates = [
        node
        for node in _iter_account_tree(tree)
        if node.get("id")
        and node.get("type") != "ROOT"
        and str(node.get("currency") or "").upper() in {BASE_CURRENCY, "XXX"}
        and not node.get("placeholder", False)
        and not node.get("hidden", False)
    ]
    if len(candidates) < 2:
        raise RuntimeError("benchmark fixture did not expose two selectable preview accounts")

    def pick(types: set[str], *, exclude: str | None = None) -> str | None:
        for candidate in candidates:
            account_id = str(candidate["id"])
            if account_id != exclude and candidate.get("type") in types:
                return account_id
        return None

    debit_account_id = pick({"BANK"}) or pick({"ASSET"}) or str(candidates[0]["id"])
    credit_account_id = (
        pick({"EXPENSE"}, exclude=debit_account_id)
        or pick({"INCOME", "LIABILITY", "CREDIT"}, exclude=debit_account_id)
        or pick({"BANK", "ASSET"}, exclude=debit_account_id)
    )
    if credit_account_id is None:
        raise RuntimeError("benchmark fixture did not expose a distinct preview credit account")
    return debit_account_id, credit_account_id


def _select_many_split_transaction_id(book_path: Path) -> str:
    with sqlite3.connect(book_path) as conn:
        row = conn.execute(
            "select guid from transactions where description = ?",
            ("Synthetic benchmark transaction many splits",),
        ).fetchone()
    if row is None:
        raise RuntimeError("benchmark fixture did not expose a many-splits transaction id")
    return str(row[0])


def _build_case_request_json(
    case: BenchmarkCase,
    *,
    debit_account_id: str,
    credit_account_id: str,
) -> dict[str, Any] | None:
    if case.request_json is None:
        return None
    if debit_account_id == credit_account_id:
        raise ValueError("synthetic write-path benchmark requires distinct account IDs")
    if case.request_json == "synthetic_create_preview":
        return {
            "date": "2026-06-15",
            "debit_account_id": debit_account_id,
            "credit_account_id": credit_account_id,
            "amount": "123.4500",
            "currency": BASE_CURRENCY,
            "description": "Synthetic benchmark create preview only",
            "memo": "Synthetic local performance preview; no write executed",
        }
    if case.request_json == "synthetic_transaction_validation":
        return {
            "date": "2026-06-15",
            "description": "Synthetic benchmark create validation only",
            "splits": [
                {
                    "account_id": debit_account_id,
                    "amount": "-123.4500",
                    "currency": BASE_CURRENCY,
                    "memo": "Synthetic local validation performance; no write executed",
                },
                {
                    "account_id": credit_account_id,
                    "amount": "123.4500",
                    "currency": BASE_CURRENCY,
                    "memo": "Synthetic local validation performance; no write executed",
                },
            ],
        }
    if case.request_json == "synthetic_existing_transaction_readback":
        return None
    raise ValueError(f"unsupported benchmark request_json: {case.request_json}")


def _build_readback_request_from_detail(detail: TransactionDetailDTO) -> TransactionCreateRequestDTO:
    """Build a synthetic read-back verification request from an existing fixture transaction."""
    return TransactionCreateRequestDTO(
        date=detail.date,
        description=detail.description,
        splits=[
            TransactionSplitWriteDTO(
                account_id=split.account_id,
                amount=split.amount,
                currency=split.currency,
                memo=split.memo or "",
            )
            for split in detail.splits
        ],
    )


def _json_response_size(payload: Any) -> int:
    return len(json.dumps(payload, default=str, sort_keys=True).encode("utf-8"))


def _summarize_response(
    case: BenchmarkCase, response: Any
) -> tuple[int | None, int | None, int | None, bool | None]:
    item_count: int | None = None
    csv_limit: int | None = None
    csv_total: int | None = None
    csv_truncated: bool | None = None

    if case.name in {"csv_export_up_to_cap", "account_detail_csv_export"}:
        csv_limit_header = response.headers.get("X-CSV-Export-Limit")
        if csv_limit_header is not None:
            csv_limit = int(csv_limit_header)
        csv_total_header = response.headers.get("X-CSV-Export-Total")
        if csv_total_header is not None:
            csv_total = int(csv_total_header)
        csv_truncated = response.headers.get("X-CSV-Export-Truncated") == "true"
        rows = list(csv.reader(io.StringIO(response.text)))
        item_count = max(0, len(rows) - 1)
        return item_count, csv_limit, csv_total, csv_truncated

    try:
        payload = response.json()
    except ValueError:
        return None, None, None, None
    if isinstance(payload, list):
        item_count = len(payload)
    elif isinstance(payload, dict) and isinstance(payload.get("items"), list):
        item_count = len(payload["items"])
    elif isinstance(payload, dict) and isinstance(payload.get("splits"), list):
        item_count = len(payload["splits"])
    elif case.name == "period_comparison_previous_equivalent" and isinstance(payload, dict):
        expense_changes = payload.get("expense_changes")
        if isinstance(expense_changes, list):
            item_count = len(expense_changes)
    return item_count, None, None, None


def _run_service_benchmark_case(
    case: BenchmarkCase,
    *,
    book_path: Path,
    debit_account_id: str,
    credit_account_id: str,
    many_split_transaction_id: str,
    repeats: int,
) -> BenchmarkResult:
    """Run a non-mutating service/read-back benchmark case without enabling write routes."""
    durations: list[float] = []
    last_payload: dict[str, Any] | None = None
    status_code = 200
    item_count: int | None = None

    if case.request_json == "synthetic_transaction_validation":
        payload = _build_case_request_json(
            case,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
        )
        if payload is None:  # pragma: no cover - defensive guard for future edits
            raise RuntimeError("validation benchmark requires a synthetic payload")
        request = TransactionCreateRequestDTO(**payload)
        service = GnuCashWriteService({"uri_or_path": str(book_path), "base_currency": BASE_CURRENCY})
        for _ in range(repeats):
            start = time.perf_counter()
            validation = service.validate_transaction_create(request)
            durations.append((time.perf_counter() - start) * 1000)
            last_payload = validation.model_dump()
        status_code = 200 if last_payload and last_payload.get("valid") is True else 422
        summary = last_payload.get("summary", {}) if last_payload else {}
        item_count = int(summary.get("split_count", 0)) if summary.get("split_count") is not None else None
    elif case.request_json == "synthetic_existing_transaction_readback":
        from app.routers.transactions import _verify_transaction_create_readback

        detail = GnuCashBookService(
            {"uri_or_path": str(book_path), "base_currency": BASE_CURRENCY}
        ).get_transaction(many_split_transaction_id)
        request = _build_readback_request_from_detail(detail)
        synthetic_book = Book(
            name="Synthetic benchmark read-back fixture",
            storage_type="sqlite",
            uri_or_path=str(book_path),
            base_currency=BASE_CURRENCY,
            is_default=True,
        )
        result = TransactionWriteResultDTO(
            transaction_id=many_split_transaction_id,
            backup_path="synthetic-readback-benchmark-ref",
        )
        for _ in range(repeats):
            start = time.perf_counter()
            last_payload = dict(_verify_transaction_create_readback(synthetic_book, request, result))
            durations.append((time.perf_counter() - start) * 1000)
        item_count = int(last_payload.get("readback_split_count", 0)) if last_payload else None
    else:
        raise ValueError(f"unsupported service benchmark case: {case.name}")

    if last_payload is None:  # pragma: no cover - repeats validation prevents this
        raise RuntimeError("service benchmark produced no result")
    return BenchmarkResult(
        name=case.name,
        method=case.method,
        path=case.path_template,
        status_code=status_code,
        duration_ms_min=round(min(durations), 2),
        duration_ms_median=round(statistics.median(durations), 2),
        duration_ms_max=round(max(durations), 2),
        response_bytes=_json_response_size(last_payload),
        item_count=item_count,
    )


def run_benchmark(
    book_path: str | Path,
    *,
    repeats: int = 3,
    case_names: set[str] | None = None,
) -> list[BenchmarkResult]:
    """Run selected synthetic benchmark cases without enabling mutation routes."""
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    selected_cases = benchmark_plan(case_names)
    resolved_book_path = Path(book_path)
    client, book_id, headers, cleanup = _build_client(resolved_book_path)
    try:
        account_id = _select_account_id(client, book_id, headers)
        preview_debit_account_id, preview_credit_account_id = _select_preview_account_ids(client, book_id, headers)
        many_split_transaction_id = _select_many_split_transaction_id(resolved_book_path)
        results: list[BenchmarkResult] = []
        for case in selected_cases:
            if case.method == "SERVICE":
                results.append(
                    _run_service_benchmark_case(
                        case,
                        book_path=resolved_book_path,
                        debit_account_id=preview_debit_account_id,
                        credit_account_id=preview_credit_account_id,
                        many_split_transaction_id=many_split_transaction_id,
                        repeats=repeats,
                    )
                )
                continue
            path = case.path_template.format(
                book_id=book_id,
                account_id=account_id,
                many_split_transaction_id=many_split_transaction_id,
            )
            durations: list[float] = []
            last_response = None
            request_json = _build_case_request_json(
                case,
                debit_account_id=preview_debit_account_id,
                credit_account_id=preview_credit_account_id,
            )
            request_kwargs: dict[str, Any] = {"headers": headers}
            if request_json is not None:
                request_kwargs["json"] = request_json
            for _ in range(repeats):
                start = time.perf_counter()
                response = client.request(case.method, path, **request_kwargs)
                durations.append((time.perf_counter() - start) * 1000)
                response.raise_for_status()
                last_response = response
            if last_response is None:  # pragma: no cover - repeats validation prevents this
                raise RuntimeError("benchmark produced no response")
            item_count, csv_limit, csv_total, csv_truncated = _summarize_response(case, last_response)
            results.append(
                BenchmarkResult(
                    name=case.name,
                    method=case.method,
                    path=path,
                    status_code=last_response.status_code,
                    duration_ms_min=round(min(durations), 2),
                    duration_ms_median=round(statistics.median(durations), 2),
                    duration_ms_max=round(max(durations), 2),
                    response_bytes=len(last_response.content),
                    item_count=item_count,
                    csv_limit=csv_limit,
                    csv_total=csv_total,
                    csv_truncated=csv_truncated,
                )
            )
        return results
    finally:
        cleanup()


def write_results_json(path: str | Path, metadata: FixtureMetadata, results: list[BenchmarkResult]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    result_names = {result.name for result in results}
    read_only_api_paths_only = all(result.method in {"GET", "HEAD"} for result in results)
    includes_write_preview = "transaction_create_preview_validation" in result_names
    includes_validation_service = "transaction_create_validation_service" in result_names
    includes_readback_service = "transaction_create_readback_existing_synthetic" in result_names
    payload = {
        "fixture": {**asdict(metadata), "path": str(metadata.path)},
        "results": [asdict(result) for result in results],
        "scope": {
            "synthetic_generated_data_only": True,
            "local_synthetic_measurements_only": True,
            "non_mutating_read_and_preview_paths_only": True,
            "non_mutating_read_preview_validation_readback_paths_only": True,
            "read_only_api_paths_only": read_only_api_paths_only,
            "includes_write_preview_validation_path": includes_write_preview,
            "includes_transaction_validation_service_path": includes_validation_service,
            "includes_existing_synthetic_readback_path": includes_readback_service,
            "write_alpha_mutation_routes_called": False,
            "contains_private_book": False,
            "writes_enabled": False,
            "production_performance_claim": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run local synthetic large-book, many-splits, write-preview, validation, and read-back benchmark"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--transactions", type=int, default=BenchmarkConfig.transaction_count)
    parser.add_argument("--expense-accounts", type=int, default=BenchmarkConfig.expense_account_count)
    parser.add_argument("--account-branches", type=int, default=BenchmarkConfig.account_branch_count)
    parser.add_argument("--account-depth", type=int, default=BenchmarkConfig.account_depth)
    parser.add_argument("--many-splits", type=int, default=BenchmarkConfig.many_split_count)
    parser.add_argument("--repeats", type=int, default=BenchmarkConfig.repeats)
    parser.add_argument(
        "--case",
        action="append",
        dest="case_names",
        default=None,
        help="Run only the named benchmark case; repeat for multiple cases.",
    )
    parser.add_argument("--json-output", type=Path, default=None)
    args = parser.parse_args(argv)

    metadata = create_large_synthetic_book(
        args.output,
        transaction_count=args.transactions,
        expense_account_count=args.expense_accounts,
        account_branch_count=args.account_branches,
        account_depth=args.account_depth,
        many_split_count=args.many_splits,
    )
    selected_case_names = set(args.case_names) if args.case_names else None
    results = run_benchmark(metadata.path, repeats=args.repeats, case_names=selected_case_names)

    print("Local synthetic large-book, many-splits, write-preview, validation, and read-back benchmark")
    print(f"Synthetic fixture: {metadata.path}")
    print(f"Transactions: {metadata.transaction_count}")
    print(f"Expense accounts: {metadata.expense_account_count}")
    print(f"Synthetic hierarchy branches: {metadata.account_branch_count}")
    print(f"Synthetic hierarchy depth: {metadata.account_depth}")
    print(f"Synthetic account count: {metadata.synthetic_account_count}")
    print(f"Many-splits transaction splits: {metadata.many_split_count}")
    if selected_case_names:
        print(f"Selected benchmark cases: {', '.join(sorted(selected_case_names))}")
    print("Scope: local synthetic fixture only; non-mutating read, create-preview, validation, and read-back paths only.")
    print("No private book data used; no writes executed; no production performance claim.")
    for result in results:
        extra = ""
        if result.item_count is not None:
            extra += f", items={result.item_count}"
        if result.csv_total is not None:
            extra += (
                f", csv_limit={result.csv_limit}, csv_total={result.csv_total}, "
                f"truncated={result.csv_truncated}, "
                f"expected_body_rows={result.csv_expected_body_rows}, "
                f"body_matches_expected={result.csv_body_matches_expected}"
            )
        print(
            f"{result.name}: status={result.status_code}, median={result.duration_ms_median:.2f} ms, "
            f"min={result.duration_ms_min:.2f} ms, max={result.duration_ms_max:.2f} ms, bytes={result.response_bytes}{extra}"
        )

    if args.json_output:
        output = write_results_json(args.json_output, metadata, results)
        print(f"JSON results: {output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
