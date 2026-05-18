# Phase 89 — Dashboard aggregate performance and correctness pass

## Status

Complete. Phase 89 was executed as a PM→Engineer phase with no analyst/auditor role. No audit-only phase and no `docs/audits/phase-89-audit.md` were created.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data were committed.

## PM report

### Decision

Implement exactly Phase 89: harden dashboard report correctness claims and extend the existing synthetic large-book benchmark so dashboard aggregates are measured beyond the summary endpoint.

### Why

Phase 87/88 made read-only large-book and many-split risks measurable. Phase 89 narrows the next roadmap risk to dashboard aggregates: they must avoid fake FX conversion, stay explicit about base-currency-only reporting, handle empty/error cases conservatively, and avoid unbounded heavy dashboard claims without evidence.

### Phase brief

- Goal: make dashboard reports less likely to be slow or misleading on larger books.
- Non-goals: no real/private book, no committed generated binary fixture, no write-mode work, no v0.2 work, no release/tag, no fake FX conversion, no broad query optimization/refactor, no production scalability claim.
- Acceptance criteria:
  - Dashboard summary exposes conservative base-currency-only limitations.
  - Web dashboard shows the multi-currency/no-conversion limitation.
  - Summary, cashflow, expenses-by-account, and recent-transactions endpoints have regression coverage for conservative behavior/error quality where reasonable.
  - The large-book synthetic benchmark covers all dashboard report endpoints.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are updated.
  - Required checks pass or blockers are explicitly recorded.
  - Commit is pushed to `origin/main` and working tree is clean.
- Safety checks:
  - Synthetic/generated data only.
  - Generated fixture output lives under ignored `apps/api/tests/generated-fixtures/` or `/tmp`.
  - Read-only endpoints only.
  - `GNUCASH_WRITES_ENABLED=false` remains the default.
  - No tag/release publication.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - Local benchmark command and GitHub issue/release/tag verification.

### GitHub/backlog

- GitHub #33 is the dashboard aggregate performance tracking issue and is closed with Phase 89 evidence.
- GitHub #39 remains open for the CSV export row count/header mismatch still observed during the benchmark.
- No release/tag publication.

## Engineer report

### Concrete result

Hardened dashboard reporting and benchmark coverage:

- `apps/api/app/routers/reports.py` now centralizes report date parsing/range validation and returns clear `422` client errors for invalid dashboard report dates.
- `apps/api/app/services/gnucash_book.py` now includes explicit summary metadata: `reporting_basis="base_currency_only"`, `includes_currency_conversion=false`, and a limitation explaining that non-base-currency accounts/splits are excluded without conversion.
- `apps/api/app/schemas/gnucash.py` and `apps/web/src/lib/api/types.ts` now expose the summary limitation metadata explicitly.
- `apps/web/src/routes/dashboard/+page.svelte` displays the summary limitation above dashboard summary cards so mixed-currency/no-conversion constraints are visible in the UI.
- `apps/api/tests/test_reports.py` covers conservative empty-book summary, mixed-currency summary exclusion, mixed-currency cashflow exclusion, and invalid date error quality for dashboard reports.
- `apps/api/app/performance/large_book_benchmark.py` now measures dashboard summary, cashflow-by-month, expenses-by-account, and recent-transactions paths.
- `apps/api/tests/test_large_book_benchmark.py` asserts those dashboard benchmark cases stay in the plan.
- `docs/performance/phase-89-dashboard-aggregate-benchmark.md` records the benchmark command, results, findings, and limitations.

The generated benchmark fixture is not committed. It is written under ignored `apps/api/tests/generated-fixtures/` by default.

### Benchmark evidence

Command:

```bash
python apps/api/scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --many-splits 60 --repeats 3 --json-output /tmp/phase-89-dashboard-benchmark.json
```

Results:

```text
dashboard_summary: status=200, median=103.12 ms, min=102.17 ms, max=148.46 ms, bytes=367
dashboard_cashflow_monthly: status=200, median=566.56 ms, min=537.09 ms, max=582.42 ms, bytes=936, items=12
dashboard_expenses_by_account_month: status=200, median=79.02 ms, min=77.41 ms, max=124.94 ms, bytes=1858, items=12
dashboard_recent_transactions: status=200, median=608.60 ms, min=588.54 ms, max=636.92 ms, bytes=3522, items=10
```

All dashboard aggregate endpoints returned `200` in the 1,000-transaction synthetic benchmark. Cashflow/recent transaction paths remain service-layer scans and are documented as pre-alpha evidence, not a production scalability guarantee.

### Required checks

```text
pytest tests/test_reports.py tests/test_large_book_benchmark.py -q
PASS — 33 passed, 21 warnings

cd apps/api && pytest -q
PASS — 323 passed, 27 warnings

cd apps/api && pytest tests/test_reports.py -q
PASS — 29 passed, 1 warning (rerun after import cleanup)

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

- `apps/api/app/performance/large_book_benchmark.py`
- `apps/api/app/routers/reports.py`
- `apps/api/app/schemas/gnucash.py`
- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_large_book_benchmark.py`
- `apps/api/tests/test_reports.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/routes/dashboard/+page.svelte`
- `docs/performance/phase-89-dashboard-aggregate-benchmark.md`
- `docs/handoff/phase-89.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

### GitHub/release

- GitHub #33 updated/closed with Phase 89 benchmark and correctness evidence.
- GitHub #39 left open because the CSV export row count/header mismatch still reproduces.
- Existing tags verified: `v0.1.0-readonly`, `v0.0.2-prealpha`, `v0.0.1-prealpha`.
- Existing GitHub pre-releases verified; no new tag or release was created.

### Commit/push

To be filled after final verification and push.
