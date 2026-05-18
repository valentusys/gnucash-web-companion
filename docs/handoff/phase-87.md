# Phase 87 — Large-book read-only benchmark v1

## Status

Complete. Phase 87 was executed as a PM→Engineer phase with no analyst/auditor role. No audit-only phase and no `docs/audits/phase-87-audit.md` were created.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data were committed.

## PM report

### Decision

Implement exactly Phase 87: create a local large-book benchmark v1 using generated synthetic GnuCash SQLite data and measure only read-only authenticated API paths.

### Why

The project already has a published `v0.1.0-readonly` pre-release and several performance risks were previously tracked from audit-only work. Phase 87 converts part of that uncertainty into repeatable local evidence without using private books, enabling writes, starting v0.2, or publishing a release.

### Phase brief

- Goal: start measuring large-book read-only performance instead of guessing.
- Non-goals: no real/private book, no committed generated binary fixture, no write-mode work, no v0.2 work, no release/tag, no production scalability claim, no broad optimization/refactor.
- Acceptance criteria:
  - Benchmark can be run locally.
  - Benchmark covers accounts tree, transactions first page, transaction filters, account detail transactions, dashboard summary, and CSV export up to cap.
  - Results are documented in `docs/performance/phase-87-large-book-benchmark.md`.
  - Any serious slowdown or correctness finding is filed as a GitHub issue.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are updated.
  - Required checks pass or blockers are explicitly recorded.
  - Commit is pushed to `origin/main` and working tree is clean.
- Safety checks:
  - Synthetic/generated data only.
  - Generated fixture output lives under ignored `apps/api/tests/generated-fixtures/` or `/tmp`.
  - No CSV exports with real data are committed.
  - Read-only endpoints only.
  - `GNUCASH_WRITES_ENABLED=false` remains the default.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - Local benchmark command and GitHub issue/release/tag verification.

### GitHub/backlog

- GitHub #30 is the existing large-book benchmark issue and should be updated/closed with Phase 87 evidence.
- GitHub #39 was created from Phase 87 evidence for the CSV export row count/header mismatch discovered by the benchmark.
- No release/tag publication.

## Engineer report

### Concrete result

Added a repeatable local benchmark and synthetic generator:

- `apps/api/app/performance/large_book_benchmark.py` — creates a deterministic synthetic GnuCash SQLite book and measures the Phase 87 read-only API paths through FastAPI `TestClient`.
- `apps/api/scripts/run_large_book_benchmark.py` — CLI wrapper runnable from the repository root.
- `apps/api/tests/test_large_book_benchmark.py` — regression tests for the benchmark plan and synthetic fixture generator.
- `docs/performance/phase-87-large-book-benchmark.md` — benchmark scope, command, measured results, and findings.

The generated benchmark fixture is not committed. It is written under ignored `apps/api/tests/generated-fixtures/` by default.

### Benchmark evidence

Command:

```bash
python apps/api/scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --repeats 3 --json-output /tmp/phase-87-large-book-benchmark.json
```

Results:

```text
accounts_tree_load: status=200, median=75.62 ms, min=72.43 ms, max=116.00 ms, bytes=6237, items=5
transactions_list_first_page: status=200, median=651.73 ms, min=610.97 ms, max=660.28 ms, bytes=17622, items=50
transaction_filters: status=200, median=624.86 ms, min=622.08 ms, max=662.89 ms, bytes=17628, items=50
account_detail_transactions: status=200, median=1136.67 ms, min=1132.53 ms, max=1170.01 ms, bytes=17602, items=50
dashboard_summary: status=200, median=105.18 ms, min=103.08 ms, max=157.24 ms, bytes=180
csv_export_up_to_cap: status=200, median=659.42 ms, min=622.80 ms, max=688.46 ms, bytes=118793, items=500, csv_total=1000, truncated=False
```

Finding filed: GitHub #39 because CSV export advertises a 10,000-row cap and reports `truncated=false` for 1,000 synthetic transactions, but returns only 500 CSV data rows.

### Required checks

```text
cd apps/api && pytest -q
PASS — 315 passed, 27 warnings

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

The piecash/SQLAlchemy warnings in backend tests are existing expected dependency noise and are not introduced by Phase 87.

### Files changed

- `apps/api/app/performance/__init__.py`
- `apps/api/app/performance/large_book_benchmark.py`
- `apps/api/scripts/run_large_book_benchmark.py`
- `apps/api/tests/test_large_book_benchmark.py`
- `docs/performance/phase-87-large-book-benchmark.md`
- `docs/handoff/phase-87.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

### GitHub/release

- GitHub #30 updated/closed with Phase 87 benchmark evidence.
- GitHub #39 opened for CSV export row count/header mismatch evidence.
- No new tag or release was created.

### Commit/push

Phase commit: pushed HEAD for `feat: add large-book read-only benchmark`.

Pushed to `origin/main`: pending final push at the time of this handoff edit.
