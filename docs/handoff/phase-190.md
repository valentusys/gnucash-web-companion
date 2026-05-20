# Phase 190 — Combined release-candidate dogfood after cycle-2 changes

Date: 2026-05-20
Status: COMPLETE — default read-only and bounded write-alpha release-candidate dogfood completed; no release/tag published
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 9 only)

## Goal

Gather final practical evidence after cycle-2 Phases 183–189: default read-only Docker/Caddy regression plus explicit disposable write-alpha smoke for the touched create/PATCH/DELETE route family.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-189.md`;
  - roadmap file named by the phase contract;
  - relevant read-only/browser/write-alpha smoke helpers and earlier dogfood evidence.
- Ran default Docker/Caddy config validation with `GNUCASH_WRITES_ENABLED=false` rendered for API and web.
- Ran default read-only API smoke against the committed synthetic fixture copied into ignored runtime data.
- Ran browser dogfood at mobile `320x720` and desktop `1280x900` viewports; both passed login, protected redirect, read-only pages, hidden write UI, CSV fetch, no-overflow checks, and no artifact creation.
- Ran explicit local-only write-alpha smokes under `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true` for create, PATCH, and DELETE on synthetic/disposable runtime copies.
- Returned the stack to default false, reran read-only API smoke, stopped Docker/Caddy, and removed ignored runtime data.

## Files changed

- `docs/dogfood/phase-190-cycle-2-release-candidate-dogfood.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-190.md`

No product code or smoke helper changes were needed.

## Verification summary

Commands/results recorded for this phase:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test ORIGIN=http://localhost:8080 docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test ORIGIN=http://localhost:8080 docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test ORIGIN=http://localhost:8080 docker compose up -d --build
SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-api-smoke.py --api-base-url http://localhost:8080/api
SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --viewport-width 320 --viewport-height 720 --fixture-path apps/api/tests/fixtures/test-book.gnucash.sqlite
SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --viewport-width 1280 --viewport-height 900 --fixture-path apps/api/tests/fixtures/test-book.gnucash.sqlite
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/write-alpha-create-smoke.py --api-base-url http://localhost:8080/api
SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/write-alpha-patch-smoke.py --api-base-url http://localhost:8080/api
SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/write-alpha-delete-restore-smoke.py --api-base-url http://localhost:8080/api
# container-side redacted audit/backup/lock inspection for create/PATCH/DELETE host-readability limits
# reset to default false, final read-only API smoke, docker compose down, runtime cleanup/no-artifact scan
```

Results:

- Default rendered Compose config passed and showed `GNUCASH_WRITES_ENABLED: "false"` for both API and web.
- Default read-only API smoke passed: health, login/auth, books, accounts, transactions, transaction detail, CSV export, reports summary, and disabled validate/create/PATCH/DELETE probes returning 403.
- Mobile and desktop browser dogfood passed with hidden write UI, auth cookie not readable from `document.cookie`, CSV fetch success, no horizontal overflow, and no screenshots/downloads/CSV artifacts.
- Explicit write-alpha rendered config showed `GNUCASH_WRITES_ENABLED: "true"` only for the local write smoke runs.
- Create route evidence: one success audit row, transaction id present, backup evidence present, one backup file, stale/non-active lock evidence from inside the API container.
- PATCH route evidence: one expected safe missing-transaction failed audit row without backup, one success audit row with backup evidence, one backup file, stale/non-active lock evidence from inside the API container.
- DELETE route evidence: one success audit row with backup evidence, one backup file, stale/non-active lock evidence from inside the API container. The host helper stopped at backup readability during restore proof, so no restore claim is made for this phase.
- Final default false config render and read-only API smoke passed after the write-enabled runs.
- Targeted backend checks passed: `cd apps/api && pytest tests/test_health.py tests/test_transaction_writes.py tests/test_write_lock.py tests/test_write_alpha_smoke_lock_evidence.py -q` (`86 passed`).
- Frontend checks passed: `npm run check`, `npm run test:auth-routes`, and `npm run build`.
- Final Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.
- Teardown/no-artifact scan found zero non-placeholder runtime files under `data/books`, `data/app`, `data/backups`, and `data/locks`.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default before and after the phase.
- Write-alpha was enabled only for explicit local `APP_ENV=test` disposable smoke runs.
- No real/private/only-copy book, app DB, backup, `.env`, token, key, cert, screenshot, raw CSV export, private path, account name, memo, amount, or private financial data was committed.
- No release, tag, package, Docker image, public deployment, production-readiness claim, security-audit claim, or real/private-book write-safety claim was added.

## Next

Proceed only to the next roadmap phase when explicitly requested. Do not start release-readiness, tag, or GitHub release publication from this phase.
