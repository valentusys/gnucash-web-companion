# Phase 108 PM brief — account detail transaction filter parity

Date: 2026-05-19
Status: planned
Related GitHub issue: #11
Roadmap source: analyst Phase 3 of 10

## Decision

Implement Phase 108 as a narrow read-only account-detail UX parity slice: `/accounts/[id]` should let users filter the account-scoped transaction list with the same approved search/date/amount/state semantics as the main transaction list and export that same account-scoped filtered view.

## Why

The backend account transaction endpoint already shares the same service-layer filter contract as the main transaction list, but the account detail page only exposes pagination. Closing this UI gap improves practical navigation without changing write mode, imports, book management, releases, or private-data handling.

## Phase brief

- Goal: Add account detail transaction filter/search/export parity for account-scoped transactions.
- Non-goals: No write-mode expansion, no transaction editing/import, no saved filters/localStorage/sessionStorage, no release/tag publication, no direct frontend GnuCash file access, no cross-account navigation from the account-detail filter form.
- Acceptance criteria:
  - Account detail accepts and preserves `query`, `date_from`, `date_to`, `min_amount`, `max_amount`, and `transaction_state` filters for its own transactions.
  - Pagination and displayed counts reflect the same account-scoped filtered result set.
  - CSV export from account detail includes the fixed `account_id` plus active filters and excludes pagination-only parameters.
  - Empty state/copy explains that active filters may hide account transactions.
  - Transaction rows/cards still link to transaction detail.
  - Backend account-scoped filter regression coverage proves no cross-account leakage and count/list parity.
- Safety checks:
  - Keep `GNUCASH_WRITES_ENABLED=false` default untouched.
  - Do not change write endpoints/services.
  - Preserve book access boundary through existing authenticated book-aware API context.
  - Do not commit real books, exports, screenshots, app DBs, `.env`, secrets, backups, certs, keys, private paths, account names, memos, amounts, or personal financial data.
  - Keep money as Decimal/string; no float money logic and no fake currency conversion.
- Verification:
  - `cd apps/api && pytest -q tests/test_transactions.py tests/test_transaction_export.py tests/test_multi_book_access.py tests/test_transaction_writes.py`
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

## Risks

- Reusing the general transaction filter component must not let the account-detail page drop its fixed account scope or navigate to another account accidentally.
- CSV export URLs must include the account scope even though the visible page URL should not require an `account_id` query parameter.
- Empty-state wording should remain read-only and avoid implying any write/edit capability.

## Files/docs to update

- `apps/web/src/routes/accounts/[id]/+page.server.ts`
- `apps/web/src/routes/accounts/[id]/+page.svelte`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `apps/api/tests/test_transactions.py`
- `docs/handoff/phase-108.md`
- `PROJECT_STATUS.md`

## GitHub/backlog

- Update GitHub #11 with Phase 108 evidence if `gh` is authenticated.
- Leave #11 open unless the remaining filter/search scope is fully complete.
