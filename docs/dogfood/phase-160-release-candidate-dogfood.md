# Phase 160 — Release-candidate synthetic Docker/browser dogfood

Date: 2026-05-20
Status: PASS — synthetic/disposable release-candidate dogfood passed after Phases 153–159
Starting HEAD: `131d568`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 9/10 only)

## Summary

Phase 160 reran the complete local Docker/Caddy read-only dogfood pass after the cycle's read-only changes through Phase 159.

Result: PASS on synthetic/disposable data. The local API smoke, headless browser dogfood, hidden write UI checks, disabled write endpoint probes, no-artifact checks, Docker Compose validation, and sensitive tracked-file hygiene checks passed with `GNUCASH_WRITES_ENABLED=false`.

No release, tag, package, image, production deployment, write-alpha expansion, private directory search, copied personal-book run, screenshot, raw CSV export, app DB, GnuCash book, backup, `.env`, token, key, cert, private path, or real/private financial data was committed.

## Runtime setup

- Deployment: local Docker Compose through Caddy.
- Proxy URL: `http://localhost:8080`.
- API smoke URL: `http://localhost:8080/api`.
- Runtime fixture: ignored local copy at `data/books/main.gnucash.sqlite`.
- Source class: committed synthetic/disposable fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Runtime fixture filename recorded only as `main.gnucash.sqlite` in dogfood output.
- Runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- Runtime writes: `GNUCASH_WRITES_ENABLED=false`.
- Browser: headless Chromium via Chrome DevTools Protocol at 320x720 mobile viewport.
- SvelteKit origin: `ORIGIN=http://localhost:8080`.

The ignored local `data/app/app.db` already existed, so it was temporarily moved aside for the disposable Docker run to ensure the dummy admin password matched the smoke configuration. The generated ignored app DB and runtime fixture were removed after `docker compose down`, and the previous ignored app DB was restored. This did not affect tracked files and no app DB artifact was added to git.

## Docker/health evidence

Docker Compose config validation passed with dummy local secrets and writes disabled:

```text
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config --quiet
# passed
```

Rendered Compose config kept writes disabled for both API and web services:

```text
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"
```

`/api/health` reported the expected local read-only posture:

```text
status=ok
checks.default_book.exists=true
checks.default_book.readable=true
checks.writes_enabled=false
checks.cors.risk_level=ok
```

## API smoke evidence

```text
read-only API smoke: target=http://localhost:8080/api
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

Additional disabled write probe:

```text
DELETE disabled-write probe status=403 body={"detail":"GnuCash writes are disabled. MVP v0.1 is read-only by default."}
```

## Browser/UI dogfood evidence

```text
read-only browser dogfood: target=http://localhost:8080
fixture: filename=main.gnucash.sqlite sha256=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
ok: mobile_viewport: 320x720
ok: login_page: loaded
ok: protected_redirect: dashboard redirected to login
ok: login: authenticated; auth cookie not readable from document.cookie
ok: mobile_no_overflow: dashboard: scrollWidth=320 clientWidth=320
ok: dashboard: /dashboard loaded; write UI hidden
ok: mobile_no_overflow: accounts: scrollWidth=320 clientWidth=320
ok: accounts: /accounts loaded; write UI hidden
ok: mobile_no_overflow: books: scrollWidth=320 clientWidth=320
ok: books: /books loaded; write UI hidden
ok: mobile_no_overflow: scheduled: scrollWidth=320 clientWidth=320
ok: scheduled: /scheduled loaded; write UI hidden
ok: mobile_no_overflow: account_detail: scrollWidth=320 clientWidth=320
ok: account_detail: first account detail loaded
ok: mobile_no_overflow: transactions_filters: scrollWidth=320 clientWidth=320
ok: transactions_filters: filtered transactions page loaded; export link preserved query
ok: mobile_no_overflow: transaction_detail: scrollWidth=320 clientWidth=320
ok: transaction_detail: first transaction detail loaded
ok: csv_export: status=200 total=0 truncated=false
ok: no_artifacts: no screenshots/downloads/CSV files written
PASS: read-only browser dogfood completed
```

Covered paths:

- Login page and authenticated login.
- Protected dashboard redirect to login.
- Dashboard.
- Accounts.
- Books.
- Scheduled transactions.
- Account detail.
- Transaction filters.
- Transaction detail.
- CSV export through authenticated browser/proxy fetch.
- Mobile-width horizontal-overflow checks on read-only paths.

## Acceptance criteria result

- Docker Compose config/startup: pass.
- API smoke through health, login/auth, books, accounts, transactions, transaction detail, CSV export, reports summary: pass.
- Browser dogfood through login, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV export: pass.
- Hidden write UI checks: pass.
- Disabled validate/create/patch/delete write probes: pass.
- No-artifact checks: pass.
- Sensitive tracked-file hygiene: pass.

## Limitations

- This is synthetic/disposable dogfood only.
- No safe copied personal-book path was explicitly provided for this phase, so the optional copied-book dogfood path was not run.
- This is local pre-alpha evidence, not a production-readiness claim and not a security audit.
- This does not broaden GnuCash compatibility claims beyond existing synthetic/disposable fixture evidence.
- This does not publish or authorize a release; Phase 10 remains a separate release gate.

## Verification commands

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ADMIN_USERNAME=admin ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose up -d --build
SMOKE_API_BASE_URL=http://localhost:8080/api SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-api-smoke.py
SMOKE_WEB_BASE_URL=http://localhost:8080 SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --fixture-path data/books/main.gnucash.sqlite
# manual DELETE disabled-write probe: passed with HTTP 403
# no raw screenshots/csv/backups found in repo root/data backup paths
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose down
```

## Safety

- `GNUCASH_WRITES_ENABLED=false` was runtime-verified and remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- GnuCash Desktop remains the authoritative editor.
- Frontend still accesses GnuCash data only through the backend API.
- No screenshots, raw CSV exports, app DBs, GnuCash books, backups, `.env`, secrets, tokens, certs, keys, private paths, account names from real data, memos, amounts from real data, or personal financial data were committed.
