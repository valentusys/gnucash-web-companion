# Compatibility Fixture v1

Status: Phase 46 implementation artifact. This document describes the first generated disposable compatibility fixture path. It does not claim broad GnuCash Desktop compatibility.

`gnucash-web-companion` remains read-only by default. `GNUCASH_WRITES_ENABLED=false` remains the safe default. Controlled writes remain experimental post-MVP and disabled by default.

## What Phase 46 adds

Phase 46 adds a reproducible generator path instead of committing a new binary GnuCash book:

```bash
cd apps/api
python scripts/create_compatibility_fixture_v1.py
```

By default the script writes to:

```text
apps/api/tests/generated-fixtures/compatibility-v1.gnucash.sqlite
apps/api/tests/generated-fixtures/compatibility-v1.gnucash.sqlite.metadata.json
```

That directory is git-ignored. The generated SQLite book and metadata are local test artifacts, not tracked release data.

The generator can also write to an explicit temporary path:

```bash
cd apps/api
python scripts/create_compatibility_fixture_v1.py /tmp/compatibility-v1.gnucash.sqlite
```

## Fixture source and limits

- Fixture ID: `compatibility-v1-piecash-synthetic`.
- Format: GnuCash SQLite.
- Generator: `apps/api/scripts/create_compatibility_fixture_v1.py`.
- Source: synthetic disposable fixture generated with `piecash`.
- Desktop version: not desktop-generated in Phase 46 v1.
- Base currency: SEK.
- Real data: none.
- Phase 102 metadata refresh: generated fixture metadata now includes safe runtime provenance (`generator_version`, OS, Python version, SQLite version, and piecash version) so local evidence is easier to reproduce without exposing row data or private paths.

This is a compatibility implementation path beyond mocks because the read-only service opens and reads a real SQLite GnuCash book generated on demand. It is not yet a matrix of books saved by multiple GnuCash Desktop releases. That remains future compatibility work.

## Synthetic data model

The fixture uses boring fake names only:

- Assets: Checking, Savings, Cash.
- Liabilities: Credit Card.
- Income: Salary, Interest.
- Expenses: Groceries, Utilities, Travel.
- Equity: Opening Balances.

It creates nine transactions in January 2024:

- two opening balances;
- salary income;
- interest income;
- grocery expense;
- one four-split monthly expense transaction;
- transfer to cash;
- credit-card expense;
- credit-card payment.

There are no real account numbers, addresses, customer/vendor names, private paths, screenshots, CSV exports, app DBs, backups, `.env` files, secrets, keys, or tokens.

## Validation coverage

`apps/api/tests/test_compatibility_fixture_v1.py` generates the fixture in `tmp_path` and validates:

- fixture generation and non-sensitive metadata;
- safe runtime provenance in generated fixture metadata;
- SQLite `versions` markers are readable;
- read-only service access does not mutate the fixture checksum;
- account tree;
- transaction list;
- split transaction detail;
- basic report summary values;
- copied generated fixture can be loaded from a documented path.

Run the Phase 46 fixture tests with:

```bash
cd apps/api
pytest -q tests/test_compatibility_fixture_v1.py
```

## Safety notes

- Do not commit generated `.gnucash.sqlite` files from this path.
- Do not replace this fixture with a scrubbed real user book.
- If a future phase adds desktop-generated fixtures, record GnuCash Desktop version, OS/source, SQL backend, schema markers, generator/manual steps, and SHA-256.
- Keep compatibility claims conservative until desktop-generated fixtures and CI coverage exist.
