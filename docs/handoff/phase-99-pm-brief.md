# Phase 99 PM Brief — v0.1.1-readonly pre-publish dry-run and authorization guard

Date: 2026-05-18
Role: Project Lead / PM
Status: planned for engineer implementation
Source roadmap: `docs/audits/2026-05-18-analyst-10-phase-plan.md`
Previous phase evidence: `docs/handoff/phase-98.md`
Current planning HEAD: `3901d22`

## Decision

Plan Phase 99 as a safe, non-publishing pre-publish dry-run/authorization-guard phase for `v0.1.1-readonly`.

Do not create a git tag, do not create a GitHub release, and do not publish packages in this phase. Val has not given the separate explicit authorization required for publication, so the original roadmap publish step must be converted into a practical non-publishing release-readiness step.

## Why this phase now

`PROJECT_STATUS.md` and `docs/handoff/phase-98.md` show Phases 95–98 are complete and the release gate verdict is `Ready for later authorized publish phase`. The next roadmap slot is Phase 99, but the analyst roadmap explicitly required publication authorization and the repository policy forbids publishing releases unless explicitly requested.

This phase preserves the practical value of Phase 99 without crossing the irreversible/publication boundary: it verifies the exact publish inputs, validates command readiness where safely possible, records the would-publish target commit/tag/notes, and leaves a clear stop point for a later explicitly authorized publish phase.

## Goal

Produce a durable pre-publish dry-run/authorization-guard artifact for `v0.1.1-readonly` that confirms the repository is ready for a later authorized publish, or records exact blockers, while performing no public release action.

Expected artifact: `docs/release/v0.1.1-readonly-prepublish-dry-run.md`.

## Non-goals

- Do not create tag `v0.1.1-readonly`.
- Do not create or edit a GitHub release for `v0.1.1-readonly`.
- Do not upload packages or publish any release artifact.
- Do not run `gh release create` unless it is an explicitly safe help/validation command that cannot mutate GitHub; prefer not to run it at all.
- Do not change backend/frontend product behavior unless a pre-publish blocker is discovered and the controller explicitly moves to a blocker-fix phase.
- Do not start v0.2 controlled-write work or enable writes.
- Do not claim production readiness, audited security, broad GnuCash compatibility, hosted SaaS readiness, personal-book dogfood success, family-wallet positioning, or collaborative accounting.
- Do not use, create, commit, screenshot, or export real/private financial data.

## Acceptance criteria

- `docs/release/v0.1.1-readonly-prepublish-dry-run.md` exists and records:
  - current branch and HEAD;
  - intended tag: `v0.1.1-readonly`;
  - intended release notes file: `docs/release/v0.1.1-readonly-notes.md`;
  - final gate artifact: `docs/release/v0.1.1-readonly-final-gate.md`;
  - confirmation that Phase 98 gate verdict is ready for later authorized publish;
  - local tag absence: `git tag --list 'v0.1.1-readonly'` produces no tag;
  - GitHub release absence: `gh release view v0.1.1-readonly` reports not found, if `gh` is authenticated;
  - recent GitHub Actions state for `main`, if `gh` is authenticated;
  - exact would-run publish commands, clearly marked as NOT EXECUTED;
  - explicit authorization status: absent/not authorized in this phase;
  - final verdict: `Ready for explicit authorized publish` or `Blocked`.
- `docs/handoff/phase-99.md` is created with implementation summary, verification summary, safety statement, changed files, GitHub/backlog note, next recommended phase, and commit/push evidence.
- `PROJECT_STATUS.md` is updated after implementation to mark Phase 99 complete as a non-publishing dry-run/authorization-guard phase and to set the next planned step based on verdict:
  - if ready: wait for explicit Val authorization before any publish/tag/release command, or proceed to the next non-publishing practical roadmap phase if the controller forbids waiting;
  - if blocked: a narrow practical blocker-fix phase.
- `CHANGELOG.md` is updated only if current changelog practice warrants a narrow Unreleased entry for the pre-publish artifact.
- No `v0.1.1-readonly` tag or GitHub release exists as a result of Phase 99.
- No real/private financial data, GnuCash books, app DBs, backups, `.env`, secrets, tokens, certs, keys, screenshots, or private CSV exports are committed.

## Safety checks

