# Phase 17 — Synthetic GnuCash Fixture and Read-Only Integration Validation

## Status
Complete — 2026-05-17.

## Actual results

### Files created
- `apps/api/scripts/create_test_fixture.py` — standalone fixture generation script (piecash 1.2.1).
- `apps/api/tests/fixtures/test-book.gnucash.sqlite` — 208 KB synthetic GnuCash book.
- `apps/api/tests/test_integration_fixture.py` — 19 integration tests in 9 test classes.

### Files modified
- `apps/api/tests/test_gnucash_book.py` — replaced `@pytest.mark.skipif` placeholder with `test_fixture_based_integration_tests_exist`.
- `docs/handoff/phase-17.md` — this file.
- `PROJECT_STATUS.md` — Phase 17 marked complete.

### Fixture details
- 10 accounts in `book.accounts` (ROOT is in `book.root_account` only, not in `book.accounts`).
- Account tree: Root Account (ROOT) → Assets (ASSET), Expenses (EXPENSE), Income (INCOME), Liabilities (LIABILITY) → Bank (BANK), Food (EXPENSE), Transport (EXPENSE), Salary (INCOME), Credit Card (LIABILITY) → Checking (BANK).
- 5 transactions: January salary, Grocery store, Bus pass, Monthly expenses (4 splits), Credit card payment.
- Single currency: SEK. No real financial data.

### Integration test results (19 tests)
All pass in ~1s total:
- `TestFixtureConnection::test_fixture_connection` — check_connection() returns True.
- `TestFixtureAccountTree::test_fixture_account_tree` — 10 accounts, 4 tree roots, correct nesting.
- `TestFixtureAccountBalances` — 5 tests: Checking=2729.50, Food=670.50, Salary=5000.00, Transport=350.00, Credit Card=-1250.00.
- `TestFixtureTransactionList` — 3 tests: count=5, date-desc sort, all descriptions present.
- `TestFixtureTransactionDetail` — 2 tests: multi-split has 4 splits, two-split has 2.
- `TestFixtureSummary::test_fixture_summary` — account_count=10, transaction_count=5, currency=SEK.
- `TestFixtureCashflow` — 3 tests: Jan (in=5000, out=320.50), Feb (out=700), full range.
- `TestFixtureReportSummary` — 2 tests: assets/liabilities non-zero, Feb income/expenses correct.
- `TestFixtureErrors::test_fixture_missing_book_error` — BookNotFoundError raised.

### Full backend suite
187 passed, 0 failed (167 existing + 19 new + 1 updated placeholder).

### Frontend checks
- `npm run check` — 0 errors, 0 warnings.
- `npm run test:auth-routes` — passed.
- `npm run build` — built successfully.

### Docker config
`docker compose config --quiet` — passed (exit 0).

### Git
- `git diff --check` — no whitespace errors.
- Fixture file is NOT git-ignored (`.gitignore` allows `tests/fixtures/*.sqlite`).

### Deviations from spec
1. **Account count**: spec said 9 (1 ROOT + 8 children). Actual: `book.accounts` returns 10 non-ROOT accounts. ROOT is in `book.root_account` only. Service layer returns 10 accounts. Tests assert 10.
2. **Account tree**: spec assumed ROOT visible in tree. Actual: ROOT is not in `_accounts()`, so the 4 children of ROOT become top-level tree nodes. Tree has 4 roots, not 1.
3. **Balance signs**: spec said Salary=-5000, Credit Card=1250. Actual (piecash convention): Salary=5000.00 (income positive), Credit Card=-1250.00 (liability negative). Tests match actual piecash behavior.

### No production code changes
Only new test files + script. No changes to services, routers, schemas, frontend, or Docker.

### GitHub issue status
- `docs/github/issues/01-synthetic-disposable-gnucash-sqlite-fixture.md` — closable.
- `docs/github/issues/02-validate-read-only-adapter-real-book.md` — closable.
- `gh` not available; local issue files updated.

## Summary
Create a synthetic (disposable, no real financial data) GnuCash SQLite book fixture and validate the piecash read-only service layer against it. This replaces mock-only tests with real-SQLite integration tests while keeping the repo free of personal data.

