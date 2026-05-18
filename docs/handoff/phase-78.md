# Phase 78 — Fix Docker /login Redirect Loop and Rerun Browser Dogfood

## Status

Complete. Phase 78 was not audit-only: it reproduced #37 in Docker, identified the root cause, added failing regression checks first, fixed the minimal auth-layout cause, repaired the existing CSV export UI route needed for dogfood, reran Docker browser/UI dogfood through Caddy against a copied/disposable SQL fixture, verified writes stayed disabled, updated GitHub issues, and pushed the phase commit.

No release was published. Writes were not enabled. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DB, backups, screenshots with real financial data, secrets, or tokens were committed.

## PM report

### Precise blocker

GitHub #37 was a Docker web UI blocker: unauthenticated `GET /login` returned `303 Location: /login` repeatedly, so the browser could not reach the login page. The root cause was not Caddy. The root SvelteKit layout loaded authenticated book context for every route, including `/login`; with no `access_token` cookie it called `getAuthToken(cookies)`, which redirects to `/login`, causing `/login` to redirect to itself.

### Success criteria

Phase 78 success criteria were:

- `/login` loads in Docker through Caddy/proxy.
- Unauthenticated protected pages redirect to `/login`.
- `/login` itself does not redirect to itself.
- After login, dashboard loads.
- Accounts page loads.
- Account detail loads.
- Transactions page loads.
- Transaction detail loads.
- CSV export is reachable from UI or documented route.
- Write UI remains hidden with `GNUCASH_WRITES_ENABLED=false`.
- Write API probes still return 403.
- No real financial data is committed.
- No release is published.

All criteria passed using a copied/disposable synthetic SQL fixture in `/tmp/gnucash-web-companion-phase78`.

### Release blockers

- #37: fixed and closed/updated as completed by this phase.
- #25: keep open until the release gate/PM accepts the Phase 78 browser dogfood evidence as satisfying the copied/disposable-data dogfood gate.
- #24: remains open; Phase 78 did not complete v0.1.0-readonly release notes.

Release verdict: ready after remaining release-prep fixes, not ready to publish until #24 is completed and #25 is accepted/closed. No v0.1 release/tag was published in this phase.

## Engineer report

### Reproduction before fix

Runtime setup:

- Workdir outside git: `/tmp/gnucash-web-companion-phase78`.
- Runtime book copy: `/tmp/gnucash-web-companion-phase78/data/books/main.gnucash.sqlite`.
- Source fixture: `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Runtime copy SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- Proxy URL: `http://127.0.0.1:18080`.
- Runtime writes: `GNUCASH_WRITES_ENABLED=false` in Compose config and `/api/health`.

Pre-fix evidence:

```text
GET /login -> HTTP/1.1 303 See Other
Location: /login

curl -L --max-redirs 5 /login -> curl: (47) Maximum (5) redirects followed
Direct web container GET http://localhost:3000/login -> status=303 location=/login
```

### Root cause

`hooks.server.ts` only protects `/dashboard`, `/accounts`, `/books`, and `/transactions`, so `/login` was not protected by the hook. The redirect came from `src/routes/+layout.server.ts`: root layout always called `getAuthToken(cookies)` and `getActiveBookContext(...)` before returning layout data. Root layout also runs for `/login`, so unauthenticated `/login` hit `getAuthToken()` and redirected to `/login`.

### Fix

Changed `apps/web/src/routes/+layout.server.ts` so it:

- uses `locals.authenticated` set by `hooks.server.ts`;
- returns public unauthenticated layout data for public routes before reading the required auth token;
- only resolves token and book context after authentication.

Also fixed the existing CSV export UI dogfood route by adding `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts`, a server-side proxy that reads the httpOnly auth cookie, calls the API export endpoint with a bearer token, and streams CSV back to the browser. This keeps the existing export feature usable from the UI without exposing auth tokens to browser storage.

### Tests

TDD RED evidence:

```text
cd apps/web && npm run test:auth-routes
AssertionError [ERR_ASSERTION]: root layout must use hook-provided authentication state so public routes like /login can render without an auth cookie
```

GREEN evidence:

```text
cd apps/web && npm run test:auth-routes
auth route checks passed
```

Regression coverage added in `apps/web/scripts/test-auth-routes.mjs`:

- public unauthenticated root layout branch exists before token lookup;
- authenticated root layout still resolves token + book context after login;
- protected route redirect checks remain in `hooks.server.ts`;
- CSV export proxy reads httpOnly auth cookie server-side and calls API with bearer auth.

### Docker/browser dogfood result

After rebuild, services were healthy:

```text
api: Up (healthy)
web: Up (healthy)
proxy: Up on 127.0.0.1:18080
```

HTTP checks:

```text
GET /login -> 200 OK
GET /dashboard unauthenticated -> 303 Location: /login?next=%2Fdashboard
```

Headless Chromium browser dogfood through Caddy:

```text
login_page: http://127.0.0.1:18080/login Sign in — GnuCash Web Companion true
protected_redirect: http://127.0.0.1:18080/login?next=%2Fdashboard
after_login: http://127.0.0.1:18080/dashboard Dashboard — GnuCash Web Companion true
dashboard: http://127.0.0.1:18080/dashboard true
accounts: http://127.0.0.1:18080/accounts true
account_detail: http://127.0.0.1:18080/accounts/3768edb4158844e9a4091adb3d1199ad true
transactions: http://127.0.0.1:18080/transactions true new_button_visible= false
csv_export_link: /books/1/transactions/export
transaction_detail: http://127.0.0.1:18080/transactions/89bdbe5a90af4c2fb4fc76b781d4a23b true
```

CSV export route reached from the UI link:

```text
GET /books/1/transactions/export?query=salary
status=200
content_type=text/csv; charset=utf-8
csv_rows=2
header=['id', 'date', 'description', 'amount', 'currency', 'account_id', 'account_name', 'counter_account_name']
```

Runtime write-disabled probes:

```text
POST /books/1/transactions/validate status=403 detail=GnuCash writes are disabled. MVP v0.1 is read-only by default.
POST /books/1/transactions status=403 detail=GnuCash writes are disabled. MVP v0.1 is read-only by default.
PATCH /books/1/transactions/nonexistent status=403 detail=GnuCash writes are disabled. MVP v0.1 is read-only by default.
```

Browser UI confirmed the write entry point stayed hidden with writes disabled:

```text
new_button_visible= false
```

### Checks

Required checks passed:

```text
cd apps/api && pytest -q
282 passed, 27 warnings

cd apps/web && npm run check
svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
auth route checks passed

cd apps/web && npm run build
built successfully

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
passed

Docker runtime smoke/browser dogfood through Caddy/proxy
passed

git diff --check
passed
```

### Files changed

- `apps/web/src/routes/+layout.server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts`
- `docs/dogfood/phase-78-browser-dogfood.md`
- `docs/handoff/phase-78.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## Safety confirmation

- `GNUCASH_WRITES_ENABLED=false` remains the default and was runtime-verified.
- Controlled writes remain experimental/post-MVP and disabled by default.
- Write UI remains hidden with writes disabled.
- Write API probes return 403 with valid payloads.
- No release/tag was published.
- No real financial data, real GnuCash books, `.env`, app DB, backup, screenshot with real financial data, secrets, tokens, certs, or keys were committed.
