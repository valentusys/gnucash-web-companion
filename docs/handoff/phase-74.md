# Phase 74 — Controlled Writes Boundary Audit

## Status

Complete. Phase 74 performed the auditor-first controlled-writes boundary audit from the auditor roadmap, created the required audit artifact, created one meaningful GitHub follow-up issue, synchronized durable status docs, ran relevant checks, and pushed the phase commit.

This phase did not publish `v0.1.0-readonly`, did not enable writes, did not expand controlled-write scope, did not claim write-mode safety, and did not start Phase 75.

## Auditor report

### Verdict

Keep writes experimental.

The current repository preserves the safe read-only default: `GNUCASH_WRITES_ENABLED=false` remains the backend/default environment setting, backend validate/create/patch write routes are gated before book resolution and write-service construction, frontend write UI is hidden unless explicitly enabled and requires warning/acknowledgement, write integration tests use disposable copied fixtures, file-based locking is documented, and backup/restore smoke coverage exists.

This verdict is limited to the Phase 74 controlled-writes boundary review. It is not `v0.1.0-readonly` release approval, not approval to plan/ship a write milestone, not a production-readiness claim, and not a professional security audit.

### Blockers

No new Phase 74 blocker was found for the current pre-alpha/read-only posture.

Carried-forward blockers before any `v0.1.0-readonly` publication:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.

Write-mode blockers before any v0.2-alpha/write milestone:

1. #36 — remaining controlled-write readiness gates must be tracked and intentionally handled before write mode is promoted beyond experimental.
2. #22 — real GnuCash version fixture coverage remains incomplete; write compatibility must not be generalized from the current synthetic/disposable fixture evidence.

### Audit report

- `docs/audits/phase-74-audit.md`

### Suggested / created GitHub issues

Created:

- #36 — Track remaining controlled-write v0.2 readiness gates.

Not created separately:

- Backend write feature flag bypass hardening — already covered by closed #18 and committed regression tests.
- UI write warning — already covered by closed #21 and committed static/frontend checks.
- Write lock replacement — already covered by closed #7 and current file-lock implementation.
- Backup restore smoke — already covered by closed #9 and current backup/restore tests.

### Auditor evidence summary

- AGENTS.md, PROJECT_STATUS.md, README.md, CHANGELOG.md, release docs, latest handoff, roadmap file, relevant backend/frontend code, tests, docs, and GitHub issues were inspected.
- `Settings.gnucash_writes_enabled` defaults to `False` and `.env.example` sets `GNUCASH_WRITES_ENABLED=false`.
- `_ensure_writes_enabled()` gates validate/create/patch routes before `_write_service_for()` can construct `GnuCashWriteService`.
- Disabled-write tests prove validate/create/patch return 403 and do not construct the write service with writes disabled.
- Frontend `/transactions/new` redirects when writes are disabled; write entry points are hidden unless `GNUCASH_WRITES_ENABLED === 'true'`; final create requires acknowledgement and confirmation.
- Write integration and backup/restore tests copy synthetic fixtures into temp paths before mutation and verify original fixture immutability.
- `docs/v0.2-controlled-writes.md` says write mode is experimental/post-MVP, not v0.1, and not production-safe.

## PM report

### Decision

Accept the auditor verdict. Phase 74 may safely record the controlled-writes boundary audit, create one meaningful GitHub issue for remaining v0.2 write-readiness gates, update README/PROJECT_STATUS/CHANGELOG/handoff, and run verification.

No product feature work, write enablement, write-scope expansion, v0.2 planning milestone, release publication, or Phase 75 work is accepted in this phase.

### Why

The roadmap asks for a controlled-writes boundary audit, not implementation. The existing default-disabled boundary is adequate for the current pre-alpha/read-only posture, but remaining write-readiness gaps must stay explicit so experimental write code is not over-promoted. The safest accepted work is durable audit/status/docs synchronization plus issue hygiene.

### Phase brief

- Goal: complete Phase 74 as a controlled-writes boundary audit; verify disabled-by-default settings, backend gate ordering, frontend warning/confirmation, experimental docs, disposable-fixture tests, locking docs, backup/restore coverage, and absence of production-safe write claims.
- Non-goals: no Phase 75, no product feature work, no write enablement, no write-scope expansion, no v0.2-alpha planning milestone, no release/tag publication, no real financial/secrets artifacts, no production/security-audited/safe-write claims.
- Acceptance criteria:
  - `docs/audits/phase-74-audit.md` exists.
  - `docs/handoff/phase-74.md` exists.
  - `PROJECT_STATUS.md` reflects completion through Phase 74 and next explicit-only Phase 75.
  - README latest-audit/current-status references are synchronized.
  - CHANGELOG records the release-facing Phase 74 audit result.
  - Meaningful GitHub issue hygiene is completed without noisy issues.
  - Relevant checks pass.
  - A separate commit is created and pushed to `origin/main`.
- Safety checks:
  - Keep MVP read-only by default.
  - Keep `GNUCASH_WRITES_ENABLED=false` as the default.
  - Keep controlled writes experimental/post-MVP only.
  - Do not commit `.env`, real books, app DBs, backups, secrets, keys, certs, real screenshots, or real exports.
  - Do not claim production readiness, security audit, broad compatibility, SaaS readiness, GnuCash replacement, collaborative accounting, safe write mode, or family-wallet positioning.
