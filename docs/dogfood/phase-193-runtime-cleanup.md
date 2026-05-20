# Phase 193 — root-owned runtime cleanup dogfood note

Date: 2026-05-20
Status: COMPLETE — redacted cleanup helper exercised on synthetic ignored runtime files only

## Scope

This note records a manual dry-run/cleanup check for the Phase 193 helper. It used only synthetic placeholder files under ignored runtime classes:

- `data/books/` synthetic disposable placeholder;
- `data/app/` synthetic disposable placeholder;
- `data/backups/` synthetic disposable placeholder directory;
- `data/locks/` synthetic stale lock file.

No GnuCash book was opened, parsed, copied from a private source, or mutated.

## Redacted command class

```text
# create synthetic placeholders under ignored data runtime classes
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
```

## Redacted output summary

```text
mode=dry_run
path_classes:
  books: count=1
  app: count=1
  backups: count=1
  locks: count=1
statuses:
  cleanup_runtime_artifact: count=3
  cleanup_stale_lock: count=1
  lock_stale_released: count=1
messages:
  - stopped-runtime acknowledgement accepted
  - output is redacted to path classes and counts only

mode=cleanup
path_classes:
  books: count=1
  app: count=1
  backups: count=1
  locks: count=1
statuses:
  cleanup_runtime_artifact: count=3
  cleanup_stale_lock: count=1
  lock_stale_released: count=1
  removed: count=4
messages:
  - stopped-runtime acknowledgement accepted
  - output is redacted to path classes and counts only

mode=dry_run
path_classes:
  books: count=0
  app: count=0
  backups: count=0
  locks: count=0
statuses:
messages:
  - stopped-runtime acknowledgement accepted
  - output is redacted to path classes and counts only
```

## Safety notes

- Helper refused-by-design paths are tested separately: missing stopped-runtime acknowledgement, non-repository data root, unsupported lock children, and active flock-held locks.
- Output contains path classes/counts/statuses only, not raw artifact paths, account names, transaction descriptions, memos, amounts, backup filenames, app DB rows, `.env`, or secrets.
- `GNUCASH_WRITES_ENABLED=false` remains the default; this helper does not enable writes and does not call write routes.
