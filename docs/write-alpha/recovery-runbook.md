# Copied-book write-alpha recovery runbook

- goal: give conservative recovery steps for copied-book write-alpha only.
- scope: backups, restore, locks, failed mutation, default reset, stop conditions.
- non-goals: no original-book instructions, no production disaster-recovery claim.
- acceptance criteria: operator can identify when to stop and restore a copied working book.
- safety checks: use only copied/restorable books outside git; never mutate original/private/only-copy books.
- verification: docs-only Phase 408 update; final public-status and hygiene checks run later.
- expected artifacts: this runbook and `docs/handoff/phase-408.md`.
- final verdict: CONTINUE.

Steps:
1. Before any write-alpha mutation, make an independent outside-git backup of the copied working book.
2. Confirm `GNUCASH_WRITES_ENABLED=false` is the default before and after the session.
3. Enable writes only under `APP_ENV=test` and only for the authorized copied/restorable working copy.
4. Stop immediately if backup creation, audit row creation, ownership marker, read-back, restore, compatibility, lock cleanup, or default reset fails.
5. Restore by copying the pre-mutation backup to a new outside-git target, then verify read-only open before any further mutation.
6. Commit only redacted counts/statuses/opaque refs; never commit books, app DBs, backups, paths, account names, memos, descriptions, amounts, screenshots, CSV exports, `.env`, tokens, keys, or certs.
