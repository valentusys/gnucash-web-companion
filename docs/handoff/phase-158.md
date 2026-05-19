# Phase 158 — Transaction/account mobile dogfood fix pass

Date: 2026-05-19
Status: DONE — narrow mobile dogfood now pins account/transaction overflow and touch-target behavior on synthetic data
Starting HEAD: `aa34766`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 7/10 only)

## Goal

Use current synthetic browser dogfood to find and fix one concrete mobile/narrow-width read-only UX pain point in account/transaction flows.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-157.md`;
  - roadmap phase 7 and common safety constraints from `cycle-1-roadmap.md`.
- Kept this as Phase 158 only; no neighboring roadmap phases were started.
- Fixed a concrete narrow-width account/transaction UX issue: transaction/account export and transaction empty-state recovery actions now use `inline-flex min-h-11 items-center justify-center`, keeping touch-friendly 44px targets on mobile.
- Extended `scripts/smoke/read-only-browser-dogfood.py` so browser dogfood defaults to a 320x720 mobile viewport and checks:
  - no horizontal overflow on dashboard, accounts, books, scheduled, account detail, transactions, and transaction detail;
  - visible CSV export links are at least 44px tall;
  - transaction detail can be opened through the mobile card path, not only desktop table rows.
- Updated frontend static route checks to pin transaction/account mobile CTA sizing.
- Added dogfood evidence in `docs/dogfood/phase-158-mobile-readonly-dogfood.md`.
- Updated `CHANGELOG.md` and `PROJECT_STATUS.md`.

## Verification

Targeted checks run before handoff:

```bash
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --fixture-path data/books/main.gnucash.sqlite --viewport-width 320 --viewport-height 720
```

Results: passed. Browser dogfood reported `mobile_viewport: 320x720`, no horizontal overflow on covered pages (`scrollWidth=320 clientWidth=320`), CSV export success, hidden write UI, and no screenshots/downloads/CSV files written.

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
- No redesign, heavy UI library, write-mode UI expansion, screenshots, raw CSV exports, real/private book, `.env`, app DB, backup, token, key, cert, private path, or private financial data was committed.
- Browser dogfood used only the committed synthetic fixture copied into ignored runtime data.
- Auth remained httpOnly-cookie based; no localStorage/sessionStorage was added for sensitive state.

## Files changed

- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/routes/accounts/[id]/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `scripts/smoke/read-only-browser-dogfood.py`
- `docs/dogfood/phase-158-mobile-readonly-dogfood.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-158.md`
