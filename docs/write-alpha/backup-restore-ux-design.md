# Backup and restore UX design

Before any write the operator must see:
- target class: copied/restorable or future PM-authorized working copy;
- backup class: independent/outside app or blocked;
- restore readiness: verified helper plus dry-run/restore-to-copy plan;
- Desktop closed confirmation requirement;
- stop condition if restore cannot be proven.

Backups must never be committed. Evidence uses opaque backup refs only. Restore proof for a real working book must restore to a separate temporary copy, never overwrite the working book during validation.
