# Daytime write continuation worker 2 — #36-W2-B synthetic backup/restore drill

## PM scope lock

- Goal: prove synthetic backup/restore readiness and post-mutation verification behavior around owner-writebeta sessions.
- Scope: state-machine and in-memory route tests only; no real backup artifact and no GnuCash book access.
- Non-goals: copied-book dogfood, real backup restore execution, release claims.
- Safety checks: opaque refs only, path-like refs rejected before entering summaries, restore failure hard-stops and blocks further mutation.
- Acceptance criteria: successful synthetic mutation requires audit/restore refs plus lock release/default reset; restore/default failure blocks completion; path-like audit/restore refs are rejected even if the operation would otherwise hard-stop; summaries expose only opaque refs.
- Verification commands: `cd apps/api && python -m pytest -q tests/test_owner_writebeta_synthetic_backup_restore_drill.py tests/test_owner_writebeta_backup_manifest_linkage.py tests/test_owner_writebeta_synthetic_failure_drill.py --tb=short`.
- Mutation mode: synthetic/disposable only.

## Implementation

- Added `apps/api/tests/test_owner_writebeta_synthetic_backup_restore_drill.py`.
- Strengthened `mark_post_mutation_checks()` to validate provided `audit_ref` and `restore_ref` as opaque refs before entering the hard-stop branch. This keeps path-like restore/audit strings out of route responses even when `lock_released` or `defaults_reset` is false.

## Verification

- `cd apps/api && python -m pytest -q tests/test_owner_writebeta_synthetic_backup_restore_drill.py tests/test_owner_writebeta_backup_manifest_linkage.py tests/test_owner_writebeta_synthetic_failure_drill.py --tb=short` => 24 passed, 1 warning.

## Safety summary

- No private/original/working/only-copy GnuCash book was touched.
- No real backup, restore artifact, book path, app DB file, raw evidence, amount, memo, description, account name, `.env`, key, or token was committed.
- No release was created.
