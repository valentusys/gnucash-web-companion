# Maintainer copied-book dogfood packet

Status: Phase 253 maintainer packet for future owner-run copied-book dogfood.

This packet is an operator procedure only. Phase 253 does not run dogfood, does not mutate a book,
does not request private paths, and does not prove write-alpha safety for real/private, original,
production, shared, or only-copy books.

## Default recommendation

Start with dry-run only.

Do not proceed to CREATE until the dry-run, external backup, restore plan, redaction plan, and
explicit local write-alpha gates have all passed. Do not perform PATCH in the same session unless a
later maintainer decision explicitly authorizes it. Do not perform DELETE unless it is separately and
specifically authorized against a test transaction created by write-alpha in the bounded dogfood run.

## Hard safety boundary

Forbidden targets:

- the original GnuCash book;
- the only existing copy of any book;
- a book inside the git checkout;
- a book whose raw path, account names, memos, amounts, screenshots, CSV rows, or contents would need
  to be committed as evidence;
- production, shared, LAN/VPN-exposed, or public-internet deployments.

Allowed target shape:

- an outside-git copied/restorable working book;
- an independent pre-mutation backup exists before the app opens the copy;
- the original book remains closed and untouched;
- the app is bound to local-only addresses;
- write-alpha is explicitly enabled only for the bounded test run;
- `APP_ENV=test` is present;
- reset to `GNUCASH_WRITES_ENABLED=false` is verified at the end.

If any condition is unclear, stop and do dry-run only.

## Packet checklist

Use this checklist in order.

1. Preflight.
2. Independent backup.
3. Dry-run.
4. Optional one CREATE only.
5. Optional PATCH later, only after review.
6. DELETE prohibited unless separately authorized for a write-alpha-created test transaction.
7. Compatibility check after mutation.
8. Evidence redaction.
9. Restore verification.
10. Cleanup.
11. Reset to default false.

## 1. Preflight

Run preflight before starting a write-enabled app stack.

Required checks:

- source/original book is not used as the runtime target;
- copied working book exists outside git;
- copied working book is readable by the operator account expected to run Docker/runtime commands;
- backup destination is outside git or explicitly ignored;
- no committed config sets `GNUCASH_WRITES_ENABLED=true`;
- explicit write-alpha run would use both `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test`;
- local-only binding is planned;
- evidence can be reduced to redacted counts/statuses/placeholders.

Command shape, with placeholders only:

```bash
GNUCASH_WRITES_ENABLED=true APP_ENV=test \
python3 scripts/write_alpha_preflight.py \
  --target <copied-book-path> \
  --backup-dir <external-or-ignored-backup-dir>
```

Do not paste the real command with private paths into committed docs, GitHub issues, chat reports, or
release notes.

Stop if preflight rejects the target or prints a warning you cannot explain safely.

## 2. Independent backup

Before any mutation-capable run:

1. Stop GnuCash Desktop and this app for the copied working book.
2. Create an independent backup of the copied working book outside git and outside app runtime backup
   directories.
3. Verify the backup is readable and restorable using local-only operator tools.
4. Record only `<external-backup-ref>` or counts/statuses in notes.

Do not alter, replace, or back up over the original book. The original remains untouched for the whole
packet.

## 3. Dry-run first

Dry-run is the default recommended action.

Dry-run goals:

- validate preflight/readiness;
- confirm the app can be configured without exposing the original;
- confirm redaction workflow;
- confirm reset to default false;
- perform no create, no PATCH, no DELETE, and no write-enabled mutation.

Suggested dry-run command shapes:

```bash
GNUCASH_WRITES_ENABLED=true APP_ENV=test \
python3 scripts/write_alpha_preflight.py \
  --target <copied-book-path> \
  --backup-dir <external-or-ignored-backup-dir>
```

```bash
GNUCASH_WRITES_ENABLED=true APP_ENV=test \
python3 scripts/write_alpha_readiness.py --redacted
```

If using Docker/Caddy for a default-disabled browser/API smoke, render or run it with the safe default:

```bash
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> \
docker compose config --quiet
```

The rendered/default posture must keep `GNUCASH_WRITES_ENABLED=false` unless this is the explicit,
short-lived write-alpha test run. Dry-run evidence should record `backup_count=0`, `audit_row_count=0`,
`lock_status=not-acquired-no-mutation`, and `disabled_reset_status=verified-default-false` when
applicable.

## 4. Optional one CREATE only

CREATE is optional and must be a separate, explicit maintainer decision after dry-run passes.

Rules for a one-CREATE run:

- use only the outside-git copied/restorable working book;
- verify the independent backup immediately before starting;
- enable writes only locally and only with `APP_ENV=test`;
- create exactly one small test transaction intended for later removal by restore, not a real
  financial operation;
- verify read-back, one successful audit row, backup evidence, and lock release;
- do not PATCH or DELETE in the same step unless separately authorized later;
- stop after evidence and restore/reset.

The app records write-alpha ownership metadata for transactions created through the write-alpha CREATE
flow. That ownership marker limits later PATCH/DELETE eligibility in this app, but it does not make
real/private or only-copy books safe for writes.

## 5. Optional PATCH later

PATCH is not part of the default packet run.

PATCH may be considered only after a successful dry-run and one-CREATE run are reviewed. If authorized,
PATCH only the transaction created by write-alpha in the same bounded dogfood scenario and only while
all gates and backups are still valid.

Never PATCH historical/imported/manual transactions from the source book. Backend ownership guards
must reject non-owned PATCH attempts, but the operator procedure should not rely on mistakes to test
private data.

