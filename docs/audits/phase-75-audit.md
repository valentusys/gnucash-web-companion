# Phase 75 Audit — v0.1.1 Maintenance Release

Date: 2026-05-18

## Executive summary
Phase 75 audited whether a `v0.1.1-readonly` maintenance release should be prepared.

Verdict: No release needed. More precisely, a v0.1.1 maintenance release is not applicable yet because `v0.1.0-readonly` has not been published: no local `v0.1*` tag exists, GitHub releases list only `v0.0.1-prealpha` and `v0.0.2-prealpha`, and `gh release view v0.1.0-readonly` reports `release not found`.

The current repository has no recorded post-v0.1 dogfood bugfix stream to package into a maintenance release. The known release blockers remain #24 and #25: conservative v0.1.0 release notes and copied/disposable-data runtime smoke/dogfood evidence. Preparing v0.1.1 now would be misleading scope drift.

## Verdict
No release needed.

This is not approval to publish `v0.1.0-readonly`, not approval to prepare `v0.1.1-readonly`, not a production-readiness claim, and not a professional security audit.

## Blockers
No new Phase 75 blocker was found for the current pre-alpha/read-only posture.

Blocking conditions before any `v0.1.1-readonly` maintenance release can be considered:

1. `v0.1.0-readonly` does not exist as a git tag or GitHub release.
2. #24 remains open — conservative `v0.1.0-readonly` release notes are still required before initial v0.1 publication.
3. #25 remains open — copied/disposable-data runtime smoke/dogfood evidence is still required before initial v0.1 publication.
4. No completed post-v0.1 dogfood bugfixes, docs fixes, or small read-only UX fixes exist because the base v0.1 release has not happened.

