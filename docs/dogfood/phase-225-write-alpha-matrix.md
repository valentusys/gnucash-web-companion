# Phase 225 — Combined create/PATCH/DELETE backup-audit matrix

Date: 2026-05-21
Status: PASS — fresh bounded create, PATCH, and DELETE write-alpha route-family matrix passed after backup evidence hardening
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-3/roadmap-cycle-3.md` (Cycle 3, Phase 4 only)

## Scope

This phase produced one fresh bounded write-alpha matrix across the existing create, PATCH, and DELETE route families. Each route family used a separate external temporary disposable copy of the committed synthetic fixture and an ignored runtime copy under `data/books/main.gnucash.sqlite`.

The run used:

- committed synthetic fixture source: `apps/api/tests/fixtures/test-book.gnucash.sqlite`;
- external temporary disposable copies for create, PATCH, and DELETE provenance;
- ignored runtime book/app/backup/lock storage under `data/`;
- explicit local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` only while each write-alpha route-family runtime was running;
- default `GNUCASH_WRITES_ENABLED=false` Docker/Caddy reset after the write-alpha matrix;
- dummy local admin credentials only.

No new write feature, amount/account PATCH expansion, import/account/scheduled write, release/tag/package/image, real/private/only-copy book, or production write-safety claim was added.

## Evidence matrix

| Route family | Successful routed write | Read-back / restore evidence | Backup evidence | Audit evidence | Expected failed probes | Lock evidence | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| create | exactly one balanced two-split create succeeded | API transaction read-back matched the new transaction and two splits | one backup file under ignored backup storage | one successful `transaction.create` audit row with backup evidence | validation rejected unbalanced, invalid-account, and placeholder-style missing-account probes before mutation; no failed write audit row was expected | stale-released, not active | PASS |
| PATCH | exactly one metadata/split-memo PATCH succeeded | API and runtime SQLite read-back matched synthetic PATCH markers; split count and amount fingerprint stayed unchanged | one backup file under ignored backup storage | one successful `transaction.patch` audit row with backup evidence | missing-transaction PATCH returned 404, created no backup, and recorded one failed safe-error audit row without backup | stale-released, not active | PASS |
| DELETE | exactly one existing synthetic transaction DELETE succeeded | API and runtime SQLite absence checks passed; host-readable backup restore and API read-back passed | one backup file under ignored backup storage | one successful `transaction.delete` audit row with backup evidence | no additional DELETE failure probe was run in this phase; the route-family helper did not rerun a successful DELETE | stale-released, not active | PASS |

Additional redacted per-run count checks:

```text
create_evidence backup_files=1 success_audits_with_backup=1 failed_audits=0 failed_without_backup=0
patch_evidence backup_files=1 success_audits_with_backup=1 failed_audits=1 failed_without_backup=1
delete_evidence backup_files=1 success_audits_with_backup=1 failed_audits=0 failed_without_backup=0
```

Default false reset:

```text
PASS: read-only API smoke checks completed
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
ok: delete endpoint is write-disabled
```

Cleanup:

```text
final stopped-runtime cleanup dry-run: books=0, app=0, backups=0, locks=0
```

## Commands run

```bash
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 docker compose down --remove-orphans
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-create-disposable-copy>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-create-smoke.py
<redacted create count check>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose down --remove-orphans
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute --via-compose
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-PATCH-disposable-copy>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-patch-smoke.py
<redacted PATCH count check>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose down --remove-orphans
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute --via-compose
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-DELETE-disposable-copy>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-delete-restore-smoke.py
<redacted DELETE count check>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose down --remove-orphans
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 docker compose down --remove-orphans
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute --via-compose
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
```

## Acceptance result

- All three existing write-alpha route families passed once each on isolated synthetic/disposable runtime copies.
- Every successful write had one matching backup file count and one successful audit row with backup evidence in that isolated run.
- Expected validation/missing-transaction probes failed safely without backup creation; PATCH recorded the expected failed no-backup audit row.
- The helpers did not rerun successful mutations after evidence collection.
- Locks were stale-released/not active after route-family writes.
- The stack was reset to default write-disabled mode and read-only API smoke confirmed validate/create/PATCH/DELETE returned 403.
- Ignored runtime books, app DB, backups, and locks were cleaned after Docker shutdown.

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains the default. `APP_ENV=test` was not weakened. The only write-enabled runs were explicit local synthetic/disposable runs with `GNUCASH_WRITES_ENABLED=true`; all raw runtime book, app DB, backup, and lock artifacts stayed under ignored `data/` and were cleaned. No raw financial data, account names, memos, amounts, backup filenames, `.env`, screenshot, export, token, key, cert, or real/private path is committed.
