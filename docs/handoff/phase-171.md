# Phase 171 — v0.1.7-readonly release gate and authorized publication

Date: 2026-05-20
Status: COMPLETE — release artifacts committed, release commit CI passed, tag/GitHub pre-release published and verified
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 10/10 only)

## Goal

Prepare the next read-only maintenance release artifact after Phases 162–170 and publish only if the gate is green and the task scope authorizes publication.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-170.md`;
  - roadmap phase 10 and shared safety constraints from `cycle-2-roadmap.md`.
- Kept this as Phase 171 only; no cycle 3 phase or neighboring phase was started.
- Chose candidate tag `v0.1.7-readonly`, matching the existing release history after `v0.1.6-readonly`.
- Confirmed starting state before release artifacts:
  - branch `main`;
  - `HEAD == origin/main == cec8e5ed07d83335efcd5af72be89494ff932c0f`;
  - tracked tree clean, with only untracked repo-local `.hermes/` agent logs ignored;
  - no local `v0.1.7-readonly` tag;
  - no GitHub release named `v0.1.7-readonly`;
  - GitHub Actions CI for starting HEAD completed with `success`.
- Prepared conservative release artifacts:
  - `docs/release/v0.1.7-readonly-notes.md`;
  - `docs/release/v0.1.7-readonly-checklist.md`;
  - `docs/release/v0.1.7-readonly-final-gate.md`;
  - `docs/release/v0.1.7-readonly-publication-evidence.md`.
- Synchronized status docs for the release gate:
  - `README.md`;
  - `CHANGELOG.md`;
  - `PROJECT_STATUS.md`;
  - this handoff.
- Committed and pushed the Phase 171 release-gate artifacts to `origin/main` at `d248b5a355ed2b57913d0c408e643b5f6cfcfe5b`.
- Waited for GitHub Actions on the exact release commit to pass (`run 26116039298`).
- Re-checked final publication gates before tagging: clean `main`, `HEAD == origin/main`, tag/release absence, write-disabled defaults, and sensitive tracked-file hygiene.
- Published annotated tag and GitHub pre-release `v0.1.7-readonly`.
- Updated post-publication release/status artifacts to record the published state.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default and was verified in rendered Compose config.
- Production writes were not enabled.
- Controlled writes were not promoted; they remain post-MVP/write-alpha, experimental, disabled by default, and outside this read-only release scope.
- No backend/frontend product code, Docker runtime default, write route, write-mode UI, package, binary artifact, Docker image, production deployment, real/private book, app DB, backup, committed `.env`, screenshot/export, token, key, cert, private path, or private financial data was added.
- Release language remains conservative: pre-alpha, not production-ready, not security-audited, test disposable/copy books first, do not expose directly to public internet.

## Verification before release artifact commit

```bash
git status --short --branch
git fetch origin main --tags --prune
git rev-parse HEAD
git rev-parse origin/main
git tag --list 'v0.1.7-readonly'
gh release view v0.1.7-readonly --json tagName,url,isPrerelease,isDraft 2>&1 || true
gh run list --branch main --limit 5 --json status,conclusion,headSha,workflowName,createdAt,url
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results:

- Starting tracked tree was clean except untracked `.hermes/` local agent logs.
- Starting `HEAD` and `origin/main` matched at `cec8e5ed07d83335efcd5af72be89494ff932c0f`.
- `v0.1.7-readonly` local tag was absent.
- `v0.1.7-readonly` GitHub release was absent.
- GitHub Actions CI for starting HEAD `cec8e5ed07d83335efcd5af72be89494ff932c0f` passed (`run 26115370807`).
- Backend full suite passed: `395 passed, 32 warnings`.
- Frontend `npm run check` passed: `0 errors and 0 warnings`.
- Frontend auth/static route checks passed.
- Frontend production build passed.
- Docker Compose config validation passed.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed before artifact edits.
- Sensitive tracked-file hygiene scan passed.

## Publication state

Publication completed in Phase 171 after all gates were green:

1. Phase 171 release artifact/status update was committed and pushed: `d248b5a355ed2b57913d0c408e643b5f6cfcfe5b`.
2. GitHub Actions CI on the exact Phase 171 release commit completed successfully (`run 26116039298`).
3. Final checks confirmed clean tracked tree, `HEAD == origin/main`, local/remote tag absence, GitHub release absence, `GNUCASH_WRITES_ENABLED=false`, and sensitive tracked-file hygiene before publication.
4. Annotated tag `v0.1.7-readonly` was created and pushed.
5. GitHub pre-release was created and verified: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.7-readonly
6. No package, binary artifact, Docker image, or production deployment was created.

## Files changed

- `docs/release/v0.1.7-readonly-notes.md`
- `docs/release/v0.1.7-readonly-checklist.md`
- `docs/release/v0.1.7-readonly-final-gate.md`
- `docs/release/v0.1.7-readonly-publication-evidence.md`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-171.md`
