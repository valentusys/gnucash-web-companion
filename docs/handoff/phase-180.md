# Phase 180 — full read-only plus write-alpha regression dogfood

Date: 2026-05-20
Status: COMPLETE — combined default-read-only and explicit disposable write-alpha regression dogfood
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 9 only)

## Goal

Re-run a combined regression pass after write-alpha dogfood-driven fixes while preserving read-only default safety.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-179.md`;
  - roadmap file named by the phase contract;
  - relevant smoke helpers and Phase 175–179 dogfood evidence.
- Ran local Docker/Caddy read-only dogfood with default `GNUCASH_WRITES_ENABLED=false`.
- Verified API read-only flows and disabled validate/create/PATCH/DELETE probes.
- Verified browser read-only flows at `320x720`, hidden write UI, no auth-cookie JavaScript readability, no mobile overflow, CSV-export response through the helper, and no screenshot/download/CSV artifacts.
- Ran explicit synthetic/disposable write-alpha create smoke under `APP_ENV=test` plus local-only `GNUCASH_WRITES_ENABLED=true` because Phases 175–179 included write-alpha dogfood/fixes.
- Reconfirmed return to default read-only config and read-only API smoke after the write-alpha run.
- Tore down runtime data and documented evidence in `docs/dogfood/phase-180-combined-regression-dogfood.md`.

## Files changed

- `docs/dogfood/phase-180-combined-regression-dogfood.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-180.md`

## Verification summary

Commands/results recorded for this phase:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test ORIGIN=http://localhost:8080 docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test ORIGIN=http://localhost:8080 docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
SMOKE_ADMIN_PASSWORD=dummy SMOKE_API_BASE_URL=http://localhost:8080/api scripts/smoke/read-only-api-smoke.py
SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --password dummy --viewport-width 320 --viewport-height 720
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
SMOKE_ADMIN_PASSWORD=dummy SMOKE_API_BASE_URL=http://localhost:8080/api scripts/smoke/write-alpha-create-smoke.py
# container-side redacted inspection after known host lock-file permission limitation
SMOKE_ADMIN_PASSWORD=dummy SMOKE_API_BASE_URL=http://localhost:8080/api scripts/smoke/read-only-api-smoke.py
```

Results:

- Default Compose config rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- Read-only API smoke passed, including disabled validate/create/PATCH/DELETE probes returning 403.
- Browser dogfood passed with write UI hidden and no artifacts written.
- Explicit write-alpha override rendered `GNUCASH_WRITES_ENABLED: "true"` only for the local `APP_ENV=test` disposable run.
- Write-alpha create smoke executed one create against the disposable runtime copy; the host helper stopped at the known root-owned lock-file readability check after the create. It was not rerun. Container-side inspection confirmed exactly one successful `transaction.create` audit row, one backup file, and no active lock hold.
- After stopping the write-enabled run, default config again rendered `GNUCASH_WRITES_ENABLED: "false"`, `/api/health` reported `writes_enabled=false`, and read-only API smoke again passed with disabled write probes returning 403.
- Docker runtime data was removed after verification.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The write-enabled run was explicit, local-only, `APP_ENV=test`, synthetic/disposable, and temporary.
- No real/private/only-copy book was used.
- No release/tag/package was published.
- No raw book, backup, app DB, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data was committed.

## Next

Continue only with the next explicitly requested phase. Do not run Phase 10 release-readiness gate or publish any release/tag unless a later phase explicitly requests and authorizes it.
