# Phase 139 — Synthetic dogfood refresh

Date: 2026-05-19
Status: passed on generated/disposable data
Related roadmap item: roadmap phase 7 / project phase 139

## Summary

Phase 139 reran a full local Docker/Caddy synthetic dogfood pass after the Phase 133–138 read-only UX, docs, compatibility, and deployment-hardening work.

Result: core read-only API and browser/UI paths passed locally with `GNUCASH_WRITES_ENABLED=false`. The pass used only the committed synthetic/disposable fixture copied into ignored runtime data. No release, tag, publication, write-alpha expansion, screenshots, raw CSV exports, app DBs, GnuCash books, backups, `.env`, tokens, keys, private paths, or real/private financial data were committed.

## Runtime setup

- Deployment: local Docker Compose through Caddy.
- Proxy URL: `http://127.0.0.1:8080`.
- Runtime fixture: ignored local copy at `data/books/main.gnucash.sqlite`.
- Source class: committed synthetic/disposable fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Runtime fixture filename recorded only as `main.gnucash.sqlite` in script output.
- Runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- Runtime writes: `GNUCASH_WRITES_ENABLED=false`.
- Web internal API URL: `http://api:8000`.
- Browser: headless Chromium via Chrome DevTools Protocol.
- Browser origin used for SvelteKit CSRF safety: `ORIGIN=http://127.0.0.1:8080`.

The ignored local `data/app/app.db` had a pre-existing admin credential from an earlier run, so the disposable smoke runtime was reset to seed the requested dummy admin password. After Docker was stopped, the pre-existing ignored app DB was restored from a temporary backup outside git. This did not affect tracked files and did not add any app DB artifact to git.

## Docker/API evidence

Docker Compose config validation passed with safe dummy secrets and writes disabled:

```text
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy GNUCASH_WRITES_ENABLED=false docker compose config --quiet
# passed
```

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
read-only API smoke: target=http://127.0.0.1:8080/api
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

Passed browser checks:

```text
read-only browser dogfood: target=http://127.0.0.1:8080
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

Covered UI paths:

- Login page and authenticated login.
- Protected dashboard redirect to login.
- Dashboard.
- Accounts.
- Books.
- Scheduled transactions.
- Account detail.
- Transactions list with filters.
- Transaction detail.
- CSV export through authenticated browser/proxy fetch.

Write UI check:

- The browser dogfood script checked dashboard, accounts, books, scheduled, and filtered transactions pages for unexpected `New transaction` write UI text.
- All checked pages reported write UI hidden while `GNUCASH_WRITES_ENABLED=false`.
- API write probes for validate/create/patch returned disabled-write `403` responses.

## Operational findings

- First API smoke attempt failed because a pre-existing ignored local `data/app/app.db` did not match the requested dummy admin password. Root cause was local runtime state, not application behavior. The dogfood runtime was safely reset to a disposable app DB for the pass, then the previous ignored app DB was restored after Docker shutdown.
- First browser attempt failed with SvelteKit `Cross-site POST form submissions are forbidden` because the container had been started with `ORIGIN=http://localhost:8080` while the dogfood target was `http://127.0.0.1:8080`. Restarting with `ORIGIN=http://127.0.0.1:8080` resolved the local environment mismatch. No product code change was required.

## Acceptance criteria result

- Docker/Caddy starts against synthetic/disposable data: pass.
- Full read-only API smoke: pass.
- Full browser dogfood: pass.
- Login, dashboard, accounts, books, scheduled, transactions, filters, account detail, transaction detail, and CSV export: pass.
- Write UI hidden/disabled with `GNUCASH_WRITES_ENABLED=false`: pass.
- Redacted evidence documented: pass.

## Limitations

- This is synthetic/disposable dogfood only, not personal-book dogfood.
- This is local pre-alpha evidence, not a production-readiness claim and not a security audit.
- This does not broaden GnuCash compatibility claims beyond existing synthetic fixture evidence.
- This does not publish or prepare a release by itself.

## Safety

- `GNUCASH_WRITES_ENABLED=false` was runtime-verified and remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- GnuCash Desktop remains the authoritative editor.
- Frontend still accesses GnuCash data only through the backend API.
- No screenshots, CSV exports, app DBs, GnuCash books, backups, `.env`, secrets, tokens, certs, keys, private paths, account names from real data, memos, amounts from real data, or personal financial data were committed.

## Verification commands

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy GNUCASH_WRITES_ENABLED=false docker compose config --quiet
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy GNUCASH_WRITES_ENABLED=false API_INTERNAL_URL=http://api:8000 ORIGIN=http://127.0.0.1:8080 docker compose up -d --build
# passed

APP_ADMIN_PASSWORD=dummy SMOKE_ADMIN_PASSWORD=dummy SMOKE_API_BASE_URL=http://127.0.0.1:8080/api scripts/smoke/read-only-api-smoke.py
# passed

SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --fixture-path data/books/main.gnucash.sqlite
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose down
# passed
```
