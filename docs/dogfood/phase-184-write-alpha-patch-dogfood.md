# Phase 184 — write-alpha PATCH disposable dogfood

Date: 2026-05-20
Status: PASS — one synthetic/disposable PATCH dogfood run completed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 3 only)

## Scope

This phase exercised the existing experimental `PATCH /books/{book_id}/transactions/{transaction_id}` route on a copied committed synthetic fixture only.

No new write endpoint, write field, account/amount mutation, release, tag, package, real/private book, only-copy book, screenshot, export, `.env`, token, key, cert, app DB, runtime book, backup, or lock artifact was committed.

## Fixture and runtime boundary

Preflight source/runtime/backup classes were checked before the write run:

```text
status=ready; book=<redacted.gnucash.sqlite>; reason=write-alpha copied-book preflight passed without copying or mutation; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; size_bytes=212992; sha256_12=c8f22b449c49; dry_run=true
```

Runtime setup:

- source: committed synthetic fixture copied first to a temporary external disposable source under `/tmp`, then into ignored `data/books/main.gnucash.sqlite`;
- app metadata DB: ignored `data/app/app.db` created by local Docker runtime;
- backups: ignored `data/backups/`;
- locks: ignored `data/locks/`;
- write-enabled run env: `APP_ENV=test`, `GNUCASH_WRITES_ENABLED=true`, dummy local-only admin password/JWT secret;
- reset run env: default Compose write-disabled mode, no `GNUCASH_WRITES_ENABLED=true`.

## Write-alpha PATCH evidence

The PATCH smoke was run inside the API container so Docker-created root-owned lock files could be inspected without host permission false negatives. Output was redacted and did not print transaction descriptions from the original fixture, account names, amounts, raw memos, paths, cookies, app DB rows, backup filenames, or private data.

```text
write-alpha PATCH smoke: target=http://localhost:8000
ok: APP_ENV=test and GNUCASH_WRITES_ENABLED=true were supplied by local runtime command
ok: source/runtime/backup paths were preflighted outside script and runtime book was an ignored disposable copy
ok: health/books/read-only transaction detail routes passed
ok: missing-transaction PATCH returned 404 without a new backup
ok: exactly one metadata/split-memo PATCH succeeded
ok: API read-back matched synthetic PATCH markers only
ok: runtime SQLite read-back matched markers and split amount fingerprint was unchanged
ok: backup count increased before mutation response returned
ok: audit success count increased by exactly one and failed safe-error audit was recorded
ok: write lock evidence status=stale_released; lock file remains but is not actively held; with the app stopped an operator may remove only the book-specific stale lock from ignored runtime storage
PASS: write-alpha PATCH smoke completed with redacted output
```

Evidence covered:

- exactly one successful PATCH of transaction metadata/split memo markers;
- no PATCH of split amounts or accounts;
- API read-back matched the synthetic marker values only;
- runtime SQLite read-back confirmed marker values and unchanged split amount fingerprint;
- one new pre-write backup file existed in ignored backup storage;
- one successful `transaction.patch` audit row existed;
- one failed missing-transaction `transaction.patch` audit row existed with no backup path;
- lock probe from inside the API container showed `stale_released`, not an active `flock` hold.

## Return to default false and disabled-write probes

After stopping the write-enabled runtime, Docker Compose was restarted without `GNUCASH_WRITES_ENABLED=true`. The standard read-only API smoke passed and confirmed validate/create/PATCH/DELETE all returned disabled-write `403` responses.

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

Docker Compose config validation also confirmed the default remains false:

```text
GNUCASH_WRITES_ENABLED: "false"
```

## Teardown / no-artifact result

After verification, Docker was stopped and ignored runtime artifacts were removed via a one-shot Alpine container mounted on `data/` to avoid host permission issues from root-owned Docker files.

No remaining ignored runtime files were found under `data/books`, `data/backups`, `data/locks`, or `data/app` except tracked `.gitkeep` placeholders.

## Safety result

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The only write-enabled run used explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`.
- The write target was a copied synthetic fixture in ignored runtime storage.
- No real/private/only-copy book was read or mutated.
- No raw runtime book, app DB, backup, lock, `.env`, token, key, cert, screenshot, export, path, account name, original transaction description, original memo, amount, or private financial data was committed.
- No release/tag publication was performed.