- Confirm no publishing command was executed and no public release/tag was created.
- Confirm `GNUCASH_WRITES_ENABLED=false` remains the default/documented posture where inspected or touched.
- Confirm controlled writes remain experimental/post-MVP and are not represented as safe for production books.
- Preserve the MVP model: one installation, one local admin user, one default GnuCash book, read-only access.
- Keep GnuCash Desktop positioned as the authoritative editor.
- Keep release language conservative: pre-alpha, not production-ready, not security-audited, use disposable/test copies first, do not expose directly to the public internet.
- Do not print tokens or secret values. `gh auth status` may mask token output; do not inspect credential files.
- Do not inspect private user directories or personal book paths.

## Verification required from engineer

Run these checks from the repository root unless noted:

```bash
git status --short
git rev-parse --abbrev-ref HEAD
git rev-parse --short HEAD
git tag --list 'v0.1.1-readonly'
test -f docs/release/v0.1.1-readonly-notes.md
test -f docs/release/v0.1.1-readonly-checklist.md
test -f docs/release/v0.1.1-readonly-final-gate.md
git diff --check
```

GitHub/release checks when `gh` is authenticated:

```bash
gh auth status
gh release view v0.1.1-readonly || true
gh run list --limit 10
gh issue view 39 --json number,state,title
gh issue view 38 --json number,state,title
```

Product test suites are not required if the engineer only creates the dry-run/handoff/status artifacts and does not touch product code. If any product code, Docker config, or command documentation that affects behavior is changed, run the relevant checks from `AGENTS.md`:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

## Files/docs to update

Expected files:

- `docs/release/v0.1.1-readonly-prepublish-dry-run.md` — new non-publishing dry-run/authorization-guard artifact.
- `docs/handoff/phase-99.md` — completion handoff with evidence and next step.
- `PROJECT_STATUS.md` — mark Phase 99 complete after implementation and update next planned phase according to the dry-run verdict.
- `CHANGELOG.md` — optional/narrow entry only if consistent with current changelog practice.

Do not modify historical handoff documents except for a narrowly necessary forward-reference correction.

## GitHub/backlog note

- GitHub #39 should remain closed unless concrete CSV export regression evidence is discovered.
- GitHub #38 remains open/blocked for copied personal-book dogfood; do not claim it passed.
- Do not create a GitHub release or tag in this phase.
- Do not create new noisy backlog issues; update existing issues only if the dry-run discovers relevant evidence.
- If the dry-run is green, the backlog state should say publication remains blocked only by missing explicit Val authorization, not by engineering checks.

## Exact engineer instructions

1. Start from current `main`; verify `git status --short` is clean.
2. Read `AGENTS.md`, `PROJECT_STATUS.md`, this PM brief, `docs/handoff/phase-98.md`, `docs/release/v0.1.1-readonly-notes.md`, `docs/release/v0.1.1-readonly-checklist.md`, `docs/release/v0.1.1-readonly-final-gate.md`, and `docs/audits/2026-05-18-analyst-10-phase-plan.md`.
3. Confirm Phases 95–98 are complete and Phase 99 is the next roadmap slot, but publication is not authorized.
4. Run the non-mutating verification commands listed above.
5. Create `docs/release/v0.1.1-readonly-prepublish-dry-run.md` with branch/HEAD, tag/release absence, release notes/checklist/gate artifact presence, GitHub Actions summary when available, would-run publish commands clearly marked `NOT EXECUTED`, authorization status, and final verdict.
6. Do not create a tag. Do not create a GitHub release. Do not publish packages.
7. Create `docs/handoff/phase-99.md` with implementation summary, verification summary, safety statement, changed files, GitHub/backlog note, next recommended phase, and commit/push evidence.
8. Update `PROJECT_STATUS.md` after implementation; update `CHANGELOG.md` only if narrowly appropriate.
9. Run `git diff --check`, commit with a concise message such as `docs: record v0.1.1 prepublish dry run`, push to `origin/main`, and leave `git status --short` clean.

## Required Telegram phase report contents

The engineer's Telegram report to Val must be in Russian and include:

- Phase 99 title and final dry-run verdict: ready for explicit authorized publish, or blocked.
- Paths to the dry-run artifact and handoff.
- Confirmation that no tag/release/package was published.
- Intended tag and release notes file.
- Verification summary: git status/HEAD, tag absence, GitHub release absence, GitHub Actions state if checked, notes/checklist/gate artifact presence, `git diff --check`.
- GitHub #39 state and #38 reminder/blocker.
- Safety statement: writes remain disabled by default; controlled writes remain post-MVP/experimental; no real/private financial data committed.
- Commit hash and push status.
