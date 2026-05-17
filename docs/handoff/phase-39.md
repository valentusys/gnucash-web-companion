# Phase 39 — Read-Only Smoke Test Automation

## Status

Complete. Automated smoke script added; checks passed; commit/push completed.

## PM report

### Decision

Execute exactly Phase 39 from the roadmap as a minimal read-only API smoke automation phase.

### Why

Phase 38 created a manual personal dogfood checklist. The next safest stabilization step is a small automated API smoke script that can run against a local Docker deployment and confirm the read-only path works while controlled-write endpoints remain disabled by default.

### Phase brief

- Goal: add a minimal automated smoke script for local read-only Docker/API deployments.
- Non-goals: no new product features, no release/tag, no write-mode enablement, no write-scope expansion, no real data/exports/screenshots committed.
- Acceptance criteria:
  - `scripts/smoke/read-only-api-smoke.py` exists and is documented.
  - The script does not require real financial data.
  - The script can run against a local Docker deployment.
  - The script checks API health, login, `/auth/me`, default book discovery, accounts, transactions, reports summary, and disabled-write 403 responses for validate/create/patch endpoints.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are synchronized for Phase 39.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains the safe default.
  - Controlled writes remain experimental post-MVP and disabled by default.
  - No write endpoint is expanded or enabled.
  - No real GnuCash book, `.env`, app DB, backup, secret, token, key, screenshot, or export is committed.
- Verification:
  - `python3 -m py_compile scripts/smoke/read-only-api-smoke.py`
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

### Risks

- The roadmap names `books/default`, but the current API does not expose a literal `/books/default` route. The script avoids adding a new endpoint and instead discovers the default book via `GET /books`, then verifies `GET /books/{book_id}`. This keeps Phase 39 scoped to smoke automation only.
- Running the script against a deployment with the authoritative real book could expose sensitive data in local terminal output if future logging is expanded; the current script prints only endpoint status and book id, not accounts, transactions, balances, descriptions, or CSV data.
- The script needs the local admin password through `SMOKE_ADMIN_PASSWORD` or `APP_ADMIN_PASSWORD`; it never prints the password.

### Files/docs to update

- `scripts/smoke/read-only-api-smoke.py`
- `scripts/smoke/read-only-smoke-check.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-39.md`

### GitHub/backlog

- No Phase 39-specific GitHub issue was found in the current open issue list.
- GitHub #18, #20, and #22 intentionally remain open for their separate scopes.

## Engineer report

Implemented Phase 39 smoke automation only:

- Created `scripts/smoke/read-only-api-smoke.py`:
  - stdlib-only Python script, no new dependencies;
  - default target: `http://localhost:8080/api`, matching Docker/Caddy proxy routing;
  - accepts `SMOKE_API_BASE_URL`, `SMOKE_ADMIN_USERNAME`, and `SMOKE_ADMIN_PASSWORD`/`APP_ADMIN_PASSWORD`;
  - checks `/health`, `/auth/login`, `/auth/me`, default book discovery through `/books`, `/books/{book_id}`, `/books/{book_id}/accounts`, `/books/{book_id}/transactions`, `/books/{book_id}/reports/summary`;
  - explicitly probes validate/create/patch controlled-write endpoints and requires disabled-write HTTP 403 responses.
- Updated `scripts/smoke/read-only-smoke-check.md` with the automated API smoke command and scope.
- Updated `PROJECT_STATUS.md` to completed through Phase 39 and set Phase 40 as the next planned phase.
- Updated `CHANGELOG.md` with a Phase 39 Unreleased entry.

No backend/frontend product behavior changed. No write behavior changed. No release/tag was created.

## Verification

Passed:

- `python3 -m py_compile scripts/smoke/read-only-api-smoke.py` — passed.
- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.

Not run:

- Live smoke script against Docker was not run in this phase because it requires a running local deployment and local admin password/book setup. The script is documented for that deployment-time smoke path.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No auth localStorage/sessionStorage path was introduced.
- No real financial data, GnuCash books, `.env`, app DBs, backups, secrets, keys, tokens, certs, real screenshots, or real CSV exports were added.

## Commit / push

- Commit message: `test: add read-only API smoke script`.
- Final commit SHA: see `git log -1 --oneline` for this phase commit.
- Push: pushed to `origin/main`.

## GitHub issue status

- No Phase 39-specific GitHub issue was found in the current open issue list.
- GitHub #18, #20, and #22 intentionally remain open for separate scopes.
