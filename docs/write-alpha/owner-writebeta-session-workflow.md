# Owner-writebeta session workflow posture

This document describes the safe target workflow for owner-only writebeta work. It is not a public write beta and does not authorize real working-book writes.

## Default posture

- Public beta remains public read-only beta.
- `GNUCASH_WRITES_ENABLED=false` remains the default in committed examples and rendered Compose config.
- Enabled write-alpha/writebeta work remains `APP_ENV=test` gated unless a stronger PM-approved gate is implemented, tested, and documented.
- GnuCash Desktop remains the authoritative editor.

## Required session states

1. `disabled`: writes are unavailable; API/UI must not silently arm writes.
2. `preflight_required`: operator has requested a writebeta flow, but no mutation may occur.
3. `preflight_passed`: non-mutating checks passed against an allowed target.
4. `armed_for_preview`: exact operation preview can be generated.
5. `awaiting_confirmation`: operator must confirm the exact target/scope/operation.
6. `mutating`: one authorized operation is executing under lock and backup coverage.
7. `verification_required`: read-back, audit, lock, restore-readiness, and compatibility evidence are required.
8. `reset_required`: runtime must return to disabled defaults.
9. `completed`: evidence is accepted and defaults are disabled.
10. `hard_stopped`: no further mutation is allowed until PM/owner review.

## Copied-book mutation gates

Every copied-book mutation requires all of the following:

- PM authorization for exact operation counts and abort conditions.
- Outside-git copied/restorable target; original/only-copy forbidden.
- Pre-mutation backup before every operation.
- Read-back proof after mutation.
- Safe audit row with bounded counters/opaque refs only.
- Lock lifecycle evidence.
- Restore verification from pre-mutation backup.
- Compatibility check where tooling exists.
- Default-disabled reset proof and disabled-probe verification.

## Real working-book hard stop

Real working-book mutation remains blocked unless the owner provides exact same-context confirmation of target book/copy/operation and the PM authorizes the one-operation scope after all preflight/dry-run/backup/restore rehearsal gates. If any post-mutation verification fails, stop immediately.
