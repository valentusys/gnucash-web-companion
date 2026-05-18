# Phase 106 — read-only transaction state/reconciliation filters

Date: 2026-05-19
Status: complete
Related GitHub issue: #11
PM brief: `docs/handoff/phase-106-pm-brief.md`

## Summary

Phase 106 implemented a narrow read-only transaction filter for confirmed GnuCash split reconciliation state metadata. The new `transaction_state` query parameter supports:

- `unreconciled` → split `reconcile_state = "n"`
- `cleared` → split `reconcile_state = "c"`
- `reconciled` → split `reconcile_state = "y"`
- `voided` → split `reconcile_state = "v"`

The feature is intentionally read-only and describes split reconciliation/cleared state rather than inventing an editable transaction workflow.

## PM decision

Continue GitHub #11 with a practical read-only state/reconciled filtering slice. The phase excluded write-mode, imports, saved filters, browser storage, releases/tags, and private data handling.

## Implementation

Backend:

- Added the centralized `SUPPORTED_TRANSACTION_STATES` mapping in the GnuCash service layer.
- Added `transaction_state` support to transaction listing/counting and account-scoped transaction retrieval.
- Applied state filtering through the same service-layer matcher used by list/count/export paths.
- When an account filter is present, the state match is scoped to the selected account split; without an account filter, a transaction matches if any split has the requested state.
- Added fail-fast API validation so unsupported values return HTTP 400 before opening/querying a book.
- Added CSV export support for the same parameter and validation contract.

Frontend:

- Added a transaction state dropdown to the transaction filters UI.
- Added active-filter summary copy for the selected state.
- Preserved `transaction_state` through transaction filter URL construction and CSV export query-string parity.
- Extended auth-route/static checks to cover the new selector and allowed parameter.

Docs/status:

- Updated `docs/transactions-filters.md` with the new read-only parameter, allowed values, validation behavior, and URL example.
- Updated `PROJECT_STATUS.md` through Phase 106.

## Safety

- `GNUCASH_WRITES_ENABLED=false` default was not changed.
- No write endpoints/services were expanded.
- No tag, release, or package was published.
- No real/private GnuCash books, `.env`, app DBs, backups, screenshots, CSV exports, secrets, tokens, certs, private paths, account names, transaction descriptions, memos, amounts, or personal financial data were committed.
- Money display/calculation behavior was not changed; no float money logic was added.
- GitHub #11 remains open for remaining filter/preset scope.

## Verification

Passed:

```bash
cd apps/api && pytest -q tests/test_transactions.py tests/test_transaction_export.py tests/test_transaction_writes.py
# 84 passed, 7 warnings

cd apps/api && pytest -q
# 338 passed, 27 warnings

cd apps/web && npm run test:auth-routes
# passed

cd apps/web && npm run build
# passed, 0 Svelte errors/warnings

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

git diff --check
# passed
```

## Files changed

- `apps/api/app/services/gnucash_book.py`
- `apps/api/app/routers/transactions.py`
- `apps/api/tests/test_transactions.py`
- `apps/api/tests/test_transaction_export.py`
- `apps/web/src/routes/transactions/+page.server.ts`
- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/transactions-filters.md`
- `docs/handoff/phase-106-pm-brief.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-106.md`

## Commit/push

- Commit: this commit (`Add read-only transaction state filters`); final SHA is recorded in the phase controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.
