# Phase 95 — CSV export row-count/header mismatch fix

## Status

Complete. Phase 95 implemented the PM brief from `docs/handoff/phase-95-pm-brief.md` and fixed GitHub #39.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or real CSV exports were committed.

## PM brief followed

Goal: make CSV export body row count and CSV metadata headers internally consistent above the normal transaction-list pagination/service clamp and up to the documented 10,000-row CSV cap.

Non-goals preserved:

- no write-mode expansion;
- no import/OFX/CSV ingestion;
- no async/background export infrastructure;
- no new export format;
- no real/private data artifacts;
- no tag/release and no `v0.1.1-readonly` release notes/checklist in this phase.

## Root cause

`GET /books/{book_id}/transactions/export` correctly computed `X-CSV-Export-Total` and `X-CSV-Export-Truncated` against the full matching transaction count and used `CSV_EXPORT_LIMIT = 10000` for headers.

However, it fetched rows via `GnuCashBookService.list_transactions(limit=capped, offset=0)`, and `list_transactions()` had an internal historical clamp of `min(limit, 500)`. That clamp was useful as a service-level safety default for list-style callers, but it silently capped CSV export bodies at 500 rows while the export route reported the 10,000 CSV cap and `truncated=false` for totals below 10,000.

## Implementation

Changed:

- `apps/api/app/services/gnucash_book.py`
  - added `max_limit: int = 500` to `GnuCashBookService.list_transactions()`;
  - kept the default 500 service clamp for existing/list-style callers.
- `apps/api/app/routers/transactions.py`
  - CSV export now passes `max_limit=CSV_EXPORT_LIMIT`, so export can return up to the documented 10,000-row cap.
- `apps/api/tests/test_transaction_export.py`
  - added a regression test with 501 synthetic/fake transactions proving body rows and headers are consistent above the old 500-row clamp.
- `apps/api/app/performance/large_book_benchmark.py`
  - benchmark output/JSON now records `csv_limit` from `X-CSV-Export-Limit` for targeted evidence.
- `apps/api/tests/test_large_book_benchmark.py`
  - added coverage that benchmark CSV summary captures the limit header.
- `PROJECT_STATUS.md` and `CHANGELOG.md`
  - updated Phase 95 status/evidence.

Frontend proxy note:

- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts` already forwarded `x-csv-export-limit`, `x-csv-export-total`, `x-csv-export-truncated`, and `x-csv-export-timeout-policy` unchanged.
- No proxy code change was needed; `npm run test:auth-routes` still verifies header forwarding.

## TDD evidence

RED:

```text
cd apps/api && pytest tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_above_service_page_clamp_returns_all_rows_and_consistent_headers -q
FAIL — expected header + 501 rows, got header + 500 rows
```

GREEN:

```text
cd apps/api && pytest tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_above_service_page_clamp_returns_all_rows_and_consistent_headers -q
PASS — 1 passed, 1 warning
```

Benchmark header recording RED/GREEN:

```text
cd apps/api && pytest tests/test_large_book_benchmark.py::test_csv_export_benchmark_summary_records_limit_header -q
RED first — expected 4 returned values including csv_limit, old helper returned 3
GREEN after update — 1 passed, 1 warning
```

## CSV export evidence

Regression test synthetic/fake export:

```text
body data rows: 501
X-CSV-Export-Limit: 10000
X-CSV-Export-Total: 501
X-CSV-Export-Truncated: false
body rows match expected total/cap: yes
```

Targeted synthetic benchmark command used:

```bash
cd apps/api
python scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --repeats 1 --json-output /tmp/phase-95-csv-export-check.json
```

Benchmark CSV result:

```text
csv_export_up_to_cap: status=200
body data rows/items: 1000
csv_limit / X-CSV-Export-Limit: 10000
csv_total / X-CSV-Export-Total: 1000
truncated / X-CSV-Export-Truncated: False
body rows match expected total/cap: yes
JSON evidence: /tmp/phase-95-csv-export-check.json (outside git)
```

The benchmark uses generated synthetic data only. The generated fixture path is under `apps/api/tests/generated-fixtures/phase-87-large-book.gnucash.sqlite` and remains ignored/uncommitted.

## Required checks

```text
cd apps/api && pytest -q
PASS — 328 passed, 27 warnings

cd apps/web && npm run check
PASS — svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
PASS — auth route checks passed

cd apps/web && npm run build
PASS — production build completed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
PASS

git diff --check
PASS
```

Warnings observed are existing piecash/SQLAlchemy/FastAPI deprecation warnings; no new failure was introduced.

## GitHub / backlog

- GitHub #39 was updated with Phase 95 evidence and closed after regression + targeted benchmark verification.
- GitHub #38 remains open and out of scope: copied personal-book dogfood rerun still requires a safe copied SQL book outside git.
- No new issue was created.

## Risks / follow-up

- CSV export remains synchronous and capped at 10,000 rows; this phase fixed row/header correctness, not large async export architecture.
- Normal list endpoints remain paginated and capped by route/service defaults; this phase intentionally did not expand UI list pagination.
- Next PM phase should choose the next release-value step from the analyst roadmap, likely Phase 96 synthetic large-export benchmark/UX confirmation or subsequent `v0.1.1-readonly` release-prep work after #39 closure is verified.

## Commit / push

Commit: phase changes are committed in git; final pushed HEAD is reported in Telegram/stdout.

Push: pending until final push verification.
