# Phase 202 — Read-only first-run health drill

Date: 2026-05-20
Status: COMPLETE — default read-only first-run diagnostics now expose redacted next actions for health/login triage
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 1 only)

## Goal

Harden the default read-only first-run diagnostics path so a new operator can distinguish missing/unreadable default book, placeholder JWT/admin bootstrap config, unsafe CORS posture, and write-disabled status without exposing paths or secrets.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-201.md`, and the cycle-1 roadmap file.
- Extended `/health` redacted `first_run.checks` with `safe_next_actions` for:
  - `jwt_secret`
  - `admin_bootstrap`
  - `default_book`
  - `cors`
  - `write_mode`
- Added redacted default-book `path_kind` to distinguish:
  - `not_configured`
  - `missing_file`
  - `unreadable_file`
  - `local_file`
- Updated `/login` to render the redacted per-check next actions from `/health` in the existing mobile-safe diagnostics panel.
- Updated TypeScript DTOs and static route checks for the new first-run diagnostics shape.
- Added/updated targeted backend tests for missing/unreadable/default-book, placeholder JWT/admin bootstrap, CORS warning, write-disabled default, and explicit write-mode warning.
- Ran a minimal Docker/Caddy default read-only API smoke on only the committed synthetic fixture copied into ignored runtime data.
- Updated `PROJECT_STATUS.md` and this handoff.

## Files changed

- `apps/api/app/diagnostics.py`
- `apps/api/tests/test_health.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/routes/login/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-202.md`

## Verification summary

Commands/results:

```text
cd apps/api && pytest tests/test_health.py -q
# passed: 11 passed

cd apps/api && pytest tests/test_health.py tests/test_auth.py tests/test_multi_book_access.py tests/test_transaction_writes.py -q
# passed: 118 passed

cd apps/api && pytest -q
# passed: 471 passed

cd apps/web && npm run test:auth-routes
# passed

cd apps/web && npm run check && npm run test:auth-routes && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered false for API and web

git diff --check
# passed

local Docker/Caddy default-read-only smoke
# /api/health returned ok with action_required=[] and write_mode ok/default disabled
# scripts/smoke/read-only-api-smoke.py passed health, login/auth, books/default book,
# accounts, transactions, transaction detail, CSV export, reports summary,
# validate/create/PATCH/DELETE disabled-write 403 probes

sensitive tracked-file hygiene scan
# passed
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default and was verified in rendered Docker Compose config.
- Default read-only write probes still return 403 for validate/create/PATCH/DELETE.
- `APP_ENV=test` write-alpha gate was not changed.
- Auth remains httpOnly-cookie based; no localStorage/sessionStorage for auth or financial state was added.
- `/health` and `/login` expose only redacted status/action guidance; no raw secret/token/app DB/book path or GnuCash data is displayed.
- Docker smoke used only `apps/api/tests/fixtures/test-book.gnucash.sqlite` copied to ignored `data/books/main.gnucash.sqlite`; ignored runtime data and dummy local `.env` were removed after smoke.
- No real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw path, account name, memo, amount, or private financial data was committed.

## Risks / follow-up

- This is operator guidance only; it is not a setup wizard and does not modify deployment configuration.
- CORS guidance remains conservative and does not claim production/public-internet safety.
- Write-alpha remains experimental, disabled by default, and synthetic/disposable-only when explicitly enabled under `APP_ENV=test`.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
