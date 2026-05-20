# Phase 216 dogfood — read-only CSV/list parity

Date: 2026-05-21

## Scope

Cycle 2 Phase 5 verified read-only CSV/export and transaction-list parity with a committed synthetic fixture copied into ignored runtime storage.

This dogfood did not enable writes, did not use a real/private book, and did not save screenshots, downloads, or raw CSV bodies.

## Runtime setup

- Runtime book: committed synthetic fixture copied to ignored `data/books/phase-216-csv-parity.gnucash.sqlite`.
- App DB: temporary local runtime DB; any previous ignored local `data/app/app.db` was moved aside and restored after teardown.
- Local-only dummy credentials/secrets were used and are intentionally redacted here.
- `GNUCASH_WRITES_ENABLED=false` was set explicitly.
- `ORIGIN=http://localhost:8080` was set for the local Caddy/browser smoke.

## Evidence

Commands run:

```bash
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py --api-base-url http://localhost:8080/api
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --viewport-width 320 --viewport-height 720
```

API smoke passed:

- health, login, `/auth/me`;
- `/books` default book discovery;
- accounts, transactions, transaction detail;
- CSV export endpoint with advisory headers;
- reports summary, scheduled metadata, write-alpha audit summary;
- validate/create/PATCH/DELETE probes returned write-disabled responses.

Browser dogfood passed at 320x720:

- login and protected redirect;
- auth cookie not readable from `document.cookie`;
- dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail;
- CSV export fetched through browser `fetch` without writing a download artifact;
- CSV response status `200`, `X-CSV-Export-Total=0`, `X-CSV-Export-Truncated=false`, and expected header prefix;
- no screenshots/downloads/CSV files were written;
- hidden write UI remained hidden.

## Cleanup

Docker Compose was stopped with volumes removed. The ignored Phase 216 runtime book and temporary runtime app DB were removed. The pre-existing ignored local app DB, if present, was restored.

## Safety notes

- `GNUCASH_WRITES_ENABLED=false` remained the runtime default.
- No CSV body, screenshot, export file, runtime book, app DB, backup, `.env`, token, key, cert, private path, account name, memo, or amount was committed.
- This is synthetic read-only parity evidence only; it does not claim production readiness, security-audit completion, broad compatibility, or write safety for real/private books.
