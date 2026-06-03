# Daytime write continuation worker 3 — #36-W2-D synthetic lock contention drill

## PM scope lock

- Goal: prove concurrent/contended synthetic owner-writebeta write sessions fail safely.
- Scope: in-memory owner-writebeta session map and state-machine tests only; no GnuCash book access.
- Non-goals: OS/file lock implementation changes, copied-book dogfood, real working-book mutation, release claims.
- Safety checks: one confirmation cannot be reused, active MUTATING sessions reject second writers, failed hard-stop is terminal, default-disabled reset clears active arms.
- Acceptance criteria: second mutation cannot proceed while a synthetic session is active; expired confirmation fails closed; hard-stopped stale lock cannot recover through token reuse; a fresh session can proceed only after prior session was fully default-disabled/reset.
- Verification commands: `cd apps/api && python -m pytest -q tests/test_owner_writebeta_synthetic_lock_contention_drill.py tests/test_owner_writebeta_route_guard_fail_closed.py tests/test_owner_writebeta_state_machine.py --tb=short`.
- Mutation mode: synthetic/disposable only.

## Implementation

- Added `apps/api/tests/test_owner_writebeta_synthetic_lock_contention_drill.py` with direct route-guard/state-machine contention coverage.
- No production code change was needed for this package.

## Verification

- `cd apps/api && python -m pytest -q tests/test_owner_writebeta_synthetic_lock_contention_drill.py tests/test_owner_writebeta_route_guard_fail_closed.py tests/test_owner_writebeta_state_machine.py --tb=short` => 34 passed, 1 warning.

## Safety summary

- No private/original/working/only-copy GnuCash book was touched.
- No app DB file, backup, export, screenshot, account name, transaction description, memo, amount, `.env`, key, token, or raw private evidence was committed.
- No release was created.
