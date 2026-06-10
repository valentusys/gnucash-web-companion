# Backup and restore UX design

Before any write the operator must see:
- target class: copied/restorable or future PM-authorized working copy;
- backup class: independent/outside app or blocked;
- restore readiness: verified helper plus dry-run/restore-to-copy plan;
- Desktop closed confirmation requirement;
- default posture: `GNUCASH_WRITES_ENABLED=false` until an explicitly authorized, `APP_ENV=test`-gated write session is armed;
- stop condition if restore cannot be proven.

Backups must never be committed. Evidence uses opaque backup refs only. Restore proof for a real working book must restore to a separate temporary copy, never overwrite the working book during validation.

Default-disabled UX requirements:
- The read-only/default screen must not imply that backup readiness enables writes.
- Any disabled-write probe must remain a no-op and must report the default-disabled state, not a recoverable operator warning.
- Failed restore, read-back, or audit evidence is a hard stop: preserve the copied target, preserve the backup outside git, reset `GNUCASH_WRITES_ENABLED=false`, and require owner/maintainer review before another attempt.
- Public/user-facing wording must not claim public write beta readiness, stable release readiness, production safety, security-audited status, broad GnuCash compatibility, or only-copy safety.

Docs/tests-only readiness copy:
- Label non-mutating maintenance as `docs/tests-only restore-readiness wording check`; it is not recovery proof, disaster-recovery validation, or public write beta readiness.
- Wording checks may read tracked docs, pure guard code, and pytest assertions only; they must not create backup artifacts, restore artifacts, app DB records, or filesystem evidence.
- Any disabled-write probe mentioned here is a documented no-op expectation under `GNUCASH_WRITES_ENABLED=false`, not an executed product mutation.
- Restore-to-copy validation remains a future separately authorized copied/restorable or synthetic/disposable fixture drill under `APP_ENV=test`; docs/tests-only checks do not satisfy that drill.
- Backup availability and restore-helper readiness are displayed as prerequisites only; they must not change the default disabled state or invite retrying on the same copy after failed restore/read-back/audit evidence.
- If the operator cannot verify restore wording from tracked docs/tests alone, the UX copy should direct them to checkpoint and escalate instead of creating backup or restore evidence.

Docs/tests-only status labels shown in reviewer-facing UX copy:
- `NOT_RESTORE_DRILL`: no restore command was run and no restored book was opened.
- `NO_BACKUP_ARTIFACT_CREATED`: no backup copy, checksum manifest, app DB row, or filesystem evidence was created.
- `DO_NOT_ENABLE_WRITES`: the wording check does not authorize changing `GNUCASH_WRITES_ENABLED=false` or relaxing the `APP_ENV=test` gate.
- `NO_PRIVATE_DATA_REVIEWED`: the wording check reviewed tracked text/guard assertions only, not private books, paths, accounts, transactions, memos, amounts, screenshots, exports, backups, or logs.

Reviewer-facing docs/tests-only assertion copy must stay negative and non-operational:
- `backup_restore_readiness_scope=docs-tests-only`
- `restore_drill_performed=false`
- `backup_artifact_created=false`
- `private_data_reviewed=false`
- `writes_enabled_or_app_env_gate_relaxed=false`
- `runtime_backup_manifest_reviewed=false`
- `restore_target_opened=false`
- `app_db_opened_or_modified=false`

Do not add restore filenames, checksum lines, backup manifests, app DB rows, runtime logs, private paths, account names, transaction descriptions, memos, amounts, screenshots, exports, books, or backup artifacts to UX copy for a docs/tests-only wording check.
