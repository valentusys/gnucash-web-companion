# Phase 74 Audit — Controlled Writes Boundary

## Executive summary
Phase 74 re-audited the experimental controlled-write boundary after read-only stabilization.

The current repository keeps the safe default intact: `GNUCASH_WRITES_ENABLED=false` remains the backend/default environment setting, write UI entry points are hidden unless the explicit feature flag is enabled, backend validate/create/patch routes call the write feature gate before resolving books or constructing `GnuCashWriteService`, integration tests use disposable synthetic fixture copies, file-based locking is documented, and backup/restore smoke coverage exists.

No blocker was found for the current pre-alpha/read-only posture. Controlled writes must still stay experimental/post-MVP. The project is not ready to promote write mode to a real-user milestone or to claim production-safe writes.

## Verdict
Keep writes experimental.

This is not approval to publish `v0.1.0-readonly`, not approval to plan/ship a write milestone, not a production-readiness claim, and not a professional security audit.

## Blockers
No new Phase 74 blocker was found for the current pre-alpha/read-only posture.

Carried-forward blockers before any `v0.1.0-readonly` publication:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.

Write-mode blockers before any v0.2-alpha/write milestone:

1. #36 — remaining controlled-write readiness gates must be tracked and intentionally handled before write mode is promoted beyond experimental.
2. #22 — real GnuCash version fixture coverage remains incomplete; write compatibility must not be generalized from the current synthetic/disposable fixture evidence.

## Important non-blockers
1. The backend write feature gate is route-level and tested for validate/create/patch with writes disabled. This is appropriate for the current experimental surface.
2. Write integration and backup/restore tests use copied disposable fixture books. They do not prove safety for arbitrary real GnuCash books.
3. File-based `fcntl.flock()` locking is documented and tested, but broader realistic multi-worker/concurrency evidence remains a v0.2-readiness gap.
4. Frontend warning/acknowledgement behavior exists when writes are explicitly enabled, but write UI still must not be marketed as safe for real books.

