# Phase 105 PM Brief — v0.1.1-readonly release-docs correction

Date: 2026-05-19
Role: Project Lead / PM
Status: planned for engineer implementation
Source audit: `docs/audits/2026-05-19-analyst-report.md`
Current planning HEAD: `a4d0415`

## Decision

Plan Phase 105 as one narrow release-documentation correction phase that fixes the exact blocker identified by the analyst report: `v0.1.1-readonly` is already published, but public release/status documentation still reads like a draft/unpublished candidate and does not honestly match the tag target after Phase 104.

This phase is documentation/release-metadata correction only. It must not change product code, must not publish a new tag or release, and must not touch write-mode behavior.

## Why

Analyst verdict is `Ready after blockers fixed`. The blocker is release/docs drift:

- GitHub pre-release `v0.1.1-readonly` exists and targets `a4d0415` after Phase 104.
- `README.md` still presents `v0.1.0-readonly` as the current public release.
- `docs/release/v0.1.1-readonly-notes.md` and GitHub release notes still say draft/not published.
- `PROJECT_STATUS.md` and `CHANGELOG.md` do not fully reflect the actual published state and tag scope.

Fixing this drift is a release-facing blocker and should happen before any further feature/backlog work.

## Goal

Synchronize public release/status documentation and GitHub release notes so `v0.1.1-readonly` is honestly represented as already published at tag/commit `a4d0415`, with scope including the actual read-only changes that are inside the tag target, including Phase 103/104 transaction filter/search work.

## Non-goals

- Do not change backend, frontend, tests, build config, Docker runtime config, write services, write routes, or app behavior.
- Do not create a new tag.
- Do not publish a new GitHub release.
- Do not rename or move the existing `v0.1.1-readonly` tag.
- Do not enable or expand write mode.
- Do not set `GNUCASH_WRITES_ENABLED=true` anywhere.
- Do not start v0.2 controlled-write work.
- Do not run personal-book dogfood or search for private GnuCash books.
- Do not create or close GitHub issues.
- Do not claim production readiness, audited security, hosted SaaS readiness, broad compatibility, safe real-book write mode, family-wallet positioning, or collaborative accounting.

## Acceptance criteria

- `README.md` names `v0.1.1-readonly` as the current/latest public read-only pre-alpha release while preserving conservative warnings: pre-alpha, read-only by default, not production-ready, not security-audited, use copied/test data first, do not expose directly to the public internet.
- `PROJECT_STATUS.md` reflects the fact that `v0.1.1-readonly` has been published and that the tag points after Phase 104.
- `CHANGELOG.md` contains a `v0.1.1-readonly` section with the real included scope, including Phase 103 and Phase 104 read-only transaction filter/search changes.
- `docs/release/v0.1.1-readonly-notes.md` no longer says draft, prep-only, not authorized, or not published; it must honestly describe the release as already published.
- GitHub release notes for `v0.1.1-readonly` are synchronized with the corrected local release notes.
- The corrected release notes explicitly acknowledge that the tag target includes Phase 103/104 read-only transaction date-preset and split-memo search changes, or otherwise clearly explain the included scope.
- No product code files are changed.
- No new tag, GitHub release, package, or external release artifact is created.
- Write mode is untouched and remains disabled by default (`GNUCASH_WRITES_ENABLED=false`).
- `docs/handoff/phase-105.md` is updated after implementation with implementation summary, verification, changed docs/release metadata, safety statement, commit/push evidence, and GitHub release-notes sync evidence.
- The existing audit report `docs/audits/2026-05-19-analyst-report.md` is committed if it is still untracked.

## Required instruction for engineer

Всегда правь документацию сразу вместе с фактическим изменением состояния проекта; не оставляй release/status/docs drift на потом.

## Safety checks

- Before editing, confirm current branch and release state:
  - `git status --short --branch`
  - `git rev-parse --abbrev-ref HEAD`
  - `git rev-parse --short HEAD`
  - `git tag --list 'v0.1.1-readonly'`
  - `git show --no-patch --format='%H %s' v0.1.1-readonly`
  - `gh release view v0.1.1-readonly --json tagName,targetCommitish,isDraft,isPrerelease,publishedAt,url || true`
