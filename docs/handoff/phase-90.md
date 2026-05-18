# Phase 90 — Transaction search/filter UX improvement

## Status

Complete. Phase 90 was executed as a PM→Engineer phase with no analyst/auditor role. No audit-only phase and no `docs/audits/phase-90-audit.md` were created.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data were committed.

## PM report

### Decision

Implement exactly Phase 90 by selecting one narrow UX improvement from the existing transaction search/filter backlog: a better active filter summary in the transaction filter panel.

### Why

A reset button and date/amount validation already existed, and CSV export filter parity was already covered. The least risky user-facing improvement is to make current filter state explicit so users can understand which filters affect the list and CSV export without changing backend behavior or expanding search semantics.

### Phase brief

- Goal: improve practical usability of the read-only transaction list by making active filters understandable.
- Non-goals: no backend search/filter semantics, no new filters, no saved presets, no detail/back navigation redesign, no write-mode work, no v0.2 work, no release/tag publication, no real/private data artifacts.
- Acceptance criteria:
  - The transaction filter UI shows a readable summary for active search, account, date, and amount filters.
  - The summary explicitly says active filters apply to both the read-only list and CSV export.
  - CSV export query-string parity remains intact.
  - No backend write changes are made.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are updated.
  - Required checks pass or blockers are explicitly recorded.
  - Commit is pushed to `origin/main` and working tree is clean.
- Safety checks:
  - Frontend-only UX change.
  - Read-only transaction browsing/export copy only.
  - `GNUCASH_WRITES_ENABLED=false` remains the default.
  - No tag/release publication.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - GitHub issue/release/tag verification.

### GitHub/backlog

- GitHub #11 is the transaction search/filter improvements backlog issue and was updated with Phase 90 evidence.
- #11 remains open because broader future read-only enhancements (state filters, saved presets, date presets, broader search semantics) are still not implemented.
- No release/tag publication.

## Engineer report

### Concrete result

Implemented a focused transaction filter UX improvement:

- `apps/web/src/lib/components/TransactionFilters.svelte` now builds an `activeFilterSummary` for the current search text, selected account, date range, and amount range.
- The filter panel renders accessible summary chips under the filter heading when any filters are active.
- The summary copy says: `Active filters applied to list and CSV export`, preserving user understanding that CSV export uses the same filter state.
- Existing reset behavior, date validation, amount validation, URL filter preservation, and CSV export query construction were left intact.
- `apps/web/scripts/test-auth-routes.mjs` now checks that the active filter summary exists and that the summary ties active filters to both the list and CSV export.

### Required checks

```text
cd apps/api && pytest -q
PASS — 323 passed, 27 warnings

cd apps/web && npm run check
PASS — svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
PASS — auth route checks passed

cd apps/web && npm run build
PASS — production build completed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
PASS

git diff --check
PASS
```

### Files changed

- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/handoff/phase-90.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

### GitHub/release

- GitHub #11 updated with Phase 90 evidence and kept open for future broader read-only search/filter improvements: https://github.com/valentusys/gnucash-web-companion/issues/11#issuecomment-4476492874
- Existing tags/releases verified: `v0.1.0-readonly`, `v0.0.2-prealpha`, `v0.0.1-prealpha`.
- No new tag or GitHub release was created.

### Commit/push

Phase implementation commit: `a943720 feat: summarize active transaction filters`.

Push evidence: `git push origin main` succeeded and remote `origin/main` advanced from `81bef46` to `a943720`.
