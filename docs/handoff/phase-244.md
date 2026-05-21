# Phase 244 — Backend guard: PATCH only write-alpha-owned transactions

Date: 2026-05-21

## Summary

Phase 244 adds the backend ownership guard for write-alpha PATCH mutations. After the existing write-enabled flag, book resolution, edit-access check, and `APP_ENV=test` gate pass, PATCH now requires an app metadata ownership row for the same book and transaction with `created_by_write_alpha=true` before constructing `GnuCashWriteService`.

Non-owned historical/imported/manual fixture transactions are rejected with HTTP 403 before backup creation, lock acquisition, audit-row creation, or GnuCash mutation. Write-alpha-created synthetic transactions still use the existing description/date/split-memo-only PATCH scope, and successful PATCH refreshes the app metadata `last_mutated_at` timestamp.

## Changes

- Added a pre-write-service PATCH ownership check in `apps/api/app/routers/transactions.py`.
- Added `_mark_write_alpha_transaction_mutated` to update `last_mutated_at` after a successful allowed PATCH.
- Kept PATCH limited to existing metadata/memo-only fields; no amount/account mutation support was added.
- Added targeted backend coverage for:
  - non-owned fixture transaction PATCH rejection before write-service construction;
  - write-alpha-owned synthetic transaction PATCH success;
  - `last_mutated_at` refresh after PATCH;
  - viewer/outsider and disabled-write safety behavior staying blocked.
- Updated public/status documentation to record Phase 244 as the latest completed phase.
- Updated the transaction ownership model documentation with the Phase 244 PATCH guard behavior.

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The `APP_ENV=test` write-alpha gate remains intact.
- Backend ownership checks are authoritative; no frontend-only enforcement was introduced.
- No DELETE ownership guard was added in this phase; that remains Phase 245 scope.
- No broad edit support, amount mutation, account mutation, real/private-book write safety claim, release, or tag was added.
- No real/private books, app DBs, backups, CSVs, screenshots, tokens, keys, certs, or private financial data were used or committed.

## Verification

Targeted backend tests:

```bash
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_fast_route_family_writes_have_unique_backups_and_redacted_refs tests/test_transaction_writes.py::TestPatchTransaction tests/test_transaction_writes.py::TestWriteAlphaPatchRouteDisposableFixture -q
# 14 passed
```

Full backend suite:

```bash
cd apps/api && pytest -q
# 555 passed
```

Public status guard:

```bash
python3 scripts/check_public_status.py
# passed
```

Docker config/default write flag:

```bash
JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config --quiet
# passed

JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered GNUCASH_WRITES_ENABLED=false by default
```

Git hygiene:

```bash
git diff --check
# passed
```

## Result

Phase 244 is complete. PATCH can no longer mutate non-owned historical/imported/manual transactions through write-alpha; only app metadata write-alpha-owned transactions can reach the existing PATCH mutation flow.
