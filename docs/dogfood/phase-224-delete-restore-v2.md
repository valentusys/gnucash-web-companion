# Phase 224 — Write-alpha DELETE restore proof v2

Date: 2026-05-21
Status: PASS — one synthetic/disposable DELETE succeeded; backup restore/read-back was proved from the same single backup; default read-only reset passed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-3/roadmap-cycle-3.md` (Cycle 3, Phase 3 only)

## Scope

This phase reran only the DELETE route-family dogfood after the Phase 222/223 backup evidence hardening.

The run used:

- committed synthetic fixture source: `apps/api/tests/fixtures/test-book.gnucash.sqlite`;
- a temporary external disposable copy as source provenance;
- ignored runtime copy: `data/books/main.gnucash.sqlite`;
- ignored runtime app/backup/lock storage under `data/`;
- explicit local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` for the DELETE runtime;
- dummy local admin credentials only.

No create/PATCH routed write was rerun. No real/private/only-copy book was used. No release/tag/package/image was published.

## Evidence summary

Preflight and setup:

```text
stopped-runtime cleanup dry-run: app runtime artifact found only
stopped-runtime cleanup execute: removed previous ignored app runtime artifact
write-alpha preflight: status=ready; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; size_bytes=212992; sha256_12=c8f22b449c49; dry_run=true
runtime copy prepared under ignored data/books
```

DELETE route-family smoke:

```text
PASS: write-alpha DELETE restore smoke completed with redacted output
ok: exactly one existing synthetic transaction DELETE succeeded
ok: API and runtime SQLite absence checks confirmed transaction was deleted
ok: backup count increased by exactly one before mutation response returned
ok: audit success count increased by exactly one
ok: backup contained the deleted transaction with matching bounded split fingerprint
ok: write lock evidence status=stale_released; active=false
```

The host-side helper could not read the root-owned backup artifact for its built-in restore copy and therefore did not perform a host-side restore. The successful DELETE was not rerun. A follow-up container-side restore proof used the same single backup artifact from that DELETE run:

```text
ok: container-side single backup readable
ok: delete audit count=1
ok: restore checksum matched backup
ok: sqlite/API read-back found the restored deleted transaction
ok: restored transaction id prefix=92cfb49a
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
stopped-runtime cleanup dry-run before cleanup: books=2, app=1, backups=2, locks=1; lock evidence unreadable/stopped-runtime only
host cleanup hit root-owned backup permission boundary and stopped
via-compose cleanup execute: backups=2 removed; stale_released lock removed; output redacted
final stopped-runtime cleanup dry-run: books=0, app=0, backups=0, locks=0
```

## Acceptance result

- Exactly one routed `DELETE /books/{book_id}/transactions/{transaction_id}` succeeded.
- API and runtime SQLite absence were confirmed after DELETE.
- Exactly one successful `transaction.delete` audit row was counted for the run.
- Exactly one corresponding backup file was identified under ignored backup runtime storage.
- The backup was readable inside the API container, checksum-copied back over the ignored runtime copy, and then verified by SQLite and API read-back to contain the deleted synthetic transaction.
- The write lock was stale/released, not active.
- The stack was reset to default write-disabled mode and read-only API smoke confirmed validate/create/PATCH/DELETE all returned 403.
- Ignored runtime books, app DB, backups, and locks were cleaned after Docker shutdown.

## Commands run

```bash
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 docker compose down --remove-orphans
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-disposable-copy>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-delete-restore-smoke.py
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose exec -T api python <container-side-restore-proof>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 docker compose down --remove-orphans
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 docker compose down --remove-orphans
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute --via-compose
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
```

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains the default. The only routed write in this phase was one explicit local DELETE under `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true` against an ignored synthetic/disposable runtime copy. No raw book, backup, app DB, `.env`, screenshot, export, token, key, cert, account name, memo, amount, private path, or private financial data is committed. This is bounded synthetic/disposable write-alpha evidence only; it is not a production, security, or real/private-book write-safety claim.
