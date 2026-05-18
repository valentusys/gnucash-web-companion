# Phase 59 Audit — Post-Release Regression Risk

Date: 2026-05-18

## Executive summary

Phase 59 audited the auditor-roadmap question: whether commits after `v0.1.0-readonly` accidentally changed the assumptions of that release.

Verdict: not applicable as a post-v0.1 regression audit / stay pre-release for v0.1.

There is still no `v0.1.0-readonly` git tag and no GitHub release. Therefore there are no post-v0.1 commits to compare against a published v0.1 release baseline. The correct risk finding is process-related: do not treat Phase 59 completion as evidence that a v0.1 release exists or that post-release regression risk has been fully assessed.

The inspected commits after Phase 58 are limited to this Phase 59 audit/status work. No product feature work, write-scope expansion, or release publication was performed in this phase.

## Verdict

Not applicable as a post-v0.1 regression audit; stay pre-release for v0.1.

## Top blockers

1. No `v0.1.0-readonly` git tag exists, so there is no release baseline for a true post-release regression comparison.
2. No GitHub release exists for `v0.1.0-readonly`; `gh release view v0.1.0-readonly` returned `release not found`.
3. Existing Phase 57/58 blockers remain unresolved: conservative v0.1 release notes are missing, and copied/disposable-data runtime smoke/dogfood evidence is not recorded.
4. Because v0.1 has not been published, the roadmap check “new commits after v0.1 do not silently expand scope” cannot be completed as written.

## Important non-blockers

1. README still distinguishes the latest public release (`v0.0.2-prealpha`) from current `main` and explicitly says no `v0.1.0-readonly` tag/release has been published.
2. PROJECT_STATUS records post-v0.1 planning/audit work and carries forward the unresolved v0.1 publication blockers.
3. Open GitHub issues #24 and #25 already track the meaningful v0.1 publication blockers; duplicate “post-release regression” issues would be noisy while no v0.1 release exists.
4. The read-only/default-write safety boundary remains intact in inspected config, routes, docs, and tests.

## Product consistency

Checked files and state:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/handoff/phase-58.md`
- auditor roadmap Phase 59 entry
- local git history/tags
- GitHub release and open issue state via `gh`
- backend config/write routes
- frontend static route safety checks through the test suite

Findings:

- README correctly says Phase 0–58 were complete before this phase, identifies `v0.0.2-prealpha` as the current public pre-alpha release, and says no `v0.1.0-readonly` publication exists yet.
- PROJECT_STATUS correctly records completion through Phase 58 before this phase and carries forward the Phase 57/58 release-publication blockers.
- CHANGELOG records the Phase 57/58 v0.1 gate/publication-audit results without claiming a v0.1 release.
- The v0.1 plan/checklist remain conservative and still block publication when release notes, runtime smoke/dogfood evidence, checks, or clean-tree requirements are missing.
- No inspected current doc claims the project is SaaS, a GnuCash replacement, collaborative accounting, production-ready, security-audited, or safe for write mode.

## Safety boundary

Findings:

- `.env.example` keeps `GNUCASH_WRITES_ENABLED=false`.
- `docker-compose.yml` defaults API and web `GNUCASH_WRITES_ENABLED` to `false`.
- `apps/api/app/config.py` keeps `gnucash_writes_enabled: bool = False`.
- `apps/api/app/routers/transactions.py` still calls `_ensure_writes_enabled(settings)` before resolving edit access or constructing `_write_service_for(book)` in validate/create/patch write routes.
- Frontend write UI remains gated by `GNUCASH_WRITES_ENABLED === 'true'` and the committed `test:auth-routes` check covers write UI safety expectations.
- Controlled writes remain documented as experimental/post-MVP only.

No read-only boundary blocker was found in this Phase 59 audit.

## Release/readme/docs consistency

Findings:

- `v0.1.0-readonly` tag: missing.
- `v0.1.0-readonly` GitHub release: missing.
- `docs/release/v0.1.0-readonly-notes.md`: still missing.
- README does not link to a v0.1 release, which is correct because no such release exists.
- README distinguishes latest release vs main: current public release is `v0.0.2-prealpha`; main is now beyond that and still pre-alpha/MVP in progress.
- PROJECT_STATUS records the v0.1 release-gate/publication-audit blockers rather than claiming v0.1 has shipped.
- CHANGELOG has no dated v0.1 release section, which remains correct.

## GitHub project hygiene

Open issues reviewed via `gh issue list`:

- #25 — Complete v0.1 read-only runtime smoke/dogfood gate on copied or disposable data.
- #24 — Prepare conservative v0.1.0-readonly release notes before publication.
- #22 — Add compatibility fixtures from real GnuCash versions.
- #17 — Plan Russian documentation and UI localization.
- #13 — Book management UI.
- #12 — Scheduled/recurring transaction awareness.
- #11 — Transaction search/filter improvements.

No new GitHub issue is required for Phase 59. Issues #24 and #25 remain the actionable blockers before any v0.1 publication or true post-v0.1 regression audit. They were updated with a Phase 59 note confirming that post-release regression audit is not applicable until v0.1 exists.

## Security notes

- No new hardcoded JWT secret was found in inspected config/docs.
- `.env.example` still warns not to commit `.env` and requires replacing the JWT secret placeholder.
- README/security/deployment wording remains conservative: not production-ready, not security-audited, and do not expose early builds directly to the public internet.
- The audit did not find auth-token localStorage/sessionStorage use beyond allowed non-auth preference storage and static tests that prohibit auth storage in browser storage.
- No real GnuCash book, `.env`, app DB, backup, secret, key, cert, real screenshot, or real financial export was added by this phase.

## Test/CI notes

Phase 59 is audit/status documentation work with no product-code changes. Because it still reports a release/readiness verdict, it is backed by full local checks rather than only markdown checks:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `git diff --check`

Final results are recorded in `docs/handoff/phase-59.md`.

## Recommended next actions

1. Do not publish, advertise, or treat `v0.1.0-readonly` as existing from Phase 59.
2. Resolve #24 by creating conservative `docs/release/v0.1.0-readonly-notes.md` with explicit read-only/default-write/no-production/no-security-audit/test-copied-book/no-collaboration language.
3. Resolve #25 by completing and recording copied/disposable-data Docker/runtime smoke plus manual read-only dogfood evidence.
4. Only after #24 and #25 are resolved, run an explicit publication phase for the tag/GitHub pre-release.
5. After actual publication, rerun a true post-release regression audit against the published v0.1 baseline.

## Suggested GitHub issues

Created: none.

Updated:

1. #24 — commented with the Phase 59 audit result and confirmed it remains a prerequisite before v0.1 publication.
2. #25 — commented with the Phase 59 audit result and confirmed it remains a prerequisite before v0.1 publication.

Suggested: none beyond existing #24 and #25. Creating a new post-release regression issue before v0.1 exists would be backlog noise.

## What not to do next

- Do not treat Phase 59 completion as a passed post-v0.1 regression audit.
- Do not create a `v0.1.0-readonly` tag or GitHub release before #24 and #25 are resolved by an explicit later phase.
- Do not mark the project production-ready or security-audited.
- Do not expand controlled writes, enable writes by default, or promote write mode into v0.1.
- Do not add real financial data, copied real books, `.env`, app DBs, backups, secrets, keys, certs, real screenshots, or real CSV exports to git.
- Do not start Phase 60 from this phase.
