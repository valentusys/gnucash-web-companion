# Phase 118 — Transaction table column width and horizontal scroll fix

Date: 2026-05-19
Status: complete
Previous phase: `docs/handoff/phase-117.md`

## Goal

Fix desktop horizontal shifting and unstable column widths in the transaction table while preserving mobile-friendly card behavior.

## Scope completed

- Stabilized `apps/web/src/lib/components/TransactionTable.svelte` desktop table layout:
  - uses a full-width fixed table instead of `min-w-full` with desktop horizontal scrolling;
  - predictable Date, Description, Account, Counter account, and Amount column widths;
  - long descriptions/account names truncate safely and expose full text through `title` attributes;
  - Amount and Date stay single-line;
  - mobile table remains hidden so the existing mobile card layout continues to handle small screens.
- Checked account tree components for similar narrow desktop overflow behavior and fixed a CSS-only issue:
  - `AccountTree.svelte` header and `AccountTreeNode.svelte` rows now use bounded shrinkable desktop grid columns with `minmax(0,1fr)`;
  - account name/full-name cells keep truncation inside the first column instead of widening the whole row.
- Added static frontend regression coverage in `apps/web/scripts/test-auth-routes.mjs` for:
  - no desktop transaction-table `overflow-x-auto`/`min-w-full` contract;
  - fixed transaction column sizing/truncation classes;
  - account tree shrinkable columns and truncating name cells.

## Non-goals preserved

- No API/data/schema changes.
- No pagination/filter changes.
- No heavy UI library or mobile card redesign.
- No write-mode/default change.
- No release, tag, or package publication.

## Safety

- CSS/UI-only product changes plus static frontend checks.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- Controlled writes remain post-MVP/experimental and disabled by default.
- No real/private GnuCash book, app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private path, account name, transaction description, memo, amount, or personal financial data was added.

## Verification

TDD RED/GREEN evidence:

- RED: `cd apps/web && npm run test:auth-routes` failed before implementation on the new transaction-table fixed/no-scroll assertion.
- GREEN: `cd apps/web && npm run test:auth-routes` passed after implementation.

Final checks run:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
```

Results:

- Backend pytest: passed (`349 passed, 27 warnings`).
- Frontend check: passed, 0 errors, 0 warnings.
- Frontend auth route/static checks: passed.
- Frontend build: passed.
- Docker Compose config validation: passed.
- `git diff --check`: passed.

## Files changed

- `apps/web/src/lib/components/TransactionTable.svelte`
- `apps/web/src/lib/components/AccountTree.svelte`
- `apps/web/src/lib/components/AccountTreeNode.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-118.md`

## Handoff notes

The transaction table desktop layout is intentionally fixed-width and clipped/truncated rather than horizontally scrollable. If future requirements need more visible text on desktop, prefer responsive column ratio adjustments or detail-row affordances rather than reintroducing a global desktop horizontal scroll.
