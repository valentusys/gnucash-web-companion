# Autonomous multiqueue cycle 6 — #36 non-mutating write-gate regression tests

## Queue

- Issue: #36 Track remaining controlled-write v0.2 readiness gates
- PM package: non-mutating write gate regression tests.

## Scope

- Add route-level tests proving owner-writebeta status remains default-disabled before preflight.
- Add route-level tests proving reset-disabled fails closed before verify-reset.
- Add a regression test for verify-reset before any routed mutation evidence.
- Tighten the route so verify-reset requires an actual `mutating` session state, not merely a confirmed
  preview.

## TDD/root-cause evidence

The new verify-reset regression initially failed: the route returned `200` and moved a confirmed
preview to `failed_hard_stop` when `defaults_reset=false`, even though no routed mutation had entered
the mutating state. Root cause: the route called `mark_post_mutation_checks` without first requiring
`OwnerWritebetaState.MUTATING`.

Fix: `owner_writebeta_verify_reset` now returns `409` unless the session is already `mutating`.

## Verification

Focused command passed:

```bash
pytest apps/api/tests/test_owner_writebeta_routes.py apps/api/tests/test_owner_writebeta_state_machine.py -q
```

Result: `13 passed, 1 warning`.

## Safety

- Non-mutating tests only; no GnuCash book was opened.
- GnuCash mutations: CREATE 0 / PATCH 0 / DELETE 0.
- `GNUCASH_WRITES_ENABLED=false` remains default.
