# Phase 248 — Read-only audit summary ownership view

Date: 2026-05-21

## Summary

Phase 248 made write-alpha ownership evidence visible in the existing read-only audit summary without exposing raw audit payloads or private financial data.

The audit summary API now returns a safe `ownership_summary` with:

- app-metadata `write_alpha_created_count`;
- `non_owned_mutation_rejections_count` from filtered redacted audit rows;
- `last_mutation_type` from the newest successful create/PATCH/DELETE audit action.

The operator UI renders those bounded counters/action labels alongside the existing safe action/result/time-window, transaction ID prefix, backup-present/opaque-backup-ref, and safe-error evidence.

## Changes

- Extended `WriteAlphaAuditSummaryDTO` with `ownership_summary`.
- Added backend summary logic for write-alpha-created ownership marker counts, non-owned rejection counts, and last successful mutation type.
- Updated backend audit summary tests to cover ownership evidence and redaction.
- Updated frontend API types and `/books/write-alpha-audit` to render safe ownership evidence.
- Updated i18n keys and frontend static route checks for the new ownership summary.
- Updated `CHANGELOG.md` and `PROJECT_STATUS.md` for Phase 248.

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The `APP_ENV=test` write-alpha gate remains intact.
- The endpoint remains read-only and app-metadata-only.
- Viewer/outsider access remains blocked as before.
- Raw audit payloads, backup paths, private file paths, account names, memos, amounts, request payloads, screenshots, CSV exports, app DBs, runtime books, backups, tokens, keys, certs, and private financial data are not committed or rendered by the summary UI.
- Transaction IDs remain redacted to the existing safe prefix behavior.
- No app DB management UI, write expansion, release, tag, real/private-book use, or real/private/only-copy write-safety claim was added.

## Verification

```bash
cd apps/api && pytest tests/test_public_status_guard.py tests/test_write_alpha_audit_summary.py -q
cd apps/api && pytest -q
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
python3 scripts/check_public_status.py
git diff --check
git status --short
```

Results:

- Targeted backend audit/public-status tests: PASS (`25 passed`).
- Full backend test suite: PASS (`557 passed`).
- Frontend auth/static route checks: PASS.
- Frontend Svelte/type check: PASS (`0 errors, 0 warnings`).
- Frontend production build: PASS.
- Docker Compose config: PASS.
- Public status guard: PASS.
- Git diff whitespace check: PASS.
- Sensitive tracked-file hygiene scan: PASS.

## Result

Phase 248 is complete. Operators can now confirm write-alpha ownership guard behavior through safe read-only audit summary counters without exposing raw payloads, amounts, memos, account names, or paths.
