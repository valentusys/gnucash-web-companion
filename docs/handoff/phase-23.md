# Phase 23 — Backup Restore Smoke Test

## Status

Status: complete. Phase commit pushed.

## Goal

Add an automated smoke test that verifies backups created before write operations can actually be restored, confirming the original book state is recoverable.

## Context

Phase 22 validated the full write flow (create, patch, lock, backup, audit) against real piecash books. The backup service (`apps/api/app/services/backup.py`) creates timestamped copies via `shutil.copy2`. However, there is no automated test that exercises the *restore* path — i.e., that a backup can replace the original book and the original state is readable again.

This is the last remaining item from the v0.2 controlled-writes safety checklist (`docs/v0.2-controlled-writes.md`, line 51: "Backup restore behavior needs automated smoke coverage") and corresponds to GitHub issue #9.

## Scope

- Use the existing synthetic fixture (`tests/fixtures/test-book.gnucash.sqlite`) — do NOT create a new fixture.
- Copy the fixture to a temp directory, run `create_book_backup()`, perform a write (create a transaction via `GnuCashWriteService.create_transaction()`), then restore the backup by copying it back over the modified book, and verify the original state (account count, transaction count, specific MD5 or transaction GUIDs) is intact.
- Test that the backup file itself is a valid GnuCash SQLite book (piecash can open it read-only and returns the pre-write state).
- Test that after restore, the write service can read the original accounts and transactions.
- All tests must use `tmp_path` or `tempfile` — never modify the committed fixture.
- No production code changes expected. This is a test-only phase.

## Non-goals

- No restore API endpoint (no `POST /books/{book_id}/restore`).
- No UI for restore.
- No automated cleanup of old backups.
- No testing of incremental/differential backups.
- No testing of concurrent restore + write.
- No testing of backup integrity after power loss or crash.

## Files likely touched

- `apps/api/tests/test_backup_restore.py` — new test file (created).
- No production code files should change.

## Acceptance criteria

1. At least 4 tests covering:
   - Backup creation returns a valid path and the backup file exists.
   - Backup is a valid GnuCash book: piecash can open it and returns the original transaction count.
   - After write + restore, the book has the original transaction count (the write is undone).
   - After restore, the write service can read the original accounts (account count matches pre-write).
2. All tests pass with `pytest -q` (added to the existing suite, no regressions).
3. No production code changes.
4. No real financial data used.
5. Original fixture file is never modified.

## Safety checks

- `GNUCASH_WRITES_ENABLED` is never set to `true` in production by this phase.
- Tests only use disposable copies in `tmp_path`.
- No `.env`, secrets, or credentials are created or modified.
- No real GnuCash books are committed.

## Verification

```bash
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

Expected: backend tests = previous count + new tests, 0 failures. Frontend unchanged. Docker config valid.

## GitHub

- Related issue: #9 (`docs/github/issues/09-backup-restore-smoke-test.md`).
- On completion: close issue #9, update `PROJECT_STATUS.md`, commit, push if auth available.

## Handoff notes for next phase

After Phase 23, the v0.2 controlled-writes safety checklist will be complete:
- ✅ Synthetic fixture (Phase 17)
- ✅ Read-only integration tests (Phase 17)
- ✅ File-based write lock (Phase 21)
- ✅ Real write integration tests (Phase 22)
- ✅ Backup restore smoke test (Phase 23)

The next phase after this could be:
- Frontend write-mode UI warning/confirmation (if pursuing v0.2 writes).
- Or a new MVP feature area (e.g., search, export, filtering).
- Or documentation/release work for v0.1.
