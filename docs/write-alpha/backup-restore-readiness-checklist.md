# Backup/restore readiness evidence checklist

This checklist is a non-mutating guard for future controlled-write packages. It does not authorize any CREATE, PATCH, or DELETE operation. It is meant to make backup/restore evidence explicit before any later write milestone is considered.

## Required markers

A future package must fail closed unless its redacted evidence includes all of these bounded markers:

| Marker | Required value | Why |
|---|---|---|
| `fixture_classification` | `copied-disposable`, `copied-restorable`, `synthetic-disposable`, or `synthetic-or-copied-disposable-only` | Proves the target is not an original, private working, or only-copy book. |
| `backup_location` | `outside-git` or `approved-temp-area` | Prevents committed backup artifacts and private paths. |
| `restore_hash_verified` | `true` | Proves restored bytes match the selected backup or expected checksum. |
| `restore_row_count_verified` | `true` | Proves bounded row-count/read-back evidence exists without publishing private rows. |
| `restore_schema_marker_verified` | `true` | Proves schema-marker evidence was checked after restore. |
| `private_raw_evidence_included` | `false` | Rejects raw/private paths, account names, memos, amounts, payloads, screenshots, exports, app DBs, books, or backups. |
| `default_writes_disabled` | `true` | Confirms `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture. |
| `recovery_hard_stop_note` | Text containing stop/hard-stop plus recovery guidance | Makes the operator stop and recover from verified backup before any further write attempt after a failed gate. |
| `abort_after_failed_restore_or_readback_or_audit` | `true` | Requires an explicit hard stop after failed restore, read-back, or audit evidence instead of continuing the write milestone. |
| `backup_preservation_note` | Text containing preserve plus backup guidance | Requires preserving the pre-write backup and damaged candidate/evidence outside git for review. |
| `no_retry_same_copy_without_recovery` | `true` | Blocks retrying writes on the same copied book until recovery/regeneration and read-only checks pass. |
| `maintainer_review_or_owner_escalation` | `true` | Requires maintainer review or owner escalation before any further write attempt after recovery-path failure. |
| `default_disabled_reset_probe` | `true` | Requires reset to `GNUCASH_WRITES_ENABLED=false` plus a disabled-write probe after recovery. |
| `serialized_per_book_lock_acquisition_evidence` | `true` | Proves future write evidence observed serialized per-book lock acquisition rather than parallel mutation. |
| `active_lock_contention_blocked_or_rejected_evidence` | `true` | Proves an active-lock/contention attempt was blocked or rejected before overlapping write execution. |
| `no_overlapping_write_execution_evidence` | `true` | Proves collected evidence found no overlapping write execution for the same book. |
| `audit_trail_includes_contention_rejection` | `true` | Proves the audit trail records lock contention/rejection as a failed/rejected write attempt. |
| `default_disabled_no_write_probe` | `true` | Confirms the default-disabled posture still rejects write probes after the lock-contention evidence package. |

## Code guard

`apps/api/app/write_alpha_readiness.py` exposes:

```python
validate_backup_restore_readiness_evidence(evidence)
```

The function is pure/non-mutating and returns a redacted `WriteAlphaReadiness` report. It fails closed when required markers are missing and never echoes raw evidence values.

## Safety boundary

- This checklist is evidence readiness only; it is not a write milestone approval.
- It does not claim v0.2 readiness, public write beta readiness, production safety, stable release readiness, or security-audited status.
- It does not make real/private/original/only-copy books safe targets.
- Any future mutation still requires exact same-context owner and PM authorization plus the existing write-alpha/writebeta gates, backup, audit, read-back, restore verification, compatibility, reset, and redaction checks.
