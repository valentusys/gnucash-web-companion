# Daytime write worker 2 — #36-W1-D Lock lifecycle and stale-lock recovery

## Worker ID

daytime-write-worker-2

## Target issue

#36 — controlled-write v0.2 readiness gates

## Package

#36-W1-D — Lock lifecycle and stale-lock recovery

## Scope completed

- Hardened write operations to use the `WriteLockService.lock()` context manager for CREATE, PATCH, and DELETE flows so lock release is tied to `finally` cleanup.
- Added lock inspection metadata to `WriteLockError` for operator diagnostics when context-manager acquisition fails.
- Added service-level cleanup of open lock file descriptors on object GC to model interruption/crash recovery in tests.
- Added cross-instance lock contention tests proving separate service instances sharing one lock directory serialize writes.
- Added stale lock inspection/reacquire tests proving released/stale lock files do not expose raw paths or book identifiers in operator messages.
- Preserved existing `acquire(..., blocking=False) -> False` behavior for same-instance/non-blocking contention to avoid breaking existing callers.

## Safety notes

- No original/private/working/only-copy GnuCash books were touched.
- Tests used temporary lock directories and existing disposable/synthetic fixtures only.
- No private paths, account names, memos, descriptions, amounts, screenshots, app DBs, backups, `.env`, tokens, or raw evidence were added.
- `GNUCASH_WRITES_ENABLED=false` defaults and APP_ENV/test write gates were not changed.
- No public write beta or release action was performed.

## Verification

From `apps/api`:

```text
pytest -q tests/test_write_lock.py tests/test_transaction_writes.py tests/test_write_integration.py --tb=short
120 passed, 34 warnings in 39.68s
```

From repository root:

```text
git diff --check
git diff --cached --check
# no output
```

## Follow-up

Supervisor should review, run broader gates as practical, commit/push if safe, then continue with the next #36 W1/W2 package.
