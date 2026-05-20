# Phase 223 handoff — Backup naming collision and monotonic evidence hardening

Date: 2026-05-21
Status: COMPLETE — backup identity and redacted operator evidence hardened after the Phase 222 collision fix.

## Summary

Phase 223 stayed within the Cycle 3 Phase 2 contract. It added deterministic route-family coverage proving that rapid synthetic create/PATCH/DELETE write-alpha operations cannot collapse backup artifacts or produce ambiguous operator evidence.

The implementation keeps internal audit rows correlated to exact backup paths for recovery/debug use, while the read-only audit summary exposes only an opaque `backup_artifact_ref` so operators can distinguish backup artifacts without raw paths, filenames, account names, memos, amounts, or private financial data.

## Files changed

- `apps/api/app/routers/transactions.py` — adds bounded opaque backup refs for audit payloads and redacted audit-summary items.
- `apps/api/app/schemas/gnucash_writes.py` — adds `backup_artifact_ref` to audit-summary item DTOs.
- `apps/api/tests/test_transaction_writes.py` — adds fixed-clock create/PATCH/DELETE route-family regression for unique readable backups and matching audit refs.
- `apps/api/tests/test_write_alpha_audit_summary.py` — pins redacted opaque backup refs and no raw paths/filenames.
- `apps/web/src/lib/api/types.ts`, `apps/web/src/lib/i18n/messages.ts`, `apps/web/src/routes/books/write-alpha-audit/+page.svelte` — lets the operator UI render the opaque backup ref only.
- `docs/dogfood/phase-223-backup-identity-evidence.md` — redacted evidence note.
- `docs/handoff/phase-223.md` — this handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — phase status synchronized.

## Verification performed

Targeted checks:

- `cd apps/api && pytest tests/test_backup_restore.py tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_fast_route_family_writes_have_unique_backups_and_redacted_refs tests/test_write_alpha_audit_summary.py -q` — passed (`15 passed`, existing warnings only).

Standard checks:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet`
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'`
- `git diff --check`
- sensitive tracked-file hygiene scan

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` gate was not weakened.
- Write-alpha execution remains limited to explicit local test enablement plus synthetic/disposable fixtures.
- No production backup service, retention policy rewrite, write endpoint, write scope expansion, release/tag/package/image, or deployment was added.
- No real/private/only-copy book was used.
- No runtime book, app DB, backup artifact, `.env`, screenshot, export, token, cookie, cert, key, raw private path, account name, memo, amount, or private financial data was staged or committed.

## Risks / blockers

This phase hardens deterministic backup identity and redacted monotonic evidence, but it does not replace later roadmap dogfood. Release remains blocked until later phases rerun bounded synthetic/disposable DELETE restore proof, combined create/PATCH/DELETE matrix, default read-only regression, and final release gate.

## Next

Do not start the next roadmap phase from this session. The next safe phase is Cycle 3 Phase 3/224 only if explicitly launched in a fresh Hermes session.
