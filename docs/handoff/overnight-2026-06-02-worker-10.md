# Overnight worker 10 handoff — #36 concurrency/lock-contention readiness guard

Worker task ID: `overnight-2026-06-02-worker-10`

UTC handoff time: 2026-06-02T06:07:19Z

## Scope completed

Added a non-mutating concurrency/lock-contention readiness package for #36 by extending the existing backup/restore readiness evidence validator from workers 07 and 09.

Changed files:

- `apps/api/app/write_alpha_readiness.py`
- `apps/api/tests/test_write_alpha_readiness.py`
- `docs/write-alpha/backup-restore-readiness-checklist.md`
- `docs/write-alpha/evidence-matrix.md`
- `PROJECT_STATUS.md`
- `docs/handoff/overnight-2026-06-02-worker-10.md`

## TDD evidence

RED:

```text
cd apps/api && pytest tests/test_write_alpha_readiness.py::test_backup_restore_readiness_evidence_blocks_missing_concurrency_lock_contention_markers -q
F ... AssertionError: serialized_per_book_lock_acquisition_evidence
1 failed, 1 warning
```

GREEN:

```text
cd apps/api && pytest tests/test_write_alpha_readiness.py::test_backup_restore_readiness_evidence_blocks_missing_concurrency_lock_contention_markers tests/test_write_alpha_readiness.py::test_backup_restore_readiness_evidence_requires_all_fail_closed_markers -q
2 passed, 1 warning
```

## Readiness markers added

`validate_backup_restore_readiness_evidence()` now fails closed unless redacted/synthetic evidence includes:

- `serialized_per_book_lock_acquisition_evidence=true`
- `active_lock_contention_blocked_or_rejected_evidence=true`
- `no_overlapping_write_execution_evidence=true`
- `audit_trail_includes_contention_rejection=true`
- `default_disabled_no_write_probe=true`

Existing fail-closed requirements remain in place for fixture classification, backup location, restore hash, row count, schema marker, private/raw evidence absence, default writes disabled, recovery/hard-stop notes, abort/hard-stop after failed restore/read-back/audit, backup preservation, no retry on same copy before recovery, maintainer/owner escalation, and default write-disabled reset/probe markers.

## Verification

Focused package tests already run:

```text
cd apps/api && pytest tests/test_write_alpha_readiness.py -q
10 passed, 21 warnings in 1.34s
```

Required verification final run:

```text
cd apps/api && pytest tests/test_write_alpha_readiness.py tests/test_write_alpha_restore_verify.py tests/test_transaction_writes.py::TestWritesDisabledByDefault -q
23 passed, 21 warnings in 5.92s

python3 scripts/check_public_status.py
public-status-guard: ok

python3 scripts/check_tracked_hygiene.py
Tracked hygiene check passed (1737 tracked paths inspected).

git diff --check
passed

JWT_SECRET=*** APP_ADMIN_PASSWORD=*** docker compose config --quiet
passed
```

Static added-line security scan:

```text
git diff | grep '^+' | grep -iE '(api_key|secret|password|token|passwd)\s*=\s*["'"''][^"'"'']{6,}["'"'']' || true
git diff | grep '^+' | grep -E 'os\.system\(|subprocess.*shell=True|\beval\(|\bexec\(|pickle\.loads?\(|execute\(f"|\.format\(.*SELECT|\.format\(.*INSERT' || true
```

No findings.

Independent reviewer note: project `AGENTS.md` forbids `delegate_task` unless explicitly overridden, so no reviewer subagent was launched.

## Safety summary

- CREATE/PATCH/DELETE performed: 0/0/0.
- No real/private/original/working/only-copy GnuCash book was opened, copied, or mutated.
- Tests use synthetic dictionaries and existing test fixtures only.
- No app DBs, books, backups, CSV exports, screenshots, `.env`, tokens, keys, certs, private paths, account names, memos, descriptions, amounts, or raw private evidence were added.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test`, owner-writebeta, write-alpha, and public-readonly gates were not weakened.
- No release/tag/package/image was published.
- No v0.2-ready, public-write-beta, stable, production, or security-audited claim was added.

## Issue #36 update

Recommendation: keep #36 open.

Completed in this package: concurrency/lock-contention readiness evidence is explicit and fail-closed for missing serialized per-book lock acquisition, active-lock contention blocked/rejected, no overlapping write execution, contention/rejection audit trail, and default-disabled no-write probe markers.

Remaining gates to keep open:

- future copied/restorable mutation evidence only under explicit same-context owner + PM authorization;
- exact rollback/error-path and recovery evidence for any future mutation package;
- any broader readiness decision still requires owner/PM review and must not imply real-book or public write readiness.

## Commit / CI

Implementation commit SHA: `f8fb0d1`.

Handoff SHA update: `7b98e98`.

CI: success for pushed `7b98e98` on main: https://github.com/valentusys/gnucash-web-companion/actions/runs/26801932018.

## Next supervisor recommendation

#36 should remain open. Proceed only to a safe copied/restorable evidence package if explicitly authorized in the same execution context; otherwise continue non-mutating readiness guards only. Keep default-disabled/test-gated posture unchanged.
