# Phase 326 copied-book CREATE-one dogfood

Status: PASS.

## Mutation count

Exactly one CREATE attempt was made. The attempt succeeded.

## Redacted evidence

- Pre-mutation backup: created before the CREATE.
- CREATE command: passed.
- Mutation requested/performed: `true` / `true`.
- Created transaction shape: one balanced two-split write-alpha smoke transaction using test-only description/memo; committed docs do not contain account names, amounts from the owner book, memos, descriptions, raw payloads, transaction IDs, or paths.
- API read-back: passed inside the create smoke.
- App metadata audit rows: exactly 1 `transaction.create` row.
- Write-alpha ownership markers: exactly 1 marker.
- Lock evidence: no active lock remained after CREATE.
- Working-copy checksum changed after the authorized CREATE.
- Default-disabled reset check: `verified-default-disabled`.
- DELETE: not run.
- PATCH: not run.

## Safety result

The mutation used only the outside-git copied/restorable working book. The read-only upload copy and independent upload backup were not used as mutation targets. Raw private evidence remains outside git.
