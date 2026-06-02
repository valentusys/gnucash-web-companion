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

## Maintainer review packet before any future write milestone

This packet is a human review gate, not an execution approval. It separates accepted non-mutating readiness evidence from future mutation evidence that still needs same-context owner and PM authorization.

Before any maintainer considers a copied-book/write milestone, record all checkpoints below in the milestone handoff or issue comment:

- Reviewer and decision owner: maintainer name plus PM/owner decision reference.
- Exact commit SHA and route family under review.
- Exact fixture scope: synthetic/disposable or copied/restorable only; never original/private/working/only-copy.
- Desktop posture: GnuCash Desktop closed for the target copy before the web app can open it writable.
- Default posture proof: `GNUCASH_WRITES_ENABLED=false` before and after the milestone plus an `APP_ENV=test` gate statement for any enabled write-alpha route.
- Non-mutating evidence accepted so far: checklist, guard, handoff, or CI links only; no raw private data.
- Future mutation evidence requested: route family, operation counts, preflight, backup, read-back, audit, lock, rollback/restore, reset/default-disabled probe, and redaction expectations.
- Explicit keep-open posture for issue #36 unless maintainer/PM review accepts every remaining blocker and states the original issue scope is satisfied.
- Explicit no-release posture: no public write beta, stable, production, security-audited, v0.2-ready, tag, package, image, or release claim.

If any checkpoint is missing, stop at documentation review. Mark the exact item blocked and keep writes disabled.

## Evidence required before future copied-book/write milestones

Non-mutating evidence may satisfy only documentation, guard, and review readiness. It must not be treated as proof that writes are safe for a copied or real book.

Accepted non-mutating evidence can include:

- passing static guards such as `scripts/check_write_safety_defaults.py`, `scripts/check_public_status.py`, and `scripts/check_tracked_hygiene.py`;
- synthetic/unit tests that do not open, copy, or mutate GnuCash books;
- redacted handoffs and docs that preserve `GNUCASH_WRITES_ENABLED=false`, `APP_ENV=test`, no-release, and #36 keep-open posture.

Future copied/restorable mutation evidence, only after exact same-context authorization, must include all of the following before the milestone can be reviewed:

- copied/restorable fixture provenance outside git and outside original/private/working/only-copy data;
- operator confirmation that GnuCash Desktop is closed for the copied target;
- preflight showing the target is a disposable copy and write mode is still disabled before arming;
- explicit arming/route family/count scope for CREATE, PATCH, or DELETE;
- pre-write backup path recorded in audit without publishing private paths;
- per-book lock acquisition and contention/rejection evidence;
- post-write read-back through read-only app routes;
- audit rows for success and for any routed failure after write-route entry, with non-sensitive metadata only;
- rollback or restore verification evidence: selected backup, restore hash/checksum marker, bounded row-count marker, schema marker, and read-only reopen result;
- reset/default-disabled probe proving CREATE/PATCH/DELETE are blocked again after reset;
- redaction review proving no book, app DB, backup, CSV/export, screenshot, private path, account name, transaction description, memo, amount, `.env`, token, key, cert, or raw private evidence is committed or posted.

Missing future mutation evidence is a blocker. Do not substitute existing non-mutating evidence for it.

## Hard-stop and recovery decision tree

Use this decision tree for failed or incomplete copied/synthetic write-alpha attempts:

1. Did a restore, read-back, or audit expectation fail?
   - Yes: hard stop. Preserve the pre-write backup and damaged disposable candidate outside git, keep writes disabled, do not retry on the same copy, and escalate to maintainer/owner review with redacted facts only.
   - No: continue to the next decision.
2. Is the backup missing, ambiguous, not tied to the route attempt, or not restorable?
   - Yes: hard stop. Do not perform another write. Regenerate a disposable fixture or wait for maintainer/owner review.
   - No: continue to restore/read-back checks below.
3. Is a lock active or unreadable?
   - Active: stop the app or wait for the active writer; do not remove lock files blindly.
   - Unreadable: inspect from the container or fix runtime ownership; do not assume stale status.
   - Stale released with app stopped: remove only the affected book-specific stale lock from ignored runtime storage if needed.
4. Did the restored/regenerated book open through read-only app routes and, if available, a separate GnuCash Desktop copy check?
   - No: hard stop and preserve evidence outside git.
   - Yes: record rollback/read-back/audit evidence, reset to disabled, and proceed only to maintainer review.
5. Did reset/default-disabled probes return to `GNUCASH_WRITES_ENABLED=false` with write routes blocked?
   - No: hard stop; do not claim readiness.
   - Yes: mark the copied/synthetic attempt recovered for review only. This still does not authorize public write beta or real-book writes.

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

## Check for active vs stale write locks

A `.lock` file can remain after a released `flock`. The file by itself is not proof that a write is still active. Inspect it without printing paths or private book details:

```bash
python - <<'PY'
from pathlib import Path
from app.services.write_lock import WriteLockService
book_id = '<redacted-book-id-or-runtime-book-key>'
result = WriteLockService(Path('data/locks')).inspect(book_id)
print(f'status={result.status} active={result.is_active}')
print(result.operator_message)
PY
```

Interpretation:

- `active` means a writer still holds the flock. Do not remove the lock file; wait for the active write to finish or stop the runtime cleanly.
- `stale_released` means a lock file remains but no active flock was detected. With the app stopped, an operator may remove only the affected book-specific stale lock from ignored runtime storage.
- `unreadable` means the current user cannot inspect the file, which can happen after Docker creates root-owned runtime files. Inspect from the API container or fix runtime ownership first; do not assume active vs stale from the host error alone.
- `not_present` means there is no lock file for that book.

If the smoke helper reports `status=stale_released`, treat it as released-lock evidence, not as active contention. If it reports unreadable, do not rerun a write blindly; inspect from the API container and continue recovery with redacted evidence.

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
