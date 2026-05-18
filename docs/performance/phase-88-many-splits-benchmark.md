# Phase 88 — Account with many splits performance test

## Scope

Phase 88 adds a concrete read-only performance scenario for a known GnuCash-web-like risk: accounts and transaction detail pages can become slow when a book contains many transactions and at least one transaction with many splits.

Boundaries:

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
  --many-splits 60 \
  --repeats 3 \
  --json-output /tmp/phase-88-many-splits-benchmark.json
```

The script writes the generated synthetic fixture under the ignored path:

```text
apps/api/tests/generated-fixtures/phase-87-large-book.gnucash.sqlite
```

That directory is ignored by git and is not a durable artifact.

## Scenario covered

The fixture contains:

- 1,000 synthetic transactions;
- 12 synthetic expense accounts;
- one deterministic transaction named `Synthetic benchmark transaction many splits` with 60 splits;
- account-detail transaction pagination coverage through offset 0 and offset 50;
- transaction-detail rendering coverage for the many-splits transaction.

## Benchmark cases

The benchmark creates a temporary in-memory app metadata database, authenticates a local benchmark admin user, registers the generated synthetic book, and measures these read-only API paths through FastAPI `TestClient`:

| Case | Endpoint |
| --- | --- |
| Accounts tree load | `GET /books/{book_id}/accounts/tree` |
| Transactions list first page | `GET /books/{book_id}/transactions?limit=50&offset=0` |
| Transaction filters | `GET /books/{book_id}/transactions?limit=50&offset=0&query=synthetic&date_from=2026-01-01&date_to=2026-12-31` |
| Account detail transactions page 1 | `GET /books/{book_id}/accounts/{account_id}/transactions?limit=50&offset=0` |
| Account detail transactions page 2 | `GET /books/{book_id}/accounts/{account_id}/transactions?limit=50&offset=50` |
| Many-splits transaction detail | `GET /books/{book_id}/transactions/{many_split_transaction_id}` |
| Dashboard summary | `GET /books/{book_id}/reports/summary?as_of_date=2026-12-31` |
| CSV export up to cap | `GET /books/{book_id}/transactions/export` |

## Phase 88 local result

Environment: local development host, FastAPI `TestClient`, generated synthetic SQLite fixture, 1,000 transactions, 12 synthetic expense accounts, one 60-split transaction, 3 repeats per case.

```text
accounts_tree_load: status=200, median=76.09 ms, min=74.99 ms, max=120.76 ms, bytes=6237, items=5
transactions_list_first_page: status=200, median=655.76 ms, min=628.42 ms, max=675.70 ms, bytes=17622, items=50
transaction_filters: status=200, median=670.07 ms, min=653.49 ms, max=681.37 ms, bytes=17628, items=50
account_detail_transactions: status=200, median=1165.91 ms, min=1160.13 ms, max=1167.05 ms, bytes=17602, items=50
account_detail_transactions_page_2: status=200, median=1090.05 ms, min=1089.86 ms, max=1144.77 ms, bytes=17607, items=50
many_splits_transaction_detail: status=200, median=48.23 ms, min=47.94 ms, max=48.42 ms, bytes=9927, items=60
dashboard_summary: status=200, median=96.67 ms, min=95.66 ms, max=142.38 ms, bytes=180
csv_export_up_to_cap: status=200, median=641.58 ms, min=605.63 ms, max=645.81 ms, bytes=118793, items=500, csv_total=1000, truncated=False
```

The raw JSON result was written to `/tmp/phase-88-many-splits-benchmark.json` during this run and was intentionally not committed.

## Findings and limitations

- The many-splits transaction detail path rendered the 60-split synthetic transaction without endpoint failure and without an observed local/TestClient UI-freeze equivalent; median was 48.23 ms.
- Account-detail pagination exists in the benchmark for page 1 and page 2, and both returned 50 items without endpoint failure.
- Account-detail transaction pages remain above one second locally in this synthetic case. This was already visible in Phase 87 and should not be treated as a production scalability claim.
- Existing GitHub #31 is the many-splits benchmark tracker and was closed with this evidence.
- Existing GitHub #39 remains open for the CSV export row-count/header mismatch: CSV body still contains 500 data rows while headers report `csv_total=1000` and `truncated=false`.

## Interpreting the numbers

This is a local synthetic benchmark, not a guarantee of production performance. It is intended to catch regressions and make many-splits/account-detail risk visible before broader optimization work. Use generated data only; do not commit private books or exported private CSV data.
