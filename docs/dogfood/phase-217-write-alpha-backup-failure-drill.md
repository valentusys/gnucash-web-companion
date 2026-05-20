# Phase 217 dogfood — write-alpha backup-failure and no-mutation drill

Date: 2026-05-21

## Scope

This evidence covers synthetic/disposable write-alpha failure paths only. It does not add write scope and does not claim production, security-audited, real/private-book, or only-copy-book write safety.

Write-enabled coverage was limited to pytest fixtures that copy the committed synthetic GnuCash fixture into temporary ignored/disposable runtime paths and run with explicit test settings equivalent to `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`.

## Evidence collected

### Backup creation unavailable/failure before mutation

Targeted backend route tests inject path-like backup failures for all write-alpha route families:

- create: `TestWriteAlphaCreateRouteDisposableFixture::test_create_backup_failure_fails_before_mutation_audits_and_releases_lock`
- PATCH: `TestWriteAlphaPatchRouteDisposableFixture::test_patch_backup_failure_fails_before_mutation_audits_and_releases_lock`
- DELETE: `TestWriteAlphaDeleteRouteDisposableFixture::test_delete_backup_failure_fails_before_mutation_audits_and_releases_lock`

Assertions:

- request returns a safe `422` response;
- response/audit error text is generic and does not expose the injected path-like backup destination;
- `backup_path` remains `null` in failed audit payloads because no backup was created;
- the book is not opened for write after backup failure;
- transaction state in the disposable synthetic fixture is unchanged;
- per-book write lock can be acquired immediately after the failed route, proving release.

### Post-backup injected failures

Existing route-family tests still cover post-backup injected failures:

- create: `test_failure_during_create_write_releases_lock_audits_failure_and_keeps_backup`
- PATCH: `test_failure_during_patch_write_releases_lock_audits_failure_and_keeps_backup`
- DELETE: `test_failure_during_delete_write_releases_lock_audits_failure_and_keeps_backup`

Assertions:

- failed audit rows are written;
- backup evidence is retained;
- backup copy reads back as the pre-write synthetic state;
- disposable runtime fixture is unchanged after the injected failure;
- lock can be reacquired after failure.

### Default-readonly reset

Existing default-disabled route tests still cover validate/create/PATCH/DELETE returning `403` before book resolution or write-service construction when `GNUCASH_WRITES_ENABLED=false`.

## Verification commands

Targeted drill:

```bash
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_create_backup_failure_fails_before_mutation_audits_and_releases_lock tests/test_transaction_writes.py::TestWriteAlphaPatchRouteDisposableFixture::test_patch_backup_failure_fails_before_mutation_audits_and_releases_lock tests/test_transaction_writes.py::TestWriteAlphaDeleteRouteDisposableFixture::test_delete_backup_failure_fails_before_mutation_audits_and_releases_lock -q
```

Result: passed (`3 passed`).

Full verification was run after docs/status updates; see `docs/handoff/phase-217.md` and final report.

## Safety notes

- No real/private GnuCash book was opened or copied.
- No app DB, backup artifact, `.env`, screenshot, export, token, key, cert, account name, memo, amount, or raw private path is committed here.
- Runtime defaults remain `GNUCASH_WRITES_ENABLED=false`.
- Write-alpha remains gated by `APP_ENV=test` when explicitly enabled.
