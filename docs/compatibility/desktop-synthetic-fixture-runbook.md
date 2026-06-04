# Desktop synthetic SQLite fixture runbook for #22

Status: manual-safe external blocker runbook. Use this only for isolated synthetic fixture evidence. Do not use private or owner books.

## Decision gate

Run this only when the operator has an isolated disposable GnuCash Desktop GUI environment. If that environment is unavailable, keep #22 open.

A future worker may close #22 only after all of these are true:

1. A synthetic SQLite book was created/saved by GnuCash Desktop in an isolated disposable GUI/manual-safe environment.
2. The raw book stayed outside git and outside private/source-only folders.
3. Redacted metadata passed `scripts/preflight_desktop_fixture_candidate.py`.
4. Default-read-only validation passed with `GNUCASH_WRITES_ENABLED=false`.
5. No private paths/data, screenshots, exports, app DBs, backups, tokens, keys, certs, account names, descriptions, memos, amounts, or raw SQL/DB data were committed or posted.

## Required environment

Use a disposable VM/container/desktop session with:

- GnuCash Desktop installed;
- a working display server or Xvfb/GUI session;
- no mounted private home directory;
- no mounted owner/private GnuCash books;
- no mounted app runtime `data/app`, `data/books`, `data/backups`, `.env`, `secrets`, or backup directories;
- network optional; not required for fixture creation;
- an output directory outside git, for example `/tmp/gwc-desktop-fixture`.

Do not use `E:\Syncthing\Main\Other\gnucash` or any source-only/private folder.

## Synthetic data requirements

Create only a minimal disposable book. Recommended data:

- book/backend: SQLite;
- currency: any generic test currency supported by GnuCash, for example USD or SEK;
- accounts:
  - `Assets:Checking`
  - `Expenses:Test`
  - `Equity:Opening Balances`
- optional transaction if needed by Desktop workflow:
  - date: a generic fixed date such as 2024-01-01;
  - description: `Synthetic fixture transaction`;
  - splits: `Assets:Checking` and `Equity:Opening Balances`;
  - amount: a trivial synthetic value only, never a real amount.

If public evidence is later posted, do not include account names, transaction descriptions, memos, or amounts. The names above are allowed only as local creation instructions for the synthetic book.

## Desktop creation steps

1. Start the isolated disposable Desktop GUI environment.
2. Start GnuCash Desktop.
3. Create a new file/book.
4. Choose SQLite backend when saving.
5. Create only the synthetic account tree and optional trivial synthetic transaction described above.
6. Save to an outside-git path with a synthetic/disposable filename, for example:

```text
/tmp/gwc-desktop-fixture/desktop-synthetic-fixture.gnucash.sqlite
```

7. Close GnuCash Desktop before web/API validation.
8. Do not capture screenshots. Do not export CSV. Do not upload the raw DB.

## Metadata collection

From the repository root, collect redacted metadata only:

```bash
python3 apps/api/scripts/collect_gnucash_compatibility_metadata.py \
  /tmp/gwc-desktop-fixture/desktop-synthetic-fixture.gnucash.sqlite \
  --gnucash-version "GnuCash X.Y" \
  --fixture-origin desktop-generated-synthetic \
  --output /tmp/gwc-desktop-fixture/desktop-synthetic-fixture-metadata.json
```

Replace `GnuCash X.Y` with the exact Desktop version shown by the isolated Desktop environment.

Expected safe collector behavior:

- input path redacted as `<redacted>`;
- `fixture_origin` is `desktop-generated-synthetic`;
- `desktop_generated_synthetic_fixture` is `true`;
- `backend` is `SQLite`;
- `versions` contains schema markers;
- `table_counts` contains only bounded counts for safe tables;
- no row values, account names, descriptions, amounts, memos, or private paths.

## Candidate preflight

Create a small candidate JSON for preflight by adding the required explicit validation markers to the redacted metadata after read-only validation passes:

```json
{
  "backend": "SQLite",
  "fixture_origin": "desktop-generated-synthetic",
  "desktop_generated_synthetic_fixture": true,
  "gnucash_desktop_version": "GnuCash X.Y",
  "fixture_scope": "synthetic",
  "synthetic_disposable_evidence": "operator-created-disposable-empty-book",
  "default_read_only_validation": "passed",
  "versions": {"Gnucash": 3000000, "Gnucash-Resave": 19920},
  "table_counts": {"accounts": 3, "transactions": 1, "splits": 2, "commodities": 1, "books": 1}
}
```

Then run:

```bash
python3 scripts/preflight_desktop_fixture_candidate.py \
  /tmp/gwc-desktop-fixture/desktop-fixture-candidate-metadata.json
```

Expected output shape:

```json
{
  "accepted": true,
  "backend": "SQLite",
  "default_read_only_validation": "passed",
  "fixture_origin": "desktop-generated-synthetic"
}
```

If preflight fails, keep #22 open and fix only the metadata/evidence issue. Do not weaken the guard.

## Default-read-only validation

Use only a disposable runtime copy of the synthetic fixture. Keep writes disabled:

```bash
export GNUCASH_WRITES_ENABLED=false
```

Run the project gates relevant to read-only compatibility from the repository root:

```bash
cd apps/api && pytest -q tests/test_compatibility_fixture_v1.py tests/test_integration_fixture.py
cd ../..
python3 scripts/check_public_status.py
python3 scripts/check_tracked_hygiene.py
```

If a smoke validation is available and configured for a disposable runtime copy, run it with writes disabled:

```bash
GNUCASH_WRITES_ENABLED=false SMOKE_ADMIN_PASSWORD=dummy-local-password \
  scripts/smoke/read-only-api-smoke.py
```

Do not run real/private/owner-book mutation. Do not run copied-book dogfood for #22.

## What may be committed

Allowed:

- this runbook;
- package handoffs/final report;
- redacted metadata summaries with no raw paths/row values/private data, if reviewed;
- validator outputs that contain only bounded, redacted fields.

Forbidden:

- raw `.gnucash`, `.gnucash.sqlite`, `.sqlite`, `.sqlite3`, `.db` files;
- app DBs, backups, screenshots, CSV exports, `.env`, tokens, keys, certs;
- private paths, account names, transaction descriptions, memos, amounts, SQL dumps, row data;
- owner/private/working/only-copy books or evidence from them.

## #22 update template after successful evidence

Use only after actual evidence exists and gates pass:

```text
Desktop-generated synthetic SQLite fixture evidence was produced in an isolated disposable GUI environment and validated with writes disabled. Raw fixture stayed outside git. Redacted metadata passed scripts/preflight_desktop_fixture_candidate.py and default-read-only validation. Scope remains synthetic SQLite only; no private/real-book, broad backend, production, stable, security-audited, or public-write claim.
```

## #22 update template when blocked

```text
#22 remains open. Current blocker is external/manual: this environment cannot safely create the Desktop-generated synthetic SQLite fixture because GUI/Xvfb automation is unavailable or no isolated Desktop GUI session was provided. Next manual step: create/save a minimal synthetic SQLite book in an isolated disposable GnuCash Desktop session, keep the raw DB outside git, run redacted metadata collection, run scripts/preflight_desktop_fixture_candidate.py, and run default-read-only validation with GNUCASH_WRITES_ENABLED=false.
```
