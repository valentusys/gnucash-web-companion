# Phase 206 — Read-only edge-case browser dogfood

Date: 2026-05-20
Status: PASS — local synthetic Docker/Caddy read-only dogfood only

## Scope

This dogfood pass covered the Phase 206 transaction/scheduled read-only edge-case polish after implementation. It used only the committed synthetic fixture copied into ignored runtime storage and kept `GNUCASH_WRITES_ENABLED=false`.

## Runtime setup

- Base URL: `http://127.0.0.1:8080`
- API smoke URL: `http://127.0.0.1:8080/api`
- Runtime fixture: ignored local copy `data/books/main.gnucash.sqlite`
- Fixture source class: committed synthetic/disposable fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`
- Runtime fixture filename recorded by helper only as `main.gnucash.sqlite`
- Runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`
- Local credentials/secrets were dummy-only and are redacted here.

## Results

### Browser dogfood — mobile width

Command used redacted dummy credentials:

```text
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --username admin --fixture-path data/books/main.gnucash.sqlite
```

Result: PASS at `320x720`.

Covered:

- Login page loaded and protected dashboard redirected to login before auth.
- Authenticated session used httpOnly cookie; `access_token` was not readable from `document.cookie`.
- `/dashboard`, `/accounts`, `/books`, `/scheduled`, account detail, transaction filters, and transaction detail loaded with write UI hidden.
- Horizontal-overflow checks passed at `320px`, including `/scheduled`, transaction filters, and transaction detail.
- CSV export link preserved active filters and CSV fetch returned status `200` with the existing export metadata headers.
- No screenshots, downloads, or raw CSV files were written by the browser helper.

### Browser dogfood — desktop width

Command used redacted dummy credentials:

```text
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --username admin --fixture-path data/books/main.gnucash.sqlite --viewport-width 1365 --viewport-height 900
```

Result: PASS at `1365x900`.

Covered the same route set and no-overflow/hidden-write/no-artifact checks as the mobile pass.

### Disabled-write API smoke

Command used redacted dummy credentials:

```text
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py --api-base-url http://127.0.0.1:8080/api --username admin
```

Result: PASS.

Covered:

- `/health`, login, `/auth/me`, books/default book discovery, accounts, transactions, transaction detail, CSV export, and reports summary.
- Disabled write probes for validate/create/PATCH/DELETE returned 403.

## Teardown and artifact hygiene

- Docker Compose stack was stopped with `docker compose down`.
- Ignored runtime fixture/app DB paths created for the smoke were removed after teardown.
- No `.env`, app DB, GnuCash runtime book, backup, screenshot, CSV export, token, key, cert, or private data artifact was committed.

## Boundary

This is local synthetic/disposable evidence only. It does not prove real/private-book safety, production readiness, broad GnuCash Desktop/backend compatibility, or write-mode safety.
