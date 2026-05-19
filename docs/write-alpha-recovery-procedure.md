# Write-alpha recovery procedure

Status: experimental / pre-alpha. This procedure exists for maintainer review of the disabled-by-default write-alpha path. It is not a production disaster-recovery guarantee and must not be used to justify enabling writes against the only copy of a real GnuCash book.

## Safety boundary

Write-alpha execution is intentionally limited to all of the following:

- `GNUCASH_WRITES_ENABLED=true` explicitly set by the operator;
- `APP_ENV=test` route gate still active;
- copied, synthetic, or otherwise disposable GnuCash SQL books only;
- pre-write backup, per-book lock, validation where applicable, audit, and unlock lifecycle;
- no tag/release/publication claim that write mode is safe for real books.

Keep the repository default at:

```text
GNUCASH_WRITES_ENABLED=false
```

Do not use this procedure on the only copy of a GnuCash book. For real user data, first create an out-of-repository copy and verify independent backups with GnuCash Desktop.

## Inputs to collect without leaking private data

For a failed write-alpha attempt, collect only non-sensitive operational facts:

- app version or commit SHA;
- exact route family, for example `POST /books/{book_id}/transactions`, `PATCH /books/{book_id}/transactions/{transaction_id}`, or `DELETE /books/{book_id}/transactions/{transaction_id}`;
- HTTP status and non-sensitive error code/message;
- UTC timestamp of the attempt;
- anonymized book id, not a filesystem path;
- whether a backup path was recorded in the audit row;
- whether a `.lock` file remains for the book id;
- whether the disposable book opens read-only after the failure.

Do not paste real account names, transaction descriptions, memos, amounts, file paths, SQL dumps, screenshots, CSV exports, cookies, tokens, `.env`, database files, or backup binaries into issues or docs.

## Immediate containment

1. Stop the app before inspecting or restoring a failed disposable write-alpha run:

   ```bash
   docker compose down
   ```

2. Keep write mode disabled before restarting anything:

   ```bash
   grep -E '^GNUCASH_WRITES_ENABLED=' .env || true
   # Expected safe value:
   # GNUCASH_WRITES_ENABLED=false
   ```

3. Verify Compose renders writes as disabled:

   ```bash
   JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -E 'GNUCASH_WRITES_ENABLED: "?false"?'
   ```

4. Do not run GnuCash Desktop and the web app against the same writable book at the same time. GnuCash Desktop remains the authoritative editor.

## Find the pre-write backup

The backup service stores pre-write backups under the configured backups root, normally:

```text
data/backups/<book_id>/
```

List backups for the affected disposable book id, newest first:

```bash
find data/backups/<book_id> -maxdepth 1 -type f -printf '%T@ %p\n' | sort -nr | head -20
```

If the failed audit row recorded a backup path, prefer that exact backup file. If no backup was recorded, use the newest backup before the failed attempt timestamp only if it clearly belongs to the same disposable book id and write attempt.

Never commit backup files. `data/backups/*` must remain ignored runtime data.

## Check for a stale write lock

A stale lock can remain only after abnormal process termination. Inspect it while the app is stopped:

```bash
find data/locks -maxdepth 1 -type f -name '*.lock' -printf '%p %s bytes\n' 2>/dev/null || true
```

If the app is stopped and the affected disposable book still has a lock file, remove only that book-specific lock file:

```bash
rm -f data/locks/<book_id>.lock
```

Do not remove all lock files while the app is running. Do not weaken or bypass `WriteLockService`; stale-lock cleanup is an operator recovery action after the process has stopped.

## Restore a disposable book from backup

Use this only on copied/synthetic/disposable books.

1. Save the current damaged candidate for later local inspection outside git:

   ```bash
   mkdir -p /tmp/gnucash-web-companion-recovery
   cp data/books/<book-file>.gnucash.sqlite /tmp/gnucash-web-companion-recovery/damaged-$(date -u +%Y%m%dT%H%M%SZ).gnucash.sqlite
   ```

2. Restore the selected pre-write backup over the disposable book path:

   ```bash
   cp data/backups/<book_id>/<backup-file>.gnucash.sqlite data/books/<book-file>.gnucash.sqlite
   ```

3. Keep permissions readable by the app container/user:

   ```bash
   chmod 0640 data/books/<book-file>.gnucash.sqlite
   ```

4. Restart with writes disabled:

   ```bash
   docker compose up -d --build
   ```

## Integrity checks after restore

Run read-only checks first. Do not re-enable writes as a recovery test.

1. Verify API health:

   ```bash
   curl -fsS http://localhost:8080/api/health
   ```

2. Log in through the UI and browse read-only pages: dashboard, accounts, transactions, and the affected transaction detail if known.

   If the failed action was a DELETE that intentionally removed the affected transaction, verify instead that the transaction list loads read-only and that the deleted transaction id is absent from the disposable restored/regenerated state you expect.

3. If local backend tooling is available, run the automated suite from the repository root:

   ```bash
   cd apps/api && pytest -q
   cd ../web && npm run check
   cd ../web && npm run build
   ```

4. Open a copy of the restored disposable book with GnuCash Desktop if available. Do not open the same file while the web app is using it.

## Damaged-book triage

If a disposable book still appears damaged after restore:

1. Keep the damaged candidate under `/tmp` or another ignored local directory only.
2. Do not commit the damaged book, backup, app DB, logs with private paths, screenshots, SQL dumps, or exports.
3. Reproduce on a synthetic fixture under `tmp_path` or another disposable copy.
4. File or update an issue with redacted facts only: route, status code, non-sensitive error, commit SHA, whether backup/lock/audit were present, and whether read-only open succeeded.
5. Keep `GNUCASH_WRITES_ENABLED=false` for normal operation until a maintainer review explicitly clears the issue for further synthetic-only testing.

## Recovery acceptance criteria

A recovery attempt is considered complete only when all are true:

- the app is back to `GNUCASH_WRITES_ENABLED=false`;
- no stale lock exists for the affected disposable book while the app is stopped;
- a known pre-write backup was restored or the disposable fixture was regenerated;
- the restored/regenerated book opens through read-only app routes;
- no private/runtime artifacts were added to git;
- the incident notes explicitly say whether the evidence is synthetic/disposable only.
