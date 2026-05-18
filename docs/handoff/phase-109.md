# Phase 109 — scheduled/recurring transaction read-only awareness

Date: 2026-05-19
Status: complete
Related GitHub issue: #12
PM brief: `docs/handoff/phase-109-pm-brief.md`

## Summary

Phase 109 implemented the analyst roadmap Phase 4 slice: the app now has honest read-only awareness of GnuCash scheduled/recurring transaction metadata when piecash can expose it safely, without adding a scheduling editor, write-mode behavior, or fake upcoming-run calculations.

## PM decision

Address GitHub #12 as read-only visibility/limitation UX only. The phase was intentionally limited to safe scheduled transaction summary metadata and an explanatory UI page. Creation, editing, deletion, instantiation, template split exposure, raw SQL dumps, and exact next-run prediction were excluded.

## Implementation

Backend:

- Added `ScheduledTransactionDTO` and `ScheduledTransactionRecurrenceDTO` for explicit safe scheduled metadata.
- Added `GnuCashBookService.list_scheduled_transactions()` using piecash `ScheduledTransaction` metadata in read-only book context.
- Exposed only safe summary fields:
  - id
  - name
  - enabled
  - start/end/last-occurred dates
  - configured total/remaining occurrences
  - auto-create/auto-notify flags
  - advance create/notify days
  - instance count
  - template-account presence as a boolean only
  - raw recurrence metadata: period type, multiplier, period start, weekend adjustment
  - conservative limitations text
- Added authenticated endpoints:
  - `GET /scheduled-transactions` for the MVP default-book alias.
  - `GET /books/{book_id}/scheduled-transactions` for book-aware active-book access.
- Preserved existing archived/unauthorized book access boundary by resolving through the same default/book-aware access helpers.

Frontend:

- Added `ScheduledTransaction` TypeScript types.
- Added protected `/scheduled` route, loaded through `getActiveBookContext()` and the book-aware API path for the active accessible book.
- Added desktop/mobile navigation links for `/scheduled`.
- Added UI copy that:
  - this is read-only awareness only;
  - GnuCash Desktop remains the authoritative editor;
  - the app does not create/edit/delete/instantiate schedules;
  - the app does not calculate upcoming schedule predictions;
  - template split details and private raw SQL are not exposed.
- Added empty/limitation state for books with no safe scheduled metadata available.

Docs/status:

- Created `docs/scheduled-transactions.md` with API behavior, safe/unsupported fields, and safety boundaries.
- Created the PM brief at `docs/handoff/phase-109-pm-brief.md`.
- Updated `PROJECT_STATUS.md` through Phase 109 and set Phase 110 as the next roadmap phase.
- Updated `CHANGELOG.md` Unreleased notes.

## Safety

- `GNUCASH_WRITES_ENABLED=false` default was not changed.
- No backend write endpoints/services were changed.
- No scheduled transaction tables are modified.
- No scheduling editor, creation, editing, deletion, instantiation, or import workflow was added.
- No fake next occurrence/upcoming-run calculation was added.
- Template split details, raw SQL, account names, memos, descriptions, amounts, private paths, exports, and real/private financial data are not exposed by the scheduled endpoint/page.
- Frontend still never reads GnuCash files/databases directly.
- No localStorage/sessionStorage was added for scheduled transaction state or auth.
- No tag, release, or package was published.
- No real/private GnuCash books, `.env`, app DBs, backups, screenshots, CSV exports, secrets, tokens, certs, keys, private paths, account names, transaction descriptions, memos, amounts, or personal financial data were committed.
- Money logic was not changed; no float money logic was added.

## Verification

Passed:

```bash
cd apps/api && pytest -q tests/test_scheduled_transactions.py tests/test_transaction_writes.py
# 38 passed, 7 warnings

cd apps/api && pytest -q
# 343 passed, 27 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run build
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

git diff --check
# passed
```

## Files changed

- `apps/api/app/main.py`
- `apps/api/app/routers/books.py`
- `apps/api/app/routers/scheduled_transactions.py`
- `apps/api/app/schemas/gnucash.py`
- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_scheduled_transactions.py`
- `apps/web/src/hooks.server.ts`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/components/DesktopNav.svelte`
- `apps/web/src/lib/components/MobileNav.svelte`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/scheduled/+page.server.ts`
- `apps/web/src/routes/scheduled/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/scheduled-transactions.md`
- `docs/handoff/phase-109-pm-brief.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-109.md`

## GitHub

- Updated #12: https://github.com/valentusys/gnucash-web-companion/issues/12#issuecomment-4482675662
- Left #12 open because richer verified schedule calculations/dashboard widgets remain future scope and must not be faked.

## Commit/push

- Commit: this commit (`Add read-only scheduled transaction awareness`); final SHA is recorded in the phase controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.
