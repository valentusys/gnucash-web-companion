# Phase 215 dogfood — unavailable-book recovery

Date: 2026-05-21

## Scope

Local Docker/Caddy dogfood for the Phase 215 unavailable-book read-only error contract.

The run used only:

- committed synthetic fixture copied into ignored runtime data;
- dummy local-only admin credentials;
- default-disabled writes: `GNUCASH_WRITES_ENABLED=false`;
- an app-metadata-only accessible synthetic book entry whose underlying local file is intentionally missing.

No real/private GnuCash book, app DB, backup, screenshot, CSV export, token, key, certificate, or raw financial data was committed.

## Runtime setup

- Default book path: ignored runtime synthetic fixture `phase-215-synthetic.gnucash.sqlite`.
- Unavailable book entry: accessible synthetic metadata row with missing local storage.
- Write mode: disabled by default.
- Web origin: local Docker/Caddy.

## Evidence

- `/api/health` returned `status=ok` with default book present/readable and writes disabled.
- `scripts/smoke/read-only-api-smoke.py` passed:
  - health;
  - login/auth;
  - books/default book;
  - accounts;
  - transactions;
  - transaction detail;
  - CSV export;
  - reports summary;
  - scheduled transactions;
  - write-alpha audit summary;
  - validate/create/PATCH/DELETE all returned disabled-write 403.
- `scripts/smoke/read-only-browser-dogfood.py` passed at `320x720` with unavailable-book recovery enabled.
- `scripts/smoke/read-only-browser-dogfood.py` passed at `1280x900` with unavailable-book recovery enabled.

The browser dogfood verified:

- login and protected-route redirect;
- auth cookie was not readable from `document.cookie`;
- inaccessible/unavailable synthetic book selection redirected to `/books?book_context=unavailable_selected_book`;
- `/books` showed safe storage diagnostics without raw path fragments or data-view links for the unavailable book;
- dashboard/accounts/books/scheduled/account-detail/transactions/transaction-detail loaded for the available synthetic book;
- write UI stayed hidden;
- CSV export fetch succeeded without writing browser download artifacts;
- no screenshots/downloads/raw CSV files were produced.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remained the rendered/runtime default.
- The unavailable-book row was app metadata only; the missing file was not opened.
- No upload/delete/default-changing/registry-edit UI was added.
- No write-enabled mode was run.
- No broad compatibility, production-readiness, security-audited, or real/private-book safety claim is made.
