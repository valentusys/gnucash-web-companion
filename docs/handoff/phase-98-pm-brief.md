# Phase 98 PM Brief — v0.1.1-readonly release-gate verification

Date: 2026-05-18
Role: Project Lead / PM
Status: planned for engineer implementation
Source roadmap: `docs/audits/2026-05-18-analyst-10-phase-plan.md`
Previous phase evidence: `docs/handoff/phase-97.md`

## Decision

Plan Phase 98 as the next unfinished practical phase from the 10-phase roadmap: run the final `v0.1.1-readonly` release-gate verification and produce a gate artifact before any publication step.

## Why this phase now

`PROJECT_STATUS.md` and `docs/handoff/phase-97.md` show that Phases 95, 96, and 97 are complete: the CSV export row-count/header mismatch was fixed, the large synthetic export benchmark confirmed the fix, and conservative `v0.1.1-readonly` release-prep notes/checklist were created. The next planned and not-yet-completed roadmap item is Phase 98: release-gate verification.

This is practical release-value work, not audit-only work. It must execute and record concrete checks against the current `main` HEAD and return an honest ready/blocked verdict. It must not publish a tag or GitHub release.

## Goal

Run final release-gate checks for the `v0.1.1-readonly` maintenance candidate and create `docs/release/v0.1.1-readonly-final-gate.md` with an honest verdict: ready to publish in a later explicitly authorized phase, or blocked with exact blockers.

## Non-goals

- Do not publish `v0.1.1-readonly`, create a git tag, create a GitHub release, or upload packages.
- Do not implement unrelated product features or broad cleanup.
- Do not start v0.2 controlled-write planning or expand write capability.
- Do not enable `GNUCASH_WRITES_ENABLED=true` by default.
- Do not claim production readiness, audited security, broad GnuCash compatibility, hosted SaaS readiness, personal-book dogfood success, family-wallet positioning, or collaborative accounting.
- Do not use, create, commit, screenshot, or export real/private financial data.
- Do not close GitHub #38 unless a separate approved copied personal-book dogfood phase actually passes with safe redacted evidence.

## Acceptance criteria

- `docs/release/v0.1.1-readonly-final-gate.md` exists and records:
  - current HEAD/branch checked;
  - release candidate target `v0.1.1-readonly`;
  - backend test result;
  - frontend check/auth-routes/build result;
  - Docker Compose config validation result;
  - read-only/default-write-disabled safety confirmation;
  - sensitive-data hygiene check summary;
  - GitHub Actions state for recent `main` runs when `gh` is authenticated;
  - tag/release absence confirmation before publication;
  - final verdict: `Ready for later authorized publish phase` or `Blocked`.
- `docs/handoff/phase-98.md` is created with implementation summary, verification outputs summary, safety statement, GitHub/backlog note, changed files, and next recommended phase.
- `PROJECT_STATUS.md` is updated after implementation to mark Phase 98 complete and set the next planned phase according to the gate verdict:
  - if ready: Phase 99 publish `v0.1.1-readonly` only if PM/controller explicitly authorizes publication;
  - if blocked: a narrow practical blocker-fix phase.
- `CHANGELOG.md` is updated only if the repository convention needs an Unreleased entry for the release-gate artifact; do not create broad docs churn.
- No `v0.1.1-readonly` tag or GitHub release exists as a result of Phase 98.
- No real/private financial data, GnuCash books, app DBs, backups, `.env`, secrets, tokens, certs, keys, screenshots, or private CSV exports are committed.

## Safety checks

- Confirm `GNUCASH_WRITES_ENABLED=false` remains the documented/default posture in settings/examples/docs touched by this phase.
- Confirm controlled writes remain experimental/post-MVP and are not marketed as safe for production books.
- Preserve the MVP model: one installation, one local admin user, one default GnuCash book, read-only access.
- Keep GnuCash Desktop positioned as the authoritative editor.
- Verify the release-gate artifact uses conservative language: pre-alpha, not production-ready, not security-audited, use disposable/test copies first, do not expose directly to the public internet.
- Run hygiene checks without printing or committing secrets. If a command would expose token contents or private data, do not run it; record a safe alternative.
- Do not inspect private user directories or personal book paths for this phase.

