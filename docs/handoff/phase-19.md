# Phase 19 — Multi-Currency Limitation Tests and Auth Cookie Security Documentation

## Status
Complete — 2026-05-17.

## Results

### Multi-currency fixture
- Created `apps/api/tests/fixtures/test-book-multicurrency.gnucash.sqlite` (208 KB).
- SEK base currency + EUR commodity.
- 13 accounts: 10 SEK (Assets, Bank, Checking, Expenses, Food, Transport, Income, Salary, Liabilities, Credit Card) + 3 EUR (EUR Income, EUR Expenses, EUR Travel).
- 6 transactions: 5 SEK + 1 EUR (Paris hotel, 120 EUR, 2 splits).
- Created by `apps/api/scripts/create_multicurrency_fixture.py`.

### Multi-currency integration tests
- Created `apps/api/tests/test_multicurrency_reports.py` — 11 new tests.
- All tests pass (11/11).
- Test classes:
  - `TestMultiCurrencyAccountListing` (3 tests) — all 13 accounts returned regardless of currency.
  - `TestMultiCurrencyReportSummary` (5 tests) — EUR accounts excluded from assets, liabilities, net worth, income, expenses.
  - `TestMultiCurrencyCashflow` (2 tests) — EUR splits excluded from cashflow totals.
  - `TestMultiCurrencyExpensesByAccount` (3 tests) — EUR expense accounts excluded; only SEK accounts appear.

### Auth cookie documentation
- Created `docs/security/auth-cookie-deployment.md`.
- Covers: cookie attributes table, stateless JWT logout model, local development behaviour, self-hosted deployment warnings, no-production-guarantee disclaimer.

### README update
- Added `## Security and Deployment` section (3 sentences + link to new doc).

### Test results
- Before: 187 passed.
- After: **198 passed** (187 existing + 11 new multi-currency tests), 0 failed.

### Verification
- `pytest -q` — 198 passed, 27 warnings.
- `npm run check` — 0 errors, 0 warnings.
- `npm run build` — built successfully.
- `docker compose config --quiet` — passed.

### Safety checks
- No production code modified (only docs, tests, test fixtures).
- No real financial data in any fixture.
- `.gitignore` intact.
- `GNUCASH_WRITES_ENABLED` untouched.
- Auth doc includes pre-alpha disclaimer.

### Deviations from spec
- None. All acceptance criteria met.

## Related issues
Closes GitHub issues #6 (document multi-currency reporting limitations) and
#10 (auth cookie security review).
