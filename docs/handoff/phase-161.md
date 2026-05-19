# Phase 161 — Read-only maintenance release gate

Date: 2026-05-20
Status: DONE — `v0.1.6-readonly` published as authorized GitHub pre-release
Starting HEAD: `d56c335`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 10/10 only)

## Goal

Prepare and, only if safe and explicitly authorized, publish the next read-only maintenance pre-release after Phases 153–160; otherwise mark release `BLOCKED` with exact blockers.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-160.md`;
  - roadmap phase 10 and common safety constraints from `cycle-1-roadmap.md`.
- Kept this as Phase 161 only; no neighboring roadmap phases were started.
- Chose `v0.1.6-readonly` because `v0.1.5-readonly` was already published in Phase 152.
- Re-checked clean `main`, `HEAD == origin/main`, no local tag, no existing GitHub release, and GitHub auth.
- Re-ran full local release checks and sensitive tracked-file hygiene.
- Prepared release notes, checklist, final gate, and publication evidence for `v0.1.6-readonly` with conservative pre-alpha/read-only wording.
- Updated `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff to reflect the actual published release state.
- Committed and pushed the Phase 161 release/status documentation commit.
- Watched GitHub Actions for the Phase 161 release commit to success before publication.
- Created annotated tag `v0.1.6-readonly`, pushed it to origin, and created the GitHub pre-release from `docs/release/v0.1.6-readonly-notes.md`.

## Verification

Local checks:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results: passed. Backend test result: `386 passed, 32 warnings`. Frontend `npm run check`, `npm run test:auth-routes`, and `npm run build` passed. Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web. `git diff --check` passed. Sensitive tracked-file hygiene scan passed.

Release gate checks:

```bash
git status --short --branch
git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
git tag --list 'v0.1.6-readonly'
gh release view v0.1.6-readonly --json tagName,url,isPrerelease,isDraft,targetCommitish
# before publication: release not found
# after release commit push: gh run watch <run-id> --exit-status
# after publication: tag/release view checks
```

Results: passed. Starting tree was clean except untracked `.hermes/`. `HEAD == origin/main` before release docs and after the release commit push. No tag/release collision existed before publication. GitHub Actions for the release commit passed before tag/release creation. After publication, local and remote tag checks and GitHub release view checks passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default and was verified in rendered Compose config.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- Publication created only an annotated git tag and GitHub pre-release; no package, binary, Docker image, production deployment, or write-alpha promotion was published.
- No product code changed in this phase.
- No real/private GnuCash book, `.env`, app DB, backup, screenshot/export, token, key, cert, private path, or private financial data was committed.
- Release notes remain conservative: pre-alpha, read-only by default, not production-ready, not security-audited, test disposable/copy books first, no public-internet exposure claim.

## Files changed

- `docs/release/v0.1.6-readonly-notes.md`
- `docs/release/v0.1.6-readonly-checklist.md`
- `docs/release/v0.1.6-readonly-final-gate.md`
- `docs/release/v0.1.6-readonly-publication-evidence.md`
- `docs/handoff/phase-161.md`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`

## Publication

- Tag: `v0.1.6-readonly`
- GitHub pre-release: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.6-readonly
