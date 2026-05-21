# Phase 255 — UI warning review and create-only copied-book mode copy

Date: 2026-05-21

Status: COMPLETE — transaction create/write-alpha UI warnings reviewed, strengthened, and verified.

## Summary

Phase 255 reviewed the transaction create page and shared write-alpha warning copy against the maintainer copied-book dogfood packet.

The UI copy was strengthened so future create-only copied-book dogfood warnings now explicitly say:

- use only an outside-git copied/restorable test book;
- keep the original/source book untouched and never use the only existing copy;
- dry-run first unless explicitly continuing;
- create at most one small CREATE test transaction;
- require an independent backup, restore plan, audit row, app backup evidence, and lock-release evidence;
- do not use the form for production entries, PATCH, or DELETE.

English and Russian release-critical warning strings were updated. The transaction create page remains hidden unless the frontend write gate is explicitly enabled, and backend write gates remain authoritative.

## Artifacts

- `apps/web/src/lib/components/WriteModeWarning.svelte`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/lib/i18n/safety-glossary.ts`
- `apps/web/src/routes/transactions/new/+page.server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-255.md`

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- The `APP_ENV=test` backend write-alpha gate was not changed or weakened.
- No new write capability, route, mutation mode, design overhaul, release/tag, or dogfood run was added.
- No real/private/original/only-copy book was used.
- No app DB, book, backup, CSV, screenshot, `.env`, token, key, cert, or private financial data artifact was committed.
- Backend remains authoritative; frontend warnings are operator guidance only.

## Verification performed

```bash
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
cd apps/web && npm run build
cd apps/api && pytest tests/test_health.py tests/test_transaction_writes.py -q
cd apps/api && pytest tests/test_public_status_guard.py -q
python3 scripts/check_public_status.py
JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config --quiet
JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
```

Results:

- Frontend static/auth route checks: PASS.
- Svelte/TypeScript check: PASS (`0 errors`, `0 warnings`).
- Frontend production build: PASS.
- Backend health/write-gate regression subset: PASS (`77 passed`, warnings only from existing FastAPI/piecash/SQLAlchemy deprecations).
- Public status guard unit tests: PASS (`23 passed`).
- Public status guard: PASS.
- Docker Compose config: PASS; rendered `GNUCASH_WRITES_ENABLED: "false"` for app/API services.
- Git whitespace check: PASS.

## GitHub issues

No new GitHub issue was required. Existing strategic write-alpha tracker #36 remains relevant.

## Next phase boundary

Phase 256 may add a best-effort compatibility check harness after copied-book mutation. Phase 255 did not add compatibility checks, restore harnesses, mutation execution, release publication, or any real/private/only-copy write-safety claim.
