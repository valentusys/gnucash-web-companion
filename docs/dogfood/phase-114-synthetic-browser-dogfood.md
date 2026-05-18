# Phase 114 — Synthetic browser dogfood refresh

Date: 2026-05-19
Status: passed on generated/disposable data
Related roadmap item: analyst Phase 9
Related GitHub issues: #11, #12, #13, #38

## Summary

Phase 114 reran a current Docker/Caddy UI dogfood pass after the recent transaction-filter, account-detail, scheduled-transaction, books-metadata, CORS-safety, and localization changes. The pass used only the committed synthetic/disposable test fixture copied into ignored local runtime data.

Result: core read-only UI/API paths passed locally with `GNUCASH_WRITES_ENABLED=false`. Disabled validate/create/patch write probes returned 403. CSV export was checked through both the API smoke path and authenticated browser/proxy route. No personal/private book dogfood is claimed; GitHub #38 remains blocked until Val provides an explicit safe copied personal SQL book path outside git.

## Runtime setup

- Deployment: local Docker Compose through Caddy.
- Proxy URL: `http://127.0.0.1:18080`.
- Runtime fixture: ignored local copy at `data/books/main.gnucash.sqlite`.
- Source class: committed synthetic/disposable fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Runtime fixture filename recorded only as `main.gnucash.sqlite` in script output.
- Runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- Runtime writes: `GNUCASH_WRITES_ENABLED=false`.
- Web internal API URL: `http://api:8000`.
- Browser: headless Chromium via Chrome DevTools Protocol.

No `.env`, app DB, GnuCash book, backup, screenshot, CSV export, token, cookie, cert, key, private path, or real/private financial data was committed.

## Docker/API evidence

Docker Compose config validation passed with safe dummy secrets and writes disabled.

`/api/health` reported:

```text
status=ok
checks.default_book.exists=true
checks.default_book.readable=true
checks.writes_enabled=false
checks.cors.risk_level=ok
```

API smoke passed:

```text
read-only API smoke: target=http://127.0.0.1:18080/api
ok: API health
ok: login
ok: /auth/me
ok: default book discovered via /books and verified at /books/1
ok: accounts endpoint
ok: transactions endpoint
ok: transaction detail endpoint
ok: CSV export endpoint
ok: reports summary
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
PASS: read-only API smoke checks completed
```

## Browser/UI dogfood evidence

The durable browser dogfood helper added in this phase drives Chromium through CDP without writing screenshots/downloads/raw CSV files.

Passed browser checks:

```text
read-only browser dogfood: target=http://127.0.0.1:18080
fixture: filename=main.gnucash.sqlite sha256=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
ok: login_page: loaded
ok: protected_redirect: dashboard redirected to login
ok: login: authenticated; auth cookie not readable from document.cookie
ok: dashboard: /dashboard loaded; write UI hidden
ok: accounts: /accounts loaded; write UI hidden
ok: books: /books loaded; write UI hidden
ok: scheduled: /scheduled loaded; write UI hidden
ok: account_detail: first account detail loaded
ok: transactions_filters: filtered transactions page loaded; export link preserved query
ok: transaction_detail: first transaction detail loaded
ok: csv_export: status=200 total=0 truncated=false
ok: no_artifacts: no screenshots/downloads/CSV files written
PASS: read-only browser dogfood completed
```

The browser CSV export check intentionally uses an active filtered URL and validates headers/content in memory only. The filtered synthetic combination returned zero rows, which is acceptable for parity: the UI export link preserved the active filter query string and the proxy/API returned a successful CSV response with expected metadata headers and no write side effects.

## Findings and fixes

This phase produced one durable tooling improvement:

- Added `scripts/smoke/read-only-browser-dogfood.py`, a local headless Chromium/CDP dogfood script for Docker/Caddy UI routes.

Operational finding during the run:

- Host environment variable `API_INTERNAL_URL` was set to `http://127.0.0.1:8000`, which is invalid from inside the web container. The runtime was restarted for dogfood with `API_INTERNAL_URL=http://api:8000`. This was an environment issue, not an app bug; no product code change was required.

No application behavior bug was found in the covered read-only routes.

## Acceptance criteria result

- Docker/Caddy starts against synthetic/disposable data: pass.
- Login and authenticated UI shell load: pass.
- Dashboard, accounts, books, scheduled, account detail, transactions filters, and transaction detail load: pass.
- Transaction filter export URL preserves active filters: pass.
- CSV export through browser/proxy route returns expected CSV headers and metadata: pass.
- API smoke covers core read-only endpoints and CSV export: pass.
- Disabled write probes validate/create/patch return 403: pass.
- Write UI remains hidden with `GNUCASH_WRITES_ENABLED=false`: pass.
- No real/private data or runtime artifacts committed: pass.

## Limitations

- This is synthetic/disposable dogfood only, not personal-book dogfood.
- It is local pre-alpha evidence, not a production-readiness claim and not a security audit.
- It does not broaden GnuCash compatibility claims beyond existing fixture evidence.
- It does not publish or prepare a release by itself.

## Safety

- `GNUCASH_WRITES_ENABLED=false` remains the default and was runtime-verified.
- Controlled writes remain post-MVP/experimental.
- GnuCash Desktop remains the authoritative editor.
- Frontend still accesses GnuCash data only through the backend API.
- No screenshots, CSV exports, app DBs, GnuCash books, backups, `.env`, secrets, tokens, certs, keys, private paths, account names from real data, memos, amounts from real data, or personal financial data were committed.

## Verification commands

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

APP_ADMIN_PASSWORD=dummy SMOKE_ADMIN_PASSWORD=dummy SMOKE_API_BASE_URL=http://127.0.0.1:18080/api scripts/smoke/read-only-api-smoke.py
# passed

SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:18080 --fixture-path data/books/main.gnucash.sqlite
# passed
```
