# Phase 131 — Write-alpha DELETE transaction and validation hardening

Date: 2026-05-19
Status: DONE

## Goal

Complete the explicitly authorized write-alpha DELETE transaction slice while preserving all write-mode safety boundaries: disabled by default, executable only with `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test`, copied/disposable fixture tests only, pre-write backup, per-book lock, audit logging, and no real/private-book write claims.

## Scope completed

- Added experimental `DELETE /books/{book_id}/transactions/{transaction_id}`:
  - still requires `GNUCASH_WRITES_ENABLED=true`;
  - still requires `APP_ENV=test`;
  - still requires editor/owner book access;
  - uses the same write-alpha safety lifecycle as create/PATCH.
- Added backend service support for deleting a transaction through piecash:
  - missing transaction is checked before lock/backup/mutation and surfaced as 404;
  - successful deletion removes the transaction and its split graph through piecash book deletion;
  - post-backup delete failures keep backup-path evidence in route-level failed audit payloads;
  - locks are released after success and failure.
- Added copied/disposable fixture route tests for:
  - successful DELETE with backup, audit, lock release, read-only reload verification, and backup retaining the original transaction/splits;
  - missing transaction returns 404 with no mutation, no backup, no lock leak, and failed audit;
  - synthetic post-backup DELETE failure releases lock, records failed audit with backup path, keeps backup readable/intact, and leaves book unmutated;
  - read-only/viewer access returns 403 before write-service construction;
  - concurrent DELETE+CREATE produces one success and one lock-contention failure.
- Added hidden-by-default frontend delete form on transaction detail:
  - rendered only when write mode is explicitly enabled;
  - requires acknowledgement checkbox value `experimental-delete-acknowledged`;
  - uses browser confirmation before submit;
  - server action refuses deletion unless write mode is enabled and acknowledgement matches.
- Updated controlled-write docs/status:
  - `docs/v0.2-controlled-writes.md` Phase 131 readiness snapshot;
  - `docs/write-alpha-recovery-procedure.md` delete-route recovery wording;
  - `CHANGELOG.md`, `PROJECT_STATUS.md`, `README.md` status sync.

## Non-goals / safety boundaries

- No default write enablement; `GNUCASH_WRITES_ENABLED=false` remains the default.
- No weakening of the `APP_ENV=test` write-alpha gate.
- No real/private GnuCash books used, searched for, copied, opened, or committed.
- No import/recurring/account-write implementation.
- No soft-delete, undo, or bulk delete.
- No tag, GitHub release, package, upload, or Phase 132 publication action.
- No production-readiness, audited-security, or real-book write-safety claim.
- No app DB, runtime SQLite DB, backups, `.env`, secrets, tokens, credentials, certs, keys, screenshots, CSV/media/private exports, private paths, or real/private financial data committed.

## Verification

- `cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaDeleteRouteDisposableFixture -q` — passed (`5 passed, 22 warnings`).
- `cd apps/api && pytest tests/test_transaction_writes.py -q` — passed (`57 passed, 32 warnings`).
- `cd apps/api && pytest -q` — passed (`377 passed, 32 warnings`).
- `cd apps/web && npm run check` — passed (`0 errors, 0 warnings`).
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-compose-config-secret-for-validation-only docker compose config` — passed.
- `git diff --check` — passed.
- Sensitive changed/untracked-file scan excluding `.hermes/` run logs — passed/no private sensitive artifacts found (test dummy credentials allowed).

## Expected artifacts

- `apps/api/app/services/gnucash_write.py`
- `apps/api/app/routers/transactions.py`
- `apps/api/tests/test_transaction_writes.py`
- `apps/web/src/routes/transactions/[id]/+page.server.ts`
- `apps/web/src/routes/transactions/[id]/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/v0.2-controlled-writes.md`
- `docs/write-alpha-recovery-procedure.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `README.md`
- `docs/handoff/phase-131.md`

## GitHub / release state

- No tag or GitHub release was created.
- Phase 132 publication remains pending separate explicit authorization.
- This phase only implements the authorized write-alpha DELETE transaction slice under the existing test/disposable safety gate.
