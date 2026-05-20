# Backup and Recovery Runbook

> **Pre-alpha warning:** This runbook is conservative operational guidance for local/private testing of `gnucash-web-companion`. It is not a production-grade backup system, disaster-recovery certification, security audit, or guarantee. Always keep GnuCash Desktop as the authoritative editor and test with copied/disposable books first.

## Scope

This runbook covers manual backup and recovery for:

- the app metadata SQLite database;
- copied GnuCash SQL books used by the web companion;
- Docker-mounted data paths used by the default Compose setup;
- restore dry-runs and read-only verification;
- what the experimental controlled-write path is expected to do before writes.

It does not provide automated retention, encrypted off-site backup tooling, point-in-time recovery, high availability, compliance controls, or a guarantee that every GnuCash version/backend can be restored by this app.

## Safety model

The read-only MVP should not modify GnuCash books. Even so, backups matter because local deployments can still lose data through host failure, manual copy mistakes, volume deletion, bad upgrades, or future experimental write testing.

Required safety defaults:

```dotenv
GNUCASH_WRITES_ENABLED=false
```

Controlled writes, if deliberately enabled for post-MVP testing, are experimental and must be tested only on disposable/copy books with backups. Do not use write mode against your only authoritative GnuCash file.

## Data locations

The default Docker Compose setup mounts the repository `./data` directory into containers as `/data`.

| Host path | Container path | Purpose | Backup priority |
| --- | --- | --- | --- |
| `./data/app/app.db` | `/data/app/app.db` | App metadata DB: users, book registry/access metadata, local app state | Back up if you care about local app accounts/configuration. |
| `./data/books/*.gnucash.sqlite` | `/data/books/*.gnucash.sqlite` | Copied GnuCash SQL books read by the app | Back up copied/test books; keep authoritative originals outside this repo. |
| `./data/backups/<book_id>/` | `/data/backups/<book_id>/` | Pre-write backup copies created by experimental controlled-write paths | Preserve if testing write mode; never commit. |
| `./data/locks/` | `/data/locks/` | Runtime write-lock files | Usually not backed up; recreate as runtime state. |

Never commit `data/app/`, `data/books/`, `data/backups/`, `.env`, secrets, keys, certs, screenshots, or real CSV exports.

## Backup frequency

Choose a cadence based on how often the copied book or app metadata changes:

- **Read-only testing with a static copied book:** back up `data/app/app.db` before upgrades and after user/book registry changes; keep the original GnuCash book outside the repository.
- **Regular dogfood against a copied book:** back up `data/app/app.db` and the copied book before every app upgrade, migration, or host maintenance window.
- **Experimental controlled-write testing:** back up before every test session and keep the app-created pre-write backups under `data/backups/` until restore has been tested.

For real personal accounting data, also maintain your normal GnuCash/Desktop backup routine outside this project.

## Manual backup procedure

Stop the stack first for the simplest consistent file copy:

```bash
docker compose down
BACKUP_TS="$(date +%F-%H%M%S)"
BACKUP_DIR="../gnucash-web-companion-backups/$BACKUP_TS"
mkdir -p "$BACKUP_DIR"
```

Back up app metadata:

```bash
cp -a data/app "$BACKUP_DIR/app"
```

Back up copied GnuCash books:

```bash
cp -a data/books "$BACKUP_DIR/books"
```

Back up controlled-write backup copies if they exist:

```bash
cp -a data/backups "$BACKUP_DIR/backups"
```

Record non-secret operational context:

```bash
{
  git rev-parse HEAD
  docker compose config --services
} > "$BACKUP_DIR/manifest.txt"
```

Do not copy `.env` into shared bug reports. If you keep a private encrypted backup of `.env`, treat it as a secret backup and store it separately from public artifacts.

## Online backup notes

For local pre-alpha use, prefer stopping containers before copying SQLite files. If you need online backups later, use database-aware tooling and verify the result before trusting it. Do not assume that copying a live SQLite file is always consistent.

## Restore dry-run procedure

Run restore dry-runs into a separate disposable directory first. Do not overwrite your only working copy until the dry-run has been verified.

Example dry-run workspace:

```bash
mkdir -p /tmp/gnucash-web-restore-dry-run
cp -a "$BACKUP_DIR/app" /tmp/gnucash-web-restore-dry-run/app
cp -a "$BACKUP_DIR/books" /tmp/gnucash-web-restore-dry-run/books
cp -a "$BACKUP_DIR/backups" /tmp/gnucash-web-restore-dry-run/backups 2>/dev/null || true
```

Basic file checks:

```bash
test -f /tmp/gnucash-web-restore-dry-run/app/app.db
test -n "$(find /tmp/gnucash-web-restore-dry-run/books -name '*.gnucash.sqlite' -print -quit)"
```

If the app metadata DB is SQLite, verify it opens:

```bash
sqlite3 /tmp/gnucash-web-restore-dry-run/app/app.db 'PRAGMA integrity_check;'
```

Expected output:

```text
ok
```

For each copied GnuCash SQLite book, run a SQLite integrity check:

```bash
sqlite3 /tmp/gnucash-web-restore-dry-run/books/main.gnucash.sqlite 'PRAGMA integrity_check;'
```

This does not prove semantic GnuCash compatibility, but it catches obvious SQLite corruption.

