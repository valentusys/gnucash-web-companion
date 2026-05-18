# Phase 100 PM Brief — Non-publishing synthetic install/upgrade smoke

Date: 2026-05-18
Role: Project Lead / PM
Status: planned for engineer implementation
Source roadmap: `docs/audits/2026-05-18-analyst-10-phase-plan.md`
Previous phase evidence: `docs/handoff/phase-99.md`
Current planning HEAD: `b8471ad`

## Decision

Plan Phase 100 as a non-publishing synthetic/disposable install/upgrade smoke phase on current `main`, not as a post-publication validation of a newly published `v0.1.1-readonly` tag.

Do not create or publish tag `v0.1.1-readonly`, do not create or edit a GitHub release, and do not publish packages. Publication remains reserved for a separate explicit authorization from Val.

## Why this phase now

`PROJECT_STATUS.md` and `docs/handoff/phase-99.md` show Phase 99 is complete: the pre-publish dry-run says `Ready for explicit authorized publish`, but Val has not provided the separate explicit authorization required for any tag/release publication.

The next uncompleted practical roadmap slot is Phase 100. Because Phase 99 publication was deliberately converted to a non-publishing dry-run, Phase 100 must also be adapted safely: run practical install/upgrade-style smoke evidence against current `main` and synthetic/disposable data only, while preserving the no-publish boundary.

## Goal

Validate the current `main` read-only maintenance candidate through a local synthetic/disposable install/upgrade smoke path, covering operator-facing setup basics and core read-only behavior without publishing or requiring real/private financial data.

Expected evidence artifact: `docs/dogfood/phase-100-synthetic-install-upgrade-smoke.md`.

## Non-goals

- Do not publish `v0.1.1-readonly`.
- Do not create tag `v0.1.1-readonly`.
- Do not create or edit a GitHub release.
- Do not publish packages or release artifacts.
- Do not require or use a personal/private GnuCash book.
- Do not claim personal-book dogfood success; GitHub #38 remains separate and blocked until a safe copied book is available.
- Do not enable writes or test write-mode success paths.
- Do not add CSV/OFX import, banking integrations, collaborative accounting, or family-wallet positioning.
- Do not start v0.2 controlled-write expansion.
- Do not commit real financial data, GnuCash books, app DBs, backups, `.env`, screenshots with private data, CSV exports with private data, secrets, tokens, certs, keys, or private paths.

## Acceptance criteria

- `docs/dogfood/phase-100-synthetic-install-upgrade-smoke.md` exists and records:
  - branch and HEAD under test;
  - that no `v0.1.1-readonly` tag/release was published or required;
  - synthetic/disposable data source used;
  - install/config path checked, including Docker Compose config validation;
  - read-only smoke coverage for login/auth, books/default book discovery, dashboard, accounts, transactions, transaction detail where feasible, CSV export, and disabled write probes;
  - any upgrade-style check performed from existing local state, or an honest reason if only fresh/synthetic smoke was feasible in this environment;
  - safety statement and limitations.
- Existing smoke tooling is used where possible, especially `scripts/smoke/read-only-api-smoke.py`, instead of inventing a broad new framework.
- If the smoke exposes a quick-start or smoke-doc drift, fix it narrowly in documentation or the smoke script with tests/compile checks.
- `docs/handoff/phase-100.md` is created with implementation summary, verification summary, safety statement, changed files, GitHub/backlog note, and commit/push evidence.
- `PROJECT_STATUS.md` is updated after implementation to mark Phase 100 complete and to recommend the next practical non-publishing phase unless Val separately authorizes publication.
- `CHANGELOG.md` is updated only if the implementation changes user-visible docs/tooling enough to warrant a narrow Unreleased entry.
- GitHub #38 remains open unless a safe copied personal SQL book is explicitly provided and dogfood actually passes; this phase should not close #38 by synthetic evidence alone.
- No product release/tag/package is published.

## Safety checks

