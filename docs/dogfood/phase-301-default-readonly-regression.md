# Phase 301 default-read-only regression dogfood

Status: PASS

## Scope

Phase 301 verified the Docker/Caddy default read-only path after the Phase 294 owner CREATE-to-PATCH evidence and Cycle 1 release/no-release documentation work.

The run used only the committed synthetic fixture copied to the ignored runtime book path:

- Source fixture: `apps/api/tests/fixtures/test-book.gnucash.sqlite`
- Runtime book filename: `main.gnucash.sqlite`
- Fixture/runtime SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`

No real/private/original/only-copy book was used. No screenshots, CSV files, raw payloads, app DBs, books, backups, or private financial artifacts are part of this report.

## Runtime posture

Docker Compose was run with documented dummy/local values:

- `JWT_SECRET=dummy-validation-secret`
- `APP_ADMIN_PASSWORD` set to a dummy local smoke password
- `APP_DATABASE_URL=sqlite:////data/app/phase301-app.db`
- `GNUCASH_WRITES_ENABLED=false`
- `APP_ENV=development`
- `ORIGIN=http://localhost:8080`

Health response confirmed:

- API status `ok`
- default book present and readable
- app metadata DB reachable
- `writes_enabled=false`
- first-run write-mode check reported GnuCash writes disabled

## API dogfood

Command:

```bash
SMOKE_ADMIN_PASSWORD='<dummy>' \
SMOKE_API_BASE_URL=http://localhost:8080/api \
scripts/smoke/read-only-api-smoke.py
```

Result: PASS.

Covered checks:

- API health
- login
- `/auth/me`
- default book discovery via `/books` and `/books/{id}`
- accounts endpoint
- transactions endpoint
- transaction detail endpoint
- CSV export endpoint and headers
- reports summary endpoint
- scheduled transactions endpoint
- write-alpha audit summary endpoint
- disabled `POST /transactions/validate` returned 403
- disabled `POST /transactions` returned 403
- disabled `PATCH /transactions/{transaction_id}` returned 403
- disabled `DELETE /transactions/{transaction_id}` returned 403

## Browser/UI dogfood

Command:

```bash
SMOKE_ADMIN_PASSWORD='<dummy>' \
SMOKE_WEB_BASE_URL=http://localhost:8080 \
scripts/smoke/read-only-browser-dogfood.py \
  --base-url http://localhost:8080 \
  --fixture-path data/books/main.gnucash.sqlite \
  --viewport-width 320 \
  --viewport-height 720
```

Result: PASS.

Covered checks:

- login page loaded
- protected dashboard redirected to login before authentication
- valid login reached dashboard
- `document.cookie` did not expose the `access_token` auth cookie
- dashboard loaded with write UI hidden
- accounts page loaded with write UI hidden
- books page loaded with write UI hidden
- scheduled page loaded with write UI hidden
- first account detail loaded
- filtered transactions page loaded
- CSV export link preserved the active filter query
- first transaction detail loaded
- browser-side CSV fetch returned 200 with expected header and export limit
- no screenshots, downloads, or CSV files were written
- mobile 320px viewport had no horizontal overflow on checked routes

## Safety conclusion

Phase 301 passed. Default read-only mode remains healthy with `GNUCASH_WRITES_ENABLED=false`; write UI remained hidden; disabled validate/create/PATCH/DELETE probes returned 403; the auth cookie was not visible to browser JavaScript; and no committed artifact contains private financial data or runtime evidence.
