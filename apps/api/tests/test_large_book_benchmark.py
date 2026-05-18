"""Tests for the Phase 87 large-book read-only benchmark helper."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.performance.large_book_benchmark import (
    BENCHMARK_CASES,
    BenchmarkConfig,
    benchmark_plan,
    create_large_synthetic_book,
)


def test_benchmark_plan_covers_phase_87_read_only_scope() -> None:
    plan = benchmark_plan()
    names = [case.name for case in plan]

    assert names == [
        "accounts_tree_load",
        "transactions_list_first_page",
        "transaction_filters",
        "account_detail_transactions",
        "account_detail_transactions_page_2",
        "many_splits_transaction_detail",
        "dashboard_summary",
        "dashboard_cashflow_monthly",
        "dashboard_expenses_by_account_month",
        "dashboard_recent_transactions",
        "csv_export_up_to_cap",
    ]
    assert plan == BENCHMARK_CASES
    assert all(case.read_only for case in plan)


def test_create_large_synthetic_book_uses_only_disposable_data(tmp_path: Path) -> None:
    output = tmp_path / "phase-87-small.gnucash.sqlite"

    metadata = create_large_synthetic_book(
        output,
        transaction_count=24,
        expense_account_count=4,
        many_split_count=8,
    )

    assert metadata.path == output
    assert metadata.transaction_count == 24
    assert metadata.expense_account_count == 4
    assert metadata.many_split_count == 8
    assert metadata.synthetic is True
    assert metadata.contains_real_data is False
    assert output.exists()

    with sqlite3.connect(output) as conn:
        account_count = conn.execute("select count(*) from accounts").fetchone()[0]
        tx_count = conn.execute("select count(*) from transactions").fetchone()[0]
        descriptions = [
            row[0]
            for row in conn.execute(
                "select description from transactions order by post_date, description limit 5"
            ).fetchall()
        ]
        many_split_tx_guid = conn.execute(
            "select guid from transactions where description = 'Synthetic benchmark transaction many splits'"
        ).fetchone()[0]
        many_split_count = conn.execute(
            "select count(*) from splits where tx_guid = ?",
            (many_split_tx_guid,),
        ).fetchone()[0]

    assert account_count >= 10
    assert tx_count == 24
    assert many_split_count == 8
    assert all(description.startswith("Synthetic benchmark transaction") for description in descriptions)


def test_create_large_synthetic_book_rejects_too_small_scope(tmp_path: Path) -> None:
    output = tmp_path / "invalid.gnucash.sqlite"
    config = BenchmarkConfig(transaction_count=0, expense_account_count=1)

    try:
        create_large_synthetic_book(
            output,
            transaction_count=config.transaction_count,
            expense_account_count=config.expense_account_count,
        )
    except ValueError as exc:
        assert "transaction_count" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("expected ValueError for empty benchmark scope")


def test_create_large_synthetic_book_rejects_too_few_many_splits(tmp_path: Path) -> None:
    output = tmp_path / "invalid-many-splits.gnucash.sqlite"

    try:
        create_large_synthetic_book(output, transaction_count=10, expense_account_count=4, many_split_count=1)
    except ValueError as exc:
        assert "many_split_count" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("expected ValueError for too small many-splits scope")
