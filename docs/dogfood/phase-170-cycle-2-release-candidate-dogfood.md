# Phase 170 — Cycle 2 release-candidate synthetic dogfood

Date: 2026-05-20
Status: PASS — synthetic/disposable dogfood passed after cycle 2 phases 162–169
Starting HEAD: `309526c`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 9/10 only)

## Summary

Phase 170 reran the local Docker/Caddy read-only dogfood pass after the cycle 2 read-only changes through Phase 169.

Result: PASS on synthetic/disposable data. Docker Compose validation, runtime `/api/health`, read-only API smoke, headless browser dogfood at 320x720 and 1280x900, hidden write UI checks, disabled validate/create/patch/delete write probes, no-artifact checks, and sensitive tracked-file hygiene passed with `GNUCASH_WRITES_ENABLED=false`.

No release, tag, package, image, production deployment, write-alpha expansion, private directory search, copied-book run, screenshot, raw CSV export, app DB, GnuCash book, backup, `.env`, token, key, cert, private path, or real/private financial data was committed.

## Runtime setup

- Deployment: local Docker Compose through Caddy.
- Proxy URL: `http://localhost:8080`.
- API smoke URL: `http://localhost:8080/api`.
- Runtime fixture: ignored local copy at `data/books/main.gnucash.sqlite`, removed after the smoke.
- Source class: committed synthetic/disposable fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Runtime fixture filename recorded only as `main.gnucash.sqlite` in dogfood output.
- Runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- Runtime writes: `GNUCASH_WRITES_ENABLED=false`.
- Browser: headless Chromium via Chrome DevTools Protocol at 320x720 and 1280x900 viewports.
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
health status= ok
default_book.exists= True
default_book.readable= True
writes_enabled= False
cors.risk_level= ok
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
ok: delete endpoint is write-disabled
PASS: read-only API smoke checks completed
```

## Browser/UI dogfood evidence

Mobile/narrow viewport:

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

Desktop-width viewport:

```text
read-only browser dogfood: target=http://localhost:8080
fixture: filename=main.gnucash.sqlite sha256=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
ok: mobile_viewport: 1280x900
ok: login_page: loaded
ok: protected_redirect: dashboard redirected to login
ok: login: authenticated; auth cookie not readable from document.cookie
ok: mobile_no_overflow: dashboard: scrollWidth=1280 clientWidth=1280
ok: dashboard: /dashboard loaded; write UI hidden
ok: mobile_no_overflow: accounts: scrollWidth=1280 clientWidth=1280
ok: accounts: /accounts loaded; write UI hidden
ok: mobile_no_overflow: books: scrollWidth=1280 clientWidth=1280
ok: books: /books loaded; write UI hidden
ok: mobile_no_overflow: scheduled: scrollWidth=1280 clientWidth=1280
ok: scheduled: /scheduled loaded; write UI hidden
ok: mobile_no_overflow: account_detail: scrollWidth=1280 clientWidth=1280
ok: account_detail: first account detail loaded
ok: mobile_no_overflow: transactions_filters: scrollWidth=1280 clientWidth=1280
ok: transactions_filters: filtered transactions page loaded; export link preserved query
ok: mobile_no_overflow: transaction_detail: scrollWidth=1280 clientWidth=1280
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
- Mobile and desktop-width horizontal-overflow checks on read-only paths.

## Acceptance criteria result

- Docker Compose config/startup: pass.
- `/api/health` with default book mounted and writes disabled: pass.
- API smoke through health, login/auth, books, accounts, transactions, transaction detail, CSV export, reports summary: pass.
- Browser dogfood through login, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV export: pass at 320x720 and 1280x900.
- Hidden write UI checks: pass.
- Disabled validate/create/patch/delete write probes: pass through the API smoke helper.
- No-artifact checks: pass.
- Sensitive tracked-file hygiene: pass.

## Limitations

- This is synthetic/disposable dogfood only.
- No safe copied personal-book path was explicitly provided for this phase, so the optional copied-book dogfood path was not run.
- This is local pre-alpha evidence, not a production-readiness claim and not a security audit.
- This does not broaden GnuCash compatibility claims beyond existing synthetic/disposable fixture evidence.
- This does not publish or authorize a release; phase 10 remains a separate release gate.

## Verification commands

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ADMIN_USERNAME=admin ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose up -d --build
SMOKE_API_BASE_URL=http://localhost:8080/api SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-api-smoke.py
SMOKE_WEB_BASE_URL=http://localhost:8080 SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --fixture-path data/books/main.gnucash.sqlite --viewport-width 320 --viewport-height 720
SMOKE_WEB_BASE_URL=http://localhost:8080 SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --fixture-path data/books/main.gnucash.sqlite --viewport-width 1280 --viewport-height 900
# no raw screenshots/csv/backups found outside allowed docs/images
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose down
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
# sensitive tracked-file hygiene scan
```

## Safety

- `GNUCASH_WRITES_ENABLED=false` was runtime-verified and remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- GnuCash Desktop remains the authoritative editor.
- Frontend still accesses GnuCash data only through the backend API.
- No screenshots, raw CSV exports, app DBs, GnuCash books, backups, `.env`, secrets, tokens, certs, keys, private paths, account names from real data, memos, amounts from real data, or personal financial data were committed.
