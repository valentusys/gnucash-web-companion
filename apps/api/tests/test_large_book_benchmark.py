"""Tests for the Phase 87 large-book read-only benchmark helper."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from app.schemas.gnucash import TransactionDetailDTO, TransactionSplitDTO
from app.services.gnucash_book import GnuCashBookService
from app.performance.large_book_benchmark import (
    BENCHMARK_CASES,
    BenchmarkCase,
    BenchmarkConfig,
    BenchmarkResult,
    EXPLORER_FILTERED_PAGE_SIZE,
    EXPLORER_LATER_PAGE_NUMBER,
    EXPLORER_PAGE_SIZE,
    FixtureMetadata,
    ISSUE55_ACCOUNT_DATASETS,
    ISSUE55_ACCOUNT_QUERY_TEXT,
    ISSUE55_ACTIVITY_ACCOUNT_ID,
    ISSUE56_EXTRA_REGISTERED_BOOKS,
    SPARSE_QUERY_TEXT,
    _build_case_request_json,
    _build_readback_request_from_detail,
    _summarize_response,
    benchmark_plan,
    create_issue55_account_performance_book,
    create_large_synthetic_book,
    issue55_account_benchmark_plan,
    issue56_lifecycle_benchmark_plan,
    run_benchmark,
    run_issue55_account_benchmark,
    run_issue56_lifecycle_benchmark,
    write_results_json,
)


def test_benchmark_plan_covers_phase_87_read_only_scope() -> None:
    plan = benchmark_plan()
    names = [case.name for case in plan]

    assert names == [
        "accounts_tree_load",
        "accounts_explorer_primary",
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
        "period_report_primary",
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


def test_issue55_account_benchmark_plan_is_separate_read_only_scope() -> None:
    one_k = issue55_account_benchmark_plan("1k")
    ten_k = issue55_account_benchmark_plan("10k")

    assert ISSUE55_ACCOUNT_DATASETS == {"1k": (1_000, 1_000), "10k": (10_000, 10_000)}
    assert [case.name for case in one_k] == [
        "issue55_1k_account_unfiltered_tree",
        "issue55_1k_account_text_filtered_tree",
        "issue55_1k_account_flat_search",
        "issue55_1k_account_type_filtered_explorer",
        "issue55_1k_root_overview",
        "issue55_1k_recursive_native_buckets",
        "issue55_1k_direct_period_activity",
        "issue55_1k_account_transaction_explorer_first_page",
    ]
    assert [case.name for case in ten_k] == [
        "issue55_10k_account_filtered_tree",
        "issue55_10k_account_unfiltered_tree_expected_422",
        "issue55_10k_root_overview",
        "issue55_10k_direct_activity",
        "issue55_10k_drilldown_first_page",
    ]
    assert all(case.method == "GET" and case.read_only for case in one_k + ten_k)
    assert next(case for case in ten_k if case.name.endswith("expected_422")).expected_status_code == 422
    assert issue55_account_benchmark_plan("1k", {"issue55_1k_direct_period_activity"}) == [one_k[6]]
    try:
        issue55_account_benchmark_plan("bad-dataset")
    except ValueError as exc:
        assert "unknown issue55 account dataset" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("expected ValueError for unknown issue55 dataset")


def test_issue56_lifecycle_benchmark_plan_covers_preflight_cached_health_and_registration_scale() -> None:
    plan = issue56_lifecycle_benchmark_plan()

    assert [case.name for case in plan] == [
        "issue56_list_registered_books",
        "issue56_preflight",
        "issue56_cached_health",
        "issue56_health_recheck",
        "issue56_first_readonly_open_after_registration",
        "issue56_unavailable_source_cached_health",
        "issue56_multiple_registered_books",
    ]
    assert [case.name for case in issue56_lifecycle_benchmark_plan({"issue56_preflight"})] == [
        "issue56_preflight"
    ]
    preflight = next(case for case in plan if case.name == "issue56_preflight")
    assert preflight.method == "POST"
    assert preflight.path_template == "/books/preflight"
    assert preflight.request_json == "issue56_book_payload"
    assert preflight.read_only is True
    assert next(case for case in plan if case.name == "issue56_health_recheck").method == "POST"
    assert next(case for case in plan if case.name == "issue56_cached_health").method == "GET"


def test_issue56_lifecycle_benchmark_records_bounded_probe_and_app_db_counters(tmp_path: Path) -> None:
    output = tmp_path / "issue56-lifecycle.gnucash.sqlite"
    create_large_synthetic_book(
        output,
        transaction_count=24,
        expense_account_count=4,
        account_branch_count=1,
        account_depth=1,
        many_split_count=8,
    )

    results = run_issue56_lifecycle_benchmark(
        output,
        repeats=1,
        warmups=0,
        case_names={
            "issue56_preflight",
            "issue56_cached_health",
            "issue56_health_recheck",
            "issue56_first_readonly_open_after_registration",
            "issue56_unavailable_source_cached_health",
            "issue56_multiple_registered_books",
        },
    )

    assert [result.name for result in results] == [
        "issue56_preflight",
        "issue56_cached_health",
        "issue56_health_recheck",
        "issue56_first_readonly_open_after_registration",
        "issue56_unavailable_source_cached_health",
        "issue56_multiple_registered_books",
    ]
    for result in results:
        assert result.status_code == 200
        assert result.warmup_count == 0
        assert result.measured_samples == 1
        assert result.app_db_statement_count_min is not None
        assert result.app_db_statement_count_min >= 0
        assert result.app_db_statement_count_max is not None
        assert result.app_db_statement_count_max <= 8
        assert result.full_transaction_materialization_count_max == 0

    preflight = _result_by_name(results, "issue56_preflight")
    assert preflight.preflight_sqlite_query_count_min == 5
    assert preflight.preflight_sqlite_query_count_max == 5
    assert preflight.preflight_piecash_open_count_min == 1
    assert preflight.preflight_piecash_open_count_max == 1
    assert preflight.preflight_account_materialization_count_max == 0
    assert preflight.preflight_transaction_materialization_count_max == 0
    assert preflight.read_only_book_open_count_max == 0

    cached_health = _result_by_name(results, "issue56_cached_health")
    assert cached_health.preflight_sqlite_query_count_max == 0
    assert cached_health.preflight_piecash_open_count_max == 0
    assert cached_health.read_only_book_open_count_max == 0

    recheck = _result_by_name(results, "issue56_health_recheck")
    assert recheck.preflight_sqlite_query_count_max == 5
    assert recheck.preflight_piecash_open_count_max == 1
    assert recheck.read_only_book_open_count_max == 0

    first_open = _result_by_name(results, "issue56_first_readonly_open_after_registration")
    assert first_open.item_count is not None and first_open.item_count > 0
    assert first_open.preflight_sqlite_query_count_max == 0
    assert first_open.preflight_piecash_open_count_max == 0
    assert first_open.read_only_book_open_count_min == 1
    assert first_open.read_only_book_open_count_max == 1
    assert first_open.legacy_count_call_count_max == 0

    missing_health = _result_by_name(results, "issue56_unavailable_source_cached_health")
    assert missing_health.preflight_sqlite_query_count_max == 0
    assert missing_health.preflight_piecash_open_count_max == 0
    assert missing_health.read_only_book_open_count_max == 0

    listed = _result_by_name(results, "issue56_multiple_registered_books")
    assert listed.item_count == ISSUE56_EXTRA_REGISTERED_BOOKS + 2
    assert listed.preflight_sqlite_query_count_max == 0
    assert listed.preflight_piecash_open_count_max == 0
    assert listed.read_only_book_open_count_max == 0


def test_create_issue55_account_performance_book_uses_exact_deterministic_data(tmp_path: Path) -> None:
    output = tmp_path / "issue55-1k.gnucash.sqlite"

    metadata = create_issue55_account_performance_book(
        output,
        candidate_account_count=1_000,
        transaction_count=1_000,
    )

    assert metadata.path == output
    assert metadata.transaction_count == 1_000
    assert metadata.synthetic_account_count == 1_000
    assert metadata.candidate_account_count == 1_000
    assert metadata.hidden_account_count == 450
    assert metadata.placeholder_account_count == 11
    assert metadata.commodity_count == 4
    assert metadata.duplicate_account_name_count == 2
    assert metadata.unicode_account_name_count == 14
    assert metadata.synthetic is True
    assert metadata.contains_real_data is False

    with sqlite3.connect(output) as conn:
        account_count = conn.execute("select count(*) from accounts").fetchone()[0]
        tx_count = conn.execute("select count(*) from transactions").fetchone()[0]
        split_count = conn.execute("select count(*) from splits").fetchone()[0]
        deterministic_accounts = conn.execute(
            "select count(*) from accounts where guid like 'a551%'"
        ).fetchone()[0]
        deterministic_transactions = conn.execute(
            "select count(*) from transactions where guid like '7551%'"
        ).fetchone()[0]
        deterministic_splits = conn.execute("select count(*) from splits where guid like '5551%'").fetchone()[0]
        template_roots = conn.execute("select count(*) from accounts where name = 'Template Root'").fetchone()[0]
        direct_activity_account = conn.execute(
            "select name, account_type, hidden, placeholder from accounts where guid = ?",
            (ISSUE55_ACTIVITY_ACCOUNT_ID,),
        ).fetchone()
        query_accounts = conn.execute(
            "select count(*) from accounts where name like ?",
            (f"%{ISSUE55_ACCOUNT_QUERY_TEXT}%",),
        ).fetchone()[0]
        split_accounts = conn.execute("select count(distinct account_guid) from splits").fetchone()[0]

    assert account_count == 1_000
    assert tx_count == 1_000
    assert split_count == 2_000
    assert deterministic_accounts == 1_000
    assert deterministic_transactions == 1_000
    assert deterministic_splits == 2_000
    assert template_roots == 0
    assert direct_activity_account == ("Bank", "BANK", 0, 0)
    assert query_accounts == 8
    assert split_accounts >= 100


def test_issue55_account_benchmark_records_account_counters_and_drilldown_consistency(tmp_path: Path) -> None:
    output = tmp_path / "issue55-account-counters.gnucash.sqlite"
    create_issue55_account_performance_book(
        output,
        candidate_account_count=1_000,
        transaction_count=1_000,
    )

    results = run_issue55_account_benchmark(
        output,
        dataset="1k",
        repeats=1,
        warmups=0,
        case_names={
            "issue55_1k_account_text_filtered_tree",
            "issue55_1k_direct_period_activity",
            "issue55_1k_account_transaction_explorer_first_page",
        },
    )

    assert [result.name for result in results] == [
        "issue55_1k_account_text_filtered_tree",
        "issue55_1k_direct_period_activity",
        "issue55_1k_account_transaction_explorer_first_page",
    ]
    for result in results:
        assert result.status_code == 200
        assert result.warmup_count == 0
        assert result.measured_samples == 1
        assert result.mutation_capable_request_count == 0
        assert result.read_only_book_open_count_min == 1
        assert result.read_only_book_open_count_max == 1
        assert result.legacy_count_call_count_max == 0
        assert result.full_transaction_materialization_count_max == 0
        assert result.local_timing_budget_dataset == "1k"
        assert result.local_timing_budget_ms == 2_500
        assert isinstance(result.local_timing_budget_passed, bool)

    tree = _result_by_name(results, "issue55_1k_account_text_filtered_tree")
    assert tree.item_count == 14
    assert tree.account_candidate_accounts == 999
    assert tree.account_returned_nodes == 14
    assert tree.actual_query_count == 2
    assert tree.account_split_rows is not None and tree.account_split_rows <= 20_000
    assert tree.account_split_aggregate_rows is not None and tree.account_split_aggregate_rows <= 1_000
    assert tree.account_serialized_bytes is not None and tree.account_serialized_bytes <= 256 * 1024

    activity = _result_by_name(results, "issue55_1k_direct_period_activity")
    assert activity.item_count == 10
    assert activity.activity_recent_item_count == 10
    assert activity.actual_query_count == 5
    assert activity.activity_change_split_rows is not None
    assert activity.activity_recent_split_rows is not None and activity.activity_recent_split_rows <= 40
    assert activity.activity_recent_transaction_objects is not None
    assert activity.activity_recent_transaction_objects <= 20

    drilldown = _result_by_name(results, "issue55_1k_account_transaction_explorer_first_page")
    assert drilldown.item_count == 10
    assert drilldown.returned_count == 10
    assert drilldown.page_size == 10
    assert drilldown.actual_query_count == 2
    assert drilldown.stable_unique_order is True
    assert drilldown.activity_recent_ids_match is True
    assert drilldown.activity_recent_amounts_match is True


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


def test_b1_primary_routes_have_explicit_budgets_and_bounded_read_work(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "b1-primary-routes.gnucash.sqlite"
    metadata = create_large_synthetic_book(
        output,
        transaction_count=2_050,
        expense_account_count=120,
        account_branch_count=20,
        account_depth=2,
        many_split_count=60,
    )
    source_hash_before = hashlib.sha256(output.read_bytes()).hexdigest()

    results = run_benchmark(
        output,
        repeats=1,
        warmups=0,
        case_names={
            "accounts_explorer_primary",
            "transactions_list_first_page",
            "transaction_explorer_first_page",
            "dashboard_summary",
            "dashboard_cashflow_monthly",
            "dashboard_expenses_by_account_month",
            "dashboard_recent_transactions",
            "period_report_primary",
        },
    )

    assert metadata.transaction_count >= 2_000
    assert hashlib.sha256(output.read_bytes()).hexdigest() == source_hash_before
    by_name = {result.name: result for result in results}
    assert set(by_name) == {
        "accounts_explorer_primary",
        "transactions_list_first_page",
        "transaction_explorer_first_page",
        "dashboard_summary",
        "dashboard_cashflow_monthly",
        "dashboard_expenses_by_account_month",
        "dashboard_recent_transactions",
        "period_report_primary",
    }
    for name in {
        "accounts_explorer_primary",
        "transaction_explorer_first_page",
        "dashboard_summary",
        "dashboard_cashflow_monthly",
        "dashboard_expenses_by_account_month",
        "dashboard_recent_transactions",
        "period_report_primary",
    }:
        result = by_name[name]
        assert result.status_code == 200
        assert result.mutation_capable_request_count == 0
        assert result.read_only_book_open_count_max == 1
        assert result.legacy_count_call_count_max == 0
        assert result.local_timing_budget_dataset == "1k"
        assert result.local_timing_budget_ms is not None
        assert result.local_timing_budget_passed is True
        assert result.gnucash_sql_statement_count_max is not None
        assert result.transaction_object_materialization_count_max is not None
        assert result.split_object_materialization_count_max is not None

    account_explorer = by_name["accounts_explorer_primary"]
    assert account_explorer.gnucash_sql_statement_count_max is not None
    assert account_explorer.gnucash_sql_statement_count_max <= 8

    for name in {
        "dashboard_summary",
        "dashboard_cashflow_monthly",
        "dashboard_expenses_by_account_month",
        "period_report_primary",
    }:
        result = by_name[name]
        assert result.gnucash_sql_statement_count_max is not None
        assert result.gnucash_sql_statement_count_max <= 12
        assert result.transaction_object_materialization_count_max is not None
        assert result.transaction_object_materialization_count_max <= metadata.transaction_count

    recent = by_name["dashboard_recent_transactions"]
    assert recent.full_transaction_materialization_count_max == 0
    assert recent.gnucash_sql_statement_count_max is not None
    assert recent.gnucash_sql_statement_count_max <= 8
    assert recent.transaction_object_materialization_count_max is not None
    assert recent.transaction_object_materialization_count_max <= 10

    period_report = by_name["period_report_primary"]
    assert period_report.full_transaction_materialization_count_max is not None
    assert period_report.full_transaction_materialization_count_max <= 1
    assert period_report.report_transaction_visit_count_max is not None
    assert period_report.report_transaction_visit_count_max <= 4 * metadata.transaction_count

    explorer = by_name["transaction_explorer_first_page"]
    assert explorer.local_relative_timing_budget_reference_ms == by_name["transactions_list_first_page"].duration_ms_median
    assert explorer.local_relative_timing_budget_passed is True

    service = GnuCashBookService({"uri_or_path": str(output), "base_currency": "SEK"})
    optimized_recent = [item.model_dump() for item in service.list_transactions(limit=10, offset=0)]
    with monkeypatch.context() as patcher:
        patcher.setattr(GnuCashBookService, "_sql_recent_transactions", lambda *args, **kwargs: None)
        legacy_recent = [item.model_dump() for item in service.list_transactions(limit=10, offset=0)]
    assert optimized_recent == legacy_recent
    assert hashlib.sha256(output.read_bytes()).hexdigest() == source_hash_before


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
