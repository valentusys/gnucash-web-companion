# Phase 261 — Cycle 3 release/no-release and final next-step recommendation

Date: 2026-05-21

Status: COMPLETE — `v0.2.8-writealpha` published as a conservative GitHub pre-release after PM authorization and release gates.

## Summary

Phase 261 finished the 30-phase execution plan with a release and a clear stop point.

PM was called because this phase was an explicit release/no-release decision gate. PM returned `AUTHORIZE_RELEASE` for a narrow publication scope: annotated git tag plus GitHub pre-release only.

`v0.2.8-writealpha` was published only after the full local release gate, tag/release absence checks, exact release/status commit CI, and post-publication verification. No package, image, production deployment, write-default change, `APP_ENV=test` gate weakening, real/private/only-copy book use, or real/private/only-copy write-safety claim was added.

## Final recommendation

Next owner action: copied-book dry-run only.

The owner should use an outside-git copied/restorable book, keep the original untouched, create an independent backup and restore plan, run local-only dry-run tooling, record redacted evidence only, and reset back to `GNUCASH_WRITES_ENABLED=false`.

CREATE-one is not the immediate owner step. It can be considered only after owner dry-run evidence review confirms preflight, backup, redaction, local-only runtime, restore plan, compatibility/restore evidence boundaries, and default-disabled reset.

## Artifacts

- `docs/release/v0.2.8-writealpha-notes.md`
- `docs/release/v0.2.8-writealpha-checklist.md`
- `docs/release/v0.2.8-writealpha-final-gate.md`
- `docs/release/v0.2.8-writealpha-publication-evidence.md`
- `docs/handoff/phase-261.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- README/README.ru/docs/ROADMAP public status updates
- `scripts/check_public_status.py`
- `apps/api/tests/test_public_status_guard.py`

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- The backend `APP_ENV=test` write-alpha gate was not changed or weakened.
- Write-alpha remains experimental/pre-alpha and local-only when explicitly enabled.
- Evidence for this cycle remains synthetic/disposable plus bounded release documentation; owner copied-book dry-run may still be pending.
- No owner/private/original/only-copy book was used, requested, mutated, or committed.
- No app DB, GnuCash book, backup, CSV, screenshot, `.env`, token, key, cert, raw path, account name, memo, amount, API payload, cookie, or private financial data artifact was committed.
- No production, security-audited, public-internet, production disaster-recovery, broad Desktop/version compatibility, or real/private/only-copy write-safety claim was added.

## Verification performed

```bash
# PM release/no-release decision subprocess: AUTHORIZE_RELEASE
python3 scripts/check_public_status.py
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
grep -n 'GNUCASH_WRITES_ENABLED' .env.example
grep -R "GNUCASH_WRITES_ENABLED" -n .env.example docker-compose.yml apps || true
grep -R "gnucash_writes_enabled" -n apps/api || true
grep -R "APP_ENV=test" -n README.md docs apps || true
grep -R "localStorage\|sessionStorage" -n apps/web/src || true
git diff --check
# sensitive tracked-file hygiene scan
# push release/status commit, wait exact commit CI success
# publish annotated tag + GitHub pre-release, verify tag/release target
```

Results:

- PM decision: `AUTHORIZE_RELEASE`.
- Public status guard: PASS.
- Backend tests: PASS.
- Frontend checks/auth-route tests/build: PASS.
- Docker Compose config: PASS.
- Rendered Docker Compose default: `GNUCASH_WRITES_ENABLED=false` for API and web.
- Safety greps: PASS; browser storage remains theme-only `localStorage` use.
- Git whitespace check: PASS.
- Sensitive tracked-file hygiene scan: PASS.
- Exact release/status commit CI: PASS before publication.
- Publication verification: local tag, remote tag, and GitHub pre-release point to the intended release/status commit.

## GitHub issues

No new GitHub issue was created. Phase 261 is a release/no-release gate and final recommendation phase within the existing controlled-write readiness umbrella (#36).

## Final 30-phase stop point

Completed phases: 232–261.

Published releases during the 30-phase plan:

- `v0.2.6-writealpha` in Phase 241.
- `v0.2.7-writealpha` in Phase 251.
- `v0.2.8-writealpha` in Phase 261.

No phase authorized real/private/original/only-copy write safety. The safe stop point is owner copied-book dry-run only, not owner CREATE-one and not v0.3 planning.
