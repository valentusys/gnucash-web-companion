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
