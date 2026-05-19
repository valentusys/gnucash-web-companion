# Phase 120 — Account detail performance optimization

## Scope

Phase 120 optimizes the read-only account-scoped transaction listing/count path used by account detail pages and account-scoped CSV export.

Boundaries:

- synthetic/generated GnuCash SQLite data only;
- no private book, app DB, CSV export body, screenshot, `.env`, secret, token, key, cert, backup, or real financial data committed;
- read-only authenticated API paths only;
- no cache layer, API contract change, dashboard/global transaction-list optimization, write-mode work, tag, release, or package publication;
- `GNUCASH_WRITES_ENABLED=false` remains the default.

## Code change

Before this phase, `GnuCashBookService.list_transactions(account_id=...)` and `count_transactions(account_id=...)` iterated the full book transaction collection and then filtered each transaction by split account.

Phase 120 adds a scoped candidate path for real piecash books:

- account-scoped list/count uses the piecash SQLAlchemy session to select transactions joined through `splits.account_guid = account_id`;
- split/account relationships are eager-loaded for the selected transaction candidates;
- existing filter semantics remain in the shared service-layer matcher: query, date range, reconciliation state, amount range, pagination, and CSV export all reuse the same account-scoped candidate list;
- unknown `account_id` behavior remains compatible with the existing API: empty list/count rather than 404;
- test doubles that do not model piecash session/relationships keep a compatibility fallback.

## Regression coverage

New/updated tests:

- `tests/test_gnucash_book.py::test_account_scoped_transactions_use_account_splits_without_global_scan`
  - RED evidence: failed before implementation with `GnuCashReadError: account-scoped listing must not scan the whole book` because the test book forbids touching `book.transactions`.
  - GREEN evidence: passes after the scoped candidate path.
  - Covers list, count, pagination ordering, query preservation, and unknown account empty behavior.
- `tests/test_large_book_benchmark.py::test_benchmark_plan_covers_phase_87_read_only_scope`
  - Adds account filtered list and account CSV export benchmark cases.
- `tests/test_large_book_benchmark.py::test_account_detail_csv_benchmark_summary_records_limit_header`
  - Records account-scoped CSV header/body consistency metadata.

Existing endpoint/export tests continue to cover account-scope parity for list/count/CSV filters.

## Local benchmark command

From `apps/api`:

```bash
python -m app.performance.large_book_benchmark \
  --transactions 1000 \
  --repeats 3 \
  --json-output tests/generated-fixtures/phase-120-account-detail-benchmark.json
```

The generated fixture and JSON output are under `apps/api/tests/generated-fixtures/`, which is ignored by git. They are not committed.

## Phase 120 local result

Environment: local development host, FastAPI `TestClient`, generated synthetic SQLite fixture, 1,000 transactions, 12 synthetic expense accounts, one 60-split transaction, 3 repeats per case.

```text
accounts_tree_load: status=200, median=78.34 ms, min=78.25 ms, max=124.31 ms, bytes=5951, items=5
transactions_list_first_page: status=200, median=705.10 ms, min=640.24 ms, max=715.63 ms, bytes=16322, items=50
transaction_filters: status=200, median=639.85 ms, min=636.79 ms, max=701.43 ms, bytes=16328, items=50
account_detail_transactions: status=200, median=296.83 ms, min=292.64 ms, max=299.53 ms, bytes=16302, items=50
account_detail_transactions_page_2: status=200, median=291.64 ms, min=284.59 ms, max=295.58 ms, bytes=16307, items=50
account_detail_transactions_filtered: status=200, median=295.75 ms, min=279.91 ms, max=309.26 ms, bytes=16302, items=50
account_detail_csv_export: status=200, median=294.34 ms, min=290.49 ms, max=298.72 ms, bytes=202781, items=961, csv_limit=10000, csv_total=961, truncated=False, expected_body_rows=961, body_matches_expected=True
many_splits_transaction_detail: status=200, median=48.58 ms, min=47.52 ms, max=48.68 ms, bytes=9147, items=60
dashboard_summary: status=200, median=99.80 ms, min=96.73 ms, max=143.56 ms, bytes=367
dashboard_cashflow_monthly: status=200, median=525.01 ms, min=523.13 ms, max=569.03 ms, bytes=936, items=12
dashboard_expenses_by_account_month: status=200, median=77.86 ms, min=76.99 ms, max=77.89 ms, bytes=1702, items=12
dashboard_recent_transactions: status=200, median=617.47 ms, min=574.20 ms, max=627.32 ms, bytes=3262, items=10
csv_export_up_to_cap: status=200, median=661.02 ms, min=617.29 ms, max=689.84 ms, bytes=211400, items=1000, csv_limit=10000, csv_total=1000, truncated=False, expected_body_rows=1000, body_matches_expected=True
```

## Before/after evidence

Historical synthetic evidence from `docs/performance/phase-88-many-splits-benchmark.md` on the same 1,000-transaction benchmark shape recorded:

- `account_detail_transactions`: median `1165.91 ms`;
- `account_detail_transactions_page_2`: median `1090.05 ms`.

Phase 120 local run after the scoped SQLAlchemy candidate path recorded:

- `account_detail_transactions`: median `296.83 ms`;
- `account_detail_transactions_page_2`: median `291.64 ms`;
- new `account_detail_transactions_filtered`: median `295.75 ms`;
- new `account_detail_csv_export`: median `294.34 ms`, `csv_total=961`, `body_matches_expected=True`.

This is bounded local synthetic evidence only. It is not a production scalability claim.

## Findings and limitations

- Account-scoped list/count/export now avoids unnecessary full-book transaction iteration for real piecash books when `account_id` is present.
- The global transactions list, dashboard recent-transactions, dashboard cashflow, and global CSV export are intentionally not optimized in this phase.
- The benchmark still runs in-process with `TestClient`; network, browser rendering, reverse proxy, and real-book variability are not measured.
- No endpoint failure was observed on the 1,000-transaction synthetic account-detail/list/filter/CSV paths.
