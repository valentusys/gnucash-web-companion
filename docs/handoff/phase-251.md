# Phase 251 — Cycle 2 release/no-release gate

Date: 2026-05-21

Status: COMPLETE — PM authorized publication; `v0.2.7-writealpha` published as a GitHub pre-release after final gate.

## Summary

Phase 251 made the Cycle 2 release/no-release decision for `v0.2.7-writealpha`.

PM/Project Lead was called because this phase explicitly required a release/no-release decision. PM returned `AUTHORIZE_RELEASE` for a conservative pre-alpha write-alpha maintenance publication, conditioned on a fresh full local release gate, clean tracked tree, `HEAD == origin/main`, exact release/status commit CI green, and local/remote/GitHub tag/release absence.

The final release gate passed, the release/status commit was pushed, GitHub Actions on the exact commit passed, and `v0.2.7-writealpha` was published as a GitHub pre-release.

## Changes

- Converted `docs/release/v0.2.7-writealpha-notes.md` from candidate draft to published release notes while preserving conservative safety boundaries.
- Updated `docs/release/v0.2.7-writealpha-checklist.md` with PM authorization and final release checklist evidence.
- Updated `docs/release/v0.2.7-writealpha-final-gate.md` from draft gate to final gate.
- Added `docs/release/v0.2.7-writealpha-publication-evidence.md`.
- Updated README/README.ru, CHANGELOG, PROJECT_STATUS, and docs/ROADMAP for Phase 251 and the `v0.2.7-writealpha` publication.
- Updated `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` for the current public write-alpha release baseline.

## Release publication

Published only:

- annotated git tag `v0.2.7-writealpha`;
- GitHub pre-release `v0.2.7-writealpha` using `docs/release/v0.2.7-writealpha-notes.md`.

No package, image, binary artifact, production deployment, write default change, write-scope expansion, `APP_ENV=test` gate weakening, real/private-book safety claim, production/security/public-internet/broad-compatibility claim, or private data artifact was added.

## Verification

```bash
git status --short --branch
git fetch origin main --tags
git rev-parse HEAD origin/main
git tag -l v0.2.7-writealpha
git ls-remote --tags origin refs/tags/v0.2.7-writealpha refs/tags/v0.2.7-writealpha^{}
gh release view v0.2.7-writealpha --json tagName,url,isPrerelease,isDraft,targetCommitish
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
python3 - <<'PY'
# tracked sensitive-file hygiene scan
PY
```

Results:

- PM decision: PASS — `AUTHORIZE_RELEASE`.
- Pre-publication local tag: absent.
- Pre-publication remote tag: absent.
- Pre-publication GitHub release: absent.
- Public status guard: PASS.
- Backend full test suite: PASS.
- Frontend check/auth-route/build: PASS.
- Docker Compose config: PASS.
- Rendered Compose write default: PASS — API and web keep `GNUCASH_WRITES_ENABLED=false`.
- `.env.example` default: PASS — `GNUCASH_WRITES_ENABLED=false`.
- Safety greps: PASS — no default/gate weakening found; browser-storage matches remain limited to theme storage and route checks.
- Git diff whitespace check: PASS.
- Sensitive tracked-file hygiene scan: PASS.
- Exact release/status commit GitHub Actions: PASS before publication.
- Post-publication local tag, remote tag, and GitHub pre-release: PASS, all point to the intended release/status commit.

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Backend `APP_ENV=test` write-alpha gating remains intact.
- Evidence for this release is synthetic/disposable only.
- Ownership guards reduce accidental PATCH/DELETE against historical/manual transactions in this app, but do not make real/private, original, production, shared, or only-copy books safe for write-alpha.
- No real/private book, only-copy book, app DB, backup, `.env`, CSV/export, screenshot, token, key, cert, raw private path, account name, memo, amount, or private financial artifact was used or committed.

## Result

Phase 251 is complete. `v0.2.7-writealpha` is the current public experimental write-alpha GitHub pre-release. The project remains pre-alpha, read-only by default, write-alpha remains explicitly gated and unsafe for real/private or only-copy books.
