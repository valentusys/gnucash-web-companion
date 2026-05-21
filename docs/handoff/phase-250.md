# Phase 250 — v0.2.7 release-candidate preparation or no-release verdict

Date: 2026-05-21

## Summary

Phase 250 prepared `v0.2.7-writealpha` as a release candidate only. It did not publish a tag, GitHub release, package, image, or deployment.

The candidate state is justified because the required Cycle 2 gates are satisfied:

- Backend ownership guards are implemented: PATCH and DELETE require same-book app metadata write-alpha ownership before write-service construction.
- Synthetic/disposable ownership route-family dogfood passed in Phase 247: one write-alpha-owned synthetic transaction was created, PATCHed, and DELETEd; non-owned PATCH/DELETE probes returned 403 without backup growth; backup/audit/lock/restore/default-reset evidence was redacted.
- Ownership docs were synchronized in Phase 249: CREATE ownership, PATCH/DELETE ownership limits, historical/manual read-only behavior, and no real/private/only-copy safety claim are documented.

## Changes

- Added `docs/release/v0.2.7-writealpha-notes.md` as release-candidate-only notes.
- Added `docs/release/v0.2.7-writealpha-checklist.md` as a candidate checklist with Phase 251 publication gates left pending.
- Added `docs/release/v0.2.7-writealpha-final-gate.md` as a final-gate draft deferred to Phase 251.
- Updated README/README.ru, CHANGELOG, PROJECT_STATUS, docs/ROADMAP, and the public-status guard baseline to Phase 250.
- Updated public-status guard tests to reject stale Phase 249 current-baseline wording.

## Release/no-release state

Decision: release candidate prepared for `v0.2.7-writealpha`.

Publication remains blocked until a later Phase 251 release/no-release gate:

1. calls PM/Project Lead;
2. reruns full local release verification;
3. verifies clean tracked tree and `HEAD == origin/main` for the release/status commit;
4. waits for exact release/status commit GitHub Actions;
5. confirms local tag, remote tag, and GitHub release absence;
6. publishes only if all gates pass and PM authorizes.

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The backend `APP_ENV=test` write-alpha gate remains intact.
- No release, tag, package, Docker image, production deployment, write default change, write-scope expansion, or gate weakening was added.
- No create/PATCH/DELETE dogfood mutation was run in this phase.
- No real/private book, only-copy book, app DB, backup, `.env`, CSV/export, screenshot, token, key, cert, raw private path, account name, memo, amount, or private financial artifact was used or committed.
- Release-candidate docs state synthetic/disposable evidence only and do not claim real/private or only-copy write safety.
- Docs continue to avoid production/security/public-internet/broad-compatibility claims.

## Verification

```bash
python3 scripts/check_public_status.py
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
grep -R "GNUCASH_WRITES_ENABLED" -n .env.example docker-compose.yml apps || true
grep -R "gnucash_writes_enabled" -n apps/api || true
grep -R "APP_ENV=test" -n README.md docs apps || true
grep -R "localStorage\|sessionStorage" -n apps/web/src || true
git diff --check
python3 - <<'PY'
# tracked sensitive-file hygiene scan
PY
```

Results:

- Public status guard: PASS.
- Backend full test suite: PASS (`559 passed`, known piecash/SQLAlchemy warnings only).
- Frontend check/auth-route/build: PASS.
- Docker Compose config: PASS.
- Rendered Compose write default: PASS — API and web keep `GNUCASH_WRITES_ENABLED=false`.
- Safety greps: PASS — no default/gate weakening found; browser-storage matches remain limited to theme storage and route checks.
- Git diff whitespace check: PASS.
- Sensitive tracked-file hygiene scan: PASS.

## Result

Phase 250 is complete. `v0.2.7-writealpha` is prepared as a release candidate only, with publication deferred to Phase 251 and no change to the read-only default or write-alpha safety boundaries.
