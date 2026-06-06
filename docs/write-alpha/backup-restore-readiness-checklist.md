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

## Docs/tests-only reviewer packet

For non-mutating readiness maintenance, the reviewer packet is limited to wording and guard evidence:

- accepted inputs: tracked docs, pure Python guard output, and pytest assertions that read tracked text only;
- forbidden inputs: filesystem backup copies, restore artifacts, app DB records, private path snippets, account names, transaction descriptions, memos, amounts, screenshots, or CSV/export rows;
- do not fill operational markers such as `backup_location`, `restore_hash_verified`, `restore_row_count_verified`, or `restore_schema_marker_verified` from assumptions when no authorized restore drill was run;
- backup manifest and checksum wording must use opaque refs plus redacted status summaries only, never raw paths, filenames, account names, memos, amounts, app DB rows, books, or backup artifacts;
- proof language must say `docs/tests-only restore-readiness wording check`, not disaster-recovery validation or public write beta readiness;
- any disabled-write probe described by this packet must remain a documented no-op expectation under `GNUCASH_WRITES_ENABLED=false`, not an executed product mutation;
- docs/tests-only wording validation is not recovery proof and cannot replace an authorized restore-to-copy drill against a copied/restorable or synthetic/disposable fixture.

## Default-disabled wording contract

Docs/tests-only checks may prove that the repository wording stayed conservative, but they must not convert backup/restore readiness into write permission. The wording contract for this task class is:

- default-disabled restore readiness means write routes are still expected to reject mutation attempts unless a separately authorized `APP_ENV=test` write session is explicitly armed;
- a documented disabled-write probe is an expected-failure/no-write statement, not evidence that the application mutated or restored a book;
- restore-to-copy wording must explicitly say the restore target is a separate disposable copy and must not overwrite the current copied fixture, original book, working book, or only-copy book;
- backup availability, restore helper availability, and restore-to-copy planning are prerequisites for future authorization, not approval to run dogfood or touch private data;
- if restore wording cannot be verified from tracked docs/tests alone, the safe result is a checkpoint, not a fallback to creating filesystem backup or restore evidence.

## Negative-result labels for repeated docs/tests tasks

When a generated or repeated backup/restore-readiness task has only tracked wording evidence, the review result must use explicit negative labels instead of implying operational proof:

- `NOT_RESTORE_DRILL`: no restore command was run and no restored book was opened;
- `NO_BACKUP_ARTIFACT_CREATED`: no backup copy, checksum manifest, app DB row, or runtime evidence was created for the task;
- `DO_NOT_ENABLE_WRITES`: the result does not authorize changing `GNUCASH_WRITES_ENABLED=false`, arming write routes, or relaxing the `APP_ENV=test` gate;
- `NO_PRIVATE_DATA_REVIEWED`: the task reviewed tracked wording/guard behavior only, not private books, paths, accounts, transactions, memos, amounts, screenshots, exports, backups, or logs.

If these labels cannot be stated truthfully, stop and checkpoint rather than broadening scope into backup creation, restore execution, dogfood, or private-data inspection.

Repeated generated docs/tests tasks must also avoid churn. If the tracked wording and guard assertions already satisfy this boundary, the safe outcome is an explicit no-change checkpoint using the labels above, not creating a new backup/restore procedure, operational evidence, runtime manifest, or cosmetic edit solely to produce a diff.

## Docs/tests-only assertion template

A repeated readiness-docs task may report this wording-only assertion only when it can be proven from tracked docs/tests and guard output:

```text
backup_restore_readiness_scope=docs-tests-only
restore_drill_performed=false
backup_artifact_created=false
private_data_reviewed=false
writes_enabled_or_app_env_gate_relaxed=false
runtime_backup_manifest_reviewed=false
restore_target_opened=false
```

The assertion must not include raw backup manifests, checksum lines, restore filenames, private paths, account names, descriptions, memos, amounts, screenshots, exports, app DB rows, books, backups, runtime logs, or product dogfood output. If a reviewer cannot truthfully set every boolean above to the conservative value, the safe result is a checkpoint, not an operational restore-readiness claim.

## Code guard

`apps/api/app/write_alpha_readiness.py` exposes:

```python
validate_backup_restore_readiness_evidence(evidence)
```

The function is pure/non-mutating and returns a redacted `WriteAlphaReadiness` report. It fails closed when required markers are missing and never echoes raw evidence values.

## Safety boundary

- This checklist is evidence readiness only; it is not a write milestone approval.
- Checklist maintenance is non-mutating: safe changes may update docs or guards that verify wording, but must not create backups, must not restore into books, must not open private data, and must not run product dogfood.
- For docs/tests-only readiness work, restore-to-copy validation remains non-mutating and does not create backup artifacts, restore artifacts, or app DB records.
- Public readiness evidence remains restore-to-copy only and must use copied/restorable or synthetic/disposable targets; it must never overwrite a real/original/private/working/only-copy book.
- Restore evidence must use opaque restore refs and redacted marker summaries only; do not publish filenames, private paths, account names, descriptions, memos, amounts, row contents, screenshots, exports, app DB rows, books, or backup artifacts.
- A successful restore-to-copy marker does not prove broad compatibility or only-copy safety; it only proves that the named copied/synthetic fixture evidence met this checklist.
- Any later enabled write-alpha/writebeta restore drill remains `APP_ENV=test` gated and must reset to `GNUCASH_WRITES_ENABLED=false` afterward.
- It does not claim v0.2 readiness, public write beta readiness, production safety, stable release readiness, or security-audited status.
- It does not make real/private/original/only-copy books safe targets.
- Any future mutation still requires exact same-context owner and PM authorization plus the existing write-alpha/writebeta gates, backup, audit, read-back, restore verification, compatibility, reset, and redaction checks.
