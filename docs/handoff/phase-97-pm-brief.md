# Phase 97 PM Brief — v0.1.1-readonly release-prep checklist and notes

Date: 2026-05-18
Role: Project Lead / PM
Status: planned for engineer implementation
Source roadmap: `docs/audits/2026-05-18-analyst-10-phase-plan.md`
Previous phase evidence: `docs/handoff/phase-96.md`

## Decision

Plan Phase 97 as the next practical release-value phase: prepare conservative `v0.1.1-readonly` release notes and a release-prep checklist now that Phase 95 fixed GitHub #39 and Phase 96 confirmed the CSV export behavior with synthetic benchmark evidence.

## Why this phase now

The analyst roadmap made GitHub #39 the primary blocker before `v0.1.1-readonly`. Current `PROJECT_STATUS.md` shows Phase 95 completed the CSV export row-count/header mismatch fix, and Phase 96 confirmed it through a 1,000-transaction synthetic large-export benchmark with matching CSV body rows, total, limit, and truncation metadata. The next unfinished practical phase from the 10-phase roadmap is Phase 97: release preparation, not publication.

This is release-value work, not audit-only work. It should create useful release artifacts for the next engineer/controller step while preserving conservative pre-alpha language and avoiding any release/tag publication.

## Goal

Prepare honest, conservative `v0.1.1-readonly` release notes and a release-prep checklist that summarize post-`v0.1.0-readonly` maintenance changes, required checks, known limitations, and explicit non-claims before any publication phase.

## Non-goals

- Do not publish `v0.1.1-readonly`, create a git tag, create a GitHub release, or upload packages.
- Do not run a full release gate in this phase; final gate verification belongs to Phase 98.
- Do not claim production readiness, security audit completion, broad GnuCash compatibility, or personal-book dogfood success.
- Do not close GitHub #38 unless Val has provided/approved a safe copied personal GnuCash SQL book outside git and a later dogfood phase passes.
- Do not start v0.2 controlled-write planning or expand write capability.
- Do not enable `GNUCASH_WRITES_ENABLED=true` by default or change write routes/UI behavior.
- Do not use, create, commit, screenshot, or export real/private financial data.
- Do not do broad markdown cleanup or backlog theater beyond release-prep artifacts and necessary status/handoff updates.

## Acceptance criteria

- `docs/release/v0.1.1-readonly-notes.md` exists and is suitable as draft GitHub pre-release notes for a future publish phase.
- `docs/release/v0.1.1-readonly-checklist.md` exists and clearly separates:
  - already completed evidence from Phases 95–96;
  - required Phase 98 release-gate checks;
  - publish steps that are intentionally not authorized in Phase 97;
  - known limitations and open issues.
- Release language stays conservative: pre-alpha, read-only by default, not production-ready, not security-audited, use disposable/test copies first, do not expose directly to the public internet, controlled writes experimental/post-MVP and disabled by default.
- Notes include the Phase 95 CSV export fix and Phase 96 synthetic benchmark evidence without overclaiming performance or production readiness.
- Notes mention that GitHub #39 is fixed/closed based on synthetic evidence, while GitHub #38 remains open/blocked until safe copied personal-book dogfood is possible.
- `CHANGELOG.md` and `PROJECT_STATUS.md` are updated only as needed to record candidate preparation, not publication.
- `docs/handoff/phase-97.md` is created with evidence, commands, safety statement, files changed, release status, and commit/push details.
- No new tag/release exists as a result of Phase 97.
- No real/private financial data, GnuCash books, app DBs, backups, `.env`, secrets, tokens, certs, keys, screenshots, or private CSV exports are committed.

## Safety checks

- Confirm `GNUCASH_WRITES_ENABLED=false` remains the documented/default posture in settings/examples/docs touched by this phase.
- Treat controlled writes as experimental post-MVP only; do not market or imply safe production write mode.
- Preserve the MVP model: one local admin user, one default book, read-only access.
- Keep GnuCash Desktop positioned as the authoritative editor.
- Do not add production-ready, security-audited, broad compatibility, hosted SaaS, family-wallet, or collaborative-accounting claims.
- Use only existing synthetic benchmark evidence from committed docs/status; do not generate or commit private data.
- If any release note references checks, distinguish between checks already run in Phase 95/96 and checks still required before publishing.