## Verification required from engineer

Run these checks from the repository root unless noted:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
git status --short
```

GitHub/release checks when `gh` is authenticated:

```bash
gh auth status
gh run list --limit 10
git tag --list 'v0.1.1-readonly'
gh release view v0.1.1-readonly || true
gh issue view 39 --json number,state,title
gh issue view 38 --json number,state,title
```

Read-only/write-disabled confirmation must be represented by the backend test suite and/or targeted evidence from existing disabled-write tests. Do not enable writes to perform the release gate.

Sensitive-data hygiene summary should include safe checks such as `git status --short`, review of changed files, and confirmation that no prohibited data classes were added. Do not print secret values.

If any required gate check fails, stop release-gate progression, record the failed command and blocker in `docs/release/v0.1.1-readonly-final-gate.md` and `docs/handoff/phase-98.md`, and set the next planned phase to a narrow practical blocker-fix. Do not publish.

## Files/docs to update

Expected files:

- `docs/release/v0.1.1-readonly-final-gate.md` — new release-gate verdict artifact.
- `docs/handoff/phase-98.md` — completion handoff with evidence and next step.
- `PROJECT_STATUS.md` — mark Phase 98 complete after implementation and update next planned phase based on the verdict.
- `CHANGELOG.md` — optional/narrow entry only if consistent with current changelog practice.

Do not modify historical handoff documents except for a narrowly necessary forward-reference correction.

## GitHub/backlog note

- GitHub #39 should remain closed unless the gate rediscovers concrete CSV export mismatch evidence.
- GitHub #38 remains open/blocked for copied personal-book dogfood; do not claim it passed in Phase 98.
- If the gate is green, the next roadmap step is Phase 99 publish `v0.1.1-readonly`, but only with explicit PM/controller authorization.
- If the gate is blocked, do not create noisy backlog theater. Either fix a narrow blocker if in scope or record one exact follow-up issue/update.
- No GitHub release should be published in Phase 98.

## Exact engineer instructions

1. Start from current `main`; verify `git status --short` is clean.
2. Read `AGENTS.md`, `PROJECT_STATUS.md`, this PM brief, `docs/handoff/phase-97.md`, `docs/release/v0.1.1-readonly-notes.md`, `docs/release/v0.1.1-readonly-checklist.md`, and `docs/audits/2026-05-18-analyst-10-phase-plan.md`.
3. Confirm Phases 95–97 are complete and Phase 98 is the next unfinished roadmap phase.
4. Run the required backend, frontend, Docker, git diff/status, GitHub Actions/release-state, and disabled-write/read-only safety checks listed above.
5. Create `docs/release/v0.1.1-readonly-final-gate.md` with a concise table of checks, command summaries, safety/hygiene results, tag/release state, and final verdict.
6. If all required checks pass, verdict should be `Ready for later authorized publish phase`; do not publish in this phase.
7. If any required check fails, verdict should be `Blocked`; record exact blocker(s), keep publication prohibited, and set the next planned phase to a narrow blocker-fix.
8. Create `docs/handoff/phase-98.md` with the implementation summary, verification summary, safety statement, changed files, GitHub/backlog note, next recommended phase, commit/push evidence.
9. Update `PROJECT_STATUS.md` after implementation; update `CHANGELOG.md` only if narrowly appropriate.
10. Run `git diff --check`, commit with a concise message such as `docs: record v0.1.1 release gate`, push to `origin/main`, and leave `git status --short` clean.

## Required Telegram phase report contents

The engineer's Telegram report to Val must be in Russian and include:

- Phase 98 title and final gate verdict: ready for later authorized publish, or blocked.
- Paths to the final gate artifact and handoff.
- Required check summary: backend, frontend, Docker, GitHub Actions/release state, disabled-write/read-only safety, sensitive-data hygiene.
- Confirmation that no tag/release was published.
- GitHub #39 state and #38 reminder/blocker.
- Safety statement: writes remain disabled by default; controlled writes remain post-MVP/experimental; no real/private financial data committed.
- Commit hash and push status.