## Context
- The existing `test_gnucash_book.py` uses in-memory Python fakes (FakeBook, FakeAccount, etc.) — good for unit logic, but never exercises real piecash SQL reading.
- The optional `tests/fixtures/sample.gnucash` path is referenced in a skipped test but the file does not exist and must not be committed if it contains real data.
- The `.gitignore` already blocks `*.sqlite` / `*.gnucash` in `data/` but does NOT block a committed synthetic fixture under `tests/fixtures/` — this is intentional and acceptable for a disposable test book.
- `piecash>=1.2` is already in `pyproject.toml` dependencies.
- The project is at `v0.0.1-prealpha`. This phase does NOT change the release tag.

## Goal
1. Add a script that generates a small synthetic GnuCash SQLite book using `piecash` (create-book + add accounts + add transactions).
2. Store the generated fixture at `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
3. Add integration tests that open this real fixture with `GnuCashBookService` and validate the full read-only path.
4. Document how the fixture was created and why it is safe to commit.

## Non-goals
- No changes to production code paths (service layer, routers, schemas).
- No real financial data. No personal data. No real account numbers.
- No Docker or deployment changes.
- No frontend changes.
- No write operations — fixture generation is a one-time script, not a runtime feature.
- No multi-currency accounts in the fixture (keep it single-currency SEK for simplicity).
- No GitHub release or tag bump.

## Files likely touched

### New files
- `apps/api/scripts/create_test_fixture.py` — standalone script that uses piecash to create a disposable GnuCash SQLite book with a known account tree and transactions.
- `apps/api/tests/fixtures/test-book.gnucash.sqlite` — the generated fixture (committed to repo; synthetic data only).
- `apps/api/tests/test_integration_fixture.py` — integration tests that validate `GnuCashBookService` against the real fixture.

### Modified files
- `apps/api/tests/test_gnucash_book.py` — remove the `@pytest.mark.skipif` placeholder for `tests/fixtures/sample.gnucash` (or update it to reference the new fixture).
- `docs/handoff/phase-17.md` — this file.

### Potentially updated
- `PROJECT_STATUS.md` — mark Phase 17 complete.
- `.gitignore` — verify that `apps/api/tests/fixtures/*.sqlite` is NOT ignored (the fixture must be commitable). If the global `*.gitignore` patterns block it, add an exception.

## Fixture requirements

### Account tree (all commodity: SEK)
```text
Root (type: ROOT)
├── Assets (type: ASSET)
│   └── Bank (type: BANK)
│       └── Checking (type: BANK)
├── Expenses (type: EXPENSE)
│   ├── Food (type: EXPENSE)
│   └── Transport (type: EXPENSE)
├── Income (type: INCOME)
│   └── Salary (type: INCOME)
└── Liabilities (type: LIABILITY)
    └── Credit Card (type: LIABILITY)
```

### Transactions
1. **Two-split**: Salary → Checking (Income:Salary → Assets:Bank:Checking), amount 5000.00 SEK, date 2026-01-15, description "January salary"
2. **Two-split**: Checking → Food (Assets:Bank:Checking → Expenses:Food), amount -320.50 SEK, date 2026-01-20, description "Grocery store"
3. **Two-split**: Checking → Transport (Assets:Bank:Checking → Expenses:Transport), amount -150.00 SEK, date 2026-02-01, description "Bus pass"
4. **Multi-split (3+ splits)**: Checking → Food + Transport + Credit Card, amount -800.00 SEK total, date 2026-02-15, description "Monthly expenses" (split: Food -350.00, Transport -200.00, Credit Card -250.00)
5. **Two-split**: Checking → Credit Card payment, amount -1000.00 SEK, date 2026-03-01, description "Credit card payment"

### Known balances (for assertions)
- Checking: 5000.00 - 320.50 - 150.00 - 800.00 - 1000.00 = 2729.50 SEK
- Food: 320.50 + 350.00 = 670.50 SEK
- Transport: 150.00 + 200.00 = 350.00 SEK
- Salary: -5000.00 SEK (income accounts are negative)
- Credit Card: 250.00 + 1000.00 = 1250.00 SEK

## Acceptance criteria

1. `python apps/api/scripts/create_test_fixture.py` runs without error and produces `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
2. The fixture contains exactly 9 accounts (1 root + 8 children as specified above).
3. The fixture contains exactly 5 transactions.
4. Integration tests in `test_integration_fixture.py` pass:
   - `test_fixture_connection` — `check_connection()` returns True.
   - `test_fixture_account_tree` — full account tree has correct structure and count.
   - `test_fixture_account_balances` — Checking balance == "2729.50", Food == "670.50", Salary == "-5000.00".
   - `test_fixture_transaction_list` — 5 transactions returned, sorted by date desc.
   - `test_fixture_transaction_detail` — multi-split transaction (guid or description match) has 4 splits.
   - `test_fixture_summary` — account_count == 9, transaction_count == 5, currency == "SEK".
   - `test_fixture_cashflow` — cashflow for Jan 2026 has expected inflow/outflow.
   - `test_fixture_report_summary` — report summary returns non-zero assets and liabilities.
   - `test_fixture_missing_book_error` — non-existent path raises BookNotFoundError.
5. All existing tests still pass: `cd apps/api && pytest -q` — no regressions.
6. No real financial data in the fixture (all descriptions are generic: "Grocery store", "Bus pass", etc.).
7. `.gitignore` allows the fixture file to be committed.
8. Phase handoff doc (`docs/handoff/phase-17.md`) is updated with results.
9. `PROJECT_STATUS.md` updated: Phase 17 marked complete.

## Safety checks

- [ ] No production code modified (only new test files + script).
- [ ] No real financial data in fixture.
- [ ] No `.env`, secrets, credentials created or modified.
- [ ] `GNUCASH_WRITES_ENABLED` remains `false` (not touched).
- [ ] Fixture is read-only — integration tests only call read methods.
- [ ] `.gitignore` still blocks `data/books/*`, `data/app/*`, `data/backups/*`, `.env`, secrets.
- [ ] No frontend changes.
- [ ] No Docker/deployment changes.
- [ ] All existing tests pass (167+ passed, no new failures).

## Verification commands

```bash
# Generate fixture
cd apps/api
python scripts/create_test_fixture.py

# Run all backend tests (existing + new integration tests)
pytest -q

# Verify fixture exists and is reasonable size (< 1MB)
ls -lh tests/fixtures/test-book.gnucash.sqlite

# Verify no real data in fixture (spot-check)
python -c "
import sqlite3
conn = sqlite3.connect('tests/fixtures/test-book.gnucash.sqlite')
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print('Tables:', [t[0] for t in tables])
for t in tables:
    count = conn.execute(f'SELECT COUNT(*) FROM \"{t[0]}\"').fetchone()[0]
    print(f'  {t[0]}: {count} rows')
conn.close()
"

# Verify .gitignore allows the fixture
git check-ignore -v tests/fixtures/test-book.gnucash.sqlite
# (should return nothing — meaning the file is NOT ignored)

# Frontend checks still pass
cd ../../apps/web
npm run check
npm run test:auth-routes
npm run build

# Docker config still valid
cd ../..
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

## Handoff requirements

After Phase 17 completion:
1. Update `PROJECT_STATUS.md` — add Phase 17 entry, mark complete.
2. Update `docs/handoff/phase-17.md` — record actual results, test counts, any deviations.
3. Commit all changes.
4. Push to GitHub if auth is available.
5. Create/update GitHub issue if `gh` is available.

## GitHub/backlog

Related existing issues:
- `docs/github/issues/01-synthetic-disposable-gnucash-sqlite-fixture.md`
- `docs/github/issues/02-validate-read-only-adapter-real-book.md`

After Phase 17, both issues should be closable (mark as done in the local issue file).

Next backlog items after this phase:
- `docs/github/issues/03-readme-screenshots-mobile-preview.md`
- `docs/github/issues/06-document-multicurrency-reporting-limitations.md`
- `docs/github/issues/05-book-switcher-ui-future-multibook.md`

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| piecash version mismatch produces different SQLite schema | Fixture may not open in CI or other environments | Pin piecash version in script comments; document tested version |
| Fixture file too large for repo | Bloated git history | Keep it minimal (9 accounts, 5 transactions); expect < 200KB |
| `.gitignore` blocks fixture commit | Tests fail in CI because fixture is missing | Add explicit `!tests/fixtures/*.sqlite` exception if needed |
| Integration tests slow down CI | Longer feedback loop | Fixture is small; tests should run in < 5s total |
| Accidentally modifying fixture during tests | Test pollution, flaky tests | Integration tests must only call read-only methods; never write |
