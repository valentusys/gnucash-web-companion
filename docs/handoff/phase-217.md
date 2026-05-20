# Phase 217 handoff — write-alpha backup-failure and no-mutation drill

Date: 2026-05-21

## Summary

Phase 217 added backend write-alpha safety regression coverage for backup-failure/no-mutation paths across create, PATCH, and DELETE without adding write scope.

The new tests inject path-like backup creation failures and prove the route fails before opening the book for write, leaves the disposable synthetic fixture unchanged, records a failed audit row with no backup path, returns path-safe API/audit errors, and releases the lock. Existing post-backup injected failure tests continue to prove backup evidence is retained and the fixture remains unchanged after create/PATCH/DELETE post-backup failures.

## Files changed

- `apps/api/tests/test_transaction_writes.py`
  - Imported `BackupError` for explicit backup-failure injection.
  - Added create route backup-failure/no-mutation/audit/lock-release coverage.
  - Added PATCH route backup-failure/no-mutation/audit/lock-release coverage.
  - Added DELETE route backup-failure/no-mutation/audit/lock-release coverage.
- `docs/dogfood/phase-217-write-alpha-backup-failure-drill.md`
  - Recorded redacted synthetic/disposable evidence and safety boundaries.
- `PROJECT_STATUS.md`
  - Updated current baseline through Phase 217 and added the factual Phase 217 status entry.

## Verification performed

- `cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_create_backup_failure_fails_before_mutation_audits_and_releases_lock tests/test_transaction_writes.py::TestWriteAlphaPatchRouteDisposableFixture::test_patch_backup_failure_fails_before_mutation_audits_and_releases_lock tests/test_transaction_writes.py::TestWriteAlphaDeleteRouteDisposableFixture::test_delete_backup_failure_fails_before_mutation_audits_and_releases_lock -q` — passed (`3 passed`).
- `cd apps/api && pytest -q` — passed (`520 passed`).
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — rendered `"false"` for API and web.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test` gate was not weakened.
- Write-enabled test execution is limited to copied/disposable synthetic fixture paths in pytest temp directories.
- No new write endpoints, amount/account PATCH, account/import/scheduled writes, default-write enablement, release/tag publication, or production/private-book write-safety claim was added.
- No real/private books, app DBs, backup artifacts, `.env`, screenshots, exports, tokens, keys, certs, raw paths, account names, memos, or amounts were committed.

## Follow-up risks/blockers

None blocking Phase 217.

This remains experimental write-alpha evidence for synthetic/disposable test fixtures only. It is not production-ready, not security-audited, and not safe for real/private or only-copy books.
