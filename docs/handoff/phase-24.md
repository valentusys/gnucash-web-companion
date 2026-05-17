# Phase 24 — CSV Export for Transactions

## Summary

Added read-only CSV export for transactions: backend endpoint + frontend button.

## Changes

### Backend

**`apps/api/app/routers/transactions.py`**
- Added `GET /books/{book_id}/transactions/export` endpoint
- Read-only, book-aware, requires auth + book view access
- Supports all list filters: `account_id`, `date_from`, `date_to`, `query`, `min_amount`, `max_amount`
- Row cap at 10,000 (`CSV_EXPORT_LIMIT`)
- Returns `StreamingResponse` with `text/csv` media type and `Content-Disposition: attachment; filename="transactions-book{id}.csv"`
- CSV columns: `id`, `date`, `description`, `amount`, `currency`, `account_id`, `account_name`, `counter_account_name`
- Endpoint placed *before* `{transaction_id}` route to avoid path collision (`/export` would match as `transaction_id="export"`)
- Added imports: `csv`, `io`, `StreamingResponse`

**`apps/api/tests/test_transaction_export.py`** (new)
- 8 tests in `TestExportTransactionsCSV` class:
  1. `test_requires_auth` — 401 without auth
  2. `test_returns_csv_with_correct_headers` — 200, text/csv, correct header row
  3. `test_csv_contains_all_transactions` — header + 3 data rows
  4. `test_export_respects_date_filter` — date_from/date_to filtering
  5. `test_export_respects_account_filter` — account_id filtering
  6. `test_export_respects_query_filter` — query text filtering
  7. `test_export_access_denied` — 403 for viewer without book access
  8. `test_export_content_disposition_filename` — correct filename in Content-Disposition

### Frontend

**`apps/web/src/routes/transactions/+page.svelte`**
- Added `exportCsvUrl` derived computation preserving current filters (query, date_from, date_to, account_id)
- Added «Экспорт CSV» button next to "New transaction" button
- Button only shown when `data.activeBook` is set
- Button links to `/books/{bookId}/transactions/export?{filters}`

## Test Results

- Backend: 262 passed (254 existing + 8 new), 0 failed
- Frontend: `npm run check` — 0 errors, `npm run test:auth-routes` — passed, `npm run build` — success
- Docker config: valid

## Safety

- Read-only only — no write-path changes
- No new dependencies (uses stdlib `csv` + `io`)
- Auth + book view access required
- Row cap prevents memory issues
- Zero production data involved

## Known Limitations

- Export is book-aware only (no MVP alias `/transactions/export`)
- No amount range filtering in frontend export URL (backend supports it but frontend doesn't expose amount filters)
- Pyright false positive: `"items" is possibly unbound` — safe because `handle_gnucash_error` always raises
