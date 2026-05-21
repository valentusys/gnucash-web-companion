# Phase 246 — Frontend guard: hide edit/delete unless transaction is write-alpha-owned

Date: 2026-05-21

## Summary

Phase 246 aligns the transaction detail frontend with the Phase 244/245 backend ownership boundary. The transaction detail API now returns a safe app-metadata-only `is_write_alpha_owned` hint, and the Svelte transaction detail page shows experimental delete controls only when all UI preconditions are true: write mode is explicitly enabled, an active book is present, and the transaction is marked write-alpha-owned in app metadata.

Non-owned historical/imported/manual transactions show safe explanatory read-only copy instead of edit/delete controls. This is only a UI guard and operator hint; backend PATCH/DELETE ownership guards remain authoritative before any mutation path.

## Changes

- Added an app-metadata-only ownership hint to transaction detail API responses for both book-aware and default-book detail endpoints.
- Updated frontend transaction detail types with optional `is_write_alpha_owned` metadata.
- Changed the transaction detail Svelte page to:
  - hide experimental delete controls unless `writesEnabled`, `activeBook`, and `transaction.is_write_alpha_owned` are all true;
  - show explanatory non-owned read-only copy when write mode is enabled but the transaction lacks a write-alpha ownership marker;
  - keep existing browser confirmation and explicit delete acknowledgement for owned synthetic/disposable transactions.
- Added English/Russian localized copy warning that backend ownership guards remain authoritative and controls are experimental/disposable-only under `APP_ENV=test`.
- Updated static route checks to pin owned-only controls and non-owned explanatory copy.
- Updated backend tests to pin `is_write_alpha_owned=false` for non-owned transactions and `true` when an app metadata ownership marker exists.
- Updated `PROJECT_STATUS.md` and `CHANGELOG.md` for Phase 246.

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The `APP_ENV=test` write-alpha gate remains intact.
- Backend PATCH/DELETE guards remain authoritative; no frontend-only enforcement claim was added.
- No broad transaction editor, write-mode toggle, release, or tag was added.
- No real/private books, app DBs, backups, CSVs, screenshots, tokens, keys, certs, or private financial data were used or committed.
- No real/private-book or only-copy write-safety claim was added.

## Verification

Pending final verification in this phase:

```bash
cd apps/api && pytest tests/test_transactions.py::TestGetTransactionMVP::test_returns_transaction_detail tests/test_transactions.py::TestGetBookTransaction::test_returns_transaction_detail tests/test_transactions.py::TestGetBookTransaction::test_returns_write_alpha_owned_hint_for_app_metadata_owned_transaction -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
cd apps/api && pytest -q
python3 scripts/check_public_status.py
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
git diff --check
```

## Result

Phase 246 is implemented in scope pending final verification/commit/push. Non-owned transactions no longer expose write-alpha edit/delete controls in the UI; owned synthetic write-alpha transactions can expose controls only under explicit write mode while backend ownership guards remain the real enforcement boundary.
