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
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

import piecash
from fastapi.testclient import TestClient
from piecash import Account, Commodity, Split, Transaction
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import Book, BookHealthSnapshot, User, UserBookAccess
from app.routers.auth import get_db
from app.schemas.gnucash import TransactionDetailDTO
from app.schemas.gnucash_writes import (
    TransactionCreateRequestDTO,
    TransactionSplitWriteDTO,
    TransactionWriteResultDTO,
)
from app.services import book_preflight
from app.services.auth import hash_password
from app.services.gnucash_book import GnuCashBookService
from app.services.gnucash_write import GnuCashWriteService

BASE_CURRENCY = "SEK"
CSV_EXPORT_LIMIT = 10_000
SPARSE_QUERY_TEXT = "sparse-ζ-needle"
EXPLORER_DATE_FROM = "2026-01-01"
EXPLORER_DATE_TO = "2026-12-31"
EXPLORER_PAGE_SIZE = 25
EXPLORER_FILTERED_PAGE_SIZE = 5
EXPLORER_LATER_PAGE_NUMBER = 20
EXPLORER_FIRST_PAGE_TEMPLATE = (
    "/books/{book_id}/transactions/explorer"
    f"?date_from={EXPLORER_DATE_FROM}&date_to={EXPLORER_DATE_TO}"
    f"&page_size={EXPLORER_PAGE_SIZE}&sort=date_desc"
)
EXPLORER_FILTERED_PAGE_TEMPLATE = (
    "/books/{book_id}/transactions/explorer"
    f"?date_from={EXPLORER_DATE_FROM}&date_to={EXPLORER_DATE_TO}"
    f"&page_size={EXPLORER_FILTERED_PAGE_SIZE}&sort=date_desc&query={quote(SPARSE_QUERY_TEXT, safe='')}"
)
ISSUE55_ACCOUNT_QUERY_TEXT = "Needle ζ"
ISSUE55_ACCOUNT_DATE_FROM = "2026-01-01"
ISSUE55_ACCOUNT_DATE_TO = "2026-12-31"
ISSUE55_ACCOUNT_ACTIVITY_LIMIT = 10
ISSUE55_1K_VISIBLE_ACCOUNT_INDEX_LIMIT = 550
ISSUE55_ACCOUNT_GUID_NAMESPACE = 0xA551
ISSUE55_SPLIT_GUID_NAMESPACE = 0x5551
ISSUE55_TRANSACTION_GUID_NAMESPACE = 0x7551
ISSUE55_COMMODITY_GUID_NAMESPACE = 0xC551
ISSUE55_ROOT_ACCOUNT_ID = f"{ISSUE55_ACCOUNT_GUID_NAMESPACE:04x}{0:028x}"
ISSUE55_ASSETS_ACCOUNT_ID = f"{ISSUE55_ACCOUNT_GUID_NAMESPACE:04x}{1:028x}"
ISSUE55_ACTIVITY_ACCOUNT_ID = f"{ISSUE55_ACCOUNT_GUID_NAMESPACE:04x}{6:028x}"
ISSUE55_MIXED_PARENT_ACCOUNT_ID = f"{ISSUE55_ACCOUNT_GUID_NAMESPACE:04x}{8:028x}"
ISSUE55_ACCOUNT_DATASETS: dict[str, tuple[int, int]] = {
    "1k": (1_000, 1_000),
    "10k": (10_000, 10_000),
}
ISSUE56_EXTRA_REGISTERED_BOOKS = 5
LOCAL_TIMING_BUDGETS_MS = {
    "1k": {
        "accounts_explorer_primary": 2_500,
        "issue55_1k_account_unfiltered_tree": 2_500,
        "issue55_1k_account_text_filtered_tree": 2_500,
        "issue55_1k_account_flat_search": 2_500,
        "issue55_1k_account_type_filtered_explorer": 2_500,
        "issue55_1k_root_overview": 2_500,
        "issue55_1k_recursive_native_buckets": 2_500,
        "issue55_1k_direct_period_activity": 2_500,
        "issue55_1k_account_transaction_explorer_first_page": 2_500,
        "period_comparison_previous_equivalent": 1_500,
        "transaction_explorer_first_page": 1_500,
        "transaction_explorer_sparse_scan_limited": 2_500,
        "transaction_explorer_later_forward_page": 1_500,
        "transaction_explorer_previous_page": 1_500,
        "dashboard_summary": 2_500,
        "dashboard_cashflow_monthly": 2_500,
        "dashboard_expenses_by_account_month": 2_500,
        "dashboard_recent_transactions": 2_500,
        "period_report_primary": 2_500,
    },
    "10k": {
        "accounts_explorer_primary": 12_000,
        "issue55_10k_account_filtered_tree": 8_000,
        "issue55_10k_root_overview": 8_000,
        "issue55_10k_direct_activity": 8_000,
        "issue55_10k_drilldown_first_page": 8_000,
        "period_comparison_previous_equivalent": 12_000,
        "transaction_explorer_first_page": 4_000,
        "transaction_explorer_sparse_scan_limited": 8_000,
        "transaction_explorer_later_forward_page": 4_000,
        "transaction_explorer_previous_page": 4_000,
        "dashboard_summary": 12_000,
        "dashboard_cashflow_monthly": 12_000,
        "dashboard_expenses_by_account_month": 12_000,
        "dashboard_recent_transactions": 8_000,
        "period_report_primary": 12_000,
    },
}
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
    expected_status_code: int = 200


