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
    EXPLORER_FILTERED_PAGE_SIZE,
    EXPLORER_LATER_PAGE_NUMBER,
    EXPLORER_PAGE_SIZE,
    FixtureMetadata,
    SPARSE_QUERY_TEXT,
    _build_case_request_json,
    _build_readback_request_from_detail,
    _summarize_response,
    benchmark_plan,
    create_large_synthetic_book,
    run_benchmark,
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
        "transaction_explorer_first_page",
        "transaction_explorer_sparse_scan_limited",
        "transaction_explorer_later_forward_page",
        "transaction_explorer_previous_page",
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
    explorer_first = next(case for case in plan if case.name == "transaction_explorer_first_page")
    assert explorer_first.method == "GET"
    assert "/books/{book_id}/transactions/explorer" in explorer_first.path_template
    assert f"page_size={EXPLORER_PAGE_SIZE}" in explorer_first.path_template
    explorer_filtered = next(case for case in plan if case.name == "transaction_explorer_sparse_scan_limited")
    assert explorer_filtered.method == "GET"
    assert f"page_size={EXPLORER_FILTERED_PAGE_SIZE}" in explorer_filtered.path_template
    explorer_later = next(case for case in plan if case.name == "transaction_explorer_later_forward_page")
    assert "cursor={cursor}" in explorer_later.path_template
    explorer_previous = next(case for case in plan if case.name == "transaction_explorer_previous_page")
    assert "cursor={cursor}" in explorer_previous.path_template
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
            "select guid from transactions where description like 'Synthetic benchmark transaction many splits%'"
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


def test_create_large_synthetic_book_supports_issue54_reproducible_explorer_data(tmp_path: Path) -> None:
    output = tmp_path / "issue54-1k.gnucash.sqlite"

    metadata = create_large_synthetic_book(
        output,
        transaction_count=1_000,
        expense_account_count=4,
        account_branch_count=1,
        account_depth=1,
        many_split_count=8,
    )

    with sqlite3.connect(output) as conn:
        tx_count = conn.execute("select count(*) from transactions").fetchone()[0]
        duplicate_date_buckets = conn.execute(
            "select count(*) from (select post_date from transactions group by post_date having count(*) > 1)"
        ).fetchone()[0]
        deterministic_tx_guids = conn.execute(
            "select count(*) from transactions where guid like '7001%'"
        ).fetchone()[0]
        unicode_descriptions = conn.execute(
            "select count(*) from transactions where description like '%Привет%' or description like '%旅費%'"
        ).fetchone()[0]
        sparse_descriptions = conn.execute(
            "select count(*) from transactions where description like ?",
            (f"%{SPARSE_QUERY_TEXT}%",),
        ).fetchone()[0]
        sparse_memos = conn.execute(
            "select count(*) from splits where memo like ?",
            (f"%{SPARSE_QUERY_TEXT}%",),
        ).fetchone()[0]
        repeated_amount_buckets = conn.execute(
            """
            select count(*)
            from (
                select value_num, value_denom, count(*) as c
                from splits
                group by value_num, value_denom
                having c > 1
            )
            """
        ).fetchone()[0]
        split_account_count = conn.execute("select count(distinct account_guid) from splits").fetchone()[0]

    assert metadata.transaction_count == 1_000
    assert tx_count == 1_000
    assert duplicate_date_buckets > 0
    assert deterministic_tx_guids == 1_000
    assert unicode_descriptions > 0
    assert sparse_descriptions > 0
    assert sparse_memos > 0
    assert repeated_amount_buckets > 0
    assert split_account_count >= 4


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


def _result_by_name(results: list[BenchmarkResult], name: str) -> BenchmarkResult:
    return next(result for result in results if result.name == name)


