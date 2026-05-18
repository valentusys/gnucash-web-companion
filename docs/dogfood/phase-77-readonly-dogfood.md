# Phase 77 — Read-only Dogfood on Copied/Disposable GnuCash Book

Date: 2026-05-18

## Summary

Phase 77 produced a real local Docker dogfood result against a copied/disposable GnuCash SQL book. The backend/API read-only path worked and write endpoints were disabled at runtime. Browser/UI dogfood was blocked by a Docker web UI redirect loop on `/login`, tracked as GitHub #37.

Release verdict: not ready for `v0.1.0-readonly` until the web UI login redirect loop is fixed and a browser-level copied/disposable-book dogfood pass is rerun. The API-level dogfood evidence is positive but not sufficient for release.

## Dogfood environment and commit

- Repository: `valentusys/gnucash-web-companion`
- Local path: `/home/val/gnucash-web-companion`
- Branch: `main`
- Starting commit: `12092a7e4e045d884f7f2f0b7e05bf3d2c5d4e02` (`12092a7`)
- Runtime: Docker Engine 29.5.0, Docker Compose v5.1.3
- Compose files:
  - `docker-compose.yml`
  - temp override outside git: `/tmp/gnucash-web-companion-phase77/docker-compose.phase77.yml`
- Temp runtime workdir outside git: `/tmp/gnucash-web-companion-phase77`
- Proxy dogfood URL: `http://127.0.0.1:18080`
- API base URL: `http://127.0.0.1:18080/api`
- No `.env`, real book, app DB, backup, screenshot, token, or CSV export was committed.

## Copied/disposable book source class

No safe real personal GnuCash SQL book was discoverable under `/home/val` during this phase. To avoid touching real data or guessing private locations, Phase 77 used the existing committed synthetic/disposable SQL fixture as the copied/disposable dogfood book:

- Source class: committed synthetic/disposable fixture, not real personal data.
- Source file: `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Runtime copy: `/tmp/gnucash-web-companion-phase77/data/books/main.gnucash.sqlite`.
- Runtime copy SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.

This means the phase is a valid real Docker/runtime dogfood pass on a disposable SQL book, but partial against the requested “copied real book” target. The remaining real copied-book evidence requirement should stay tracked until a safe real copied book is explicitly available.

## PM scenario

Dogfood scenario:

1. Start Docker Compose locally against a copied/disposable GnuCash SQL SQLite book.
2. Confirm runtime config keeps `GNUCASH_WRITES_ENABLED=false`.
3. Confirm `/api/health` reports app DB reachable, default book present/readable, and writes disabled.
4. Log in as the local bootstrap admin.
5. Exercise read-only MVP flows:
   - dashboard/reports summary;
   - accounts list;
   - account detail;
   - account transaction list;
   - transactions list;
   - transaction detail;
   - search/filter;
   - CSV export.
6. Probe write endpoints and confirm disabled-write 403 responses.
7. Attempt browser/UI dogfood for login/dashboard/accounts/transactions.

## Pass/fail criteria

Pass criteria:

- Docker deployment starts with a copied/disposable SQL book.
- Runtime health is `ok` with `writes_enabled: false`.
- Compose-resolved API and web environments include `GNUCASH_WRITES_ENABLED: "false"`.
- Login succeeds.
- Accounts, account detail, transactions, transaction detail, reports/dashboard-equivalent summary, search/filter, and CSV export return expected read-only responses.
- Validate/create/patch write endpoints return read-only/write-disabled 403 responses.
- Browser can load `/login`, authenticate, and navigate the main read-only screens without a blocker.

Fail/blocker criteria:

- Any real/original GnuCash book would need to be touched.
- Runtime writes are enabled or write probes are not blocked.
- Docker cannot run.
- Login or core read-only flows fail.
- Browser/UI cannot be used for normal dogfood.

## GNUCASH_WRITES_ENABLED=false proof

Compose config proof:

```text
$ docker compose --env-file /tmp/gnucash-web-companion-phase77/phase77.env -f docker-compose.yml -f /tmp/gnucash-web-companion-phase77/docker-compose.phase77.yml config | grep -E 'GNUCASH_WRITES_ENABLED'
      GNUCASH_WRITES_ENABLED: "false"
      GNUCASH_WRITES_ENABLED: "false"
```

Health endpoint proof:

```json
{
  "status": "ok",
  "service": "api",
  "checks": {
    "app_database": {
      "backend": "sqlite",
      "database_name": "app.db",
      "configured": true,
      "reachable": true,
      "message": "App metadata database is reachable."
    },
    "default_book": {
      "configured": true,
      "exists": true,
      "readable": true,
      "filename": "main.gnucash.sqlite",
      "parent_exists": true,
      "message": "Default GnuCash book file is present."
    },
    "writes_enabled": false
  }
}
```

Write endpoint probes:

```text
write_disabled: POST /books/1/transactions/validate status= 403 detail= GnuCash writes are disabled. MVP v0.1 is read-only by default.
write_disabled: POST /books/1/transactions status= 403 detail= GnuCash writes are disabled. MVP v0.1 is read-only by default.
write_disabled: PATCH /books/1/transactions/nonexistent status= 403 detail= GnuCash writes are disabled. MVP v0.1 is read-only by default.
```

## Route/API/browser checks attempted

### Docker/runtime

```text
Docker version 29.5.0, build 98f1464
Docker Compose version v5.1.3
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet — passed
```

Compose services after startup:

```text
api: running, healthy
proxy: running
web: running, unhealthy
```

Safe API log snippets:

```text
api-1  | INFO:     Application startup complete.
api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Automated read-only API smoke

