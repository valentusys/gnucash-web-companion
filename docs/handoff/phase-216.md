# Phase 216 handoff — read-only CSV/export and list parity regression pack

Date: 2026-05-21

## Summary

Phase 216 tightened the regression pack around read-only transaction list/account-detail filters and CSV export parity.

Backend export tests now pin transaction-note query parity with the list view, account-scoped empty exports, header-only CSV behavior, and advisory cap/total/truncation headers. Frontend static route checks now reject browser storage and money-string coercion in the transaction-list/account-detail export/filter UI while preserving URL-only filters, account-scoped export URLs, row-count/truncation copy, and mobile touch targets.

## Files changed

- `apps/api/tests/test_transaction_export.py`
  - Added a fake transaction `notes` field to mirror the transaction list fixture.
  - Added regression coverage for CSV query matches against transaction notes.
  - Added account-scoped empty export coverage that asserts header-only output plus `X-CSV-Export-Total: 0` and `X-CSV-Export-Truncated: false`.
- `apps/web/scripts/test-auth-routes.mjs`
  - Added static guards that transaction-list and account-detail export/filter UI does not use `localStorage`, `sessionStorage`, `Number()`, `parseFloat()`, or `parseInt()` in relevant browser paths.
  - Existing checks continue to pin URL filters, account-scoped CSV URLs, mobile 44px actions, empty/count/truncation copy, and no-currency-conversion wording.
- `docs/dogfood/phase-216-csv-parity-dogfood.md`
  - Records synthetic default-read-only API/browser CSV dogfood evidence without raw CSV artifacts.
- `PROJECT_STATUS.md`
  - Updated current phase status.

## Verification performed

- `cd apps/api && pytest tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_query_filter_matches_transaction_notes_like_list_view tests/test_transaction_export.py::TestExportTransactionsCSV::test_empty_account_scoped_export_is_header_only_and_preserves_metadata -q`
- `cd apps/api && pytest tests/test_transaction_export.py tests/test_transactions.py -q`
- `cd apps/web && npm run test:auth-routes`
- Local Docker/Caddy dogfood with committed synthetic fixture copied into ignored runtime storage and `GNUCASH_WRITES_ENABLED=false`:
  - `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py --api-base-url http://localhost:8080/api`
  - `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --viewport-width 320 --viewport-height 720`
- Full standard verification was run after docs/status updates; see final report for exact pass/fail state.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test` gate was not weakened.
- Amounts remain Decimal/string-style values; the relevant web export/filter paths are statically guarded against browser money coercion.
- Filters remain URL-only; no browser storage is used for financial filters.
- No import, background export queue, cap increase, raw CSV artifact commit, FX conversion, or write behavior was added.
- No real/private books, app DBs, backups, `.env`, screenshots, exports, tokens, keys, certs, private paths, account names, memos, or amounts were committed.

## Follow-up risks/blockers

None blocking Phase 216.

This is a read-only regression/evidence phase only. It does not claim production readiness, security audit completion, broad GnuCash compatibility, or write safety for real/private or only-copy books.
