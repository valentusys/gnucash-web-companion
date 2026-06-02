# Write evidence matrix

This matrix summarizes current controlled-write readiness evidence without broadening the default
public posture. It is documentation only and does not authorize any mutation. For #36, write
compatibility remains tied to synthetic/disposable or copied/restorable evidence only; supported-version
write compatibility remains pending and must not be converted into broad GnuCash compatibility,
public write beta, production, stable, or security-audited claims.

| Area | Current evidence | Status |
|---|---|---|
| Public read-only beta | `v0.5.0-public-readonly-beta` | Published |
| Missing public read-only beta | `v0.5.1-public-readonly-beta` | Not published; do not claim |
| Owner-writebeta release | `v0.4.0-owner-writebeta` | Deferred/not published |
| Default write-disabled posture | `.env.example`, Compose render, disabled probes | Passed |
| `APP_ENV=test` gate | Guard docs and enabled write-alpha/writebeta paths | Required for explicit writes |
| Issue #43 routed copied-book dogfood | Routed copied/restorable evidence accepted and #43 closed | Accepted narrowly |
| Owner-writebeta state-machine routes | preflight, preview, confirm, verify-reset, reset-disabled | Passed in tests and copied-book dogfood |
| CREATE copied-book dogfood | Routed copied/restorable creates | Passed narrowly |
| PATCH copied-book dogfood | Routed metadata/memo-only patch of owned copied/restorable target | Passed narrowly |
| DELETE copied-book dogfood | Routed delete of owned copied/restorable target in accepted evidence | Passed narrowly; not a real-book claim |
| Final DELETE reset evidence | verify-reset `reset_required`, reset-disabled `disabled` | Passed |
| Backup/restore readiness checklist guard | `validate_backup_restore_readiness_evidence`, checklist docs, synthetic tests | Non-mutating guard added; required before future write milestones |
| Recovery/hard-stop readiness guard | Synthetic tests require abort-after-failed-restore/read-back/audit, backup preservation, no retry on same copy before recovery, maintainer/owner escalation, and default-disabled reset/probe markers | Non-mutating guard added; required before future write milestones |
| Concurrency/lock-contention readiness guard | Synthetic tests require serialized per-book lock acquisition evidence, active-lock contention blocked/rejected evidence, no overlapping write execution evidence, contention/rejection audit trail evidence, and default-disabled no-write probe | Non-mutating guard added; required before future write milestones |
| Maintainer #36 audit checklist | `docs/write-alpha-maintainer-checklist.md` now links accepted #36 evidence, states remaining blockers, preserves no-release/no-public-write posture, and lists exact next worker packages; `scripts/check_write_safety_defaults.py` guards required checklist wording | Non-mutating audit package added; #36 should stay open |
| Maintainer review/recovery packet | `docs/write-alpha-recovery-procedure.md` now defines pre-milestone human checkpoints, a hard-stop/recovery decision tree, evidence required before future copied-book/write milestones, rollback/read-back/audit expectations, and separation between non-mutating evidence and future mutation evidence | Non-mutating documentation packet added; not copied-book/write evidence |
| Disabled route probes | CREATE/PATCH/DELETE -> 403 after reset | Passed |
| Real working/private/original book | No accepted evidence; not authorized | Blocked |
| Public write beta | No accepted milestone decision | Blocked |
| Stable/production/security-audited claim | No audit or release basis | Blocked |

## Current #36 readiness interpretation

#36 should remain open for the current milestone. The accepted copied/restorable evidence is useful
for readiness, but it does not authorize real working-book mutation, public write beta, default write
enablement, production use, or stable/security-audited claims. Any future real working-book trial still
requires owner and PM confirmation in the same execution context plus backup, restore, Desktop-closed,
preflight, reset, and redaction evidence.

The maintainer review/recovery packet is documentation evidence only. It tightens the operator review
and recovery procedure for future owner-only milestones, but it does not replace copied/restorable
mutation evidence and does not reduce the remaining #36 blockers.
