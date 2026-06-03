# Daytime write continuation worker 1 — #36-W2-A synthetic route-family drill

## PM scope lock

- Goal: prove the routed owner-writebeta/write-alpha path handles a synthetic CREATE -> metadata/memo-only PATCH -> DELETE route family with fail-closed guards and default reset.
- Scope: in-memory app DB plus fake write service only; no GnuCash book is opened or mutated.
- Non-goals: copied-book dogfood, real working-book mutation, release readiness claims.
- Safety checks: synthetic URI only, no private/original/working book path, no raw financial evidence, writes disabled by default remains enforced in reset probes.
- Acceptance criteria: CREATE requires a confirmed gate; PATCH/DELETE previews require write-alpha-owned target; PATCH schema rejects amount/account changes; DELETE rejects non-owned IDs without consuming the owner-writebeta confirmation; reset returns to disabled posture; default-disabled probes return 403 before write service.
- Verification commands: `cd apps/api && python -m pytest -q tests/test_owner_writebeta_synthetic_route_family_drill.py tests/test_owner_writebeta_routes.py tests/test_owner_writebeta_route_guard_fail_closed.py --tb=short`.
- Mutation mode: synthetic/disposable only.

## Implementation

- Added `apps/api/tests/test_owner_writebeta_synthetic_route_family_drill.py`.
- Reordered PATCH/DELETE write routes so write-alpha ownership is checked before consuming the owner-writebeta confirmation and transitioning the session to MUTATING. This prevents a non-owned PATCH/DELETE rejection from leaving a valid synthetic confirmation stuck in MUTATING.

## Verification

- `cd apps/api && python -m pytest -q tests/test_owner_writebeta_synthetic_route_family_drill.py tests/test_owner_writebeta_routes.py tests/test_owner_writebeta_route_guard_fail_closed.py --tb=short` => 31 passed, 1 warning.

## Safety summary

- No private/original/working/only-copy GnuCash book was touched.
- No book, SQLite DB, backup, export, `.env`, token, account name, transaction description, memo, amount, or raw private evidence was committed.
- No release was created.
