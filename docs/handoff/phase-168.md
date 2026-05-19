# Phase 168 — First-run and broken-configuration operator UX

Date: 2026-05-20
Status: DONE
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 7/10 only)

## Goal

Make common first-run failures actionable for self-hosted operators while preserving private-path redaction and pre-alpha safety warnings.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-167.md`;
  - roadmap phase 7 and safety constraints from `cycle-2-roadmap.md`.
- Kept this as Phase 168 only; no neighboring roadmap phases were started.
- Improved backend diagnostics:
  - `/health` now reports safe `auth_configuration` status for placeholder/missing `JWT_SECRET` and missing admin bootstrap credentials;
  - default-book diagnostics now distinguish an existing-but-unreadable file from a missing/unmounted book without exposing full paths;
  - startup diagnostics log a redacted `first_run_configuration_warning` with safe next actions when auth bootstrap is incomplete.
- Improved operator-facing web guidance:
  - `/login` reports backend auth-configuration failures as setup problems, not generic invalid credentials;
  - `/books` empty-state copy points first-run operators to `GNUCASH_DEFAULT_BOOK_PATH`, readable test-copy book placement, and `/health`;
  - the global error component gives safe 5xx next actions for `/health`, local `.env`, and book-volume checks.
- Added support doc:
  - `docs/operations/troubleshooting.md` covers missing/unreadable default book, placeholder JWT secret, missing admin bootstrap credentials, app DB reachability, and UI guidance.
- Updated `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Production writes were not enabled.
- No setup wizard or config-writing UI was added.
- No secrets, `.env` values, private full paths, real/private books, app DBs, backups, screenshots/exports, account names, transaction descriptions, memos, amounts, or private financial data were committed.
- No book upload/management UI was added.
- No public-hosting hardening, production-readiness, or security-audited claim was added.
- GnuCash Desktop remains the authoritative editor.

## Verification

```bash
cd apps/api && pytest tests/test_health.py -q
cd apps/web && npm run test:auth-routes
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results:

- Targeted backend health/config diagnostics tests passed.
- Frontend auth/static route checks passed.
- Backend full suite passed.
- Frontend `npm run check` passed.
- Frontend production build passed.
- Docker Compose config validation passed.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Files changed

- `apps/api/app/diagnostics.py`
- `apps/api/tests/test_health.py`
- `apps/web/src/routes/login/+page.server.ts`
- `apps/web/src/lib/components/ErrorState.svelte`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/operations/troubleshooting.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-168.md`
