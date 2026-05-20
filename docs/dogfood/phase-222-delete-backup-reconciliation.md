# Phase 222 — DELETE backup reconciliation evidence

Date: 2026-05-21
Status: COMPLETE — Phase 220 backup-count mismatch reproduced by code inspection/regression and fixed at backup artifact creation.
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-3/roadmap-cycle-3.md` (Cycle 3, Phase 1 only)

## Scope

This phase investigated the Phase 220 bounded write-alpha DELETE evidence anomaly: three successful backup-bearing route-family audit rows existed for create/PATCH/DELETE, but only two readable backup files were counted.

Only synthetic/disposable fixture copies and tests were used. No real/private or only-copy book was opened, copied, backed up, restored, or mutated. No runtime book, backup artifact, app DB, `.env`, screenshot, export, token, key, cert, private path, account name, memo, amount, or raw audit payload is committed here.

## Finding

The backup service generated names from the source stem plus a UTC timestamp with second precision. Fast route-family smokes can execute multiple successful writes against same-named disposable runtime copies inside one second. Because `shutil.copy2` writes to the chosen destination path, an existing backup artifact with the same name could be silently replaced.

That explains the Phase 220 evidence shape without requiring a DELETE-route mutation semantics bug:

```text
successful backup-bearing audit rows: create=1, patch=1, delete=1
readable backup files observed: 2
likely cause: one rapid route-family backup filename collision/overwrite
```

## Fix

`apps/api/app/services/backup.py` now:

- includes microseconds in backup filenames;
- falls back to deterministic `_1`, `_2`, ... suffixes if a candidate path already exists;
- copies with exclusive create mode (`xb`) so an existing backup artifact is never overwritten silently;
- retries on a rare filename race and removes only a partial destination created by its own failed copy attempt.

This preserves existing create/PATCH/DELETE write semantics: backup still happens before mutation and returned/audited `backup_path` still points to the created pre-write artifact. It only hardens backup artifact identity/evidence.

## Regression evidence

Targeted backend regression:

```text
cd apps/api && pytest tests/test_backup_restore.py tests/test_transaction_writes.py tests/test_write_integration.py::TestBackupCreation tests/test_write_integration.py::TestAuditBehavior -q
result: 74 passed
```

The new regression freezes the backup clock and creates three backups for one copied synthetic fixture at the same timestamp. Expected result:

```text
backup 1: base timestamp name
backup 2: same timestamp plus _1 suffix
backup 3: same timestamp plus _2 suffix
file count: 3
content: all three artifacts match the same pre-write source copy
```

Relevant default-disabled write-route coverage remained in `tests/test_transaction_writes.py`; validate/create/PATCH/DELETE stay 403 when writes are disabled.

Smoke helper syntax check:

```text
python3 -m py_compile scripts/smoke/write_alpha_smoke_evidence.py scripts/smoke/write-alpha-create-smoke.py scripts/smoke/write-alpha-patch-smoke.py scripts/smoke/write-alpha-delete-restore-smoke.py
result: passed
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` gate was not changed.
- No write endpoint, write scope, create/PATCH/DELETE mutation semantics, release tag, package, image, or deployment was added.
- Evidence uses only tests and synthetic/disposable fixture copies.
- The Phase 220 release blocker is narrowed to backup filename collision/overwrite; a fresh write-alpha route-family dogfood rerun is still required by later roadmap phases before any release gate.
