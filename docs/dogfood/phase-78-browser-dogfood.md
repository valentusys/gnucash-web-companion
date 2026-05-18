# Phase 78 — Docker Browser Dogfood after /login Redirect Fix

Date: 2026-05-18

## Summary

Phase 78 fixed release blocker #37 and reran Docker browser/UI dogfood through the Caddy proxy against a copied/disposable GnuCash SQL fixture with `GNUCASH_WRITES_ENABLED=false`.

Result: `/login` no longer redirects to itself, protected routes still redirect unauthenticated users to `/login`, login succeeds in a real headless Chromium browser, and the main read-only UI flows load after authentication. Runtime write endpoints stayed disabled by default.

Release verdict: ready after remaining release-prep fixes, not published in this phase. #37 can be closed as fixed. #25 should remain open until PM accepts this browser dogfood as satisfying the copied/disposable-data gate and/or any remaining release-gate wording is updated. #24 remains open because release notes were not completed in this phase.

## Environment

- Repository: `valentusys/gnucash-web-companion`
- Local path: `/home/val/gnucash-web-companion`
- Starting commit: `0903622` (`docs: add phase 77 dogfood evidence`)
- Runtime workdir outside git: `/tmp/gnucash-web-companion-phase78`
- Runtime book copy: `/tmp/gnucash-web-companion-phase78/data/books/main.gnucash.sqlite`
- Source class: committed synthetic/disposable fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`
- Runtime copy SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`
- Proxy URL: `http://127.0.0.1:18080`
- Browser: headless Chromium via Chrome DevTools Protocol
- No `.env`, real GnuCash book, app DB, backup, token, real screenshot, or raw CSV export was committed.

## Blocker definition

#37 was a Docker web UI blocker: the root SvelteKit layout tried to load authenticated book context for every route, including public `/login`. Without an `access_token` cookie, that layout path called `getAuthToken(cookies)`, which redirects to `/login`. Because the same layout also ran for `/login`, unauthenticated `GET /login` returned `303 Location: /login` repeatedly.

This was not a Caddy proxy rewrite problem: Phase 78 reproduced the loop through Caddy and directly inside the web container.

## Reproduction before fix

Docker was started with a copied/disposable fixture and writes disabled.

Runtime proof before the fix:

```text
Compose config:
GNUCASH_WRITES_ENABLED: "false"
ORIGIN: http://127.0.0.1:18080

/api/health:
status=ok
checks.default_book.exists=true
checks.default_book.readable=true
checks.writes_enabled=false
```

Redirect-loop evidence before the fix:

```text
$ curl -i http://127.0.0.1:18080/login
HTTP/1.1 303 See Other
Location: /login
Via: 1.1 Caddy

$ curl -L --max-redirs 5 http://127.0.0.1:18080/login
curl: (47) Maximum (5) redirects followed
HTTP/1.1 303 See Other
Location: /login
...
```

Direct web-container proof before the fix:

```text
status=303 location=/login
```

## Fix summary

Minimal code changes:

- `apps/web/src/routes/+layout.server.ts`
  - uses hook-provided `locals.authenticated`;
  - returns public unauthenticated layout data for public routes like `/login` without calling `getAuthToken(cookies)`;
  - still resolves token + book context only after authentication.
- `apps/web/scripts/test-auth-routes.mjs`
  - added regression checks that the root layout has a public unauthenticated branch before token lookup and keeps authenticated book-context loading after login.
- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts`
  - added a server-side CSV export proxy for the existing UI link so the browser can use the httpOnly auth cookie server-side and receive CSV from the API through Caddy/web.
  - This fixes the existing CSV export UI dogfood path; it does not add a new export feature or enable writes.

## TDD evidence

Regression tests were added before the fix and failed as expected:

```text
$ cd apps/web && npm run test:auth-routes
AssertionError [ERR_ASSERTION]: root layout must use hook-provided authentication state so public routes like /login can render without an auth cookie
```

After the minimal auth-layout fix and CSV proxy route, the regression checks passed:

```text
$ cd apps/web && npm run test:auth-routes
auth route checks passed
```

Covered by the route checks:

- `/login` can render unauthenticated because root layout has a public unauthenticated branch.
- Protected route behavior still lives in `hooks.server.ts` and redirects unauthenticated protected routes to `/login?next=...`.
- Authenticated layout loads still call `getAuthToken(cookies)` and `getActiveBookContext(fetch, cookies, token)` after login.
- CSV export proxy reads the httpOnly cookie server-side and calls the API with `Authorization: Bearer ...`.

## Docker/browser dogfood after fix

Services after rebuild:

```text
api: running, healthy
web: running, healthy
proxy: running on 127.0.0.1:18080 through Caddy
```

HTTP route checks:

```text
GET /login -> 200 OK
GET /dashboard unauthenticated -> 303 Location: /login?next=%2Fdashboard
```

Headless Chromium dogfood through Caddy:

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

Important browser evidence:

- `document.cookie` was empty after login, which is expected because the auth cookie is httpOnly.
- The authenticated shell displayed `Read-only by default`.
- `new_button_visible=false`, confirming the write UI stayed hidden with `GNUCASH_WRITES_ENABLED=false`.

CSV export reachable from UI route:

```text
GET /books/1/transactions/export?query=salary with authenticated browser cookie
status=200
content_type=text/csv; charset=utf-8
Content-Disposition: attachment; filename="transactions-book1.csv"
csv_rows=2
header=['id', 'date', 'description', 'amount', 'currency', 'account_id', 'account_name', 'counter_account_name']
```

API smoke after fix:

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

Write-disabled runtime probes with valid payloads:

```text
POST /books/1/transactions/validate status=403 detail=GnuCash writes are disabled. MVP v0.1 is read-only by default.
POST /books/1/transactions status=403 detail=GnuCash writes are disabled. MVP v0.1 is read-only by default.
PATCH /books/1/transactions/nonexistent status=403 detail=GnuCash writes are disabled. MVP v0.1 is read-only by default.
```

## Acceptance criteria result

- `/login` loads in Docker through Caddy/proxy: pass.
- Unauthenticated protected pages redirect to `/login`: pass (`/dashboard -> /login?next=%2Fdashboard`).
- `/login` itself does not redirect to itself: pass (`200 OK`).
- After login, dashboard loads: pass.
- Accounts page loads: pass.
- Account detail loads: pass.
- Transactions page loads: pass.
- Transaction detail loads: pass.
- CSV export is reachable from UI route: pass (`/books/1/transactions/export?... -> 200 text/csv`).
- Write UI remains hidden with `GNUCASH_WRITES_ENABLED=false`: pass (`New transaction` not visible in browser dogfood).
- Write API probes still return 403: pass for validate/create/patch with valid payloads.
- No real financial data committed: pass; dogfood used committed synthetic/disposable fixture copied to `/tmp`.
- No release published: pass.

## Limitations

- The dogfood book is the synthetic/disposable fixture copied outside git, not a real personal copied GnuCash book. This matches the safe source class from Phase 77 because no explicitly safe real personal copied SQL book was available locally.
- No release notes were completed in this phase; #24 remains open.
- #25 remains open pending PM/release-gate acceptance of this browser dogfood evidence and release-note completion.

## Checks

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

git diff --check
passed
```
