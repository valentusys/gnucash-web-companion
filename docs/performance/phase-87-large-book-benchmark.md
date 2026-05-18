# Phase 87 — Large-book read-only benchmark v1

## Scope

Phase 87 starts measuring large-book read-only behavior with conservative boundaries:

- synthetic/generated GnuCash SQLite data only;
- no private book, app DB, CSV export, screenshot, `.env`, secret, token, key, cert, backup, or real financial data committed;
- read-only authenticated API paths only;
- no write-mode work and no `GNUCASH_WRITES_ENABLED` change;
- no v0.2 scope and no tag/release publication.

## Local benchmark command

From the repository root:

```bash
python apps/api/scripts/run_large_book_benchmark.py \
  --transactions 1000 \
  --expense-accounts 12 \
  --repeats 3 \
  --json-output /tmp/phase-87-large-book-benchmark.json
```

The script writes the generated synthetic fixture under the ignored path:

```text
apps/api/tests/generated-fixtures/phase-87-large-book.gnucash.sqlite
```

That directory is ignored by git and is not a durable artifact. Delete it after local benchmarking if desired.

## Benchmark cases

The script creates a temporary in-memory app metadata database, authenticates a local benchmark admin user, registers the generated synthetic book, and measures these read-only API paths through FastAPI `TestClient`:

| Case | Endpoint |
| --- | --- |
| Accounts tree load | `GET /books/{book_id}/accounts/tree` |
| Transactions list first page | `GET /books/{book_id}/transactions?limit=50&offset=0` |
| Transaction filters | `GET /books/{book_id}/transactions?limit=50&offset=0&query=synthetic&date_from=2026-01-01&date_to=2026-12-31` |
| Account detail transactions | `GET /books/{book_id}/accounts/{account_id}/transactions?limit=50&offset=0` |
| Dashboard summary | `GET /books/{book_id}/reports/summary?as_of_date=2026-12-31` |
| CSV export up to cap | `GET /books/{book_id}/transactions/export` |

## Phase 87 local result

Environment: local development container/host, FastAPI `TestClient`, generated synthetic SQLite fixture, 1,000 transactions, 12 synthetic expense accounts, 3 repeats per case.

```text
accounts_tree_load: status=200, median=75.62 ms, min=72.43 ms, max=116.00 ms, bytes=6237, items=5
transactions_list_first_page: status=200, median=651.73 ms, min=610.97 ms, max=660.28 ms, bytes=17622, items=50
transaction_filters: status=200, median=624.86 ms, min=622.08 ms, max=662.89 ms, bytes=17628, items=50
account_detail_transactions: status=200, median=1136.67 ms, min=1132.53 ms, max=1170.01 ms, bytes=17602, items=50
dashboard_summary: status=200, median=105.18 ms, min=103.08 ms, max=157.24 ms, bytes=180
csv_export_up_to_cap: status=200, median=659.42 ms, min=622.80 ms, max=688.46 ms, bytes=118793, items=500, csv_total=1000, truncated=False
```

The raw JSON result was written to `/tmp/phase-87-large-book-benchmark.json` during this run and was intentionally not committed.

## Findings

- The benchmark can be run locally and measures the requested read-only paths.
- No private book or real financial data was used or committed.
- No new tag/release was published.
- No write setting was changed; writes remain disabled by default.
- A correctness/performance evidence issue was filed: GitHub #39. The CSV export endpoint advertises a 10,000-row cap and reports `X-CSV-Export-Truncated: false` for a 1,000-transaction synthetic book, but the CSV body contains only 500 data rows. This appears to come from the service-layer list limit clamp and should be fixed in a later narrow maintenance phase with a regression test.

## Interpreting the numbers

This is benchmark v1, not a scalability claim. It is a conservative baseline that makes large-book behavior measurable on synthetic data. The timing values are local-host/TestClient numbers and should not be used as production guarantees.

The 1,000-transaction run did not show a total endpoint failure, but the account-detail transaction path is already above one second locally, and CSV export row count/header consistency needs follow-up in #39 before larger export claims are trusted.
