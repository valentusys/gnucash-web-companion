# Phase 88 — Account with many splits performance test

## Status

Complete. Phase 88 was executed as a PM→Engineer phase with no analyst/auditor role. No audit-only phase and no `docs/audits/phase-88-audit.md` were created.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data were committed.

## PM report

### Decision

Implement exactly Phase 88: extend the existing synthetic read-only benchmark to include many transactions, at least one transaction with many splits, account-detail pagination, and transaction-detail rendering for the many-splits transaction.

### Why

Phase 87 made large-book performance measurable. Phase 88 narrows the next roadmap risk to GnuCash-style many-split transactions and account-detail pagination without using private books, enabling writes, starting v0.2, or publishing another release.

### Phase brief

- Goal: add a repeatable synthetic performance/regression scenario for accounts/transactions with many splits.
- Non-goals: no real/private book, no committed generated binary fixture, no write-mode work, no v0.2 work, no release/tag, no production scalability claim, no broad optimization/refactor.
- Acceptance criteria:
  - Test or benchmark exists for many splits.
  - Account transaction pagination is included.
  - Transaction detail rendering for a many-splits transaction is included.
  - Reasonable synthetic case does not fail or freeze locally.
  - Limitations are documented if performance is not acceptable.
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

- GitHub #31 was the existing many-splits benchmark issue and is closed with Phase 88 evidence.
- GitHub #39 remains open for the CSV export row count/header mismatch still observed during Phase 88.
- No release/tag publication.

## Engineer report

### Concrete result

Extended the existing benchmark and synthetic generator:

- `apps/api/app/performance/large_book_benchmark.py` now creates a deterministic many-splits transaction and measures:
  - account detail page 1;
  - account detail page 2 (`offset=50`);
  - transaction detail for the many-splits transaction.
- `apps/api/scripts/run_large_book_benchmark.py` documents/runs the Phase 87/88 benchmark helper.
- `apps/api/tests/test_large_book_benchmark.py` now asserts the benchmark plan includes account pagination and many-splits transaction detail, verifies the synthetic many-splits transaction exists, and rejects invalid many-splits scope.
- `docs/performance/phase-88-many-splits-benchmark.md` records the Phase 88 command, measured results, findings, and limitations.

The generated benchmark fixture is not committed. It is written under ignored `apps/api/tests/generated-fixtures/` by default.

### Benchmark evidence

Command:

```bash
python apps/api/scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --many-splits 60 --repeats 3 --json-output /tmp/phase-88-many-splits-benchmark.json
```

Results:

```text
accounts_tree_load: status=200, median=76.09 ms, min=74.99 ms, max=120.76 ms, bytes=6237, items=5
transactions_list_first_page: status=200, median=655.76 ms, min=628.42 ms, max=675.70 ms, bytes=17622, items=50
transaction_filters: status=200, median=670.07 ms, min=653.49 ms, max=681.37 ms, bytes=17628, items=50
account_detail_transactions: status=200, median=1165.91 ms, min=1160.13 ms, max=1167.05 ms, bytes=17602, items=50
account_detail_transactions_page_2: status=200, median=1090.05 ms, min=1089.86 ms, max=1144.77 ms, bytes=17607, items=50
many_splits_transaction_detail: status=200, median=48.23 ms, min=47.94 ms, max=48.42 ms, bytes=9927, items=60
dashboard_summary: status=200, median=96.67 ms, min=95.66 ms, max=142.38 ms, bytes=180
csv_export_up_to_cap: status=200, median=641.58 ms, min=605.63 ms, max=645.81 ms, bytes=118793, items=500, csv_total=1000, truncated=False
```

Finding: many-splits transaction detail rendered 60 splits without endpoint failure in the local/TestClient synthetic case. Account-detail pagination remained above one second locally; this is documented as a limitation, not a production scalability claim. GitHub #39 remains open for the pre-existing CSV row count/header mismatch.

### Required checks

```text
cd apps/api && pytest -q
PASS — 316 passed, 27 warnings

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
- `apps/api/scripts/run_large_book_benchmark.py`
- `apps/api/tests/test_large_book_benchmark.py`
- `docs/performance/phase-88-many-splits-benchmark.md`
- `docs/handoff/phase-88.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

### GitHub/release

- GitHub #31 updated/closed with Phase 88 benchmark evidence.
- GitHub #39 left open because the CSV export row count/header mismatch still reproduces.
- No new tag or release was created.

### Commit/push

Phase implementation commit: `11021e2 feat: add many-splits performance benchmark`.

Pushed to `origin/main`: pending until final controller push.
