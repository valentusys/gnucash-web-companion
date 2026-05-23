# Conservative DELETE copied-book plan

Status: PLAN_ONLY. Not executable without fresh explicit owner and PM authorization.

## Allowed future target

Only the write-alpha-created test transaction from the copied/restorable working book may be considered. Historical/manual transactions are forbidden.

## Required future authorization

A future DELETE run requires all of the following in the same context:

1. Owner explicitly authorizes DELETE execution, not just planning.
2. PM explicitly approves the exact target and runbook.
3. The working target is a copied/restorable book, not an original/private/only-copy book.
4. Independent backup and restore proof are available before mutation.

## Required future preflight

- Confirm target transaction is app-metadata write-alpha-owned.
- Confirm transaction exists in the target book immediately before mutation.
- Record redacted split count and structural fingerprint before mutation.
- Confirm no amount/account/currency/split-count changes are planned.
- Confirm `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- Confirm enabled write-alpha remains `APP_ENV=test` gated.
- Confirm original/read-only upload and independent upload backup are not mutation targets.

## Required future mutation controls

- Create a pre-mutation backup outside git.
- Acquire the per-book write lock.
- Use only the routed write-alpha DELETE path after authorization.
- Audit the attempt and result.
- Do not use direct SQL mutation.
- Do not mutate private/original/only-copy data.

## Required future read-back and restore evidence

- Verify deleted test transaction is absent from the copied working target after mutation.
- Verify no unrelated amount/account/currency/split-count change is detected.
- Verify GnuCash/piecash readability.
- Restore from the pre-mutation backup to a separate target and verify the target transaction is present there.
- Reset to default-disabled and prove write routes are blocked.

## Abort criteria

Abort before mutation if any of these is true:

- Owner authorization is ambiguous or only says planning/dry-run.
- PM approval is absent.
- Target ownership is not write-alpha-created.
- Target is historical/manual, original/private, or an only copy.
- Backup or restore proof is missing.
- Any private path/data would need to be committed or exposed.
- `GNUCASH_WRITES_ENABLED` defaults changed from false.
- `APP_ENV=test` gate weakened.
- Static or dry-run evidence suggests the helper or route may mutate unexpectedly.

## Evidence redaction

Committed artifacts must use only redacted summaries. Do not commit raw paths, account names, memos, amounts, descriptions, screenshots, CSVs, databases, backups, app DBs, tokens, keys, certs, or private evidence.