## Verification required from engineer

Minimum expected commands for a docs/release-prep-only implementation:

```bash
git diff --check
```

Also inspect generated release files for conservative wording and absence of publication commands being presented as already done.

If touching frontend/backend code unexpectedly, stop and justify why; then run the relevant full checks:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

For GitHub/release state, use `gh` only if authenticated. If `gh auth status` reports invalid auth, do not block local release-prep docs; record that publication/release state checks need authenticated `gh` or controller verification later.

The Phase 97 report must include: release notes path, checklist path, whether any tag/release was created, GitHub #39/#38 status, safety statement, verification summary, commit hash, and push status.

## Files/docs to update

Expected files:

- `docs/release/v0.1.1-readonly-notes.md` — new draft release notes.
- `docs/release/v0.1.1-readonly-checklist.md` — new release-prep checklist.
- `CHANGELOG.md` — add an Unreleased entry for Phase 97 release-prep artifacts if consistent with current changelog structure.
- `PROJECT_STATUS.md` — advance completed phase/status after implementation and set the next planned phase to Phase 98 release-gate verification.
- `docs/handoff/phase-97.md` — completion handoff.

Do not modify historical handoff documents except to add forward references only if absolutely necessary.

## GitHub/backlog note

- GitHub #39 should remain closed; do not reopen it unless release-prep inspection finds concrete evidence that the CSV export mismatch is still present.
- GitHub #38 remains open and separate for copied personal-book dogfood. Do not claim personal-book success.
- Do not create new GitHub issues unless a concrete release-prep blocker is discovered and cannot be fixed narrowly.
- Do not publish a GitHub release in Phase 97. Publishing is reserved for a later phase and requires a passing release gate plus explicit authorization.

## Exact engineer instructions

1. Start from current `main`; verify `git status --short` is clean.
2. Read `AGENTS.md`, `PROJECT_STATUS.md`, this PM brief, `docs/handoff/phase-96.md`, and `docs/audits/2026-05-18-analyst-10-phase-plan.md`.
3. Confirm Phase 95 and Phase 96 are complete in status/handoff docs, and that Phase 97 is the next unfinished roadmap phase.
4. Create `docs/release/v0.1.1-readonly-notes.md` with conservative draft release notes. Include:
   - pre-alpha/read-only/default-write-disabled warnings;
   - summary of maintenance value since `v0.1.0-readonly`, especially the Phase 95 CSV export fix and Phase 96 benchmark confirmation;
   - known limitations including #38 blocked personal-book dogfood and narrow compatibility evidence;
   - explicit “not published yet” or draft status if appropriate for the artifact.
5. Create `docs/release/v0.1.1-readonly-checklist.md` with required release-gate checks and publication preconditions. Make publication commands placeholders/instructions for a later authorized phase, not actions already taken.
6. Update `CHANGELOG.md` and `PROJECT_STATUS.md` narrowly for Phase 97 after implementation.
7. Create `docs/handoff/phase-97.md` with the implementation summary, safety statement, verification, GitHub/backlog note, and next recommended Phase 98 release-gate verification.
8. Run `git diff --check`. Run additional tests only if product code changes unexpectedly.
9. Verify no `v0.1.1-readonly` tag or GitHub release was created by this phase. If `gh` auth is invalid, record the limitation instead of fabricating GitHub evidence.
10. Commit with a concise message such as `docs: prepare v0.1.1 release notes`, push to `origin/main`, and leave `git status --short` clean.

## Required Telegram phase report contents

The engineer's Telegram report to Val must be in Russian and include:

- Phase 97 title and one-sentence result.
- Paths to the release notes, checklist, and handoff.
- Confirmation that no tag/release was published.
- GitHub #39 state and #38 reminder/blocker.
- Safety statement: writes remain disabled by default; controlled writes remain post-MVP/experimental; no real/private financial data committed.
- Verification summary, including `git diff --check` and any additional checks run.
- Commit hash and push status.
