# Phase 240 handoff — v0.2.6 release-candidate preparation

Date: 2026-05-21
Status: COMPLETE — `v0.2.6-writealpha` release-candidate docs prepared only; no tag or GitHub release published.

## Summary

Phase 240 chose the release-candidate path rather than a no-release verdict because Phases 232–239 produced meaningful operator-safety changes, not only internal churn:

- public status/changelog reconciliation after `v0.2.5-writealpha` publication;
- raw markdown readability improvements for public status docs;
- conservative copied-book dogfood runbook;
- redacted target preflight CLI;
- redacted dogfood evidence schema/helper;
- local-only write-alpha environment guidance;
- redacted non-mutating readiness command/helper coverage;
- synthetic copied-book Docker/Caddy no-mutation dry-run evidence with disabled write probes and checksum proof.

The candidate is explicitly release-candidate only. Phase 240 did not call PM because it did not publish or authorize publication. PM/release gate is required before any later `v0.2.6-writealpha` tag or GitHub pre-release.

## Files changed

- `docs/release/v0.2.6-writealpha-notes.md` — release-candidate notes, safety boundaries, and publication requirements.
- `docs/release/v0.2.6-writealpha-checklist.md` — candidate checklist with publication gates pending.
- `docs/release/v0.2.6-writealpha-final-gate.md` — draft final-gate artifact for the later release/no-release phase.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md` — public/status documentation advanced to Phase 240 without claiming publication.
- `scripts/check_public_status.py`, `apps/api/tests/test_public_status_guard.py` — public-status guard advanced to Phase 240 and extended to cover the `v0.2.6-writealpha` candidate docs.
- `docs/handoff/phase-240.md` — this handoff.

## Verification performed

- Candidate tag/release absence:
  - `git tag -l v0.2.6-writealpha` — absent.
  - `git ls-remote --tags origin refs/tags/v0.2.6-writealpha` — absent.
  - `gh release view v0.2.6-writealpha` — release not found.
- `python3 scripts/check_public_status.py` — passed.
- `cd apps/api && pytest -q` — passed: 550 tests.
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- Rendered Docker Compose grep confirmed API and web keep `GNUCASH_WRITES_ENABLED: "false"`.
- `git diff --check` — passed.
- Safety greps for `GNUCASH_WRITES_ENABLED`, backend `gnucash_writes_enabled`, `APP_ENV=test`, and browser storage were reviewed; no Phase 240 weakening was found. Existing theme-only localStorage remains unrelated to auth/financial data.
- Sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Backend `APP_ENV=test` write-alpha gate was not changed or weakened.
- No write endpoint, write scope, write service behavior, or runtime default changed.
- No create/PATCH/DELETE mutation was run in this phase.
- No real/private/only-copy book was used, opened, copied into git, backed up, mutated, or committed.
- No raw private paths, account names, memos, amounts, payloads, `.env`, app DB, runtime book, backup, CSV, screenshot, token, key, or cert were committed.
- No release/tag/package was published.
- No production readiness, stable release, security audit, public-internet safety, broad compatibility, or real/private-book write-safety claim was added.

## Risks / blockers

No Phase 240 implementation blocker remains.

Publication remains blocked until a later explicit Phase 241-style release/no-release gate calls PM, re-runs final checks on the exact release/status commit, verifies candidate tag/release absence, waits for exact-commit GitHub Actions, and authorizes publication.

## Next

Do not continue to Phase 241 from this session.
