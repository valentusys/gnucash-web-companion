# Phase 151 — v0.1.5-readonly maintenance release readiness artifacts

Date: 2026-05-19
Status: DONE
Starting HEAD: `83a0a3f`

## Goal

Prepare release notes/checklist/final gate for possible `v0.1.5-readonly` without publishing.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-150.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 151 only; no PM/auditor was involved and no later roadmap phase was started.
- Prepared `docs/release/v0.1.5-readonly-notes.md` as conservative unpublished release notes summarizing Phases 143–150.
- Prepared `docs/release/v0.1.5-readonly-checklist.md` with candidate scope, evidence, safety checks, reserved publish commands, current blocker, and known limitations.
- Prepared `docs/release/v0.1.5-readonly-final-gate.md` with release-state, local-check, tag/release-absence, sensitive-hygiene, and CI-gate evidence.
- Synchronized public/status docs: `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md`.

## Release verdict

`v0.1.5-readonly` is prepared but unpublished.

Current gate verdict: `Ready for later authorized publish phase — prepared but unpublished`.

Reason: local release-readiness checks passed, no `v0.1.5-readonly` tag/release exists, and GitHub Actions for the Phase 151 pushed commit were watched to success. Phase 151 did not create any tag, GitHub release, package, image, upload, or production deployment. A later authorized release phase must still re-run the final gate immediately before publishing.

## Verification

- `git status --short --branch` before implementation — clean tracked `main...origin/main`; untracked `.hermes/` only.
- `git rev-parse --short HEAD` / `origin/main` before implementation — both `83a0a3f`.
- `git tag --list 'v0.1.5-readonly'` — passed, no output.
- `gh release view v0.1.5-readonly --json tagName,url,isPrerelease,isDraft 2>&1 || true` — passed, `release not found`.
- Initial `gh run list --branch main --limit 5` — latest run for starting HEAD `83a0a3f` completed successfully; the later release phase still must verify green CI for the Phase 151 release commit before publishing.
- Targeted disabled-write/config tests — passed.
- Backend full suite — passed.
- Frontend `npm run check` — passed.
- Frontend `npm run test:auth-routes` — passed.
- Frontend `npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default and is documented in release artifacts.
- Controlled writes remain post-MVP/experimental, disabled by default, and were not expanded or enabled.
- Release language says pre-alpha, read-only by default, not production-ready, not security-audited, and test/disposable/copy books first.
- No backend/frontend product code, endpoint, runtime config, write route, write service, write-mode UI, tag, GitHub release, package, upload, app DB, GnuCash book, backup, `.env`, token, key, cert, screenshot, CSV/private export, private path, or real/private financial data was added.

## Files changed

- `docs/release/v0.1.5-readonly-notes.md`
- `docs/release/v0.1.5-readonly-checklist.md`
- `docs/release/v0.1.5-readonly-final-gate.md`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-151.md`
