# Phase 130 — Write-alpha PATCH transaction hardening

Date: 2026-05-19
Status: DONE

## Goal

Harden the experimental transaction edit/PATCH write-alpha path with full safety lifecycle evidence while keeping writes disabled by default and executable only in explicit test-environment copied/disposable fixture scope.

## Scope completed

- Hardened `PATCH /books/{book_id}/transactions/{transaction_id}` for write-alpha only:
  - still requires `GNUCASH_WRITES_ENABLED=true`;
  - still requires `APP_ENV=test`;
  - still requires editor/owner book access;
  - remains limited to description, date, and split memo metadata edits.
- Updated backend write service behavior:
  - missing transaction is detected before lock/backup/write and surfaced as 404;
  - PATCH mutation logic is isolated in `_do_patch_transaction` for narrow failure/concurrency testing;
  - post-backup PATCH failures carry the backup path into route-level failed audit payloads.
- Added copied/disposable fixture route tests for:
  - successful PATCH with backup, audit, lock release, and read-only reload verification;
  - missing transaction returns 404 with no mutation, no backup, no lock leak, and failed audit;
  - validation error causes no mutation, no backup, no lock leak, and failed audit;
  - synthetic post-backup PATCH failure releases lock, records failed audit with backup path, keeps backup readable/intact, and leaves book unmutated;
  - concurrent PATCH+CREATE produces one success and one lock-contention failure.
- Updated controlled-write docs/status:
  - `docs/v0.2-controlled-writes.md` Phase 130 readiness snapshot;
  - `CHANGELOG.md`, `PROJECT_STATUS.md`, `README.md` status sync.

## Non-goals / safety boundaries

- No DELETE implementation.
- No import/recurring/account-write implementation.
- No default write enablement; `GNUCASH_WRITES_ENABLED=false` remains the default.
- No weakening of the `APP_ENV=test` write-alpha gate.
- No frontend write UI changes were needed in this phase; existing write UI remains hidden by default behind write-mode behavior.
- No real/private GnuCash books used, searched for, copied, opened, or committed.
- No tag, GitHub release, package, upload, or Phase 132 publication action.
- No production-readiness, audited-security, or real-book write-safety claim.
- No app DB, runtime SQLite DB, backups, `.env`, secrets, tokens, credentials, certs, keys, screenshots, CSV/media/private exports, private paths, or real/private financial data committed.

## Verification

- `cd apps/api && pytest tests/test_transaction_writes.py -q` — passed (`51 passed, 31 warnings`).
- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-compose-config-secret-for-validation-only docker compose config` — passed.
- `git diff --check` — passed.
- Sensitive changed/untracked-file scan excluding `.hermes/` run logs — passed/no private sensitive artifacts found (test/dummy placeholders allowed).

## Expected artifacts

- `apps/api/app/services/gnucash_write.py`
- `apps/api/app/routers/transactions.py`
- `apps/api/tests/test_transaction_writes.py`
- `apps/api/tests/test_write_integration.py`
- `docs/v0.2-controlled-writes.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `README.md`
- `docs/handoff/phase-130.md`

## GitHub / release state

- No tag or GitHub release was created.
- Phase 132 publication remains pending separate explicit authorization.
- Phase 131 DELETE has separate explicit user authorization, but this phase intentionally did not implement DELETE.
