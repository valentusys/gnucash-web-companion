# Phase 101 PM Brief — Copied personal-book dogfood rerun gate (#38)

Date: 2026-05-18
Role: Project Lead / PM
Status: planned for engineer implementation
Source roadmap: `docs/audits/2026-05-18-analyst-10-phase-plan.md`
Previous phase evidence: `docs/handoff/phase-100.md`
Current planning HEAD: `4d13d09`

## Decision

Plan Phase 101 as the next roadmap phase, focused on the copied personal-book dogfood rerun tracked by GitHub #38, with a strict safety gate.

The current repository is already complete through Phase 100, so Phase 99 and Phase 100 are not the next available phases on current `main`. Phase 101 is the next uncompleted practical roadmap slot. It must not publish a tag/release and must not claim dogfood success unless a safe copied GnuCash SQL book path outside the repository is explicitly available to the engineer/controller.

## Why this phase now

`PROJECT_STATUS.md` and `docs/handoff/phase-100.md` show Phase 100 completed the non-publishing synthetic install/API smoke and kept publication unauthorized. The analyst roadmap lists Phase 101 as the next practical dogfood phase after the synthetic smoke. GitHub #38 remains open because synthetic evidence must not be used to claim personal-book dogfood success.

This phase gives the engineer a concrete dogfood/preflight task while preserving the no-private-data and no-publication boundaries. If no safe copied book path is provided, the correct outcome is a redacted blocked result, not fabricated success and not a release claim.

## Goal

Rerun or gate GitHub #38 copied personal-book dogfood against a safe copied GnuCash SQL book outside git, using read-only local-only checks with `GNUCASH_WRITES_ENABLED=false`.

If a safe copied book path is not available in the engineer context, record the blocked status honestly with redacted evidence and leave #38 open.

Expected evidence artifact: `docs/dogfood/phase-101-personal-copied-book-results.md`.

## Non-goals

- Do not publish `v0.1.1-readonly`.
- Do not create or push any tag.
- Do not create or edit a GitHub release.
- Do not publish packages or release artifacts.
- Do not search private directories broadly or guess personal-book locations.
- Do not use a live/original personal GnuCash book; only a safe copied SQL book outside the repository is allowed.
- Do not commit GnuCash books, app DBs, backups, `.env`, screenshots, CSV exports, real account names, real transaction descriptions, real amounts, private paths, secrets, tokens, certs, or keys.
- Do not enable writes or test write-mode success paths.
- Do not claim production readiness, audited security, broad compatibility, family-wallet positioning, or collaborative accounting.
- Do not start v0.2 controlled-write expansion.

## Acceptance criteria

- Engineer verifies current branch/HEAD and starts from a clean working tree.
- Engineer checks whether a safe copied GnuCash SQL book path was explicitly provided by the controller/environment/user context, for example via a documented variable such as `GNUCASH_DOGFOOD_BOOK_PATH`, inline controller instruction, or an existing redacted handoff note.
- If a candidate path is available:
  - confirm it is outside `/home/val/gnucash-web-companion`;
  - confirm it is a copy/disposable test input, not a live authoritative book;
  - run the existing dogfood preflight/helper where available, with output redacted so no private path/account/amount/description data is committed;
  - run local read-only API/browser smoke where feasible with `GNUCASH_WRITES_ENABLED=false`;
  - confirm disabled write probes return 403 or the existing automated equivalent passes;
  - update GitHub #38 with non-sensitive evidence, and close #38 only if the copied-book dogfood genuinely passes.
- If no safe candidate path is available:
  - do not inspect private directories trying to find one;
  - create `docs/dogfood/phase-101-personal-copied-book-results.md` with verdict `BLOCKED — safe copied book path not provided`;
  - keep GitHub #38 open and update it only with the redacted blocked status if `gh` is authenticated;
  - do not claim dogfood success anywhere.
- `docs/handoff/phase-101.md` is created with implementation summary, verification summary, safety statement, changed files, GitHub/backlog note, risks/follow-up, and commit/push evidence.
- `PROJECT_STATUS.md` is updated after implementation to mark Phase 101 complete or blocked, and to recommend the next practical non-publishing step.
- `CHANGELOG.md` is updated only if there is a meaningful user-facing dogfood/tooling/doc outcome; avoid noisy docs churn.
- No release/tag/package is published.

## Safety checks

- Keep `GNUCASH_WRITES_ENABLED=false` for any local stack, API smoke, or browser dogfood.
- Before any dogfood run, confirm the candidate book path is outside the git repository and is a copied/disposable SQL book.
- Redact all private paths, account names, transaction descriptions, memos, amounts, CSV rows, screenshots, and app DB paths from committed docs.
- Never commit the copied book, runtime app DB, backups, `.env`, smoke exports, screenshots, secrets, tokens, certs, or keys.
- If the path is missing or unsafe, stop the dogfood path and record a blocked result.
- Preserve conservative language: pre-alpha, read-only by default, not production-ready, not security-audited, use copied/test books first, do not expose directly to the public internet.
- GnuCash Desktop remains the authoritative editor.
- Do not run any publish command. Publication still requires separate explicit authorization from Val.

