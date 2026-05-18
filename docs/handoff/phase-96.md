# Phase 96 — Synthetic large-export benchmark and UX confirmation

## Status

Complete. Phase 96 implemented `docs/handoff/phase-96-pm-brief.md`: the Phase 95 / GitHub #39 CSV export row-count fix was confirmed through the generated synthetic large-book benchmark path, benchmark JSON evidence now records explicit body-row consistency fields, and the user-visible CSV export helper copy was tightened.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or real/private CSV exports were committed.

## PM brief followed

Goal: re-run or extend the synthetic large-book benchmark focused on CSV export after the Phase 95 fix, and confirm the UI/export copy does not mislead users about filtering, row caps, truncation, or read-only behavior.

Non-goals preserved:

- no write-mode expansion;
- no default write setting change;
- no async/background export infrastructure, streaming export, new export formats, CSV customization, import, or banking integrations;
- no real/private data artifacts;
- no tag/release and no `v0.1.1-readonly` release notes/checklist;
- no performance, security, production-readiness, broad compatibility, or personal-book dogfood claims.

## Implementation

Changed:

- `apps/api/app/performance/large_book_benchmark.py`
  - `BenchmarkResult` now derives `csv_expected_body_rows = min(csv_total, csv_limit)` and `csv_body_matches_expected` for the `csv_export_up_to_cap` benchmark case.
  - CLI output now prints the expected row count and match flag for CSV export evidence.
- `apps/api/tests/test_large_book_benchmark.py`
  - Added regression coverage proving benchmark JSON records `csv_expected_body_rows` and `csv_body_matches_expected`.
- `apps/web/src/routes/transactions/+page.svelte`
  - Updated visible CSV helper copy to state that export is read-only, uses the current filtered view, is capped at 10,000 rows, runs synchronously, and may require narrower filters if it times out or is truncated.
- `apps/web/scripts/test-auth-routes.mjs`
  - Added a static route check covering the important CSV export copy.
- `docs/performance/phase-96-large-export-benchmark.md`
  - Added the Phase 96 synthetic benchmark/evidence artifact.
- `PROJECT_STATUS.md` and `CHANGELOG.md`
  - Updated concise Phase 96 status/evidence.

## TDD evidence

Benchmark JSON evidence RED:

```text
cd apps/api && pytest tests/test_large_book_benchmark.py::test_benchmark_json_records_csv_body_row_consistency -q
FAIL — JSON did not include csv_expected_body_rows / csv_body_matches_expected
```

Benchmark JSON evidence GREEN:

```text
cd apps/api && pytest tests/test_large_book_benchmark.py::test_benchmark_json_records_csv_body_row_consistency -q
PASS — 1 passed, 1 warning
```

Frontend CSV copy RED:

```text
cd apps/web && npm run test:auth-routes
FAIL — CSV export copy did not match read-only/filtered/capped/synchronous requirement
```

Frontend CSV copy GREEN:

```text
cd apps/web && npm run test:auth-routes
PASS — auth route checks passed
```

## Synthetic CSV export evidence

Benchmark command used from `apps/api`:

```bash
python scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --repeats 1 --json-output /tmp/phase-96-large-export-benchmark.json
```

Benchmark CSV result:

```text
csv_export_up_to_cap: status=200
body data rows / item_count: 1000
X-CSV-Export-Limit / csv_limit: 10000
X-CSV-Export-Total / csv_total: 1000
X-CSV-Export-Truncated / truncated: False
expected body rows / min(total, limit): 1000
body rows match expected: True
median duration: 610.97 ms
response bytes: 237387
JSON evidence: /tmp/phase-96-large-export-benchmark.json (outside git)
Committed evidence artifact: docs/performance/phase-96-large-export-benchmark.md
```

The benchmark uses generated synthetic data only. The generated fixture path is under `apps/api/tests/generated-fixtures/phase-87-large-book.gnucash.sqlite` and remains ignored/uncommitted.

## Required checks

```text
cd apps/api && pytest tests/test_large_book_benchmark.py::test_benchmark_json_records_csv_body_row_consistency -q
PASS — 1 passed, 1 warning

cd apps/api && python scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --repeats 1 --json-output /tmp/phase-96-large-export-benchmark.json
PASS — csv_export_up_to_cap returned 1000 rows, csv_limit=10000, csv_total=1000, truncated=False, body_matches_expected=True

cd apps/api && pytest -q
PASS — 329 passed, 27 warnings

cd apps/web && npm run check && npm run test:auth-routes && npm run build
PASS — svelte-check 0 errors/0 warnings; auth route checks passed; production build completed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
PASS

git diff --check
PASS
```

Existing piecash/SQLAlchemy/FastAPI warnings appeared during backend tests/benchmark; they are pre-existing deprecation/relationship warnings, not Phase 96 failures.

## GitHub / backlog

- GitHub #39 was verified closed before implementation and remains closed after the Phase 96 benchmark confirmed the Phase 95 fix.
- GitHub #38 remains open and separate; copied personal-book dogfood still requires a safe copied SQL book outside git.
- No new issue was created.

## Risks / follow-up

- CSV export remains synchronous and capped at 10,000 rows; this phase records correctness evidence and honest UX copy, not async export architecture.
- The benchmark is local/TestClient synthetic pre-alpha evidence only and must not be marketed as production performance evidence.
- Next recommended phase: prepare conservative `v0.1.1-readonly` release notes/checklist without publishing a tag/release, keeping #38 separate unless a safe copied personal SQL book is available.

## Commit / push

Commit: pending until final commit.

Push: pending until final push verification.
