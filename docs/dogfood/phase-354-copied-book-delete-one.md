# Phase 354 — Copied-book CREATE-to-DELETE chain executed

Status: PASS.

## Summary

Phase 354 was executed as a safe CREATE-to-DELETE chain on the
owner-provided copied/restorable GnuCash book outside the git working tree.

Phase 353 was previously blocked because no app metadata DB contained a
`write_alpha_transaction_ownership` row for any transaction in the copied book.
Phase 354 resolves this by:

1. Bootstrapping a temporary app metadata DB outside git for this copied-book run.
2. Creating a NEW disposable test transaction through the FastAPI write-alpha
   `POST /books/{book_id}/transactions` route with `APP_ENV=test` and
   `GNUCASH_WRITES_ENABLED=true`.
3. Verifying the matching `write_alpha_transaction_ownership` row in that app DB.
4. Executing exactly one `DELETE /books/{book_id}/transactions/{transaction_id}`
   for that same write-alpha-owned transaction.
5. Proving backup, audit, lock-backed route flow, read-back absence, restore,
   compatibility, and default-disabled reset.

No historical/manual transaction was mutated. No original book was touched.

## Execution evidence (redacted)

- Scenario: copied-book-create-to-delete-chain
- Classification: copied-restorable-disposable-only
- Result: pass
- Create: success via write-alpha route
- Ownership recorded and verified: true (`write_alpha_created_count: 1`)
- Delete preflight eligible: true (same-session ownership metadata)
- Delete: success via write-alpha route
- Read-back transaction absent: true
- Restore from pre-DELETE backup: transaction present
- Compatibility (piecash read-only): pass
  - account_count: 221
  - transaction_count: 2537
  - commodity_count: 5
- Default-disabled verification: disabled DELETE probe returned 403
- Audit rows: 1 create + 1 delete in temporary local app metadata DB
- Backups: create backup and pre-DELETE backup created, checksum prefixes verified
- Lock lifecycle: write-alpha route/service path used per-book write lock acquire/release around CREATE and DELETE

## Script

`scripts/write_alpha_create_delete_chain.py`

The script performs the full chain in one run using the FastAPI write-alpha
routes against a temporary app metadata DB outside git:
preflight → route CREATE → ownership verification → route DELETE → audit/read-back
→ restore → compatibility → default-disabled DELETE probe.

## Safety

- Copied/restorable book only.
- Original book untouched.
- Exactly one CREATE and exactly one DELETE of the same test transaction.
- No private paths, account names, descriptions, memos, or amounts committed.
- `GNUCASH_WRITES_ENABLED=false` remains default in `.env.example` and Compose.
- `APP_ENV=test` gate preserved.
- No copied book, backup, or app DB committed to git.

## Phase 353 adaptation

Phase 353 was previously blocked at preflight because no app metadata DB
existed. Phase 354 adapts the approach: instead of requiring a pre-existing
ownership record, it creates one atomically with the CREATE, then uses it
for DELETE preflight. This is the only safe path when no prior write-alpha
run has left ownership metadata.

## Acceptance criteria

- [x] Exactly one DELETE attempt made.
- [x] DELETE target was write-alpha-created in the same session.
- [x] Backup exists before DELETE.
- [x] Audit row exists for DELETE.
- [x] Deleted transaction is absent on read-back.
- [x] Restored book contains the transaction.
- [x] Compatibility check passes (piecash read-only).
- [x] Default-disabled probe returned 403 after reset.
- [x] Redacted evidence only; no private data committed.
