# Phase 14 Handoff — MVP Read-Only Scope Lock

## Status

Phase 14 reconciles the project with the clarified product directive: MVP v0.1 is strictly read-only for GnuCash.

The Phase 12 controlled write implementation remains in the codebase as a post-MVP capability, but it is disabled by default and hidden from the UI unless explicitly enabled.

## Why this phase exists

The clarified product model is:

- MVP: one installation, one local admin user, one default GnuCash book, read-only access.
- Future: multiple users and multiple independent books.
- Advanced future: serialized/locked editing only; no real-time collaborative editing.

Therefore, write endpoints must not be active in the default MVP configuration.

## Changes

### Backend

- Added `Settings.gnucash_writes_enabled: bool = False`.
- Added write gate in `apps/api/app/routers/transactions.py`.
- Write routes now return `403` by default:
  - `POST /books/{book_id}/transactions/validate`
  - `POST /books/{book_id}/transactions`
  - `PATCH /books/{book_id}/transactions/{transaction_id}`
- Existing write tests explicitly enable writes for post-MVP write behavior coverage.
- Added a test confirming writes are forbidden when the setting is disabled.

### Frontend

- `/transactions` hides the `New transaction` link unless `GNUCASH_WRITES_ENABLED=true`.
- `/transactions/new` redirects to `/transactions` unless writes are enabled.
- Form actions return a read-only error if invoked while writes are disabled.

### Config/deployment

- `.env.example` documents `GNUCASH_WRITES_ENABLED=false`.
- `docker-compose.yml` passes `GNUCASH_WRITES_ENABLED=false` to both API and web by default.

### Project context

- Updated `AGENTS.md` with the clarified single-agent operating mode, product model, stack, absolute restrictions, and post-MVP write policy.
- Updated `PROJECT_STATUS.md` with Phase 14 status and the clarified MVP/future positioning.

## GitHub tooling

Checked:

```bash
git --version
gh --version
gh auth status
```

Result:

- `git` is available.
- `gh` is not installed, so issue automation is blocked.
- Push can proceed through existing git credentials.

## Verification

Run before commit:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
```

## Follow-up

- If post-MVP write testing is needed, set `GNUCASH_WRITES_ENABLED=true` explicitly in a disposable environment only.
- Install/authenticate GitHub CLI if automatic issue management is required.
