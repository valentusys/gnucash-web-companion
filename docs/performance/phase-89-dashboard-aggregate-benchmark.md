# Phase 89 — Dashboard aggregate benchmark and correctness pass

## Scope

Phase 89 extends the existing synthetic read-only large-book benchmark to cover all dashboard report endpoints that feed the current dashboard experience:

- `GET /books/{book_id}/reports/summary?as_of_date=2026-12-31`
- `GET /books/{book_id}/reports/cashflow?date_from=2026-01-01&date_to=2026-12-31&by_month=true`
- `GET /books/{book_id}/reports/expenses-by-account?date_from=2026-12-01&date_to=2026-12-31`
- `GET /books/{book_id}/reports/recent-transactions?limit=10`

The benchmark uses generated synthetic GnuCash SQLite data only. It does not use, commit, export, screenshot, or disclose any real/private financial data.

## Dashboard safety claims

The dashboard remains conservative:

- no fake currency conversion is performed;
- summary totals report `reporting_basis=base_currency_only`;
- summary totals report `includes_currency_conversion=false`;
- summary responses include a visible limitation message explaining that only base-currency accounts/splits are included and other currencies are excluded without conversion;
- the web dashboard renders the summary limitation above the summary cards;
- invalid report date inputs return a client-safe `422` message naming the invalid field;
- recent transactions remain bounded by the existing `limit` query parameter capped at 50;
- the synthetic benchmark now measures the dashboard aggregate endpoints instead of only the summary endpoint.

## Local benchmark command

```bash
python apps/api/scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --many-splits 60 --repeats 3 --json-output /tmp/phase-89-dashboard-benchmark.json
```

## Benchmark evidence

Fixture:

```text
Synthetic fixture: apps/api/tests/generated-fixtures/phase-87-large-book.gnucash.sqlite
Transactions: 1000
Expense accounts: 12
Many-splits transaction splits: 60
No private book data used; read-only API paths only.
```

Results from the local TestClient run:

```text
accounts_tree_load: status=200, median=73.78 ms, min=73.16 ms, max=121.36 ms, bytes=6237, items=5
transactions_list_first_page: status=200, median=640.24 ms, min=602.50 ms, max=654.50 ms, bytes=17622, items=50
transaction_filters: status=200, median=670.87 ms, min=610.28 ms, max=675.26 ms, bytes=17628, items=50
account_detail_transactions: status=200, median=1173.60 ms, min=1140.70 ms, max=1178.49 ms, bytes=17602, items=50
account_detail_transactions_page_2: status=200, median=1138.14 ms, min=1132.16 ms, max=1166.10 ms, bytes=17607, items=50
many_splits_transaction_detail: status=200, median=51.36 ms, min=49.58 ms, max=51.95 ms, bytes=9927, items=60
dashboard_summary: status=200, median=103.12 ms, min=102.17 ms, max=148.46 ms, bytes=367
dashboard_cashflow_monthly: status=200, median=566.56 ms, min=537.09 ms, max=582.42 ms, bytes=936, items=12
dashboard_expenses_by_account_month: status=200, median=79.02 ms, min=77.41 ms, max=124.94 ms, bytes=1858, items=12
dashboard_recent_transactions: status=200, median=608.60 ms, min=588.54 ms, max=636.92 ms, bytes=3522, items=10
csv_export_up_to_cap: status=200, median=663.45 ms, min=625.37 ms, max=681.01 ms, bytes=118793, items=500, csv_total=1000, truncated=False
```

## Findings and limitations

- All dashboard aggregate endpoints returned `200` in the 1,000-transaction synthetic benchmark.
- Dashboard summary and expenses-by-account were comfortably below one second in this local run.
- Cashflow-by-month and recent-transactions were below one second in this local run but still scan transaction data in the current service layer; this is acceptable for pre-alpha evidence, not a production scalability guarantee.
- Existing account-detail pagination remains above one second locally and remains documented as a performance limitation.
- The existing CSV export row-count/header mismatch remains tracked separately by GitHub #39.

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains the default. Phase 89 did not enable writes, start v0.2 work, publish a tag/release, or commit real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data.
