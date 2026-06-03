# Daytime W3 copied-book dogfood

Status: PASS

Timestamp: 2026-06-03T12:42:41+10:00

## Scope

W3 copied-book dogfood ran only against the staged outside-git copied target for this run. The original/source book remained source-only and was not mutated.

## Authorized counts vs actual counts

| Operation | Authorized | Actual attempts | Actual successes |
| --- | ---: | ---: | ---: |
| CREATE | 2 | 2 | 2 |
| PATCH | 1 | 1 | 1 |
| DELETE | 1 | 1 | 1 |

PATCH was limited to metadata/memo-only on a write-alpha-created transaction. DELETE was limited to a write-alpha-created disposable transaction.

## Redacted evidence summary

- Pre-batch backup: created.
- Routed write backups: 4 route backup files existed after the run.
- Audit summary: 4 successful routed write entries; 0 failed, 0 unknown.
- Audit action counts: 2 transaction.create, 1 transaction.patch, 1 transaction.delete.
- Ownership evidence: 2 write-alpha-created ownership rows for the created transactions.
- Read-back: retained created transaction present; deleted disposable transaction absent.
- Restore: restore from pre-batch backup succeeded and matched the backup digest.
- Compatibility: copied book opened read-only via piecash after mutation.
- Default-disabled reset probes: CREATE 403, PATCH 403, DELETE 403.
- Redaction: committed docs contain only opaque refs and aggregate counts; no raw private paths/account names/descriptions/memos/amounts.

## Safety notes

- No historical/manual transaction was patched or deleted.
- No amount/account/split-shape PATCH was attempted.
- No source/original/private/working/only-copy book was mutated.
- `GNUCASH_WRITES_ENABLED=false` remains the default posture.
- No public write beta or release was published.

## Result

W3 copied-book dogfood passed for the authorized copied target and exact operation counts.