def test_issue54_explorer_benchmark_records_read_budget_counters(tmp_path: Path) -> None:
    output = tmp_path / "issue54-explorer-pages.gnucash.sqlite"
    create_large_synthetic_book(
        output,
        transaction_count=(EXPLORER_LATER_PAGE_NUMBER * EXPLORER_PAGE_SIZE) + 50,
        expense_account_count=4,
        account_branch_count=1,
        account_depth=1,
        many_split_count=8,
    )

    results = run_benchmark(
        output,
        case_names={
            "transaction_explorer_first_page",
            "transaction_explorer_later_forward_page",
            "transaction_explorer_previous_page",
        },
    )

    assert [result.name for result in results] == [
        "transaction_explorer_first_page",
        "transaction_explorer_later_forward_page",
        "transaction_explorer_previous_page",
    ]
    for result in results:
        assert result.status_code == 200
        assert result.warmup_count == 1
        assert result.measured_samples == 3
        assert result.response_bytes <= 256 * 1024
        assert result.mutation_capable_request_count == 0
        assert result.read_only_book_open_count_min == 1
        assert result.read_only_book_open_count_max == 1
        assert result.legacy_count_call_count_max == 0
        assert result.full_transaction_materialization_count_max == 0
        assert result.page_size == EXPLORER_PAGE_SIZE
        assert result.returned_count is not None and result.returned_count <= result.page_size
        assert result.scan_limits is not None
        assert result.scan_limits["candidate_chunk"] <= 200
        assert result.scan_limits["candidate_rows"] <= 2_000
        assert result.scan_limits["split_rows"] <= 20_000
        assert result.scan_candidate_rows is not None and result.scan_candidate_rows <= 2_000
        assert result.scan_split_rows is not None and result.scan_split_rows <= 20_000
        assert result.scan_query_count is not None and result.scan_query_count <= 23
        assert result.stable_unique_order is True
        if result.next_cursor_length is not None:
            assert result.next_cursor_length <= 1024
        if result.previous_cursor_length is not None:
            assert result.previous_cursor_length <= 1024

    later = _result_by_name(results, "transaction_explorer_later_forward_page")
    previous = _result_by_name(results, "transaction_explorer_previous_page")
    assert "cursor=<redacted>" in later.path
    assert "cursor=<redacted>" in previous.path
    assert previous.cursor_roundtrip_matches is True


def test_issue54_sparse_explorer_benchmark_records_scan_limited_page_and_local_budget(tmp_path: Path) -> None:
    output = tmp_path / "issue54-sparse-scan.gnucash.sqlite"
    create_large_synthetic_book(
        output,
        transaction_count=2_050,
        expense_account_count=4,
        account_branch_count=1,
        account_depth=1,
        many_split_count=8,
    )

    result = run_benchmark(output, case_names={"transaction_explorer_sparse_scan_limited"})[0]

    assert result.status_code == 200
    assert result.warmup_count == 1
    assert result.measured_samples == 3
    assert result.returned_count is not None and result.returned_count <= EXPLORER_FILTERED_PAGE_SIZE
    assert result.scan_limited is True
    assert result.has_more is True
    assert result.scan_candidate_rows == 2_000
    assert result.scan_split_rows is not None and result.scan_split_rows <= 20_000
    assert result.scan_query_count is not None and result.scan_query_count <= 23
    assert result.next_cursor_length is not None and result.next_cursor_length <= 1024
    assert result.response_bytes <= 256 * 1024
    assert result.mutation_capable_request_count == 0
    assert result.read_only_book_open_count_min == 1
    assert result.read_only_book_open_count_max == 1
    assert result.legacy_count_call_count_max == 0
    assert result.full_transaction_materialization_count_max == 0
    assert result.local_timing_budget_dataset == "1k"
    assert result.local_timing_budget_ms == 2_500
    assert isinstance(result.local_timing_budget_passed, bool)


def test_issue54_report_comparison_benchmark_records_one_open_and_visit_bound(tmp_path: Path) -> None:
    output = tmp_path / "issue54-report-comparison.gnucash.sqlite"
    metadata = create_large_synthetic_book(
        output,
        transaction_count=180,
        expense_account_count=4,
        account_branch_count=1,
        account_depth=1,
        many_split_count=8,
    )

    result = run_benchmark(output, case_names={"period_comparison_previous_equivalent"})[0]

    assert result.status_code == 200
    assert result.warmup_count == 1
    assert result.measured_samples == 3
    assert result.response_bytes <= 128 * 1024
    assert result.mutation_capable_request_count == 0
    assert result.read_only_book_open_count_min == 1
    assert result.read_only_book_open_count_max == 1
    assert result.full_transaction_materialization_count_max is not None
    assert result.full_transaction_materialization_count_max <= 1
    assert result.report_transaction_visit_count_max is not None
    assert result.report_transaction_visit_count_max <= 8 * metadata.transaction_count


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
