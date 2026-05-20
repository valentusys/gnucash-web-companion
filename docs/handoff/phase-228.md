# Phase 228 handoff — Fresh-clone and upgrade smoke after remediation

Date: 2026-05-21
Status: COMPLETE — fresh-clone Docker smoke and synthetic `v0.2.4-writealpha` → current `HEAD` upgrade smoke passed with default-disabled writes.

## Summary

Phase 228 stayed within the Cycle 3 Phase 7 contract. It verified a clean checkout and synthetic upgrade path after the write-alpha backup/audit remediation, before any release gate.

No product code, write route, migration feature, release tag, package, image, write default, or `APP_ENV=test` gate changed.

## Files changed

- `docs/dogfood/phase-228-fresh-clone-upgrade-after-remediation.md` — redacted fresh-clone and synthetic upgrade evidence.
- `docs/handoff/phase-228.md` — this handoff.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, and `PROJECT_STATUS.md` — factual public/status synchronization to Phase 228 while keeping `v0.2.4-writealpha` as the current published write-alpha release.
- `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` — guard expectation synchronized to Phase 228 so CI keeps the public docs consistent.

## Verification performed

- `scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref HEAD --port 18084` — passed; current `HEAD` `059b40f`, read-only API smoke, browser dogfood at `320x720` and `1280x900`, disabled validate/create/PATCH/DELETE probes returned HTTP 403, no raw screenshot/export/backup artifacts.
- `scripts/smoke/synthetic-upgrade-smoke.sh --repo /home/val/gnucash-web-companion --previous-ref v0.2.4-writealpha --current-ref HEAD --port 18085` — passed; previous checkout `05f9080`, current checkout `059b40f`, dummy app metadata/default book/selected-book recovery/read-only routes/audit-summary preserved, disabled validate/create/PATCH/DELETE probes returned HTTP 403.
- Post-smoke Docker cleanup check for `gwc_fresh_clone` / `gwc_synthetic_upgrade` containers and volumes — passed; no leftovers reported.
- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- `python3 scripts/check_public_status.py` — passed.
- Rendered Compose grep for `GNUCASH_WRITES_ENABLED: "false"` — passed for API and web.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.

Local smoke logs are untracked under `/home/val/.hermes/logs/gnucash-web-companion/phase-228/` and were not committed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remained default and active in both smokes.
- `APP_ENV=test` was not weakened.
- No write-enabled smoke was run.
- Only the committed synthetic fixture was copied into ignored temporary runtime paths.
- Temporary clones and Docker runtime were removed by helper teardown.
- No real/private/only-copy book, committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw path, account name, memo, amount, production/security claim, broad migration guarantee, or real/private-book write-safety claim was added.

## Risks / blockers

No Phase 228 blocker remains. `v0.2.5-writealpha` remains unpublished; a later release-gate phase must still run before any tag or GitHub release. The next roadmap phase is Cycle 3 Phase 8/229, public status and release-doc drift guard refresh, and should be run only in a fresh Hermes session.

## Next

Do not start the next roadmap phase from this session.
