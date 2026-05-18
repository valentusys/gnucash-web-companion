# Phase 108 — account detail transaction filter/export parity

Date: 2026-05-19
Status: complete
Related GitHub issue: #11
PM brief: `docs/handoff/phase-108-pm-brief.md`

## Summary

Phase 108 implemented the analyst roadmap Phase 3 slice: account detail now has the same approved read-only filter/search/export semantics for its own transaction list as the main transactions page, while keeping the account scope fixed and preserving the existing access boundary.

## PM decision

Continue GitHub #11 with a practical account-detail navigation improvement. The phase was intentionally limited to read-only account-scoped transaction filtering/export, excluding write-mode changes, imports, saved/private browser storage, release/tag publication, and any direct frontend access to GnuCash files.

## Implementation

Frontend:

- Extended `TransactionFilters` with a locked account scope mode.
- The locked mode renders the current account as fixed context instead of an account selector, includes the fixed `account_id` as a hidden form value, and explains that other filters narrow only the current account's transactions.
- Updated `/accounts/[id]` server load to accept and forward the approved account-scoped filters:
  - `query`
  - `date_from`
  - `date_to`
  - `min_amount`
  - `max_amount`
  - `transaction_state`
- Added account-scoped date preset URLs and clear-filter URLs that stay on `/accounts/[id]` and reset pagination to `offset=0`.
- Updated account detail pagination to preserve active filters.
- Added account detail CSV export link that calls the existing read-only export proxy with fixed `account_id` plus active search/date/amount/state filters, excluding pagination-only parameters.
- Added filtered count/status copy and an empty-state explanation when active filters hide all transactions for the account.
- Kept transaction table/card selection linking to transaction detail.

Backend/tests:

- The backend route already used the shared account-scoped filter contract.
- Added regression coverage proving combined account-scoped filters keep count/list parity and return only transactions for the requested account.
- Added a no-leakage regression where a query matching another account's transaction returns an empty list when the requested account does not participate.

Docs/status:

- Created the PM brief at `docs/handoff/phase-108-pm-brief.md`.
- Updated `PROJECT_STATUS.md` through Phase 108 and set Phase 109 as the next roadmap phase.

## Safety

- `GNUCASH_WRITES_ENABLED=false` default was not changed.
- No backend write endpoints/services were changed.
- The account detail page still resolves the active book through the authenticated book-aware API context; archived/unauthorized book access remains blocked by existing backend access rules.
- Frontend still never reads GnuCash files/databases directly.
- No localStorage/sessionStorage was added for filters, account IDs, search strings, amounts, dates, or auth.
- No tag, release, or package was published.
- No real/private GnuCash books, `.env`, app DBs, backups, screenshots, CSV exports, secrets, tokens, certs, keys, private paths, account names, transaction descriptions, memos, amounts, or personal financial data were committed.
- Money logic was not changed; no float money logic was added.
- GitHub #11 was updated with Phase 108 evidence and remains open for remaining read-only search/filter scope.

## Verification

Passed:

```bash
cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/api && pytest -q tests/test_transactions.py tests/test_transaction_export.py tests/test_multi_book_access.py tests/test_transaction_writes.py
# 117 passed, 7 warnings

cd apps/api && pytest -q
# 340 passed, 27 warnings

cd apps/web && npm run build
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

git diff --check
# passed
```

## Files changed

- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/src/routes/accounts/[id]/+page.server.ts`
- `apps/web/src/routes/accounts/[id]/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `apps/api/tests/test_transactions.py`
- `docs/handoff/phase-108-pm-brief.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-108.md`

## Commit/push

- Commit: this commit (`Add account detail transaction filter parity`); final SHA is recorded in the phase controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.

## GitHub

- Updated #11: https://github.com/valentusys/gnucash-web-companion/issues/11#issuecomment-4482578896
- Left #11 open for remaining roadmap search/filter scope.
