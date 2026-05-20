# Phase 222 handoff — DELETE backup artifact/accounting reconciliation

Date: 2026-05-21
Status: COMPLETE — backup artifact collision/overwrite cause fixed with targeted regression coverage.

## Summary

Phase 222 investigated the Phase 220 DELETE backup-count anomaly where redacted evidence showed three successful backup-bearing create/PATCH/DELETE audit rows but only two readable backup files.

The fresh regression/code inspection found a product backup-evidence integrity bug: backup filenames used only second-precision timestamps, and `shutil.copy2` could silently replace an existing artifact when rapid route-family smokes created backups for same-named disposable runtime copies inside the same second.

The backup service now uses microsecond timestamps, deterministic suffix fallback for existing candidates, and exclusive create mode for the destination file. Successful backup-bearing route-family audits can no longer silently collapse multiple artifacts into one filename.

## Files changed

- `apps/api/app/services/backup.py` — unique backup path selection and no-overwrite copy.
- `apps/api/tests/test_backup_restore.py` — regression for rapid same-timestamp backups producing three distinct artifacts without overwrite.
- `docs/dogfood/phase-222-delete-backup-reconciliation.md` — redacted investigation/fix evidence.
- `docs/handoff/phase-222.md` — this handoff.
- `PROJECT_STATUS.md` and `CHANGELOG.md` — phase status synchronized.

## Verification performed

Targeted checks:

- `cd apps/api && pytest tests/test_backup_restore.py tests/test_transaction_writes.py tests/test_write_integration.py::TestBackupCreation tests/test_write_integration.py::TestAuditBehavior -q` — passed (`74 passed`, existing warnings only).
- `python3 -m py_compile scripts/smoke/write_alpha_smoke_evidence.py scripts/smoke/write-alpha-create-smoke.py scripts/smoke/write-alpha-patch-smoke.py scripts/smoke/write-alpha-delete-restore-smoke.py` — passed.

Standard checks were run after docs/status updates before commit:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet`
- `git diff --check`
- sensitive tracked-file hygiene scan

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` gate was not weakened.
- No new write endpoint, write route family, create/PATCH/DELETE mutation semantics, release/tag/package/image, or deployment was added.
- No real/private/only-copy book was used.
- No runtime book, app DB, backup artifact, `.env`, screenshot, export, token, cookie, cert, key, raw private path, account name, memo, amount, or private financial data was staged or committed.

## Risks / blockers

The Phase 220 no-release blocker is explained and fixed at backup artifact identity level, but this phase did not run the later roadmap's write-alpha DELETE restore proof or full create/PATCH/DELETE matrix. A release remains blocked until later phases rerun bounded synthetic/disposable route-family dogfood and default-disabled reset evidence.

## Next

Do not start the next roadmap phase from this session. The next safe phase is Cycle 3 Phase 2/223 only if explicitly launched in a fresh Hermes session.
