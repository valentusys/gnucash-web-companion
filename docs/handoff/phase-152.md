# Phase 152 — Conditional v0.1.5-readonly release publication

Date: 2026-05-19
Status: DONE
Starting HEAD: `a94a0a3`

## Goal

If Phase 151 says release is warranted and gates are green, publish `v0.1.5-readonly`; otherwise commit a no-release decision artifact.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-151.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 152 only; no PM/auditor was involved and no later roadmap phase was started.
- Re-ran the final release gate for `v0.1.5-readonly`.
- Confirmed the Phase 151 candidate remained warranted and unblocked.
- Published `v0.1.5-readonly` as an authorized GitHub pre-release after the Phase 152 release commit was pushed and CI passed.
- Synchronized release/status docs:
  - `docs/release/v0.1.5-readonly-notes.md`;
  - `docs/release/v0.1.5-readonly-checklist.md`;
  - `docs/release/v0.1.5-readonly-final-gate.md`;
  - `docs/release/v0.1.5-readonly-publication-evidence.md`;
  - `README.md`;
  - `CHANGELOG.md`;
  - `PROJECT_STATUS.md`.

## Release verdict

`v0.1.5-readonly` is published as an authorized GitHub pre-release.

Release URL: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.5-readonly

No no-release decision artifact was needed because the gate was green.

## Verification

Pre-publication:

- `git status --short --branch` before implementation — clean tracked `main...origin/main`; untracked `.hermes/` only.
- `git rev-parse --short HEAD` / `origin/main` before implementation — both `a94a0a3`.
- `git tag --list 'v0.1.5-readonly'` — passed, no output.
- `gh release view v0.1.5-readonly --json tagName,url,isPrerelease,isDraft 2>&1 || true` — passed, `release not found`.
- `gh run list --branch main --limit 10 --json ...` — starting HEAD `a94a0a3` CI completed successfully.
- Targeted disabled-write/config tests — passed (`63 passed, 32 warnings`).
- Backend full suite — passed (`380 passed, 32 warnings`).
- Frontend `npm run check` — passed (`0 errors and 0 warnings`).
- Frontend `npm run test:auth-routes` — passed.
- Frontend `npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.
- GitHub Actions for the Phase 152 release commit — passed before tag/release publication.

Post-publication:

- Local tag `v0.1.5-readonly` exists.
- Remote tag `origin` contains `v0.1.5-readonly`.
- `gh release view v0.1.5-readonly --json tagName,url,isPrerelease,isDraft` reports the expected release URL, `isPrerelease=true`, and `isDraft=false`.
- `HEAD == origin/main` verified after push.
- `git status --short` clean except untracked `.hermes/`.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default and is documented in release artifacts.
- Controlled writes remain post-MVP/experimental, disabled by default, and were not expanded or enabled.
- Release language says pre-alpha, read-only by default, not production-ready, not security-audited, and test/disposable/copy books first.
- No backend/frontend product code, endpoint, runtime config, write route, write service, write-mode UI, package, Docker image, production deployment, app DB, GnuCash book, backup, `.env`, token, key, cert, screenshot, CSV/private export, private path, or real/private financial data was added.

## Files changed

- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/release/v0.1.5-readonly-notes.md`
- `docs/release/v0.1.5-readonly-checklist.md`
- `docs/release/v0.1.5-readonly-final-gate.md`
- `docs/release/v0.1.5-readonly-publication-evidence.md`
- `docs/handoff/phase-152.md`
