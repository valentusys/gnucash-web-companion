# Phase 325 CREATE-one authorization

Status: COMPLETE — PM decision recorded.

## Evidence reviewed

- Phase 321 analyst gate: ready.
- Phase 322 copied-book intake: outside-git working copy, original/read-only evidence copies preserved.
- Phase 323 non-mutating preflight: passed, no checksum change.
- Phase 324 read-only smoke: passed, write probes returned 403.

## PM decision

`AUTHORIZE_ONE_CREATE`.

## Authorized scope

- Exactly one minimal two-split test transaction CREATE.
- Copied/restorable working book only.
- Local/test runtime only: `APP_ENV=test`, `GNUCASH_WRITES_ENABLED=true` only for the mutation window.
- Backup before mutation.
- Read-back, audit row, lock lifecycle evidence, compatibility check, restore/backup verification.
- Reset to `GNUCASH_WRITES_ENABLED=false` after mutation.

## Explicitly not authorized

- PATCH.
- DELETE.
- Any original/private/only-copy mutation.
- Any release or publication.
- Any private data in committed artifacts.