- Before and after the phase, confirm `git tag --list 'v0.1.1-readonly'` and `gh release view v0.1.1-readonly || true`; do not create either.
- Keep `GNUCASH_WRITES_ENABLED=false` in the smoke environment and in documented defaults.
- Disabled write probes must return 403 or the existing automated equivalent must pass.
- Use only synthetic/disposable fixture data. Do not inspect private user directories or personal book paths.
- Keep GnuCash Desktop positioned as the authoritative editor.
- Keep language conservative: pre-alpha, not production-ready, not security-audited, use disposable/test copies first, do not expose directly to the public internet.
- Do not print tokens or secret values. `gh auth status` is allowed because it masks tokens.

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
```

Use existing smoke tooling where feasible. Prefer a command shape like this, adjusted only if the existing script documents different variables/options:

```bash
python3 scripts/smoke/read-only-api-smoke.py --help
python3 -m py_compile scripts/smoke/read-only-api-smoke.py
```

If a local Docker/API stack is started for the smoke, record exact commands and run the smoke against synthetic/disposable data only. If the environment cannot safely start Docker services, record the blocker honestly and still validate config plus script compile/help behavior.

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

- `docs/dogfood/phase-100-synthetic-install-upgrade-smoke.md` — new smoke evidence artifact.
- `docs/handoff/phase-100.md` — implementation handoff with evidence and next step.
- `PROJECT_STATUS.md` — mark Phase 100 complete after implementation and update next planned phase.
- `CHANGELOG.md` — optional/narrow entry only if consistent with the actual changes.
- `scripts/smoke/read-only-api-smoke.py` or `scripts/smoke/read-only-smoke-check.md` — only if the smoke run discovers a concrete, narrow tooling/doc gap.

Do not modify historical handoff documents except for a narrowly necessary forward-reference correction.

## GitHub/backlog note

- Do not create a GitHub release or tag in this phase.
- GitHub #39 should remain closed unless concrete CSV export regression evidence is discovered.
- GitHub #38 remains open/blocked for copied personal-book dogfood; synthetic Phase 100 evidence must not be used to close it.
- GitHub #22 remains open for broader compatibility evidence; do not make broad compatibility claims.
- If a smoke failure exposes a real bug, either fix it narrowly in Phase 100 if small and in-scope, or leave a precise follow-up note/update an existing issue rather than creating backlog noise.

## Exact engineer instructions

1. Start from current `main`; verify `git status --short` is clean.
2. Read `AGENTS.md`, `PROJECT_STATUS.md`, this PM brief, `docs/handoff/phase-99.md`, `docs/release/v0.1.1-readonly-prepublish-dry-run.md`, `scripts/smoke/read-only-smoke-check.md`, and `docs/audits/2026-05-18-analyst-10-phase-plan.md`.
3. Confirm Phase 99 completed without publication and that publication remains unauthorized.
4. Run the non-mutating release-boundary checks: branch/HEAD, tag absence, GitHub release absence.
5. Validate Docker Compose config with dummy secrets.
6. Inspect/use existing read-only smoke tooling. Compile/help-check the smoke script at minimum.
7. If feasible in this environment, run a local Docker/API smoke against synthetic/disposable data with `GNUCASH_WRITES_ENABLED=false`; cover login/auth, books/default book, dashboard, accounts, transactions, CSV export, and disabled write probes. If not feasible, document the exact blocker and the completed substitute checks.
8. Create `docs/dogfood/phase-100-synthetic-install-upgrade-smoke.md` with the evidence, limits, and safety statement.
9. Create `docs/handoff/phase-100.md` with implementation summary, verification summary, safety statement, changed files, GitHub/backlog note, risks/follow-up, and commit/push evidence.
10. Update `PROJECT_STATUS.md` after implementation; update `CHANGELOG.md` only if narrowly appropriate.
11. Do not create a tag, GitHub release, package, private screenshot, private export, or real-book artifact.
12. Run `git diff --check`, commit and push to `origin/main`, and leave `git status --short` clean.

## Required Telegram phase report contents

The engineer's Telegram report to Val must be in Russian and include:

- Phase 100 title and final smoke verdict: passed, partially passed with blocker, or failed.
- Paths to the smoke evidence artifact and handoff.
- Confirmation that no tag/release/package was published.
- Branch/HEAD tested and whether tag/release absence was checked.
- Synthetic/disposable data source used; explicit statement that no real/private financial data was committed.
- Verification summary: Docker Compose config, smoke script compile/help, local API/Docker smoke if run, disabled write probe result, and `git diff --check`.
- GitHub #39 remains closed unless regression found; GitHub #38 remains open/blocked unless a safe copied book was explicitly provided and tested.
- Safety statement: writes remain disabled by default; controlled writes remain post-MVP/experimental; GnuCash Desktop remains authoritative editor.
- Commit hash and push status.
