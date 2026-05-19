# Phase 126 — Read-only polish and issue triage

Date: 2026-05-19
Status: DONE

## Goal

Close or precisely narrow the remaining read-only GitHub #11/#12 scope before later write-alpha phases.

## Scope completed

- GitHub #11 transaction search/filter triage:
  - Broadened the existing read-only `query` matcher from description + split memo to description + transaction notes + split memo when piecash exposes transaction notes.
  - Kept semantics as one case-insensitive substring matcher shared by list/count/account-scoped/export paths.
  - Explicitly de-scoped persistent named/saved filter presets for the pre-alpha read-only line because they would store private search terms/account IDs; current preset/reset behavior remains URL-only/bookmarkable.
  - Updated transaction filter UI placeholder and localization docs to reflect description/notes/split-memo semantics.
- GitHub #12 scheduled/recurring awareness triage:
  - Confirmed the conservative Phase 109 implementation already provides the accepted read-only awareness scope.
  - Closed the issue with remaining next-occurrence/template-split/editor features intentionally out of current read-only scope unless a separate issue/phase authorizes them.
- Updated `CHANGELOG.md`, `PROJECT_STATUS.md`, `docs/transactions-filters.md`, `docs/localization.md`, and this handoff.

## Non-goals / safety boundaries

- No write routes changed.
- No API contract shape changed; the existing `query` parameter was only broadened inside the service-layer matcher.
- No persistent saved filters, browser storage, app metadata storage, or user profile storage for private filter values.
- No real/private GnuCash books, app DBs, backups, CSV exports, media, secrets, tokens, keys, certs, or `.env` files committed.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test` write gate was not weakened.
- No tag, GitHub release, package, upload, or Phase 132 publication action.

## Verification

- `cd apps/api && pytest tests/test_transactions.py -q` — 34 passed, 1 warning.
- `cd apps/api && pytest -q` — 362 passed, 28 warnings.
- `cd apps/web && npm run check` — passed, 0 errors/0 warnings.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.
- Sensitive tracked-file scan (`git ls-files | grep -E '(^|/)(\.env$|secrets?$|credentials?$)|data/books/.*\.(sqlite|sqlite3|gnucash|db)$|data/backups/.'`) — passed/no matches.

## Expected artifacts

- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_transactions.py`
- `apps/web/src/lib/i18n/messages.ts`
- `docs/transactions-filters.md`
- `docs/localization.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-126.md`
- GitHub #11/#12 triage comments/closure
