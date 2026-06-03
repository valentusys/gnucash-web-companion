# Daytime Write Worker 8 — #36-W1-B backup manifest linkage

## Worker ID

daytime-write-worker-8

## Target issue

#36 — controlled-write v0.2 readiness gates

## Package

#36-W1-B — Backup manifest linkage.

## Goal

Strengthen non-mutating regression coverage proving owner-writebeta sessions preserve only opaque operation/backup/audit/restore refs and reject raw/path-like evidence refs before summaries can expose them.

## Scope completed

Added `apps/api/tests/test_owner_writebeta_backup_manifest_linkage.py` with 7 synthetic state-machine tests:

- successful post-mutation verification summary links `operation_ref`, `backup_ref`, `audit_ref`, and `restore_ref`;
- successful reset-required summaries clear active arms (`preview_hash`, `confirmation_token_ref`, `restore_readiness_ref`);
- summaries do not contain payload field names/values, paths, `.gnucash`, sqlite names, descriptions, memos, or amounts;
- failed post-mutation verification preserves pre-mutation operation/backup refs but does not record audit/restore refs from the failed verification attempt;
- path-like, URL-like, backslash-bearing, or whitespace-bearing backup/restore-readiness/audit/restore refs are rejected as non-opaque.

No production code changed.

## Verification

From `apps/api`:

```text
python -m pytest -q tests/test_owner_writebeta_backup_manifest_linkage.py --tb=short
7 passed in 0.04s
```

Related owner-writebeta suite:

```text
python -m pytest -q \
  tests/test_owner_writebeta_backup_manifest_linkage.py \
  tests/test_owner_writebeta_state_machine.py \
  tests/test_owner_writebeta_routes.py \
  tests/test_owner_writebeta_route_guard_fail_closed.py --tb=short
51 passed, 1 warning in 11.86s
```

Repository check:

```text
git diff --check
# clean
```

## Safety notes

- No original/private/working/only-copy GnuCash book was touched.
- Tests use synthetic in-memory state-machine sessions only.
- No GnuCash book, SQLite book, backup, export, screenshot, `.env`, token, key, private path, account name, transaction description, memo, amount, or raw private evidence was added.
- `GNUCASH_WRITES_ENABLED=false` default remains unchanged.
- `APP_ENV=test` gate remains unchanged.
- No public write beta and no release.

## Issue #36 comment draft

> daytime-write-worker-8 (#36-W1-B): Added backup/audit/restore manifest-linkage regression tests for owner-writebeta. Successful synthetic post-mutation summaries now prove operation/backup/audit/restore refs are all linked as opaque refs while active arms are cleared; failed post-mutation attempts preserve pre-mutation operation/backup refs but do not record failed audit/restore refs; path-like/URL-like/whitespace-bearing evidence refs are rejected before summaries can expose them. Verification: new test 7 passed; related owner-writebeta suite 51 passed; `git diff --check` clean. No production code change, no book mutation, no private evidence, writes remain default-disabled.

## Blockers

None for this package.
