# Phase 352 DELETE-one authorization

Status: AUTHORIZE_ONE_DELETE_CONTINGENT_ON_PREFLIGHT.

## PM decision

PM authorizes exactly one DELETE only if Phase 353 proves a concrete eligible target before mutation.

## Allowed target rule

The only allowed DELETE target is one transaction in the owner-provided copied/restorable book that satisfies all of these conditions in Phase 353:

1. The copied book is outside git and is not the original or an only copy.
2. The transaction exists in the copied book immediately before mutation.
3. The app metadata DB has a matching `write_alpha_transaction_ownership` row for the same app book id and transaction id with `created_by_write_alpha=1`.
4. The transaction is therefore write-alpha-created/test-owned, not historical/manual/imported/user data.
5. Pre-mutation backup location and restore path are ready.
6. Non-mutating preflight proves checksums/audit rows are stable.

If any condition is missing or ambiguous, authorization is not executable and Phase 353 must stop before mutation.

## Required mutation evidence if Phase 353 passes

- Pre-mutation backup before DELETE.
- Exactly one DELETE attempt.
- Audit row for the DELETE attempt/result.
- Lock lifecycle evidence.
- Read-back proving the target transaction is absent after DELETE.
- Restore proof from the pre-DELETE backup to an outside-git target.
- Compatibility attempt through piecash and `gnucash-cli` when available.
- Runtime reset to `GNUCASH_WRITES_ENABLED=false`.
- Disabled write probes return 403 after reset.
- Redacted committed evidence only.

## Safety confirmations

- Copied/restorable book only.
- Original book remains excluded and untouched.
- Exactly one DELETE is authorized; no CREATE/PATCH/batch expansion is authorized by this phase.
- No private paths, account names, descriptions, memos, amounts, raw IDs, app DB, backups, screenshots, CSVs, `.env`, tokens, or keys may be committed.
- `GNUCASH_WRITES_ENABLED=false` and the `APP_ENV=test` gate must not be weakened.

## Abort conditions

Stop before mutation if Phase 353 cannot verify app-metadata write-alpha ownership, cannot read the copied book, cannot verify backup/restore readiness, detects target ambiguity, detects private/original/only-copy risk, or detects default/gate drift.
