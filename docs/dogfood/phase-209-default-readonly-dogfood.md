# Phase 209 — default-read-only full dogfood refresh

Date: 2026-05-21
Status: PASS — full default-read-only Docker/Caddy API and browser dogfood completed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 8 only)

## Summary

Phase 209 re-ran the default read-only product path after cycle-1 Phases 202–208 using only the committed synthetic fixture copied into ignored local runtime data.

Result: PASS. Docker Compose config kept `GNUCASH_WRITES_ENABLED=false` for API and web, local Docker/Caddy started against the synthetic runtime copy, read-only API smoke passed, validate/create/PATCH/DELETE write probes returned HTTP 403, browser dogfood passed at `320x720` and `1280x900`, auth cookie was not readable from `document.cookie`, horizontal-overflow checks passed, and the stack was torn down with the ignored runtime book and generated smoke app DB removed.

No write-enabled mode was run. No release/tag/package was published. No real/private/only-copy book, backup, `.env`, screenshot, download, raw CSV export, token, key, cert, private path, account name, memo, amount, or private financial data was committed.

## Runtime setup

- Deployment: local Docker Compose through Caddy.
- Proxy URL: `http://localhost:8080`.
- API smoke URL: `http://localhost:8080/api`.
- Source fixture class: committed synthetic/disposable fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Runtime fixture class: ignored local copy `data/books/main.gnucash.sqlite`, removed after the smoke.
- Runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- App metadata DB class: ignored `data/app/app.db`; a pre-existing ignored local app DB was moved aside before smoke and restored after teardown.
- Runtime writes: `GNUCASH_WRITES_ENABLED=false` only.
- Browser: headless Chromium through Chrome DevTools Protocol at `320x720` and `1280x900` viewports.
- SvelteKit origin: `ORIGIN=http://localhost:8080`.
- Local `.env`: dummy local-only values, removed after teardown and not committed.

## Docker config evidence

```text
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"
```

## API smoke evidence

`read-only-api-smoke.py` was extended in this phase so the full default-read-only smoke now explicitly covers scheduled transaction metadata and the read-only write-alpha audit-summary endpoint in addition to the existing health/login/books/accounts/transactions/details/CSV/reports/write-disabled probes.

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
ok: scheduled transactions endpoint
ok: write-alpha audit summary endpoint
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
ok: delete endpoint is write-disabled
PASS: read-only API smoke checks completed
```

Covered API paths:

- `/api/health`.
- `POST /api/auth/login` and `GET /api/auth/me`.
- `/api/books` and `/api/books/{book_id}`.
- `/api/books/{book_id}/accounts`.
- `/api/books/{book_id}/transactions`.
- `/api/books/{book_id}/transactions/{transaction_id}`.
- `/api/books/{book_id}/transactions/export`.
- `/api/books/{book_id}/reports/summary`.
- `/api/books/{book_id}/scheduled-transactions`.
- `/api/books/{book_id}/write-alpha-audit-summary`.
- disabled-write probes for validate, create, PATCH, and DELETE returning HTTP 403.

## Browser dogfood evidence — mobile `320x720`

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

## Browser dogfood evidence — desktop `1280x900`

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

Covered browser paths:

- Login page.
- Protected dashboard redirect to login.
- Authenticated dashboard.
- Accounts.
- Books.
- Scheduled transactions.
- First account detail.
- Transaction filters with CSV link parity.
- First transaction detail.
- Authenticated CSV fetch without writing a download file.
- Hidden write UI checks.
- Auth cookie no-readability check.
- Horizontal-overflow checks at mobile and desktop widths.

## Teardown and artifact hygiene

After dogfood:

- Docker/Caddy containers and the Compose network were stopped/removed with `docker compose down --remove-orphans`.
- Ignored smoke runtime files were removed: `data/books/main.gnucash.sqlite`, generated `data/app/app.db`, and local `.env`.
- The pre-existing ignored local `data/app/app.db` was restored after the smoke.
- Runtime listing after cleanup showed zero non-placeholder entries under `data/books`, `data/backups`, and `data/locks`; `data/app/app.db` is an ignored pre-existing local artifact and was not staged.
- Browser helper denied downloads and removed its temporary Chromium profile by default.
- No screenshot/download/raw CSV/book/backup/app DB artifact was committed.

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains the default. This phase did not run write-enabled mode, did not use any real/private/only-copy book, did not publish a release/tag, and does not claim production readiness, a security audit, public-internet safety, broad Desktop compatibility, or write safety for real/private books.

## Final repository checks

```text
python3 -m py_compile scripts/smoke/read-only-api-smoke.py
# passed

cd apps/api && pytest -q
# passed: 481 passed; existing piecash/SQLAlchemy/FastAPI warnings only

cd apps/web && npm run check && npm run test:auth-routes && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"

git diff --check
# passed

sensitive tracked-file hygiene scan
# passed
```
