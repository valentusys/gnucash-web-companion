# Phase 247 — Synthetic ownership route-family dogfood

Date: 2026-05-21
Status: PASS — synthetic/disposable ownership route-family dogfood completed through Docker/Caddy.

## Scope

This run exercised the write-alpha ownership route family with synthetic/disposable data only:

- created one write-alpha-owned synthetic transaction;
- PATCHed the same created transaction;
- DELETEd the same created transaction;
- attempted PATCH and DELETE against one non-owned fixture transaction and verified rejection;
- verified backup/audit/lock/restore evidence;
- reset the runtime to default-disabled writes and verified disabled probes.

No real/private/only-copy book was used. No release was published.

## Phase 236 schema evidence

```json
{
  "phase_number": 247,
  "scenario_type": "ownership-route-family",
  "classification": "synthetic-disposable",
  "commands_run": [
    "docker-caddy-write-alpha-enabled-route-family-redacted",
    "non-owned-patch-delete-403-probes",
    "owned-create-patch-delete-route-family",
    "backup-audit-lock-restore-evidence-redacted",
    "docker-caddy-default-disabled-api-smoke",
    "backend-route-tests",
    "docker-compose-default-config"
  ],
  "result": "pass",
  "redacted_artifact_refs": [
    "<redacted-artifact-ref:phase-247-dogfood-report>",
    "<redacted-artifact-ref:phase-247-handoff>"
  ],
  "backup_count": 3,
  "audit_row_count": 3,
  "lock_status": "stale-released-not-active",
  "restore_proof_status": "performed-redacted",
  "disabled_reset_status": "verified-default-false",
  "mutation_performed": true,
  "raw_private_data_present": false
}
```

## Evidence summary

- Docker/Caddy was started locally with explicit `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true` against an ignored synthetic/disposable fixture copy.
- Non-owned fixture PATCH returned 403 before backup growth.
- Non-owned fixture DELETE returned 403 before backup growth.
- One write-alpha-owned synthetic transaction was created through the API and returned an app-metadata ownership hint on read-back.
- The same owned transaction was PATCHed successfully through the metadata-only PATCH route.
- The same owned transaction was DELETEd successfully through the DELETE route.
- Backup evidence: three backup artifacts total for the allowed create/PATCH/DELETE route family.
- Audit evidence: one successful audit row for each allowed route action: create, PATCH, DELETE.
- Lock evidence: a lock file was stale-released/not actively held when inspected from the API container; no active write lock remained.
- Restore evidence: the DELETE backup was restored into the disposable runtime copy and the deleted synthetic transaction read-back passed after restore.
- Runtime was restarted with `GNUCASH_WRITES_ENABLED=false`; read-only API smoke passed through Caddy, including disabled validate/create/PATCH/DELETE probes returning 403.
- Cleanup removed ignored runtime books, app DB, backups, and locks after the smoke.

## Verification commands

```bash
APP_ENV=test JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> \
  GNUCASH_WRITES_ENABLED=true GNUCASH_DEFAULT_BOOK_PATH=/data/books/<synthetic-disposable-copy> \
  ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 <redacted-smoke-helper>
PYTHONPATH=scripts/smoke python3 <redacted-container-evidence-probe>
APP_ENV=test JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> \
  GNUCASH_WRITES_ENABLED=false GNUCASH_DEFAULT_BOOK_PATH=/data/books/<synthetic-disposable-copy> \
  ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py --api-base-url http://localhost:8080/api
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture \
  tests/test_transaction_writes.py::TestWriteAlphaPatchRouteDisposableFixture \
  tests/test_transaction_writes.py::TestWriteAlphaDeleteRouteDisposableFixture -q
```

## Safety boundaries

- No real/private/only-copy GnuCash book was used.
- No raw filesystem paths, account names, memos, amounts, request payloads, cookies, screenshots, CSV exports, app DBs, runtime books, backups, tokens, keys, or certs are committed in this evidence.
- The committed evidence records only bounded counts/statuses and redacted artifact refs.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The `APP_ENV=test` write-alpha gate was not changed or weakened.
- No production, security-audited, public-internet, broad compatibility, or real/private-book write-safety claim was added.
- No release/tag/package was published.

## Verdict

Phase 247 acceptance criteria are satisfied: the owned create/PATCH/DELETE route family works on a synthetic/disposable copy, non-owned PATCH/DELETE are rejected, backup/audit/lock/restore/default reset evidence is recorded with redaction, and disabled probes return 403 after reset.
