# Add synthetic disposable GnuCash SQLite fixture

Labels: `gnucash, safety, pre-alpha`

Milestone: `v0.1 read-only MVP`

## Goal
Add a small synthetic GnuCash SQL SQLite fixture suitable for automated tests.

## Why
The read-only adapter and future controlled-write flows need validation against a real GnuCash-compatible SQL book, not only mocks.

## Requirements
- No real financial data.
- Fixture must be disposable.
- Include a few accounts:
  - Assets:Bank:Checking
  - Expenses:Food
  - Expenses:Transport
  - Income:Salary
  - Liabilities:Credit Card
- Include simple two-split transactions.
- Include at least one split transaction with more than two splits.
- Document how fixture was created.
- Ensure fixture is safe to commit or generate fixture during tests.

## Acceptance criteria
- Tests can load the fixture.
- Account tree test uses fixture.
- Transaction detail test uses fixture.
- No personal data in fixture.
