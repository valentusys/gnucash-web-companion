# Phase 156 — Dashboard drilldown and reporting evidence

Date: 2026-05-19
Status: DONE — read-only dashboard drilldowns added without new accounting/write behavior
Starting HEAD: `616661e`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 5/10 only)

## Goal

Improve read-only usefulness by linking dashboard summary/report cards to the exact existing transaction-filter views that support the same period/account context, while preserving accounting limitations.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-155.md`;
  - roadmap phase 5 and common safety constraints from `cycle-1-roadmap.md`.
- Kept this as Phase 156 only; no neighboring roadmap phases were started.
- Added dashboard server-side drilldown URL construction from existing `/transactions` URL filters:
  - `limit=50` and `offset=0` for every drilldown;
  - current-month `date_from`/`date_to` for income and expense summary cards;
  - `account_id` plus current-month `date_from`/`date_to` for expenses-by-account rows;
  - exact month `date_from`/`date_to` for cashflow periods;
  - unfiltered newest-first `/transactions` link for recent transactions.
- Wired drilldown URLs through dashboard components while relying on the existing active-book context/cookie rather than storing filter state in browser persistence.
- Added conservative copy that dashboard/report totals remain base-currency-only, no FX conversion is included, and drilldown views are supporting read-only transaction evidence rather than invented browser-side recomputations.
- Updated frontend route/static checks to pin URL construction, dashboard component wiring, expense account links, cashflow month links, no-conversion copy, and no invented totals.
- Updated `docs/money-model.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md`.

## Verification

Targeted frontend route/static checks:

```bash
cd apps/web && npm run test:auth-routes
```

Result: passed.

Frontend type/static check:

```bash
cd apps/web && npm run check
```

Result: passed.

Standard checks run for this phase:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'`
- `git diff --check`
- Sensitive tracked-file hygiene scan

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- No new accounting engine, FX conversion, forecasting, write route, production correctness guarantee, release/tag/package, browser filter persistence, localStorage/sessionStorage state, or GnuCash data write was added.
- Drilldowns use only existing read-only `/transactions` filters and preserve active-book context through existing app mechanisms.
- No real/private book, `.env`, app DB, backup, screenshot/export, token, key, cert, private path, account name, description, memo, amount, or private data was committed.

## Files changed

- `apps/web/src/routes/dashboard/+page.server.ts`
- `apps/web/src/routes/dashboard/+page.svelte`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/components/SummaryGrid.svelte`
- `apps/web/src/lib/components/RecentTransactions.svelte`
- `apps/web/src/lib/components/ExpensesByAccount.svelte`
- `apps/web/src/lib/components/CashflowSummary.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/money-model.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-156.md`
