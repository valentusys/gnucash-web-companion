# Phase 134 — Read-only UX skeleton loading states

Date: 2026-05-19
Status: DONE

## Goal

Improve perceived performance for the main read-only pages by showing skeleton screens while SvelteKit reloads route data, especially after switching active books.

## Scope completed

- Extended `LoadingState.svelte` from a generic spinner into an accessible skeleton component with variants for:
  - `dashboard` — summary cards, recent transactions, expense bars, and cashflow/chart-like placeholders;
  - `accounts` — account-tree header and nested row placeholders;
  - `transactions` — filter controls plus desktop table/mobile card placeholders;
  - `books` — configured-book card/list placeholders.
- Wired `/dashboard`, `/accounts`, `/transactions`, and `/books` to SvelteKit `navigating` state so each page shows its matching skeleton while route data reloads.
- Kept skeleton structure close to the final content layout to reduce perceived layout shift when data arrives.
- Added static frontend route checks for the skeleton variants and page-level navigation-loading wiring.
- Updated `PROJECT_STATUS.md` for Phase 134 completion.

## Non-goals / safety boundaries

- No backend API, schema, route, service, GnuCash adapter, or endpoint changed.
- No real charts were added; dashboard chart areas are placeholders only.
- No write endpoint, write service, write lock, audit, backup, or write-mode gate changed.
- No write-alpha capability was expanded or enabled.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No release/tag/package/publication was performed.
- No real/private GnuCash books, app DBs, backups, `.env`, tokens, keys, screenshots, exports, or private financial data were added or committed.
- Docs remain honest: pre-alpha/test copies/no production guarantee.

## Verification

- RED: `cd apps/web && npm run test:auth-routes` — failed before implementation on missing structured `LoadingState` skeleton variants.
- GREEN: `cd apps/web && npm run test:auth-routes` — passed (`auth route checks passed`).
- `cd apps/web && npm run check` — passed (`0 errors, 0 warnings`).
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.
- Sensitive tracked-file scan — passed; no committed `.env`, app DB, GnuCash book, backup, screenshot/export, key, token, or secret artifact detected in the phase diff.

## Expected artifacts

- `apps/web/src/lib/components/LoadingState.svelte`
- `apps/web/src/routes/dashboard/+page.svelte`
- `apps/web/src/routes/accounts/+page.svelte`
- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-134.md`

## GitHub / release state

- No release/publication gate was executed for this phase.
- No tag or GitHub release was created.
- Push `main` after all verification passes and the single Phase 134 commit is created.
