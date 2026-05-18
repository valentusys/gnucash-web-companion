# Phase 76 Audit — v0.2 Planning

Date: 2026-05-18

## Executive summary
Phase 76 audited whether the project is ready to create or advance a v0.2 controlled-writes planning milestone.

Verdict: Not ready; keep write mode experimental. The narrow controlled-write boundary is still gated and tested, but v0.2 planning should not be promoted while the initial `v0.1.0-readonly` release remains unpublished and blocked by #24/#25, actual copied/disposable-data dogfood results are still missing, and remaining write-readiness gaps are already tracked in #36.

This audit does not approve enabling writes, does not approve expanding write scope, does not approve a write milestone, does not publish any release, and is not a production-readiness or professional security-audit claim.

## Verdict
Not ready; keep write mode experimental.

Reason: the prerequisites from the auditor roadmap are only partially satisfied. Backup/restore docs, disposable write tests, feature-gated backend write routes, file-based locking, and UI warnings exist. However, `v0.1.0-readonly` is not yet stable/published, dogfood is not completed, maintainer write-risk review is not recorded, and #36 remains open for remaining v0.2 write-readiness gates.

## Blockers
1. `v0.1.0-readonly` has not been published as a git tag or GitHub release, so it cannot be considered stable enough as a release baseline for v0.2 planning.
2. #24 remains open — conservative `v0.1.0-readonly` release notes are still required before initial v0.1 publication.
3. #25 remains open — copied/disposable-data runtime smoke/dogfood evidence is still required before initial v0.1 publication.
4. Dogfood completed: not satisfied. The repo has dogfood readiness/checklist docs, but no completed copied-book dogfood results artifact.
5. #36 remains open — remaining controlled-write v0.2 readiness gates are not complete, including stronger concurrency/lock-contention evidence and maintainer review/recovery procedure.
6. #22 remains open — real GnuCash version fixture coverage remains incomplete, so write compatibility must not be generalized from synthetic/disposable fixture tests.

## Important non-blockers
1. `GNUCASH_WRITES_ENABLED=false` remains the backend/default environment setting.
2. Backend validate/create/patch write routes are still gated by `_ensure_writes_enabled(settings)` before `GnuCashWriteService` construction.
3. Disabled-write regression tests prove validate/create/patch return 403 without constructing the write service when writes are disabled.
4. Write integration tests and backup/restore tests use copied disposable fixture books.
5. File-based `fcntl.flock()` locking exists and is tested at unit/integration level, but broader realistic multi-worker evidence remains a v0.2-readiness gap.
6. Frontend write UI remains hidden unless explicitly enabled and has warning/acknowledgement text when enabled.
7. Backup/recovery docs exist and are honest about manual/operator-run limitations and no production disaster-recovery guarantee.

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
- `docs/handoff/phase-75.md`
- `docs/audits/phase-74-audit.md`
- `docs/audits/phase-75-audit.md`
- `docs/v0.2-controlled-writes.md`
- `docs/dogfood/personal-readonly-dogfood.md`
- `docs/operations/backup-and-recovery.md`
- auditor roadmap file: `/home/val/.hermes/cache/documents/doc_524e3283b5e8_auditor-roadmap-56-75.txt`
- backend config, write routes, write tests, lock tests, backup/restore tests
- frontend write UI gate/warning static checks
- Git tags, GitHub releases, and open GitHub issues

Git/GitHub evidence:

- `git tag -l 'v0.1*'` returned no tags.
- `gh release list --repo valentusys/gnucash-web-companion --limit 20` listed only `v0.0.2-prealpha` and `v0.0.1-prealpha`.
- GitHub issues #24, #25, #36, and #22 are open.

## Phase 76 audit checks

### v0.1 read-only is stable enough
Not satisfied for v0.2 planning.

The code/test baseline supports the current pre-alpha/read-only posture, but the explicit `v0.1.0-readonly` release has not happened. #24 and #25 remain open, and no `v0.1*` tag/GitHub release exists. That is not a stable release baseline for v0.2 controlled-write planning.

### Dogfood completed
Fail / blocker.

`docs/dogfood/personal-readonly-dogfood.md` and the v0.1 release plan/checklist define a safe dogfood process using copied/disposable data. Phase 60 found dogfood can start safely. Phase 61 and later status docs record that actual dogfood/runtime evidence is still missing and tracked in #25.

### Backup/restore docs exist
Pass for planning evidence, with limitations.

`docs/operations/backup-and-recovery.md` documents app metadata backups, copied GnuCash book backups, restore dry-runs, read-only verification, and experimental controlled-write backup expectations. It explicitly says this is not production-grade disaster recovery.

### Write tests use real disposable fixtures
Pass for current experimental surface, not enough for real-user confidence.