- Verification:
  - Static controlled-writes boundary/code/docs searches.
  - `git diff --check`.
  - `cd apps/api && pytest -q`.
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`.
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`.
  - GitHub issue verification via `gh`.

### Risks

- The presence of experimental write code can be misread as write-mode readiness. Mitigation: audit/handoff/README/PROJECT_STATUS keep controlled writes experimental, disabled by default, and not part of v0.1.
- Existing lock/backup tests could be overread as production safety. Mitigation: #36 tracks remaining v0.2 readiness gates and the audit explicitly rejects production-safe write claims.
- Phase 74 could be mistaken as v0.2 planning approval. Mitigation: PM decision limits work to audit/status/docs/issue hygiene only.

### Files/docs to update

- `docs/audits/phase-74-audit.md`
- `docs/handoff/phase-74.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`

### GitHub/backlog

- Created #36 for remaining controlled-write v0.2 readiness gates.
- #24 and #25 remain v0.1 publication blockers.
- #22 remains relevant before broad write compatibility claims.

## Engineer report

Implemented only PM-accepted Phase 74 docs/status/GitHub hygiene work:

- Created `docs/audits/phase-74-audit.md` with auditor verdict, blockers, non-blockers, controlled-write boundary findings, GitHub issue decisions, safety notes, and next actions.
- Created GitHub issue #36 for remaining controlled-write v0.2 readiness gates.
- Updated `PROJECT_STATUS.md` to mark completion through Phase 74, add Phase 74 to completed phases, set Phase 75 as the next explicit-only roadmap phase, and add a Phase 74 status section.
- Updated `README.md` current status through Phase 74 and latest-audit link.
- Updated `CHANGELOG.md` with the release-facing Phase 74 controlled-writes boundary audit entry.
- Created this handoff document.

No product code changed. No write behavior/default changed. No tag or GitHub release was published. No Phase 75 work was started.

## Checks

Run during Phase 74:

- `git status --short --branch` — clean against `origin/main` before edits.
- `~/.local/bin/gh auth status` — authenticated as `valentusys`.
- `~/.local/bin/gh issue list --state open --limit 100 --json number,title,labels,url` — reviewed open issues and avoided duplicates.
- `~/.local/bin/gh issue list --state all --limit 200 --search "write OR concurrency OR controlled OR v0.2" --json number,title,state,labels,url` — reviewed prior write-boundary issues and avoided duplicates for completed #18/#21/#7/#9 work.
- `~/.local/bin/gh issue create ...` — created #36.
- Static controlled-writes boundary/code/docs searches:
  - backend default settings and `.env.example` keep writes disabled;
  - backend write routes call `_ensure_writes_enabled()` before `_write_service_for()`;
  - disabled-write tests prove validate/create/patch cannot construct the write service while writes are disabled;
  - frontend write UI and `/transactions/new` are hidden/redirected unless writes are explicitly enabled;
  - frontend final create requires acknowledgement and confirmation;
  - write tests use copied disposable fixtures;
  - `docs/v0.2-controlled-writes.md` documents experimental status, locking, backup restore, and remaining gates.
- `git diff --check` — passed.
- `cd apps/api && pytest -q` — passed, 282 passed, 27 warnings.
- `cd apps/web && npm run check` — passed, 0 errors and 0 warnings.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.

Final check results:

- Required audit artifacts: passed.
- GitHub issue hygiene: passed (#36 created; no noisy duplicate issue created).
- Static controlled-writes boundary assertions: passed.
- Backend/frontend/Docker checks: passed.
- Diff whitespace: passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No v0.1 release/tag was published.
- No Phase 74 result was represented as production readiness, release approval, security audit, broad compatibility, safe write-mode support, collaborative accounting, family-wallet support, or SaaS readiness.
- No GnuCash replacement, hosted SaaS, family-wallet baseline, collaborative accounting, banking integration, import/sync, book-management UI, archive UI, or safe write-mode positioning was introduced.
- No real financial data, new GnuCash book, `.env`, app DB, backup, secret, key, token, cert, real screenshot, or real CSV export was added.

## Commit / push

- Phase commit message: `docs: add phase 74 controlled writes audit`.
- Phase commit: final pushed `origin/main` HEAD for Phase 74.
- Pushed to `origin/main`: yes.

## Blockers carried forward

1. Create and review conservative `docs/release/v0.1.0-readonly-notes.md` before any release publication (#24).
2. Complete and record copied/disposable-data Docker/runtime smoke and manual dogfood evidence before any release publication (#25).
3. Keep remaining controlled-write v0.2 readiness gates explicit and unresolved until an explicit write-readiness phase handles them (#36).
4. Continue real GnuCash Desktop version fixture coverage in #22 before broad compatibility/write-compatibility claims.
5. Redact/sanitize full default-book seed log path/URI output and add/adjust tests (#27).
6. Use #26 to make CORS origin narrowing visible in future release/checklist/deployment hardening work.
7. Continue gradual markdown source readability cleanup before broader announcement (#28).
8. Add a localization glossary for accounting/safety terms before the Russian translation surface grows (#29).
9. Implement generated/disposable read-only performance benchmark coverage for #30–#33 before claiming known large-book scalability.
10. Replace frontend display-only `Number()` money decisions with string/sign helpers or a decimal-safe utility in a later hardening phase (#34).
11. Add archived-book and full route-family multi-book access-boundary tests in a later hardening phase (#35).

Do not start Phase 75 until explicitly requested.
