# Phase 165 — Large account tree usability and benchmark

Date: 2026-05-20
Status: DONE
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 4/10 only)

## Goal

Improve read-only account-tree usability/performance evidence for large synthetic account hierarchies without inventing accounting semantics.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-164.md`;
  - roadmap phase 4 and safety constraints from `cycle-2-roadmap.md`.
- Kept this as Phase 165 only; no neighboring roadmap phases were started.
- Extended `apps/api/app/performance/large_book_benchmark.py`:
  - generated synthetic wide/deep account hierarchy branches;
  - added `account_branch_count`, `account_depth`, and `synthetic_account_count` benchmark metadata;
  - added CLI flags `--account-branches` and `--account-depth`;
  - added account-tree large-hierarchy benchmark case.
- Updated `apps/api/tests/test_large_book_benchmark.py`:
  - pins the new benchmark plan case;
  - proves synthetic hierarchy generation and metadata;
  - rejects invalid hierarchy scope.
- Fixed one concrete UI issue exposed by large/deep hierarchy scope:
  - `AccountTreeNode.svelte` caps visual indentation at depth 8;
  - full account path remains available as hover/title text;
  - row/grid truncation behavior remains bounded.
- Updated frontend static checks to pin the indentation cap/no-overflow account-tree contract.
- Added benchmark evidence in `docs/performance/phase-165-large-account-tree-benchmark.md`.
- Synchronized `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff.

## Benchmark evidence

Command run from `apps/api`:

```bash
python -m app.performance.large_book_benchmark \
  --transactions 1000 \
  --expense-accounts 24 \
  --account-branches 16 \
  --account-depth 6 \
  --repeats 3 \
  --json-output /tmp/phase-165-large-account-tree-benchmark.json
```

Result summary:

- Synthetic fixture only; no private data.
- 1,000 synthetic transactions.
- 24 synthetic expense accounts.
- 16 synthetic hierarchy branches.
- 6 nested synthetic levels per branch.
- 146 synthetic non-root benchmark accounts.
- `accounts_tree_load`: HTTP 200, median 185.88 ms.
- `accounts_tree_large_hierarchy_filter_seed`: HTTP 200, median 198.76 ms.
- CSV consistency remained intact for both global and account-scoped export cases.

Raw benchmark JSON was written to `/tmp/phase-165-large-account-tree-benchmark.json` and intentionally not committed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No production writes were enabled.
- No cache layer, account editing, production scalability claim, release/tag/package, or write-alpha expansion was added.
- Synthetic account names only.
- No real/private GnuCash book, app DB, backup, `.env`, screenshot/export, token, key, cert, private path, account name, transaction description, memo, amount, or private financial data was committed.

## Verification

```bash
cd apps/api && pytest tests/test_large_book_benchmark.py -q
cd apps/api && python -m app.performance.large_book_benchmark --transactions 1000 --expense-accounts 24 --account-branches 16 --account-depth 6 --repeats 3 --json-output /tmp/phase-165-large-account-tree-benchmark.json
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
cd apps/api && pytest -q
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results:

- Targeted benchmark tests passed: `8 passed, 21 warnings`.
- Local synthetic benchmark completed with account-tree HTTP 200 and median timings documented above.
- Frontend auth/static route checks passed.
- Frontend `npm run check` passed with `0 errors and 0 warnings`.
- Backend full suite passed: `389 passed, 32 warnings`.
- Frontend production build passed.
- Docker Compose config validation passed.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Files changed

- `apps/api/app/performance/large_book_benchmark.py`
- `apps/api/tests/test_large_book_benchmark.py`
- `apps/web/src/lib/components/AccountTreeNode.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/performance/phase-165-large-account-tree-benchmark.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-165.md`
