# Daytime Write Worker 5 — #36-W1-G UI/operator blocked states

## Package

#36-W1-G — UI/operator blocked states.

## Goal

Strengthen owner-writebeta operator status output for blocked write-mode states without adding public write UI or touching any GnuCash book.

## Changes

- `apps/api/app/routers/owner_writebeta.py`
  - `/owner-writebeta/status` now reports explicit blocked reasons for:
    - `state_failed_hard_stop`
    - `state_reset_required`
    - `confirmation_expired`
    - `restore_not_ready`
  - Confirmation state only reports `preview_confirmed_armed` when confirmation is not expired.

- `apps/api/app/owner_writebeta_state_machine.py`
  - Entering `RESET_REQUIRED` or `FAILED_HARD_STOP` clears active-arm material (`preview_hash`, `confirmation_token_ref`, `restore_readiness_ref`, `expires_at`) so stale confirmations cannot be reused or displayed as active.

- `apps/api/tests/test_owner_writebeta_routes.py`
  - Added route-level regression tests for:
    - expired confirmation blocked state;
    - reset-required blocked state and cleared active arms;
    - failed-hard-stop blocked state and safe failed reason;
    - preflight blocked reasons avoiding state_* noise;
    - confirmation without restore readiness reporting `restore_not_ready`.

- `apps/api/tests/test_owner_writebeta_state_machine.py`
  - Updated happy-path reset-required expectation to match the stricter active-arm clearing behavior.

## Verification

Run from `apps/api`:

```bash
pytest -q tests/test_owner_writebeta_routes.py tests/test_owner_writebeta_state_machine.py tests/test_write_safety_defaults_guard.py --tb=short
```

Result:

```text
42 passed, 1 warning in 12.16s
```

Repository-level checks run by supervisor after worker patch review:

```bash
git diff --check
```

Result: clean.

## Safety notes

- No original/private/working/only-copy GnuCash book was touched.
- No GnuCash book, SQLite book, backup, export, screenshot, `.env`, token, key, private path, account name, transaction description, memo, amount, or raw private evidence was added.
- `GNUCASH_WRITES_ENABLED=false` default remains unchanged.
- `APP_ENV=test` gate remains unchanged.
- No public write beta or release.
- This is API/operator state visibility only, not public write UI.

## Issue #36 comment draft

> daytime-write-worker-5 (#36-W1-G): Strengthened owner-writebeta operator blocked-state visibility. `/owner-writebeta/status` now distinguishes failed hard stop, reset required, expired confirmation, and missing restore readiness. Reset-required and failed-hard-stop transitions clear active confirmation material so stale arms are not shown or reusable. Added route regression tests for expired confirmations, reset-required cleared arms, failed-hard-stop blocked status, preflight blocked reasons, and confirmation without restore readiness. Verification: `cd apps/api && pytest -q tests/test_owner_writebeta_routes.py tests/test_owner_writebeta_state_machine.py tests/test_write_safety_defaults_guard.py --tb=short` => 42 passed. No book mutation; no private evidence; writes remain default-disabled.

## Blockers

None for this package.
