# Phase 107 PM brief — filter URL presets and reset UX

Date: 2026-05-19
Related GitHub issue: #11

## Decision

Continue GitHub #11 with a narrow read-only UX improvement: make transaction filter URLs more predictable and add an explicit one-click Clear filters action without browser storage or saved private queries.

## Why

Phases 103, 104, and 106 added date presets, split-memo search, and reconciliation-state filtering. The next practical value is to make those filters easier to share, preserve, export, and reset as URL query parameters, while keeping the MVP read-only boundary intact.

## Phase brief

- Goal: improve the transactions filter UX through explicit URL-based presets/reset behavior and CSV query-string parity.
- Non-goals: no localStorage/sessionStorage financial filters, no saved presets, no user-specific stored searches, no backend write changes, no import/export expansion beyond existing read-only CSV export, no tag or release publication.
- Acceptance criteria:
  - A user can clear all active transaction filters in one visible action.
  - Date preset links preserve non-date filters: `query`, `account_id`, `min_amount`, `max_amount`, and `transaction_state`.
  - Pagination preserves active filters and changes only `offset`.
  - CSV export receives the same active filter query string, excluding pagination-only `limit`/`offset`.
  - The UI and docs state that filter state lives in the URL and is not persisted in browser storage.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` default is unchanged.
  - No write endpoints/services are changed.
  - No real books, app DBs, `.env`, secrets, screenshots, CSV exports, backups, certs, or private paths are committed.
  - No localStorage/sessionStorage is added for searches, account IDs, amounts, dates, or state filters.
- Verification:
  - Frontend static/auth-route checks for URL construction, Clear filters, storage restrictions, and CSV parity.
  - Targeted disabled-write backend tests.
  - `npm run check`, `npm run test:auth-routes`, `npm run build`.
  - `cd apps/api && pytest -q tests/test_transaction_writes.py` and backend full suite if practical.
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`.

## Risks

- URL helpers can drift if new filters are added in one path but not another; tests should pin the shared parameter set.
- A reset button implemented only as client state would be less shareable; prefer a normal URL link for clear-all behavior.
- Do not accidentally persist financial filters in browser storage while improving UX.

## Files/docs to update

- `apps/web/src/routes/transactions/+page.server.ts`
- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/transactions-filters.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-107.md`

## GitHub/backlog

- Keep GitHub #11 open unless the remaining read-only filter backlog is fully complete; add evidence only if the phase controller chooses to update GitHub.
