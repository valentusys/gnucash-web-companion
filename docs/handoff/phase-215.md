# Phase 215 handoff — read-only unavailable-book error contract hardening

Date: 2026-05-21

## Summary

Phase 215 hardened unavailable/missing/not-configured book behavior across read-only API route families and the web recovery path.

Read-only data routes now fail before opening GnuCash when an accessible book's configured local storage is missing or not configured. The response is a deterministic, path-safe `503` message. Metadata-only `/books` remains available for recovery diagnostics and does not expose raw `uri_or_path` values.

## Files changed

- `apps/api/app/routers/books.py`
  - Added `require_book_storage_available_for_readonly` and `resolve_readonly_data_book`.
  - Accounts and scheduled route families now require openable storage before service construction.
- `apps/api/app/routers/accounts.py`
  - Default account routes require openable storage before read-only service use.
- `apps/api/app/routers/transactions.py`
  - Transaction/list/detail/export/report-adjacent read-only paths use openable-book resolution.
  - Write-alpha audit summary preserves edit-access checks and then fails safely for unavailable storage.
- `apps/api/app/routers/reports.py`
  - Book-specific report routes use openable-book resolution.
  - Date validation remains independent of storage availability.
- `apps/api/tests/test_multibook_readonly_access.py`
  - Route-family regression coverage for missing/not-configured books returning safe `503` without opening read services or leaking paths.
- `apps/api/tests/test_write_alpha_audit_summary.py`
  - Audit-summary fixtures use an existing temporary synthetic SQLite file for metadata-only success paths.
- `apps/web/src/routes/+error.svelte`
  - `503` errors send operators back to `/books` instead of dashboard.
- `apps/web/src/lib/i18n/messages.ts`
  - Added localized recovery label for reviewing books.
- `apps/web/scripts/test-auth-routes.mjs`
  - Static checks updated for the safe recovery/error behavior.
- `scripts/smoke/read-only-browser-dogfood.py`
  - Added unavailable-book recovery dogfood using server-validated `/books/{bookId}/select` and path-leak/no-data-link assertions.
- `docs/dogfood/phase-215-unavailable-book-recovery-dogfood.md`
  - Records local synthetic dogfood evidence.

## Verification performed

- `cd apps/api && pytest tests/test_transaction_writes.py tests/test_write_alpha_audit_summary.py tests/test_reports.py -q`
- `cd apps/api && pytest tests/test_multibook_readonly_access.py tests/test_write_alpha_audit_summary.py -q`
- `cd apps/api && pytest -q`
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `scripts/smoke/read-only-api-smoke.py` against local Docker/Caddy with the synthetic default book.
- `scripts/smoke/read-only-browser-dogfood.py --viewport-width 320 --viewport-height 720 --unavailable-book-id <synthetic-missing-book>`
- `scripts/smoke/read-only-browser-dogfood.py --viewport-width 1280 --viewport-height 900 --unavailable-book-id <synthetic-missing-book>`
- `git diff --check`
- Sensitive tracked-file hygiene scan.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test` gate was not weakened.
- Missing/not-configured books are not opened by read-only data routes.
- Raw `uri_or_path`, private paths, backup paths, account names, memos, amounts, screenshots, CSV exports, app DBs, backups, `.env`, tokens, keys, and certificates were not committed.
- No book upload/delete/default-changing/registry-edit UI was added.
- No write-enabled mode was run.
- No release/tag/package/image was published.

## Follow-up risks/blockers

None blocking Phase 215.

This is a read-only recovery/error-contract hardening phase only. It does not claim production readiness, security audit completion, broad GnuCash compatibility, or write safety for real/private or only-copy books.
