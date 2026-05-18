# Phase 107 — transaction filter URL presets and clear-all reset UX

Date: 2026-05-19
Status: complete
Related GitHub issue: #11
PM brief: `docs/handoff/phase-107-pm-brief.md`

## Summary

Phase 107 implemented a narrow read-only UX improvement for transaction filters: filter presets and reset behavior remain URL-only, the transaction page has an explicit `Clear filters` link, and route/static checks pin date preset, pagination, and CSV export query-string parity.

## PM decision

Continue GitHub #11 with a practical shareable-URL/reset slice after the Phase 103/104/106 filter work. The phase excluded browser storage, saved private queries, write-mode changes, releases/tags, and private data handling.

## Implementation

Frontend:

- Added a server-built `clearFiltersHref` for the transactions page.
- Replaced the previous client-only reset button with an explicit URL-based `Clear filters` link.
- The clear-all URL keeps only `limit=<current page size>` and `offset=0`, removing `query`, `date_from`, `date_to`, `account_id`, `min_amount`, `max_amount`, and `transaction_state`.
- Preserved the existing date preset behavior and pinned it in tests so presets update only date filters while preserving `query`, `account_id`, `min_amount`, `max_amount`, and `transaction_state`.
- Kept pagination and CSV export URL construction on the same filter contract; CSV export still excludes pagination-only `limit`/`offset`.

Tests/static checks:

- Extended `apps/web/scripts/test-auth-routes.mjs` to assert:
  - date preset URLs preserve all approved non-date filters including `transaction_state`;
  - transaction server load exposes a clear-all URL;
  - the filter form renders an explicit URL-based `Clear filters` link;
  - existing localStorage/sessionStorage restrictions remain enforced.

Docs/status:

- Updated `docs/transactions-filters.md` with URL-only presets/reset behavior and explicit no browser-storage/no saved-query language.
- Updated `PROJECT_STATUS.md` through Phase 107.

## Safety

- `GNUCASH_WRITES_ENABLED=false` default was not changed.
- No backend write endpoints/services were changed.
- No tag, release, or package was published.
- No localStorage/sessionStorage was added for transaction search strings, account IDs, dates, amount ranges, or state filters.
- No real/private GnuCash books, `.env`, app DBs, backups, screenshots, CSV exports, secrets, tokens, certs, private paths, account names, transaction descriptions, memos, amounts, or personal financial data were committed.
- Money logic was not changed; no float money logic was added.
- GitHub #11 was updated with Phase 107 evidence and remains open for remaining read-only search/filter scope.

## Verification

Passed:

```bash
cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run build
# passed

cd apps/api && pytest -q tests/test_transaction_writes.py
# 35 passed, 7 warnings

cd apps/api && pytest -q
# 338 passed, 27 warnings

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

git diff --check
# passed
```

## Files changed

- `apps/web/src/routes/transactions/+page.server.ts`
- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/transactions-filters.md`
- `docs/handoff/phase-107-pm-brief.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-107.md`

## Commit/push

- Commit: this commit (`Add transaction filter clear URL UX`); final SHA is recorded in the phase controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.

## GitHub

- Updated #11: https://github.com/valentusys/gnucash-web-companion/issues/11#issuecomment-4482466467
- Left #11 open for remaining account-detail/filter parity scope.
