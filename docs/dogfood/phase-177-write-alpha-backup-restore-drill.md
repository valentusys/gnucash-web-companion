# Phase 177 — write-alpha backup and restore drill

Date: 2026-05-20
Status: COMPLETE — disposable backup restore drill passed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 6 only)

## Scope

This drill proved that the backup generated before a write-alpha create mutation can restore the pre-write book state for a synthetic/disposable GnuCash SQLite copy.

The drill used only:

- source class: committed synthetic fixture copied to a temporary external path before preflight;
- preflight: Phase 174 dry-run preflight helper with disposable-copy acknowledgement;
- runtime copy class: ignored `data/books/` disposable copy;
- backup class: ignored `data/backups/` local runtime backup created by the existing write route before mutation;
- restored copy class: ignored `data/books/` disposable restore target;
- app DB/lock class: ignored `data/app/` and `data/locks/` runtime paths;
- write run environment: `APP_ENV=test` plus explicit local-only `GNUCASH_WRITES_ENABLED=true`;
- restore/read-only run environment: `APP_ENV=test` with default `GNUCASH_WRITES_ENABLED=false`.

No private, real, or only-copy book was used. No raw book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data is committed.

## Redacted command/result evidence

Commands/results are summarized only. The created transaction was identified only by bounded metadata during the drill and was not committed.

```text
source_preflight=status=ready; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; size_bytes=212992; sha256_12=c8f22b449c49; dry_run=true
write_run=APP_ENV=test; GNUCASH_WRITES_ENABLED=explicit local-only true
write_operation=one balanced two-split create via existing write-alpha create route
write_result=one transaction.create success audit row; tx_id_12=3e1ce7e13dce
backup_before_write=one backup file under ignored data/backups; backup_sha256_12=c8f22b449c49; backup_size=212992
mutated_copy=sha256_12=e502ac9ac38f
lock_state_after_write=lock file remained as expected; flock probe showed active hold=false
restore_target=ignored data/books restored copy
restore_copy_ms=0.43
restored_copy=sha256_12=c8f22b449c49; checksum matched pre-write backup and original external disposable source
restored_transaction_absence=API query for the synthetic create marker returned zero matches
read_only_smoke_after_restore=PASS with GNUCASH_WRITES_ENABLED=false; validate/create/PATCH/DELETE probes returned 403
default_config_after=GNUCASH_WRITES_ENABLED: "false"
teardown=ignored runtime book/app DB/backups/locks removed after verification
```

## Restore procedure exercised

1. Copy the committed synthetic fixture to a temporary external disposable source outside the repository.
2. Run the Phase 174 preflight helper with `--write-alpha-plan --dry-run --confirm-disposable-copy`.
3. Copy the disposable source to ignored runtime storage as `/data/books/main.gnucash.sqlite`.
4. Start local Docker/Caddy with `APP_ENV=test` and explicit `GNUCASH_WRITES_ENABLED=true` only for the write-alpha create run.
5. Execute one balanced two-split create through the existing write-alpha smoke helper.
6. Confirm one successful audit row, one backup file, and released flock state.
7. Copy the generated backup to a separate ignored restore target under `data/books/` and measure restore copy time.
8. Stop the write-enabled runtime.
9. Start local runtime with the restored copy as `GNUCASH_DEFAULT_BOOK_PATH` and without a write-enabled override.
10. Run read-only API smoke and a transaction-absence probe against the restored copy.
11. Confirm default Docker Compose config still renders `GNUCASH_WRITES_ENABLED=false`.
12. Tear down containers and remove ignored runtime books, app DB, backups, and locks.

## Findings

- The backup created before the write-alpha create matched the original pre-write synthetic fixture checksum and differed from the mutated runtime copy checksum.
- Restoring the backup to an ignored runtime path was executable and fast in this local synthetic run (`0.43 ms` copy time for a 212,992-byte fixture).
- The restored copy lacked the transaction created by the write-alpha smoke; the read-only API transaction search for the synthetic create marker returned zero matches.
- The restored copy passed the existing read-only API smoke with writes disabled by default, including validate/create/PATCH/DELETE returning 403.
- The current file-lock implementation may leave a lock file after releasing `flock`; this is expected. Stale-lock cleanup for future failed dogfood/manual recovery remains: stop the write-enabled runtime, verify no active process holds the lock, then remove ignored `data/locks/*` as part of teardown/recovery before restarting.
- The app metadata DB contains audit rows only for the runtime that performed the write; restoring a book copy does not restore or rewrite app DB audit history. This is expected for this app model and was documented as runtime-state evidence, not book-content evidence.

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains the default. The explicit write-enabled run was local-only, `APP_ENV=test`, synthetic/disposable, and temporary. Backup and restored copy stayed under ignored runtime paths and were removed after verification. This is not production/private-book disaster recovery evidence and does not make write-alpha safe for real/private or only-copy books.
