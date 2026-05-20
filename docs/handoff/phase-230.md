# Phase 230 handoff — Cycle 3 final release-candidate dogfood pack

Date: 2026-05-21
Status: COMPLETE — final release-candidate dogfood pack passed; no release or tag published.

## Summary

Phase 230 stayed within the Cycle 3 Phase 9 contract. It produced the final release-candidate dogfood evidence pack for a later `v0.2.5-writealpha` attempt after the backup/audit remediation cycle.

No product feature, write route, write default, `APP_ENV=test` gate, release tag, GitHub release, package, image, production/security claim, broad compatibility claim, or real/private-book write-safety claim changed.

## Files changed

- `docs/dogfood/phase-230-cycle-3-release-candidate-dogfood.md` — redacted default-read-only API/browser dogfood, write-alpha create/PATCH/DELETE matrix, DELETE restore proof, default-false reset, cleanup, and Phase 10 release input.
- `PROJECT_STATUS.md`, `README.md`, `README.ru.md`, `CHANGELOG.md`, and `docs/ROADMAP.md` — factual status synchronized to completed Phase 230 while retaining `v0.2.4-writealpha` as the current published write-alpha pre-release and `v0.1.7-readonly` as the current read-only pre-release.
- `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` — public-status guard expectations moved to Phase 230 so standard backend tests keep matching the updated public docs.
- `docs/handoff/phase-230.md` — this handoff.

## Verification performed

Dogfood and release-candidate evidence:

- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://127.0.0.1:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/phase-230-synthetic.gnucash.sqlite GNUCASH_WRITES_ENABLED=false docker compose config --quiet` — passed.
- Rendered Compose grep for `GNUCASH_WRITES_ENABLED` — API and web showed `"false"`.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py` — passed before write-alpha and after reset.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --viewport-width 320 --viewport-height 720` — passed.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --viewport-width 1280 --viewport-height 900` — passed.
- `python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-disposable-copy>` — passed for create, PATCH, and DELETE candidates.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-create-smoke.py` — passed.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-patch-smoke.py` — passed.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-delete-restore-smoke.py` — passed with host-readable backup restore proof.
- `python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute --via-compose` — removed ignored runtime artifacts after each route-family/reset run.
- Final `python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED` — passed with `books=0, app=0, backups=0, locks=0`.

Standard checks:

- `python3 scripts/check_public_status.py` — passed.
- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` was not weakened.
- Write-alpha was enabled only for bounded explicit local synthetic/disposable route-family smokes.
- Successful mutations were not rerun after evidence collection.
- No real/private/only-copy book, committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw path, account name, memo, amount, production/security claim, public-internet-safety claim, broad compatibility claim, or real/private-book write-safety claim was added.

## Risks / blockers

No Phase 230 dogfood blocker remains. The Phase 10 input is green, but `v0.2.5-writealpha` remains unpublished until a separate authorized release-gate/publication phase succeeds.

## Next

Do not start the next roadmap phase from this session.
