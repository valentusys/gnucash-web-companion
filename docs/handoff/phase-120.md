# Phase 120 — Account detail performance optimization

## Summary

Phase 120 optimized the read-only account detail transaction path. Account-scoped transaction list/count now avoids unnecessary full-book transaction iteration for real piecash books by querying transaction candidates through account splits first, then applying the existing service-layer filters and pagination semantics.

No API contract, write path, dashboard/global list behavior, release/tag/package, private data, or default write configuration changed. `GNUCASH_WRITES_ENABLED=false` remains the default.

## Scope completed

- Investigated the account transaction path in `apps/api/app/services/gnucash_book.py` and benchmark coverage in `apps/api/app/performance/large_book_benchmark.py`.
- Added an optimized account-scoped transaction candidate query for real piecash books.
- Preserved existing account-scope behavior for:
  - query filter;
  - date range filters;
  - amount range filters;
  - reconciliation state filter;
  - pagination;
  - CSV export parity;
  - unknown account IDs returning empty list/count.
- Added regression coverage proving the account-scoped service path does not touch the global `book.transactions` collection.
- Extended synthetic read-only benchmark coverage with account-detail filtered list and account-detail CSV export cases.
- Documented local synthetic benchmark evidence in `docs/performance/phase-120-account-detail-benchmark.md`.

## Implementation notes

Primary files changed:

- `apps/api/app/services/gnucash_book.py`
  - Imported `joinedload`.
  - Account-scoped transaction retrieval now attempts a real piecash SQLAlchemy query joining `Transaction.splits` and filtering `Split.account_guid == account_id`.
  - Eager-loads selected transaction splits and split accounts for downstream mapping/filtering.
  - Keeps compatibility fallback for lightweight test doubles that do not expose the piecash SQLAlchemy session/relationship shape.
  - Fixed the previous fallback behavior where an account with splits but no matching transaction candidates could still fall back to the global book transaction scan.

- `apps/api/tests/test_gnucash_book.py`
  - Added `test_account_scoped_transactions_use_account_splits_without_global_scan`.
  - The test uses a fake book whose `transactions` property raises if touched, proving account scope stays scoped.

- `apps/api/app/performance/large_book_benchmark.py`
  - Added `account_detail_transactions_filtered` benchmark case.
  - Added `account_detail_csv_export` benchmark case.
  - CSV body/header consistency checks now cover account-detail CSV export as well as the existing global capped CSV case.

- `apps/api/tests/test_large_book_benchmark.py`
  - Updated benchmark-plan assertions for Phase 120 cases.
  - Added summary coverage for account-detail CSV limit/header/body metadata.

- `docs/performance/phase-120-account-detail-benchmark.md`
  - Documents benchmark command, local result, before/after synthetic comparison, and limitations.

- `PROJECT_STATUS.md`
  - Updated baseline to completed through Phase 120 and added a Phase 120 status entry.

## Benchmark evidence

Command run from `apps/api`:

```bash
python -m app.performance.large_book_benchmark \
  --transactions 1000 \
  --repeats 3 \
  --json-output tests/generated-fixtures/phase-120-account-detail-benchmark.json
```

Result highlights from synthetic disposable data only:

- `account_detail_transactions`: median `296.83 ms`;
- `account_detail_transactions_page_2`: median `291.64 ms`;
- `account_detail_transactions_filtered`: median `295.75 ms`;
- `account_detail_csv_export`: median `294.34 ms`, `csv_total=961`, `expected_body_rows=961`, `body_matches_expected=True`.

Historical Phase 88 synthetic evidence on the same benchmark family recorded account detail medians above one second. Phase 120 evidence is bounded local synthetic evidence only and is not a production scalability claim.

Generated benchmark JSON remained under ignored `apps/api/tests/generated-fixtures/` and was not committed.

## Verification run

Targeted checks completed before full-suite verification:

```bash
cd apps/api && pytest tests/test_large_book_benchmark.py tests/test_gnucash_book.py::test_account_scoped_transactions_use_account_splits_without_global_scan -q
```

Result: `8 passed`.

Full required verification for this phase:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
```

Docker Compose config validation was not required because env/config/release/status files were not changed.

## Safety notes

- Read-only API behavior only.
- No controlled writes work.
- No real/private financial data used or committed.
- No screenshot/CSV export/private fixture committed.
- No release, tag, or package publication.
- `GNUCASH_WRITES_ENABLED=false` remains default.

## Follow-up ideas

Not part of Phase 120:

- global transaction list optimization;
- dashboard read-path optimization;
- caching layer;
- production performance claims;
- write-mode behavior.
