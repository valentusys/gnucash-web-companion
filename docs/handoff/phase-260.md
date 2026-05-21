# Phase 260 — v0.2.8 release-candidate or no-release verdict

Date: 2026-05-21

Status: COMPLETE — `v0.2.8-writealpha` release-candidate artifacts prepared; no publication.

## Summary

Phase 260 reviewed the Phase 258 synthetic copied-book package rehearsal and the Phase 259 owner copied-book dry-run-only decision gate.

Verdict: prepare an unpublished `v0.2.8-writealpha` release candidate.

Rationale:

- The Cycle 3 maintainer copied-book package is strong enough for a conservative release candidate: maintainer packet, explicit dry-run/create-one wrapper, stronger UI warnings, bounded compatibility harness, restore harness, synthetic end-to-end rehearsal, and default-disabled reset evidence are documented.
- The candidate remains conservative: owner copied-book dogfood may still be pending, and the next owner ask remains dry-run only.
- CREATE-one is not the immediate owner ask and can be considered only after owner dry-run evidence is reviewed.

## Artifacts

- `docs/release/v0.2.8-writealpha-notes.md`
- `docs/release/v0.2.8-writealpha-checklist.md`
- `docs/release/v0.2.8-writealpha-final-gate.md`
- `docs/handoff/phase-260.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- public status docs/guard updates for Phase 260

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- The backend `APP_ENV=test` write-alpha gate was not changed or weakened.
- No owner/private/original/only-copy book was used or requested.
- No app DB, GnuCash book, backup, CSV, screenshot, `.env`, token, key, cert, raw path, account name, memo, amount, API payload, cookie, or private financial data artifact was committed.
- No release/tag was published.
- No production, security-audited, public-internet, production disaster-recovery, broad Desktop/version compatibility, or real/private/only-copy write-safety claim was added.

## Verification performed

```bash
python3 scripts/check_public_status.py
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# safety greps for GNUCASH_WRITES_ENABLED, gnucash_writes_enabled, APP_ENV=test, localStorage/sessionStorage
# sensitive tracked-file hygiene scan
```

Results:

- Public status guard: PASS.
- Backend tests: PASS — 579 passed, 35 warnings.
- Frontend checks/auth-route tests/build: PASS.
- Docker Compose config: PASS.
- Rendered Docker Compose default: `GNUCASH_WRITES_ENABLED=false` for API and web.
- Git whitespace check: PASS.
- Safety greps: PASS; browser storage remains theme-only `localStorage` use.
- Sensitive tracked-file hygiene scan: PASS.

## GitHub issues

No new GitHub issue was created. The release-candidate decision remains within the existing controlled-write readiness umbrella (#36) and does not require a separate noisy issue.

## Next phase boundary

Phase 261 may make the Cycle 3 release/no-release decision. If publication is considered, Phase 261 must call PM, rerun the final gate, verify tag/release absence, wait for exact release/status commit CI, and publish only if authorized and green. Phase 260 did not publish, did not call PM, did not execute owner dogfood, did not ask for private data, did not authorize CREATE-one as the immediate owner action, and did not claim real/private/only-copy write safety.
