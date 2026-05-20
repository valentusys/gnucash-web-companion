# Phase 179 — write-alpha API hardening from dogfood findings

Date: 2026-05-20
Status: COMPLETE — backend path-safe error hardening from disposable dogfood findings
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 8 only)

## Goal

Fix only real backend safety/correctness gaps discovered during copied-book write-alpha dogfood.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-178.md`;
  - roadmap file named by the phase contract;
  - Phase 175–178 dogfood/UX evidence and backend write-alpha routes/tests.
- Addressed the concrete dogfood-linked backend gap behind Phase 178's frontend safe-error workaround: write-alpha API/audit error strings could still contain path-like backend internals on lock contention or post-backup failures.
- Kept create/PATCH/DELETE write-alpha scope unchanged.
- Did not add endpoints, direct SQL writes, production/private-write support, release/tag publication, or default write enablement.

## Files changed

- `apps/api/app/routers/transactions.py`
- `apps/api/tests/test_transaction_writes.py`
- `docs/dogfood/phase-179-write-alpha-api-hardening.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-179.md`

## Behavior changed

- Lock-contention responses and audit `error` values now use a generic safe write-lock message without embedding the book/lock path.
- `GnuCashWriteError` handling now preserves non-path validation/business wording but collapses path-like or URI-like internals into a generic safe backend failure detail.
- Backup path recording remains explicit in `backup_path`; it is no longer duplicated through error text.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Write-enabled paths still require `APP_ENV=test` and copied/disposable fixture scope.
- Disabled-write routes still return 403 before book resolution/write-service construction.
- No direct SQL mutation was added; write-alpha still uses the existing piecash service path.
- Backup-before-write and audit-row invariants remain covered by existing route tests.
- No real/private/only-copy book was opened or mutated.
- No release/tag/package was published.
- No raw book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data was committed.

## Verification

Commands run:

```bash
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_path_like_create_failure_uses_safe_api_and_audit_error tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_lock_contention_error_does_not_leak_lock_file_or_book_path tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_concurrent_enabled_create_allows_one_success_and_one_lock_contention tests/test_transaction_writes.py::TestWritesDisabledByDefault::test_disabled_write_routes_short_circuit_before_book_resolution -q
cd apps/api && pytest tests/test_transaction_writes.py -q
cd apps/api && pytest -q
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
python3 - <<'PY'
# sensitive tracked-file hygiene scan from the project phase-execution checklist
PY
```

Results:

- Targeted backend write-alpha/error/gate tests passed: `4 passed`.
- Full write-alpha transaction test file passed: `59 passed`.
- Full backend pytest passed: `404 passed, 33 warnings`.
- Docker Compose config validation passed.
- Docker Compose still renders `GNUCASH_WRITES_ENABLED: "false"` for relevant services.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Next

Continue only with the next explicitly requested phase. Do not run Phase 9 combined regression dogfood, release-readiness gate, release/tag publication, PATCH dogfood, DELETE dogfood, or private-book disaster recovery unless a later phase explicitly requests it.
