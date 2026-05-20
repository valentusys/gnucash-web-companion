# Copied-book write-alpha dogfood runbook

Status: conservative maintainer runbook v1 for future local-only dogfood.

This runbook documents a safe procedure shape for future copied-book write-alpha dogfood. Phase 234 does not run copied-book dogfood and does not prove that write-alpha is safe for real/private books or only copies.

## Hard safety boundary

Never use:

- the original GnuCash book;
- the only existing copy of a book;
- a book stored inside the git checkout;
- a production, shared, or public-internet deployment;
- a book whose contents or paths would need to be committed as evidence.

Only use a copied/disposable book that can be deleted or restored from an independent backup. GnuCash Desktop remains the authoritative editor. Write-alpha remains experimental, pre-alpha, disabled by default, and not production-ready or security-audited.

## Preconditions

Before any mutation attempt, confirm all of the following:

1. The original book is closed and will not be mounted or opened by this app.
2. A copied/disposable working book exists outside the repository, for example under a local temporary/operator directory that is not tracked by git.
3. A separate pre-mutation backup exists outside the repository and outside the app runtime backup directory.
4. Docker Compose will be bound to local-only addresses such as `127.0.0.1`; do not expose the write-alpha stack to a LAN, VPN, or the public internet.
5. The runtime is explicitly configured with both gates:
   - `GNUCASH_WRITES_ENABLED=true`
   - `APP_ENV=test`
6. `.env.example`, committed docs, and default Docker configuration still keep `GNUCASH_WRITES_ENABLED=false` as the safe default.
7. Evidence collection can be redacted before anything is committed.

If any precondition fails, stop before starting the stack.

## Prepare the copied/disposable book

1. Choose the source book only long enough to make an external copy.
2. Copy it to an outside-git working location.
3. Make an independent backup of that working copy before running this app.
4. Confirm the app will receive only the copied/disposable path, never the original path.
5. Record only redacted labels in notes, for example `<copied-book-path>` and `<external-backup-path>`.

Do not paste raw private paths, account names, memos, amounts, CSV rows, screenshots, or book contents into committed files, issue comments, chat reports, or release notes.

## Start local-only write-alpha

Use local-only dummy/operator secrets and explicit write-alpha gates. Example shape:

```bash
APP_ENV=test \
GNUCASH_WRITES_ENABLED=true \
JWT_SECRET=<dummy-local-secret> \
APP_ADMIN_PASSWORD=<dummy-local-password> \
docker compose up -d
```

The exact book mount/path should point to the outside-git copied/disposable book. Keep any `.env` file untracked and local-only. Do not change committed defaults to make writes easier to enable.

After startup, verify the rendered/runtime posture before mutation:

```bash
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
```

Confirm locally that the API reports write-alpha enabled only for this test run and that `APP_ENV=test` is active. If the app is not in `APP_ENV=test`, stop immediately.

## Mutation rule: one at a time

Run at most one mutation per dogfood step:

1. prefer a no-mutation readiness/preflight step first;
2. perform one CREATE only if the copied/disposable target, backup, and gates are confirmed;
3. verify read-back, audit row, backup artifact, and lock release;
4. decide whether to stop before considering any PATCH;
5. do not DELETE unless a later phase/runbook explicitly authorizes DELETE against a transaction created by the write-alpha test itself.

Never mix CREATE, PATCH, and DELETE in an unreviewed batch. Never mutate historical/manual transactions from the source book.

## Stop conditions

Stop immediately and keep the copied working book isolated if any of these occur:

- the original or only-copy book path is about to be used;
- the working copy is inside the git repository;
- `APP_ENV=test` is absent or false;
- `GNUCASH_WRITES_ENABLED=true` appears in committed defaults or an unreviewed persistent config;
- Docker is exposed beyond local-only access;
- a pre-mutation backup is missing or unreadable;
- audit, backup, lock, or restore evidence is missing or inconsistent;
- a write returns an unexpected success/failure status;
- redaction would require committing raw private paths, account names, memos, amounts, screenshots, CSV, app DB, backups, or book files.

On stop, do not continue to another mutation. Preserve local-only evidence for investigation, redact summaries, and restore/reset before any later attempt.

## Evidence and redaction

Committed evidence may include only bounded, redacted facts:

- phase/scenario name;
- synthetic or copied/disposable classification;
- command names without raw private arguments;
- pass/fail status;
- opaque backup/audit/lock references;
- counts such as backup count or audit row count;
- restore proof status;
- disabled-reset status.

Committed evidence must not include:

- real/private GnuCash files or copied books;
- app DBs, runtime backups, lock files, screenshots, CSV exports, `.env` files;
- tokens, keys, certs, passwords, raw JWTs;
- raw private paths;
- account names/descriptions, transaction descriptions, split memos, amounts, balances, CSV rows, or request payloads.

Use placeholders such as `<copied-book-path>`, `<external-backup-path>`, `<opaque-backup-ref>`, and `<redacted-command>`.

## Restore procedure

After the one mutation step, verify restore before claiming the run is usable evidence:

1. Stop the app stack.
2. Keep the mutated working copy isolated outside git.
3. Restore the copied/disposable working book from the independent pre-mutation backup.
4. Verify the restored copy can be opened/read by the intended read-only path.
5. Verify the mutation is absent from the restored copy when that is the expected restore result.
6. Record only redacted restore status and counts.

Do not replace or alter the original book during restore. The original book must remain untouched for the whole run.

## Return to the default read-only posture

Every write-alpha dogfood attempt must end by resetting and proving the default disabled posture:

1. Stop Docker Compose and remove local runtime containers/volumes as appropriate for the test run.
2. Remove or revert any local-only `.env` values that set `GNUCASH_WRITES_ENABLED=true`.
3. Restart or render config with the default posture and verify `GNUCASH_WRITES_ENABLED=false`.
4. Run disabled-write probes where available; validate/create/PATCH/DELETE should return 403 when writes are disabled.
5. Confirm no tracked file changed to enable writes by default.

Example reset verification shape:

```bash
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
python3 scripts/check_public_status.py
git diff --check
git status --short
```

Only commit redacted documentation or summaries. Never commit the copied book, backup, app DB, `.env`, CSV, screenshot, token, key, cert, or private financial data.
