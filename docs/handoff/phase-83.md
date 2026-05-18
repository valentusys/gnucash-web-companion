# Phase 83 — Frontend Decimal-string Money Display Hardening

## Status

Complete. Phase 83 was a PM→Engineer post-release hardening phase with one concrete tested user-facing/UX safety result. No auditor role was used. No audit-only phase or `docs/audits/phase-83-audit.md` was created.

No new tag/release was published. No scope expansion was made. Writes were not enabled. `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DB, backups, screenshots/exports with real financial data, secrets, tokens, certs, or keys were committed.

## PM report

### Decision

Pick GitHub #34 for Phase 83: a narrow, low-risk, post-release read-only UI hardening task that removes frontend `Number()` usage from money display decisions.

### Why

Phase 80 already published `v0.1.0-readonly`, Phase 81 fixed post-release seed-log redaction, and Phase 82 hardened read-only multi-book boundary tests. Phase 83 therefore should not publish another tag/release, start v0.2 work, or perform audit-only documentation. #34 was open, concrete, testable, and aligned with the project rule that money values stay Decimal/string rather than JS float/Number for amount, balance, total, and net fields.

### Phase brief

- Goal: replace frontend `Number()` money display/range decisions with decimal-string helpers and add lightweight coverage for those helpers.
- Non-goals: no auditor role, no audit-only docs, no write-mode changes, no `GNUCASH_WRITES_ENABLED` enablement, no v0.2 planning, no new release/tag, no product-scope expansion, no currency conversion, no backend Decimal validation replacement.
- Acceptance criteria:
  - Inventory frontend `Number()` usage on amount/balance/total/net display paths.
  - Replace dashboard/card sign color, recent transaction sign color, cashflow net sign color, expenses bar widths, and transaction amount-range prevalidation to avoid converting money strings through `Number()`.
  - Keep remaining frontend `Number()` usage limited to non-money IDs/pagination route parameters.
  - Add a lightweight helper test proving decimal-string comparison, sign checks, and percent width calculations handle precision-sensitive values without JS Number conversion.
  - Update `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff with Phase 83 evidence.
  - Close GitHub #34 only after implementation and checks pass.
- Safety checks:
  - Keep MVP read-only by default.
  - Do not commit real financial data, real GnuCash books, `.env`, app DB, backups, secrets, keys, screenshots/exports with real data.
  - Preserve positioning: GnuCash Desktop remains authoritative; project is not SaaS, not a GnuCash replacement, not collaborative accounting.
- Verification:
  - `cd apps/web && npm run test:money-strings`
  - `cd apps/web && npm run check`
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - verify existing `v0.1.0-readonly` tag/release state with git/gh.

### GitHub/backlog

- Close #34 with implementation/check evidence.
- Leave #22, #26, #28–#33, and #36 open for later narrow phases; do not close issues without evidence.

## Engineer report

### Concrete result

Implemented frontend decimal-string money display hardening for #34:

- Added `apps/web/src/lib/money.js` with decimal-string parsing/comparison helpers based on `BigInt`, not JS `Number()` on money strings.
- Added `apps/web/scripts/test-money-strings.mjs` plus `npm run test:money-strings` for lightweight helper coverage.
- Replaced money-string `Number()` decisions in:
  - `apps/web/src/lib/components/SummaryGrid.svelte` — net-worth trend sign.
  - `apps/web/src/lib/components/RecentTransactions.svelte` — transaction amount color.
  - `apps/web/src/lib/components/CashflowSummary.svelte` — period net color.
  - `apps/web/src/lib/components/ExpensesByAccount.svelte` — expense bar width calculation.
  - `apps/web/src/lib/components/TransactionFilters.svelte` — client-side amount range prevalidation.
- Inventory result after implementation: no `Number()`/`parseFloat`/`parseInt` remains in `.svelte` files; remaining frontend `Number()` usage in `.ts` files is for cookie/book IDs, route params, pagination offsets/limits, not money values.

Backend Decimal validation remains authoritative. The frontend change is display/prevalidation hardening only; it does not add writes, currency conversion, or release/production-readiness claims.

### TDD evidence

RED:

```text
cd apps/web && node scripts/test-money-strings.mjs
Error [ERR_MODULE_NOT_FOUND]: Cannot find module '.../apps/web/src/lib/money.js'
```

GREEN:

```text
cd apps/web && npm run test:money-strings
money string checks passed
```

### Required checks

```text
cd apps/web && npm run test:money-strings
money string checks passed

cd apps/web && npm run check
svelte-check found 0 errors and 0 warnings

cd apps/api && pytest -q
307 passed, 27 warnings

cd apps/web && npm run test:auth-routes
auth route checks passed

cd apps/web && npm run build
built successfully

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
passed

git diff --check
passed
```

Release-state verification:

```text
git tag --list 'v0.1.0-readonly'
v0.1.0-readonly

gh release view v0.1.0-readonly --json tagName,isPrerelease,url,targetCommitish,publishedAt
{"isPrerelease":true,"publishedAt":"2026-05-18T06:04:26Z","tagName":"v0.1.0-readonly","targetCommitish":"main","url":"https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly"}
```

### Files changed

- `apps/web/src/lib/money.js`
- `apps/web/scripts/test-money-strings.mjs`
- `apps/web/package.json`
- `apps/web/src/lib/components/SummaryGrid.svelte`
- `apps/web/src/lib/components/RecentTransactions.svelte`
- `apps/web/src/lib/components/CashflowSummary.svelte`
- `apps/web/src/lib/components/ExpensesByAccount.svelte`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-83.md`

### GitHub/release

- GitHub #34 closed after implementation and passing checks.
- No new release/tag was created.
- Existing `v0.1.0-readonly` GitHub pre-release remains published at https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly

### Commit/push

Phase changes were committed and pushed to `origin/main` after the required checks. The pushed HEAD was verified after push, and the working tree was clean.
