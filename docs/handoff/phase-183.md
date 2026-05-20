# Phase 183 — write-alpha restore UX/API evidence tightening

Date: 2026-05-20
Status: COMPLETE — lock evidence and recovery guidance tightened without write-scope expansion
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 2 only)

## Goal

Close the Phase 177/180 practical recovery risk: stale lock files after released `flock` and root-owned lock readability need a safe operator workflow and tests without expanding write-alpha create/PATCH/DELETE scope.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-182.md`;
  - Phase 177 and Phase 180 handoffs;
  - roadmap file named by the phase contract;
  - relevant write-lock service, transaction write tests, write-alpha smoke helper, write-mode warning UI, auth-route static checks, and recovery docs.
- Added a path-safe backend `WriteLockService.inspect()` helper that classifies lock state as `active`, `stale_released`, `unreadable`, or `not_present` without deleting files or returning filesystem paths.
- Updated the write-alpha create smoke helper to report redacted lock evidence states instead of treating every remaining lock file as active contention.
- Added backend and smoke-helper tests proving active lock vs stale released file vs unreadable lock guidance behavior.
- Updated write-mode UI copy and static checks to point operators to recovery guidance for stale locks and host permission errors.
- Updated the write-alpha recovery procedure to explain active-vs-stale inspection, root-owned/unreadable lock handling, and stopped-runtime cleanup boundaries.
- Added redacted evidence artifact `docs/dogfood/phase-183-write-alpha-lock-recovery-evidence.md`.

## Files changed

- `apps/api/app/services/write_lock.py`
- `apps/api/tests/test_write_lock.py`
- `apps/api/tests/test_write_alpha_smoke_lock_evidence.py`
- `scripts/smoke/write-alpha-create-smoke.py`
- `apps/web/src/lib/components/WriteModeWarning.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/write-alpha-recovery-procedure.md`
- `docs/dogfood/phase-183-write-alpha-lock-recovery-evidence.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-183.md`

## Verification summary

Commands/results recorded for this phase:

```bash
cd apps/api && pytest tests/test_write_lock.py tests/test_write_alpha_smoke_lock_evidence.py -q
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_lock_contention_error_does_not_leak_lock_file_or_book_path -q
python3 -m py_compile scripts/smoke/write-alpha-create-smoke.py
cd apps/web && npm run test:auth-routes
python3 <redacted temporary lock evidence probe>
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan over git ls-files
```

Results:

- Targeted write-lock tests passed: `18 passed`.
- Existing active-lock route regression passed: `1 passed` with existing piecash warnings.
- Smoke helper compiles.
- Frontend auth-route/static checks passed.
- Redacted temporary lock evidence probe showed `not_present`, `stale_released`, and `active` classifications with no raw paths.
- Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No new write endpoint, write feature, direct SQL mutation, automatic lock deletion, production lock-management UI, release, tag, or package was added.
- Active lock contention still blocks writes with HTTP 409 through existing route behavior.
- Stale released lock evidence no longer masks as active hold in the smoke-helper evidence path.
- Recovery guidance remains synthetic/disposable-only and does not recommend real/private or only-copy books.
- No real/private book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, private path, account name, description, memo, amount, or private financial data was committed.

## Next

Proceed only to the next roadmap phase when explicitly requested. Do not start PATCH/DELETE dogfood or release-readiness work from this phase.
