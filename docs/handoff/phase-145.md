# Phase 145 — Transaction list usability and filter/export confidence

Date: 2026-05-19
Status: DONE

## Goal

Reduce friction in read-only transaction browsing and CSV export confidence after `v0.1.4-readonly`.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-144.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 145 only; no PM/auditor was involved and no later roadmap phase was started.
- Added a localized transaction current-view summary above the transactions table:
  - visible page range for the current read-only page;
  - newest-first transaction-date ordering copy;
  - active-filter/no-filter status;
  - explicit statement that list, pagination, and CSV export use the same URL filters;
  - reminder that CSV export ignores page offset, starts from the first matching row, and is capped at 10,000 rows.
- Kept this as display-only UX: no new browser storage, no new saved searches, no backend API contract change, no CSV body/header behavior change, and no write-mode expansion.
- Extended frontend route/static checks to pin the transaction current-view summary and localized export cap/parity copy.
- Updated `docs/transactions-filters.md`, `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` for Phase 145 state.

## Verification

- `cd apps/web && npm run test:auth-routes` — passed: `auth route checks passed`.
- `cd apps/web && npm run check` — passed: `svelte-check found 0 errors and 0 warnings`.
- `cd apps/api && pytest -q tests/test_transactions.py tests/test_transaction_export.py` — passed: `52 passed, 1 warning`.
- `cd apps/api && pytest -q` — passed: `377 passed, 32 warnings`.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed with no output.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed with the existing synthetic fixture/docs-image allowlist; no new private GnuCash book, app DB, backup, `.env`, token/key/cert, screenshot, export, raw CSV, or private financial artifact was added.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No backend API, service-layer, DTO, schema, CSV export response, or write route changed.
- No write UI, import, saved search persistence, book upload/registry editing, release/tag, package, or production/security claim was added.
- No localStorage/sessionStorage was introduced for transaction filters or sensitive data.
- No raw CSV artifact, real/private transaction description, amount, GnuCash book, app DB, backup, `.env`, screenshot, export, token, key, cert, private path, or real/private financial data was committed.

## Files changed

- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/transactions-filters.md`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-145.md`