Command:

```bash
SMOKE_API_BASE_URL=http://127.0.0.1:18080/api \
SMOKE_ADMIN_PASSWORD=<redacted> \
scripts/smoke/read-only-api-smoke.py
```

Result:

```text
read-only API smoke: target=http://127.0.0.1:18080/api
ok: API health
ok: login
ok: /auth/me
ok: default book discovered via /books and verified at /books/1
ok: accounts endpoint
ok: transactions endpoint
ok: reports summary
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
PASS: read-only API smoke checks completed
```

### Manual API dogfood details

```text
login: ok token_len= 119
book: id= 1 name= main is_default= True
accounts: count= 10 first_names= ['Assets', 'Expenses', 'Income']
account_detail: ok id= 3768edb4158844e9a4091adb3d1199ad name= Assets type= ASSET
transactions: total= 5 returned= 5
transaction_detail: ok id= 89bdbe5a90af4c2fb4fc76b781d4a23b splits= 2
search_filter: query=salary returned= 1 total= 1
account_transactions: returned= 0 total= 0
csv_export: status= 200 content_type= text/csv; charset=utf-8 rows= 2 header= ['id', 'date', 'description', 'amount', 'currency', 'account_id', 'account_name', 'counter_account_name']
```

### Browser/UI dogfood

Attempted:

- `browser_navigate("http://127.0.0.1:18080/login")`
- `browser_navigate("http://localhost:18080/login")`
- terminal curl checks against `/login` and `/`

Result: blocked. `/login` redirects to itself repeatedly:

```text
$ curl -i http://127.0.0.1:18080/login
HTTP/1.1 303 See Other
Location: /login
```

With redirects enabled:

```text
$ curl -L --max-redirs 5 http://127.0.0.1:18080/login
curl: (47) Maximum (5) redirects followed
HTTP/1.1 303 See Other
Location: /login
...
```

Impact: browser dogfood could not proceed to login, dashboard, accounts, account detail, transactions, transaction detail, search/filter UI, or CSV export UI.

## What worked

- Docker API service built and started.
- API container became healthy.
- App metadata DB was reachable.
- Default copied/disposable SQL book was present and readable.
- Runtime `writes_enabled` was false.
- API login worked.
- `/auth/me` worked.
- Book discovery worked.
- Accounts list worked.
- Account detail worked.
- Transactions list worked.
- Transaction detail worked.
- Reports summary worked as dashboard-equivalent API evidence.
- Search/filter worked (`query=salary`).
- CSV export worked and returned `text/csv` with expected header.
- Validate/create/patch write endpoints returned disabled-write 403 before any write was allowed.

## What failed / blockers

1. Web UI login route redirects to itself and prevents browser dogfood.
   - Evidence: `GET /login` returns `303 Location: /login` repeatedly.
   - Web container health status: unhealthy.
   - GitHub issue: #37.
   - Release impact: blocks `v0.1.0-readonly` until fixed and browser dogfood is rerun.
2. No safe real copied personal GnuCash SQL book was discoverable in the local environment.
   - Phase used the committed synthetic/disposable SQL fixture instead.
   - Release impact: API/runtime evidence is useful, but the real copied-book dogfood gate remains only partially satisfied unless PM accepts synthetic/disposable-only evidence.

## Issues created / updated

- Created #37 — Docker web UI redirects `/login` to itself and prevents browser dogfood.
- #25 remains the broader copied/disposable-data runtime smoke/dogfood gate. Phase 77 provides API-level evidence but does not fully close #25 because browser dogfood failed and no safe real copied book was available.

## Release verdict

Not ready for `v0.1.0-readonly`.

Reason:

- The read-only API path works against a copied/disposable SQL book with writes disabled.
- However, the Docker web UI is not usable because `/login` redirects to itself.
- Browser-level dogfood is a release gate for a user-facing read-only web companion.
- The phase also did not use a safe copied real personal book because none was discoverable; it used a synthetic/disposable fixture.

Required next release-unblocking work:

1. Fix #37.
2. Rerun Phase 77-style browser/API dogfood against copied/disposable data.
3. If possible, rerun with an explicitly provided safe copied real SQL book outside git; otherwise record that the release gate is satisfied only by synthetic/disposable fixture evidence if PM accepts that scope.
4. Keep `GNUCASH_WRITES_ENABLED=false` and controlled writes experimental/post-MVP.
