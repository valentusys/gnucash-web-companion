# Phase 11 handoff — Integration QA and MVP hardening

Date: 2026-05-16

## Scope

Phase 11 focused on integration QA, security sanity, and MVP hardening for the read-only pre-alpha. No product features or write operations were added.

## Changes made

### Fresh deployment access seed

A fresh single-book deployment now grants the first admin user `owner` access to the seeded default book.

Files:

- `apps/api/app/services/seed.py`
- `apps/api/app/main.py`
- `apps/api/tests/test_seed.py`

Reason: previous bootstrap could create both an admin user and a default book, but `/books` returned an empty list because there was no `UserBookAccess` row.

### JWT secret hardening

`JWT_SECRET` is now required for usable auth.

Files:

- `apps/api/app/config.py`
- `apps/api/app/services/auth.py`
- `apps/api/app/routers/auth.py`
- `apps/api/tests/test_auth.py`
- `.env.example`
- `docker-compose.yml`
- `.github/workflows/ci.yml`

Behavior:

- Empty or known placeholder secrets are rejected.
- `/auth/login` and `/auth/me` return controlled `503` when JWT signing is not configured safely.
- `docker-compose.yml` requires `JWT_SECRET` to be set.
- CI compose validation injects a temporary validation-only secret.

### SQLite runtime hardening

SQLite app metadata connections now use `check_same_thread=False`.

File:

- `apps/api/app/database.py`

Reason: FastAPI can enter/exit sync DB dependencies in worker threads while async route handlers use the yielded session on the event-loop thread. Runtime curl QA previously reproduced a SQLite thread `500`; this setting fixes the runtime issue.

### Root route integration

Opening `http://localhost:8080/` now redirects:

- unauthenticated users → `/login`
- authenticated users → `/dashboard`

File:

- `apps/web/src/routes/+page.server.ts`

### Controlled frontend error page

Added a root SvelteKit error page for controlled book/API errors.

File:

- `apps/web/src/routes/+error.svelte`

This keeps missing-book and unknown-id states understandable instead of showing the default framework error page.

## Backend QA

Local backend checks:

```text
python -m pytest tests/ -q
135 passed, 1 skipped, 1 warning
```

Runtime curl QA with a deliberately missing GnuCash book:

- `GET /health` → `200`
- `GET /books` without auth → `401`
- `POST /auth/login` → `200`
- `GET /auth/me` → `200`
- `GET /books` → one default book visible to admin
- `GET /books/{book_id}/accounts` → controlled `404` for missing book
- `GET /books/{book_id}/transactions` → controlled `404` for missing book
- `GET /books/{book_id}/reports/summary` → controlled `404` for missing book
- `GET /books/999/accounts` → `404`
- `GET /books/{book_id}/transactions?limit=501` → `422`, pagination max enforced
- `POST/PUT/PATCH/DELETE /books/{book_id}/accounts` → `405`

No GnuCash write endpoints are registered in the API route table. POST routes are limited to auth login/logout.

## Frontend QA

Frontend checks:

```text
npm run check
npm run test:auth-routes
npm run build
```

All passed.

Runtime curl QA through SvelteKit dev server on `http://127.0.0.1:8080`:

- `GET /` → `303 /login`
- `GET /login` renders sign-in page
- `POST /login` sets `access_token` cookie with `HttpOnly`
- authenticated `GET /dashboard` → `200`
- authenticated `GET /accounts` with missing book → controlled error page
- authenticated `GET /transactions` with missing book → controlled error page
- `POST /logout` → `303 /login`

Headless Chromium smoke test:

- `360px` login page rendered successfully.

The Hermes browser tool timed out in this environment, so deeper visual/browser interaction was approximated with curl plus headless Chromium DOM smoke testing.

## Security sanity

Checked:

- no tracked `.env`, secrets, credentials, GnuCash book files, or backups
- no `localStorage` / `sessionStorage` usage outside theme persistence files
- auth token remains in `HttpOnly` cookie
- `JWT_SECRET` required for auth
- no telemetry added
- no write endpoints added
- no financial API data stored in browser storage

## Docker Compose status

`docker` is not installed on this machine, so `docker compose up` could not be executed locally.

Hardening done for Compose:

- `docker-compose.yml` now requires `JWT_SECRET`
- CI compose validation runs with a temporary validation-only secret

Known limitation: full runtime Docker Compose startup still needs verification on a host with Docker installed.

## Known limitations after Phase 11

- Project remains pre-alpha / MVP in progress.
- Use a test copy of the GnuCash book only.
- Missing or unreadable GnuCash book surfaces controlled errors; it does not fake data.
- No writes to GnuCash are implemented.
- No true collaborative multi-user accounting.
- Multi-currency reports aggregate only base-currency values; no conversion is performed.
- Browser visual QA was limited by local tool timeout; curl/headless Chromium checks were used instead.
- Docker Compose runtime startup was not locally tested because Docker is unavailable on this host.

## Next recommended step

Run Docker Compose on a Docker-capable host with:

```bash
cp .env.example .env
# edit .env: set JWT_SECRET, APP_ADMIN_PASSWORD or APP_ADMIN_PASSWORD_HASH,
# and GNUCASH_DEFAULT_BOOK_PATH pointing at a test copy.
docker compose up --build
```

Then repeat the Phase 11 user flow against `http://localhost:8080` with a real test GnuCash SQL book.
