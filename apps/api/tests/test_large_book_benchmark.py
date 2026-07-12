"""Tests for the Phase 87 large-book read-only benchmark helper."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.schemas.gnucash import TransactionDetailDTO, TransactionSplitDTO
from app.performance.large_book_benchmark import (
    BENCHMARK_CASES,
    BenchmarkCase,
    BenchmarkConfig,
    BenchmarkResult,
    FixtureMetadata,
    _build_case_request_json,
    _build_readback_request_from_detail,
    _summarize_response,
    benchmark_plan,
    create_large_synthetic_book,
    write_results_json,
)


def test_benchmark_plan_covers_phase_87_read_only_scope() -> None:
    plan = benchmark_plan()
    names = [case.name for case in plan]

    assert names == [
        "accounts_tree_load",
        "accounts_tree_large_hierarchy_filter_seed",
        "transactions_list_first_page",
        "transaction_filters",
        "account_detail_transactions",
        "account_detail_transactions_page_2",
        "account_detail_transactions_filtered",
        "account_detail_csv_export",
        "many_splits_transaction_detail",
        "transaction_create_preview_validation",
        "transaction_create_validation_service",
        "transaction_create_readback_existing_synthetic",
        "dashboard_summary",
        "dashboard_cashflow_monthly",
        "dashboard_expenses_by_account_month",
        "dashboard_recent_transactions",
        "period_comparison_previous_equivalent",
        "csv_export_up_to_cap",
    ]
    assert plan == BENCHMARK_CASES
    assert all(case.read_only for case in plan)
    preview_case = next(case for case in plan if case.name == "transaction_create_preview_validation")
    assert preview_case.method == "POST"
    assert preview_case.path_template == "/books/{book_id}/transactions/create-preview"
    assert preview_case.request_json == "synthetic_create_preview"
    validation_case = next(case for case in plan if case.name == "transaction_create_validation_service")
    assert validation_case.method == "SERVICE"
    assert validation_case.path_template == "GnuCashWriteService.validate_transaction_create"
    assert validation_case.request_json == "synthetic_transaction_validation"
    readback_case = next(case for case in plan if case.name == "transaction_create_readback_existing_synthetic")
    assert readback_case.method == "SERVICE"
    assert readback_case.path_template == "transactions._verify_transaction_create_readback"
    assert readback_case.request_json == "synthetic_existing_transaction_readback"
    comparison_case = next(case for case in plan if case.name == "period_comparison_previous_equivalent")
    assert comparison_case.method == "GET"
    assert comparison_case.read_only is True
    assert comparison_case.request_json is None
    assert comparison_case.path_template == (
        "/books/{book_id}/reports/comparison?date_from=2026-07-02&date_to=2026-12-30"
        "&comparison_mode=previous_equivalent"
        "&comparison_date_from=2026-01-01&comparison_date_to=2026-07-01"
    )


def test_benchmark_plan_can_select_issue53_comparison_without_mutation_adjacent_cases() -> None:
    plan = benchmark_plan(case_names={"period_comparison_previous_equivalent"})

    assert [case.name for case in plan] == ["period_comparison_previous_equivalent"]
    assert all(case.method == "GET" for case in plan)
    assert all(case.request_json is None for case in plan)
    assert not any("create" in case.name or case.method in {"POST", "SERVICE"} for case in plan)


def test_synthetic_create_preview_benchmark_payload_is_local_disposable_only() -> None:
    case = BenchmarkCase(
        "transaction_create_preview_validation",
        "POST",
        "/books/{book_id}/transactions/create-preview",
        request_json="synthetic_create_preview",
    )

    payload = _build_case_request_json(case, debit_account_id="checking-guid", credit_account_id="expense-guid")

    assert payload == {
        "date": "2026-06-15",
        "debit_account_id": "checking-guid",
        "credit_account_id": "expense-guid",
        "amount": "123.4500",
        "currency": "SEK",
        "description": "Synthetic benchmark create preview only",
        "memo": "Synthetic local performance preview; no write executed",
    }
    serialized = str(payload)
    assert "/" not in serialized
    assert "private" not in serialized.lower()
    assert "real" not in serialized.lower()


def test_synthetic_transaction_validation_benchmark_payload_is_local_disposable_only() -> None:
    case = BenchmarkCase(
        "transaction_create_validation_service",
        "SERVICE",
        "GnuCashWriteService.validate_transaction_create",
        request_json="synthetic_transaction_validation",
    )

    payload = _build_case_request_json(case, debit_account_id="checking-guid", credit_account_id="expense-guid")

    assert payload == {
        "date": "2026-06-15",
        "description": "Synthetic benchmark create validation only",
        "splits": [
            {
                "account_id": "checking-guid",
                "amount": "-123.4500",
                "currency": "SEK",
                "memo": "Synthetic local validation performance; no write executed",
            },
            {
                "account_id": "expense-guid",
                "amount": "123.4500",
                "currency": "SEK",
                "memo": "Synthetic local validation performance; no write executed",
            },
        ],
    }
    serialized = str(payload)
    assert "/" not in serialized
    assert "private" not in serialized.lower()
    assert "real" not in serialized.lower()


def test_readback_benchmark_request_reuses_existing_synthetic_detail_without_mutation() -> None:
    detail = TransactionDetailDTO(
        id="synthetic-existing-tx",
        date="2026-06-16",
        description="Synthetic benchmark transaction readback fixture",
        currency="SEK",
        splits=[
            TransactionSplitDTO(
                account_id="checking-guid",
                account_name="Synthetic Checking",
                memo="source memo",
                reconcile_state="",
                amount="-10.00",
                currency="SEK",
            ),
            TransactionSplitDTO(
                account_id="expense-guid",
                account_name="Synthetic Expense",
                memo="destination memo",
                reconcile_state="",
                amount="10.00",
                currency="SEK",
            ),
        ],
    )

    request = _build_readback_request_from_detail(detail)

    assert request.date == "2026-06-16"
    assert request.description == "Synthetic benchmark transaction readback fixture"
    assert [split.account_id for split in request.splits] == ["checking-guid", "expense-guid"]
    assert [split.amount for split in request.splits] == ["-10.00", "10.00"]
    assert [split.memo for split in request.splits] == ["source memo", "destination memo"]
    serialized = request.model_dump_json()
    assert "/" not in serialized
    assert "private" not in serialized.lower()


def test_create_large_synthetic_book_uses_only_disposable_data(tmp_path: Path) -> None:
    output = tmp_path / "phase-87-small.gnucash.sqlite"

    metadata = create_large_synthetic_book(
        output,
        transaction_count=24,
        expense_account_count=4,
        account_branch_count=3,
        account_depth=3,
        many_split_count=8,
    )

    assert metadata.path == output
    assert metadata.transaction_count == 24
    assert metadata.expense_account_count == 4
    assert metadata.account_branch_count == 3
    assert metadata.account_depth == 3
    assert metadata.synthetic_account_count == 26
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
        hierarchy_count = conn.execute(
            "select count(*) from accounts where name like 'Synthetic Hierarchy Branch %'"
        ).fetchone()[0]

    assert account_count >= metadata.synthetic_account_count
    assert hierarchy_count == 12
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


def test_create_large_synthetic_book_rejects_invalid_account_hierarchy(tmp_path: Path) -> None:
    output = tmp_path / "invalid-account-hierarchy.gnucash.sqlite"

    try:
        create_large_synthetic_book(
            output,
            transaction_count=10,
            expense_account_count=4,
            account_branch_count=0,
        )
    except ValueError as exc:
        assert "account_branch_count" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("expected ValueError for empty account hierarchy scope")


def test_csv_export_benchmark_summary_records_limit_header() -> None:
    class Response:
        headers = {
            "X-CSV-Export-Limit": "10000",
            "X-CSV-Export-Total": "2",
            "X-CSV-Export-Truncated": "false",
        }
        text = "id,date\ntx-1,2026-05-01\ntx-2,2026-05-02\n"

    item_count, csv_limit, csv_total, csv_truncated = _summarize_response(
        BenchmarkCase("csv_export_up_to_cap", "GET", "/books/{book_id}/transactions/export"),
        Response(),
    )

    assert item_count == 2
    assert csv_limit == 10000
    assert csv_total == 2
    assert csv_truncated is False


def test_account_detail_csv_benchmark_summary_records_limit_header() -> None:
    class Response:
        headers = {
            "X-CSV-Export-Limit": "10000",
            "X-CSV-Export-Total": "2",
            "X-CSV-Export-Truncated": "false",
        }
        text = "id,date\ntx-1,2026-05-01\ntx-2,2026-05-02\n"

    item_count, csv_limit, csv_total, csv_truncated = _summarize_response(
        BenchmarkCase(
            "account_detail_csv_export",
            "GET",
            "/books/{book_id}/transactions/export?account_id={account_id}",
        ),
        Response(),
    )
    result = BenchmarkResult(
        name="account_detail_csv_export",
        method="GET",
        path="/books/1/transactions/export?account_id=checking",
        status_code=200,
        duration_ms_min=1.0,
        duration_ms_median=1.0,
        duration_ms_max=1.0,
        response_bytes=128,
        item_count=item_count,
        csv_limit=csv_limit,
        csv_total=csv_total,
        csv_truncated=csv_truncated,
    )

    assert result.csv_limit == 10000
    assert result.csv_total == 2
    assert result.csv_expected_body_rows == 2
    assert result.csv_body_matches_expected is True


def test_comparison_benchmark_summary_counts_expense_delta_rows() -> None:
    class Response:
        headers = {}

        def json(self):
            return {"expense_changes": [{"account_id": "a"}, {"account_id": "b"}]}

    item_count, csv_limit, csv_total, csv_truncated = _summarize_response(
        BenchmarkCase(
            "period_comparison_previous_equivalent",
            "GET",
            "/books/{book_id}/reports/comparison?date_from=2026-07-02&date_to=2026-12-30"
            "&comparison_mode=previous_equivalent"
            "&comparison_date_from=2026-01-01&comparison_date_to=2026-07-01",
        ),
        Response(),
    )

    assert item_count == 2
    assert csv_limit is None
    assert csv_total is None
    assert csv_truncated is None


def test_benchmark_json_records_csv_body_row_consistency(tmp_path: Path) -> None:
    metadata = FixtureMetadata(
        path=tmp_path / "synthetic.gnucash.sqlite",
        transaction_count=1000,
        expense_account_count=12,
        account_branch_count=8,
        account_depth=4,
        synthetic_account_count=62,
        many_split_count=60,
        synthetic=True,
        contains_real_data=False,
    )
    result = BenchmarkResult(
        name="csv_export_up_to_cap",
        method="GET",
        path="/books/1/transactions/export",
        status_code=200,
        duration_ms_min=1.0,
        duration_ms_median=1.0,
        duration_ms_max=1.0,
        response_bytes=1024,
        item_count=1000,
        csv_limit=10000,
        csv_total=1000,
        csv_truncated=False,
    )

    output = write_results_json(tmp_path / "benchmark.json", metadata, [result])

    content = output.read_text(encoding="utf-8")
    assert '"csv_expected_body_rows": 1000' in content
    assert '"csv_body_matches_expected": true' in content
    assert '"local_synthetic_measurements_only": true' in content
    assert '"non_mutating_read_and_preview_paths_only": true' in content
    assert '"non_mutating_read_preview_validation_readback_paths_only": true' in content
    assert '"read_only_api_paths_only": true' in content
    assert '"includes_write_preview_validation_path": false' in content
    assert '"includes_transaction_validation_service_path": false' in content
    assert '"includes_existing_synthetic_readback_path": false' in content
    assert '"write_alpha_mutation_routes_called": false' in content
    assert '"production_performance_claim": false' in content