## Verification required from engineer

Run these checks from the repository root unless noted:

```bash
git status --short
git rev-parse --abbrev-ref HEAD
git rev-parse --short HEAD
git tag --list 'v0.1.1-readonly'
gh auth status || true
gh release view v0.1.1-readonly || true
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
python3 scripts/smoke/read-only-api-smoke.py --help
python3 -m py_compile scripts/smoke/read-only-api-smoke.py
```

If a safe copied book path is explicitly available, run the narrow preflight/dogfood flow using existing tooling and local-only read-only checks. Suggested shape, adjusted to the actual script options and redaction rules:

```bash
# Example only; use the provided safe copied-book path and do not print it in committed docs.
GNUCASH_WRITES_ENABLED=false SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/read-only-api-smoke.py
```

If backend/frontend/product code changes are made, run the relevant full checks from `AGENTS.md`:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
```

Always run before commit:

```bash
git diff --check
```

## Files/docs to update

Expected files:

- `docs/dogfood/phase-101-personal-copied-book-results.md` — new dogfood/preflight evidence artifact with pass/blocked verdict and redacted details only.
- `docs/handoff/phase-101.md` — implementation handoff with evidence, safety statement, and next step.
- `PROJECT_STATUS.md` — mark Phase 101 outcome after implementation and update next planned phase.
- `CHANGELOG.md` — optional/narrow entry only if consistent with the actual outcome.

Do not modify historical handoff documents except for a narrowly necessary forward-reference correction.

## GitHub/backlog note

- GitHub #38 is the primary issue for this phase.
- Close #38 only if a safe copied personal-book dogfood actually passes with non-sensitive evidence.
- If blocked by missing safe copied book path, keep #38 open and record the blocker without private details.
- GitHub #39 remains closed unless concrete CSV export regression evidence is discovered.
- GitHub #22 remains open for broader compatibility evidence; do not make broad compatibility claims in this phase.
- Do not create a tag or GitHub release.
- Do not create new GitHub issues unless a concrete new bug is found and cannot be handled under existing issues.

## Exact engineer instructions

1. Start from current `main`; verify `git status --short` is clean.
2. Read `AGENTS.md`, `PROJECT_STATUS.md`, this PM brief, `docs/handoff/phase-100.md`, `docs/audits/2026-05-18-analyst-10-phase-plan.md`, `docs/dogfood/personal-readonly-dogfood.md`, and existing smoke/preflight tooling under `scripts/smoke/`.
3. Confirm Phase 100 completed without publication and that publication remains unauthorized.
4. Run the non-mutating release-boundary checks: branch/HEAD, tag absence, GitHub release absence.
5. Check whether a safe copied GnuCash SQL book path was explicitly provided by the controller/environment/user context. Do not search private directories if no path was provided.
6. If a candidate path is provided, verify it is outside the repository and safe to use as a copied/disposable dogfood input. Redact it in committed docs.
7. If safe, run the existing preflight and local read-only dogfood smoke with `GNUCASH_WRITES_ENABLED=false`; include disabled write probes.
8. If no safe path is provided or the candidate is unsafe, stop the dogfood run and record `BLOCKED — safe copied book path not provided/unsafe`.
9. Create `docs/dogfood/phase-101-personal-copied-book-results.md` with pass/blocked verdict, checks performed, redacted evidence, safety statement, and #38 state.
10. Create `docs/handoff/phase-101.md` with implementation summary, verification summary, safety statement, changed files, GitHub/backlog note, risks/follow-up, and commit/push evidence.
11. Update `PROJECT_STATUS.md` after implementation; update `CHANGELOG.md` only if narrowly warranted.
12. Do not create a tag, GitHub release, package, private screenshot, private CSV export, real-book artifact, app DB, backup, or secret artifact.
13. Run `git diff --check`, commit and push to `origin/main`, and leave `git status --short` clean.

## Required Telegram phase report contents

The engineer's Telegram report to Val must be in Russian and include:

- Phase 101 title and verdict: passed, blocked by missing/unsafe copied book, partially passed, or failed.
- Paths to the dogfood/preflight evidence artifact and handoff.
- Whether a safe copied GnuCash SQL book path was explicitly provided; do not reveal private paths.
- If dogfood ran: read-only smoke coverage, disabled write probe result, and whether #38 was updated/closed.
- If blocked: exact redacted blocker and confirmation that #38 remains open.
- Confirmation that no tag/release/package was published.
- Verification summary: branch/HEAD, tag/release absence, Docker Compose config, smoke script compile/help, local API/Docker smoke if run, and `git diff --check`.
- Safety statement: writes remain disabled by default; controlled writes remain post-MVP/experimental; GnuCash Desktop remains authoritative editor; no real/private data was committed.
- Commit hash and push status.
