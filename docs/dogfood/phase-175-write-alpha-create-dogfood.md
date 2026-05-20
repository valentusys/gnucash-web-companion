# Phase 175 — write-alpha controlled create dogfood

Date: 2026-05-20
Status: COMPLETE — exactly one write-alpha create was executed on a disposable synthetic copy
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 4 only)

## Scope

This phase ran the first actual write-alpha create dogfood against a copied/disposable test fixture only. No private, real, or only-copy book was used.

The run used:

- source class: committed synthetic fixture copied to a temporary external path before preflight;
- preflight: Phase 174 dry-run preflight helper with disposable-copy acknowledgement;
- runtime copy class: ignored `data/books/` disposable copy;
- app DB class: ignored `data/app/` local runtime DB;
- backup class: ignored `data/backups/` local runtime backup;
- environment: `APP_ENV=test`;
- writes: explicit local-only `GNUCASH_WRITES_ENABLED=true` for the create run only.

## Redacted command/result evidence

Commands/results were recorded only as summaries. No account names, transaction description, memos, amounts, cookies, raw DB rows, book files, backup files, screenshots, CSV exports, tokens, or private paths are committed here.

```text
source_preflight=status=ready; book=<redacted.gnucash.sqlite>; reason=write-alpha copied-book preflight passed without copying or mutation; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; size_bytes=212992; sha256_12=c8f22b449c49; dry_run=true
default_config_before=GNUCASH_WRITES_ENABLED: "false"
runtime=ignored disposable copy under data/books
app_env=test
writes_enabled=explicit local-only true
operation=one balanced two-split create
validation_valid_payload=pass
validation_unbalanced_probe=reject
validation_invalid_account_probe=reject
validation_placeholder_style_probe=reject via invalid placeholder-probe account id; backend placeholder rejection remains covered by targeted tests
api_readonly_routes_during_write_run=health/books/accounts/read-back pass
api_create=201 created exactly once
audit=one transaction.create success row
backup_before_write=one backup file created by write route before mutation response
lock_released=pass; flock probe could reacquire the remaining lock file after write
runtime_stopped_after_create=pass
read_only_smoke_after_restore=pass with GNUCASH_WRITES_ENABLED default false; validate/create/patch/delete returned 403
teardown=runtime book/app DB/backups/locks removed from ignored data paths
no_artifacts_staged=pass
```

## Findings

- The create route successfully produced exactly one new transaction on the disposable runtime copy.
- The write route created one backup under ignored backup storage before returning the mutation result.
- The app metadata DB contained one successful `transaction.create` audit row for the dogfood run.
- The lock service leaves the lock file path behind after releasing `flock`; this is expected for the current file-lock implementation. A follow-up flock probe from inside the API container reacquired the file, confirming the lock was released.
- The initial smoke helper assumed release meant lock-file deletion. The helper was corrected to verify that any remaining lock file is not actively held instead of expecting zero lock files.
- No PATCH or DELETE write dogfood was run.
- No default config changed; Docker Compose without explicit override still renders `GNUCASH_WRITES_ENABLED: "false"`.

## Verification performed

```bash
python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy <temporary external synthetic copy>
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... docker compose up --build
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/write-alpha-create-smoke.py
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... docker compose exec -T api <redacted lock/audit/backup probe>
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... docker compose down --remove-orphans
APP_ENV=test ... docker compose up --build -d
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/read-only-api-smoke.py
APP_ENV=test ... docker compose down --remove-orphans
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git status --short -- data/books data/backups data/app data/locks
```

Results:

- Preflight passed with redacted source/runtime/backup classes and short checksum.
- Exactly one create dogfood succeeded on the disposable copy.
- Validation probes rejected unbalanced and invalid/placeholder-style cases; backend placeholder-account rejection remains pinned by targeted write tests.
- Read-only API smoke passed after restoring the disposable runtime copy with writes disabled by default.
- Ignored runtime data was removed after the run.
- Default Compose config remains write-disabled.

## Safety result

No real/private/only-copy book was used. No raw GnuCash book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data is committed. `GNUCASH_WRITES_ENABLED=false` remains the default.
