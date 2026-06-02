# Copied-book dogfood readiness packet for #36

Status: non-mutating packet. This document defines future authorization and evidence requirements only; it does not authorize or perform copied-book mutation.

## Required authorization

A copied/restorable dogfood operation requires same-context owner + PM authorization before execution. The authorization must include:

1. copied/restorable fixture class and outside-git staging class, without publishing a private path;
2. route family and operation counts;
3. backup/read-back/audit/lock/restore/reset expectations;
4. redacted evidence only publication limits;
5. confirmation of no original/private/real-working/only-copy book target.

## Required preflight shape

- `GNUCASH_WRITES_ENABLED=false` is the committed default before and after the packet.
- Enabled write-alpha/writebeta routes remain `APP_ENV=test` gated.
- Desktop must be closed for the copied target if mutation is later authorized.
- Independent backup and restore-to-copy plan must exist before any route execution.
- Route preflight, preview, confirmation, backup, read-back, audit, lock, restore, reset, and disabled-probe outcomes must be captured without raw financial/private content.

## Current package result

- Mutation counts: CREATE 0 / PATCH 0 / DELETE 0.
- No copied/restorable dogfood mutation was authorized here.
- #36 remains open.
- Default decision remains NO_RELEASE and no public write beta.

## Forbidden evidence

Do not publish or commit GnuCash books, SQLite books, app DBs, backups, CSV exports, screenshots, `.env`, tokens, keys, certs, private paths, account names, transaction descriptions, memos, amounts, or raw private evidence.
