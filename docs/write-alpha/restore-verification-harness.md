# Restore verification harness

Status: Phase 257 operator-facing restore proof for copied-book write-alpha dogfood.

This harness verifies that an outside-git copied/disposable working book can be restored from an independent pre-mutation backup after a bounded write-alpha dogfood run. It is not a production disaster-recovery procedure and does not make real/private, original, shared, or only-copy books safe for writes.

## Safety boundary

Use only:

- a copied/disposable working book outside the git checkout;
- an independent pre-mutation backup outside the git checkout;
- local-only operator execution;
- redacted evidence only.

Never use this harness to restore over the original book. Never commit the working book, backup, app DB, `.env`, screenshots, CSV exports, raw paths, account names, memos, amounts, tokens, keys, or certs.

## Command shape

Stop the app stack first, then run with placeholders only in committed docs/reports:

```bash
python3 scripts/write_alpha_restore_verify.py \
  --target <copied-working-book-path> \
  --backup <pre-mutation-backup-path> \
  --output <redacted-restore-evidence-json> \
  --expected-restored-sha256 <optional-full-backup-sha256> \
  --api-read-command <read-only-api-or-web-probe-command> \
  --confirm-copied-disposable \
  --confirm-original-untouched \
  --confirm-restore-over-copy \
  --confirm-backup-pre-mutation
```

The script:

1. rejects missing files and files inside this git checkout;
2. requires explicit confirmations that the target is copied/disposable, the original remains untouched, restore is over the copy only, and the backup is pre-mutation;
3. copies the backup over the copied working book;
4. verifies restored checksum matches the backup checksum and, when supplied, the expected full sha256;
5. opens the restored copy read-only with piecash and records only bounded counts;
6. optionally runs an operator-supplied read-only API/web probe command with stdout/stderr redacted;
7. verifies committed/default `GNUCASH_WRITES_ENABLED=false` posture via Docker Compose config when available;
8. writes redacted JSON evidence and validates it with the Phase 236 redaction helper before writing.

## Result semantics

- `pass`: restore checksum matched, optional expected checksum matched when provided, piecash read-back passed, read-only API/web probe passed, and default-disabled reset proof passed.
- `blocked`: restore checksum and piecash read-back passed, but no read-only API/web probe was supplied or Docker Compose reset proof could not run in the local environment.
- `fail`: checksum mismatch, expected checksum mismatch, piecash read failure, API/web probe failure, or default-disabled posture failure.

`blocked` is usable as local restore filesystem evidence only; it is not complete web/API restore evidence.

## Evidence contract

The evidence file records only redacted fields:

- `restore_status`, `checksum_status`, and short checksum prefixes;
- bounded piecash read-back counts;
- `api_read.status` and a placeholder command label;
- `restore_proof_status`;
- `disabled_reset_status`;
- `backup_count=1`, `audit_row_count=0`, and offline restore lock status;
- placeholders for command arguments and artifact refs.

It does not include raw paths, filenames, account names, transaction descriptions, split memos, amounts, API response bodies, Desktop output, screenshots, CSV rows, app DBs, books, backups, `.env`, tokens, keys, or certs.

## Relationship to copied-book dogfood

Run this after a bounded CREATE-only copied-book dogfood step and after the Phase 256 compatibility check. If a later phase explicitly authorizes PATCH or DELETE on a write-alpha-created test transaction, run restore verification after that mutation too.

A successful restore proof only says the copied/disposable working book was restored from the provided backup in this local run. It does not prove broad disaster recovery, production readiness, public-internet safety, security, or real/private-book write safety.
