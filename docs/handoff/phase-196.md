# Phase 196 — First-run/read-only deployment confidence pass

Date: 2026-05-20
Status: COMPLETE — scoped first-run diagnostics implemented, tested, committed/pushed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 5 only)

## Goal

Make safe self-hosted read-only first-run deployment problems easier to triage after `v0.2.2-writealpha`, without adding a setup wizard, config-writing UI, write enablement, or production/security claims.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-195.md`;
  - roadmap file named by the phase contract;
  - existing health/auth/login/i18n/troubleshooting files.
- Added a redacted `/health` `first_run` block with stable safe check keys:
  - `jwt_secret` for missing/placeholder secret state;
  - `admin_bootstrap` for missing admin password/hash bootstrap state;
  - `default_book` for configured/missing/unreadable default-book state using existing path-redacted diagnostics;
  - `cors` for unsafe wildcard CORS outside development-like `APP_ENV`;
  - `write_mode` for default read-only vs explicitly enabled experimental writes.
- Added `summary`, `action_required`, and per-check status/message fields so operators can triage without parsing lower-level diagnostics.
- Updated `/login` to fetch `/health` server-side and render the redacted first-run diagnostics before authentication.
- Added EN/RU catalog copy for critical login first-run diagnostics and status labels.
- Kept login UI mobile-safe with bounded layouts, `min-w-0`, and `break-words` diagnostics.
- Updated troubleshooting docs with the `first_run` shape, action list guidance, unsafe wildcard CORS guidance, and write-disabled expectation.
- Updated `PROJECT_STATUS.md`.

## Files changed

- `PROJECT_STATUS.md`
- `apps/api/app/diagnostics.py`
- `apps/api/tests/test_health.py`
- `apps/web/scripts/test-auth-routes.mjs`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/login/+page.server.ts`
- `apps/web/src/routes/login/+page.svelte`
- `docs/operations/troubleshooting.md`
- `docs/handoff/phase-196.md`

No setup wizard, config-writing UI, auth-model change, write endpoint/default change, release/tag publication, public-internet hardening claim, or production/security claim was added.

## Verification summary

Commands/results:

```bash
cd apps/api && pytest tests/test_health.py -q
# 10 passed

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/api && pytest tests/test_health.py tests/test_transaction_writes.py -q
# 69 passed, 33 warnings

cd apps/web && npm run build
# built successfully

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered default remains false for API and web

cd apps/api && pytest -q
# 470 passed, 34 warnings

# Synthetic first-run Docker/Caddy smoke with dummy local-only secrets and copied committed fixture:
# JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose up -d --build
# /api/health returned status=ok, first_run summary configured, action_required=[], write_mode=ok.
# /login rendered first-run diagnostics and did not expose dummy secret/password.

SMOKE_ADMIN_PASSWORD=<dummy-local-password> scripts/smoke/read-only-api-smoke.py
# PASS: health, login/auth, books, accounts, transactions, transaction detail, CSV export, reports summary, and disabled validate/create/PATCH/DELETE probes all passed.
```

Final checks before commit/push:

```bash
git diff --check
# passed

# sensitive tracked-file hygiene scan from phase execution playbook
# passed
```

## Redaction / safety evidence

- Backend tests assert placeholder `JWT_SECRET` values and private temporary paths are absent from the health payload.
- Health diagnostics expose only boolean/status/key/message fields and path-redacted default-book filename/status metadata inherited from existing diagnostics.
- Login first-run UI is populated from server-side `/health` and static route checks assert no `localStorage`, `sessionStorage`, `JWT_SECRET=`, or `APP_ADMIN_PASSWORD=` strings in the login diagnostics surface.
- Synthetic Docker smoke checked that dummy local-only secret/password values were absent from both `/api/health` JSON and `/login` HTML.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The first-run diagnostics do not expose secrets, full paths, tokens, app DB contents, book data, backups, or private env values.
- Auth cookie remains httpOnly; no auth localStorage/sessionStorage was added.
- The Docker smoke used a copied committed synthetic fixture under ignored runtime data and dummy local-only credentials only.
- Ignored runtime smoke artifacts were removed after `docker compose down`.
- No real/private/only-copy book was used.
- No `.env`, app DB, book, backup, screenshot, CSV export, token, key, cert, raw path, account name, memo, amount, or private financial artifact was committed.
- No release, tag, package, Docker image, production-readiness claim, security-audit claim, public-internet hardening claim, or real/private-book write-safety claim was added.

## Risks / follow-up

- This is deployment triage UX only, not a full setup wizard and not a replacement for reading deployment docs.
- The health/login messages are intentionally conservative and redacted; they identify configuration classes, not exact secret values or full paths.
- Write-alpha remains experimental, disabled by default, `APP_ENV=test` gated when enabled, and unsafe for real/private or only-copy books.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
