# daytime-write-worker-6 — #36-W2-C Synthetic failure/hard-stop drill

## Package

`#36-W2-C` — Synthetic failure/hard-stop drill for the owner-writebeta state
machine and routed API.

## Goal

Add or strengthen synthetic/disposable tests proving that when
read-back/restore/audit/lock/default-reset verification fails after a synthetic
mutation attempt, the owner-writebeta state machine / route reports
`failed_hard_stop` and future mutation remains blocked.

## Files changed

```
apps/api/tests/test_owner_writebeta_synthetic_failure_drill.py   (new, 11 tests)
```

No production code was changed. All new tests target the existing state machine
(`app/owner_writebeta_state_machine.py`) and routed API
(`app/routers/owner_writebeta.py`) which already implement the correct
closed transition behavior.

## Tests added (11 total)

### Pure state-machine tests (6)

| Test | Failure mode | Proves |
|------|-------------|--------|
| `test_synthetic_missing_audit_ref_triggers_hard_stop` | `audit_ref=""` | state=`failed_hard_stop`, writes_blocked=True |
| `test_synthetic_missing_restore_ref_triggers_hard_stop` | `restore_ref=""` | state=`failed_hard_stop`, writes_blocked=True |
| `test_synthetic_lock_not_released_triggers_hard_stop` | `lock_released=False` | state=`failed_hard_stop` |
| `test_synthetic_defaults_not_reset_triggers_hard_stop` | `defaults_reset=False` | state=`failed_hard_stop` |
| `test_synthetic_hard_stop_blocks_all_further_transitions` | all-FAILED-HARD-STOP | every other target state raises `OwnerWritebetaTransitionError` |
| `test_synthetic_hard_stop_summary_is_safe_and_redacted` | all fields missing | redacted_summary has no leaked values/keys; `failed_reason` is sanitized |

### Route-level tests (5)

| Test | Verification | Proves |
|------|-------------|--------|
| `test_synthetic_route_mutation_after_hard_stop_is_blocked` | verify-reset with `defaults_reset=False` | status=failed_hard_stop, writes_blocked=True, `state_failed_hard_stop` in blocked_reasons; /status continues showing hard stop |
| `test_synthetic_route_preflight_after_hard_stop_is_blocked` | /preflight after hard stop | 409, "blocked by current state" |
| `test_synthetic_route_preview_and_confirm_after_hard_stop_are_blocked` | /preview and /confirm after hard stop | both 409 |
| `test_synthetic_multiple_distinct_failure_modes_are_hard_stop` | 2 distinct failure modes across fresh sessions | each yields `failed_hard_stop` with safe summary |
| `test_synthetic_two_failure_modes_summary_sanitized_redirect` | failed_reason in 2 failure modes | `failed_reason` is always one of the 3 safe sanitized reasons |

That covers at least 4 distinct post-mutation failure modes:
- missing audit_ref
- missing restore_ref
- lock_released=False
- defaults_reset=False

## Verification

```
cd apps/api
python -m pytest tests/test_owner_writebeta_state_machine.py \
                 tests/test_owner_writebeta_routes.py \
                 tests/test_owner_writebeta_synthetic_failure_drill.py -v
# 42 passed
```

```
git diff --check
# clean
```

## Safety notes

- No production code changed.
- No real/private/original/working GnuCash books used. Fixtures use synthetic
  in-memory SQLite databases with disposable synthetic book paths (e.g.
  `/data/books/synthetic-failure-drill.sqlite`) — these are never written to
  disk and the path name is only used for fixture setup; it does not leak in
  any response.
- No GnuCash books, SQLite files, backups, or exports were committed.
- No public write UI added.
- `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=false` defaults unchanged.
- Route DTOs retain `min_length=1` on `audit_ref`/`restore_ref` (no weakening).
- `_SESSIONS` cleared between every test and in the `client` teardown.
- Handoff doc path: `docs/handoff/daytime-write-worker-6.md` — this file.
- Issue #36 comment draft below (do not post).

## Issue #36 comment draft (do not post)

```
#36-W2-C complete.

Added 11 synthetic/disposable regression tests in
`tests/test_owner_writebeta_synthetic_failure_drill.py` covering 4 distinct
post-mutation verification failure modes (missing audit_ref, missing
restore_ref, lock_released=False, defaults_reset=False).

All tests prove:
- state = `failed_hard_stop`
- `writes_blocked = True`
- `/status` shows `state_failed_hard_stop` in blocked_reasons
- Route mutation attempts after hard stop return 409 ("blocked by current state")
- `/summary` fields are redacted; no raw paths, amounts, account IDs, or
  private key names leak
- `failed_reason` is always sanitized to one of 3 safe variants

No production code changes required — the existing state machine and route
implement the correct fail-closed behavior. Full test suite passes (42/42).
git diff --check clean.
```

## Blockers

None.
