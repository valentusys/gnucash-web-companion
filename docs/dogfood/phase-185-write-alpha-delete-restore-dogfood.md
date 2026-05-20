# Phase 185 — write-alpha DELETE disposable dogfood with restore proof

Date: 2026-05-20
Status: PASS — bounded synthetic/disposable DELETE evidence captured; restore path proved on the copied runtime book
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 4 only)

## Scope

This phase exercised the existing experimental DELETE transaction route exactly once on a committed synthetic fixture copied into ignored runtime storage. The run used explicit local-only write-alpha gates:

- `APP_ENV=test`
- `GNUCASH_WRITES_ENABLED=true`
- dummy local admin credentials
- ignored runtime book under `data/books/`
- ignored backup/app/lock runtime directories under `data/`

No real/private/only-copy book was used. No release/tag/package was published.

## Evidence summary

Preflight:

- Disposable source: temporary external copy of the committed synthetic fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Runtime target: ignored `data/books/main.gnucash.sqlite`.
- Backup class: ignored `data/backups/`.
- Redacted preflight result: `status=ready`, `source=external copied/disposable`, `runtime=ignored data/books`, `backups=ignored data/backups`, `size_bytes=212992`, `sha256_12=c8f22b449c49`, `dry_run=true`.

Write-enabled DELETE run:

- Local Docker runtime was started with `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true`.
- `scripts/smoke/write-alpha-delete-restore-smoke.py` authenticated against the API and discovered the default synthetic book.
- The helper selected one existing synthetic transaction by ID only; it did not print account names, descriptions, memos, amounts, backup filenames, cookies, or raw app DB contents.
- Pre-delete transaction detail read-back passed.
- Exactly one `DELETE /books/{book_id}/transactions/{transaction_id}` request succeeded.
- Response included bounded write result metadata: transaction ID match, audit log ID present, and backup evidence present.
- API read-back for the deleted transaction returned `404` after DELETE.
- Runtime SQLite absence check confirmed the transaction was absent from the mutated copy.
- Backup count increased by exactly one.
- Successful `transaction.delete` audit count increased by exactly one.
- Backup contained the deleted transaction with the same bounded split fingerprint as before deletion.
- Runtime checksum changed after DELETE.
- Backup checksum matched the pre-delete runtime checksum.
- Restore was performed by copying the generated pre-write backup back over the ignored runtime copy.
- Restored runtime checksum matched backup checksum.
- Restored runtime SQLite check found the transaction again with the same bounded split fingerprint.
- Restored API transaction detail read-back passed.
- Lock evidence from inside the API container reported `stale_released`, not active; no active flock holder remained.

Reset-to-default read-only run:

- Runtime was restarted without `GNUCASH_WRITES_ENABLED=true`, returning to the default disabled-write configuration.
- `scripts/smoke/read-only-api-smoke.py` passed after restore.
- Disabled write probes returned `403` for validate, create, PATCH, and DELETE.

Teardown:

- Docker Compose runtime was stopped.
- Ignored runtime `data/books/*`, `data/backups/*`, `data/app/*`, and `data/locks/*` were removed.
- A follow-up file search under `data/` found only tracked `.gitkeep` placeholders.
- No raw book, app DB, backup, lock artifact, `.env`, token, key, certificate, screenshot, export, account name, original description, memo, amount, backup filename, private path, or private financial data was committed.

## Commands run

```bash
python3 -m py_compile scripts/smoke/write-alpha-delete-restore-smoke.py
rm -rf data/books/* data/backups/* data/app/* data/locks/*
mkdir -p data/books data/backups data/app data/locks
tmp_source=$(mktemp --suffix=.gnucash.sqlite)
cp apps/api/tests/fixtures/test-book.gnucash.sqlite "$tmp_source"
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/phase185 "$tmp_source"
cp "$tmp_source" data/books/main.gnucash.sqlite
rm -f "$tmp_source"
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose up -d
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose exec -T api python - --api-base-url http://localhost:8000 --password dummy --app-db /data/app/app.db --backup-root /data/backups --lock-root /data/locks --runtime-book /data/books/main.gnucash.sqlite < scripts/smoke/write-alpha-delete-restore-smoke.py
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 docker compose down
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-api-smoke.py
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose down
rm -rf data/books/* data/backups/* data/app/* data/locks/* || docker run --rm -v "$PWD/data:/data" debian:12-slim sh -c 'rm -rf /data/books/* /data/backups/* /data/app/* /data/locks/*'
```

## Redacted helper output

```text
write-alpha DELETE restore smoke: target=http://localhost:8000
ok: APP_ENV=test and GNUCASH_WRITES_ENABLED=true were supplied by local runtime command
ok: source/runtime/backup paths were preflighted outside script and runtime book was an ignored disposable copy
ok: health/books/read-only transaction detail routes passed before DELETE
ok: exactly one existing synthetic transaction DELETE succeeded
ok: API and runtime SQLite absence checks confirmed transaction was deleted
ok: backup count increased by exactly one before mutation response returned
ok: audit success count increased by exactly one
ok: backup contained the deleted transaction with matching bounded split fingerprint
ok: restored runtime copy checksum matched backup checksum and restored API read-back passed
ok: write lock evidence status=stale_released; lock file remains but is not actively held; with the app stopped an operator may remove only the book-specific stale lock from ignored runtime storage
PASS: write-alpha DELETE restore smoke completed with redacted output
```

```text
read-only API smoke: target=http://localhost:8080/api
ok: API health
ok: login
ok: /auth/me
ok: default book discovered via /books and verified at /books/1
ok: accounts endpoint
ok: transactions endpoint
ok: transaction detail endpoint
ok: CSV export endpoint
ok: reports summary
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
ok: delete endpoint is write-disabled
PASS: read-only API smoke checks completed
```

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains the default. The DELETE run was explicit local-only write-alpha dogfood on a synthetic disposable copy under `APP_ENV=test`; the restored copy passed read-only smoke after returning to default disabled writes. This is bounded disposable route/restore evidence only. It is not a production write-safety claim and not real/private/only-copy-book safety evidence.
