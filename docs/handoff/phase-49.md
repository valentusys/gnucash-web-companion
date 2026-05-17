# Phase 49 — Transaction Search/Filter Hardening

## Status

Complete. Transaction filter validation, CSV parity coverage, frontend URL/range checks, and documentation were updated without expanding write scope. Required checks passed, the phase commit was pushed, and no blockers remain.

## PM report

### Decision

Execute exactly Phase 49 from the roadmap: harden transaction search/filter behavior.

### Why

Phase 48 improved read-only UX copy/states. The next roadmap item is reliability and clarity around the filters users rely on for daily read-only browsing and CSV export: query, date range, amount range, account, pagination, and export parity. This is release-value work and does not require expanding controlled writes.

### Phase brief

- Goal: make transaction search/filter behavior more robust, documented, and aligned between API, frontend list views, pagination, and CSV export.
- Non-goals: no write-scope expansion, no account editing, no import/sync, no release/tag publication, no new GnuCash write behavior.
- Acceptance criteria:
  - Filter behavior is documented.
  - API and frontend are aligned on date/amount range validation.
  - CSV export preserves active list filters and has regression coverage.
  - URL/pagination filter preservation has frontend route-test coverage.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are synchronized.
  - Working tree clean after commit/push.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains the safe/default state.
  - Controlled writes remain experimental post-MVP and disabled by default.
  - No real GnuCash books, `.env`, app DBs, backups, secrets, keys, tokens, real screenshots, or real exports are committed.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

### Risks

- Filter hardening could drift into new feature scope. Mitigation: only validation, tests, and documentation; no new filter types or write behavior.
- Frontend and backend validation could diverge. Mitigation: backend remains authoritative; frontend mirrors inverted date/amount range checks for better UX.
- CSV export could accidentally include pagination parameters. Mitigation: export preserves active filters but intentionally excludes `limit`/`offset` and documents the 10,000 row cap.

### Files/docs to update

- `apps/api/app/routers/transactions.py`
- `apps/api/tests/test_transactions.py`
- `apps/api/tests/test_transaction_export.py`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/transactions-filters.md`
- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-49.md`

### GitHub/backlog

- Phase 49 is related to GitHub #11 (`Transaction search/filter improvements`).
- GitHub #11 was updated with the Phase 49 hardening summary and remains open for broader future enhancements (state filters, saved/date presets, deeper search semantics).
- Next planned phase after completion: Phase 50 — Book switcher stabilization.

## Engineer report

Implemented only Phase 49 work:

- Added shared backend transaction-filter validation for transaction list, account-scoped transaction list, book-scoped transaction list, and CSV export routes.
- Backend now rejects malformed dates, inverted date ranges, and inverted amount ranges before querying GnuCash.
- Added API regression tests for inverted date/amount range list behavior.
- Added CSV export tests for inverted date ranges and combined query/date/account/amount filter parity.
- Added frontend inverted date-range validation with accessible inline error state in `TransactionFilters.svelte`.
- Extended `npm run test:auth-routes` assertions to cover transaction filter URL preservation, CSV export query-string parity, pagination URL behavior, and frontend date/amount range validation checks.
- Added `docs/transactions-filters.md` documenting supported filters, validation, URL/pagination behavior, and CSV export parity.
- Updated `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff.

No write routes were expanded. No release/tag was published.

## Verification

Passed:

- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No account editing, import, sync, banking integration, or collaborative editing was added.
- No auth token localStorage/sessionStorage path was introduced.
- No real financial data, new GnuCash book, `.env`, app DB, backup, secret, key, token, cert, real screenshot, or real CSV export was added.

## Commit / push

- Commit message: `fix: harden transaction filters`.
- Push: pushed to `origin/main`.

## GitHub issue status

- GitHub #11 was updated with the Phase 49 hardening summary.
- GitHub #11 remains open for broader future read-only search/filter enhancements outside this phase.

## Blockers

None.