## Important non-blockers
1. Current open read-only hardening issues (#26–#35) are valid backlog items, but they do not create a v0.1.1 release need until after an actual v0.1 baseline exists and PM decides their release scope.
2. Existing controlled-write code remains experimental/post-MVP and disabled by default; it is not part of this maintenance-release decision.
3. The absence of a v0.1.1 maintenance plan is correct while v0.1.0 remains unpublished.

## Audit scope and evidence
Inspected:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `.env.example`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/release/v0.0.2-prealpha-notes.md`
- `docs/release/v0.0.2-prealpha-checklist.md`
- `docs/handoff/phase-74.md`
- `docs/audits/phase-57-audit.md`
- `docs/audits/phase-74-audit.md`
- auditor roadmap file: `/home/val/.hermes/cache/documents/doc_524e3283b5e8_auditor-roadmap-56-75.txt`
- backend write defaults/gating search results
- frontend write UI gating/warning search results
- Git tags, GitHub releases, and relevant open GitHub issues

Git/GitHub evidence:

- `git tag -l 'v0.1*'` returned no tags.
- `gh release list --repo valentusys/gnucash-web-companion --limit 20` listed only `v0.0.2-prealpha` and `v0.0.1-prealpha`.
- `gh release view v0.1.0-readonly --repo valentusys/gnucash-web-companion` returned `release not found`.
- GitHub issues #24 and #25 are open.

## Phase 75 audit checks

### Dogfood bugfixes
Not applicable yet.

No `v0.1.0-readonly` release exists, so there cannot be post-v0.1 dogfood bugfixes to package as `v0.1.1-readonly`. Phase 60 confirmed readiness to start copied-book dogfood, while Phase 61 and subsequent status docs kept actual dogfood/runtime evidence blocked by #25.

### Docs fixes
No v0.1.1-specific docs fix stream exists.

The release notes blocker is still initial-release work, tracked by #24. Treating that as v0.1.1 maintenance work would be incorrect because the initial v0.1 release is not published.

### Small read-only UX fixes
No v0.1.1-specific small read-only UX fix stream exists.

Open read-only hardening issues (#30–#35 and others) remain future backlog/hardening work. They are not post-v0.1 maintenance fixes yet.

### No scope expansion
Pass.

Phase 75 should not add product features, expand write scope, publish any release, or start Phase 76. The accepted safe work is audit/status/handoff documentation and issue hygiene only.

### No write-mode promotion
Pass.

Evidence:

- `.env.example` keeps `GNUCASH_WRITES_ENABLED=false`.
- `apps/api/app/config.py` keeps `gnucash_writes_enabled: bool = False`.
- Backend validate/create/patch write routes still call `_ensure_writes_enabled(settings)` before constructing `_write_service_for(book)`.
- Frontend write entry points remain gated by `env.GNUCASH_WRITES_ENABLED === 'true'` and retain experimental post-MVP warnings/acknowledgement.
- README and release docs keep controlled writes experimental/post-MVP and disabled by default.

## Product consistency
The repository consistently says the project is pre-alpha / MVP in progress, read-only by default, self-hosted, not SaaS, not a GnuCash replacement, not collaborative accounting, and not production-ready/security-audited.

The README currently points to `v0.0.2-prealpha` as the current public pre-alpha release and says `v0.1.0-readonly` planning/checklist exist but no v0.1 release has been published. That is consistent with git tags and GitHub releases.

## Safety boundary
Pass for this audit phase.

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP only.
- GnuCash Desktop remains the authoritative editor.
- No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, keys, certs, real screenshots, or real exports were required or added by this audit.

## Release/readme/docs consistency
Consistent for Phase 75.

- No `v0.1.0-readonly` tag or GitHub release exists.
- No `v0.1.1-readonly` release should be planned while the base `v0.1.0-readonly` is missing.
- Release blockers #24/#25 remain the next meaningful release-gate work.
- `docs/release/v0.1.0-readonly-notes.md` still does not exist, matching the open #24 blocker.

## GitHub project hygiene
No new GitHub issue was created.

Reason: the meaningful Phase 75 findings are already covered by existing issues:

- #24 — Prepare conservative v0.1.0-readonly release notes before publication.
- #25 — Complete v0.1 read-only runtime smoke/dogfood gate on copied or disposable data.

Creating a new “v0.1.1 not applicable” issue would be backlog noise.

## Security notes
This audit did not perform a professional security audit. It did not change auth, secrets, write behavior, deployment exposure, or data handling. Existing safety boundaries and warnings remain in place.

## Test/CI notes
Checks run for Phase 75 are recorded in `docs/handoff/phase-75.md`.

Because this phase makes a release/readiness decision, the full backend/frontend/Docker verification suite was run in addition to git/GitHub release checks.

## Recommended next actions
1. Do not prepare or publish `v0.1.1-readonly` now.
2. Do not publish `v0.1.0-readonly` until #24 and #25 are resolved and a later explicit release gate approves publication.
3. Keep `v0.1.1-readonly` maintenance-release decisions postponed until after a real `v0.1.0-readonly` tag/release exists and there is an actual post-release bugfix/docs/UX change set.
4. Keep controlled writes disabled by default and experimental/post-MVP only.
5. Do not start Phase 76 unless explicitly requested.

## Suggested / created GitHub issues
Created: none.

Suggested: none new. Existing #24 and #25 are the correct release blockers; a separate v0.1.1 placeholder issue would be noisy before v0.1.0 exists.

## What not to do next
- Do not prepare `v0.1.1-readonly` before `v0.1.0-readonly` exists.
- Do not publish `v0.1.0-readonly` while #24/#25 remain open.
- Do not reframe unresolved initial-release work as maintenance-release work.
- Do not enable `GNUCASH_WRITES_ENABLED` by default.
- Do not expand controlled-write scope or market write mode as safe.
- Do not claim production readiness, security audit, broad compatibility, SaaS readiness, GnuCash replacement status, collaborative accounting, or family-wallet positioning.
- Do not commit real financial/secrets/runtime artifacts.
- Do not start Phase 76 from Phase 75.
