# Phase 160 — Release-candidate synthetic Docker/browser dogfood

Date: 2026-05-20
Status: DONE — synthetic/disposable release-candidate dogfood passed
Starting HEAD: `131d568`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 9/10 only)

## Goal

Re-run complete synthetic/disposable Docker+Caddy API and browser dogfood after all read-only changes in this cycle.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-159.md`;
  - roadmap phase 9 and common safety constraints from `cycle-1-roadmap.md`.
- Kept this as Phase 160 only; no neighboring roadmap phases were started.
- Ran local Docker Compose/Caddy with the committed synthetic fixture copied into ignored runtime data as `data/books/main.gnucash.sqlite`.
- Temporarily moved the existing ignored local `data/app/app.db` aside so the dummy smoke admin password matched the disposable app DB, then restored the previous ignored app DB after shutdown.
- Verified `/api/health` reported the default book present/readable and `writes_enabled=false`.
- Ran the read-only API smoke through health, login, auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and disabled validate/create/patch write probes.
- Added a manual disabled `DELETE /books/{book_id}/transactions/{transaction_id}` probe; it returned HTTP 403 with the expected write-disabled message.
- Ran the headless browser dogfood at 320x720 mobile viewport through login, protected redirect, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV export, hidden write UI, no-overflow checks, and no download/artifact checks.
- Recorded redacted evidence in `docs/dogfood/phase-160-release-candidate-dogfood.md`.
- Updated `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff.

## Verification

Dogfood/runtime checks:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ADMIN_USERNAME=admin ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose up -d --build
SMOKE_API_BASE_URL=http://localhost:8080/api SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-api-smoke.py
SMOKE_WEB_BASE_URL=http://localhost:8080 SMOKE_ADMIN_USERNAME=admin SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --fixture-path data/books/main.gnucash.sqlite
# manual DELETE disabled-write probe
# no raw screenshots/csv/backups found in repo root/data backup paths
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose down
```

Results: passed. Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"`; API and browser dogfood both reported `PASS`; the manual DELETE write probe returned HTTP 403; no raw screenshot/CSV/backup artifacts were found in checked paths.

Standard checks:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
```

Results: passed. Backend test result: `386 passed, 32 warnings`. Frontend `npm run check`, `npm run test:auth-routes`, and `npm run build` passed. Rendered Compose config keeps `GNUCASH_WRITES_ENABLED: "false"`.

Sensitive tracked-file hygiene scan: passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- No release/tag/package/image was published.
- Optional copied-book dogfood was not run because no explicit safe copied book path was provided for this phase.
- No private directories were searched.
- No real/private GnuCash book, `.env`, app DB, backup, screenshot/export, token, key, cert, private path, or private financial data was committed.

## Files changed

- `docs/dogfood/phase-160-release-candidate-dogfood.md`
- `docs/handoff/phase-160.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
