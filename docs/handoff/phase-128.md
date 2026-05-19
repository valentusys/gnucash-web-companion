# Phase 128 — Write-alpha concurrency and error-path expansion

Date: 2026-05-19
Status: DONE

## Goal

Close narrow write-alpha readiness gaps for create-route concurrency, post-backup error handling, lock release, failed audit evidence, and read-only book access rejection while keeping write mode disabled by default and limited to copied/disposable fixtures.

## Scope completed

- Added copied/disposable fixture route coverage for two parallel `POST /books/{book_id}/transactions` requests:
  - one request succeeds;
  - the contending request returns lock contention (`409`);
  - the disposable book gains exactly one balanced transaction;
  - success and lock-failure attempts are both audited;
  - the per-book write lock is released after the attempt.
- Added synthetic post-backup write-failure coverage:
  - forces a write failure after backup creation;
  - verifies the disposable book is not mutated;
  - verifies the write lock is released;
  - verifies a failed audit row is written with the backup path;
  - verifies the backup file remains readable and matches the pre-write book state.
- Added route-level read-only/viewer access regression:
  - create write against a viewer/read-only book grant returns `403` before constructing the write service.
- Hardened `WriteLockService.acquire()` so re-entrant same-process acquisition for the same book key returns `False` instead of replacing the active lock file descriptor.
- Extended `GnuCashWriteError` with optional `backup_path` and propagated post-backup create failures into failed audit payloads.
- Updated `docs/v0.2-controlled-writes.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md`.

## Non-goals / safety boundaries

- No default write enablement; `GNUCASH_WRITES_ENABLED=false` remains default.
- No weakening of the `APP_ENV=test` write-alpha route gate.
- No real/private GnuCash books used, searched for, opened, copied, generated from, or committed.
- Write tests use only `tmp_path` copied/disposable synthetic fixtures.
- No PATCH/DELETE/import/scheduled/account-write expansion in this phase.
- No frontend write UI changes.
- No tag, GitHub release, package, upload, or Phase 132 publication action.
- No app DB, runtime SQLite DB, backups, `.env`, secrets, tokens, credentials, certs, keys, screenshots, CSV/media/private exports, private paths, or real/private financial data committed.

## Verification

- `cd apps/api && pytest tests/test_transaction_writes.py -q` — passed (`46 passed, 29 warnings`).
- `cd apps/api && pytest -q` — passed (`366 passed, 29 warnings`).
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run build` — passed.
- `cd apps/web && npm run test:auth-routes` — passed (extra safety check).
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed (extra safety check).
- `git diff --check` — passed.
- Sensitive tracked-file scan (`git ls-files | grep -E '(^|/)(\.env$|secrets?$|credentials?$)|data/books/.*\.(sqlite|sqlite3|gnucash|db)$|data/backups/.|.*\.(pem|key|crt|p12)$'`) — passed/no matches.

## Expected artifacts

- `apps/api/app/services/write_lock.py`
- `apps/api/app/services/gnucash_write.py`
- `apps/api/app/routers/transactions.py`
- `apps/api/tests/test_transaction_writes.py`
- `docs/v0.2-controlled-writes.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-128.md`

## GitHub / release state

- No tag or GitHub release was created.
- Phase 132 publication remains pending separate explicit authorization.
