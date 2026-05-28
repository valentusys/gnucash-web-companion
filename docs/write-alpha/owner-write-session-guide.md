# Owner write session guide

Phase 480 posture: prototype only.

Available now:
- `scripts/owner_write_session_preflight.py` runs a non-mutating redacted preflight and can write a redacted manifest.
- UI warning banner explains owner-writebeta session gates.

Not available yet:
- integrated arm/backup/preview/mutate/read-back/restore/reset session workflow;
- new copied-book CREATE/PATCH/DELETE evidence under the new session workflow;
- any real working-book mutation.

Example non-mutating preflight shape:
`APP_ENV=test GNUCASH_WRITES_ENABLED=false python3 scripts/owner_write_session_preflight.py --target <outside-git-copy> --backup-dir <outside-git-backup-dir> --manifest <ignored-or-temp-manifest>`

Do not commit manifests containing private values. Do not use original or only-copy books.
