# Phase 150 — Synthetic Docker/browser dogfood refresh

Date: 2026-05-19
Status: DONE
Starting HEAD: `c6eb9c1`

## Goal

Prove the new read-only UX from Phases 143–149 works end-to-end on disposable synthetic data through Docker/Caddy, API smoke, and headless browser dogfood.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-149.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 150 only; no PM/auditor was involved and no later roadmap phase was started.
- Prepared a disposable runtime fixture by copying `apps/api/tests/fixtures/test-book.gnucash.sqlite` to ignored `data/books/main.gnucash.sqlite`.
- Reset ignored local app runtime state for the Docker smoke user, then restored the previous ignored `data/app/app.db` after Docker shutdown.
- Built and started local Docker Compose through Caddy with:
  - `GNUCASH_WRITES_ENABLED=false`;
  - `APP_ADMIN_PASSWORD=dummy`;
  - `API_INTERNAL_URL=http://api:8000`;
  - `ORIGIN=http://127.0.0.1:8080`.
- Ran read-only API smoke through the Caddy proxy covering health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and disabled validate/create/patch write probes.
- Ran headless browser dogfood through login, protected redirect, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, authenticated CSV export, hidden write UI, and no-artifact checks.
- Documented dogfood evidence in `docs/dogfood/phase-150-synthetic-dogfood.md`.
- Synchronized public/status docs: `README.md`, `README.ru.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md`.

## Verification

- Runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy GNUCASH_WRITES_ENABLED=false docker compose config --quiet` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy GNUCASH_WRITES_ENABLED=false API_INTERNAL_URL=http://api:8000 ORIGIN=http://127.0.0.1:8080 docker compose up -d --build` — passed.
- `/api/health` — passed with `status=ok`, default book exists/readable, `writes_enabled=false`, `cors.risk_level=ok`.
- `APP_ADMIN_PASSWORD=dummy SMOKE_ADMIN_PASSWORD=dummy SMOKE_API_BASE_URL=http://127.0.0.1:8080/api scripts/smoke/read-only-api-smoke.py` — passed.
- `SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --fixture-path data/books/main.gnucash.sqlite` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose down` — passed; ignored local app DB restored after shutdown.
- Final standard checks before commit:
  - `cd apps/api && pytest -q` — passed: `380 passed, 32 warnings`;
  - `cd apps/web && npm run check` — passed: `svelte-check found 0 errors and 0 warnings`;
  - `cd apps/web && npm run test:auth-routes` — passed: `auth route checks passed`;
  - `cd apps/web && npm run build` — passed;
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed;
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`;
  - `git diff --check` — passed;
  - sensitive tracked-file hygiene scan — passed: `sensitive tracked-file hygiene scan passed`.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default and was verified in runtime health/API smoke.
- The dogfood pass used only a synthetic/disposable fixture copied into ignored runtime data.
- No personal-book dogfood was attempted because no safe copied path was provided for this phase.
- No screenshots, raw CSV exports, app DB, GnuCash runtime book, backup, `.env`, token, key, cert, private path, or real/private financial data was committed.
- Controlled writes remain post-MVP/experimental, disabled by default, and were not expanded or enabled.
- No release, tag, package, or GitHub pre-release was published.

## Files changed

- `docs/dogfood/phase-150-synthetic-dogfood.md`
- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-150.md`