## Manual recovery procedure

Only recover over a stopped deployment:

```bash
docker compose down
```

Move the current data directory aside instead of deleting it:

```bash
mv data "data.before-restore-$(date +%F-%H%M%S)"
mkdir -p data
```

Restore from a verified backup:

```bash
cp -a "$BACKUP_DIR/app" data/app
cp -a "$BACKUP_DIR/books" data/books
cp -a "$BACKUP_DIR/backups" data/backups 2>/dev/null || mkdir -p data/backups
mkdir -p data/locks
```

Confirm writes remain disabled before starting:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
docker compose config | grep -E 'GNUCASH_WRITES_ENABLED: "?false"?'
```

Start the stack:

```bash
docker compose up --build
```

## Verify the restored book can be read

After the stack starts, use the read-only smoke script against the restored deployment:

```bash
SMOKE_ADMIN_PASSWORD='<local-admin-password>' scripts/smoke/read-only-api-smoke.py
```

The smoke script checks health, login, `/auth/me`, book discovery, accounts, transactions, reports summary, and disabled-write 403 responses.

Manual UI verification:

- log in;
- open Dashboard;
- open Accounts;
- open an account detail page;
- open Transactions;
- open a transaction detail page;
- confirm the read-only banner/warnings are visible;
- confirm write UI is hidden while `GNUCASH_WRITES_ENABLED=false`.

If any restored book fails to open, stop the stack and keep both the failed restore directory and the prior `data.before-restore-*` directory for analysis. Do not keep retrying against the authoritative original.

## Controlled-write pre-write backups

Controlled writes are experimental post-MVP code and disabled by default. When deliberately enabled for disposable testing, the write path is expected to create a per-book backup before a routed write operation mutates a GnuCash book.

Current release-support expectation after the Phase 220 no-release blocker and its Phase 222–226 remediation: write-alpha evidence is release-useful only when each successful synthetic/disposable create, PATCH, or DELETE run has matching redacted audit evidence and a readable pre-write backup artifact. The resolved blocker was narrow: rapid same-named synthetic route-family backups could collapse evidence through timestamp collisions. The fix and follow-up dogfood remediate that synthetic evidence gap only; they do not make write-alpha production-ready, security-audited, or safe for real/private or only-copy books.

Keep the boundary explicit when preparing release notes or operator handoffs: `GNUCASH_WRITES_ENABLED=false` remains the default, and explicit write-alpha execution remains limited to `APP_ENV=test` with disposable or copied test books.

Operational expectations for write-mode testing:

- verify `data/backups/<book_id>/` exists or can be created;
- verify a backup file appears before trusting a write test;
- keep backups after the test until restore has been verified;
- restore by stopping the app and copying the selected backup file over the copied test book;
- re-run read-only smoke verification after restore;
- never treat these backups as a complete production backup system.

There is no general restore UI or restore API in the read-only MVP.

## Stopped-runtime cleanup for root-owned ignored artifacts

Disposable Docker dogfood can leave root-owned ignored runtime files under `data/books/`, `data/app/`, `data/backups/`, or `data/locks/`. Clean these only after the runtime is stopped:

```bash
docker compose down
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
```

The default command is a dry-run. It prints only path classes, counts, and statuses; it must not print raw file paths, book names, account names, transaction descriptions, memos, amounts, backup filenames, app DB rows, `.env`, or secrets.

To remove eligible ignored runtime artifacts after reviewing the dry-run:

```bash
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute
```

If host-side permissions cannot inspect root-owned artifacts, run the same helper through the API container with the repository mounted:

```bash
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --via-compose
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --via-compose --execute
```

Safety boundaries:

- the acknowledgement means you already stopped the runtime; the helper refuses to work without it;
- only the ignored runtime classes `books`, `app`, `backups`, and `locks` are in scope;
- active flock-held lock files are preserved and reported as active;
- stale lock files and unreadable lock files are removable only within the allowed ignored `data/locks/` class after stopped-runtime acknowledgement;
- unsupported lock-directory children are skipped;
- never point this at source books, backup sources outside this repo's ignored runtime data, or private directories.

## What is not guaranteed

This project does not currently guarantee:

- production-grade disaster recovery;
- encrypted or off-site backups;
- automated retention/rotation;
- point-in-time recovery;
- backup consistency for live file copies;
- compatibility with every GnuCash version or SQL backend;
- safe write-mode operation on real accounting books;
- recovery from corrupted authoritative GnuCash files;
- legal, tax, or audit compliance.

## Operator checklist

- [ ] Original authoritative GnuCash book is outside this repository.
- [ ] Deployment uses a copied/disposable book first.
- [ ] `.env` and secrets are not committed or attached to public reports.
- [ ] `GNUCASH_WRITES_ENABLED=false` is set for read-only MVP operation.
- [ ] `data/app/app.db` backup exists if local users/book registry matter.
- [ ] `data/books/` backup exists for copied/test books.
- [ ] `data/backups/` is preserved if controlled-write testing was performed.
- [ ] Restore dry-run succeeded before any destructive recovery.
- [ ] Restored app passed read-only smoke verification.
- [ ] Any failure report excludes real book files, real screenshots, real CSV exports, secrets, and account/transaction details.
