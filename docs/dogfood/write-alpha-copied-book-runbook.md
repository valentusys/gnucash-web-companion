# Write-alpha copied-book dogfood runbook

Status: executable design only. Phase 173 did not perform any real write.

This runbook is for one local-only write-alpha dogfood session against a copied/disposable GnuCash SQL book. It is not a production procedure and must not be used on a real/private/only-copy authoritative book.

## Hard stop conditions

Stop immediately if any item is true:

- The candidate book is the only copy of a real/private book.
- The candidate book is inside this git checkout before the runtime-copy step.
- The source provenance is unclear, or no independent backup exists outside this repository.
- The intended runtime target is not under ignored `data/books/`.
- The intended app DB is not under ignored `data/app/`.
- The intended backup directory is not under ignored `data/backups/`.
- `APP_ENV` would be anything other than `test` while writes are enabled.
- `GNUCASH_WRITES_ENABLED=true` would be committed, added to `.env.example`, or treated as a default.
- GnuCash Desktop is open on the same runtime copy while the web app is running.
- Any log/evidence would expose private absolute paths, account names, transaction descriptions, memos, amounts, screenshots, CSV exports, app DBs, book files, backups, cookies, tokens, or `.env` values.

## Safe path model

Use three distinct locations:

1. Source copied/disposable book outside git, for example an operator-owned path under `/tmp` or another local scratch area.
2. Runtime copy under ignored `data/books/write-alpha-dogfood.gnucash.sqlite`.
3. Pre-write backups under ignored `data/backups/write-alpha-dogfood/`.

The repository `.gitignore` must continue to cover `data/books/*.sqlite`, `data/books/*.sqlite3`, `data/books/*.db`, `data/app/*`, and `data/backups/*` before any dogfood run.

## 0. Confirm defaults are still read-only

From the repository root:

```bash
grep -n 'GNUCASH_WRITES_ENABLED=false' .env.example
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
```

Expected: default Compose config renders writes disabled. If not, stop.

## 1. Preflight the source without leaking private details

Set the source path only in the local shell. Do not commit it and do not paste it into docs/issues.

```bash
export WRITE_ALPHA_SOURCE_BOOK='/outside-git/disposable-copy.gnucash.sqlite'
python apps/api/scripts/check_dogfood_book_candidate.py \
  --write-alpha-plan \
  --confirm-disposable-copy \
  "$WRITE_ALPHA_SOURCE_BOOK"
```

Expected output is a redacted one-line summary with only the filename, path classes, and size. It must not include the absolute source directory, account names, descriptions, memos, or amounts.

The command is preflight-only: it does not open, parse, copy, or mutate the book.

## 2. Prepare ignored runtime data

Use a fresh runtime copy and a fresh local app DB for this dogfood session.

```bash
docker compose down --remove-orphans
mkdir -p data/books data/app data/backups/write-alpha-dogfood data/locks
rm -f data/books/write-alpha-dogfood.gnucash.sqlite
rm -f data/app/app.db
cp "$WRITE_ALPHA_SOURCE_BOOK" data/books/write-alpha-dogfood.gnucash.sqlite
chmod 0640 data/books/write-alpha-dogfood.gnucash.sqlite
```

Do not run this step unless Phase 1 preflight passed and the source is disposable. The copied file remains runtime data and must stay untracked.

## 3. Create a local-only write-alpha environment

Use local dummy credentials/secrets only. Do not commit `.env`.

```dotenv
APP_ENV=test
JWT_SECRET=<local random 32+ byte value>
APP_ADMIN_USERNAME=admin
APP_ADMIN_PASSWORD=<local dogfood password>
GNUCASH_DEFAULT_BOOK_PATH=/data/books/write-alpha-dogfood.gnucash.sqlite
GNUCASH_WRITES_ENABLED=true
ORIGIN=http://localhost:8080
```

Generate a local JWT secret if needed:

```bash
openssl rand -hex 32
```

This is the only place `GNUCASH_WRITES_ENABLED=true` is allowed in this runbook, and only with `APP_ENV=test` against the disposable runtime copy.

## 4. Backup-before-write check

Before starting the app, create an operator backup outside git and verify app backup storage exists:

