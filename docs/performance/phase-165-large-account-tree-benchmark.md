# Phase 165 — Large account tree benchmark and usability hardening

Date: 2026-05-20
Status: DONE
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 4/10 only)

## Scope

Phase 165 improves read-only account-tree large-hierarchy evidence without adding account editing, caching, production scalability claims, or real account names.

Implemented evidence/tooling:

- The existing synthetic large-book benchmark can now generate a wide/deep synthetic account hierarchy.
- Benchmark metadata records:
  - `account_branch_count`;
  - `account_depth`;
  - `synthetic_account_count`.
- The benchmark plan includes an account-tree large-hierarchy seed case so account-tree timing remains visible next to transaction/report paths.
- Regression tests prove the hierarchy generator uses synthetic account names only and rejects invalid hierarchy sizes.

Implemented UX fix:

- `AccountTreeNode.svelte` now caps visual indentation at depth 8 while preserving the full account path in hover/title text.
- This prevents very deep synthetic or real account paths from pushing the account row content horizontally on desktop/mobile layouts.
- Existing local account filtering remains URL-free, browser-storage-free, read-only, and searches only already-loaded account metadata.

## Local benchmark command

Run from `apps/api`:

```bash
python -m app.performance.large_book_benchmark \
  --transactions 1000 \
  --expense-accounts 24 \
  --account-branches 16 \
  --account-depth 6 \
  --repeats 3 \
  --json-output /tmp/phase-165-large-account-tree-benchmark.json
```

The generated SQLite fixture is written under `apps/api/tests/generated-fixtures/`, which is ignored by git. The JSON output was written to `/tmp` and was intentionally not committed.

## Local result

Fixture shape:

- Transactions: 1,000 synthetic transactions.
- Expense accounts: 24 synthetic expense accounts.
- Hierarchy branches: 16 synthetic branches.
- Hierarchy depth: 6 nested synthetic levels per branch.
- Synthetic account count: 146 non-root benchmark accounts.
- Many-splits transaction: 60 splits.
- Private/real data: none.
- Write paths: not used.

Selected benchmark timings from the local TestClient run:

| Case | Status | Median |
| --- | ---: | ---: |
| `accounts_tree_load` | 200 | 185.88 ms |
| `accounts_tree_large_hierarchy_filter_seed` | 200 | 198.76 ms |
| `account_detail_transactions` | 200 | 302.12 ms |
| `account_detail_transactions_page_2` | 200 | 294.12 ms |
| `dashboard_summary` | 200 | 688.47 ms |
| `csv_export_up_to_cap` | 200 | 623.25 ms |

CSV consistency remained intact in this run:

- `csv_export_up_to_cap`: 1,000 body rows, `csv_limit=10000`, `csv_total=1000`, `truncated=False`, `body_matches_expected=True`.
- `account_detail_csv_export`: 961 body rows, `csv_limit=10000`, `csv_total=961`, `truncated=False`, `body_matches_expected=True`.

## Interpretation and limits

- The large account tree loaded successfully in the in-process read-only API benchmark.
- The account UI now guards against deep-hierarchy indentation overflow with a bounded visual indent.
- This is local synthetic/TestClient evidence only. It is not a production scalability claim.
- The benchmark does not measure reverse proxy latency, browser rendering time, real private books, network variability, or production deployment behavior.
- Transaction filter paths still have higher local medians than account-tree paths and remain documented as pre-alpha performance evidence, not production confidence.

## Safety

- Synthetic account names only: `Synthetic ...`.
- No real/private GnuCash book was opened or committed.
- No `.env`, app DB, backup, screenshot, raw CSV export, token, key, cert, private path, account name, transaction description, memo, amount, or private financial data was committed.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No account editing, cache layer, production write mode, tag, release, package, or production scalability/security claim was added.
