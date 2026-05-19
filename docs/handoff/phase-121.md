# Phase 121 — Dashboard summary zero-value fallback fix

Date: 2026-05-19
Status: complete
Previous phase: `docs/handoff/phase-120.md`

## Goal

Fix Conservative dashboard totals showing zero when base-currency transactions exist, without adding currency conversion, float money handling, dashboard redesign, or write behavior.

## Scope completed

- Investigated the backend dashboard summary path in `apps/api/app/services/gnucash_book.py` and the existing API regression coverage in `apps/api/tests/test_reports.py`.
- Added a regression test with synthetic base-currency current-period transactions whose account balance fields all report zero but whose splits contain known values for:
  - assets;
  - liabilities;
  - net worth;
  - income this month;
  - expenses this month.
- Confirmed the RED failure before implementation: the new regression returned `assets == "0.00"` despite base-currency balance splits.
- Updated `get_report_summary()` to accumulate split-derived base-currency asset/liability totals through the requested `as_of_date` while scanning transactions for month-to-date income/expense values.
- Kept the fallback conservative: split-derived asset/liability totals replace account-balance totals only when both account-balance asset and liability totals are zero and at least one relevant base-currency balance split exists.
- Preserved legitimate empty-book zero summaries.
- Preserved existing no-conversion behavior: non-base-currency accounts/splits remain excluded without fake FX conversion.

## Implementation notes

Primary files changed:

- `apps/api/app/services/gnucash_book.py`
  - Reuses explicit asset and liability account type sets in `get_report_summary()`.
  - Accumulates base-currency asset/liability split totals for transactions with `tx_date <= as_of_date`.
  - Continues to compute income/expense only for the requested month-to-date window.
  - Falls back to split-derived asset/liability totals only when account-balance asset/liability totals are both zero.

- `apps/api/tests/test_reports.py`
  - Added `test_summary_falls_back_to_current_base_currency_splits_when_balances_are_zero`.
  - Fixture includes current-period income/expense, prior-period balance impact, future transaction exclusion, and foreign-currency exclusion.
  - Expected values: assets `1420.00`, liabilities `-200.00`, net worth `1220.00`, income this month `500.00`, expenses this month `-50.00`.

- `PROJECT_STATUS.md`
  - Updated baseline through Phase 121 and added the Phase 121 status entry.

- `CHANGELOG.md`
  - Added an Unreleased Phase 121 fixed entry.

## Verification run

TDD RED/GREEN evidence:

```bash
cd apps/api && pytest tests/test_reports.py::TestReportSummaryMVP::test_summary_falls_back_to_current_base_currency_splits_when_balances_are_zero -q
```

RED result before implementation: failed as expected because `assets` was `0.00` instead of `1420.00`.

Targeted GREEN checks:

```bash
cd apps/api && pytest tests/test_reports.py::TestReportSummaryMVP::test_summary_falls_back_to_current_base_currency_splits_when_balances_are_zero tests/test_reports.py::TestReportSummaryMVP::test_empty_book_returns_conservative_zero_summary tests/test_reports.py::TestReportSummaryMVP::test_summary_values -q
```

Result: `3 passed`.

Broader targeted report checks:

```bash
cd apps/api && pytest tests/test_reports.py tests/test_integration_fixture.py::TestFixtureReportSummary tests/test_compatibility_fixture_v1.py::TestCompatibilityFixtureV1ReadOnlyCoverage::test_reports_basic_values_are_available -q
```

Result: `33 passed`.

Final required checks for this phase:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
git diff --check
```

Results:

- Backend pytest: passed (`353 passed, 27 warnings`).
- Frontend check: passed, 0 errors, 0 warnings.
- Frontend auth route/static checks: passed.
- Frontend build: passed.
- `git diff --check`: passed.

## Safety notes

- Read-only dashboard summary logic only.
- No GnuCash write path touched.
- No controlled-write expansion.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- No currency conversion added or faked.
- Money remains Decimal/string-only; no float handling added.
- No real/private GnuCash book, app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private path, account name, transaction description, memo, amount, or personal financial data was added.
- No release, tag, or package publication.

## Follow-up ideas

Not part of Phase 121:

- currency conversion;
- dashboard redesign;
- global dashboard performance optimization;
- changing account-list balance behavior;
- write-mode behavior.