```bash
mkdir -p /tmp/gnucash-web-companion-write-alpha-backups
cp data/books/write-alpha-dogfood.gnucash.sqlite \
  /tmp/gnucash-web-companion-write-alpha-backups/pre-run-copy.gnucash.sqlite
test -f /tmp/gnucash-web-companion-write-alpha-backups/pre-run-copy.gnucash.sqlite
test -d data/backups/write-alpha-dogfood
```

During the actual write route, the application is also expected to create a pre-write backup under `data/backups/<book_id>/` before mutation. If no backup appears for the write attempt, treat the dogfood as failed and use the restore plan below.

## 5. Start local runtime explicitly in test write mode

```bash
docker compose up --build
```

Open only the local app origin. Do not expose this write-alpha run to LAN/public internet.

## 6. Minimal transaction dogfood shape

Perform exactly one minimal balanced create transaction through the existing write-alpha UI/API path.

Use only non-sensitive dummy values in any evidence notes. Do not paste account names or amounts into committed docs. The transaction itself may use existing disposable-book accounts, but evidence should say only:

- create route used;
- one two-split balanced transaction attempted;
- validation result/status code;
- backup present before mutation;
- audit row present;
- write lock released;
- read-back succeeded or failed.

Do not test PATCH/DELETE in this phase design. Do not expand write CRUD.

## 7. GnuCash Desktop verification path

After the web write attempt:

1. Stop the app first:

   ```bash
   docker compose down
   ```

2. Open a separate copy of the mutated runtime book with GnuCash Desktop, not the same file while Docker is running:

   ```bash
   cp data/books/write-alpha-dogfood.gnucash.sqlite /tmp/gnucash-web-companion-write-alpha-backups/desktop-open-copy.gnucash.sqlite
   # Open /tmp/.../desktop-open-copy.gnucash.sqlite manually in GnuCash Desktop.
   ```

3. Record only redacted status: Desktop version if available, open succeeded/failed, and whether the app-created transaction is visible in the disposable copy. Do not commit screenshots or data exports.

If GnuCash Desktop tooling is unavailable, record `BLOCKED — Desktop tooling unavailable` and do not claim compatibility.

## 8. Restore plan

To restore pre-run state for the disposable runtime copy:

```bash
docker compose down
cp /tmp/gnucash-web-companion-write-alpha-backups/pre-run-copy.gnucash.sqlite \
  data/books/write-alpha-dogfood.gnucash.sqlite
rm -f data/locks/*.lock
```

Then restart with writes disabled and run read-only checks:

```bash
# In .env or shell override:
# GNUCASH_WRITES_ENABLED=false
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
docker compose up -d --build
python scripts/smoke/read-only-api-smoke.py --base-url http://localhost:8080 --username admin --password '<local dogfood password>'
docker compose down
```

If the app-created pre-write backup is used instead, restore only the backup belonging to the affected disposable `book_id` and write attempt. Never restore over a real/private/only-copy book.

## 9. Teardown and no-artifact checks

After dogfood, stop containers and remove runtime artifacts unless they are being kept locally for immediate redacted analysis:

```bash
docker compose down --remove-orphans
rm -f data/books/write-alpha-dogfood.gnucash.sqlite
rm -f data/app/app.db
rm -rf data/backups/write-alpha-dogfood
rm -f data/locks/*.lock
git status --short
git diff --cached --name-only
```

Expected: no book, backup, app DB, `.env`, screenshot, CSV export, token, key, cert, or private data artifact is staged. `.hermes/` may remain untracked and must not be staged.

## Evidence template

Use this redacted template only:

```text
commit=<sha>
source_preflight=<redacted helper summary, no absolute path>
runtime=data/books ignored runtime copy
app_env=test
writes_enabled=explicit local-only true
operation=one balanced two-split create
backup_before_write=present|missing
lock_released=yes|no
audit=present|missing
api_readback=pass|fail
desktop_open=pass|blocked|fail, version=<redacted/non-sensitive>
restore=pass|fail
no_artifacts_staged=pass|fail
```

Do not include private paths, account names, transaction descriptions, memos, amounts, screenshots, CSV exports, app DBs, book files, backups, cookies, tokens, or `.env` values.
