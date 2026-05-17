# Phase 30 — Transaction Amount Range Filters for CSV Export

## Status

Complete.

## Goal

Expose read-only transaction amount range filters in the frontend and preserve them in CSV export URLs so GitHub issue #14 is resolved without expanding write capability.

## PM decision

Choose the next release-readiness/read-only MVP backlog item after the Phase 29 audit-driven docs fix: GitHub #14, frontend amount range filters for transaction browsing and CSV export.

Reason: the backend already supported `min_amount` / `max_amount` filtering, but the public UI and export URL did not expose those filters. This is a small read-only release-value improvement and removes a documented limitation from the next pre-alpha candidate.

## Scope

- Add `min_amount` and `max_amount` fields to the transactions filter UI.
- Preserve amount filters in transaction list URLs, pagination, and CSV export URLs.
- Show the active filter count on the export button.
- Add validation for inverted amount ranges.
- Update project/release docs.

## Non-goals

- No write-path expansion.
- No CSV/OFX import.
- No new report/chart features.
- No tag, release, package publication, or real screenshots.
- No real financial data, GnuCash books, app DBs, backups, secrets, tokens, keys, or certs.

## Changes

### Frontend

- `apps/web/src/lib/components/TransactionFilters.svelte`
  - Added `Min amount` and `Max amount` controls.
  - Uses decimal numeric inputs.
  - Rejects client-side inverted ranges before navigation.
  - Reset clears all filters, including amount filters.

- `apps/web/src/routes/transactions/+page.server.ts`
  - Reads `min_amount` and `max_amount` from query parameters.
  - Passes them through to the backend transaction list endpoint.
  - Returns them in page `filters` data.

- `apps/web/src/routes/transactions/+page.svelte`
  - Preserves amount filters in pagination URLs.
  - Preserves amount filters in CSV export URL.
  - Displays active filter count on the `Экспорт CSV` button.

### Backend

- `apps/api/app/routers/transactions.py`
  - Added `_validate_amount_range()`.
  - List/export/account transaction endpoints now reject `min_amount > max_amount` with HTTP 400 before querying GnuCash.
  - No write-path changes.

- `apps/api/tests/test_transaction_export.py`
  - Added test that CSV export respects `account_id + min_amount + max_amount`.
  - Added test that inverted amount ranges are rejected.

### Docs

- `README.md` — current status advanced through Phase 30.
- `CHANGELOG.md` — Phase 30 added; frontend amount-filter limitation removed.
- `docs/ROADMAP.md` — Phase 30 marked complete; #14 removed from next-work list.
- `docs/release/v0.0.2-prealpha-notes.md` — candidate notes updated through Phase 30.
- `PROJECT_STATUS.md` — baseline advanced through Phase 30.

## Safety checks

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Changes are read-only transaction list/export filtering only.
- No GnuCash write routes, write services, locks, backup behavior, or audit-write code changed.
- No real financial data or secrets added.
- No tags/releases/packages published.

## Verification

- Backend targeted: `cd apps/api && pytest -q tests/test_transaction_export.py` — 10 passed.
- Backend full suite: see final Phase 30 report.
- Frontend: see final Phase 30 report.
- Docker config: see final Phase 30 report.

## Commit

Phase commit: `dc436bf`.

## GitHub

- Related issue: #14 CSV export amount range filters in frontend.
- Issue action: close #14 after the Phase 30 commit is pushed.

## Blockers

None.
