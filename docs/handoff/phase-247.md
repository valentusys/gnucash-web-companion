# Phase 247 — Synthetic ownership route-family dogfood

Date: 2026-05-21

## Summary

Phase 247 ran synthetic/disposable Docker/Caddy dogfood for the write-alpha ownership route family after the Phase 244/245 backend ownership guards and Phase 246 UI alignment.

The smoke created one write-alpha-owned synthetic transaction, PATCHed that same transaction, DELETEd that same transaction, and separately verified that PATCH and DELETE against one non-owned fixture transaction returned 403 without backup growth. Evidence was recorded in `docs/dogfood/phase-247-ownership-route-family.md` with only redacted counts/statuses.

## Changes

- Added `docs/dogfood/phase-247-ownership-route-family.md` with Phase 236-style redacted dogfood evidence.
- Updated `PROJECT_STATUS.md` for completion through Phase 247.
- Updated `CHANGELOG.md` with the new synthetic ownership route-family dogfood evidence.
- No product code, write scope expansion, release, or tag was added.

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The `APP_ENV=test` write-alpha gate remains intact.
- Dogfood used only an ignored synthetic/disposable fixture copy.
- No real/private/only-copy book was used.
- No raw filesystem paths, account names, memos, amounts, request payloads, cookies, screenshots, CSV exports, app DBs, runtime books, backups, tokens, keys, certs, or private financial data are committed.
- No production/security/public-internet/broad-compatibility or real/private-book write-safety claim was added.
- No release/tag/package was published.

## Verification

```bash
# Docker/Caddy synthetic dogfood, explicit local write-alpha test mode:
APP_ENV=test JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> \
  GNUCASH_WRITES_ENABLED=true GNUCASH_DEFAULT_BOOK_PATH=/data/books/<synthetic-disposable-copy> \
  ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 <redacted-smoke-helper>
PYTHONPATH=scripts/smoke python3 <redacted-container-evidence-probe>

# Default-disabled reset through Docker/Caddy:
APP_ENV=test JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> \
  GNUCASH_WRITES_ENABLED=false GNUCASH_DEFAULT_BOOK_PATH=/data/books/<synthetic-disposable-copy> \
  ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py --api-base-url http://localhost:8080/api

# Backend ownership route tests:
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture \
  tests/test_transaction_writes.py::TestWriteAlphaPatchRouteDisposableFixture \
  tests/test_transaction_writes.py::TestWriteAlphaDeleteRouteDisposableFixture -q
```

Results:

- Docker/Caddy write-alpha enabled route-family dogfood: PASS after container-side stale-lock probe confirmed no active lock remained.
- Default-disabled Docker/Caddy API smoke: PASS, including validate/create/PATCH/DELETE disabled probes returning 403.
- Backend route tests: 24 passed.

## Result

Phase 247 is complete. Owned synthetic create/PATCH/DELETE works under explicit local write-alpha test mode, non-owned PATCH/DELETE are rejected, backup/audit/lock/restore/default-reset evidence is redacted, and the default read-only posture remains unchanged.
