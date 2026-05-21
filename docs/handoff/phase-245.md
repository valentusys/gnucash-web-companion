# Phase 245 — Backend guard: DELETE only write-alpha-owned transactions

Date: 2026-05-21

## Summary

Phase 245 adds the backend ownership guard for destructive write-alpha DELETE mutations. After the existing write-enabled flag, book resolution, edit-access check, and `APP_ENV=test` gate pass, DELETE now requires an app metadata ownership row for the same book and transaction with `created_by_write_alpha=true` before constructing `GnuCashWriteService`.

Non-owned historical/imported/manual fixture transactions are rejected with HTTP 403 before backup creation, lock acquisition, audit-row creation, or GnuCash mutation. Write-alpha-created synthetic transactions still use the existing lock → backup → piecash delete → audit → unlock flow, and successful DELETE refreshes the app metadata `last_mutated_at` timestamp.

## Changes

- Reused the write-alpha transaction ownership helper for DELETE in `apps/api/app/routers/transactions.py`.
- Kept the existing disabled-write, edit-access, and `APP_ENV=test` gates before ownership checks.
- Added DELETE-specific 403 copy for non-owned transactions.
- Updated `last_mutated_at` after successful allowed DELETE.
- Updated targeted backend DELETE tests so:
  - a non-owned historical fixture transaction DELETE is rejected before write-service construction;
  - no backup, lock, audit row, or GnuCash mutation happens for rejected non-owned DELETE;
  - a write-alpha-created synthetic transaction DELETE succeeds with backup/audit/lock evidence;
  - owned missing-transaction, backup-failure, post-backup failure, and concurrency paths still preserve safety behavior.
- Updated public/status documentation to record Phase 245 as the latest completed phase.
- Updated the transaction ownership model documentation with the Phase 245 DELETE guard behavior.

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The `APP_ENV=test` write-alpha gate remains intact.
- Backend ownership checks are authoritative; no frontend-only enforcement was introduced.
- No broad delete support, undo feature, release, or tag was added.
- No real/private books, app DBs, backups, CSVs, screenshots, tokens, keys, certs, or private financial data were used or committed.
- No real/private-book or only-copy write-safety claim was added.

## Verification

Targeted backend tests:

```bash
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaDeleteRouteDisposableFixture tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_fast_route_family_writes_have_unique_backups_and_redacted_refs tests/test_transaction_writes.py::TestWritesDisabledByDefault -q
# 16 passed
```

Full backend suite:

```bash
cd apps/api && pytest -q
# 556 passed, 35 warnings
```

Public status guard:

```bash
python3 scripts/check_public_status.py
# public-status-guard: ok
```

Docker config/default write flag:

```bash
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# GNUCASH_WRITES_ENABLED: "false" for API and worker services
```

Git hygiene:

```bash
git diff --check
# passed
```

## Result

Phase 245 is complete in scope. DELETE can no longer mutate non-owned historical/imported/manual transactions through write-alpha; only app metadata write-alpha-owned transactions can reach the existing DELETE mutation flow.
