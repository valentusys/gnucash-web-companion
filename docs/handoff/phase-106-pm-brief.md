# Phase 106 PM Brief — read-only transaction state filters

Date: 2026-05-19
Role: Project Lead / PM
Status: planned for immediate implementation
Roadmap source: analyst 10-phase plan, Phase 1
Related GitHub issue: #11

## Decision

Plan Phase 106 as a narrow practical read-only continuation of GitHub #11: add transaction filtering by the confirmed GnuCash split reconciliation state exposed by piecash as `Split.reconcile_state`.

## Why

GitHub #11 still has open read-only search/filter scope after Phases 103 and 104. The current code already has one shared service-layer filter contract for list/count/account-list/CSV export. The next useful slice is state filtering, but only if it uses the real GnuCash split field and does not invent transaction-level accounting status.

## Goal

Expose a safe `transaction_state` query parameter for read-only transaction browsing and CSV export, backed by split `reconcile_state` values. The UI should offer only conservative confirmed states and explain that the filter narrows by split reconciliation/cleared state.

## Non-goals

- Do not enable, expand, or modify write-mode behavior.
- Do not import transactions or persist saved filters.
- Do not add localStorage/sessionStorage.
- Do not publish a tag, release, or package.
- Do not claim production readiness or broad compatibility.
- Do not commit real GnuCash books, `.env`, app DBs, backups, screenshots, exports, secrets, or private data.

## Acceptance criteria

- Backend accepts supported `transaction_state` values only: `unreconciled`, `cleared`, `reconciled`, `voided`.
- Unsupported values return a safe HTTP 400 response before querying the book.
- Transaction list, count/pagination totals, account-scoped list, and CSV export all use the same state-filter contract.
- CSV export preserves parity with list filters and reports matching totals.
- Frontend transaction filters include a state dropdown and active-filter summary.
- Export URL, pagination, filter submit/reset, and date presets preserve or clear `transaction_state` predictably with the other filters.
- Existing date/query/account/amount filters continue to work.

## Safety checks

- Keep `GNUCASH_WRITES_ENABLED=false` default untouched.
- Do not change write routes/services except targeted disabled-write regression if needed.
- Money logic must remain Decimal/string; no float money logic.
- No real/private books or exports in git.
- Document the field as split reconciliation state, not an editable transaction workflow.

## Verification

Required:

```bash
cd apps/api && pytest -q tests/test_transactions.py tests/test_transaction_export.py tests/test_transaction_writes.py
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
```

Run broader backend pytest if the targeted set exposes cross-test risk or time permits.

## Files/docs to update

- `apps/api/app/services/gnucash_book.py`
- `apps/api/app/routers/transactions.py`
- `apps/api/tests/test_transactions.py`
- `apps/api/tests/test_transaction_export.py`
- `apps/web/src/routes/transactions/+page.server.ts`
- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/transactions-filters.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-106.md`

## GitHub/backlog

Update GitHub #11 with evidence after push. Leave #11 open unless all listed broader search/filter scope is complete; saved presets and broader notes/full-text semantics remain outside this phase.