## Audit scope and evidence
Inspected:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `.env.example`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/handoff/phase-73.md`
- `docs/audits/phase-73-audit.md`
- auditor roadmap file: `/home/val/.hermes/cache/documents/doc_524e3283b5e8_auditor-roadmap-56-75.txt`
- `docs/v0.2-controlled-writes.md`
- backend config, transaction write routes, write service, lock service, write tests, backup/restore tests
- frontend transaction list/new-transaction write UI gate, warning component, and auth-route static checks
- open/closed GitHub issues relevant to controlled writes

## Phase 74 audit checks

### Writes disabled by default
Pass.

Evidence:

- `apps/api/app/config.py` sets `gnucash_writes_enabled: bool = False`.
- `.env.example` sets `GNUCASH_WRITES_ENABLED=false` and says MVP v0.1 is read-only.
- README and release docs state controlled writes are experimental/post-MVP and disabled by default.
- `docs/v0.2-controlled-writes.md` says controlled writes are not part of v0.1 and are disabled unless explicitly enabled.

### UI requires explicit warning/confirmation
Pass for the existing experimental create UI.

Evidence:

- `apps/web/src/routes/transactions/+page.server.ts` exposes `writesEnabled` only when `env.GNUCASH_WRITES_ENABLED === 'true'`.
- `apps/web/src/routes/transactions/+page.svelte` renders the “New transaction” write entry point only when `data.writesEnabled` is true and shows experimental post-MVP warning copy near the entry point.
- `apps/web/src/routes/transactions/new/+page.server.ts` redirects away from `/transactions/new` when frontend writes are disabled and requires `write_acknowledgement` before the final create action.
- `apps/web/src/routes/transactions/new/+page.svelte` renders `WriteModeWarning`, requires an acknowledgement checkbox, and shows a browser confirmation before final create.
- `apps/web/scripts/test-auth-routes.mjs` statically checks the write UI gate, warning text, and acknowledgement requirement.

### Backend feature flag cannot be bypassed
Pass for the current validate/create/patch controlled-write routes.

Evidence:

- `apps/api/app/routers/transactions.py` calls `_ensure_writes_enabled(settings)` at the start of `validate_book_transaction`, `create_book_transaction`, and `patch_book_transaction`.
- `_ensure_writes_enabled()` returns HTTP 403 before `_resolve_viewable_book()`, `_require_book_edit_access()`, and `_write_service_for()` are reached.
- `apps/api/tests/test_transaction_writes.py::TestWritesDisabledByDefault` verifies `Settings().gnucash_writes_enabled is False` and that validate/create/patch return 403 without constructing `_write_service_for` while writes are disabled.

### Write docs say experimental
Pass.

Evidence:

- README says controlled-write code is experimental post-MVP work, disabled by default, and not safe for only-copy books.
- `docs/v0.2-controlled-writes.md` repeatedly frames write mode as design/experimental implementation only and not part of v0.1.
- Release plan/checklist exclude default-enabled writes and any safe/production write claim.

### Write integration tests use disposable fixtures
Pass.

Evidence:

- `apps/api/tests/test_write_integration.py` copies `tests/fixtures/test-book.gnucash.sqlite` into `tmp_path` before write tests.
- `apps/api/tests/test_backup_restore.py` also writes only to temporary copied fixture books.
- Tests explicitly verify original fixture immutability.

### Locking is documented
Pass, with future hardening.

Evidence:

- `docs/v0.2-controlled-writes.md` documents file-based per-book write locking with `fcntl.flock()` under `/data/locks/`.
- `apps/api/app/services/write_lock.py` implements per-book lock files and documents the multi-worker intent.
- `apps/api/tests/test_write_lock.py` and write integration tests cover lock behavior, including contention scenarios.

Gap:

- Broader realistic multi-worker/concurrency evidence is still pending before any write milestone should be promoted.

### Backup restore path exists
Pass for smoke-level coverage.

Evidence:

- `docs/v0.2-controlled-writes.md` records Phase 23 backup restore smoke coverage.
- `apps/api/tests/test_backup_restore.py` exercises backup → write → restore → verify against disposable fixture copies.
- Release/deployment docs continue to require copied/disposable data and backups.

Gap:

- This is not a production disaster-recovery guarantee and must not be marketed as one.

### No claim that write mode is production-safe
Pass.

Evidence:

- README says there is no production-readiness/security guarantee and warns against safe write-mode access to only-copy books.
- `docs/v0.2-controlled-writes.md` says no production write-mode guarantee.
- Release docs explicitly block default-enabled writes and any production-safe write claim.

## Safety boundary
Pass.

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP only.
- No Phase 74 work should expand write scope.
- GnuCash Desktop remains the authoritative editor.
- The project remains not SaaS, not a GnuCash replacement, and not collaborative accounting.

## Release/readme/docs consistency
Consistent for Phase 74.

- README current status through Phase 73 was accurate before this phase and did not claim v0.1 publication.
- `v0.1.0-readonly` docs still block publication until release notes and copied/disposable runtime smoke/dogfood evidence are completed.
- `docs/v0.2-controlled-writes.md` accurately lists completed write-boundary safeguards and pending write-readiness gaps.
- CHANGELOG had a release-facing Phase 73 entry and did not claim write readiness.

## GitHub project hygiene
Created one meaningful follow-up issue:

- #36 — Track remaining controlled-write v0.2 readiness gates (`audit`, `safety`, `v0.2-writes`).

No noisy duplicate issue was created for backend feature-gating because #18 was already closed after committed disabled-write bypass regression coverage.

## Security notes
- This audit did not perform a professional security audit.
- No secrets, tokens, app DBs, real GnuCash books, backups, real screenshots, or real exports were intentionally added.
- Auth storage was not changed.
- The current controlled-write routes still expose write capability only behind explicit backend and frontend flags; that is necessary but not sufficient for real-user write safety.

## Test/CI notes
Checks run for Phase 74 are recorded in `docs/handoff/phase-74.md`.

## Recommended next actions
1. Keep `v0.1.0-readonly` publication blocked by #24 and #25 until release notes and copied/disposable runtime evidence are complete.
2. Keep controlled writes disabled by default and experimental/post-MVP only.
3. Use #36 to track remaining v0.2 write-readiness gates before any write milestone planning or promotion.
4. Keep #22 open for real GnuCash version fixture coverage and do not generalize write compatibility beyond existing disposable fixture tests.
5. Do not add write features, enable writes, or market write mode as safe as part of Phase 74.

## Suggested / created GitHub issues
Created:

- #36 — Track remaining controlled-write v0.2 readiness gates (`audit`, `safety`, `v0.2-writes`).

Suggested but not created separately:

- Backend write feature flag bypass hardening — already covered by closed #18 and committed regression tests.
- UI write warning — already covered by closed #21 and committed static/frontend checks.
- Write lock replacement — already covered by closed #7 and current file-lock implementation.
- Backup restore smoke — already covered by closed #9 and current backup/restore tests.

## What not to do next
- Do not publish `v0.1.0-readonly` until #24/#25 are resolved and an explicit release phase approves publication.
- Do not enable `GNUCASH_WRITES_ENABLED` by default.
- Do not expand controlled-write scope beyond the current narrow experimental transaction validate/create/patch surface.
- Do not claim write mode is production-safe, security-audited, broadly GnuCash-compatible, or safe for only-copy books.
- Do not add collaborative editing, family-wallet framing, hosted SaaS positioning, banking integration, import/sync, or direct GnuCash SQL writes.