BENCHMARK_CASES: list[BenchmarkCase] = [
    BenchmarkCase("accounts_tree_load", "GET", "/books/{book_id}/accounts/tree"),
    BenchmarkCase("accounts_explorer_primary", "GET", "/books/{book_id}/accounts/explorer"),
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
    BenchmarkCase("transaction_explorer_first_page", "GET", EXPLORER_FIRST_PAGE_TEMPLATE),
    BenchmarkCase(
        "transaction_explorer_sparse_scan_limited",
        "GET",
        EXPLORER_FILTERED_PAGE_TEMPLATE,
    ),
    BenchmarkCase(
        "transaction_explorer_later_forward_page",
        "GET",
        EXPLORER_FIRST_PAGE_TEMPLATE + "&cursor={cursor}",
    ),
    BenchmarkCase(
        "transaction_explorer_previous_page",
        "GET",
        EXPLORER_FIRST_PAGE_TEMPLATE + "&cursor={cursor}",
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
        "period_report_primary",
        "GET",
        "/books/{book_id}/reports?date_from=2026-01-01&date_to=2026-12-31",
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

ISSUE55_1K_ACCOUNT_CASES: list[BenchmarkCase] = [
    BenchmarkCase("issue55_1k_account_unfiltered_tree", "GET", "/books/{book_id}/accounts/explorer"),
    BenchmarkCase(
        "issue55_1k_account_text_filtered_tree",
        "GET",
        f"/books/{{book_id}}/accounts/explorer?query={quote(ISSUE55_ACCOUNT_QUERY_TEXT, safe='')}",
    ),
    BenchmarkCase(
        "issue55_1k_account_flat_search",
        "GET",
        f"/books/{{book_id}}/accounts/explorer?mode=flat&query={quote(ISSUE55_ACCOUNT_QUERY_TEXT, safe='')}",
    ),
    BenchmarkCase("issue55_1k_account_type_filtered_explorer", "GET", "/books/{book_id}/accounts/explorer?type=BANK"),
    BenchmarkCase("issue55_1k_root_overview", "GET", "/books/{book_id}/accounts/{issue55_root_account_id}/overview"),
    BenchmarkCase(
        "issue55_1k_recursive_native_buckets",
        "GET",
        "/books/{book_id}/accounts/{issue55_mixed_account_id}/overview",
    ),
    BenchmarkCase(
        "issue55_1k_direct_period_activity",
        "GET",
        "/books/{book_id}/accounts/{issue55_activity_account_id}/activity"
        f"?date_from={ISSUE55_ACCOUNT_DATE_FROM}&date_to={ISSUE55_ACCOUNT_DATE_TO}"
        f"&limit={ISSUE55_ACCOUNT_ACTIVITY_LIMIT}",
    ),
    BenchmarkCase(
        "issue55_1k_account_transaction_explorer_first_page",
        "GET",
        "/books/{book_id}/transactions/explorer"
        f"?date_from={ISSUE55_ACCOUNT_DATE_FROM}&date_to={ISSUE55_ACCOUNT_DATE_TO}"
        f"&page_size={ISSUE55_ACCOUNT_ACTIVITY_LIMIT}&sort=date_desc"
        "&account_ids={issue55_activity_account_id}",
    ),
]

ISSUE55_10K_ACCOUNT_CASES: list[BenchmarkCase] = [
    BenchmarkCase(
        "issue55_10k_account_filtered_tree",
        "GET",
        f"/books/{{book_id}}/accounts/explorer?query={quote(ISSUE55_ACCOUNT_QUERY_TEXT, safe='')}",
    ),
    BenchmarkCase(
        "issue55_10k_account_unfiltered_tree_expected_422",
        "GET",
        "/books/{book_id}/accounts/explorer",
        expected_status_code=422,
    ),
    BenchmarkCase("issue55_10k_root_overview", "GET", "/books/{book_id}/accounts/{issue55_root_account_id}/overview"),
    BenchmarkCase(
        "issue55_10k_direct_activity",
        "GET",
        "/books/{book_id}/accounts/{issue55_activity_account_id}/activity"
        f"?date_from={ISSUE55_ACCOUNT_DATE_FROM}&date_to={ISSUE55_ACCOUNT_DATE_TO}"
        f"&limit={ISSUE55_ACCOUNT_ACTIVITY_LIMIT}",
    ),
    BenchmarkCase(
        "issue55_10k_drilldown_first_page",
        "GET",
        "/books/{book_id}/transactions/explorer"
        f"?date_from={ISSUE55_ACCOUNT_DATE_FROM}&date_to={ISSUE55_ACCOUNT_DATE_TO}"
        f"&page_size={ISSUE55_ACCOUNT_ACTIVITY_LIMIT}&sort=date_desc"
        "&account_ids={issue55_activity_account_id}",
    ),
]

ISSUE56_LIFECYCLE_CASES: list[BenchmarkCase] = [
    BenchmarkCase("issue56_list_registered_books", "GET", "/books"),
    BenchmarkCase(
        "issue56_preflight",
        "POST",
        "/books/preflight",
        request_json="issue56_book_payload",
    ),
    BenchmarkCase("issue56_cached_health", "GET", "/books/{book_id}/health"),
    BenchmarkCase("issue56_health_recheck", "POST", "/books/{book_id}/health/recheck"),
    BenchmarkCase(
        "issue56_first_readonly_open_after_registration",
        "GET",
        "/books/{book_id}/accounts/tree",
    ),
    BenchmarkCase(
        "issue56_unavailable_source_cached_health",
        "GET",
        "/books/{missing_book_id}/health",
    ),
    BenchmarkCase("issue56_multiple_registered_books", "GET", "/books"),
]


@dataclass(frozen=True)
class BenchmarkConfig:
    transaction_count: int = 1_000
    expense_account_count: int = 12
    account_branch_count: int = 8
    account_depth: int = 4
    many_split_count: int = 60
    repeats: int = 3
    warmups: int = 1


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
    candidate_account_count: int | None = None
    hidden_account_count: int | None = None
    placeholder_account_count: int | None = None
    commodity_count: int | None = None
    duplicate_account_name_count: int | None = None
    unicode_account_name_count: int | None = None


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
    error_code: str | None = None
    item_count: int | None = None
    csv_limit: int | None = None
    csv_total: int | None = None
    csv_truncated: bool | None = None
    csv_expected_body_rows: int | None = None
    csv_body_matches_expected: bool | None = None
    warmup_count: int = 1
    measured_samples: int = 3
    returned_count: int | None = None
    page_size: int | None = None
    has_more: bool | None = None
    has_previous: bool | None = None
    next_cursor_length: int | None = None
    previous_cursor_length: int | None = None
    scan_candidate_rows: int | None = None
    scan_split_rows: int | None = None
    scan_query_count: int | None = None
    scan_limited: bool | None = None
    scan_exhausted: bool | None = None
    scan_limits: dict[str, int] | None = None
    stable_unique_order: bool | None = None
    cursor_roundtrip_matches: bool | None = None
    activity_recent_ids_match: bool | None = None
    activity_recent_amounts_match: bool | None = None
    actual_query_count: int | None = None
    account_candidate_accounts: int | None = None
    account_returned_nodes: int | None = None
    account_max_depth: int | None = None
    account_max_recursive_commodity_buckets: int | None = None
    account_rollup_bucket_cells: int | None = None
    account_split_rows: int | None = None
    account_split_aggregate_rows: int | None = None
    account_serialized_bytes: int | None = None
    overview_subtree_account_count: int | None = None
    overview_child_count: int | None = None
    overview_children_returned: int | None = None
    activity_recent_item_count: int | None = None
    activity_change_split_rows: int | None = None
    activity_recent_split_rows: int | None = None
    activity_recent_transaction_objects: int | None = None
    read_only_book_open_count_min: int | None = None
    read_only_book_open_count_max: int | None = None
    legacy_count_call_count_max: int | None = None
    full_transaction_materialization_count_max: int | None = None
    report_transaction_visit_count_max: int | None = None
    gnucash_sql_statement_count_min: int | None = None
    gnucash_sql_statement_count_max: int | None = None
    account_object_materialization_count_max: int | None = None
    transaction_object_materialization_count_max: int | None = None
    split_object_materialization_count_max: int | None = None
    app_db_statement_count_min: int | None = None
    app_db_statement_count_max: int | None = None
    preflight_sqlite_query_count_min: int | None = None
    preflight_sqlite_query_count_max: int | None = None
    preflight_piecash_open_count_min: int | None = None
    preflight_piecash_open_count_max: int | None = None
    preflight_account_materialization_count_max: int | None = None
    preflight_transaction_materialization_count_max: int | None = None
    mutation_capable_request_count: int = 0
    local_timing_budget_dataset: str | None = None
    local_timing_budget_ms: int | None = None
    local_timing_budget_passed: bool | None = None
    local_relative_timing_budget_reference_ms: float | None = None
    local_relative_timing_budget_passed: bool | None = None

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
    return _select_benchmark_cases(BENCHMARK_CASES, case_names)


def issue55_account_benchmark_plan(dataset: str, case_names: set[str] | None = None) -> list[BenchmarkCase]:
    """Return the issue #55 account performance plan for one exact synthetic dataset."""
    if dataset == "1k":
        return _select_benchmark_cases(ISSUE55_1K_ACCOUNT_CASES, case_names)
    if dataset == "10k":
        return _select_benchmark_cases(ISSUE55_10K_ACCOUNT_CASES, case_names)
    raise ValueError(f"unknown issue55 account dataset: {dataset}")


def issue56_lifecycle_benchmark_plan(case_names: set[str] | None = None) -> list[BenchmarkCase]:
    """Return issue #56 synthetic lifecycle/preflight benchmark cases."""
    return _select_benchmark_cases(ISSUE56_LIFECYCLE_CASES, case_names)


def _select_benchmark_cases(cases: list[BenchmarkCase], case_names: set[str] | None) -> list[BenchmarkCase]:
    if case_names is None:
        return cases
    unknown = case_names - {case.name for case in cases}
    if unknown:
        raise ValueError(f"unknown benchmark case(s): {', '.join(sorted(unknown))}")
    return [case for case in cases if case.name in case_names]


def _synthetic_guid(namespace: int, index: int) -> str:
    """Return a stable 32-hex synthetic GUID for reproducible fixture rows."""
    if namespace < 0 or namespace > 0xFFFF:
        raise ValueError("namespace must fit in 16 bits")
    if index < 0 or index >= 16**28:
        raise ValueError("index must fit in 28 hex digits")
    return f"{namespace:04x}{index:028x}"


def _assign_guid(item: Any, guid: str) -> Any:
    setattr(item, "guid", guid)
    return item


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
    currency = _assign_guid(book.commodities[0], _synthetic_guid(0xC001, 1))
    root = _assign_guid(book.root_account, _synthetic_guid(0xA001, 0))

    account_index = 0
    split_index = 0

    def synthetic_account(name: str, account_type: str, parent: Account) -> Account:
        nonlocal account_index
        account_index += 1
        return _assign_guid(
            Account(name=name, type=account_type, parent=parent, commodity=currency),
            _synthetic_guid(0xA001, account_index),
        )

    def synthetic_split(account: Account, value: Decimal, *, memo: str = "") -> Split:
        nonlocal split_index
        split_index += 1
        return _assign_guid(
            Split(account=account, value=value, memo=memo),
            _synthetic_guid(0x5001, split_index),
        )

    def synthetic_transaction(
        idx: int,
        *,
        description: str,
        post_date: date,
        splits: list[Split],
    ) -> Transaction:
        return _assign_guid(
            Transaction(currency=currency, description=description, post_date=post_date, splits=splits),
            _synthetic_guid(0x7001, idx),
        )

    def synthetic_description(kind: str, idx: int) -> str:
        suffix = ""
        if idx % 37 == 0:
            suffix += " — Unicode café Привет 旅費"
        if idx % 997 == 0:
            suffix += f" {SPARSE_QUERY_TEXT}"
        return f"Synthetic benchmark transaction {kind} {idx:05d}{suffix}"

    def synthetic_memo(label: str, idx: int) -> str:
        suffix = ""
        if idx % 37 == 0:
            suffix += " Unicode memo café Привет 旅費"
        if idx % 997 == 0:
            suffix += f" {SPARSE_QUERY_TEXT}"
        return f"Synthetic benchmark memo {label} {idx:05d}{suffix}"

    assets = synthetic_account("Synthetic Assets", "ASSET", root)
    checking = synthetic_account("Synthetic Checking", "BANK", assets)
    savings = synthetic_account("Synthetic Savings", "BANK", assets)

    liabilities = synthetic_account("Synthetic Liabilities", "LIABILITY", root)
    credit_card = synthetic_account("Synthetic Credit Card", "CREDIT", liabilities)

    income = synthetic_account("Synthetic Income", "INCOME", root)
    salary = synthetic_account("Synthetic Salary", "INCOME", income)

    expenses = synthetic_account("Synthetic Expenses", "EXPENSE", root)
    expense_accounts = [
        synthetic_account(f"Synthetic Expense {idx:02d}", "EXPENSE", expenses)
        for idx in range(1, expense_account_count + 1)
    ]

    synthetic_hierarchy_accounts: list[Account] = []
    for branch_idx in range(1, account_branch_count + 1):
        parent = synthetic_account(f"Synthetic Hierarchy Branch {branch_idx:02d}", "ASSET", assets)
        synthetic_hierarchy_accounts.append(parent)
        for depth_idx in range(1, account_depth + 1):
            parent = synthetic_account(
                f"Synthetic Hierarchy Branch {branch_idx:02d} Level {depth_idx:02d}",
                "ASSET",
                parent,
            )
            synthetic_hierarchy_accounts.append(parent)

    equity = synthetic_account("Synthetic Equity", "EQUITY", root)
    opening = synthetic_account("Synthetic Opening Balances", "EQUITY", equity)

    synthetic_transaction(
        1,
        description="Synthetic benchmark transaction opening checking",
        post_date=date(2026, 1, 1),
        splits=[
            synthetic_split(opening, Decimal("-10000.00"), memo="Synthetic opening memo source"),
            synthetic_split(checking, Decimal("10000.00"), memo="Synthetic opening memo checking"),
        ],
    )

    per_split_amount = Decimal("1.00")
    synthetic_transaction(
        2,
        description="Synthetic benchmark transaction many splits — Unicode café Привет 旅費",
        post_date=date(2026, 1, 2),
        splits=[
            synthetic_split(
                checking,
                -(per_split_amount * (many_split_count - 1)),
                memo="Synthetic many-split source memo",
            ),
            *[
                synthetic_split(
                    expense_accounts[idx % expense_account_count],
                    per_split_amount,
                    memo=f"Synthetic many-split repeated memo {idx:03d}",
                )
                for idx in range(many_split_count - 1)
            ],
        ],
    )

    start = date(2026, 1, 2)
    for idx in range(2, transaction_count):
        tx_date = start + timedelta(days=idx % 365)
        amount = Decimal((idx % 500) + 1).quantize(Decimal("0.01"))
        tx_guid_index = idx + 1
        if idx % 10 == 0:
            synthetic_transaction(
                tx_guid_index,
                description=synthetic_description("salary", idx),
                post_date=tx_date,
                splits=[
                    synthetic_split(salary, -(amount + Decimal("1000.00")), memo=synthetic_memo("salary", idx)),
                    synthetic_split(checking, amount + Decimal("1000.00"), memo=synthetic_memo("checking", idx)),
                ],
            )
        elif idx % 15 == 0:
            synthetic_transaction(
                tx_guid_index,
                description=synthetic_description("transfer", idx),
                post_date=tx_date,
                splits=[
                    synthetic_split(checking, -amount, memo=synthetic_memo("transfer-out", idx)),
                    synthetic_split(savings, amount, memo=synthetic_memo("transfer-in", idx)),
                ],
            )
        elif idx % 22 == 0:
            expense = expense_accounts[idx % expense_account_count]
            synthetic_transaction(
                tx_guid_index,
                description=synthetic_description("credit", idx),
                post_date=tx_date,
                splits=[
                    synthetic_split(credit_card, -amount, memo=synthetic_memo("credit", idx)),
                    synthetic_split(expense, amount, memo=synthetic_memo("expense", idx)),
                ],
            )
        else:
            expense = expense_accounts[idx % expense_account_count]
            synthetic_transaction(
                tx_guid_index,
                description=synthetic_description("expense", idx),
                post_date=tx_date,
                splits=[
                    synthetic_split(checking, -amount, memo=synthetic_memo("checking", idx)),
                    synthetic_split(expense, amount, memo=synthetic_memo("expense", idx)),
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


def create_issue55_account_performance_book(
    output_path: str | Path,
    *,
    candidate_account_count: int,
    transaction_count: int,
) -> FixtureMetadata:
    """Create an exact-cardinality issue #55 synthetic account performance book."""
    if candidate_account_count < 100:
        raise ValueError("candidate_account_count must be at least 100 for issue55 coverage")
    if transaction_count < 100:
        raise ValueError("transaction_count must be at least 100 for issue55 coverage")
    if candidate_account_count > 10_000:
        raise ValueError("candidate_account_count must not exceed the issue55 10k candidate guard")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    book = piecash.create_book(currency=BASE_CURRENCY, sqlite_file=str(output), overwrite=True)
    sek = _assign_guid(book.commodities[0], _synthetic_guid(ISSUE55_COMMODITY_GUID_NAMESPACE, 1))
    eur = _assign_guid(
        Commodity(namespace="CURRENCY", mnemonic="EUR", fullname="Synthetic Euro", fraction=100),
        _synthetic_guid(ISSUE55_COMMODITY_GUID_NAMESPACE, 2),
    )
    usd = _assign_guid(
        Commodity(namespace="CURRENCY", mnemonic="USD", fullname="Synthetic Dollar", fraction=100),
        _synthetic_guid(ISSUE55_COMMODITY_GUID_NAMESPACE, 3),
    )
    gbp = _assign_guid(
        Commodity(namespace="CURRENCY", mnemonic="GBP", fullname="Synthetic Pound", fraction=100),
        _synthetic_guid(ISSUE55_COMMODITY_GUID_NAMESPACE, 4),
    )
    commodities = [sek, eur, usd, gbp]
    root = _assign_guid(book.root_account, ISSUE55_ROOT_ACCOUNT_ID)
    root.commodity = sek
    for existing_account in list(book.accounts):
        if existing_account is not root:
            book.session.delete(existing_account)
    accounts: list[Account] = [root]
    split_index = 0

    def issue_account(
        name: str,
        account_type: str,
        parent: Account,
        commodity: Commodity,
        *,
        hidden: bool = False,
        placeholder: bool = False,
    ) -> Account:
        account_index = len(accounts)
        account = _assign_guid(
            Account(name=name, type=account_type, parent=parent, commodity=commodity),
            _synthetic_guid(ISSUE55_ACCOUNT_GUID_NAMESPACE, account_index),
        )
        account.hidden = hidden
        account.placeholder = placeholder
        accounts.append(account)
        return account

    def issue_split(account: Account, value: Decimal, *, quantity: Decimal | None = None, memo: str = "") -> Split:
        nonlocal split_index
        split_index += 1
        return _assign_guid(
            Split(account=account, value=value, quantity=quantity if quantity is not None else value, memo=memo),
            _synthetic_guid(ISSUE55_SPLIT_GUID_NAMESPACE, split_index),
        )

    assets = issue_account("As", "ASSET", root, sek)
    expenses = issue_account("Ex", "EXPENSE", root, sek)
    income = issue_account("In", "INCOME", root, sek)
    liabilities = issue_account("Li", "LIABILITY", root, sek)
    equity = issue_account("Eq", "EQUITY", root, sek)
    operating = issue_account("Bank", "BANK", assets, sek)
    issue_account("Cash", "CASH", assets, sek)
    mixed_parent = issue_account("Mix", "ASSET", assets, sek)
    mixed_children = [
        issue_account("MixSEK", "ASSET", mixed_parent, sek),
        issue_account("MixEUR", "ASSET", mixed_parent, eur),
        issue_account("MixUSD", "ASSET", mixed_parent, usd),
        issue_account("MixGBP", "ASSET", mixed_parent, gbp),
    ]
    deep_parent = mixed_parent
    for depth_index in range(1, 9):
        deep_parent = issue_account(f"D{depth_index}", "ASSET", deep_parent, commodities[depth_index % len(commodities)])
    duplicate_parent = issue_account("DupParent", "EXPENSE", expenses, sek)
    issue_account("Duplicate ζ", "EXPENSE", expenses, sek)
    issue_account("Duplicate ζ", "EXPENSE", duplicate_parent, sek)

    parent_pools: dict[str, list[Account]] = {
        "ASSET": [assets, mixed_parent, *mixed_children, deep_parent],
        "BANK": [assets, mixed_parent],
        "CASH": [assets, mixed_parent],
        "EXPENSE": [expenses, duplicate_parent],
        "INCOME": [income],
        "LIABILITY": [liabilities],
        "CREDIT": [liabilities],
        "EQUITY": [equity],
    }

    def add_parent_candidate(account: Account, account_type: str, hidden: bool) -> None:
        if hidden:
            return
        parent_pools[account_type].append(account)
        if account_type == "ASSET":
            parent_pools["BANK"].append(account)
            parent_pools["CASH"].append(account)
        elif account_type == "LIABILITY":
            parent_pools["CREDIT"].append(account)

    created_account_target = candidate_account_count
    account_types = ["ASSET", "BANK", "CASH", "EXPENSE", "INCOME", "LIABILITY", "CREDIT", "EQUITY"]
    while len(accounts) < created_account_target:
        account_index = len(accounts)
        account_type = account_types[account_index % len(account_types)]
        parent = parent_pools[account_type][account_index % len(parent_pools[account_type])]
        commodity = commodities[account_index % len(commodities)]
        name = f"A{account_index:05d}"
        if account_index % 113 == 0:
            name = f"{ISSUE55_ACCOUNT_QUERY_TEXT} {account_index:05d}"
        elif account_index % 211 == 0:
            name = f"家計{account_index:05d}"
        hidden = (
            account_index >= ISSUE55_1K_VISIBLE_ACCOUNT_INDEX_LIMIT
            if candidate_account_count <= 1_000
            else account_index % 97 == 0
        )
        placeholder = account_index % 89 == 0
        account = issue_account(name, account_type, parent, commodity, hidden=hidden, placeholder=placeholder)
        add_parent_candidate(account, account_type, hidden)

    visible_expenses = [
        account
        for account in accounts
        if account.type == "EXPENSE" and not account.hidden and not account.placeholder
    ]
    visible_income = [
        account
        for account in accounts
        if account.type == "INCOME" and not account.hidden and not account.placeholder
    ]
    if not visible_expenses or not visible_income:
        raise RuntimeError("issue55 fixture did not create visible income/expense accounts")

    start = date.fromisoformat(ISSUE55_ACCOUNT_DATE_FROM)
    for tx_index in range(transaction_count):
        post_date = start + timedelta(days=tx_index % 365)
        amount = Decimal((tx_index % 250) + 1).quantize(Decimal("0.01"))
        description = f"Issue55 synthetic transaction {tx_index:05d}"
        if tx_index % 997 == 0:
            description += f" {SPARSE_QUERY_TEXT}"
        if tx_index % 40 == 0:
            target = mixed_children[(tx_index // 40) % len(mixed_children)]
            native_quantity = amount if target.commodity is sek else (amount / Decimal("2")).quantize(Decimal("0.01"))
            splits = [
                issue_split(operating, -amount, memo=f"issue55 bank transfer {tx_index:05d}"),
                issue_split(target, amount, quantity=native_quantity, memo=f"issue55 mixed native {tx_index:05d}"),
            ]
        elif tx_index % 10 == 0:
            target = visible_income[tx_index % len(visible_income)]
            income_amount = amount + Decimal("1000.00")
            splits = [
                issue_split(operating, income_amount, memo=f"issue55 income bank {tx_index:05d}"),
                issue_split(target, -income_amount, memo=f"issue55 income source {tx_index:05d}"),
            ]
        else:
            target = visible_expenses[tx_index % len(visible_expenses)]
            splits = [
                issue_split(operating, -amount, memo=f"issue55 expense bank {tx_index:05d}"),
                issue_split(target, amount, memo=f"issue55 expense target {tx_index:05d}"),
            ]
        _assign_guid(
            Transaction(currency=sek, description=description, post_date=post_date, splits=splits),
            _synthetic_guid(ISSUE55_TRANSACTION_GUID_NAMESPACE, tx_index),
        )

    book.save()
    book.close()

    with sqlite3.connect(output) as conn:
        conn.execute(
            "delete from accounts where account_type = 'ROOT' and name = 'Template Root' and guid != ?",
            (ISSUE55_ROOT_ACCOUNT_ID,),
        )
        conn.execute(
            "update accounts set commodity_guid = ? where commodity_guid is null or commodity_guid not in (?, ?, ?, ?)",
            tuple(_synthetic_guid(ISSUE55_COMMODITY_GUID_NAMESPACE, idx) for idx in (1, 1, 2, 3, 4)),
        )
        conn.commit()
        rows = conn.execute("select guid, name, account_type, parent_guid, hidden, placeholder from accounts").fetchall()
        actual_candidate_accounts = len(rows)
        tx_rows = int(conn.execute("select count(*) from transactions").fetchone()[0])
        commodity_count = int(
            conn.execute("select count(distinct commodity_guid) from accounts where commodity_guid is not null").fetchone()[0]
        )
        duplicate_account_name_count = sum(
            int(row[1])
            for row in conn.execute(
                "select name, count(*) from accounts group by name having count(*) > 1"
            ).fetchall()
        )
    if actual_candidate_accounts != candidate_account_count or tx_rows != transaction_count:
        raise RuntimeError(
            f"issue55 fixture cardinality mismatch: accounts={actual_candidate_accounts}, transactions={tx_rows}"
        )
    names = [str(row[1]) for row in rows]
    parent_by_id = {str(row[0]): str(row[3]) if row[3] else None for row in rows}

    def row_depth(account_id: str) -> int:
        depth = 0
        seen: set[str] = set()
        parent_id = parent_by_id.get(account_id)
        while parent_id is not None and parent_id not in seen:
            seen.add(parent_id)
            depth += 1
            parent_id = parent_by_id.get(parent_id)
        return depth

    return FixtureMetadata(
        path=output,
        transaction_count=transaction_count,
        expense_account_count=sum(1 for row in rows if str(row[2]).upper() == "EXPENSE"),
        account_branch_count=sum(1 for row in rows if parent_by_id[str(row[0])] == ISSUE55_ROOT_ACCOUNT_ID),
        account_depth=max(row_depth(str(row[0])) for row in rows),
        synthetic_account_count=actual_candidate_accounts,
        many_split_count=2,
        synthetic=True,
        contains_real_data=False,
        candidate_account_count=actual_candidate_accounts,
        hidden_account_count=sum(1 for row in rows if bool(row[4])),
        placeholder_account_count=sum(1 for row in rows if bool(row[5])),
        commodity_count=commodity_count,
        duplicate_account_name_count=duplicate_account_name_count,
        unicode_account_name_count=sum(1 for name in names if any(ord(char) > 127 for char in name)),
    )


def _test_settings(allowed_root: Path | None = None) -> Settings:
    kwargs: dict[str, Any] = {
        "app_env": "benchmark",
        "app_database_url": "sqlite:///:memory:",
        "jwt_secret": "benchmark-secret-key-for-local-phase-87-only",
        "jwt_token_expire_minutes": 30,
        "app_admin_username": "admin",
        "app_admin_password": "benchmark-password",
    }
    if allowed_root is not None:
        kwargs["gnucash_book_allowed_roots"] = [str(allowed_root)]
    return Settings(**kwargs)


def _build_client(book_path: Path) -> tuple[TestClient, int, dict[str, str], Callable[[], None]]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    getattr(Base, "metadata").create_all(engine)
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


def _add_health_snapshot(session: Any, book_id: int, safe_code: str) -> None:
    snapshot = BookHealthSnapshot()
    snapshot.book_id = book_id
    if safe_code == "ready":
        snapshot.source_status = "ready"
        snapshot.open_status = "ready"
        snapshot.accounts_status = "ready"
        snapshot.transactions_status = "ready"
        snapshot.reports_status = "ready"
        snapshot.safe_code = "ready"
        session.add(snapshot)
        return
    snapshot.source_status = "failed"
    snapshot.open_status = "not_checked"
    snapshot.accounts_status = "not_checked"
    snapshot.transactions_status = "not_checked"
    snapshot.reports_status = "not_checked"
    snapshot.safe_code = safe_code
    session.add(snapshot)


def _add_book_access(session: Any, *, user_id: int, book_id: int) -> None:
    access = UserBookAccess()
    access.user_id = user_id
    access.book_id = book_id
    access.role = "owner"
    session.add(access)


def _issue56_book_payload(book_path: Path, *, name: str = "Issue 56 Synthetic Lifecycle Book") -> dict[str, Any]:
    return {
        "name": name,
        "storage_type": "sqlite",
        "uri_or_path": str(book_path),
        "base_currency": BASE_CURRENCY,
        "make_default": False,
    }


def _build_issue56_lifecycle_client(
    book_path: Path,
    *,
    extra_book_count: int = ISSUE56_EXTRA_REGISTERED_BOOKS,
) -> tuple[TestClient, int, int, dict[str, str], Any, Callable[[], None]]:
    """Build an in-memory app DB with synthetic registered and unavailable books."""

    settings = _test_settings(book_path.parent)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    getattr(Base, "metadata").create_all(engine)
    session_factory = sessionmaker(bind=engine)

    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db

    with session_factory() as session:
        user = User()
        user.username = "admin"
        user.display_name = "Benchmark Admin"
        user.password_hash = hash_password("benchmark-password")
        user.is_admin = True
        session.add(user)
        session.flush()

        primary = Book()
        primary.name = "Issue 56 Synthetic Registered Book"
        primary.storage_type = "sqlite"
        primary.uri_or_path = str(book_path)
        primary.base_currency = BASE_CURRENCY
        primary.is_default = True
        primary.is_enabled = True
        session.add(primary)
        session.flush()
        primary_id = int(primary.id)
        _add_book_access(session, user_id=int(user.id), book_id=primary_id)
        _add_health_snapshot(session, primary_id, "ready")

        missing_book = Book()
        missing_book.name = "Issue 56 Synthetic Missing Source"
        missing_book.storage_type = "sqlite"
        missing_book.uri_or_path = str(book_path.parent / "issue56-unavailable-synthetic.gnucash.sqlite")
        missing_book.base_currency = BASE_CURRENCY
        missing_book.is_default = False
        missing_book.is_enabled = True
        session.add(missing_book)
        session.flush()
        missing_id = int(missing_book.id)
        _add_book_access(session, user_id=int(user.id), book_id=missing_id)
        _add_health_snapshot(session, missing_id, "missing_file")

        for index in range(extra_book_count):
            extra = Book()
            extra.name = f"Issue 56 Synthetic Extra Book {index}"
            extra.storage_type = "sqlite"
            extra.uri_or_path = str(book_path.parent / f"issue56-extra-{index}.gnucash.sqlite")
            extra.base_currency = BASE_CURRENCY
            extra.is_default = False
            extra.is_enabled = True
            session.add(extra)
            session.flush()
            _add_book_access(session, user_id=int(user.id), book_id=int(extra.id))
            _add_health_snapshot(session, int(extra.id), "missing_file")
        session.commit()

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

    return client, primary_id, missing_id, headers, engine, cleanup


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
            "select guid from transactions where description like ?",
            ("Synthetic benchmark transaction many splits%",),
        ).fetchone()
    if row is None:
        raise RuntimeError("benchmark fixture did not expose a many-splits transaction id")
    return str(row[0])


def _select_first_transaction_id(book_path: Path) -> str:
    with sqlite3.connect(book_path) as conn:
        row = conn.execute("select guid from transactions order by post_date, guid limit 1").fetchone()
    if row is None:
        raise RuntimeError("benchmark fixture did not expose a transaction id")
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
    elif isinstance(payload, dict) and isinstance(payload.get("nodes"), list):
        item_count = len(payload["nodes"])
    elif isinstance(payload, dict) and isinstance(payload.get("recent_transactions"), list):
        item_count = len(payload["recent_transactions"])
    elif isinstance(payload, dict) and isinstance(payload.get("splits"), list):
        item_count = len(payload["splits"])
    elif case.name == "period_comparison_previous_equivalent" and isinstance(payload, dict):
        expense_changes = payload.get("expense_changes")
        if isinstance(expense_changes, list):
            item_count = len(expense_changes)
    return item_count, None, None, None


@dataclass
class _BenchmarkRequestCounters:
    read_only_book_opens: int = 0
    legacy_count_calls: int = 0
    full_transaction_materializations: int = 0
    report_transaction_visits: int = 0
    gnucash_sql_statements: int = 0
    account_objects_materialized: int = 0
    transaction_objects_materialized: int = 0
    split_objects_materialized: int = 0
    app_db_statements: int = 0
    preflight_piecash_opens: int = 0
    preflight_sqlite_queries: int = 0
    preflight_account_materializations: int = 0
    preflight_transaction_materializations: int = 0


@dataclass(frozen=True)
class _PreparedBenchmarkRequest:
    path: str
    output_path: str
    expected_item_ids: list[str] | None = None
    expected_item_amounts: list[str] | None = None


@contextmanager
def _instrument_benchmark_request(app_db_engine: Any | None = None):
    counters = _BenchmarkRequestCounters()
    gnucash_engines: list[Any] = []
    original_open = GnuCashBookService._open_piecash_book
    original_count = GnuCashBookService.count_transactions
    original_transactions = GnuCashBookService._transactions
    original_report_transactions = GnuCashBookService._report_transactions
    original_health_open = book_preflight._open_piecash_readonly_once
    original_sqlite_schema_probe = book_preflight._verify_sqlite_gnucash_schema

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        counters.app_db_statements += 1

    def before_gnucash_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        counters.gnucash_sql_statements += 1

    def account_loaded(target, context):
        counters.account_objects_materialized += 1

    def transaction_loaded(target, context):
        counters.transaction_objects_materialized += 1

    def split_loaded(target, context):
        counters.split_objects_materialized += 1

    def counted_open(self: GnuCashBookService, uri_or_path: str):
        counters.read_only_book_opens += 1
        book = original_open(self, uri_or_path)
        engine = getattr(getattr(book, "session", None), "bind", None)
        if engine is not None and all(existing is not engine for existing in gnucash_engines):
            event.listen(engine, "before_cursor_execute", before_gnucash_cursor_execute)
            gnucash_engines.append(engine)
        return book

    def counted_count(self: GnuCashBookService, *args: Any, **kwargs: Any):
        counters.legacy_count_calls += 1
        return original_count(self, *args, **kwargs)

    def counted_transactions(self: GnuCashBookService, book: Any):
        counters.full_transaction_materializations += 1
        return original_transactions(self, book)

    def counted_report_transactions(self: GnuCashBookService, book: Any):
        rows = original_report_transactions(self, book)

        def visit_counter():
            for row in rows:
                counters.report_transaction_visits += 1
                yield row

        return visit_counter()

    def counted_health_open(canonical_path: str) -> None:
        counters.preflight_piecash_opens += 1
        return original_health_open(canonical_path)

    def counted_sqlite_schema_probe(canonical_path: str):
        result = original_sqlite_schema_probe(canonical_path)
        counters.preflight_sqlite_queries += int(result.sqlite_query_count)
        return result

    GnuCashBookService._open_piecash_book = counted_open  # type: ignore[method-assign]
    GnuCashBookService.count_transactions = counted_count  # type: ignore[method-assign]
    GnuCashBookService._transactions = counted_transactions  # type: ignore[method-assign]
    GnuCashBookService._report_transactions = counted_report_transactions  # type: ignore[method-assign]
    book_preflight._open_piecash_readonly_once = counted_health_open  # type: ignore[assignment]
    book_preflight._verify_sqlite_gnucash_schema = counted_sqlite_schema_probe  # type: ignore[assignment]
    event.listen(piecash.Account, "load", account_loaded)
    event.listen(piecash.Transaction, "load", transaction_loaded)
    event.listen(piecash.Split, "load", split_loaded)
    if app_db_engine is not None:
        event.listen(app_db_engine, "before_cursor_execute", before_cursor_execute)
    try:
        yield counters
    finally:
        event.remove(piecash.Account, "load", account_loaded)
        event.remove(piecash.Transaction, "load", transaction_loaded)
        event.remove(piecash.Split, "load", split_loaded)
        for engine in gnucash_engines:
            event.remove(engine, "before_cursor_execute", before_gnucash_cursor_execute)
        if app_db_engine is not None:
            event.remove(app_db_engine, "before_cursor_execute", before_cursor_execute)
        GnuCashBookService._open_piecash_book = original_open  # type: ignore[method-assign]
        GnuCashBookService.count_transactions = original_count  # type: ignore[method-assign]
        GnuCashBookService._transactions = original_transactions  # type: ignore[method-assign]
        GnuCashBookService._report_transactions = original_report_transactions  # type: ignore[method-assign]
        book_preflight._open_piecash_readonly_once = original_health_open  # type: ignore[assignment]
        book_preflight._verify_sqlite_gnucash_schema = original_sqlite_schema_probe  # type: ignore[assignment]


def _append_cursor(path: str, cursor: str) -> str:
    return f"{path}&cursor={quote(cursor, safe='')}"


def _redact_cursor_path(path: str) -> str:
    if "cursor=" not in path:
        return path
    prefix, _separator, _cursor = path.partition("cursor=")
    return f"{prefix}cursor=<redacted>"


def _explorer_item_ids(payload: dict[str, Any]) -> list[str]:
    items = payload.get("items")
    if not isinstance(items, list):
        return []
    return [str(item.get("id")) for item in items if isinstance(item, dict) and item.get("id")]


def _explorer_item_amounts(payload: dict[str, Any]) -> list[str]:
    items = payload.get("items")
    if not isinstance(items, list):
        return []
    amounts: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        matched = item.get("matched_amount")
        if isinstance(matched, dict) and matched.get("amount") is not None:
            amounts.append(str(matched["amount"]))
    return amounts


def _activity_recent_ids_and_amounts(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    recent = payload.get("recent_transactions")
    if not isinstance(recent, list):
        return [], []
    ids: list[str] = []
    amounts: list[str] = []
    for item in recent:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        ids.append(str(item["id"]))
        matched = item.get("matched_quantity")
        if isinstance(matched, dict) and matched.get("amount") is not None:
            amounts.append(str(matched["amount"]))
    return ids, amounts


def _decimal_lists_match(left: list[str], right: list[str]) -> bool:
    if len(left) != len(right):
        return False
    return all(Decimal(left_item) == Decimal(right_item) for left_item, right_item in zip(left, right))


def _fetch_explorer_payload(client: TestClient, path: str, headers: dict[str, str]) -> dict[str, Any]:
    response = client.get(path, headers=headers)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("explorer benchmark expected a JSON object response")
    return payload


def _prepare_explorer_page_path(
    client: TestClient,
    *,
    headers: dict[str, str],
    base_path: str,
    page_number: int,
) -> str:
    if page_number < 1:
        raise ValueError("page_number must be at least 1")
    if page_number == 1:
        return base_path
    payload = _fetch_explorer_payload(client, base_path, headers)
    for _page in range(2, page_number):
        cursor = payload.get("next_cursor")
        if not isinstance(cursor, str) or not cursor:
            raise RuntimeError(f"synthetic fixture did not expose page {page_number} for explorer benchmark")
        payload = _fetch_explorer_payload(client, _append_cursor(base_path, cursor), headers)
    cursor = payload.get("next_cursor")
    if not isinstance(cursor, str) or not cursor:
        raise RuntimeError(f"synthetic fixture did not expose page {page_number} for explorer benchmark")
    return _append_cursor(base_path, cursor)


def _prepare_http_benchmark_request(
    case: BenchmarkCase,
    *,
    client: TestClient,
    book_id: int,
    headers: dict[str, str],
    account_id: str,
    many_split_transaction_id: str,
) -> _PreparedBenchmarkRequest:
    base_path = EXPLORER_FIRST_PAGE_TEMPLATE.format(book_id=book_id)
    if case.name == "transaction_explorer_later_forward_page":
        path = _prepare_explorer_page_path(
            client,
            headers=headers,
            base_path=base_path,
            page_number=EXPLORER_LATER_PAGE_NUMBER,
        )
        return _PreparedBenchmarkRequest(path=path, output_path=_redact_cursor_path(path))
    if case.name == "transaction_explorer_previous_page":
        previous_page_path = _prepare_explorer_page_path(
            client,
            headers=headers,
            base_path=base_path,
            page_number=EXPLORER_LATER_PAGE_NUMBER - 1,
        )
        previous_payload = _fetch_explorer_payload(client, previous_page_path, headers)
        expected_ids = _explorer_item_ids(previous_payload)
        next_cursor = previous_payload.get("next_cursor")
        if not isinstance(next_cursor, str) or not next_cursor:
            raise RuntimeError("synthetic fixture did not expose a forward cursor for previous traversal")
        later_payload = _fetch_explorer_payload(client, _append_cursor(base_path, next_cursor), headers)
        previous_cursor = later_payload.get("previous_cursor")
        if not isinstance(previous_cursor, str) or not previous_cursor:
            raise RuntimeError("synthetic fixture did not expose a previous cursor")
        path = _append_cursor(base_path, previous_cursor)
        return _PreparedBenchmarkRequest(
            path=path,
            output_path=_redact_cursor_path(path),
            expected_item_ids=expected_ids,
        )
    if case.name in {
        "issue55_1k_account_transaction_explorer_first_page",
        "issue55_10k_drilldown_first_page",
    }:
        activity_path = (
            f"/books/{book_id}/accounts/{ISSUE55_ACTIVITY_ACCOUNT_ID}/activity"
            f"?date_from={ISSUE55_ACCOUNT_DATE_FROM}&date_to={ISSUE55_ACCOUNT_DATE_TO}"
            f"&limit={ISSUE55_ACCOUNT_ACTIVITY_LIMIT}"
        )
        activity_response = client.get(activity_path, headers=headers)
        activity_response.raise_for_status()
        activity_payload = activity_response.json()
        if not isinstance(activity_payload, dict):
            raise RuntimeError("issue55 activity benchmark expected a JSON object response")
        expected_ids, expected_amounts = _activity_recent_ids_and_amounts(activity_payload)
        path = case.path_template.format(
            book_id=book_id,
            account_id=account_id,
            many_split_transaction_id=many_split_transaction_id,
            issue55_root_account_id=ISSUE55_ROOT_ACCOUNT_ID,
            issue55_mixed_account_id=ISSUE55_MIXED_PARENT_ACCOUNT_ID,
            issue55_activity_account_id=ISSUE55_ACTIVITY_ACCOUNT_ID,
        )
        return _PreparedBenchmarkRequest(
            path=path,
            output_path=path,
            expected_item_ids=expected_ids,
            expected_item_amounts=expected_amounts,
        )
    path = case.path_template.format(
        book_id=book_id,
        account_id=account_id,
        many_split_transaction_id=many_split_transaction_id,
        issue55_root_account_id=ISSUE55_ROOT_ACCOUNT_ID,
        issue55_mixed_account_id=ISSUE55_MIXED_PARENT_ACCOUNT_ID,
        issue55_activity_account_id=ISSUE55_ACTIVITY_ACCOUNT_ID,
    )
    return _PreparedBenchmarkRequest(path=path, output_path=path)


def _request_with_counters(
    client: TestClient,
    *,
    method: str,
    path: str,
    request_kwargs: dict[str, Any],
    expected_status_code: int = 200,
    app_db_engine: Any | None = None,
) -> tuple[Any, float, _BenchmarkRequestCounters]:
    with _instrument_benchmark_request(app_db_engine=app_db_engine) as counters:
        start = time.perf_counter()
        response = client.request(method, path, **request_kwargs)
        duration_ms = (time.perf_counter() - start) * 1000
    if response.status_code != expected_status_code:
        response.raise_for_status()
        raise RuntimeError(f"expected HTTP {expected_status_code}, got {response.status_code} for {path}")
    return response, duration_ms, counters


def _counter_summary(counters: list[_BenchmarkRequestCounters]) -> dict[str, int | None]:
    if not counters:
        return {
            "read_only_book_open_count_min": None,
            "read_only_book_open_count_max": None,
            "legacy_count_call_count_max": None,
            "full_transaction_materialization_count_max": None,
            "report_transaction_visit_count_max": None,
            "gnucash_sql_statement_count_min": None,
            "gnucash_sql_statement_count_max": None,
            "account_object_materialization_count_max": None,
            "transaction_object_materialization_count_max": None,
            "split_object_materialization_count_max": None,
            "app_db_statement_count_min": None,
            "app_db_statement_count_max": None,
            "preflight_sqlite_query_count_min": None,
            "preflight_sqlite_query_count_max": None,
            "preflight_piecash_open_count_min": None,
            "preflight_piecash_open_count_max": None,
            "preflight_account_materialization_count_max": None,
            "preflight_transaction_materialization_count_max": None,
        }
    return {
        "read_only_book_open_count_min": min(counter.read_only_book_opens for counter in counters),
        "read_only_book_open_count_max": max(counter.read_only_book_opens for counter in counters),
        "legacy_count_call_count_max": max(counter.legacy_count_calls for counter in counters),
        "full_transaction_materialization_count_max": max(
            counter.full_transaction_materializations for counter in counters
        ),
        "report_transaction_visit_count_max": max(counter.report_transaction_visits for counter in counters),
        "gnucash_sql_statement_count_min": min(counter.gnucash_sql_statements for counter in counters),
        "gnucash_sql_statement_count_max": max(counter.gnucash_sql_statements for counter in counters),
        "account_object_materialization_count_max": max(counter.account_objects_materialized for counter in counters),
        "transaction_object_materialization_count_max": max(
            counter.transaction_objects_materialized for counter in counters
        ),
        "split_object_materialization_count_max": max(counter.split_objects_materialized for counter in counters),
        "app_db_statement_count_min": min(counter.app_db_statements for counter in counters),
        "app_db_statement_count_max": max(counter.app_db_statements for counter in counters),
        "preflight_sqlite_query_count_min": min(counter.preflight_sqlite_queries for counter in counters),
        "preflight_sqlite_query_count_max": max(counter.preflight_sqlite_queries for counter in counters),
        "preflight_piecash_open_count_min": min(counter.preflight_piecash_opens for counter in counters),
        "preflight_piecash_open_count_max": max(counter.preflight_piecash_opens for counter in counters),
        "preflight_account_materialization_count_max": max(
            counter.preflight_account_materializations for counter in counters
        ),
        "preflight_transaction_materialization_count_max": max(
            counter.preflight_transaction_materializations for counter in counters
        ),
    }


def _summarize_response_metadata(
    response: Any,
    *,
    expected_item_ids: list[str] | None = None,
    expected_item_amounts: list[str] | None = None,
) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        return {}
    if not isinstance(payload, dict):
        return {}
    summary: dict[str, Any] = {}
    detail = payload.get("detail")
    if isinstance(detail, dict) and detail.get("code"):
        summary["error_code"] = str(detail["code"])
    items = payload.get("items")
    if isinstance(items, list):
        ids = [str(item.get("id")) for item in items if isinstance(item, dict) and item.get("id")]
        keys = [
            (str(item.get("date")), str(item.get("id")))
            for item in items
            if isinstance(item, dict) and item.get("date") and item.get("id")
        ]
        sort = payload.get("sort")
        if keys:
            summary["stable_unique_order"] = len(ids) == len(set(ids)) and keys == sorted(
                keys,
                reverse=sort == "date_desc",
            )
        if expected_item_ids is not None:
            summary["cursor_roundtrip_matches"] = ids == expected_item_ids
        if expected_item_amounts is not None:
            summary["activity_recent_ids_match"] = ids == (expected_item_ids or [])
            summary["activity_recent_amounts_match"] = _decimal_lists_match(
                _explorer_item_amounts(payload),
                expected_item_amounts,
            )
    nodes = payload.get("nodes")
    if isinstance(nodes, list):
        depths = [int(node.get("depth", 0)) for node in nodes if isinstance(node, dict)]
        recursive_counts = [
            len(node.get("recursive_balances") or [])
            for node in nodes
            if isinstance(node, dict)
        ]
        summary["account_returned_nodes"] = len(nodes)
        summary["account_max_depth"] = max(depths, default=0)
        summary["account_max_recursive_commodity_buckets"] = max(recursive_counts, default=0)
    children = payload.get("children")
    if isinstance(children, list):
        depths = [int(child.get("depth", 0)) for child in children if isinstance(child, dict)]
        recursive_counts = [
            len(child.get("recursive_balances") or [])
            for child in children
            if isinstance(child, dict)
        ]
        root_recursive = payload.get("recursive_balances") or []
        summary["account_max_depth"] = max(depths + [int(payload.get("depth", 0))], default=0)
        summary["account_max_recursive_commodity_buckets"] = max(
            recursive_counts + [len(root_recursive) if isinstance(root_recursive, list) else 0],
            default=0,
        )
        summary["overview_subtree_account_count"] = payload.get("subtree_account_count")
        summary["overview_child_count"] = payload.get("child_count")
        summary["overview_children_returned"] = payload.get("children_returned")
    recent = payload.get("recent_transactions")
    if isinstance(recent, list):
        ids, amounts = _activity_recent_ids_and_amounts(payload)
        summary["activity_recent_item_count"] = len(recent)
        if expected_item_ids is not None:
            summary["activity_recent_ids_match"] = ids == expected_item_ids
        if expected_item_amounts is not None:
            summary["activity_recent_amounts_match"] = _decimal_lists_match(amounts, expected_item_amounts)
    for key in ("returned_count", "page_size", "has_more", "has_previous"):
        if key in payload:
            summary[key] = payload[key]
    next_cursor = payload.get("next_cursor")
    previous_cursor = payload.get("previous_cursor")
    if isinstance(next_cursor, str):
        summary["next_cursor_length"] = len(next_cursor)
    if isinstance(previous_cursor, str):
        summary["previous_cursor_length"] = len(previous_cursor)
    scan = payload.get("scan")
    if isinstance(scan, dict):
        summary["scan_candidate_rows"] = scan.get("candidate_rows")
        summary["scan_split_rows"] = scan.get("split_rows")
        summary["scan_query_count"] = scan.get("query_count")
        summary["scan_limited"] = scan.get("scan_limited")
        summary["scan_exhausted"] = scan.get("exhausted")
        if scan.get("query_count") is not None:
            summary["actual_query_count"] = scan.get("query_count")
        if scan.get("candidate_accounts") is not None:
            summary["account_candidate_accounts"] = scan.get("candidate_accounts")
            summary["account_returned_nodes"] = scan.get("returned_nodes")
            summary["account_split_rows"] = scan.get("split_rows")
            summary["account_split_aggregate_rows"] = scan.get("split_aggregate_rows")
            summary["account_rollup_bucket_cells"] = scan.get("rollup_bucket_cells")
            summary["account_serialized_bytes"] = scan.get("serialized_bytes")
        if scan.get("change_split_rows") is not None:
            summary["activity_change_split_rows"] = scan.get("change_split_rows")
            summary["activity_recent_split_rows"] = scan.get("recent_split_rows")
            summary["activity_recent_transaction_objects"] = scan.get("recent_transaction_objects")
            summary["account_serialized_bytes"] = scan.get("serialized_bytes")
        limits = scan.get("limits")
        if isinstance(limits, dict):
            summary["scan_limits"] = {str(key): int(value) for key, value in limits.items()}
    return summary


def _count_book_transactions(book_path: Path) -> int:
    with sqlite3.connect(book_path) as conn:
        return int(conn.execute("select count(*) from transactions").fetchone()[0])


def _local_timing_budget(case_name: str, transaction_count: int) -> tuple[str | None, int | None]:
    if transaction_count >= 10_000:
        dataset = "10k"
    elif transaction_count >= 1_000:
        dataset = "1k"
    else:
        return None, None
    return dataset, LOCAL_TIMING_BUDGETS_MS.get(dataset, {}).get(case_name)


def _run_service_benchmark_case(
    case: BenchmarkCase,
    *,
    book_path: Path,
    debit_account_id: str,
    credit_account_id: str,
    many_split_transaction_id: str,
    repeats: int,
    warmups: int,
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
        for _ in range(warmups):
            service.validate_transaction_create(request)
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
        for _ in range(warmups):
            _verify_transaction_create_readback(synthetic_book, request, result)
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
        warmup_count=warmups,
        measured_samples=repeats,
    )


def run_benchmark(
    book_path: str | Path,
    *,
    repeats: int = 3,
    warmups: int = 1,
    case_names: set[str] | None = None,
) -> list[BenchmarkResult]:
    """Run selected synthetic benchmark cases without enabling mutation routes."""
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if warmups < 0:
        raise ValueError("warmups must be zero or greater")
    selected_cases = benchmark_plan(case_names)
    return _run_benchmark_cases(book_path, selected_cases=selected_cases, repeats=repeats, warmups=warmups)


def run_issue55_account_benchmark(
    book_path: str | Path,
    *,
    dataset: str,
    repeats: int = 3,
    warmups: int = 1,
    case_names: set[str] | None = None,
) -> list[BenchmarkResult]:
    """Run the issue #55 synthetic account performance cases for one dataset."""
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if warmups < 0:
        raise ValueError("warmups must be zero or greater")
    selected_cases = issue55_account_benchmark_plan(dataset, case_names)
    return _run_benchmark_cases(book_path, selected_cases=selected_cases, repeats=repeats, warmups=warmups)


def run_issue56_lifecycle_benchmark(
    book_path: str | Path,
    *,
    repeats: int = 3,
    warmups: int = 1,
    case_names: set[str] | None = None,
    extra_book_count: int = ISSUE56_EXTRA_REGISTERED_BOOKS,
) -> list[BenchmarkResult]:
    """Run issue #56 lifecycle/preflight cases on synthetic local books only."""
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if warmups < 0:
        raise ValueError("warmups must be zero or greater")
    selected_cases = issue56_lifecycle_benchmark_plan(case_names)
    resolved_book_path = Path(book_path)
    client, book_id, missing_book_id, headers, app_db_engine, cleanup = _build_issue56_lifecycle_client(
        resolved_book_path,
        extra_book_count=extra_book_count,
    )
    try:
        results: list[BenchmarkResult] = []
        transaction_count = _count_book_transactions(resolved_book_path)
        for case in selected_cases:
            path = case.path_template.format(book_id=book_id, missing_book_id=missing_book_id)
            request_kwargs: dict[str, Any] = {"headers": headers}
            if case.request_json == "issue56_book_payload":
                request_kwargs["json"] = _issue56_book_payload(resolved_book_path)
            elif case.request_json is not None:
                raise ValueError(f"unsupported issue56 request_json: {case.request_json}")

            for _ in range(warmups):
                response = client.request(case.method, path, **request_kwargs)
                if response.status_code != case.expected_status_code:
                    response.raise_for_status()
                    raise RuntimeError(
                        f"expected HTTP {case.expected_status_code}, got {response.status_code} for {path}"
                    )

            durations: list[float] = []
            counters: list[_BenchmarkRequestCounters] = []
            last_response = None
            for _ in range(repeats):
                response, duration_ms, request_counters = _request_with_counters(
                    client,
                    method=case.method,
                    path=path,
                    request_kwargs=request_kwargs,
                    expected_status_code=case.expected_status_code,
                    app_db_engine=app_db_engine,
                )
                durations.append(duration_ms)
                counters.append(request_counters)
                last_response = response
            if last_response is None:  # pragma: no cover - repeats validation prevents this
                raise RuntimeError("issue56 benchmark produced no response")
            item_count, csv_limit, csv_total, csv_truncated = _summarize_response(case, last_response)
            counter_summary = _counter_summary(counters)
            response_summary = _summarize_response_metadata(last_response)
            budget_dataset, budget_ms = _local_timing_budget(case.name, transaction_count)
            median_ms = round(statistics.median(durations), 2)
            results.append(
                BenchmarkResult(
                    name=case.name,
                    method=case.method,
                    path=path,
                    status_code=last_response.status_code,
                    duration_ms_min=round(min(durations), 2),
                    duration_ms_median=median_ms,
                    duration_ms_max=round(max(durations), 2),
                    response_bytes=len(last_response.content),
                    item_count=item_count,
                    csv_limit=csv_limit,
                    csv_total=csv_total,
                    csv_truncated=csv_truncated,
                    warmup_count=warmups,
                    measured_samples=repeats,
                    mutation_capable_request_count=0 if case.method in {"GET", "HEAD"} else 1,
                    local_timing_budget_dataset=budget_dataset,
                    local_timing_budget_ms=budget_ms,
                    local_timing_budget_passed=(median_ms <= budget_ms) if budget_ms is not None else None,
                    **counter_summary,
                    **response_summary,
                )
            )
        return results
    finally:
        cleanup()


def _run_benchmark_cases(
    book_path: str | Path,
    *,
    selected_cases: list[BenchmarkCase],
    repeats: int,
    warmups: int,
) -> list[BenchmarkResult]:
    resolved_book_path = Path(book_path)
    transaction_count = _count_book_transactions(resolved_book_path)
    client, book_id, headers, cleanup = _build_client(resolved_book_path)
    try:
        needs_legacy_account_id = any("{account_id}" in case.path_template for case in selected_cases)
        needs_preview_account_ids = any(case.request_json is not None for case in selected_cases)
        account_id = (
            _select_account_id(client, book_id, headers)
            if needs_legacy_account_id
            else ISSUE55_ACTIVITY_ACCOUNT_ID
        )
        if needs_preview_account_ids:
            preview_debit_account_id, preview_credit_account_id = _select_preview_account_ids(client, book_id, headers)
        else:
            preview_debit_account_id = ISSUE55_ACTIVITY_ACCOUNT_ID
            preview_credit_account_id = ISSUE55_MIXED_PARENT_ACCOUNT_ID
        needs_many_split_transaction = any(
            case.name == "many_splits_transaction_detail"
            or case.request_json == "synthetic_existing_transaction_readback"
            for case in selected_cases
        )
        many_split_transaction_id = (
            _select_many_split_transaction_id(resolved_book_path)
            if needs_many_split_transaction
            else _select_first_transaction_id(resolved_book_path)
        )
        results: list[BenchmarkResult] = []
        median_by_case: dict[str, float] = {}
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
                        warmups=warmups,
                    )
                )
                continue
            prepared = _prepare_http_benchmark_request(
                case,
                client=client,
                book_id=book_id,
                headers=headers,
                account_id=account_id,
                many_split_transaction_id=many_split_transaction_id,
            )
            durations: list[float] = []
            counters: list[_BenchmarkRequestCounters] = []
            last_response = None
            request_json = _build_case_request_json(
                case,
                debit_account_id=preview_debit_account_id,
                credit_account_id=preview_credit_account_id,
            )
            request_kwargs: dict[str, Any] = {"headers": headers}
            if request_json is not None:
                request_kwargs["json"] = request_json
            for _ in range(warmups):
                response = client.request(case.method, prepared.path, **request_kwargs)
                if response.status_code != case.expected_status_code:
                    response.raise_for_status()
                    raise RuntimeError(
                        f"expected HTTP {case.expected_status_code}, got {response.status_code} for {prepared.path}"
                    )
            for _ in range(repeats):
                response, duration_ms, request_counters = _request_with_counters(
                    client,
                    method=case.method,
                    path=prepared.path,
                    request_kwargs=request_kwargs,
                    expected_status_code=case.expected_status_code,
                )
                durations.append(duration_ms)
                counters.append(request_counters)
                last_response = response
            if last_response is None:  # pragma: no cover - repeats validation prevents this
                raise RuntimeError("benchmark produced no response")
            item_count, csv_limit, csv_total, csv_truncated = _summarize_response(case, last_response)
            counter_summary = _counter_summary(counters)
            response_summary = _summarize_response_metadata(
                last_response,
                expected_item_ids=prepared.expected_item_ids,
                expected_item_amounts=prepared.expected_item_amounts,
            )
            budget_dataset, budget_ms = _local_timing_budget(case.name, transaction_count)
            median_ms = round(statistics.median(durations), 2)
            relative_reference_ms = None
            relative_budget_passed = None
            if budget_dataset == "10k" and case.name in {
                "transaction_explorer_later_forward_page",
                "transaction_explorer_previous_page",
            }:
                relative_reference_ms = median_by_case.get("transaction_explorer_first_page")
                if relative_reference_ms is not None:
                    relative_budget_passed = median_ms <= (2 * relative_reference_ms)
            if case.name == "transaction_explorer_first_page":
                relative_reference_ms = median_by_case.get("transactions_list_first_page")
                if relative_reference_ms is not None:
                    relative_budget_passed = median_ms <= (0.5 * relative_reference_ms)
            results.append(
                BenchmarkResult(
                    name=case.name,
                    method=case.method,
                    path=prepared.output_path,
                    status_code=last_response.status_code,
                    duration_ms_min=round(min(durations), 2),
                    duration_ms_median=median_ms,
                    duration_ms_max=round(max(durations), 2),
                    response_bytes=len(last_response.content),
                    item_count=item_count,
                    csv_limit=csv_limit,
                    csv_total=csv_total,
                    csv_truncated=csv_truncated,
                    warmup_count=warmups,
                    measured_samples=repeats,
                    mutation_capable_request_count=0 if case.method in {"GET", "HEAD"} else 1,
                    local_timing_budget_dataset=budget_dataset,
                    local_timing_budget_ms=budget_ms,
                    local_timing_budget_passed=(median_ms <= budget_ms) if budget_ms is not None else None,
                    local_relative_timing_budget_reference_ms=relative_reference_ms,
                    local_relative_timing_budget_passed=relative_budget_passed,
                    **counter_summary,
                    **response_summary,
                )
            )
            median_by_case[case.name] = median_ms
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
    includes_lifecycle_probe = any(name.startswith("issue56_") for name in result_names)
    includes_health_recheck = "issue56_health_recheck" in result_names
    payload = {
        "fixture": {**asdict(metadata), "path": str(metadata.path)},
        "results": [asdict(result) for result in results],
        "scope": {
            "synthetic_generated_data_only": True,
            "local_synthetic_measurements_only": True,
            "non_mutating_read_and_preview_paths_only": not includes_lifecycle_probe,
            "non_mutating_read_preview_validation_readback_paths_only": not includes_lifecycle_probe,
            "read_only_api_paths_only": read_only_api_paths_only,
            "includes_write_preview_validation_path": includes_write_preview,
            "includes_transaction_validation_service_path": includes_validation_service,
            "includes_existing_synthetic_readback_path": includes_readback_service,
            "includes_lifecycle_preflight_probe_path": includes_lifecycle_probe,
            "includes_lifecycle_health_recheck_metadata_write_path": includes_health_recheck,
            "app_metadata_write_routes_called": includes_health_recheck,
            "source_book_writes_executed": False,
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
        description="Run local synthetic large-book, issue #55 account, and issue #56 lifecycle benchmarks"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--transactions", type=int, default=BenchmarkConfig.transaction_count)
    parser.add_argument("--expense-accounts", type=int, default=BenchmarkConfig.expense_account_count)
    parser.add_argument("--account-branches", type=int, default=BenchmarkConfig.account_branch_count)
    parser.add_argument("--account-depth", type=int, default=BenchmarkConfig.account_depth)
    parser.add_argument("--many-splits", type=int, default=BenchmarkConfig.many_split_count)
    parser.add_argument("--repeats", type=int, default=BenchmarkConfig.repeats)
    parser.add_argument("--warmups", type=int, default=BenchmarkConfig.warmups)
    parser.add_argument(
        "--issue55-account-dataset",
        choices=sorted(ISSUE55_ACCOUNT_DATASETS),
        default=None,
        help="Generate and run the issue #55 account benchmark dataset instead of the legacy large-book plan.",
    )
    parser.add_argument(
        "--issue56-lifecycle",
        action="store_true",
        help="Generate a local synthetic book and run issue #56 lifecycle/preflight benchmark cases.",
    )
    parser.add_argument(
        "--case",
        action="append",
        dest="case_names",
        default=None,
        help="Run only the named benchmark case; repeat for multiple cases.",
    )
    parser.add_argument("--json-output", type=Path, default=None)
    args = parser.parse_args(argv)

    selected_case_names = set(args.case_names) if args.case_names else None
    if args.issue56_lifecycle and args.issue55_account_dataset:
        parser.error("--issue56-lifecycle cannot be combined with --issue55-account-dataset")
    if args.issue56_lifecycle:
        metadata = create_large_synthetic_book(
            args.output,
            transaction_count=args.transactions,
            expense_account_count=args.expense_accounts,
            account_branch_count=args.account_branches,
            account_depth=args.account_depth,
            many_split_count=args.many_splits,
        )
        results = run_issue56_lifecycle_benchmark(
            metadata.path,
            repeats=args.repeats,
            warmups=args.warmups,
            case_names=selected_case_names,
        )
    elif args.issue55_account_dataset:
        candidate_account_count, transaction_count = ISSUE55_ACCOUNT_DATASETS[args.issue55_account_dataset]
        metadata = create_issue55_account_performance_book(
            args.output,
            candidate_account_count=candidate_account_count,
            transaction_count=transaction_count,
        )
        results = run_issue55_account_benchmark(
            metadata.path,
            dataset=args.issue55_account_dataset,
            repeats=args.repeats,
            warmups=args.warmups,
            case_names=selected_case_names,
        )
    else:
        metadata = create_large_synthetic_book(
            args.output,
            transaction_count=args.transactions,
            expense_account_count=args.expense_accounts,
            account_branch_count=args.account_branches,
            account_depth=args.account_depth,
            many_split_count=args.many_splits,
        )
        results = run_benchmark(
            metadata.path,
            repeats=args.repeats,
            warmups=args.warmups,
            case_names=selected_case_names,
        )

    print("Local synthetic large-book, issue #55 account, and issue #56 lifecycle benchmark")
    print(f"Synthetic fixture: {metadata.path}")
    print(f"Transactions: {metadata.transaction_count}")
    print(f"Expense accounts: {metadata.expense_account_count}")
    print(f"Synthetic hierarchy branches: {metadata.account_branch_count}")
    print(f"Synthetic hierarchy depth: {metadata.account_depth}")
    print(f"Synthetic account count: {metadata.synthetic_account_count}")
    if metadata.candidate_account_count is not None:
        print(f"Candidate accounts: {metadata.candidate_account_count}")
        print(f"Hidden accounts: {metadata.hidden_account_count}")
        print(f"Placeholder accounts: {metadata.placeholder_account_count}")
        print(f"Native commodities: {metadata.commodity_count}")
    print(f"Many-splits transaction splits: {metadata.many_split_count}")
    print(f"Warm-up requests per case: {args.warmups}")
    print(f"Measured samples per case: {args.repeats}")
    if selected_case_names:
        print(f"Selected benchmark cases: {', '.join(sorted(selected_case_names))}")
    if any(result.name.startswith("issue56_") for result in results):
        print(
            "Scope: local synthetic fixture only; lifecycle/preflight probes may update synthetic app metadata only."
        )
        print("No private book data used; no GnuCash source writes executed; no production performance claim.")
    else:
        print(
            "Scope: local synthetic fixture only; non-mutating read, create-preview, validation, and read-back paths only."
        )
        print("No private book data used; no writes executed; no production performance claim.")
    for result in results:
        extra = ""
        if result.error_code is not None:
            extra += f", error_code={result.error_code}"
        if result.item_count is not None:
            extra += f", items={result.item_count}"
        if result.csv_total is not None:
            extra += (
                f", csv_limit={result.csv_limit}, csv_total={result.csv_total}, "
                f"truncated={result.csv_truncated}, "
                f"expected_body_rows={result.csv_expected_body_rows}, "
                f"body_matches_expected={result.csv_body_matches_expected}"
            )
        if result.next_cursor_length is not None:
            extra += f", next_cursor_len={result.next_cursor_length}"
        if result.previous_cursor_length is not None:
            extra += f", previous_cursor_len={result.previous_cursor_length}"
        if result.scan_candidate_rows is not None:
            extra += (
                f", scan_candidates={result.scan_candidate_rows}, scan_splits={result.scan_split_rows}, "
                f"scan_queries={result.scan_query_count}, scan_limited={result.scan_limited}"
            )
        if result.account_candidate_accounts is not None:
            extra += (
                f", account_candidates={result.account_candidate_accounts}, "
                f"returned_nodes={result.account_returned_nodes}, depth={result.account_max_depth}, "
                f"bucket_max={result.account_max_recursive_commodity_buckets}, "
                f"rollup_cells={result.account_rollup_bucket_cells}, data_queries={result.actual_query_count}, "
                f"account_splits={result.account_split_rows}, "
                f"account_aggregates={result.account_split_aggregate_rows}, "
                f"serialized_bytes={result.account_serialized_bytes}"
            )
        if result.overview_subtree_account_count is not None:
            extra += (
                f", overview_subtree={result.overview_subtree_account_count}, "
                f"overview_children={result.overview_children_returned}/{result.overview_child_count}"
            )
        if result.activity_recent_item_count is not None:
            extra += (
                f", recent_items={result.activity_recent_item_count}, "
                f"activity_change_splits={result.activity_change_split_rows}, "
                f"activity_recent_splits={result.activity_recent_split_rows}, "
                f"activity_recent_tx_objects={result.activity_recent_transaction_objects}"
            )
        if result.activity_recent_ids_match is not None:
            extra += (
                f", activity_ids_match={result.activity_recent_ids_match}, "
                f"activity_amounts_match={result.activity_recent_amounts_match}"
            )
        if result.read_only_book_open_count_max is not None:
            extra += (
                f", opens={result.read_only_book_open_count_min}-{result.read_only_book_open_count_max}, "
                f"count_calls={result.legacy_count_call_count_max}, "
                f"tx_materializations={result.full_transaction_materialization_count_max}"
            )
        if result.app_db_statement_count_max is not None:
            extra += (
                f", app_db_statements={result.app_db_statement_count_min}-{result.app_db_statement_count_max}, "
                f"preflight_sqlite_queries={result.preflight_sqlite_query_count_min}-"
                f"{result.preflight_sqlite_query_count_max}, "
                f"preflight_opens={result.preflight_piecash_open_count_min}-"
                f"{result.preflight_piecash_open_count_max}"
            )
        if result.gnucash_sql_statement_count_max is not None:
            extra += (
                f", gnucash_sql={result.gnucash_sql_statement_count_min}-"
                f"{result.gnucash_sql_statement_count_max}, account_objects="
                f"{result.account_object_materialization_count_max}, tx_objects="
                f"{result.transaction_object_materialization_count_max}, split_objects="
                f"{result.split_object_materialization_count_max}"
            )
        if result.local_timing_budget_ms is not None:
            extra += (
                f", local_budget={result.local_timing_budget_dataset}:{result.local_timing_budget_ms}ms, "
                f"budget_passed={result.local_timing_budget_passed}"
            )
        if result.local_relative_timing_budget_reference_ms is not None:
            extra += (
                f", relative_budget_ref={result.local_relative_timing_budget_reference_ms:.2f}ms, "
                f"relative_budget_passed={result.local_relative_timing_budget_passed}"
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
