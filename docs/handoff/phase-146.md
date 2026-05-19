# Phase 146 — Transaction detail and split readability polish

Date: 2026-05-19
Status: DONE

## Goal

Improve readability of the current read-only transaction detail page and split rows on mobile and desktop.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-145.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 146 only; no PM/auditor was involved and no later roadmap phase was started.
- Polished `apps/web/src/routes/transactions/[id]/+page.svelte`:
  - transaction detail now has a stable labeled heading and read-only helper copy;
  - date, currency, split count, and short transaction ID are shown in a bounded responsive metadata grid;
  - long descriptions/IDs are wrapped or truncated safely instead of forcing horizontal overflow.
- Polished `apps/web/src/lib/components/TransactionSplits.svelte`:
  - mobile split rows render as readable cards with account, amount, memo, reconciliation state, and short account ID;
  - desktop split rows remain a fixed, bounded table with account, memo, reconciliation state, and amount;
  - zero split rows now show a safe empty state and explicitly do not invent balancing data;
  - no `overflow-x-auto`/`min-w-full` horizontal scrolling was added.
- Added read-only split reconciliation metadata to the existing transaction-detail DTO:
  - `TransactionSplitDTO.reconcile_state` exposes the raw GnuCash split reconciliation state code;
  - frontend maps `n/c/y/v` to Unreconciled/Cleared/Reconciled/Voided display labels;
  - this is display-only metadata and does not create or expand any write route.
- Extended frontend route/static checks to pin transaction-detail readability, split metadata visibility, safe empty state, no horizontal overflow, and hidden-by-default delete/write controls.
- Updated `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` for Phase 146 state.

## Verification

- `cd apps/web && npm run test:auth-routes` — passed: `auth route checks passed`.
- `cd apps/api && pytest -q tests/test_transactions.py::TestGetTransactionMVP::test_returns_transaction_detail` — passed: `1 passed, 1 warning`.
- `cd apps/web && npm run check` — passed: `svelte-check found 0 errors and 0 warnings`.
- `cd apps/api && pytest -q tests/test_transactions.py` — passed: `34 passed, 1 warning`.
- `cd apps/api && pytest -q` — passed: `377 passed, 32 warnings`.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed with no output.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed with the existing synthetic fixture/docs-image allowlist; no new private GnuCash book, app DB, backup, `.env`, token/key/cert, screenshot, export, raw CSV, or private financial artifact was added.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No write endpoint, write-service behavior, delete/create/patch capability, import flow, release/tag/package, browser storage, screenshot, CSV/export artifact, app DB, backup, real/private GnuCash book, `.env`, token, key, cert, private path, or real/private financial data was added.
- Existing transaction delete form remains hidden unless `data.writesEnabled && data.activeBook`; existing acknowledgement and browser confirmation remain pinned by frontend route/static checks.
- The new `reconcile_state` DTO field is read-only split metadata for detail display only.

## Files changed

- `apps/api/app/schemas/gnucash.py`
- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_transactions.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/components/TransactionSplits.svelte`
- `apps/web/src/routes/transactions/[id]/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-146.md`