Phase 22/23/74 evidence remains valid: write integration and backup/restore tests copy synthetic fixture books into temporary paths before writes and verify original fixture immutability. This supports experiments only; it does not prove broad write compatibility for arbitrary real GnuCash books.

### Locking is cross-process safe enough or limitations accepted
Partially satisfied; not enough for v0.2 milestone promotion.

`apps/api/app/services/write_lock.py` uses `fcntl.flock()`-based file locks, and `apps/api/tests/test_write_lock.py` covers lock behavior. The limitation is accepted/documented for the current experimental posture, but #36 still tracks stronger concurrency/lock-contention evidence before v0.2 write-readiness promotion.

### UI warning exists
Pass.

`apps/web/src/lib/components/WriteModeWarning.svelte` says controlled write mode is experimental, not part of MVP v0.1, `GNUCASH_WRITES_ENABLED=false` is the safe default, GnuCash Desktop remains authoritative, and users must use disposable/test copies and backups. `apps/web/scripts/test-auth-routes.mjs` statically checks the write gate, warning, acknowledgement checkbox, and redirect behavior.

### Maintainer understands risk
Not recorded enough for v0.2 planning.

The docs and issues describe the risks, but this audit did not find a dedicated maintainer write-risk review/recovery sign-off artifact. #36 already tracks maintainer review/recovery procedure as a remaining gate.

### No pressure to enable writes by default
Pass.

No docs/code inspected in this phase pressure maintainers to enable writes by default. README, release docs, `.env.example`, config, and v0.2 docs all retain `GNUCASH_WRITES_ENABLED=false` as the safe/default state and keep writes experimental/post-MVP.

## Product consistency
Consistent for the current pre-alpha/read-only posture.

The repository continues to say the project is a self-hosted read-only-first GnuCash web companion, not SaaS, not a GnuCash replacement, not collaborative accounting, not production-ready, and not security-audited. Controlled writes remain experimental/post-MVP and disabled by default.

## Safety boundary
Pass for the current state.

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP only.
- GnuCash Desktop remains the authoritative editor.
- No Phase 76 work should expand write scope or enable write mode.
- No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, keys, certs, real screenshots, or real exports were required or added by this audit.

## Release/readme/docs consistency
Consistent enough for Phase 76 after status synchronization.

README/PROJECT_STATUS currently state Phase 75 complete and that v0.1 publication remains blocked by #24/#25. This matches Git/GitHub evidence. Phase 76 should update status docs to record that v0.2 planning is not ready and controlled writes remain experimental.

## GitHub project hygiene
No new issue is needed.

Existing #36 is the correct tracker for remaining controlled-write v0.2 readiness gates. Phase 76 should update #36 to record the planning-audit verdict and fix its missing `GNUCASH_WRITES_ENABLED=false` wording rather than creating a duplicate issue.

## Security notes
This audit did not perform a professional security audit. It did not change auth, secrets, write behavior, deployment exposure, or data handling. Existing safety boundaries and warnings remain in place.

## Test/CI notes
Because Phase 76 makes a readiness/planning verdict, full backend/frontend/Docker verification should be run and recorded in `docs/handoff/phase-76.md`.

## Recommended next actions
1. Do not create or promote a v0.2 controlled-writes planning milestone yet.
2. Resolve #24 and #25 first so `v0.1.0-readonly` can be considered through a later explicit release gate.
3. Keep #36 open and use it for v0.2 write-readiness gates: concurrency/lock contention evidence, maintainer review/recovery procedure, conservative write-compatibility docs, and explicit no-default-writes policy.
4. Keep #22 open for real GnuCash version fixture coverage before any broad read/write compatibility claim.
5. Keep controlled writes disabled by default and experimental/post-MVP only.

## Suggested / created GitHub issues
Created: none.

Updated / to update: #36 — record Phase 76 verdict and fix the missing `GNUCASH_WRITES_ENABLED=false` wording in the existing v0.2 write-readiness tracker.

Suggested: none new. Creating a duplicate v0.2 planning-blocked issue would be noisy while #36 already tracks the meaningful gates.

## What not to do next
- Do not enable `GNUCASH_WRITES_ENABLED` by default.
- Do not expand controlled-write scope beyond the current narrow validate/create/patch experimental surface.
- Do not create a v0.2 milestone that implies write-mode readiness before #24/#25/#36 are resolved or explicitly accepted.
- Do not publish `v0.1.0-readonly` while #24/#25 remain open.
- Do not claim write mode is production-safe, security-audited, broadly GnuCash-compatible, or safe for only-copy books.
- Do not add collaborative editing, family-wallet framing, hosted SaaS positioning, banking integration, import/sync, or direct GnuCash SQL writes.
- Do not commit real financial/secrets/runtime artifacts.
- Do not start Phase 77 from Phase 76.
