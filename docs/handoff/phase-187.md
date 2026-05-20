# Phase 187 — multi-book read-only access regression and UX hardening

Date: 2026-05-20
Status: COMPLETE — read-only multi-book route boundaries hardened after write-alpha work
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 6 only)

## Goal

Return to practical read-only MVP hardening and confirm independent-book access boundaries after write-alpha work, so write-alpha behavior does not blur the default read-only baseline.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-186.md`;
  - roadmap file named by the phase contract;
  - relevant backend book/account/transaction/report routes and frontend book-selection/write-alpha route files.
- Added backend regression coverage in `apps/api/tests/test_multibook_readonly_access.py` for:
  - accessible independent books routing only to the selected book service;
  - archived books hidden/blocked as 404 and unauthorized books blocked as 403;
  - missing-file and not-configured accessible books listed only with redacted storage diagnostics;
  - transaction, account, scheduled-transaction, and report route families blocking archived/unauthorized books before opening a GnuCash service;
  - path-safe service errors for missing/not-configured books;
  - no raw `uri_or_path` values in book metadata responses.
- Hardened API error translation in `apps/api/app/routers/books.py` so `BookNotFoundError`, `BookNotConfiguredError`, and generic `GnuCashReadError` produce stable path-safe 503 details instead of raw service exception text.
- Changed `BookSwitcher.svelte` to use the server-validated safe-link route `/books/{book_id}/select?next=...` instead of setting the `selected_book_id` cookie directly in browser JavaScript.
- Hardened `transactions/new/+page.server.ts` so the write-alpha new-transaction page still redirects under default `GNUCASH_WRITES_ENABLED=false`, and when explicitly enabled resolves accounts through `getActiveBookContext`/`bookPrefix` for the authenticated active book.
- Updated frontend static route checks to pin server-side book selection, no client-side selected-book cookie writes, active-book write-alpha account loading, hidden-by-default write UI, and no localStorage/sessionStorage sensitive state.

## Files changed

- `apps/api/app/routers/books.py`
- `apps/api/tests/test_multibook_readonly_access.py`
- `apps/web/src/lib/components/BookSwitcher.svelte`
- `apps/web/src/routes/transactions/new/+page.server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-187.md`

## Verification summary

Commands/results recorded for this phase:

```bash
cd apps/api && pytest tests/test_multibook_readonly_access.py -q
cd apps/api && pytest tests/test_multi_book_access.py tests/test_multibook_readonly_access.py tests/test_accounts.py tests/test_transactions.py tests/test_reports.py tests/test_transaction_writes.py tests/test_health.py -q
cd apps/api && pytest -q
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
python3 <sensitive tracked-file hygiene scan>
```

Results:

- New multi-book regression tests passed (`40 passed`).
- Targeted backend route/write-gate checks passed (`233 passed`, warnings only from existing piecash/FastAPI dependencies).
- Full backend suite passed (`455 passed`, warnings only from existing piecash/FastAPI dependencies).
- Frontend auth-route/static checks passed.
- Svelte check passed with `0 errors and 0 warnings`.
- Frontend production build passed.
- Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` for API/web entries.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.
- The first attempted backend command referenced a non-existent historical `tests/test_books.py` and failed before collecting tests; it was replaced with the current test filenames above.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No write mode, release, tag, package, upload/delete/default-changing/registry-edit UI, collaborative/family-wallet flow, or frontend direct file access was added.
- Book selection remains a non-secret cookie managed/recovered by server routes; no selected-book/auth state is stored in localStorage/sessionStorage.
- API/UI paths expose only redacted storage diagnostics and stable path-safe error text; raw `uri_or_path` values are not returned.
- No real/private/only-copy book, runtime app DB, runtime book, backup, lock artifact, `.env`, token, key, cert, screenshot, export, raw path, amount, memo, account name, or private financial data was committed.

## Next

Proceed only to the next roadmap phase when explicitly requested. Do not start reporting correctness edge cases, fresh-clone smoke, release-candidate dogfood, or release-readiness work from this phase.
