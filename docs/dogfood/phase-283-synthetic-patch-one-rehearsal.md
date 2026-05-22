# Phase 283 — Synthetic PATCH-one rehearsal

Date: 2026-05-22
Status: PASS — synthetic/disposable PATCH-one rehearsal completed.

## Scope

This phase rehearsed the Phase 282 PATCH-one plan using only the committed synthetic fixture copied into ignored local runtime storage. No owner/private/original/only-copy book was used.

## Rehearsal summary

1. Started local Docker/Caddy with explicit `APP_ENV=test` and temporary `GNUCASH_WRITES_ENABLED=true` against an ignored synthetic runtime copy.
2. Created exactly one write-alpha-owned synthetic transaction through the API so the PATCH target satisfied the same-book ownership guard.
3. PATCHed exactly that created transaction once, changing only metadata/memo test markers.
4. Confirmed API read-back matched the metadata/memo markers.
5. Confirmed runtime SQLite read-back preserved split count, account IDs, and amount fingerprint.
6. Confirmed one successful create audit row, one successful patch audit row, and backup artifacts existed.
7. Ran the compatibility harness: piecash passed and installed `gnucash-cli`/GnuCash CLI probing passed; `broad_compatibility_claimed=false`.
8. Restored the runtime book from the pre-PATCH backup and verified the PATCH markers were removed while the created transaction remained present.
9. Restarted with `GNUCASH_WRITES_ENABLED=false` and ran read-only API smoke; validate/create/PATCH/DELETE probes returned 403.
10. Ran targeted backend PATCH route tests.

## Redacted evidence

```json
{
  "phase_number": 283,
  "scenario_type": "synthetic-patch-one-rehearsal",
  "classification": "synthetic-disposable",
  "result": "pass",
  "mutation_performed": true,
  "patch_count": 1,
  "patch_scope": "metadata-and-split-memo-only",
  "created_write_alpha_owned_target": true,
  "amount_account_fingerprint_unchanged": true,
  "backup_count_status": "present",
  "audit_status": "one-create-and-one-patch-success",
  "compatibility_status": "pass",
  "broad_compatibility_claimed": false,
  "restore_proof_status": "pre-patch-backup-restored-and-patch-markers-absent",
  "disabled_reset_status": "verified-default-disabled",
  "disabled_probe_status": "validate-create-patch-delete-403",
  "raw_private_data_present": false
}
```

## Verification commands

```bash
# ignored synthetic runtime setup; no committed runtime artifacts
JWT_SECRET=<dummy> APP_ADMIN_PASSWORD=<dummy> APP_ENV=test \
  GNUCASH_WRITES_ENABLED=true GNUCASH_DEFAULT_BOOK_PATH=/data/books/<synthetic-copy> \
  ORIGIN=http://localhost:8080 docker compose up -d --build

# custom redacted API harness: create one write-alpha-owned transaction, then PATCH it once
python3 <redacted-inline-phase-283-api-harness>

python3 scripts/write_alpha_compatibility_check.py <synthetic-copy> --output <outside-git-redacted-json>

# restore pre-PATCH backup over ignored runtime copy, then reset to default-disabled
JWT_SECRET=<dummy> APP_ADMIN_PASSWORD=<dummy> APP_ENV=test \
  GNUCASH_WRITES_ENABLED=false GNUCASH_DEFAULT_BOOK_PATH=/data/books/<synthetic-copy> \
  ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy> python3 scripts/smoke/read-only-api-smoke.py --api-base-url http://localhost:8080/api

cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaPatchRouteDisposableFixture -q
```

## Safety boundaries

- No owner/private/original/only-copy book was used.
- No raw paths, account names, memos, amounts, payloads, screenshots, CSV exports, app DBs, books, backups, tokens, keys, certs, or raw tool output are committed.
- Runtime data stayed under ignored local `data/` paths.
- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- Enabled write-alpha remains `APP_ENV=test` gated.
- Owner PATCH remains not run and not authorized.
- DELETE remains blocked.
- No release/tag/package/image was published.
- No production/security/public-internet/broad-compatibility or real/private/original/only-copy write-safety claim is made.

## Verdict

Phase 283 acceptance criteria are satisfied for synthetic/disposable rehearsal only. The rehearsal supports a later PM/Analyst decision on whether to ask the owner for one copied-book PATCH, but it does not authorize owner PATCH execution.
