# Phase 170 — Full synthetic dogfood after cycle 2 changes

Date: 2026-05-20
Status: DONE
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 9/10 only)

## Goal

Verify the full cycle 2 read-only surface in runtime before any release gate.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-169.md`;
  - roadmap phase 9 and shared safety constraints from `cycle-2-roadmap.md`.
- Kept this as Phase 170 only; no phase 10 release gate was started.
- Ran local Docker/Caddy with the committed synthetic fixture copied to ignored runtime data and `GNUCASH_WRITES_ENABLED=false`.
- Verified `/api/health` reported the default book present/readable, writes disabled, and CORS posture `ok`.
- Ran the read-only API smoke through health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and disabled validate/create/patch/delete write probes.
- Ran headless browser dogfood at:
  - 320x720 narrow/mobile viewport;
  - 1280x900 desktop-width viewport.
- Browser dogfood covered login, protected redirect, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV export, hidden write UI, auth cookie not readable from `document.cookie`, no horizontal overflow, and no download/screenshot/CSV artifacts.
- Recorded redacted evidence in `docs/dogfood/phase-170-cycle-2-release-candidate-dogfood.md`.
- Restored the pre-existing ignored local `data/app/app.db` after the disposable Docker run and removed the ignored runtime fixture.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default and was verified in rendered Compose config and runtime health.
- Production writes were not enabled.
- Controlled writes were not expanded.
- No release, tag, package, image, or GitHub release was published.
- No private directories were searched.
- No copied-book pass was run because no explicit safe copied book path was provided.
- No secrets, `.env` values, private full paths, real/private books, app DBs, backups, screenshots/exports, account names, transaction descriptions, memos, amounts, or private financial data were committed.

## Verification

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ADMIN_USERNAME=admin ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose up -d --build
# /api/health local probe
SMOKE_API_BASE_URL=http://localhost:8080/api SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-api-smoke.py
SMOKE_WEB_BASE_URL=http://localhost:8080 SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --fixture-path data/books/main.gnucash.sqlite --viewport-width 320 --viewport-height 720
SMOKE_WEB_BASE_URL=http://localhost:8080 SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --fixture-path data/books/main.gnucash.sqlite --viewport-width 1280 --viewport-height 900
# no raw screenshot/csv artifact scan
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose down
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results:

- Docker Compose config validation passed before runtime smoke.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- Docker/Caddy startup passed.
- `/api/health` passed with `status=ok`, default book exists/readable, `writes_enabled=False`, and CORS risk `ok`.
- Read-only API smoke passed, including disabled validate/create/patch/delete write probes.
- Browser dogfood passed at 320x720.
- Browser dogfood passed at 1280x900.
- No raw screenshots/CSV artifacts were found outside allowed `docs/images`.
- Backend full suite passed.
- Frontend `npm run check` passed.
- Frontend auth/static route checks passed.
- Frontend production build passed.
- Docker Compose config validation passed after code/docs verification.
- Rendered Compose config still kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Files changed

- `docs/dogfood/phase-170-cycle-2-release-candidate-dogfood.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-170.md`
