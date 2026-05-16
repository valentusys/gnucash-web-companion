# Phase 4 Handoff — Authorization Foundation

## Status

Complete.

Phase 4 adds MVP authentication for one bootstrap admin user, backend JWT auth endpoints, and SvelteKit protected routes using an httpOnly cookie. It does not add registration, OAuth, complex RBAC UI, accounts, transactions, or GnuCash write functionality.

## Scope delivered

Backend:

- Added password hashing with bcrypt.
- Added JWT access token creation/validation with `JWT_SECRET` and configurable expiration.
- Added bootstrap admin seeding when the users table is empty.
- Added `get_current_user` dependency.
- Added auth endpoints:
  - `POST /auth/login`
  - `GET /auth/me`
  - `POST /auth/logout`

Frontend:

- Added `/login` page with mobile-friendly form and clear error messages.
- Added `/dashboard` placeholder route.
- Added `src/hooks.server.ts` route guard for protected routes.
- Added `/logout` server endpoint/action target.
- Added logout button to the authenticated app shell.
- Stored access token only in an httpOnly cookie named `access_token`.
- Added a static auth-route test to assert protected route/cookie/localStorage constraints.

Docs/config:

- Updated `.env.example`.
- Updated `docker-compose.yml` env passthrough.
- Updated `docs/DEVELOPMENT.md` env list.
- Created this handoff document.

## Files changed

Backend:

- `apps/api/app/config.py`
- `apps/api/app/main.py`
- `apps/api/app/routers/auth.py`
- `apps/api/app/services/auth.py`
- `apps/api/pyproject.toml`
- `apps/api/requirements.txt`
- `apps/api/tests/test_auth.py`

Frontend:

- `apps/web/src/app.d.ts`
- `apps/web/src/hooks.server.ts`
- `apps/web/src/routes/+layout.server.ts`
- `apps/web/src/routes/+layout.svelte`
- `apps/web/src/routes/+page.svelte`
- `apps/web/src/routes/login/+page.server.ts`
- `apps/web/src/routes/login/+page.svelte`
- `apps/web/src/routes/dashboard/+page.svelte`
- `apps/web/src/routes/logout/+server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `apps/web/package.json`

Config/docs:

- `.env.example`
- `docker-compose.yml`
- `docs/DEVELOPMENT.md`
- `docs/handoff/phase-4.md`

## Backend behavior

### `POST /auth/login`

Request:

```json
{
  "username": "admin",
  "password": "..."
}
```

Response:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "display_name": "Admin"
  }
}
```

### `GET /auth/me`

Requires:

```http
Authorization: Bearer <token>
```

Returns the current user or `401` for missing/invalid/expired tokens.

### `POST /auth/logout`

Returns:

```json
{"status":"ok"}
```

JWT logout is stateless. The frontend completes logout by deleting the httpOnly cookie.

## Admin bootstrap

When the users table is empty, startup attempts to seed one admin user from env:

- `APP_ADMIN_USERNAME`, default `admin`
- `APP_ADMIN_PASSWORD_HASH`, preferred
- `APP_ADMIN_PASSWORD`, plaintext bootstrap fallback

Production should prefer `APP_ADMIN_PASSWORD_HASH`. If `APP_ADMIN_PASSWORD` is used, it is hashed before storage, but the plaintext value exists in process/container env and is only intended for development or first bootstrap.

If neither password source is configured, startup logs a controlled warning and skips admin seeding.

## Frontend auth model

The browser never stores the JWT in `localStorage` or `sessionStorage`.

Flow:

1. `/login` server action posts credentials to FastAPI `POST /auth/login` through `API_INTERNAL_URL`.
2. On success, SvelteKit sets an httpOnly `access_token` cookie.
3. `hooks.server.ts` protects `/dashboard` and redirects missing-cookie requests to `/login?next=...`.
4. `/logout` calls FastAPI `POST /auth/logout` best-effort, deletes the cookie, and redirects to `/login`.

Current protected route list:

- `/dashboard`

## Environment variables

Backend:

- `JWT_SECRET`
- `JWT_TOKEN_EXPIRE_MINUTES`
- `APP_ADMIN_USERNAME`
- `APP_ADMIN_PASSWORD`
- `APP_ADMIN_PASSWORD_HASH`

Frontend/server-side SvelteKit:

- `API_INTERNAL_URL`

Existing app metadata variables remain unchanged:

- `APP_DATABASE_URL`
- `GNUCASH_DEFAULT_BOOK_PATH`

## Verification

Backend:

```bash
cd apps/api
pytest -q
```

Result:

```text
43 passed
```

Frontend:

```bash
cd apps/web
npm run check
npm run test:auth-routes
npm run build
```

Results:

```text
svelte-check found 0 errors and 0 warnings
auth route checks passed
vite build OK
```

Runtime smoke test:

- Started FastAPI through `TestClient` with temporary `APP_DATABASE_URL`.
- Seeded admin via `APP_ADMIN_PASSWORD`.
- Verified:
  - `POST /auth/login` returns token.
  - `GET /auth/me` returns admin with bearer token.
  - `POST /auth/logout` returns `{"status":"ok"}`.

## Intentionally not done

- No registration.
- No OAuth.
- No password reset.
- No complex RBAC UI.
- No multi-user management UI.
- No accounts/transactions implementation.
- No GnuCash writes.
- No token storage in `localStorage` or `sessionStorage`.

## Notes for next phase

- Future account/transaction API routes should depend on `get_current_user`, resolve the target book through `BookRegistryService`, and use `BookAccessService.assert_can_view` before opening a GnuCash book read-only.
- If app-level writes are introduced later, use `BookAccessService.assert_can_edit`, but keep GnuCash writes disabled until a dedicated write-safety phase.
