# Phase 21 — File-Based Write Lock Replacement

## Status
Complete — 2026-05-17. All acceptance criteria met.

## Goal
Replace the current in-process `threading.Lock`-based write lock (`WriteLockService`) with a file-based lock so that concurrent writes are serialized across multiple workers/processes, not just within a single process.

## Context

The existing `apps/api/app/services/write_lock.py` uses `threading.Lock` — safe for single-process deployments (e.g. one gunicorn worker) but **not safe** for multi-worker or multi-host setups. This is tracked as GitHub issue #7.

The write lock is used exclusively by `GnuCashWriteService` in `gnucash_write.py` for:
- `create_transaction()` — acquires lock before backup + write, releases in `finally` block
- `patch_transaction_metadata()` — same pattern

Write endpoints are gated by `gnucash_writes_enabled` (default `False`). This phase does **not** change that default.

## What to do

### 1. Replace `apps/api/app/services/write_lock.py`

Replace the `WriteLockService` class with a file-based implementation:

- Use `fcntl.flock()` (Unix) on a lock file per book.
- Lock file path: `/data/locks/{book_id}.lock` (create directory if needed).
- `acquire(book_id, blocking=False)` → open lock file, call `fcntl.LOCK_EX | fcntl.LOCK_NB` (non-blocking) or `fcntl.LOCK_EX` (blocking). Return `True` on success, `False` on `BlockingIOError`.
- `release(book_id)` → call `fcntl.LOCK_UN` and close the fd. Safe to call if not held.
- `lock(book_id)` context manager → acquire on enter, release on exit (even on exception).
- Keep the same public API: `WriteLockService` class with `acquire`, `release`, `lock`, and the module-level `write_lock_service` singleton.
- Keep `WriteLockError` exception class (same signature).
- Handle edge cases: lock file parent directory missing, fd cleanup on release.

### 2. Add tests in a new file `apps/api/tests/test_write_lock.py`

Write tests that validate the file lock behavior **without** needing real multi-process scenarios:

- `test_acquire_returns_true_when_lock_is_free` — acquire succeeds.
- `test_acquire_returns_false_when_lock_is_held_non_blocking` — second acquire with `blocking=False` returns `False`.
- `test_release_allows_reacquire` — release then re-acquire succeeds.
- `test_context_manager_acquires_and_releases` — `with service.lock(book_id):` works.
- `test_context_manager_releases_on_exception` — lock is released even if the block raises.
- `test_different_books_independent` — acquiring lock for book A does not block book B.
- `test_lock_uses_expected_lock_file` — verify the lock file is created at the expected path.
- Use `tmp_path` fixture for lock file directory to avoid polluting `/data/locks`.
- Override the lock directory via a constructor parameter or a module-level constant that tests can patch.

### 3. No changes to

- `gnucash_write.py` — the write service already calls `write_lock_service.acquire/release/lock` through the same API. No changes needed.
- `transactions.py` router — no changes.
- `config.py` — `gnucash_writes_enabled` stays `False` by default.
- Frontend — no changes.
- `.gitignore` — no changes needed (lock files in `/data/locks/` are runtime artifacts, not committed).

## Non-goals

- Do NOT implement distributed (network) locks.
- Do NOT change the write flow (validate → lock → backup → write → audit → release).
- Do NOT enable writes by default.
- Do NOT add new write endpoints.
- Do NOT change the backup service.
- Do NOT add integration tests that actually write to a GnuCash book (that's issue #8).

## Acceptance criteria

1. `WriteLockService` uses file-based locking (`fcntl.flock`) instead of `threading.Lock`.
2. Same public API: `acquire(book_id, blocking)`, `release(book_id)`, `lock(book_id)` context manager, `WriteLockError`.
3. Module-level `write_lock_service` singleton still works as a drop-in replacement.
4. Non-blocking acquire returns `False` (not exception) when lock is held.
5. Lock is released on context manager exit, including on exception.
6. Different book IDs use independent lock files.
7. At least 7 new tests in `test_write_lock.py`, all passing.
8. All existing tests still pass (207 backend, frontend check/build/auth-routes).
9. `GNUCASH_WRITES_ENABLED` remains `False` by default.
10. No new production code paths are enabled.

## Safety checks

- `gnucash_writes_enabled` default is untouched (`False`).
- No new write endpoints or write logic.
- Lock files are runtime artifacts in `/data/locks/` — never committed.
- No real GnuCash books or financial data in tests.
- `.gitignore` protections remain intact.
- File lock is released in `finally` blocks (no deadlock on exception).

## Verification

```bash
# Backend tests
cd apps/api && pytest -q

# Frontend checks
cd apps/web && npm run check && npm run test:auth-routes && npm run build

# Docker config
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

Expected: 214+ passed (207 existing + 7+ new write_lock tests), 0 new failures.

## Related issues

- GitHub issue #7 — "Replace in-process write lock before production write mode" (milestone: v0.2 controlled writes).

## Handoff requirements

After implementation:
- Update `PROJECT_STATUS.md` with Phase 21 summary.
- Update this file with actual results, deviations, and test counts.
- Commit changes.
- Push to GitHub if auth is available.
- Close/update GitHub issue #7 if `gh` is available.
