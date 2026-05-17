# Phase 58 Audit — v0.1.0-readonly Release Publication

Date: 2026-05-18

## Executive summary

Phase 58 audited the actual `v0.1.0-readonly` publication state requested by the auditor roadmap.

Verdict: Not ready / publication audit blocked.

There is no `v0.1.0-readonly` git tag and no GitHub release for `v0.1.0-readonly`. Therefore the release publication audit cannot validate tag contents, GitHub release notes, release maturity flags, or README links to a published v0.1 release. This is a process blocker, not a read-only boundary failure.

The repository still correctly says v0.1 publication is blocked after Phase 57. Existing blockers #24 and #25 remain the right GitHub tracking issues: conservative v0.1 release notes are missing, and copied/disposable-data runtime smoke/dogfood evidence is not recorded.

## Verdict

Not ready for `v0.1.0-readonly` publication audit / stay pre-release for v0.1.

## Top blockers

1. No `v0.1.0-readonly` git tag exists. Local tag inspection found only the earlier `v0.0.2-prealpha` release tag for the current release line.
2. No GitHub release exists for `v0.1.0-readonly`; `gh release view v0.1.0-readonly` returned `release not found`.
3. Phase 57 blockers remain unresolved: `docs/release/v0.1.0-readonly-notes.md` is still absent, and no copied/disposable-data runtime smoke/dogfood pass is recorded.
4. Because there is no actual v0.1 release, release notes cannot be audited for required language: read-only by default, writes disabled by default, not production-ready, test copied books first, and no collaborative editing.

## Important non-blockers

1. The absence of a v0.1 tag/release is consistent with Phase 57's explicit instruction not to publish until blockers are resolved.
2. The read-only/default-write safety boundary remains intact in inspected code and docs.
3. Existing GitHub issues #24 and #25 already cover the meaningful publication blockers; creating another issue for the same absence would be noisy.
4. Existing open backlog issues #22, #17, #13, #12, and #11 remain useful backlog items but are not newly discovered Phase 58 blockers.

## Product consistency

Checked files and state:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/handoff/phase-57.md`
- auditor roadmap Phase 58 entry
- local git tags and GitHub release state via `gh`

Findings:

- README correctly says Phase 57 completed the `v0.1.0-readonly` release-gate audit and that v0.1 publication is blocked until conservative release notes and copied/disposable-data runtime smoke/dogfood evidence are completed.
- PROJECT_STATUS correctly records completion through Phase 57 and explicitly says not to start publication until blockers are handled by a later explicit phase.
- CHANGELOG records the Phase 57 release-gate blocker state.
- Release plan/checklist are conservative and still prohibit publication when release notes, runtime smoke/dogfood evidence, checks, or clean tree requirements are missing.
- No inspected public doc claims that `v0.1.0-readonly` has already been published.

## Safety boundary

Findings:

- `.env.example` keeps `GNUCASH_WRITES_ENABLED=false`.
- `docker-compose.yml` defaults API and web `GNUCASH_WRITES_ENABLED` to `false`.
- `apps/api/app/config.py` keeps `gnucash_writes_enabled: bool = False`.
- `apps/api/app/routers/transactions.py` calls `_ensure_writes_enabled(settings)` before resolving edit access or constructing `_write_service_for(book)` in validate/create/patch write routes.
- Frontend write UI remains gated by `env.GNUCASH_WRITES_ENABLED === 'true'`, with `transactions/new` redirecting when the flag is not true.
- Controlled writes remain documented as experimental/post-MVP only.

No read-only boundary blocker was found in this Phase 58 audit.

## Release/readme/docs consistency

Findings:

- `v0.1.0-readonly` tag: missing.
- `v0.1.0-readonly` GitHub release: missing.
- `docs/release/v0.1.0-readonly-notes.md`: missing.
- README does not link to a v0.1 release, which is correct because no such release exists.
- CHANGELOG has no dated v0.1 release section, which is correct because no v0.1 release has been published.
- Phase 57's “do not publish yet” status is still the source of truth.

## GitHub project hygiene

Open issues reviewed via `gh issue list`:

- #25 — Complete v0.1 read-only runtime smoke/dogfood gate on copied or disposable data.
- #24 — Prepare conservative v0.1.0-readonly release notes before publication.
- #22 — Add compatibility fixtures from real GnuCash versions.
- #17 — Plan Russian documentation and UI localization.
- #13 — Book management UI.
- #12 — Scheduled/recurring transaction awareness.
- #11 — Transaction search/filter improvements.

No new GitHub issue is required for Phase 58. Issues #24 and #25 already represent the actionable publication blockers, and both received Phase 58 audit comments confirming they remain blockers.

## Security notes

- No new hardcoded JWT secret was found in inspected config/docs.
- `.env.example` still warns not to commit `.env` and requires replacing the JWT secret placeholder.
- README/security/deployment wording remains conservative: not production-ready, not security-audited, do not expose early builds directly to the public internet.
- The audit did not find new auth-token localStorage/sessionStorage use beyond theme preference storage and static tests that prohibit auth storage in browser storage.
- No new real GnuCash book, `.env`, app DB, backup, secret, key, cert, real screenshot, or real financial export was introduced by this audit phase.

## Test/CI notes

Phase 58 is a publication audit with no product-code changes. The release-readiness verdict is based on missing release artifacts plus the existing Phase 57 blockers, not on a green release publication.

Checks run for this phase are recorded in `docs/handoff/phase-58.md`. They include backend tests, frontend checks/build, Docker Compose config validation, and `git diff --check`.

## Recommended next actions

1. Do not publish or advertise `v0.1.0-readonly` from Phase 58.
2. Resolve #24 by creating conservative `docs/release/v0.1.0-readonly-notes.md` that repeats: read-only by default, writes disabled by default, not production-ready, test copied books first, no collaborative editing, no broad compatibility guarantee.
3. Resolve #25 by completing and recording copied/disposable-data Docker/runtime smoke plus manual read-only dogfood evidence.
4. Only after those blockers are resolved, run an explicit publication phase that creates the tag and GitHub pre-release.
5. Then re-run a publication audit against the actual tag/release notes.

## Suggested GitHub issues

Created: none.

Updated:

1. #24 — commented with the Phase 58 audit result and confirmed it remains a publication blocker.
2. #25 — commented with the Phase 58 audit result and confirmed it remains a publication blocker.

Suggested: none beyond existing #24 and #25. Creating a duplicate “v0.1 release missing” issue would be noisy because the missing release is intentional until the release blockers are resolved.

## What not to do next

- Do not treat this Phase 58 audit as approval to publish v0.1.
- Do not create a `v0.1.0-readonly` tag or GitHub release before #24 and #25 are resolved by an explicit later phase.
- Do not mark the project production-ready or security-audited.
- Do not expand controlled writes, enable writes by default, or promote write mode into v0.1.
- Do not add real financial data, copied real books, `.env`, app DBs, backups, secrets, keys, certs, real screenshots, or real CSV exports to git.
- Do not start Phase 59 from this phase.