## 6. DELETE prohibited by default

DELETE is prohibited in this packet unless a later instruction specifically authorizes it.

If DELETE is ever authorized, it must be limited to a write-alpha-created test transaction from the
bounded dogfood scenario. It must not target historical/imported/manual transactions. It must include a
fresh backup, audit/lock evidence, restore proof, and reset proof.

If there is no explicit DELETE authorization, do not run DELETE.

## 7. Compatibility check after mutation

After CREATE, and after any later authorized PATCH/DELETE, run the Phase 256 compatibility harness before restore verification:

```bash
python3 scripts/write_alpha_compatibility_check.py \
  <copied-book-path> \
  --output <redacted-compatibility-evidence-json>
```

Expected result semantics:

- `pass` means piecash read passed and already-available `gnucash-cli` report probing passed.
- `blocked` means piecash read passed but Desktop/CLI tooling was unavailable; Desktop compatibility evidence remains blocked.
- `fail` means piecash read failed, or available Desktop/CLI tooling failed or timed out.

This is a best-effort local check only. It does not prove broad GnuCash Desktop/version compatibility and does not make real/private, production, original, shared, or only-copy books safe for write-alpha.

The compatibility evidence must be redacted: no raw paths, account names, transaction descriptions, split memos, amounts, Desktop stdout/stderr, screenshots, CSV rows, or payloads.

## 8. Evidence redaction

Evidence may include only bounded, redacted facts:

- phase/scenario label;
- `synthetic` or `copied_disposable` classification;
- command names with private arguments replaced by placeholders;
- pass/fail/blocked result;
- counts for backups and audit rows;
- lock status;
- restore proof status;
- disabled reset status;
- opaque artifact refs.

Evidence must not include:

- raw filesystem paths, hostnames, usernames, mount paths, or filenames;
- real/private book files, copied books, app DBs, backups, lock files, `.env` files, CSV exports, or
  screenshots;
- account names/descriptions, transaction descriptions, split memos, notes, amounts, balances, prices,
  quantities, or request/response payloads;
- tokens, keys, certs, raw JWTs, or passwords.

Use the Phase 236 helper before committing any dogfood evidence:

```bash
python3 scripts/redact_dogfood_evidence.py <redacted-evidence-json>
```

Treat helper success as an extra guard, not as permission to commit private data. Human review still
must confirm the evidence contains placeholders only.

## 9. Restore verification

After CREATE, and after any later authorized PATCH/DELETE, verify restore before treating the run as
usable evidence.

Restore steps:

1. Stop the app stack.
2. Keep the mutated copied working book isolated outside git.
3. Restore the copied working book from the independent pre-mutation backup.
4. Verify the restored copy is readable through the intended read-only path.
5. Verify the test mutation is absent when restore is expected to remove it.
6. Record only redacted restore status and counts.

Never restore over or otherwise modify the original book.

## 10. Stop conditions

Stop immediately if any of these happen:

- original or only-copy book is selected as the app target;
- copied working book or backup is inside tracked git paths;
- preflight fails or reports unexplained unsafe posture;
- independent backup is missing, unreadable, or not restorable;
- `APP_ENV=test` is absent during an explicit write-alpha run;
- `GNUCASH_WRITES_ENABLED=true` appears in committed defaults or persistent unreviewed config;
- stack binds beyond local-only access;
- a write endpoint succeeds when writes are expected to be disabled;
- audit, backup, lock, ownership, or restore evidence is missing or inconsistent;
- redaction cannot remove raw paths, account names, memos, amounts, screenshots, CSV rows, app DBs,
  backups, tokens, keys, certs, or private book data.

On stop, do not try a second mutation. Preserve local-only evidence for operator review, then restore
and reset before any later attempt.

## 11. Cleanup

After dry-run or mutation run:

1. Stop Docker Compose and local app processes.
2. Remove or archive local-only runtime containers/volumes according to the operator's normal local
   cleanup policy.
3. Keep copied working books and backups outside git.
4. Do not commit `.env`, app DBs, books, backups, lock files, CSV exports, screenshots, or raw logs.
5. Commit only redacted docs/evidence that have passed review.

If runtime files are root-owned, stop the runtime first and use the repository cleanup helper or a
container-side cleanup only for ignored runtime paths. Do not use cleanup as permission to touch the
original book.

## 12. Reset to default false

Every run ends by proving the default disabled posture.

Required reset proof:

```bash
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> \
docker compose config --quiet
```

Then verify the rendered config and committed defaults still keep:

```text
GNUCASH_WRITES_ENABLED=false
```

When the stack is running in default-disabled mode, validate/create/PATCH/DELETE probes should return
403. `python3 scripts/check_public_status.py` should still pass.

## Operator summary template

Use this redacted summary shape after a dry-run or authorized one-CREATE run:

```text
scenario: <dry-run|create-one>
classification: copied_disposable
original book used: no
copy outside git: yes
independent backup: verified|blocked
preflight: pass|fail|blocked
mutation performed: no|create-one
backup_count: <count>
audit_row_count: <count>
lock_status: <bounded-status>
compatibility_check_status: pass|blocked|fail|not-run
compatibility_scope: best-effort-one-run-no-broad-claim
restore_proof_status: <bounded-status>
disabled_reset_status: verified-default-false|failed
private data in committed evidence: no
next action: stop|review before CREATE|review before PATCH
```

Do not include private paths, account names, memos, amounts, screenshots, CSV rows, payloads, or raw
logs in the summary.