- Preserve read-only safety language everywhere.
- Do not run any command that creates/releases/tags/publishes a new artifact.
- Do not commit `.env`, secrets, tokens, certs, keys, app DBs, backups, real GnuCash books, screenshots, private CSV exports, account names, transaction descriptions, memos, amounts, private paths, or real/private financial data.
- Keep controlled writes described as post-MVP/experimental and disabled by default.

## Verification required from engineer

Because this phase should only change release/status docs and GitHub release notes, full backend/frontend test suites are not mandatory unless product code is accidentally touched. Required checks:

```bash
git status --short --branch
git diff --check
git diff --name-only HEAD
```

Then verify scope:

```bash
git diff --name-only HEAD | grep -Ev '^(README.md|CHANGELOG.md|PROJECT_STATUS.md|docs/release/v0\.1\.1-readonly-notes\.md|docs/handoff/phase-105\.md|docs/audits/2026-05-19-analyst-report\.md)$' && exit 1 || true
```

Verify GitHub release notes after sync:

```bash
gh release view v0.1.1-readonly --json tagName,targetCommitish,isDraft,isPrerelease,publishedAt,body,url
```

Before commit, confirm there are no product code diffs:

```bash
git diff -- apps/ docker-compose.yml pyproject.toml package.json package-lock.json
```

After commit/push:

```bash
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
```

## Files/docs to update

Expected local files:

- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/release/v0.1.1-readonly-notes.md`
- `docs/handoff/phase-105.md`
- `docs/audits/2026-05-19-analyst-report.md` if still untracked

Expected remote metadata:

- GitHub release notes/body for `v0.1.1-readonly`, updated in place to match the corrected local notes.

Do not modify product code or unrelated docs.

## Exact engineer instructions

1. Start from `main`; verify clean tracked tree except for the audit/PM docs expected by this handoff if they are already present.
2. Read `AGENTS.md`, `PROJECT_STATUS.md`, `docs/audits/2026-05-19-analyst-report.md`, and this Phase 105 brief.
3. Confirm `v0.1.1-readonly` tag and GitHub release exist and target current post-Phase-104 HEAD `a4d0415` or its full hash.
4. Update only release/status docs listed above so they no longer describe `v0.1.1-readonly` as draft/not-published and correctly include the actual tag scope.
5. Update GitHub release notes for the existing `v0.1.1-readonly` release in place, using conservative pre-alpha/read-only language.
6. Do not create or publish any new release, tag, package, or artifact.
7. Do not change product code. If any product code file appears in `git diff --name-only`, stop and remove that change unless Val explicitly authorized it.
8. Keep write mode untouched and disabled by default.
9. Update `docs/handoff/phase-105.md` with implementation evidence, verification, GitHub release-note sync evidence, commit hash, push status, and final safety statement.
10. Include the analyst report `docs/audits/2026-05-19-analyst-report.md` in the commit if still untracked.
11. Commit and push with an appropriate implementation message chosen by the engineer, then leave `HEAD == origin/main` and working tree clean.

## Required engineer report contents

The engineer's final report to Val must be in Russian and include:

- Phase 105 title and verdict.
- Which release/docs drift items were corrected.
- Confirmation that GitHub release notes for `v0.1.1-readonly` were synchronized.
- Paths changed, including `docs/handoff/phase-105.md`.
- Commit hash and push status.
- Verification summary: `git diff --check`, changed-file scope, `HEAD == origin/main`, clean working tree.
- Safety statement: no product code, no new tag/release/package, write mode untouched/disabled by default, no private data committed.

## GitHub/backlog

- Do not create or close GitHub issues in this phase.
- Do not publish another release.
- Existing open issues remain as-is.
- After this correction, the project may resume narrow practical read-only backlog work only if release/status/docs drift is resolved.
